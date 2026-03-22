import { create } from 'zustand';
import type { SessionBootstrapResponse, DashboardSummaryDto } from '@fo-scanner/shared';

type SessionState = {
  bootstrapped: boolean;
  token: string | null;
  session: SessionBootstrapResponse | null;
  summary: DashboardSummaryDto | null;
  setSession: (payload: SessionBootstrapResponse) => void;
  setSummary: (payload: DashboardSummaryDto) => void;
  clearSession: () => void;
};

export const useSessionStore = create<SessionState>((set) => ({
  bootstrapped: false,
  token: null,
  session: null,
  summary: null,
  setSession: (payload) => set({ bootstrapped: true, token: payload.token, session: payload }),
  setSummary: (payload) => set({ summary: payload }),
  clearSession: () => set({ bootstrapped: true, token: null, session: null, summary: null })
}));
