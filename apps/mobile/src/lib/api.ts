import type {
  AlertHistoryItemDto,
  AuthStatusResponseDto,
  DashboardStatusDto,
  DashboardSummaryDto,
  SessionBootstrapResponse,
  UpsertWatchlistItemDto,
  UserSettingsDto,
  WatchlistItemDto,
  InstrumentSummary
} from '@fo-scanner/shared';
import { mobileEnv } from './env';
import { storage } from './storage';

const buildHeaders = async () => {
  const token = await storage.getSessionToken();
  return {
    'content-type': 'application/json',
    ...(token ? { authorization: `Bearer ${token}` } : {})
  };
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${mobileEnv.EXPO_PUBLIC_API_URL}${path}`, {
    ...options,
    headers: {
      ...(await buildHeaders()),
      ...(options.headers ?? {})
    }
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Request failed');
  }

  return (await response.json()) as T;
}

export const api = {
  bootstrapSession: (payload: { deviceId: string; displayName?: string }) =>
    request<SessionBootstrapResponse>('/v1/session/bootstrap', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  getAuthStatus: () => request<AuthStatusResponseDto>('/v1/auth/status'),
  getConnectUrl: (frontendRedirectUri: string) =>
    request<{ url: string }>(`/v1/brokers/upstox/connect-url?frontendRedirectUri=${encodeURIComponent(frontendRedirectUri)}`),
  disconnectBroker: () => request<{ success: boolean }>('/v1/brokers/upstox/connection', { method: 'DELETE' }),
  getDashboardSummary: () => request<DashboardSummaryDto>('/v1/dashboard/summary'),
  getAlertHistory: (symbol?: string) => request<AlertHistoryItemDto[]>(`/v1/alerts${symbol ? `?symbol=${encodeURIComponent(symbol)}` : ''}`),
  acknowledgeAlert: (alertId: string) => request<{ success: boolean }>(`/v1/alerts/${alertId}/ack`, { method: 'POST' }),
  getWatchlist: () => request<WatchlistItemDto[]>('/v1/watchlist'),
  upsertWatchlist: (payload: UpsertWatchlistItemDto) =>
    request<WatchlistItemDto[]>('/v1/watchlist', { method: 'POST', body: JSON.stringify(payload) }),
  deleteWatchlist: (id: string) => request<{ success: boolean }>(`/v1/watchlist/${id}`, { method: 'DELETE' }),
  searchInstruments: (query: string) => request<InstrumentSummary[]>(`/v1/instruments/search?q=${encodeURIComponent(query)}`),
  getSettings: () => request<UserSettingsDto>('/v1/settings'),
  updateSettings: (payload: UserSettingsDto) => request<UserSettingsDto>('/v1/settings', { method: 'PUT', body: JSON.stringify(payload) }),
  getSystemStatus: () => request<DashboardStatusDto>('/v1/system/status')
};
