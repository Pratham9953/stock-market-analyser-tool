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
