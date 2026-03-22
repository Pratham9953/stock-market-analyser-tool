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
