import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().int().positive().default(3000),
  LOG_LEVEL: z.enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace']).default('info'),
  APP_BASE_URL: z.string().url(),
  FRONTEND_WEB_URL: z.string().url(),
  FRONTEND_DEEP_LINK_BASE: z.string().min(1),
  CORS_ORIGIN: z.string().min(1),
  DATABASE_URL: z.string().min(1),
  APP_JWT_SECRET: z.string().min(32),
  TOKEN_ENCRYPTION_SECRET: z.string().min(16),
  UPSTOX_CLIENT_ID: z.string().min(1),
  UPSTOX_CLIENT_SECRET: z.string().min(1),
  UPSTOX_REDIRECT_URI: z.string().url(),
  UPSTOX_AUTH_DIALOG_URL: z.string().url(),
  UPSTOX_TOKEN_URL: z.string().url(),
  UPSTOX_MARKET_AUTHORIZE_V3_URL: z.string().url(),
  UPSTOX_BOD_INSTRUMENTS_URL: z.string().url(),
  DEFAULT_ALERT_THRESHOLD: z.coerce.number().default(10),
  DEFAULT_ALERT_COOLDOWN_MS: z.coerce.number().int().default(30_000),
  DEFAULT_TICK_FRESHNESS_MS: z.coerce.number().int().default(10_000),
  UPSTOX_MAX_CONNECTIONS: z.coerce.number().int().positive().max(5).default(2),
  UPSTOX_LTPC_PER_CONNECTION: z.coerce.number().int().positive().default(1000),
  UPSTOX_RECONNECT_BASE_MS: z.coerce.number().int().positive().default(1500),
  UPSTOX_RECONNECT_MAX_MS: z.coerce.number().int().positive().default(20_000),
  WS_BUFFER_DROP_THRESHOLD: z.coerce.number().int().positive().default(262_144),
  INSTRUMENT_SYNC_CRON: z.string().default('5 6 * * *')
});

export type AppEnv = z.infer<typeof envSchema>;

export const env = envSchema.parse(process.env);
