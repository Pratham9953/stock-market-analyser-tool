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
