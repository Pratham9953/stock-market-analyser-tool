import { LRUCache } from 'lru-cache';
import type { NormalizedTick } from '../../infrastructure/providers/upstox/upstox-types';

export class LatestTickStore {
  private readonly cache = new LRUCache<string, NormalizedTick>({
    max: 10_000,
    ttl: 1000 * 60 * 10
  });

  set(tick: NormalizedTick): void {
    this.cache.set(tick.instrumentKey, tick);
  }

  get(instrumentKey: string): NormalizedTick | undefined {
    return this.cache.get(instrumentKey);
  }

  count(): number {
    return this.cache.size;
  }
}
