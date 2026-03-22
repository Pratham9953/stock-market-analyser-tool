import cron from 'node-cron';
import { DataSource } from 'typeorm';
import { env } from '../../config/env';
import { BrokerConnection } from '../../infrastructure/db/entities/broker-connection.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import { ClientHub } from '../../infrastructure/realtime/client-hub';
import { logger } from '../../common/logger';
import { UpstoxApiClient } from '../../infrastructure/providers/upstox/upstox-api-client';
import { UpstoxMarketFeedConnection } from '../../infrastructure/providers/upstox/upstox-market-feed';
import { AlertsService } from '../alerts/alerts.service';
import { UpstoxOAuthService } from '../auth/oauth.service';
import { InstrumentService } from '../instruments/instrument.service';
import { SettingsService } from '../settings/settings.service';
import { LatestTickStore } from './latest-tick.store';
import { PairingService } from './pairing.service';
import { SpreadDetectorService } from './spread-detector.service';
import type { UserSettingsDto } from '@fo-scanner/shared';

const chunk = <T,>(items: T[], size: number): T[][] => {
  const result: T[][] = [];
  for (let offset = 0; offset < items.length; offset += size) {
    result.push(items.slice(offset, offset + size));
  }
  return result;
};

type RuntimeSnapshot = {
  subscribedInstrumentCount: number;
  lastTickAt: string | null;
  backendLatencyMs: number;
  websocketState: 'connected' | 'connecting' | 'closed';
  marketDataState: 'idle' | 'connecting' | 'connected' | 'expired' | 'error';
  lastInstrumentSyncAt: string | null;
  marketStatus: Record<string, string>;
};

class UserScannerWorker {
  private readonly tickStore = new LatestTickStore();
  private readonly detector = new SpreadDetectorService(this.tickStore);
  private readonly feeds: UpstoxMarketFeedConnection[] = [];
  private readonly pairIdsByInstrument = new Map<string, Set<string>>();
  private readonly liveSpreadEmissionAt = new Map<string, number>();
  private settings: UserSettingsDto | null = null;
  private pairs: Awaited<ReturnType<PairingService['getPairsForUser']>> = [];

  runtime: RuntimeSnapshot = {
    subscribedInstrumentCount: 0,
    lastTickAt: null,
    backendLatencyMs: 0,
    websocketState: 'closed',
    marketDataState: 'idle',
    lastInstrumentSyncAt: null,
    marketStatus: {}
  };

  constructor(
    private readonly user: User,
    private readonly connection: BrokerConnection,
    private readonly oauthService: UpstoxOAuthService,
    private readonly upstoxApiClient: UpstoxApiClient,
    private readonly pairingService: PairingService,
    private readonly settingsService: SettingsService,
    private readonly alertsService: AlertsService,
    private readonly clientHub: ClientHub
  ) {}

  async start(): Promise<void> {
    await this.refresh();
  }

  async refresh(): Promise<void> {
    this.settings = await this.settingsService.getForUser(this.user);
    this.pairs = await this.pairingService.getPairsForUser(this.user.id);
    this.runtime.subscribedInstrumentCount = this.pairs.length * 2;
    this.pairIdsByInstrument.clear();

    for (const pair of this.pairs) {
      const spotKey = pair.spotInstrument?.instrumentKey;
      const futureKey = pair.futureInstrument?.instrumentKey;
      if (!spotKey || !futureKey) continue;
      const spotSet = this.pairIdsByInstrument.get(spotKey) ?? new Set<string>();
      spotSet.add(pair.id);
      this.pairIdsByInstrument.set(spotKey, spotSet);
      const futureSet = this.pairIdsByInstrument.get(futureKey) ?? new Set<string>();
      futureSet.add(pair.id);
      this.pairIdsByInstrument.set(futureKey, futureSet);
    }

    this.stopFeeds();
    if (!this.pairs.length) {
      this.runtime.marketDataState = 'idle';
      this.runtime.websocketState = 'closed';
      return;
    }

    const accessToken = await this.oauthService.getAccessTokenForConnection(this.connection.id);
    const instrumentKeys = Array.from(
      new Set(this.pairs.flatMap((pair) => [pair.spotInstrument?.instrumentKey, pair.futureInstrument?.instrumentKey].filter(Boolean) as string[]))
    );
    const shards = chunk(instrumentKeys, env.UPSTOX_LTPC_PER_CONNECTION).slice(0, env.UPSTOX_MAX_CONNECTIONS);

    for (const shard of shards) {
      const feed = new UpstoxMarketFeedConnection(
        this.upstoxApiClient,
        accessToken,
        shard,
        (tick) => {
          void this.handleTick(tick);
        },
        (status) => {
          this.runtime.websocketState = status === 'connected' ? 'connected' : status === 'connecting' ? 'connecting' : 'closed';
          this.runtime.marketDataState = status === 'error' ? 'error' : status === 'connected' ? 'connected' : 'connecting';
        },
        (marketStatus) => {
          this.runtime.marketStatus = marketStatus;
        }
      );
      this.feeds.push(feed);
      await feed.start();
    }
  }

  stop(): void {
    this.stopFeeds();
  }

  private stopFeeds(): void {
    for (const feed of this.feeds) {
      feed.stop();
    }
    this.feeds.length = 0;
  }

  private async handleTick(tick: { instrumentKey: string; price: number; observedAt: Date; requestMode: string }): Promise<void> {
    const started = Date.now();
    this.tickStore.set(tick);
    this.runtime.lastTickAt = tick.observedAt.toISOString();
    const pairIds = this.pairIdsByInstrument.get(tick.instrumentKey);
    if (!pairIds || !this.settings) return;

    for (const pairId of pairIds) {
      const pair = this.pairs.find((value) => value.id === pairId);
      if (!pair || !pair.spotInstrument || !pair.futureInstrument) continue;

      const candidate = this.detector.evaluate(pair, this.settings);
      if (candidate) {
        const alert = await this.alertsService.create(this.user, candidate);
        this.clientHub.publishToUser(this.user.id, { type: 'alert.created', payload: alert }, 'critical');
      }

      const now = Date.now();
      const lastEmit = this.liveSpreadEmissionAt.get(pairId) ?? 0;
      if (now - lastEmit > 1000) {
        const spotTick = this.tickStore.get(pair.spotInstrument.instrumentKey);
        const futureTick = this.tickStore.get(pair.futureInstrument.instrumentKey);
        if (spotTick && futureTick) {
          this.clientHub.publishToUser(this.user.id, {
            type: 'scanner.spread',
            payload: {
              pairId: pair.id,
              symbol: pair.symbol,
              spread: Number((spotTick.price - futureTick.price).toFixed(2)),
              spotPrice: spotTick.price,
              futurePrice: futureTick.price,
              futureExpiry: pair.futureExpiryDate,
              observedAt: new Date(Math.max(spotTick.observedAt.getTime(), futureTick.observedAt.getTime())).toISOString()
            }
          });
          this.liveSpreadEmissionAt.set(pairId, now);
        }
      }
    }

    this.runtime.backendLatencyMs = Date.now() - started;
  }
}

export class ScannerOrchestrator {
  private readonly workers = new Map<string, UserScannerWorker>();
  private lastInstrumentSyncAt: string | null = null;

  constructor(
    private readonly dataSource: DataSource,
    private readonly oauthService: UpstoxOAuthService,
    private readonly upstoxApiClient: UpstoxApiClient,
    private readonly pairingService: PairingService,
    private readonly settingsService: SettingsService,
    private readonly alertsService: AlertsService,
    private readonly clientHub: ClientHub,
    private readonly instrumentService: InstrumentService
  ) {}

  async start(): Promise<void> {
    await this.syncInstruments();
    await this.startWorkers();
    cron.schedule(env.INSTRUMENT_SYNC_CRON, () => {
      void this.syncInstruments();
    });
  }

  async refreshUser(user: User): Promise<void> {
    await this.pairingService.refreshForUser(user);
    const worker = this.workers.get(user.id);
    if (worker) {
      await worker.refresh();
      return;
    }

    const connectionRepo = this.dataSource.getRepository(BrokerConnection);
    const connection = await connectionRepo.findOne({ where: { user: { id: user.id }, broker: 'UPSTOX', status: 'connected' }, relations: { user: true } });
    if (!connection) return;

    const nextWorker = this.createWorker(user, connection);
    this.workers.set(user.id, nextWorker);
    await nextWorker.start();
  }

  getRuntimeSnapshot(userId: string): RuntimeSnapshot {
    const runtime = this.workers.get(userId)?.runtime;
    return runtime
      ? { ...runtime, lastInstrumentSyncAt: this.lastInstrumentSyncAt }
      : {
          subscribedInstrumentCount: 0,
          lastTickAt: null,
          backendLatencyMs: 0,
          websocketState: 'closed',
          marketDataState: 'idle',
          lastInstrumentSyncAt: this.lastInstrumentSyncAt,
          marketStatus: {}
        };
  }

  private async syncInstruments(): Promise<void> {
    const count = await this.instrumentService.syncBodInstruments();
    this.lastInstrumentSyncAt = new Date().toISOString();
    logger.info({ count }, 'Instrument sync finished');
  }

  private async startWorkers(): Promise<void> {
    const repo = this.dataSource.getRepository(BrokerConnection);
    const connections = await repo.find({ where: { broker: 'UPSTOX', status: 'connected' }, relations: { user: true } });
    for (const connection of connections) {
      const worker = this.createWorker(connection.user, connection);
      this.workers.set(connection.user.id, worker);
      await worker.start();
    }
  }

  private createWorker(user: User, connection: BrokerConnection): UserScannerWorker {
    return new UserScannerWorker(
      user,
      connection,
      this.oauthService,
      this.upstoxApiClient,
      this.pairingService,
      this.settingsService,
      this.alertsService,
      this.clientHub
    );
  }
}
