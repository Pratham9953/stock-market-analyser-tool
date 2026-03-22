import { SpreadDetectorService } from './spread-detector.service';
import { LatestTickStore } from './latest-tick.store';
import { InstrumentPair } from '../../infrastructure/db/entities/instrument-pair.entity';

const pair = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  spotInstrument: { instrumentKey: 'NSE_EQ|RELIANCE' },
  futureInstrument: { instrumentKey: 'NSE_FO|RELIANCE24MARFUT' }
} as unknown as InstrumentPair;

describe('SpreadDetectorService', () => {
  it('emits a candidate when spread breaches threshold and ticks are fresh', () => {
    const store = new LatestTickStore();
    const detector = new SpreadDetectorService(store);
    const observedAt = new Date();
    store.set({ instrumentKey: 'NSE_EQ|RELIANCE', price: 2510, observedAt, requestMode: 'ltpc' });
    store.set({ instrumentKey: 'NSE_FO|RELIANCE24MARFUT', price: 2498, observedAt, requestMode: 'ltpc' });

    const result = detector.evaluate(pair, {
      threshold: 10,
      cooldownMs: 30000,
      freshnessMs: 10000,
      preferredExchange: 'NSE',
      darkMode: true,
      exchanges: ['NSE'],
      segments: ['NSE_EQ', 'NSE_FO']
    });

    expect(result?.spread).toBe(12);
    expect(result?.threshold).toBe(10);
  });

  it('deduplicates repeated identical alerts inside cooldown', () => {
    const store = new LatestTickStore();
    const detector = new SpreadDetectorService(store);
    const observedAt = new Date();
    store.set({ instrumentKey: 'NSE_EQ|RELIANCE', price: 2510, observedAt, requestMode: 'ltpc' });
    store.set({ instrumentKey: 'NSE_FO|RELIANCE24MARFUT', price: 2498, observedAt, requestMode: 'ltpc' });

    const settings = {
      threshold: 10,
      cooldownMs: 30000,
      freshnessMs: 10000,
      preferredExchange: 'NSE',
      darkMode: true,
      exchanges: ['NSE'],
      segments: ['NSE_EQ', 'NSE_FO']
    };

    expect(detector.evaluate(pair, settings)).not.toBeNull();
    expect(detector.evaluate(pair, settings)).toBeNull();
  });
});
