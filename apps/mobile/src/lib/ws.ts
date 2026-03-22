import { websocketEventSchema, type WebsocketEvent } from '@fo-scanner/shared';
import { mobileEnv } from './env';

type Listener = (event: WebsocketEvent) => void;

export class LiveWebsocketClient {
  private socket: WebSocket | null = null;
  private listeners = new Set<Listener>();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private retryCount = 0;
  private token: string | null = null;

  connect(token: string): void {
    this.token = token;
    this.open();
  }

  disconnect(): void {
    this.token = null;
    this.socket?.close();
    this.socket = null;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private open(): void {
    if (!this.token) return;
    const url = `${mobileEnv.EXPO_PUBLIC_WS_URL}?token=${encodeURIComponent(this.token)}`;
    this.socket = new WebSocket(url);

    this.socket.onmessage = (message) => {
      try {
        const event = websocketEventSchema.parse(JSON.parse(message.data));
        for (const listener of this.listeners) listener(event);
      } catch {
        // ignore malformed payloads
      }
    };

    this.socket.onclose = () => {
      if (!this.token) return;
      const delay = Math.min(1000 * 2 ** this.retryCount, 10000);
      this.retryCount += 1;
      this.reconnectTimer = setTimeout(() => this.open(), delay);
    };

    this.socket.onopen = () => {
      this.retryCount = 0;
    };
  }
}

export const liveWebsocketClient = new LiveWebsocketClient();
