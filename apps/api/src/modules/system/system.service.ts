import { DataSource } from 'typeorm';
import type { DashboardStatusDto, DashboardSummaryDto } from '@fo-scanner/shared';
import { SystemEvent } from '../../infrastructure/db/entities/system-event.entity';
import { BrokerConnection } from '../../infrastructure/db/entities/broker-connection.entity';
import { Watchlist } from '../../infrastructure/db/entities/watchlist.entity';
import { Alert } from '../../infrastructure/db/entities/alert.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import { UserSetting } from '../../infrastructure/db/entities/user-setting.entity';
import { ScannerOrchestrator } from '../market/scanner-orchestrator.service';

export class SystemService {
  constructor(private readonly dataSource: DataSource, private readonly orchestrator: ScannerOrchestrator) {}

  async getSummary(user: User): Promise<DashboardSummaryDto> {
    const watchRepo = this.dataSource.getRepository(Watchlist);
    const alertRepo = this.dataSource.getRepository(Alert);
    const settingsRepo = this.dataSource.getRepository(UserSetting);
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);

    const [watchCount, liveAlertCount, settings, connection] = await Promise.all([
      watchRepo.count({ where: { user: { id: user.id }, enabled: true } }),
      alertRepo.count({ where: { user: { id: user.id }, acknowledgedAt: null } }),
      settingsRepo.findOne({ where: { user: { id: user.id } }, relations: { user: true } }),
      connectionRepo.findOne({ where: { user: { id: user.id }, broker: 'UPSTOX' } })
    ]);

    const runtime = this.orchestrator.getRuntimeSnapshot(user.id);

    return {
      activeConnection: !!connection && connection.status === 'connected',
      subscribedInstrumentCount: runtime.subscribedInstrumentCount,
      activeWatchlistCount: watchCount,
      liveAlertCount,
      lastTickAt: runtime.lastTickAt,
      backendLatencyMs: runtime.backendLatencyMs,
      websocketState: runtime.websocketState,
      marketDataState: runtime.marketDataState,
      threshold: settings?.threshold ?? 10
    };
  }

  async getStatus(user: User): Promise<DashboardStatusDto> {
    const eventsRepo = this.dataSource.getRepository(SystemEvent);
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);
    const connection = await connectionRepo.findOne({ where: { user: { id: user.id }, broker: 'UPSTOX' } });
    const runtime = this.orchestrator.getRuntimeSnapshot(user.id);
    const events = await eventsRepo.find({ order: { createdAt: 'DESC' }, take: 20 });

    return {
      backend: 'ok',
      database: 'ok',
      brokerAuth: connection?.status ?? 'idle',
      websocket: runtime.websocketState,
      marketFeed: runtime.marketDataState,
      instrumentSyncAt: runtime.lastInstrumentSyncAt,
      marketStatus: runtime.marketStatus,
      recentEvents: events.map((event) => ({
        id: event.id,
        level: event.level,
        type: event.type,
        message: event.message,
        createdAt: event.createdAt.toISOString()
      }))
    };
  }

  async logEvent(type: string, message: string, level: 'info' | 'warning' | 'critical', payload: Record<string, unknown> = {}): Promise<void> {
    const repo = this.dataSource.getRepository(SystemEvent);
    await repo.save(repo.create({ type, message, level, payload, source: 'api' }));
  }
}
