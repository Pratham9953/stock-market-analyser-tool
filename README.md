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
