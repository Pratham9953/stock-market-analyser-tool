import { useLiveStore } from './live-store';

describe('live store', () => {
  beforeEach(() => {
    useLiveStore.setState({ spreads: {}, alerts: [], ingestEvent: useLiveStore.getState().ingestEvent, setAlerts: useLiveStore.getState().setAlerts });
  });

  it('stores incoming spread updates', () => {
    useLiveStore.getState().ingestEvent({
      type: 'scanner.spread',
      payload: {
        pairId: 'pair-1',
        symbol: 'RELIANCE',
        spread: 12,
        spotPrice: 2510,
        futurePrice: 2498,
        futureExpiry: '2026-03-26',
        observedAt: new Date().toISOString()
      }
    });

    expect(useLiveStore.getState().spreads['pair-1']?.spread).toBe(12);
  });

  it('prepends live alerts', () => {
    useLiveStore.getState().ingestEvent({
      type: 'alert.created',
      payload: {
        id: 'alert-1',
        pairId: 'pair-1',
        symbol: 'RELIANCE',
        spread: 12,
        threshold: 10,
        spotPrice: 2510,
        futurePrice: 2498,
        futureExpiry: '2026-03-26',
        triggeredAt: new Date().toISOString(),
        freshnessMs: 50,
        dedupeKey: 'pair-1:12',
        acknowledgedAt: null
      }
    });

    expect(useLiveStore.getState().alerts[0]?.id).toBe('alert-1');
  });
});
