import { create } from 'zustand';
import type { AlertHistoryItemDto, WebsocketEvent } from '@fo-scanner/shared';

type LiveSpread = {
  pairId: string;
  symbol: string;
  spread: number;
  spotPrice: number;
  futurePrice: number;
  futureExpiry: string | null;
  observedAt: string;
};

type LiveState = {
  spreads: Record<string, LiveSpread>;
  alerts: AlertHistoryItemDto[];
  ingestEvent: (event: WebsocketEvent) => void;
  setAlerts: (alerts: AlertHistoryItemDto[]) => void;
};

export const useLiveStore = create<LiveState>((set) => ({
  spreads: {},
  alerts: [],
  ingestEvent: (event) =>
    set((state) => {
      if (event.type === 'scanner.spread') {
        return {
          ...state,
          spreads: {
            ...state.spreads,
            [event.payload.pairId]: event.payload
          }
        };
      }
      if (event.type === 'alert.created') {
        return {
          ...state,
          alerts: [event.payload, ...state.alerts].slice(0, 200)
        };
      }
      return state;
    }),
  setAlerts: (alerts) => set({ alerts })
}));
