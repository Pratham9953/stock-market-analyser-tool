import type WebSocket from 'ws';
import { env } from '../../config/env';
import { websocketEventSchema, type WebsocketEvent } from '@fo-scanner/shared';

export class ClientHub {
  private readonly sockets = new Map<string, Set<WebSocket>>();

  connect(userId: string, socket: WebSocket): void {
    const set = this.sockets.get(userId) ?? new Set<WebSocket>();
    set.add(socket);
    this.sockets.set(userId, set);
    socket.on('close', () => {
      const current = this.sockets.get(userId);
      current?.delete(socket);
      if (!current || current.size === 0) {
        this.sockets.delete(userId);
      }
    });
  }

  publishToUser(userId: string, event: WebsocketEvent, priority: 'critical' | 'normal' = 'normal'): void {
    websocketEventSchema.parse(event);
    const sockets = this.sockets.get(userId);
    if (!sockets) return;
    const payload = JSON.stringify(event);
    for (const socket of sockets) {
      if (socket.readyState !== socket.OPEN) continue;
      if (priority === 'normal' && socket.bufferedAmount > env.WS_BUFFER_DROP_THRESHOLD) {
        continue;
      }
      socket.send(payload);
    }
  }
}
