from pathlib import Path
from textwrap import dedent
root = Path('/mnt/data/fo-backwardation-scanner')

def w(path, content):
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dedent(content).lstrip('\n'))

w('apps/mobile/package.json', '''
{
  "name": "@fo-scanner/mobile",
  "version": "1.0.0",
  "private": true,
  "main": "expo-router/entry",
  "scripts": {
    "dev": "expo start --clear",
    "web": "expo start --web --non-interactive",
    "build": "expo export -p web --output-dir dist",
    "lint": "eslint . --ext .ts,.tsx",
    "typecheck": "tsc --project tsconfig.json --noEmit",
    "test": "jest --runInBand",
    "clean": "rimraf dist .expo"
  },
  "dependencies": {
    "@fo-scanner/shared": "workspace:*",
    "@fo-scanner/ui": "workspace:*",
    "@tanstack/react-query": "^5.81.5",
    "@react-native-async-storage/async-storage": "2.2.0",
    "expo": "~55.0.0",
    "expo-application": "~7.0.7",
    "expo-linking": "~8.0.9",
    "expo-router": "~6.0.14",
    "expo-status-bar": "~3.0.8",
    "expo-web-browser": "~15.0.8",
    "react": "19.1.1",
    "react-dom": "19.1.1",
    "react-native": "0.83.0",
    "react-native-safe-area-context": "5.6.2",
    "react-native-screens": "~4.16.0",
    "react-native-svg": "15.13.0",
    "zustand": "^5.0.7"
  },
  "devDependencies": {
    "@babel/core": "^7.27.4",
    "@testing-library/jest-native": "^5.4.3",
    "@types/react": "^19.1.8",
    "@types/react-test-renderer": "^19.1.0",
    "jest": "^30.0.2",
    "jest-expo": "~55.0.4",
    "react-test-renderer": "19.1.1",
    "rimraf": "^6.0.1"
  }
}
''')

w('apps/mobile/.env.example', '''
EXPO_PUBLIC_API_URL=http://localhost:3000
EXPO_PUBLIC_WS_URL=ws://localhost:3000/v1/ws/live
EXPO_PUBLIC_UPSTOX_CALLBACK_URL=http://localhost:19006/auth/upstox-callback
EXPO_PUBLIC_APP_NAME=F&O Backwardation Scanner
''')

w('apps/mobile/Dockerfile', '''
FROM node:22-alpine
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-workspace.yaml turbo.json tsconfig.base.json .npmrc ./
COPY packages ./packages
COPY apps/mobile ./apps/mobile
RUN pnpm install --frozen-lockfile=false
EXPOSE 19006
CMD ["pnpm", "--filter", "@fo-scanner/mobile", "web"]
''')

w('apps/mobile/tsconfig.json', '''
{
  "extends": "../../packages/config/tsconfig/react-native.json",
  "compilerOptions": {
    "jsx": "react-jsx",
    "types": ["react", "react-native", "jest", "expo-router/types"]
  },
  "include": ["app/**/*.ts", "app/**/*.tsx", "src/**/*.ts", "src/**/*.tsx", "expo-env.d.ts"]
}
''')

w('apps/mobile/app.json', '''
{
  "expo": {
    "name": "F&O Backwardation Scanner",
    "slug": "fo-backwardation-scanner",
    "scheme": "fo-scanner",
    "version": "1.0.0",
    "orientation": "portrait",
    "userInterfaceStyle": "automatic",
    "newArchEnabled": true,
    "platforms": ["android", "ios", "web"],
    "experiments": {
      "typedRoutes": true
    },
    "web": {
      "bundler": "metro",
      "output": "single",
      "favicon": "./assets/favicon.png"
    },
    "plugins": ["expo-router"],
    "android": {
      "package": "ai.gopluto.backwardationscanner"
    },
    "ios": {
      "bundleIdentifier": "ai.gopluto.backwardationscanner"
    }
  }
}
''')

w('apps/mobile/babel.config.js', '''
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['expo-router/babel']
  };
};
''')

w('apps/mobile/metro.config.js', '''
const { getDefaultConfig } = require('expo/metro-config');
const path = require('path');

const projectRoot = __dirname;
const workspaceRoot = path.resolve(projectRoot, '../..');

const config = getDefaultConfig(projectRoot);
config.watchFolders = [workspaceRoot];
config.resolver.nodeModulesPaths = [
  path.resolve(projectRoot, 'node_modules'),
  path.resolve(workspaceRoot, 'node_modules')
];

module.exports = config;
''')

w('apps/mobile/jest.config.js', '''
module.exports = {
  preset: 'jest-expo',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|expo(nent)?|@expo|expo-router|react-native-svg|@tanstack)/)'
  ],
  moduleNameMapper: {
    '^@fo-scanner/shared$': '<rootDir>/../../packages/shared/src/index.ts',
    '^@fo-scanner/ui$': '<rootDir>/../../packages/ui/src/index.tsx'
  }
};
''')

w('apps/mobile/jest.setup.ts', '''
import '@testing-library/jest-native/extend-expect';
''')

w('apps/mobile/expo-env.d.ts', '''
/// <reference types="expo-router/types" />
''')

w('apps/mobile/src/lib/env.ts', '''
import { mobilePublicEnvSchema } from '@fo-scanner/shared';

export const mobileEnv = mobilePublicEnvSchema.parse({
  EXPO_PUBLIC_API_URL: process.env.EXPO_PUBLIC_API_URL,
  EXPO_PUBLIC_WS_URL: process.env.EXPO_PUBLIC_WS_URL,
  EXPO_PUBLIC_UPSTOX_CALLBACK_URL: process.env.EXPO_PUBLIC_UPSTOX_CALLBACK_URL,
  EXPO_PUBLIC_APP_NAME: process.env.EXPO_PUBLIC_APP_NAME
});
''')

w('apps/mobile/src/lib/storage.ts', '''
import AsyncStorage from '@react-native-async-storage/async-storage';

const SESSION_TOKEN_KEY = 'fo-scanner.session.token';
const DEVICE_ID_KEY = 'fo-scanner.device.id';

export const storage = {
  getSessionToken: () => AsyncStorage.getItem(SESSION_TOKEN_KEY),
  setSessionToken: (value: string) => AsyncStorage.setItem(SESSION_TOKEN_KEY, value),
  clearSessionToken: () => AsyncStorage.removeItem(SESSION_TOKEN_KEY),
  getDeviceId: () => AsyncStorage.getItem(DEVICE_ID_KEY),
  setDeviceId: (value: string) => AsyncStorage.setItem(DEVICE_ID_KEY, value)
};
''')

w('apps/mobile/src/lib/device.ts', '''
import * as Application from 'expo-application';
import { storage } from './storage';

const fallbackDeviceId = () => `web-${Math.random().toString(36).slice(2)}-${Date.now()}`;

export const getOrCreateDeviceId = async (): Promise<string> => {
  const existing = await storage.getDeviceId();
  if (existing) return existing;
  const generated = Application.getAndroidId?.() || Application.applicationId || fallbackDeviceId();
  await storage.setDeviceId(generated);
  return generated;
};
''')

w('apps/mobile/src/lib/api.ts', '''
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
''')

w('apps/mobile/src/lib/ws.ts', '''
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
''')

w('apps/mobile/src/store/session-store.ts', '''
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
''')

w('apps/mobile/src/store/live-store.ts', '''
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
''')

w('apps/mobile/src/hooks/use-bootstrap.ts', '''
import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { getOrCreateDeviceId } from '../lib/device';
import { storage } from '../lib/storage';
import { liveWebsocketClient } from '../lib/ws';
import { useSessionStore } from '../store/session-store';
import { useLiveStore } from '../store/live-store';

export const useBootstrap = () => {
  const router = useRouter();
  const setSession = useSessionStore((state) => state.setSession);
  const ingestEvent = useLiveStore((state) => state.ingestEvent);

  const query = useQuery({
    queryKey: ['bootstrap'],
    queryFn: async () => {
      const deviceId = await getOrCreateDeviceId();
      const payload = await api.bootstrapSession({ deviceId, displayName: 'Local Trader' });
      await storage.setSessionToken(payload.token);
      setSession(payload);
      liveWebsocketClient.connect(payload.token);
      return payload;
    }
  });

  useEffect(() => liveWebsocketClient.subscribe(ingestEvent), [ingestEvent]);

  useEffect(() => {
    if (!query.data) return;
    if (query.data.brokerConnection?.status === 'connected') {
      router.replace('/(tabs)/dashboard');
    } else {
      router.replace('/connect');
    }
  }, [query.data, router]);

  return query;
};
''')

w('apps/mobile/src/hooks/use-dashboard.ts', '''
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useSessionStore } from '../store/session-store';

export const useDashboard = () => {
  const setSummary = useSessionStore((state) => state.setSummary);
  return useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: async () => {
      const summary = await api.getDashboardSummary();
      setSummary(summary);
      return summary;
    },
    refetchInterval: 5000
  });
};
''')

w('apps/mobile/src/components/ResponsiveGrid.tsx', '''
import React from 'react';
import { useWindowDimensions, View } from 'react-native';

export const ResponsiveGrid = ({ children }: { children: React.ReactNode }) => {
  const { width } = useWindowDimensions();
  const isWide = width >= 900;
  return <View style={{ flexDirection: isWide ? 'row' : 'column', flexWrap: 'wrap', gap: 12 }}>{children}</View>;
};
''')

w('apps/mobile/src/components/LiveSpreadList.tsx', '''
import React from 'react';
import { Text, View } from 'react-native';
import { Card, Badge, useTheme } from '@fo-scanner/ui';
import { formatCurrency, formatDateTime } from '@fo-scanner/shared';
import { useLiveStore } from '../store/live-store';

export const LiveSpreadList = () => {
  const theme = useTheme();
  const spreads = Object.values(useLiveStore((state) => state.spreads)).sort((a, b) => b.spread - a.spread);

  return (
    <View style={{ gap: 12 }}>
      {spreads.map((spread) => (
        <Card key={spread.pairId}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={{ color: theme.text, fontSize: 17, fontWeight: '700' }}>{spread.symbol}</Text>
            <Badge label={`${spread.spread.toFixed(2)} INR`} tone={spread.spread >= 10 ? 'danger' : 'accent'} />
          </View>
          <Text style={{ color: theme.muted }}>Spot {formatCurrency(spread.spotPrice)} · Future {formatCurrency(spread.futurePrice)}</Text>
          <Text style={{ color: theme.muted }}>Observed {formatDateTime(spread.observedAt)}</Text>
        </Card>
      ))}
    </View>
  );
};
''')

w('apps/mobile/src/components/AlertHistoryList.tsx', '''
import React from 'react';
import { Pressable, Text, View } from 'react-native';
import { Badge, Card, useTheme } from '@fo-scanner/ui';
import { formatCurrency, formatDateTime } from '@fo-scanner/shared';
import type { AlertHistoryItemDto } from '@fo-scanner/shared';

export const AlertHistoryList = ({ alerts, onAcknowledge }: { alerts: AlertHistoryItemDto[]; onAcknowledge?: (alertId: string) => void }) => {
  const theme = useTheme();
  return (
    <View style={{ gap: 12 }}>
      {alerts.map((alert) => (
        <Card key={alert.id}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={{ color: theme.text, fontSize: 16, fontWeight: '700' }}>{alert.symbol}</Text>
            <Badge label={`${alert.spread.toFixed(2)} INR`} tone={alert.acknowledgedAt ? 'neutral' : 'danger'} />
          </View>
          <Text style={{ color: theme.muted }}>Threshold {alert.threshold.toFixed(2)} · Freshness {alert.freshnessMs}ms</Text>
          <Text style={{ color: theme.muted }}>Spot {formatCurrency(alert.spotPrice)} · Future {formatCurrency(alert.futurePrice)}</Text>
          <Text style={{ color: theme.muted }}>Triggered {formatDateTime(alert.triggeredAt)}</Text>
          {!alert.acknowledgedAt && onAcknowledge ? (
            <Pressable onPress={() => onAcknowledge(alert.id)} style={{ paddingVertical: 8 }}>
              <Text style={{ color: theme.accent, fontWeight: '700' }}>Acknowledge</Text>
            </Pressable>
          ) : null}
        </Card>
      ))}
    </View>
  );
};
''')

w('apps/mobile/app/_layout.tsx', '''
import React from 'react';
import { Stack } from 'expo-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';

const client = new QueryClient();

export default function RootLayout() {
  return (
    <QueryClientProvider client={client}>
      <StatusBar style="auto" />
      <Stack screenOptions={{ headerShown: false }} />
    </QueryClientProvider>
  );
}
''')

w('apps/mobile/app/index.tsx', '''
import React from 'react';
import { Text } from 'react-native';
import { LoadingState, Screen, SectionHeader } from '@fo-scanner/ui';
import { useBootstrap } from '../src/hooks/use-bootstrap';

export default function IndexScreen() {
  const bootstrap = useBootstrap();

  return (
    <Screen>
      <SectionHeader title="Realtime F&O Scanner" subtitle="Bootstrapping local app session and restoring market connectivity." />
      {bootstrap.isError ? <Text>{String(bootstrap.error)}</Text> : <LoadingState label="Preparing your scanner workspace..." />}
    </Screen>
  );
}
''')

w('apps/mobile/app/connect.tsx', '''
import React from 'react';
import { Text, View } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import { useRouter } from 'expo-router';
import { Badge, Card, PrimaryButton, Screen, SectionHeader, useTheme } from '@fo-scanner/ui';
import { api } from '../src/lib/api';
import { mobileEnv } from '../src/lib/env';
import { useSessionStore } from '../src/store/session-store';

export default function ConnectScreen() {
  const router = useRouter();
  const theme = useTheme();
  const session = useSessionStore((state) => state.session);
  const [loading, setLoading] = React.useState(false);

  const handleConnect = async () => {
    try {
      setLoading(true);
      const { url } = await api.getConnectUrl(mobileEnv.EXPO_PUBLIC_UPSTOX_CALLBACK_URL);
      await WebBrowser.openBrowserAsync(url);
      router.replace('/auth/upstox-callback');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <SectionHeader title="Connect Upstox" subtitle="Use hosted Upstox OAuth, exchange the auth code on the backend, and start V3 market-feed streaming." />
      <Card>
        <Badge label={session?.brokerConnection?.status ?? 'idle'} tone={session?.brokerConnection?.status === 'connected' ? 'success' : 'warning'} />
        <Text style={{ color: theme.text, fontSize: 18, fontWeight: '700' }}>Broker connection required</Text>
        <Text style={{ color: theme.muted, lineHeight: 22 }}>
          The scanner only subscribes after a valid Upstox account is linked. OAuth state and token storage are handled by the backend.
        </Text>
        <PrimaryButton title={loading ? 'Opening Upstox…' : 'Connect Upstox'} onPress={() => void handleConnect()} disabled={loading} />
      </Card>
      <View style={{ gap: 8 }}>
        <PrimaryButton title="Continue in offline shell" onPress={() => router.replace('/(tabs)/dashboard')} />
      </View>
    </Screen>
  );
}
''')

w('apps/mobile/app/auth/upstox-callback.tsx', '''
import React from 'react';
import { useRouter } from 'expo-router';
import { LoadingState, Screen, SectionHeader } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';
import { useSessionStore } from '../../src/store/session-store';

export default function UpstoxCallbackScreen() {
  const router = useRouter();
  const session = useSessionStore((state) => state.session);
  const setSession = useSessionStore((state) => state.setSession);

  React.useEffect(() => {
    const refresh = async () => {
      if (!session) {
        router.replace('/');
        return;
      }
      const authStatus = await api.getAuthStatus();
      setSession({ ...session, brokerConnection: authStatus.brokerConnection, settings: session.settings, user: session.user, token: session.token });
      router.replace('/(tabs)/dashboard');
    };
    void refresh();
  }, [router, session, setSession]);

  return (
    <Screen>
      <SectionHeader title="Finalizing Upstox link" subtitle="Refreshing broker status and restarting live subscriptions." />
      <LoadingState label="Just a moment…" />
    </Screen>
  );
}
''')

w('apps/mobile/app/(tabs)/_layout.tsx', '''
import React from 'react';
import { Tabs } from 'expo-router';

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ headerShown: false }}>
      <Tabs.Screen name="dashboard" options={{ title: 'Dashboard' }} />
      <Tabs.Screen name="scanner" options={{ title: 'Scanner' }} />
      <Tabs.Screen name="history" options={{ title: 'History' }} />
      <Tabs.Screen name="watchlist" options={{ title: 'Watchlist' }} />
      <Tabs.Screen name="settings" options={{ title: 'Settings' }} />
      <Tabs.Screen name="status" options={{ title: 'Status' }} />
    </Tabs>
  );
}
''')

w('apps/mobile/app/(tabs)/dashboard.tsx', '''
import React from 'react';
import { Text, View } from 'react-native';
import { Badge, Card, MetricCard, Screen, SectionHeader, Sparkline, useTheme } from '@fo-scanner/ui';
import { useDashboard } from '../../src/hooks/use-dashboard';
import { ResponsiveGrid } from '../../src/components/ResponsiveGrid';
import { useLiveStore } from '../../src/store/live-store';

export default function DashboardScreen() {
  const theme = useTheme();
  const { data, isLoading } = useDashboard();
  const spreads = Object.values(useLiveStore((state) => state.spreads)).map((item) => item.spread);

  return (
    <Screen>
      <SectionHeader title="Dashboard" subtitle="Realtime summary of broker connectivity, live subscriptions, and active backwardation opportunities." />
      {isLoading || !data ? null : (
        <ResponsiveGrid>
          <MetricCard label="Active connection" value={data.activeConnection ? 'Online' : 'Offline'} helper={data.marketDataState} tone={data.activeConnection ? 'success' : 'warning'} />
          <MetricCard label="Subscribed symbols" value={String(data.subscribedInstrumentCount)} helper={`Threshold ${data.threshold}`} />
          <MetricCard label="Active watchlist" value={String(data.activeWatchlistCount)} helper={`WS ${data.websocketState}`} />
          <MetricCard label="Live alerts" value={String(data.liveAlertCount)} helper={`${data.backendLatencyMs}ms backend`} tone={data.liveAlertCount ? 'danger' : 'accent'} />
        </ResponsiveGrid>
      )}
      <Card>
        <Badge label={data?.marketDataState ?? 'loading'} tone={data?.marketDataState === 'connected' ? 'success' : 'warning'} />
        <Text style={{ color: theme.text, fontSize: 18, fontWeight: '700' }}>Spread activity</Text>
        <Sparkline points={spreads.length ? spreads : [0, 0, 0, 0]} width={260} height={64} />
        <Text style={{ color: theme.muted }}>Last tick {data?.lastTickAt ?? '—'}</Text>
      </Card>
      <Card>
        <Text style={{ color: theme.text, fontSize: 18, fontWeight: '700' }}>Realtime behavior</Text>
        <View style={{ gap: 8 }}>
          <Text style={{ color: theme.muted }}>• Broker auth state, websocket fanout, and market-feed state are shown together so reconnect issues are obvious.</Text>
          <Text style={{ color: theme.muted }}>• Live spreads are throttled visually to avoid noisy flashing while critical alerts still push immediately.</Text>
        </View>
      </Card>
    </Screen>
  );
}
''')

w('apps/mobile/app/(tabs)/scanner.tsx', '''
import React from 'react';
import { EmptyState, Screen, SectionHeader } from '@fo-scanner/ui';
import { LiveSpreadList } from '../../src/components/LiveSpreadList';
import { useLiveStore } from '../../src/store/live-store';

export default function ScannerScreen() {
  const spreads = Object.values(useLiveStore((state) => state.spreads));
  return (
    <Screen>
      <SectionHeader title="Live scanner" subtitle="Streaming spot-vs-near-future spreads from the backend websocket." />
      {spreads.length ? <LiveSpreadList /> : <EmptyState title="No live spreads yet" subtitle="Connect Upstox and add watchlist symbols to start receiving realtime spreads." />}
    </Screen>
  );
}
''')

w('apps/mobile/app/(tabs)/history.tsx', '''
import React from 'react';
import { RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { EmptyState, Screen, SectionHeader } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';
import { AlertHistoryList } from '../../src/components/AlertHistoryList';
import { useLiveStore } from '../../src/store/live-store';

export default function HistoryScreen() {
  const { data, isFetching, refetch } = useQuery({ queryKey: ['alert-history'], queryFn: () => api.getAlertHistory() });
  const setAlerts = useLiveStore((state) => state.setAlerts);

  React.useEffect(() => {
    if (data) setAlerts(data);
  }, [data, setAlerts]);

  const alerts = useLiveStore((state) => state.alerts);

  return (
    <Screen>
      <SectionHeader title="Alert history" subtitle="Persisted backwardation alerts with acknowledgement support and refresh behavior." />
      {alerts.length ? (
        <AlertHistoryList alerts={alerts} onAcknowledge={(id) => void api.acknowledgeAlert(id).then(() => refetch())} />
      ) : (
        <EmptyState title="No alerts yet" subtitle="Historical alerts will appear here after the first threshold breach is detected." />
      )}
    </Screen>
  );
}
''')

w('apps/mobile/app/(tabs)/watchlist.tsx', '''
import React from 'react';
import { Pressable, Text, TextInput, View } from 'react-native';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Badge, Card, EmptyState, PrimaryButton, Screen, SectionHeader, useTheme } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';

export default function WatchlistScreen() {
  const theme = useTheme();
  const queryClient = useQueryClient();
  const [symbol, setSymbol] = React.useState('RELIANCE');
  const { data } = useQuery({ queryKey: ['watchlist'], queryFn: () => api.getWatchlist() });
  const mutation = useMutation({
    mutationFn: () => api.upsertWatchlist({ symbol, exchange: 'NSE', segment: 'NSE_FO', preferredMonthOffset: 0, enabled: true }),
    onSuccess: () => {
      setSymbol('');
      void queryClient.invalidateQueries({ queryKey: ['watchlist'] });
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
    }
  });

  return (
    <Screen>
      <SectionHeader title="Watchlist" subtitle="Manage underlying symbols that should be paired with spot and near-month futures contracts." />
      <Card>
        <TextInput value={symbol} onChangeText={setSymbol} placeholder="Enter symbol e.g. TCS" placeholderTextColor={theme.muted} style={{ borderColor: theme.border, borderWidth: 1, borderRadius: 14, padding: 14, color: theme.text }} />
        <PrimaryButton title={mutation.isPending ? 'Saving…' : 'Add symbol'} onPress={() => mutation.mutate()} disabled={!symbol.trim() || mutation.isPending} />
      </Card>
      {data?.length ? (
        <View style={{ gap: 12 }}>
          {data.map((item) => (
            <Card key={item.id}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text style={{ color: theme.text, fontWeight: '700', fontSize: 16 }}>{item.symbol}</Text>
                <Badge label={item.enabled ? 'enabled' : 'disabled'} tone={item.enabled ? 'success' : 'warning'} />
              </View>
              <Text style={{ color: theme.muted }}>Spot: {item.spotInstrument?.instrumentKey ?? 'unpaired'}</Text>
              <Text style={{ color: theme.muted }}>Future: {item.futureInstrument?.instrumentKey ?? 'unpaired'}</Text>
              <Pressable onPress={() => void api.deleteWatchlist(item.id).then(() => queryClient.invalidateQueries({ queryKey: ['watchlist'] }))}>
                <Text style={{ color: theme.danger, fontWeight: '700' }}>Remove</Text>
              </Pressable>
            </Card>
          ))}
        </View>
      ) : (
        <EmptyState title="No watchlist symbols" subtitle="Add one or more F&O underlyings to let the backend pair them with spot and futures contracts." />
      )}
    </Screen>
  );
}
''')

w('apps/mobile/app/(tabs)/settings.tsx', '''
import React from 'react';
import { Switch, Text, TextInput, View } from 'react-native';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Card, PrimaryButton, Screen, SectionHeader, useTheme } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';

export default function SettingsScreen() {
  const theme = useTheme();
  const { data } = useQuery({ queryKey: ['settings'], queryFn: () => api.getSettings() });
  const [threshold, setThreshold] = React.useState('10');
  const [cooldownMs, setCooldownMs] = React.useState('30000');
  const [freshnessMs, setFreshnessMs] = React.useState('10000');
  const [darkMode, setDarkMode] = React.useState(true);

  React.useEffect(() => {
    if (!data) return;
    setThreshold(String(data.threshold));
    setCooldownMs(String(data.cooldownMs));
    setFreshnessMs(String(data.freshnessMs));
    setDarkMode(data.darkMode);
  }, [data]);

  const mutation = useMutation({
    mutationFn: () =>
      api.updateSettings({
        threshold: Number(threshold),
        cooldownMs: Number(cooldownMs),
        freshnessMs: Number(freshnessMs),
        preferredExchange: data?.preferredExchange ?? 'NSE',
        darkMode,
        exchanges: data?.exchanges ?? ['NSE'],
        segments: data?.segments ?? ['NSE_EQ', 'NSE_FO']
      })
  });

  return (
    <Screen>
      <SectionHeader title="Settings" subtitle="Tune threshold, cooldown, freshness windows, and local display preferences." />
      <Card>
        <Text style={{ color: theme.text, fontWeight: '700' }}>Alert threshold (INR)</Text>
        <TextInput value={threshold} onChangeText={setThreshold} keyboardType="numeric" style={{ borderColor: theme.border, borderWidth: 1, borderRadius: 14, padding: 14, color: theme.text }} />
        <Text style={{ color: theme.text, fontWeight: '700' }}>Cooldown (ms)</Text>
        <TextInput value={cooldownMs} onChangeText={setCooldownMs} keyboardType="numeric" style={{ borderColor: theme.border, borderWidth: 1, borderRadius: 14, padding: 14, color: theme.text }} />
        <Text style={{ color: theme.text, fontWeight: '700' }}>Freshness window (ms)</Text>
        <TextInput value={freshnessMs} onChangeText={setFreshnessMs} keyboardType="numeric" style={{ borderColor: theme.border, borderWidth: 1, borderRadius: 14, padding: 14, color: theme.text }} />
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <Text style={{ color: theme.text, fontWeight: '700' }}>Dark mode preference</Text>
          <Switch value={darkMode} onValueChange={setDarkMode} />
        </View>
        <PrimaryButton title={mutation.isPending ? 'Saving…' : 'Save settings'} onPress={() => mutation.mutate()} disabled={mutation.isPending} />
      </Card>
    </Screen>
  );
}
''')

w('apps/mobile/app/(tabs)/status.tsx', '''
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Badge, Card, DataRow, EmptyState, Screen, SectionHeader } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';

export default function StatusScreen() {
  const { data } = useQuery({ queryKey: ['system-status'], queryFn: () => api.getSystemStatus(), refetchInterval: 5000 });
  if (!data) {
    return (
      <Screen>
        <SectionHeader title="System status" subtitle="Backend, database, websocket, broker auth, and market-feed diagnostics." />
        <EmptyState title="Waiting for status" subtitle="Status will load once the authenticated API session is ready." />
      </Screen>
    );
  }

  return (
    <Screen>
      <SectionHeader title="System status" subtitle="Backend, database, websocket, broker auth, and market-feed diagnostics." />
      <Card>
        <Badge label={data.backend} tone={data.backend === 'ok' ? 'success' : 'warning'} />
        <DataRow label="Database" value={data.database} />
        <DataRow label="Broker auth" value={data.brokerAuth} />
        <DataRow label="Websocket" value={data.websocket} />
        <DataRow label="Market feed" value={data.marketFeed} />
        <DataRow label="Instrument sync" value={data.instrumentSyncAt ?? '—'} />
      </Card>
      {data.recentEvents.map((event) => (
        <Card key={event.id}>
          <Badge label={event.level} tone={event.level === 'critical' ? 'danger' : event.level === 'warning' ? 'warning' : 'accent'} />
          <DataRow label={event.type} value={event.createdAt} />
          <DataRow label="Message" value={event.message} />
        </Card>
      ))}
    </Screen>
  );
}
''')

w('apps/mobile/__tests__/dashboard.test.tsx', '''
import React from 'react';
import { render } from '@testing-library/react-native';
import DashboardScreen from '../app/(tabs)/dashboard';

describe('DashboardScreen', () => {
  it('renders without crashing', () => {
    const screen = render(<DashboardScreen />);
    expect(screen.toJSON()).toBeTruthy();
  });
});
''')

w('apps/mobile/__tests__/connect.test.tsx', '''
import React from 'react';
import { render } from '@testing-library/react-native';
import ConnectScreen from '../app/connect';

describe('ConnectScreen', () => {
  it('renders connect CTA', () => {
    const screen = render(<ConnectScreen />);
    expect(screen.getByText(/Connect Upstox/i)).toBeTruthy();
  });
});
''')

print('Mobile generated.')
