import { InstrumentPair } from '../../infrastructure/db/entities/instrument-pair.entity';
import { LatestTickStore } from './latest-tick.store';
import type { UserSettingsDto } from '@fo-scanner/shared';

export type SpreadCandidate = {
  pair: InstrumentPair;
  spread: number;
  threshold: number;
  spotPrice: number;
  futurePrice: number;
  observedAt: Date;
  freshnessMs: number;
  dedupeKey: string;
};

export class SpreadDetectorService {
  private readonly lastAlertByPair = new Map<string, { dedupeKey: string; emittedAt: number }>();

  constructor(private readonly tickStore: LatestTickStore) {}

  evaluate(pair: InstrumentPair, settings: UserSettingsDto): SpreadCandidate | null {
    const spotKey = pair.spotInstrument?.instrumentKey;
    const futureKey = pair.futureInstrument?.instrumentKey;
    if (!spotKey || !futureKey) return null;

    const spot = this.tickStore.get(spotKey);
    const future = this.tickStore.get(futureKey);
    if (!spot || !future) return null;

    const freshnessMs = Math.abs(spot.observedAt.getTime() - future.observedAt.getTime());
    if (freshnessMs > settings.freshnessMs) return null;

    const spread = Number((spot.price - future.price).toFixed(2));
    if (spread < settings.threshold) return null;

    const observedAt = new Date(Math.max(spot.observedAt.getTime(), future.observedAt.getTime()));
    const spreadBucket = Math.floor(spread * 4) / 4;
    const dedupeKey = `${pair.id}:${spreadBucket.toFixed(2)}`;
    const previous = this.lastAlertByPair.get(pair.id);

    if (previous && previous.dedupeKey === dedupeKey && observedAt.getTime() - previous.emittedAt < settings.cooldownMs) {
      return null;
    }

    this.lastAlertByPair.set(pair.id, { dedupeKey, emittedAt: observedAt.getTime() });

    return {
      pair,
      spread,
      threshold: settings.threshold,
      spotPrice: spot.price,
      futurePrice: future.price,
      observedAt,
      freshnessMs,
      dedupeKey
    };
  }
}
