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
