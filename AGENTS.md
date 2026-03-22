# AGENTS.md

## Project overview
Production-grade realtime F&O backwardation scanner built on Upstox Market Data Feed V3, Fastify + TypeScript backend, PostgreSQL + TypeORM persistence, and Expo React Native frontend for Android, iOS, and web.

## Mission
Detect backwardation opportunities in realtime using:
- spread = spot_price - near_month_futures_price
- default trigger = spread >= 10 INR

The system must keep the realtime feed path healthy, decode V3 protobuf payloads correctly, push live opportunities to clients over websocket, and persist alert history.

## Core rules
- Never use Upstox websocket V2.
- Never hardcode secrets.
- Never bypass OAuth.
- Never break the realtime feed path.
- Never replace production logic with mock or demo logic outside test files.
- Always keep TypeScript strict.
- Always preserve shared type contracts between backend and frontend.
- Always update tests when behavior changes.
- Always keep environment handling centralized and validated.

## Commands
- install: `pnpm install`
- lint: `pnpm lint`
- typecheck: `pnpm typecheck`
- test: `pnpm test`
- build: `pnpm build`
- dev: `pnpm dev`
- docker:up: `pnpm docker:up`
- docker:down: `pnpm docker:down`

## Code style
- Prefer small, focused modules.
- Keep hot market-data processing non-blocking.
- Use structured logging only.
- Validate all external inputs with Zod or typed guards.
- Keep repository and provider logic behind abstractions.
- Write comments that explain intent, not syntax.
- Do not leak tokens or PII to logs.

## Architecture rules
- Backend must remain modular and testable.
- Hot market-data path must stay non-blocking.
- External broker/provider logic must stay behind adapters.
- Persistence logic must stay behind repositories/services.
- Realtime client delivery must be abstracted to support horizontal scaling later.
- UI must remain responsive across mobile and web.
- Shared schemas in `packages/shared` are the source of truth for DTOs/events.

## Testing policy
- Add or update unit tests for all business logic changes.
- Add or update integration tests for API contract changes.
- Add or update frontend tests for behavioral changes.
- Keep mocks realistic for Upstox auth callbacks, V3 websocket envelopes, and protobuf-decoded feeds.

## Security policy
- No secrets in code, docs, screenshots, logs, or tests.
- Sanitize logs.
- Validate OAuth state and websocket auth.
- Keep CORS and secure headers intact.
- Never weaken token encryption or session verification.

## Documentation policy
- Update README for setup changes.
- Update architecture docs for major flow changes.
- Keep folder tree, scripts, and sequence diagrams accurate.
