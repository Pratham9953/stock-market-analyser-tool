from pathlib import Path
from textwrap import dedent
root = Path('/mnt/data/fo-backwardation-scanner')

def w(path, content):
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dedent(content).lstrip('\n'))

w('apps/api/src/modules/market/spread-detector.service.test.ts', '''
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
''')

w('apps/api/src/infrastructure/security/crypto.test.ts', '''
import { decryptSecret, encryptSecret } from './crypto';

describe('token crypto', () => {
  it('round-trips encrypted broker tokens', () => {
    const encrypted = encryptSecret('super-secret-token');
    const decrypted = decryptSecret(encrypted);
    expect(decrypted).toBe('super-secret-token');
  });
});
''')

w('apps/api/src/routes/routes.contract.test.ts', '''
import Fastify from 'fastify';
import jwt from '@fastify/jwt';
import websocket from '@fastify/websocket';
import { registerRoutes } from './index';

describe('route contracts', () => {
  it('bootstraps a session through the public route', async () => {
    const app = Fastify();
    await app.register(jwt, { secret: 'test-test-test-test-test-test-test-test' });
    await app.register(websocket);

    await registerRoutes(app, {
      env: {} as never,
      sessionService: {
        bootstrap: vi.fn(async () => ({
          token: 'jwt',
          user: { id: '550e8400-e29b-41d4-a716-446655440000', deviceId: 'device-123456', displayName: 'Trader', createdAt: new Date().toISOString() },
          brokerConnection: null,
          settings: { threshold: 10, cooldownMs: 30000, freshnessMs: 10000, preferredExchange: 'NSE', darkMode: true }
        })),
        authenticate: vi.fn()
      } as never,
      oauthService: { getAuthStatus: vi.fn(), buildConnectUrl: vi.fn(), handleCallback: vi.fn(), disconnect: vi.fn() } as never,
      instrumentService: { search: vi.fn() } as never,
      watchlistService: { list: vi.fn(), upsert: vi.fn(), remove: vi.fn() } as never,
      settingsService: { getForUser: vi.fn(), updateForUser: vi.fn() } as never,
      alertsService: { history: vi.fn(), acknowledge: vi.fn() } as never,
      systemService: { getSummary: vi.fn(), getStatus: vi.fn() } as never,
      scannerOrchestrator: { refreshUser: vi.fn() } as never,
      clientHub: { connect: vi.fn() } as never
    });

    const response = await app.inject({
      method: 'POST',
      url: '/v1/session/bootstrap',
      payload: { deviceId: 'device-123456' }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json().token).toBe('jwt');
  });
});
''')

w('apps/mobile/src/store/live-store.test.ts', '''
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
''')

w('apps/mobile/jest.setup.ts', '''
import '@testing-library/jest-native/extend-expect';

jest.mock('expo-router', () => ({
  useRouter: () => ({ replace: jest.fn(), push: jest.fn() }),
  Stack: ({ children }: { children: React.ReactNode }) => children,
  Tabs: ({ children }: { children: React.ReactNode }) => children
}));
''')

w('apps/mobile/__tests__/dashboard.test.tsx', '''
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react-native';
import DashboardScreen from '../app/(tabs)/dashboard';

jest.mock('../src/hooks/use-dashboard', () => ({
  useDashboard: () => ({
    data: {
      activeConnection: true,
      subscribedInstrumentCount: 4,
      activeWatchlistCount: 2,
      liveAlertCount: 1,
      lastTickAt: new Date().toISOString(),
      backendLatencyMs: 12,
      websocketState: 'connected',
      marketDataState: 'connected',
      threshold: 10
    },
    isLoading: false
  })
}));

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>
);

describe('DashboardScreen', () => {
  it('renders dashboard heading', () => {
    const screen = render(<DashboardScreen />, { wrapper: Wrapper });
    expect(screen.getByText(/Dashboard/i)).toBeTruthy();
  });
});
''')

w('apps/mobile/__tests__/connect.test.tsx', '''
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react-native';
import ConnectScreen from '../app/connect';

jest.mock('../src/lib/api', () => ({
  api: {
    getConnectUrl: jest.fn(async () => ({ url: 'https://example.com' }))
  }
}));

jest.mock('expo-web-browser', () => ({
  openAuthSessionAsync: jest.fn(async () => ({ type: 'dismiss' }))
}));

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>
);

describe('ConnectScreen', () => {
  it('renders broker connection CTA', () => {
    const screen = render(<ConnectScreen />, { wrapper: Wrapper });
    expect(screen.getByText(/Connect Upstox/i)).toBeTruthy();
  });
});
''')

w('playwright.config.ts', '''
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  retries: 1,
  use: {
    baseURL: 'http://127.0.0.1:19006',
    headless: true
  },
  webServer: {
    command: 'pnpm --filter @fo-scanner/mobile web',
    port: 19006,
    reuseExistingServer: true,
    timeout: 120000
  }
});
''')

w('tests/e2e/smoke.spec.ts', '''
import { test, expect } from '@playwright/test';

test('web shell renders connect or dashboard copy', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText(/Realtime F&O Scanner|Connect Upstox|Dashboard/i)).toBeVisible();
});
''')

w('README.md', '''
# Realtime F&O Backwardation Scanner

Production-grade monorepo for detecting backwardation opportunities in Indian F&O using Upstox OAuth + Market Data Feed V3, Fastify + TypeScript, PostgreSQL + TypeORM, and Expo React Native for Android, iOS, and web.

## What it does

The scanner monitors spot and near-month futures pairs and computes:

```text
spread = spot_price - near_month_futures_price
```

An alert is created when `spread >= threshold`, where the default threshold is `10 INR`.

## Stack

- Backend: Fastify, TypeScript strict mode, TypeORM, PostgreSQL, Pino
- Broker integration: Upstox OAuth 2.0, Market Data Feed V3, Protobuf decoding
- Frontend: Expo Router, React Native, TanStack Query, Zustand
- Shared contracts: `packages/shared`
- Reusable UI: `packages/ui`
- Testing: Vitest, Jest, Playwright
- Monorepo: pnpm workspaces + Turbo

## Why the implementation looks this way

Upstox Market Data Feed V3 requires three things that shape the architecture:
1. OAuth hosted login and backend auth-code exchange.
2. One-time WebSocket authorize URLs per connection.
3. Binary websocket messages plus protobuf decoding for live market ticks.

The backend therefore keeps broker-specific logic behind an adapter, uses a scanner orchestrator to manage per-user feed workers, and uses a websocket client hub to fan out live spreads and alerts to mobile/web clients. Upstox V3 limits include 2 concurrent websocket connections per user with LTPC subscriptions capped at 5000 instrument keys individually and 2000 combined, while standard REST APIs are rate-limited to 50 requests per second, 500 per minute, and 2000 per 30 minutes. citeturn268060view0turn135326view2turn921678search0

## Monorepo tree

See [`docs/tree.md`](docs/tree.md) for the generated tree.

## Quick start

### 1) Install

```bash
pnpm install
```

### 2) Copy env files

```bash
cp apps/api/.env.example apps/api/.env
cp apps/mobile/.env.example apps/mobile/.env
```

Fill in your real Upstox values only in env files.

### 3) Start PostgreSQL

```bash
pnpm docker:up
```

### 4) Run locally

```bash
pnpm dev
```

API: `http://localhost:3000`
Expo web: `http://localhost:19006`
Swagger: `http://localhost:3000/docs`

### 5) Optional database utilities

```bash
pnpm --filter @fo-scanner/api db:migrate
pnpm --filter @fo-scanner/api db:seed
```

## Key flows

### Upstox connect flow

- App bootstraps a local session via `/v1/session/bootstrap`
- User taps **Connect Upstox**
- Backend creates an OAuth state record and returns the hosted Upstox auth URL
- Upstox redirects to backend callback with `code` and `state`
- Backend exchanges code at `https://api.upstox.com/v2/login/authorization/token`
- Encrypted token is stored in PostgreSQL and scanner workers refresh

Upstox documents the hosted auth dialog at `https://api.upstox.com/v2/login/authorization/dialog`, returns the authorization code to the registered `redirect_uri`, and states that the access token acquired through token exchange remains valid until 3:30 AM the following day. citeturn921678search0turn135326view0turn135326view1

### Instrument workflow

- Download BOD instrument JSON from Upstox assets
- Persist normalized instruments
- Pair watchlist underlyings with spot EQ/INDEX instruments
- Resolve nearest tradable futures using `underlying_key` + earliest future expiry

Upstox recommends using `instrument_key` instead of exchange tokens, using JSON instrument files instead of CSV, and notes that the BOD files refresh daily around 6 AM. citeturn268060view2

### Realtime market feed

- Backend fetches the V3 market-feed authorize URL
- Connects via websocket to the one-time `authorized_redirect_uri`
- Sends binary subscription payloads
- Decodes protobuf messages using the official Market Data V3 proto
- Maintains in-memory last ticks and evaluates spreads
- Persists alerts and pushes websocket updates to the client app

Upstox states that V3 websocket requests must be sent in binary format, the feed uses protobuf encoding, the first message is market status, and the next message is a snapshot before live updates continue. The V3 websocket also replaces the discontinued V2 market feed. citeturn268060view0turn268060view1turn198405search1turn809607view0

## Commands

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm docker:up
pnpm docker:down
```

## Security notes

- No secrets in source control
- JWT app sessions + OAuth state records
- Encrypted broker token persistence (AES-256-GCM)
- Helmet + CORS + Fastify rate limits
- Safe log redaction for auth headers and token material
- Secure websocket handshake using the app JWT

## Docs

- [`docs/architecture.md`](docs/architecture.md)
- [`docs/api.md`](docs/api.md)
- [`docs/sequence-diagrams.md`](docs/sequence-diagrams.md)
- [`docs/troubleshooting.md`](docs/troubleshooting.md)
- [`docs/tree.md`](docs/tree.md)
''')

w('docs/architecture.md', '''
# Architecture

## Overview

The system is split into four layers:

1. **Frontend shell** (`apps/mobile`)
   - Expo Router app shared across Android, iOS, and web.
   - TanStack Query for server state.
   - Zustand for realtime session/live spreads.
   - A dedicated websocket client for push updates.

2. **Shared contracts** (`packages/shared`)
   - API DTOs
   - Websocket event schemas
   - Env validation for the frontend
   - Formatting helpers and shared types

3. **Backend core** (`apps/api`)
   - Fastify HTTP + websocket server
   - Session bootstrap and Upstox OAuth callback handling
   - Instrument sync service
   - Pairing service
   - Scanner orchestrator with per-user workers
   - Alert persistence and history APIs

4. **Provider adapter** (`apps/api/src/infrastructure/providers/upstox`)
   - OAuth code exchange
   - Market Data Feed V3 authorize URL retrieval
   - Instrument-file download
   - Protobuf-based feed decoding

## Realtime path

```text
Upstox V3 websocket -> per-user scanner worker -> latest tick store
-> spread detector -> alert persistence -> websocket fanout -> Expo client
```

### Design choices

- **Per-user scanner workers** preserve broker/account isolation.
- **LatestTickStore** keeps hot-path computation in memory and bounded.
- **ClientHub** isolates websocket fanout so Redis or external pub/sub can be inserted later.
- **PairingService** resolves spot/future mapping from official metadata instead of hardcoding symbols.
- **SettingsService** keeps alert threshold, cooldown, and freshness configurable per user.

## Scalability notes

- Instrument subscriptions are chunked per connection to respect Upstox per-user limits.
- Backpressure protection avoids sending noisy low-priority websocket events if a client buffer grows too large.
- Market data processing never blocks on database writes longer than the async alert-persist step.
- Client fanout is abstracted behind `ClientHub` so a Redis-backed multi-instance hub can replace it later.
- REST traffic to Upstox goes through a rate-limited HTTP client with retry/backoff.

## Persistence model

Primary entities:
- User
- AppSession
- BrokerConnection
- BrokerAccessToken
- Instrument
- InstrumentPair
- Alert
- Watchlist
- UserSetting
- OAuthState
- SystemEvent

## Operational notes

- Instrument sync runs at startup and then via cron.
- Scanner workers start for users with active broker connections.
- Watchlist/settings changes trigger worker refreshes.
- Health endpoints are lightweight and unauthenticated.
''')

w('docs/api.md', '''
# API

## Public

### `POST /v1/session/bootstrap`
Create or restore a local app session.

Request:
```json
{
  "deviceId": "device-123456",
  "displayName": "Local Trader"
}
```

Response includes app JWT, user payload, broker status, and default settings.

### `GET /health/live`
Liveness probe.

### `GET /health/ready`
Readiness probe.

## Authenticated

All routes below require `Authorization: Bearer <app-jwt>`.

### `GET /v1/auth/status`
Returns broker-link status and whether re-auth is required.

### `GET /v1/brokers/upstox/connect-url?frontendRedirectUri=...`
Returns hosted Upstox auth URL.

### `DELETE /v1/brokers/upstox/connection`
Disconnect broker token locally.

### `GET /v1/dashboard/summary`
Summary cards used by the dashboard screen.

### `GET /v1/alerts`
Fetch persisted alert history.

### `POST /v1/alerts/:id/ack`
Acknowledge a single alert.

### `GET /v1/watchlist`
Fetch watchlist with resolved spot/future instrument pairing.

### `POST /v1/watchlist`
Create or update a watchlist symbol.

### `DELETE /v1/watchlist/:id`
Remove a watchlist item.

### `GET /v1/instruments/search?q=RELIANCE`
Search local instrument catalog.

### `GET /v1/settings`
Fetch user settings.

### `PUT /v1/settings`
Update threshold, cooldown, freshness, and display settings.

### `GET /v1/system/status`
Diagnostics and recent system events.

## Websocket

### `GET /v1/ws/live?token=<app-jwt>`
Authenticated websocket endpoint for live events.

Event types:
- `scanner.spread`
- `alert.created`
- `dashboard.summary`
- `system.status`
- `system.heartbeat`
''')

w('docs/sequence-diagrams.md', '''
# Sequence Diagrams

## OAuth connect

```text
User -> Expo app: tap Connect Upstox
Expo app -> API: GET /v1/brokers/upstox/connect-url
API -> DB: store OAuthState
API -> Expo app: hosted auth URL
Expo app -> Upstox: open auth dialog
Upstox -> API callback: code + state
API -> Upstox token endpoint: exchange code
API -> DB: store encrypted token + update broker connection
API -> Expo callback route: redirect success
Expo app -> API: GET /v1/auth/status
```

## Realtime scan

```text
ScannerOrchestrator -> InstrumentService: sync BOD instruments
ScannerOrchestrator -> PairingService: resolve spot/future pairs
ScannerOrchestrator -> Upstox authorize V3: get authorized websocket URL
ScannerOrchestrator -> Upstox websocket: subscribe (binary request)
Upstox websocket -> Worker: protobuf ticks
Worker -> LatestTickStore: update spot/future last tick
Worker -> SpreadDetector: evaluate spread + cooldown
SpreadDetector -> AlertsService: persist alert if breached
AlertsService -> ClientHub: push alert.created
ClientHub -> Expo app: websocket event
```
''')

w('docs/troubleshooting.md', '''
# Troubleshooting

## OAuth redirect mismatch
- Ensure `UPSTOX_REDIRECT_URI` matches the exact redirect URI configured in your Upstox developer app.
- Ensure the frontend callback URL passed to `/v1/brokers/upstox/connect-url` is reachable on your current platform.

## 401 from token exchange
- Verify `UPSTOX_CLIENT_ID`, `UPSTOX_CLIENT_SECRET`, and the auth `code` are correct.
- Remember the auth code is single-use.
- Upstox returns this when client credentials or redirect URI are wrong. citeturn135326view1

## Websocket connects but no data arrives
- Confirm the Upstox broker token is still valid.
- Confirm your watchlist symbols resolved to both spot and future instruments.
- Confirm the websocket is subscribing in binary mode.
- Check system status screen and API logs for market segment state.

## Instrument pairing missing futures
- Ensure the BOD instrument file finished syncing.
- Confirm the underlying actually has an F&O contract on the selected exchange.
- Near-month pairing relies on `underlying_key` plus earliest future expiry.

## Database migration problems
- Ensure PostgreSQL 16+ is reachable.
- The initial migration enables `pgcrypto` to support `gen_random_uuid()`.

## Expo web cannot reach API
- Confirm `EXPO_PUBLIC_API_URL` and `CORS_ORIGIN` agree.
- If you are using Docker, keep API on `localhost:3000` and Expo web on `localhost:19006`.
''')
