import crypto from 'node:crypto';
import { setTimeout as wait } from 'node:timers/promises';
import WebSocket, { RawData } from 'ws';
import { env } from '../../../config/env';
import { logger } from '../../../common/logger';
import { FeedResponseType } from './proto-loader';
import { UpstoxApiClient } from './upstox-api-client';
import type { NormalizedTick } from './upstox-types';

const REQUEST_MODE_BY_ENUM = ['ltpc', 'full_d5', 'option_greeks', 'full_d30'];

type FeedStatusCallback = (status: 'connecting' | 'connected' | 'closed' | 'error', details?: Record<string, unknown>) => void;
type TickCallback = (tick: NormalizedTick) => void;
type MarketInfoCallback = (segments: Record<string, string>) => void;

type FeedResponseObject = {
  feeds?: Record<string, any>;
  currentTs?: number;
  marketInfo?: { segmentStatus?: Record<string, string> };
};

export class UpstoxMarketFeedConnection {
  private socket: WebSocket | null = null;
  private shouldRun = true;
  private reconnectAttempt = 0;

  constructor(
    private readonly apiClient: UpstoxApiClient,
    private readonly accessToken: string,
    private readonly instrumentKeys: string[],
    private readonly onTick: TickCallback,
    private readonly onStatus: FeedStatusCallback,
    private readonly onMarketInfo: MarketInfoCallback
  ) {}

  async start(): Promise<void> {
    while (this.shouldRun) {
      try {
        this.onStatus('connecting');
        const url = await this.apiClient.getMarketFeedAuthorizeUrl(this.accessToken);
        await this.connect(url);
        this.reconnectAttempt = 0;
        return;
      } catch (error) {
        this.onStatus('error', { message: error instanceof Error ? error.message : 'feed connect failed' });
        const delay = Math.min(env.UPSTOX_RECONNECT_BASE_MS * 2 ** this.reconnectAttempt, env.UPSTOX_RECONNECT_MAX_MS);
        this.reconnectAttempt += 1;
        await wait(delay);
      }
    }
  }

  stop(): void {
    this.shouldRun = false;
    this.socket?.close();
    this.socket = null;
  }

  private async connect(url: string): Promise<void> {
    await new Promise<void>((resolve, reject) => {
      const ws = new WebSocket(url);
      this.socket = ws;

      ws.on('open', () => {
        this.onStatus('connected');
        const payload = Buffer.from(
          JSON.stringify({
            guid: crypto.randomUUID(),
            method: 'sub',
            data: {
              mode: 'ltpc',
              instrumentKeys: this.instrumentKeys
            }
          })
        );
        ws.send(payload);
        resolve();
      });

      ws.on('message', (data) => this.handleMessage(data));
      ws.on('error', (error) => {
        logger.warn({ err: error }, 'Upstox websocket error');
        reject(error);
      });
      ws.on('close', () => {
        this.onStatus('closed');
        if (this.shouldRun) {
          void this.start();
        }
      });
    });
  }

  private handleMessage(data: RawData): void {
    if (typeof data === 'string') return;
    const decoded = FeedResponseType.decode(Buffer.from(data));
    const object = FeedResponseType.toObject(decoded, {
      enums: String,
      longs: Number,
      defaults: false
    }) as FeedResponseObject;

    if (object.marketInfo?.segmentStatus) {
      this.onMarketInfo(object.marketInfo.segmentStatus);
    }

    const currentTs = typeof object.currentTs === 'number' ? object.currentTs : Date.now();
    for (const [instrumentKey, feed] of Object.entries(object.feeds ?? {})) {
      const price =
        feed.ltpc?.ltp ??
        feed.fullFeed?.marketFF?.ltpc?.ltp ??
        feed.fullFeed?.indexFF?.ltpc?.ltp ??
        feed.firstLevelWithGreeks?.ltpc?.ltp;
      if (typeof price !== 'number') continue;
      const requestMode = REQUEST_MODE_BY_ENUM[(feed.requestMode as number) ?? 0] ?? 'ltpc';
      this.onTick({
        instrumentKey,
        price,
        requestMode,
        observedAt: new Date(currentTs)
      });
    }
  }
}
