from pathlib import Path
from textwrap import dedent

root = Path('/mnt/data/fo-backwardation-scanner')

def w(path: str, content: str):
    file_path = root / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(dedent(content).lstrip('\n'), encoding='utf-8')

w('apps/api/package.json', '''
{
  "name": "@fo-scanner/api",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsup src/index.ts --format esm --dts --out-dir dist --external @fo-scanner/shared",
    "lint": "eslint src --ext .ts",
    "typecheck": "tsc --project tsconfig.json --noEmit",
    "test": "vitest run",
    "clean": "rimraf dist coverage",
    "db:migrate": "tsx ./src/infrastructure/db/run-migrations.ts",
    "db:seed": "tsx ./src/seeds/bootstrap.ts"
  },
  "dependencies": {
    "@fastify/cors": "^11.0.1",
    "@fastify/helmet": "^13.0.1",
    "@fastify/jwt": "^10.0.0",
    "@fastify/rate-limit": "^10.3.0",
    "@fastify/swagger": "^9.5.1",
    "@fastify/swagger-ui": "^5.2.3",
    "@fastify/websocket": "^11.0.2",
    "@fo-scanner/shared": "workspace:*",
    "axios": "^1.9.0",
    "axios-retry": "^4.5.0",
    "bottleneck": "^2.19.5",
    "fastify": "^5.3.2",
    "lru-cache": "^11.1.0",
    "node-cron": "^4.2.1",
    "pino": "^9.7.0",
    "pino-pretty": "^13.0.0",
    "protobufjs": "^7.5.3",
    "reflect-metadata": "^0.2.2",
    "typeorm": "^0.3.25",
    "pg": "^8.16.0",
    "uuid": "^11.1.0",
    "ws": "^8.18.2",
    "zod": "^3.24.4"
  },
  "devDependencies": {
    "@types/pg": "^8.15.4",
    "@types/ws": "^8.18.1",
    "supertest": "^7.1.1",
    "tsup": "^8.5.0",
    "tsx": "^4.20.3",
    "vitest": "^3.2.4"
  }
}
''')

w('apps/api/tsconfig.json', '''
{
  "extends": "../../packages/config/tsconfig/node.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src",
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "types": ["node", "vitest/globals"],
    "module": "ESNext",
    "moduleResolution": "Bundler"
  },
  "include": ["src/**/*.ts"]
}
''')

w('apps/api/.env.example', '''
NODE_ENV=development
PORT=3000
LOG_LEVEL=info
APP_BASE_URL=http://localhost:3000
FRONTEND_WEB_URL=http://localhost:19006
FRONTEND_DEEP_LINK_BASE=fo-scanner://auth/upstox-callback
CORS_ORIGIN=http://localhost:19006,http://localhost:8081
DATABASE_URL=postgres://fo_scanner:fo_scanner@localhost:5432/fo_scanner
APP_JWT_SECRET=replace-with-a-long-random-secret
TOKEN_ENCRYPTION_SECRET=replace-with-a-32-byte-secret
UPSTOX_CLIENT_ID=replace-with-upstox-client-id
UPSTOX_CLIENT_SECRET=replace-with-upstox-client-secret
UPSTOX_REDIRECT_URI=http://localhost:3000/v1/brokers/upstox/callback
UPSTOX_AUTH_DIALOG_URL=https://api.upstox.com/v2/login/authorization/dialog
UPSTOX_TOKEN_URL=https://api.upstox.com/v2/login/authorization/token
UPSTOX_MARKET_AUTHORIZE_V3_URL=https://api.upstox.com/v3/feed/market-data-feed/authorize
UPSTOX_BOD_INSTRUMENTS_URL=https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz
DEFAULT_ALERT_THRESHOLD=10
DEFAULT_ALERT_COOLDOWN_MS=30000
DEFAULT_TICK_FRESHNESS_MS=10000
UPSTOX_MAX_CONNECTIONS=2
UPSTOX_LTPC_PER_CONNECTION=1000
UPSTOX_RECONNECT_BASE_MS=1500
UPSTOX_RECONNECT_MAX_MS=20000
WS_BUFFER_DROP_THRESHOLD=262144
INSTRUMENT_SYNC_CRON=5 6 * * *
''')

w('apps/api/Dockerfile', '''
FROM node:22-alpine AS base
WORKDIR /app
RUN corepack enable

COPY package.json pnpm-workspace.yaml turbo.json tsconfig.base.json .npmrc ./
COPY packages ./packages
COPY apps/api ./apps/api

RUN pnpm install --frozen-lockfile=false
RUN pnpm --filter @fo-scanner/api build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
RUN corepack enable
COPY --from=base /app /app
EXPOSE 3000
CMD ["pnpm", "--filter", "@fo-scanner/api", "start"]
''')

w('apps/api/vitest.config.ts', '''
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
    setupFiles: ['./src/tests/setup.ts']
  }
});
''')

w('apps/api/src/config/env.ts', '''
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
''')

w('apps/api/src/common/logger.ts', '''
import pino from 'pino';
import { env } from '../config/env';

export const logger = pino({
  level: env.LOG_LEVEL,
  transport:
    env.NODE_ENV === 'development'
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: 'SYS:standard',
            ignore: 'pid,hostname'
          }
        }
      : undefined,
  redact: {
    paths: [
      'req.headers.authorization',
      'headers.authorization',
      '*.accessToken',
      '*.extendedToken',
      '*.cipherText'
    ],
    censor: '[REDACTED]'
  }
});
''')

w('apps/api/src/common/errors.ts', '''
export class AppError extends Error {
  constructor(
    message: string,
    public readonly statusCode = 500,
    public readonly code = 'APP_ERROR',
    public readonly details?: unknown
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export const isAppError = (error: unknown): error is AppError => error instanceof AppError;
''')

w('apps/api/src/infrastructure/db/entities/base.entity.ts', '''
import { CreateDateColumn, PrimaryGeneratedColumn, UpdateDateColumn } from 'typeorm';

export abstract class BaseEntityWithAudit {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt!: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt!: Date;
}
''')

w('apps/api/src/infrastructure/db/entities/user.entity.ts', '''
import { Column, Entity, Index, OneToMany } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { AppSession } from './app-session.entity';
import { BrokerConnection } from './broker-connection.entity';
import { Alert } from './alert.entity';
import { Watchlist } from './watchlist.entity';
import { UserSetting } from './user-setting.entity';
import { OAuthState } from './oauth-state.entity';

@Entity('users')
export class User extends BaseEntityWithAudit {
  @Index({ unique: true })
  @Column({ type: 'varchar', length: 120 })
  deviceId!: string;

  @Column({ type: 'varchar', length: 120, default: 'Trader' })
  displayName!: string;

  @Column({ type: 'varchar', length: 30, default: 'active' })
  status!: 'active' | 'disabled';

  @OneToMany(() => AppSession, (session) => session.user)
  sessions!: AppSession[];

  @OneToMany(() => BrokerConnection, (connection) => connection.user)
  brokerConnections!: BrokerConnection[];

  @OneToMany(() => Alert, (alert) => alert.user)
  alerts!: Alert[];

  @OneToMany(() => Watchlist, (watchlist) => watchlist.user)
  watchlistEntries!: Watchlist[];

  @OneToMany(() => OAuthState, (state) => state.user)
  oauthStates!: OAuthState[];

  @OneToMany(() => UserSetting, (setting) => setting.user)
  settings!: UserSetting[];
}
''')

w('apps/api/src/infrastructure/db/entities/app-session.entity.ts', '''
import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';

@Entity('app_sessions')
export class AppSession extends BaseEntityWithAudit {
  @Index({ unique: true })
  @Column({ type: 'varchar', length: 120 })
  sessionKey!: string;

  @ManyToOne(() => User, (user) => user.sessions, { onDelete: 'CASCADE' })
  user!: User;

  @Column({ type: 'varchar', length: 255, nullable: true })
  userAgent!: string | null;

  @Column({ type: 'varchar', length: 64, nullable: true })
  ipAddress!: string | null;

  @Column({ type: 'timestamptz' })
  expiresAt!: Date;

  @Column({ type: 'boolean', default: true })
  isActive!: boolean;
}
''')

w('apps/api/src/infrastructure/db/entities/broker-connection.entity.ts', '''
import { Column, Entity, Index, ManyToOne, OneToMany } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';
import { BrokerAccessToken } from './broker-access-token.entity';

@Entity('broker_connections')
export class BrokerConnection extends BaseEntityWithAudit {
  @ManyToOne(() => User, (user) => user.brokerConnections, { onDelete: 'CASCADE' })
  user!: User;

  @Index()
  @Column({ type: 'varchar', length: 20, default: 'UPSTOX' })
  broker!: 'UPSTOX';

  @Column({ type: 'varchar', length: 40, default: 'idle' })
  status!: 'idle' | 'connecting' | 'connected' | 'expired' | 'error';

  @Index()
  @Column({ type: 'varchar', length: 120, nullable: true })
  brokerUserId!: string | null;

  @Column({ type: 'varchar', length: 120, nullable: true })
  accountName!: string | null;

  @Column({ type: 'timestamptz', nullable: true })
  connectedAt!: Date | null;

  @Column({ type: 'timestamptz', nullable: true })
  tokenExpiresAt!: Date | null;

  @Column({ type: 'timestamptz', nullable: true })
  lastHeartbeatAt!: Date | null;

  @Column({ type: 'timestamptz', nullable: true })
  lastAuthorizedAt!: Date | null;

  @OneToMany(() => BrokerAccessToken, (token) => token.connection)
  tokens!: BrokerAccessToken[];
}
''')

w('apps/api/src/infrastructure/db/entities/broker-access-token.entity.ts', '''
import { Column, Entity, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { BrokerConnection } from './broker-connection.entity';

@Entity('broker_access_tokens')
export class BrokerAccessToken extends BaseEntityWithAudit {
  @ManyToOne(() => BrokerConnection, (connection) => connection.tokens, { onDelete: 'CASCADE' })
  connection!: BrokerConnection;

  @Column({ type: 'text' })
  cipherText!: string;

  @Column({ type: 'varchar', length: 64 })
  iv!: string;

  @Column({ type: 'varchar', length: 64 })
  authTag!: string;

  @Column({ type: 'text', nullable: true })
  extendedCipherText!: string | null;

  @Column({ type: 'varchar', length: 64, nullable: true })
  extendedIv!: string | null;

  @Column({ type: 'varchar', length: 64, nullable: true })
  extendedAuthTag!: string | null;

  @Column({ type: 'timestamptz' })
  expiresAt!: Date;

  @Column({ type: 'boolean', default: true })
  isActive!: boolean;
}
''')

w('apps/api/src/infrastructure/db/entities/instrument.entity.ts', '''
import { Column, Entity, Index, OneToMany } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { InstrumentPair } from './instrument-pair.entity';

@Entity('instruments')
@Index(['instrumentKey'], { unique: true })
@Index(['underlyingKey'])
@Index(['tradingSymbol'])
@Index(['segment', 'instrumentType'])
export class Instrument extends BaseEntityWithAudit {
  @Column({ type: 'varchar', length: 120 })
  instrumentKey!: string;

  @Column({ type: 'varchar', length: 20 })
  exchange!: string;

  @Column({ type: 'varchar', length: 20 })
  segment!: string;

  @Column({ type: 'varchar', length: 40 })
  instrumentType!: string;

  @Column({ type: 'varchar', length: 120 })
  tradingSymbol!: string;

  @Column({ type: 'varchar', length: 120, nullable: true })
  shortName!: string | null;

  @Column({ type: 'varchar', length: 120, nullable: true })
  name!: string | null;

  @Column({ type: 'varchar', length: 120, nullable: true })
  underlyingKey!: string | null;

  @Column({ type: 'varchar', length: 20, nullable: true })
  underlyingType!: string | null;

  @Column({ type: 'date', nullable: true })
  expiryDate!: string | null;

  @Column({ type: 'float', nullable: true })
  lotSize!: number | null;

  @Column({ type: 'float', nullable: true })
  minimumLot!: number | null;

  @Column({ type: 'float', nullable: true })
  tickSize!: number | null;

  @Column({ type: 'varchar', length: 60, nullable: true })
  isin!: string | null;

  @Column({ type: 'boolean', default: true })
  isTradable!: boolean;

  @Column({ type: 'jsonb', default: {} })
  metadata!: Record<string, unknown>;

  @OneToMany(() => InstrumentPair, (pair) => pair.spotInstrument)
  spotPairs!: InstrumentPair[];

  @OneToMany(() => InstrumentPair, (pair) => pair.futureInstrument)
  futurePairs!: InstrumentPair[];
}
''')

w('apps/api/src/infrastructure/db/entities/instrument-pair.entity.ts', '''
import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { Instrument } from './instrument.entity';

@Entity('instrument_pairs')
@Index(['userId', 'symbol'], { unique: true })
export class InstrumentPair extends BaseEntityWithAudit {
  @Column({ type: 'uuid' })
  userId!: string;

  @Column({ type: 'varchar', length: 60 })
  symbol!: string;

  @ManyToOne(() => Instrument, (instrument) => instrument.spotPairs, { eager: true, nullable: true })
  spotInstrument!: Instrument | null;

  @ManyToOne(() => Instrument, (instrument) => instrument.futurePairs, { eager: true, nullable: true })
  futureInstrument!: Instrument | null;

  @Column({ type: 'varchar', length: 20, default: 'near' })
  monthType!: 'near' | 'next' | 'far';

  @Column({ type: 'date', nullable: true })
  futureExpiryDate!: string | null;

  @Column({ type: 'varchar', length: 30, default: 'paired' })
  status!: 'paired' | 'missing_spot' | 'missing_future';

  @Column({ type: 'boolean', default: true })
  enabled!: boolean;
}
''')

w('apps/api/src/infrastructure/db/entities/alert.entity.ts', '''
import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';
import { InstrumentPair } from './instrument-pair.entity';

@Entity('alerts')
@Index(['user', 'triggeredAt'])
@Index(['dedupeKey'])
export class Alert extends BaseEntityWithAudit {
  @ManyToOne(() => User, (user) => user.alerts, { onDelete: 'CASCADE', eager: true })
  user!: User;

  @ManyToOne(() => InstrumentPair, { eager: true, nullable: false, onDelete: 'CASCADE' })
  pair!: InstrumentPair;

  @Column({ type: 'float' })
  spread!: number;

  @Column({ type: 'float' })
  threshold!: number;

  @Column({ type: 'float' })
  spotPrice!: number;

  @Column({ type: 'float' })
  futurePrice!: number;

  @Column({ type: 'integer' })
  freshnessMs!: number;

  @Column({ type: 'varchar', length: 160 })
  dedupeKey!: string;

  @Column({ type: 'timestamptz' })
  triggeredAt!: Date;

  @Column({ type: 'timestamptz', nullable: true })
  acknowledgedAt!: Date | null;
}
''')

w('apps/api/src/infrastructure/db/entities/watchlist.entity.ts', '''
import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';

@Entity('watchlists')
@Index(['user', 'symbol'], { unique: true })
export class Watchlist extends BaseEntityWithAudit {
  @ManyToOne(() => User, (user) => user.watchlistEntries, { onDelete: 'CASCADE' })
  user!: User;

  @Column({ type: 'varchar', length: 60 })
  symbol!: string;

  @Column({ type: 'varchar', length: 20, default: 'NSE' })
  exchange!: string;

  @Column({ type: 'varchar', length: 20, default: 'NSE_FO' })
  segment!: string;

  @Column({ type: 'integer', default: 0 })
  preferredMonthOffset!: number;

  @Column({ type: 'boolean', default: true })
  enabled!: boolean;
}
''')

w('apps/api/src/infrastructure/db/entities/user-setting.entity.ts', '''
import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';

@Entity('user_settings')
@Index(['user'], { unique: true })
export class UserSetting extends BaseEntityWithAudit {
  @ManyToOne(() => User, (user) => user.settings, { onDelete: 'CASCADE' })
  user!: User;

  @Column({ type: 'float', default: 10 })
  threshold!: number;

  @Column({ type: 'integer', default: 30000 })
  cooldownMs!: number;

  @Column({ type: 'integer', default: 10000 })
  freshnessMs!: number;

  @Column({ type: 'varchar', length: 20, default: 'NSE' })
  preferredExchange!: string;

  @Column({ type: 'boolean', default: true })
  darkMode!: boolean;

  @Column({ type: 'jsonb', default: ['NSE'] })
  exchanges!: string[];

  @Column({ type: 'jsonb', default: ['NSE_EQ', 'NSE_FO'] })
  segments!: string[];
}
''')

w('apps/api/src/infrastructure/db/entities/oauth-state.entity.ts', '''
import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';

@Entity('oauth_states')
export class OAuthState extends BaseEntityWithAudit {
  @Index({ unique: true })
  @Column({ type: 'varchar', length: 120 })
  state!: string;

  @ManyToOne(() => User, (user) => user.oauthStates, { onDelete: 'CASCADE' })
  user!: User;

  @Column({ type: 'varchar', length: 20, default: 'UPSTOX' })
  broker!: 'UPSTOX';

  @Column({ type: 'varchar', length: 255 })
  frontendRedirectUri!: string;

  @Column({ type: 'timestamptz' })
  expiresAt!: Date;

  @Column({ type: 'timestamptz', nullable: true })
  consumedAt!: Date | null;
}
''')

w('apps/api/src/infrastructure/db/entities/system-event.entity.ts', '''
import { Column, Entity, Index } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';

@Entity('system_events')
@Index(['type', 'createdAt'])
export class SystemEvent extends BaseEntityWithAudit {
  @Column({ type: 'varchar', length: 20 })
  level!: 'info' | 'warning' | 'critical';

  @Column({ type: 'varchar', length: 80 })
  type!: string;

  @Column({ type: 'varchar', length: 255 })
  message!: string;

  @Column({ type: 'varchar', length: 80, default: 'system' })
  source!: string;

  @Column({ type: 'jsonb', default: {} })
  payload!: Record<string, unknown>;
}
''')

w('apps/api/src/infrastructure/db/data-source.ts', '''
import 'reflect-metadata';
import { DataSource } from 'typeorm';
import { env } from '../../config/env';
import { Alert } from './entities/alert.entity';
import { AppSession } from './entities/app-session.entity';
import { BrokerAccessToken } from './entities/broker-access-token.entity';
import { BrokerConnection } from './entities/broker-connection.entity';
import { Instrument } from './entities/instrument.entity';
import { InstrumentPair } from './entities/instrument-pair.entity';
import { OAuthState } from './entities/oauth-state.entity';
import { SystemEvent } from './entities/system-event.entity';
import { UserSetting } from './entities/user-setting.entity';
import { User } from './entities/user.entity';
import { Watchlist } from './entities/watchlist.entity';
import { InitialSchema1710000000000 } from '../../migrations/1710000000000-InitialSchema';

export const buildDataSource = () =>
  new DataSource({
    type: 'postgres',
    url: env.DATABASE_URL,
    synchronize: false,
    logging: false,
    entities: [
      User,
      AppSession,
      BrokerConnection,
      BrokerAccessToken,
      Instrument,
      InstrumentPair,
      Alert,
      Watchlist,
      UserSetting,
      OAuthState,
      SystemEvent
    ],
    migrations: [InitialSchema1710000000000]
  });
''')

w('apps/api/src/infrastructure/db/run-migrations.ts', '''
import { buildDataSource } from './data-source';
import { logger } from '../../common/logger';

const main = async () => {
  const dataSource = buildDataSource();
  await dataSource.initialize();
  await dataSource.runMigrations();
  logger.info('Migrations completed');
  await dataSource.destroy();
};

void main().catch((error) => {
  logger.error({ err: error }, 'Migration failed');
  process.exit(1);
});
''')

w('apps/api/src/infrastructure/security/crypto.ts', '''
import crypto from 'node:crypto';
import { env } from '../../config/env';

export type EncryptedPayload = {
  cipherText: string;
  iv: string;
  authTag: string;
};

const key = crypto.createHash('sha256').update(env.TOKEN_ENCRYPTION_SECRET).digest();

export const encryptSecret = (value: string): EncryptedPayload => {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const encrypted = Buffer.concat([cipher.update(value, 'utf8'), cipher.final()]);
  return {
    cipherText: encrypted.toString('base64'),
    iv: iv.toString('base64'),
    authTag: cipher.getAuthTag().toString('base64')
  };
};

export const decryptSecret = (payload: EncryptedPayload): string => {
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, Buffer.from(payload.iv, 'base64'));
  decipher.setAuthTag(Buffer.from(payload.authTag, 'base64'));
  const decrypted = Buffer.concat([
    decipher.update(Buffer.from(payload.cipherText, 'base64')),
    decipher.final()
  ]);
  return decrypted.toString('utf8');
};
''')

w('apps/api/src/infrastructure/http/rate-limited-http-client.ts', '''
import axios, { AxiosInstance } from 'axios';
import axiosRetry from 'axios-retry';
import Bottleneck from 'bottleneck';
import { logger } from '../../common/logger';

export class RateLimitedHttpClient {
  private readonly client: AxiosInstance;
  private readonly limiter: Bottleneck;

  constructor(baseURL?: string) {
    this.client = axios.create({ baseURL, timeout: 15_000 });
    axiosRetry(this.client, {
      retries: 3,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => axiosRetry.isNetworkOrIdempotentRequestError(error) || error.response?.status === 429
    });
    this.limiter = new Bottleneck({
      maxConcurrent: 5,
      minTime: 25,
      reservoir: 500,
      reservoirRefreshAmount: 500,
      reservoirRefreshInterval: 60_000
    });
  }

  async request<T>(factory: () => Promise<T>): Promise<T> {
    return this.limiter.schedule(factory).catch((error) => {
      logger.warn({ err: error }, 'Rate-limited HTTP request failed');
      throw error;
    });
  }

  get axios(): AxiosInstance {
    return this.client;
  }
}
''')

w('apps/api/src/infrastructure/providers/upstox/upstox-types.ts', '''
export type UpstoxTokenResponse = {
  email: string;
  exchanges: string[];
  products: string[];
  broker: 'UPSTOX';
  user_id: string;
  user_name: string;
  order_types: string[];
  user_type: string;
  poa: boolean;
  is_active: boolean;
  access_token: string;
  extended_token?: string;
};

export type UpstoxMarketAuthorizeResponse = {
  status: 'success' | 'error';
  data: {
    authorized_redirect_uri: string;
  };
};

export type UpstoxInstrumentRecord = {
  segment: string;
  name?: string;
  exchange: string;
  isin?: string;
  instrument_type: string;
  instrument_key: string;
  lot_size?: number;
  minimum_lot?: number;
  exchange_token?: string;
  tick_size?: number;
  trading_symbol: string;
  short_name?: string;
  security_type?: string;
  expiry?: string;
  underlying_key?: string;
  underlying_type?: string;
  [key: string]: unknown;
};

export type NormalizedTick = {
  instrumentKey: string;
  price: number;
  observedAt: Date;
  requestMode: string;
};
''')

w('apps/api/src/infrastructure/providers/upstox/market-data-v3.proto', '''
syntax = "proto3";
package com.upstox.marketdatafeederv3udapi.rpc.proto;
message LTPC { double ltp = 1; int64 ltt = 2; int64 ltq = 3; double cp = 4; }
message MarketLevel { repeated Quote bidAskQuote = 1; }
message MarketOHLC { repeated OHLC ohlc = 1; }
message Quote { int64 bidQ = 1; double bidP = 2; int64 askQ = 3; double askP = 4; }
message OptionGreeks { double delta = 1; double theta = 2; double gamma = 3; double vega = 4; double rho = 5; }
message OHLC { string interval = 1; double open = 2; double high = 3; double low = 4; double close = 5; int64 vol = 6; int64 ts = 7; }
enum Type { initial_feed = 0; live_feed = 1; market_info = 2; }
message MarketFullFeed { LTPC ltpc = 1; MarketLevel marketLevel = 2; OptionGreeks optionGreeks = 3; MarketOHLC marketOHLC = 4; double atp = 5; int64 vtt = 6; double oi = 7; double iv = 8; double tbq = 9; double tsq = 10; }
message IndexFullFeed { LTPC ltpc = 1; MarketOHLC marketOHLC = 2; }
message FullFeed { oneof FullFeedUnion { MarketFullFeed marketFF = 1; IndexFullFeed indexFF = 2; } }
message FirstLevelWithGreeks { LTPC ltpc = 1; Quote firstDepth = 2; OptionGreeks optionGreeks = 3; int64 vtt = 4; double oi = 5; double iv = 6; }
message Feed { oneof FeedUnion { LTPC ltpc = 1; FullFeed fullFeed = 2; FirstLevelWithGreeks firstLevelWithGreeks = 3; } RequestMode requestMode = 4; }
enum RequestMode { ltpc = 0; full_d5 = 1; option_greeks = 2; full_d30 = 3; }
enum MarketStatus { PRE_OPEN_START = 0; PRE_OPEN_END = 1; NORMAL_OPEN = 2; NORMAL_CLOSE = 3; CLOSING_START = 4; CLOSING_END = 5; }
message MarketInfo { map<string, MarketStatus> segmentStatus = 1; }
message FeedResponse { Type type = 1; map<string, Feed> feeds = 2; int64 currentTs = 3; MarketInfo marketInfo = 4; }
''')

w('apps/api/src/infrastructure/providers/upstox/proto-loader.ts', '''
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import protobuf from 'protobufjs';

const root = protobuf.parse(
  readFileSync(join(process.cwd(), 'apps/api/src/infrastructure/providers/upstox/market-data-v3.proto'), 'utf8')
).root;

export const FeedResponseType = root.lookupType(
  'com.upstox.marketdatafeederv3udapi.rpc.proto.FeedResponse'
);
''')

w('apps/api/src/infrastructure/providers/upstox/upstox-api-client.ts', '''
import zlib from 'node:zlib';
import { promisify } from 'node:util';
import { URLSearchParams } from 'node:url';
import { AppError } from '../../../common/errors';
import { RateLimitedHttpClient } from '../../http/rate-limited-http-client';
import { env } from '../../../config/env';
import type {
  UpstoxInstrumentRecord,
  UpstoxMarketAuthorizeResponse,
  UpstoxTokenResponse
} from './upstox-types';

const gunzip = promisify(zlib.gunzip);

export class UpstoxApiClient {
  private readonly http = new RateLimitedHttpClient();

  async exchangeAuthCode(code: string): Promise<UpstoxTokenResponse> {
    const data = new URLSearchParams({
      code,
      client_id: env.UPSTOX_CLIENT_ID,
      client_secret: env.UPSTOX_CLIENT_SECRET,
      redirect_uri: env.UPSTOX_REDIRECT_URI,
      grant_type: 'authorization_code'
    });

    const response = await this.http.request(() =>
      this.http.axios.post<UpstoxTokenResponse>(env.UPSTOX_TOKEN_URL, data, {
        headers: {
          accept: 'application/json',
          'content-type': 'application/x-www-form-urlencoded'
        }
      })
    );

    return response.data;
  }

  async getMarketFeedAuthorizeUrl(accessToken: string): Promise<string> {
    const response = await this.http.request(() =>
      this.http.axios.get<UpstoxMarketAuthorizeResponse>(env.UPSTOX_MARKET_AUTHORIZE_V3_URL, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          accept: 'application/json'
        }
      })
    );

    if (response.data.status !== 'success') {
      throw new AppError('Failed to authorize Upstox market feed', 502, 'UPSTOX_MARKET_FEED_AUTH_FAILED');
    }

    return response.data.data.authorized_redirect_uri;
  }

  async downloadBodInstruments(): Promise<UpstoxInstrumentRecord[]> {
    const response = await this.http.request(() =>
      this.http.axios.get<ArrayBuffer>(env.UPSTOX_BOD_INSTRUMENTS_URL, {
        responseType: 'arraybuffer',
        headers: { accept: 'application/json' }
      })
    );

    const raw = Buffer.from(response.data);
    const decoded = env.UPSTOX_BOD_INSTRUMENTS_URL.endsWith('.gz') ? await gunzip(raw) : raw;
    const parsed = JSON.parse(decoded.toString('utf8')) as UpstoxInstrumentRecord[];

    if (!Array.isArray(parsed)) {
      throw new AppError('Unexpected instrument file payload', 502, 'UPSTOX_INSTRUMENT_FILE_INVALID');
    }

    return parsed;
  }
}
''')

w('apps/api/src/modules/auth/session.service.ts', '''
import { randomUUID } from 'node:crypto';
import { DataSource } from 'typeorm';
import { env } from '../../config/env';
import { User } from '../../infrastructure/db/entities/user.entity';
import { AppSession } from '../../infrastructure/db/entities/app-session.entity';
import { UserSetting } from '../../infrastructure/db/entities/user-setting.entity';
import { BrokerConnection } from '../../infrastructure/db/entities/broker-connection.entity';
import { AppError } from '../../common/errors';
import type { FastifyJWT } from '@fastify/jwt';
import type { SessionBootstrapResponse } from '@fo-scanner/shared';

export type AuthContext = {
  user: User;
  session: AppSession;
};

export class SessionService {
  constructor(private readonly dataSource: DataSource, private readonly jwt: FastifyJWT['sign']) {}

  async bootstrap(
    input: { deviceId: string; displayName?: string },
    meta: { userAgent?: string; ipAddress?: string }
  ): Promise<SessionBootstrapResponse> {
    const userRepo = this.dataSource.getRepository(User);
    const settingsRepo = this.dataSource.getRepository(UserSetting);
    const sessionRepo = this.dataSource.getRepository(AppSession);
    const brokerRepo = this.dataSource.getRepository(BrokerConnection);

    const normalizedDeviceId = input.deviceId.trim();
    let user = await userRepo.findOne({ where: { deviceId: normalizedDeviceId } });

    if (!user) {
      user = userRepo.create({
        deviceId: normalizedDeviceId,
        displayName: input.displayName?.trim() || 'Trader',
        status: 'active'
      });
      user = await userRepo.save(user);
    } else if (input.displayName?.trim() && input.displayName.trim() !== user.displayName) {
      user.displayName = input.displayName.trim();
      user = await userRepo.save(user);
    }

    let settings = await settingsRepo.findOne({ where: { user: { id: user.id } }, relations: { user: true } });
    if (!settings) {
      settings = settingsRepo.create({
        user,
        threshold: env.DEFAULT_ALERT_THRESHOLD,
        cooldownMs: env.DEFAULT_ALERT_COOLDOWN_MS,
        freshnessMs: env.DEFAULT_TICK_FRESHNESS_MS,
        preferredExchange: 'NSE',
        darkMode: True,
        exchanges: ['NSE'],
        segments: ['NSE_EQ', 'NSE_FO']
      });
      settings = await settingsRepo.save(settings);
    }

    const session = await sessionRepo.save(
      sessionRepo.create({
        user,
        sessionKey: randomUUID(),
        userAgent: meta.userAgent ?? null,
        ipAddress: meta.ipAddress ?? null,
        expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
        isActive: true
      })
    );

    const token = await this.jwt({ sub: user.id, sid: session.sessionKey });
    const brokerConnection = await brokerRepo.findOne({ where: { user: { id: user.id }, broker: 'UPSTOX' } });

    return {
      token,
      user: {
        id: user.id,
        deviceId: user.deviceId,
        displayName: user.displayName,
        createdAt: user.createdAt.toISOString()
      },
      brokerConnection: brokerConnection
        ? {
            id: brokerConnection.id,
            broker: brokerConnection.broker,
            status: brokerConnection.status,
            brokerUserId: brokerConnection.brokerUserId,
            accountName: brokerConnection.accountName,
            tokenExpiresAt: brokerConnection.tokenExpiresAt?.toISOString() ?? null,
            connectedAt: brokerConnection.connectedAt?.toISOString() ?? null,
            lastHeartbeatAt: brokerConnection.lastHeartbeatAt?.toISOString() ?? null
          }
        : null,
      settings: {
        threshold: settings.threshold,
        cooldownMs: settings.cooldownMs,
        freshnessMs: settings.freshnessMs,
        preferredExchange: settings.preferredExchange,
        darkMode: settings.darkMode
      }
    };
  }

  async authenticate(payload: { sub?: string; sid?: string }): Promise<AuthContext> {
    if (!payload.sub || !payload.sid) {
      throw new AppError('Invalid session token', 401, 'INVALID_SESSION');
    }

    const sessionRepo = this.dataSource.getRepository(AppSession);
    const session = await sessionRepo.findOne({
      where: { sessionKey: payload.sid, isActive: true },
      relations: { user: true }
    });

    if (!session || session.expiresAt.getTime() < Date.now()) {
      throw new AppError('Session expired', 401, 'SESSION_EXPIRED');
    }

    if (session.user.id != payload.sub || session.user.status !== 'active') {
      throw new AppError('Session not valid for user', 401, 'SESSION_INVALID_USER');
    }

    return { user: session.user, session };
  }
}
''')

w('apps/api/src/modules/auth/oauth.service.ts', '''
import { randomUUID } from 'node:crypto';
import { DataSource } from 'typeorm';
import { env } from '../../config/env';
import { AppError } from '../../common/errors';
import { logger } from '../../common/logger';
import { decryptSecret, encryptSecret } from '../../infrastructure/security/crypto';
import { UpstoxApiClient } from '../../infrastructure/providers/upstox/upstox-api-client';
import { OAuthState } from '../../infrastructure/db/entities/oauth-state.entity';
import { BrokerConnection } from '../../infrastructure/db/entities/broker-connection.entity';
import { BrokerAccessToken } from '../../infrastructure/db/entities/broker-access-token.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import type { AuthStatusResponseDto, BrokerConnectionDto } from '@fo-scanner/shared';

const nextTokenExpiry = (): Date => {
  const now = new Date();
  const expiry = new Date(now);
  expiry.setHours(3, 30, 0, 0);
  if (expiry.getTime() <= now.getTime()) {
    expiry.setDate(expiry.getDate() + 1);
  }
  return expiry;
};

export class UpstoxOAuthService {
  constructor(private readonly dataSource: DataSource, private readonly apiClient: UpstoxApiClient) {}

  async buildConnectUrl(user: User, frontendRedirectUri: string): Promise<string> {
    const stateRepo = this.dataSource.getRepository(OAuthState);
    const state = randomUUID();
    await stateRepo.save(
      stateRepo.create({
        state,
        user,
        broker: 'UPSTOX',
        frontendRedirectUri,
        expiresAt: new Date(Date.now() + 10 * 60 * 1000),
        consumedAt: null
      })
    );

    const params = new URLSearchParams({
      response_type: 'code',
      client_id: env.UPSTOX_CLIENT_ID,
      redirect_uri: env.UPSTOX_REDIRECT_URI,
      state
    });

    return `${env.UPSTOX_AUTH_DIALOG_URL}?${params.toString()}`;
  }

  async handleCallback(code: string | undefined, stateValue: string | undefined): Promise<string> {
    if (!code || !stateValue) {
      throw new AppError('Missing code or state in callback', 400, 'UPSTOX_CALLBACK_INVALID');
    }

    const stateRepo = this.dataSource.getRepository(OAuthState);
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);
    const tokenRepo = this.dataSource.getRepository(BrokerAccessToken);

    const state = await stateRepo.findOne({ where: { state: stateValue }, relations: { user: true } });
    if (!state) {
      throw new AppError('OAuth state not found', 400, 'OAUTH_STATE_NOT_FOUND');
    }
    if (state.consumedAt || state.expiresAt.getTime() < Date.now()) {
      throw new AppError('OAuth state expired', 400, 'OAUTH_STATE_EXPIRED');
    }

    state.consumedAt = new Date();
    await stateRepo.save(state);

    const tokenResponse = await this.apiClient.exchangeAuthCode(code);
    const access = encryptSecret(tokenResponse.access_token);
    const extended = tokenResponse.extended_token ? encryptSecret(tokenResponse.extended_token) : null;

    let connection = await connectionRepo.findOne({
      where: { user: { id: state.user.id }, broker: 'UPSTOX' },
      relations: { user: true }
    });

    if (!connection) {
      connection = connectionRepo.create({
        user: state.user,
        broker: 'UPSTOX',
        status: 'connected'
      });
    }

    connection.status = 'connected';
    connection.brokerUserId = tokenResponse.user_id;
    connection.accountName = tokenResponse.user_name;
    connection.connectedAt = new Date();
    connection.lastAuthorizedAt = new Date();
    connection.tokenExpiresAt = nextTokenExpiry();
    connection.lastHeartbeatAt = new Date();
    connection = await connectionRepo.save(connection);

    await tokenRepo.update({ connection: { id: connection.id }, isActive: true }, { isActive: false });
    await tokenRepo.save(
      tokenRepo.create({
        connection,
        cipherText: access.cipherText,
        iv: access.iv,
        authTag: access.authTag,
        extendedCipherText: extended?.cipherText ?? null,
        extendedIv: extended?.iv ?? null,
        extendedAuthTag: extended?.authTag ?? null,
        expiresAt: connection.tokenExpiresAt,
        isActive: true
      })
    );

    logger.info({ userId: state.user.id, brokerUserId: tokenResponse.user_id }, 'Upstox connection linked');

    const url = new URL(state.frontendRedirectUri);
    url.searchParams.set('status', 'success');
    return url.toString();
  }

  async getAccessTokenForConnection(connectionId: string): Promise<string> {
    const tokenRepo = this.dataSource.getRepository(BrokerAccessToken);
    const token = await tokenRepo.findOne({
      where: { connection: { id: connectionId }, isActive: true },
      relations: { connection: true },
      order: { createdAt: 'DESC' }
    });

    if (!token) {
      throw new AppError('No active Upstox token found', 401, 'UPSTOX_TOKEN_MISSING');
    }

    if (token.expiresAt.getTime() <= Date.now()) {
      throw new AppError('Upstox token expired', 401, 'UPSTOX_TOKEN_EXPIRED');
    }

    return decryptSecret({
      cipherText: token.cipherText,
      iv: token.iv,
      authTag: token.authTag
    });
  }

  async getAuthStatus(userId: string): Promise<AuthStatusResponseDto> {
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);
    const connection = await connectionRepo.findOne({ where: { user: { id: userId }, broker: 'UPSTOX' } });
    const dto = connection ? this.toDto(connection) : null;
    return {
      sessionActive: true,
      brokerConnection: dto,
      reauthRequired: !connection || !connection.tokenExpiresAt || connection.tokenExpiresAt.getTime() <= Date.now(),
      connectUrl: null
    };
  }

  async disconnect(userId: string): Promise<void> {
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);
    const tokenRepo = this.dataSource.getRepository(BrokerAccessToken);
    const connection = await connectionRepo.findOne({ where: { user: { id: userId }, broker: 'UPSTOX' }, relations: { user: true } });
    if (!connection) return;
    connection.status = 'idle';
    connection.tokenExpiresAt = null;
    await connectionRepo.save(connection);
    await tokenRepo.update({ connection: { id: connection.id }, isActive: true }, { isActive: false });
  }

  toDto(connection: BrokerConnection): BrokerConnectionDto {
    return {
      id: connection.id,
      broker: connection.broker,
      status: connection.status,
      brokerUserId: connection.brokerUserId,
      accountName: connection.accountName,
      tokenExpiresAt: connection.tokenExpiresAt?.toISOString() ?? null,
      connectedAt: connection.connectedAt?.toISOString() ?? null,
      lastHeartbeatAt: connection.lastHeartbeatAt?.toISOString() ?? null
    };
  }
}
''')

w('apps/api/src/modules/settings/settings.service.ts', '''
import { DataSource } from 'typeorm';
import { UserSetting } from '../../infrastructure/db/entities/user-setting.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import { env } from '../../config/env';
import { userSettingsSchema, type UserSettingsDto } from '@fo-scanner/shared';

export class SettingsService {
  constructor(private readonly dataSource: DataSource) {}

  async getForUser(user: User): Promise<UserSettingsDto> {
    const repo = this.dataSource.getRepository(UserSetting);
    let settings = await repo.findOne({ where: { user: { id: user.id } }, relations: { user: true } });
    if (!settings) {
      settings = await repo.save(
        repo.create({
          user,
          threshold: env.DEFAULT_ALERT_THRESHOLD,
          cooldownMs: env.DEFAULT_ALERT_COOLDOWN_MS,
          freshnessMs: env.DEFAULT_TICK_FRESHNESS_MS,
          preferredExchange: 'NSE',
          darkMode: true,
          exchanges: ['NSE'],
          segments: ['NSE_EQ', 'NSE_FO']
        })
      );
    }
    return userSettingsSchema.parse({
      threshold: settings.threshold,
      cooldownMs: settings.cooldownMs,
      freshnessMs: settings.freshnessMs,
      preferredExchange: settings.preferredExchange,
      darkMode: settings.darkMode,
      exchanges: settings.exchanges,
      segments: settings.segments
    });
  }

  async updateForUser(user: User, input: UserSettingsDto): Promise<UserSettingsDto> {
    const repo = this.dataSource.getRepository(UserSetting);
    const parsed = userSettingsSchema.parse(input);
    let settings = await repo.findOne({ where: { user: { id: user.id } }, relations: { user: true } });
    if (!settings) {
      settings = repo.create({ user, ...parsed });
    } else {
      Object.assign(settings, parsed);
    }
    await repo.save(settings);
    return parsed;
  }
}
''')

w('apps/api/src/modules/instruments/instrument.service.ts', '''
import { DataSource, In } from 'typeorm';
import { Instrument } from '../../infrastructure/db/entities/instrument.entity';
import { UpstoxApiClient } from '../../infrastructure/providers/upstox/upstox-api-client';
import type { InstrumentSummary } from '@fo-scanner/shared';
import { logger } from '../../common/logger';

const parseExpiry = (value: unknown): string | null => {
  if (typeof value !== 'string' || !value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString().slice(0, 10);
};

export class InstrumentService {
  constructor(private readonly dataSource: DataSource, private readonly upstox: UpstoxApiClient) {}

  async syncBodInstruments(): Promise<number> {
    const repo = this.dataSource.getRepository(Instrument);
    const rows = await this.upstox.downloadBodInstruments();
    const entities = rows.map((row) =>
      repo.create({
        instrumentKey: row.instrument_key,
        exchange: row.exchange,
        segment: row.segment,
        instrumentType: row.instrument_type,
        tradingSymbol: row.trading_symbol,
        shortName: typeof row.short_name === 'string' ? row.short_name : null,
        name: typeof row.name === 'string' ? row.name : null,
        underlyingKey: typeof row.underlying_key === 'string' ? row.underlying_key : null,
        underlyingType: typeof row.underlying_type === 'string' ? row.underlying_type : null,
        expiryDate: parseExpiry(row.expiry),
        lotSize: typeof row.lot_size === 'number' ? row.lot_size : null,
        minimumLot: typeof row.minimum_lot === 'number' ? row.minimum_lot : null,
        tickSize: typeof row.tick_size === 'number' ? row.tick_size : null,
        isin: typeof row.isin === 'string' ? row.isin : null,
        isTradable: true,
        metadata: row
      })
    );

    const chunkSize = 1000;
    for (let offset = 0; offset < entities.length; offset += chunkSize) {
      const chunk = entities.slice(offset, offset + chunkSize);
      await repo
        .createQueryBuilder()
        .insert()
        .into(Instrument)
        .values(chunk)
        .orUpdate(
          [
            'exchange',
            'segment',
            'instrumentType',
            'tradingSymbol',
            'shortName',
            'name',
            'underlyingKey',
            'underlyingType',
            'expiryDate',
            'lotSize',
            'minimumLot',
            'tickSize',
            'isin',
            'metadata',
            'updatedAt'
          ],
          ['instrumentKey']
        )
        .execute();
    }

    logger.info({ count: entities.length }, 'Instrument catalog synced');
    return entities.length;
  }

  async search(query: string, limit = 20): Promise<InstrumentSummary[]> {
    const repo = this.dataSource.getRepository(Instrument);
    const rows = await repo
      .createQueryBuilder('instrument')
      .where('instrument.tradingSymbol ILIKE :query OR instrument.shortName ILIKE :query OR instrument.name ILIKE :query', {
        query: `%${query.trim()}%`
      })
      .orderBy('instrument.expiryDate', 'ASC', 'NULLS LAST')
      .limit(limit)
      .getMany();

    return rows.map((row) => this.toSummary(row));
  }

  async getByKeys(instrumentKeys: string[]): Promise<Instrument[]> {
    const repo = this.dataSource.getRepository(Instrument);
    return repo.find({ where: { instrumentKey: In(instrumentKeys) } });
  }

  toSummary(instrument: Instrument): InstrumentSummary {
    return {
      id: instrument.id,
      instrumentKey: instrument.instrumentKey,
      exchange: instrument.exchange,
      segment: instrument.segment,
      instrumentType: instrument.instrumentType,
      tradingSymbol: instrument.tradingSymbol,
      shortName: instrument.shortName,
      underlyingKey: instrument.underlyingKey,
      expiryDate: instrument.expiryDate,
      lotSize: instrument.lotSize
    };
  }
}
''')

w('apps/api/src/modules/market/pairing.service.ts', '''
import { DataSource } from 'typeorm';
import { Instrument } from '../../infrastructure/db/entities/instrument.entity';
import { InstrumentPair } from '../../infrastructure/db/entities/instrument-pair.entity';
import { Watchlist } from '../../infrastructure/db/entities/watchlist.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import { InstrumentService } from '../instruments/instrument.service';
import type { WatchlistItemDto } from '@fo-scanner/shared';

const FUTURE_TYPES = ['FUT', 'FUTIDX', 'FUTSTK'];

const normalizeSymbol = (symbol: string): string => symbol.trim().toUpperCase();

export class PairingService {
  constructor(private readonly dataSource: DataSource, private readonly instrumentService: InstrumentService) {}

  async refreshForUser(user: User): Promise<void> {
    const watchlistRepo = this.dataSource.getRepository(Watchlist);
    const pairRepo = this.dataSource.getRepository(InstrumentPair);
    const instrumentRepo = this.dataSource.getRepository(Instrument);
    const watchlist = await watchlistRepo.find({ where: { user: { id: user.id } }, relations: { user: true } });

    for (const item of watchlist) {
      const spotInstrument = await this.findSpotInstrument(instrumentRepo, item.symbol, item.exchange);
      const futureInstrument = spotInstrument
        ? await this.findFutureInstrument(instrumentRepo, spotInstrument, item.preferredMonthOffset)
        : null;

      const status = spotInstrument ? (futureInstrument ? 'paired' : 'missing_future') : 'missing_spot';
      const existing = await pairRepo.findOne({ where: { userId: user.id, symbol: normalizeSymbol(item.symbol) } });
      const record = existing ?? pairRepo.create({ userId: user.id, symbol: normalizeSymbol(item.symbol) });
      record.spotInstrument = spotInstrument;
      record.futureInstrument = futureInstrument;
      record.status = status;
      record.futureExpiryDate = futureInstrument?.expiryDate ?? null;
      record.monthType = item.preferredMonthOffset === 0 ? 'near' : item.preferredMonthOffset === 1 ? 'next' : 'far';
      record.enabled = item.enabled;
      await pairRepo.save(record);
    }
  }

  async listForUser(user: User): Promise<WatchlistItemDto[]> {
    const watchlistRepo = this.dataSource.getRepository(Watchlist);
    const pairRepo = this.dataSource.getRepository(InstrumentPair);
    const watchlistItems = await watchlistRepo.find({ where: { user: { id: user.id } }, relations: { user: true } });

    const result: WatchlistItemDto[] = [];
    for (const watchItem of watchlistItems) {
      const pair = await pairRepo.findOne({
        where: { userId: user.id, symbol: normalizeSymbol(watchItem.symbol) },
        relations: { spotInstrument: true, futureInstrument: true }
      });
      result.push({
        id: watchItem.id,
        symbol: normalizeSymbol(watchItem.symbol),
        exchange: watchItem.exchange,
        segment: watchItem.segment,
        enabled: watchItem.enabled,
        preferredMonthOffset: watchItem.preferredMonthOffset,
        spotInstrument: pair?.spotInstrument ? this.instrumentService.toSummary(pair.spotInstrument) : null,
        futureInstrument: pair?.futureInstrument ? this.instrumentService.toSummary(pair.futureInstrument) : null,
        updatedAt: watchItem.updatedAt.toISOString()
      });
    }

    return result;
  }

  async getPairsForUser(userId: string): Promise<InstrumentPair[]> {
    const pairRepo = this.dataSource.getRepository(InstrumentPair);
    return pairRepo.find({
      where: { userId, enabled: true, status: 'paired' },
      relations: { spotInstrument: true, futureInstrument: true }
    });
  }

  private async findSpotInstrument(
    instrumentRepo: ReturnType<DataSource['getRepository']<Instrument>>,
    symbol: string,
    exchange: string
  ): Promise<Instrument | null> {
    const normalized = normalizeSymbol(symbol);
    return instrumentRepo
      .createQueryBuilder('instrument')
      .where('instrument.exchange = :exchange', { exchange })
      .andWhere("instrument.segment IN ('NSE_EQ','BSE_EQ','NSE_INDEX','BSE_INDEX')")
      .andWhere("instrument.instrumentType IN ('EQ','INDEX')")
      .andWhere('(UPPER(instrument.tradingSymbol) = :symbol OR UPPER(COALESCE(instrument.shortName, instrument.name, instrument.tradingSymbol)) = :symbol)', {
        symbol: normalized
      })
      .orderBy("CASE WHEN instrument.instrumentType = 'EQ' THEN 0 ELSE 1 END", 'ASC')
      .addOrderBy('instrument.tradingSymbol', 'ASC')
      .getOne();
  }

  private async findFutureInstrument(
    instrumentRepo: ReturnType<DataSource['getRepository']<Instrument>>,
    spotInstrument: Instrument,
    monthOffset: number
  ): Promise<Instrument | null> {
    const futureRows = await instrumentRepo
      .createQueryBuilder('instrument')
      .where('instrument.underlyingKey = :underlyingKey', { underlyingKey: spotInstrument.instrumentKey })
      .andWhere('instrument.segment IN (:...segments)', { segments: ['NSE_FO', 'BSE_FO'] })
      .andWhere('instrument.instrumentType IN (:...types)', { types: FUTURE_TYPES })
      .andWhere('instrument.expiryDate >= CURRENT_DATE')
      .orderBy('instrument.expiryDate', 'ASC')
      .getMany();

    return futureRows[monthOffset] ?? null;
  }
}
''')

w('apps/api/src/modules/market/latest-tick.store.ts', '''
import { LRUCache } from 'lru-cache';
import type { NormalizedTick } from '../../infrastructure/providers/upstox/upstox-types';

export class LatestTickStore {
  private readonly cache = new LRUCache<string, NormalizedTick>({
    max: 10_000,
    ttl: 1000 * 60 * 10
  });

  set(tick: NormalizedTick): void {
    this.cache.set(tick.instrumentKey, tick);
  }

  get(instrumentKey: string): NormalizedTick | undefined {
    return this.cache.get(instrumentKey);
  }

  count(): number {
    return this.cache.size;
  }
}
''')

w('apps/api/src/modules/market/spread-detector.service.ts', '''
import { InstrumentPair } from '../../infrastructure/db/entities/instrument-pair.entity';
import { LatestTickStore } from './latest-tick.store';
import type { UserSettingsDto } from '@fo-scanner/shared';

export type SpreadCandidate = {
  pair: InstrumentPair;
  spread: number;
  spotPrice: number;
  futurePrice: number;
  observedAt: Date;
  freshnessMs: number;
  dedupeKey: string;
};

export class SpreadDetectorService {
  private readonly lastAlertByPair = new Map<string, { dedupeKey: string; emittedAt: number }>();

  constructor(private readonly tickStore: LatestTickStore) {}

  evaluate(pair: InstrumentPair, settings: UserSettingsDto): SpreadCandidate | null {
    const spotKey = pair.spotInstrument?.instrumentKey;
    const futureKey = pair.futureInstrument?.instrumentKey;
    if (!spotKey || !futureKey) return null;

    const spot = this.tickStore.get(spotKey);
    const future = this.tickStore.get(futureKey);
    if (!spot || !future) return null;

    const freshnessMs = Math.abs(spot.observedAt.getTime() - future.observedAt.getTime());
    if (freshnessMs > settings.freshnessMs) return null;

    const spread = Number((spot.price - future.price).toFixed(2));
    if (spread < settings.threshold) return null;

    const observedAt = new Date(Math.max(spot.observedAt.getTime(), future.observedAt.getTime()));
    const spreadBucket = Math.floor(spread * 4) / 4;
    const dedupeKey = `${pair.id}:${spreadBucket.toFixed(2)}`;
    const previous = this.lastAlertByPair.get(pair.id);

    if (previous && previous.dedupeKey === dedupeKey && observedAt.getTime() - previous.emittedAt < settings.cooldownMs) {
      return null;
    }

    this.lastAlertByPair.set(pair.id, { dedupeKey, emittedAt: observedAt.getTime() });

    return {
      pair,
      spread,
      spotPrice: spot.price,
      futurePrice: future.price,
      observedAt,
      freshnessMs,
      dedupeKey
    };
  }
}
''')

w('apps/api/src/modules/alerts/alerts.service.ts', '''
import { DataSource } from 'typeorm';
import { Alert } from '../../infrastructure/db/entities/alert.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import type { AlertHistoryItemDto } from '@fo-scanner/shared';
import type { SpreadCandidate } from '../market/spread-detector.service';

export class AlertsService {
  constructor(private readonly dataSource: DataSource) {}

  async create(user: User, candidate: SpreadCandidate): Promise<AlertHistoryItemDto> {
    const repo = this.dataSource.getRepository(Alert);
    const alert = await repo.save(
      repo.create({
        user,
        pair: candidate.pair,
        spread: candidate.spread,
        threshold: candidate.spread,
        spotPrice: candidate.spotPrice,
        futurePrice: candidate.futurePrice,
        freshnessMs: candidate.freshnessMs,
        dedupeKey: candidate.dedupeKey,
        triggeredAt: candidate.observedAt,
        acknowledgedAt: null
      })
    );
    return this.toDto(alert);
  }

  async history(user: User, limit = 100, symbol?: string): Promise<AlertHistoryItemDto[]> {
    const repo = this.dataSource.getRepository(Alert);
    const qb = repo
      .createQueryBuilder('alert')
      .leftJoinAndSelect('alert.pair', 'pair')
      .where('alert.userId = :userId', { userId: user.id })
      .orderBy('alert.triggeredAt', 'DESC')
      .limit(limit);

    if (symbol?.trim()) {
      qb.andWhere('pair.symbol = :symbol', { symbol: symbol.trim().toUpperCase() });
    }

    const alerts = await qb.getMany();
    return alerts.map((item) => this.toDto(item));
  }

  async acknowledge(user: User, alertId: string): Promise<void> {
    const repo = this.dataSource.getRepository(Alert);
    await repo.update({ id: alertId, user: { id: user.id } }, { acknowledgedAt: new Date() });
  }

  toDto(alert: Alert): AlertHistoryItemDto {
    return {
      id: alert.id,
      pairId: alert.pair.id,
      symbol: alert.pair.symbol,
      spread: alert.spread,
      threshold: alert.threshold,
      spotPrice: alert.spotPrice,
      futurePrice: alert.futurePrice,
      futureExpiry: alert.pair.futureExpiryDate,
      triggeredAt: alert.triggeredAt.toISOString(),
      freshnessMs: alert.freshnessMs,
      dedupeKey: alert.dedupeKey,
      acknowledgedAt: alert.acknowledgedAt?.toISOString() ?? null
    };
  }
}
''')

w('apps/api/src/modules/watchlist/watchlist.service.ts', '''
import { DataSource } from 'typeorm';
import { upsertWatchlistItemSchema, type UpsertWatchlistItemDto, type WatchlistItemDto } from '@fo-scanner/shared';
import { Watchlist } from '../../infrastructure/db/entities/watchlist.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import { PairingService } from '../market/pairing.service';

export class WatchlistService {
  constructor(private readonly dataSource: DataSource, private readonly pairingService: PairingService) {}

  async list(user: User): Promise<WatchlistItemDto[]> {
    return this.pairingService.listForUser(user);
  }

  async upsert(user: User, input: UpsertWatchlistItemDto): Promise<WatchlistItemDto[]> {
    const parsed = upsertWatchlistItemSchema.parse(input);
    const repo = this.dataSource.getRepository(Watchlist);
    const existing = await repo.findOne({ where: { user: { id: user.id }, symbol: parsed.symbol.toUpperCase() }, relations: { user: true } });

    if (existing) {
      Object.assign(existing, {
        symbol: parsed.symbol.toUpperCase(),
        exchange: parsed.exchange,
        segment: parsed.segment,
        preferredMonthOffset: parsed.preferredMonthOffset,
        enabled: parsed.enabled
      });
      await repo.save(existing);
    } else {
      await repo.save(
        repo.create({
          user,
          symbol: parsed.symbol.toUpperCase(),
          exchange: parsed.exchange,
          segment: parsed.segment,
          preferredMonthOffset: parsed.preferredMonthOffset,
          enabled: parsed.enabled
        })
      );
    }

    await this.pairingService.refreshForUser(user);
    return this.pairingService.listForUser(user);
  }

  async remove(user: User, watchlistId: string): Promise<void> {
    const repo = this.dataSource.getRepository(Watchlist);
    await repo.delete({ id: watchlistId, user: { id: user.id } });
    await this.pairingService.refreshForUser(user);
  }
}
''')

w('apps/api/src/infrastructure/realtime/client-hub.ts', '''
import type WebSocket from 'ws';
import { env } from '../../config/env';
import { websocketEventSchema, type WebsocketEvent } from '@fo-scanner/shared';

export class ClientHub {
  private readonly sockets = new Map<string, Set<WebSocket>>();

  connect(userId: string, socket: WebSocket): void {
    const set = this.sockets.get(userId) ?? new Set<WebSocket>();
    set.add(socket);
    this.sockets.set(userId, set);
    socket.on('close', () => {
      const current = this.sockets.get(userId);
      current?.delete(socket);
      if (!current || current.size === 0) {
        this.sockets.delete(userId);
      }
    });
  }

  publishToUser(userId: string, event: WebsocketEvent, priority: 'critical' | 'normal' = 'normal'): void {
    websocketEventSchema.parse(event);
    const sockets = this.sockets.get(userId);
    if (!sockets) return;
    const payload = JSON.stringify(event);
    for (const socket of sockets) {
      if (socket.readyState !== socket.OPEN) continue;
      if (priority === 'normal' && socket.bufferedAmount > env.WS_BUFFER_DROP_THRESHOLD) {
        continue;
      }
      socket.send(payload);
    }
  }
}
''')

w('apps/api/src/modules/system/system.service.ts', '''
import { DataSource } from 'typeorm';
import type { DashboardStatusDto, DashboardSummaryDto } from '@fo-scanner/shared';
import { SystemEvent } from '../../infrastructure/db/entities/system-event.entity';
import { BrokerConnection } from '../../infrastructure/db/entities/broker-connection.entity';
import { Watchlist } from '../../infrastructure/db/entities/watchlist.entity';
import { Alert } from '../../infrastructure/db/entities/alert.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import { UserSetting } from '../../infrastructure/db/entities/user-setting.entity';
import { ScannerOrchestrator } from '../market/scanner-orchestrator.service';

export class SystemService {
  constructor(private readonly dataSource: DataSource, private readonly orchestrator: ScannerOrchestrator) {}

  async getSummary(user: User): Promise<DashboardSummaryDto> {
    const watchRepo = this.dataSource.getRepository(Watchlist);
    const alertRepo = this.dataSource.getRepository(Alert);
    const settingsRepo = this.dataSource.getRepository(UserSetting);
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);

    const [watchCount, liveAlertCount, settings, connection] = await Promise.all([
      watchRepo.count({ where: { user: { id: user.id }, enabled: true } }),
      alertRepo.count({ where: { user: { id: user.id }, acknowledgedAt: null } }),
      settingsRepo.findOne({ where: { user: { id: user.id } }, relations: { user: true } }),
      connectionRepo.findOne({ where: { user: { id: user.id }, broker: 'UPSTOX' } })
    ]);

    const runtime = this.orchestrator.getRuntimeSnapshot(user.id);

    return {
      activeConnection: !!connection && connection.status === 'connected',
      subscribedInstrumentCount: runtime.subscribedInstrumentCount,
      activeWatchlistCount: watchCount,
      liveAlertCount,
      lastTickAt: runtime.lastTickAt,
      backendLatencyMs: runtime.backendLatencyMs,
      websocketState: runtime.websocketState,
      marketDataState: runtime.marketDataState,
      threshold: settings?.threshold ?? 10
    };
  }

  async getStatus(user: User): Promise<DashboardStatusDto> {
    const eventsRepo = this.dataSource.getRepository(SystemEvent);
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);
    const connection = await connectionRepo.findOne({ where: { user: { id: user.id }, broker: 'UPSTOX' } });
    const runtime = this.orchestrator.getRuntimeSnapshot(user.id);
    const events = await eventsRepo.find({ order: { createdAt: 'DESC' }, take: 20 });

    return {
      backend: 'ok',
      database: 'ok',
      brokerAuth: connection?.status ?? 'idle',
      websocket: runtime.websocketState,
      marketFeed: runtime.marketDataState,
      instrumentSyncAt: runtime.lastInstrumentSyncAt,
      marketStatus: runtime.marketStatus,
      recentEvents: events.map((event) => ({
        id: event.id,
        level: event.level,
        type: event.type,
        message: event.message,
        createdAt: event.createdAt.toISOString()
      }))
    };
  }

  async logEvent(type: string, message: string, level: 'info' | 'warning' | 'critical', payload: Record<string, unknown> = {}): Promise<void> {
    const repo = this.dataSource.getRepository(SystemEvent);
    await repo.save(repo.create({ type, message, level, payload, source: 'api' }));
  }
}
''')

w('apps/api/src/infrastructure/providers/upstox/upstox-market-feed.ts', '''
import { setTimeout as wait } from 'node:timers/promises';
import WebSocket from 'ws';
import type protobuf from 'protobufjs';
import { env } from '../../../config/env';
import { logger } from '../../../common/logger';
import { FeedResponseType } from './proto-loader';
import { UpstoxApiClient } from './upstox-api-client';
import type { NormalizedTick } from './upstox-types';

const REQUEST_MODE_BY_ENUM = ['ltpc', 'full_d5', 'option_greeks', 'full_d30'];

type FeedStatusCallback = (status: 'connecting' | 'connected' | 'closed' | 'error', details?: Record<string, unknown>) => void;
type TickCallback = (tick: NormalizedTick) => void;
type MarketInfoCallback = (segments: Record<string, string>) => void;

type FeedResponseDecoded = protobuf.Message<unknown> & {
  feeds?: Record<string, any>;
  currentTs?: number | Long;
  marketInfo?: { segmentStatus?: Record<string, string> };
};

export class UpstoxMarketFeedConnection {
  private socket: WebSocket | null = null;
  private shouldRun = true;
  private reconnectAttempt = 0;

  constructor(
    private readonly apiClient: UpstoxApiClient,
    private readonly accessToken: string,
    private readonly instrumentKeys: string[],
    private readonly onTick: TickCallback,
    private readonly onStatus: FeedStatusCallback,
    private readonly onMarketInfo: MarketInfoCallback
  ) {}

  async start(): Promise<void> {
    while (this.shouldRun) {
      try {
        this.onStatus('connecting');
        const url = await this.apiClient.getMarketFeedAuthorizeUrl(this.accessToken);
        await this.connect(url);
        this.reconnectAttempt = 0;
        return;
      } catch (error) {
        this.onStatus('error', { message: error instanceof Error ? error.message : 'feed connect failed' });
        const delay = Math.min(
          env.UPSTOX_RECONNECT_BASE_MS * 2 ** this.reconnectAttempt,
          env.UPSTOX_RECONNECT_MAX_MS
        );
        this.reconnectAttempt += 1;
        await wait(delay);
      }
    }
  }

  stop(): void {
    this.shouldRun = false;
    this.socket?.close();
    this.socket = null;
  }

  private async connect(url: string): Promise<void> {
    await new Promise<void>((resolve, reject) => {
      const ws = new WebSocket(url);
      this.socket = ws;

      ws.on('open', () => {
        this.onStatus('connected');
        const payload = Buffer.from(
          JSON.stringify({
            guid: crypto.randomUUID(),
            method: 'sub',
            data: {
              mode: 'ltpc',
              instrumentKeys: this.instrumentKeys
            }
          })
        );
        ws.send(payload);
        resolve();
      });

      ws.on('message', (data) => this.handleMessage(data));
      ws.on('error', (error) => {
        logger.warn({ err: error }, 'Upstox websocket error');
        reject(error);
      });
      ws.on('close', () => {
        this.onStatus('closed');
        if (this.shouldRun) {
          void this.start();
        }
      });
    });
  }

  private handleMessage(data: WebSocket.RawData): void {
    if (typeof data === 'string') return;
    const decoded = FeedResponseType.decode(Buffer.from(data)) as FeedResponseDecoded;
    const object = FeedResponseType.toObject(decoded, {
      enums: String,
      longs: Number,
      defaults: false
    }) as FeedResponseDecoded;

    if (object.marketInfo?.segmentStatus) {
      this.onMarketInfo(object.marketInfo.segmentStatus as Record<string, string>);
    }

    const currentTs = typeof object.currentTs === 'number' ? object.currentTs : Date.now();
    for (const [instrumentKey, feed] of Object.entries(object.feeds ?? {})) {
      const price = feed.ltpc?.ltp ?? feed.fullFeed?.marketFF?.ltpc?.ltp ?? feed.fullFeed?.indexFF?.ltpc?.ltp ?? feed.firstLevelWithGreeks?.ltpc?.ltp;
      if (typeof price !== 'number') continue;
      const requestMode = REQUEST_MODE_BY_ENUM[(feed.requestMode as number) ?? 0] ?? 'ltpc';
      this.onTick({
        instrumentKey,
        price,
        requestMode,
        observedAt: new Date(currentTs)
      });
    }
  }
}
''')

w('apps/api/src/modules/market/scanner-orchestrator.service.ts', '''
import cron from 'node-cron';
import { DataSource } from 'typeorm';
import type { UserSettingsDto, WebsocketEvent } from '@fo-scanner/shared';
import { env } from '../../config/env';
import { logger } from '../../common/logger';
import { User } from '../../infrastructure/db/entities/user.entity';
import { BrokerConnection } from '../../infrastructure/db/entities/broker-connection.entity';
import { UpstoxOAuthService } from '../auth/oauth.service';
import { UpstoxApiClient } from '../../infrastructure/providers/upstox/upstox-api-client';
import { UpstoxMarketFeedConnection } from '../../infrastructure/providers/upstox/upstox-market-feed';
import { LatestTickStore } from './latest-tick.store';
import { SpreadDetectorService } from './spread-detector.service';
import { AlertsService } from '../alerts/alerts.service';
import { PairingService } from './pairing.service';
import { SettingsService } from '../settings/settings.service';
import { ClientHub } from '../../infrastructure/realtime/client-hub';
import { InstrumentService } from '../instruments/instrument.service';
import { SystemService } from '../system/system.service';

const chunk = <T,>(items: T[], size: number): T[][] => {
  const result: T[][] = [];
  for (let offset = 0; offset < items.length; offset += size) {
    result.push(items.slice(offset, offset + size));
  }
  return result;
};

type RuntimeSnapshot = {
  subscribedInstrumentCount: number;
  lastTickAt: string | null;
  backendLatencyMs: number;
  websocketState: 'connected' | 'connecting' | 'closed';
  marketDataState: 'idle' | 'connecting' | 'connected' | 'expired' | 'error';
  lastInstrumentSyncAt: string | null;
  marketStatus: Record<string, string>;
};

class UserScannerWorker {
  private readonly tickStore = new LatestTickStore();
  private readonly detector = new SpreadDetectorService(this.tickStore);
  private readonly feeds: UpstoxMarketFeedConnection[] = [];
  private readonly pairIdsByInstrument = new Map<string, Set<string>>();
  private readonly liveSpreadEmissionAt = new Map<string, number>();
  private settings: UserSettingsDto | null = null;
  private pairs: Awaited<ReturnType<PairingService['getPairsForUser']>> = [];
  runtime: RuntimeSnapshot = {
    subscribedInstrumentCount: 0,
    lastTickAt: null,
    backendLatencyMs: 0,
    websocketState: 'closed',
    marketDataState: 'idle',
    lastInstrumentSyncAt: null,
    marketStatus: {}
  };

  constructor(
    private readonly user: User,
    private readonly connection: BrokerConnection,
    private readonly oauthService: UpstoxOAuthService,
    private readonly upstoxApiClient: UpstoxApiClient,
    private readonly pairingService: PairingService,
    private readonly settingsService: SettingsService,
    private readonly alertsService: AlertsService,
    private readonly clientHub: ClientHub
  ) {}

  async start(): Promise<void> {
    await this.refresh();
  }

  async refresh(): Promise<void> {
    this.settings = await this.settingsService.getForUser(this.user);
    this.pairs = await this.pairingService.getPairsForUser(this.user.id);
    this.runtime.subscribedInstrumentCount = this.pairs.length * 2;
    this.pairIdsByInstrument.clear();

    for (const pair of this.pairs) {
      const spotKey = pair.spotInstrument?.instrumentKey;
      const futureKey = pair.futureInstrument?.instrumentKey;
      if (!spotKey || !futureKey) continue;
      const spotSet = this.pairIdsByInstrument.get(spotKey) ?? new Set<string>();
      spotSet.add(pair.id);
      this.pairIdsByInstrument.set(spotKey, spotSet);
      const futureSet = this.pairIdsByInstrument.get(futureKey) ?? new Set<string>();
      futureSet.add(pair.id);
      this.pairIdsByInstrument.set(futureKey, futureSet);
    }

    this.stopFeeds();
    if (!this.pairs.length) {
      this.runtime.marketDataState = 'idle';
      return;
    }

    const accessToken = await this.oauthService.getAccessTokenForConnection(this.connection.id);
    const instrumentKeys = Array.from(
      new Set(
        this.pairs.flatMap((pair) => [pair.spotInstrument?.instrumentKey, pair.futureInstrument?.instrumentKey].filter(Boolean) as string[])
      )
    );
    const shards = chunk(instrumentKeys, env.UPSTOX_LTPC_PER_CONNECTION).slice(0, env.UPSTOX_MAX_CONNECTIONS);

    for (const shard of shards) {
      const feed = new UpstoxMarketFeedConnection(
        this.upstoxApiClient,
        accessToken,
        shard,
        (tick) => this.handleTick(tick),
        (status) => {
          this.runtime.websocketState = status === 'connected' ? 'connected' : status === 'connecting' ? 'connecting' : 'closed';
          this.runtime.marketDataState = status === 'error' ? 'error' : status === 'connected' ? 'connected' : 'connecting';
        },
        (marketStatus) => {
          this.runtime.marketStatus = marketStatus;
        }
      );
      this.feeds.push(feed);
      await feed.start();
    }
  }

  stop(): void {
    this.stopFeeds();
  }

  private stopFeeds(): void {
    for (const feed of this.feeds) {
      feed.stop();
    }
    this.feeds.length = 0;
  }

  private async handleTick(tick: { instrumentKey: string; price: number; observedAt: Date; requestMode: string }): Promise<void> {
    const started = Date.now();
    this.tickStore.set(tick);
    this.runtime.lastTickAt = tick.observedAt.toISOString();
    const pairIds = this.pairIdsByInstrument.get(tick.instrumentKey);
    if (!pairIds || !this.settings) return;

    for (const pairId of pairIds) {
      const pair = this.pairs.find((value) => value.id === pairId);
      if (!pair) continue;

      const candidate = this.detector.evaluate(pair, this.settings);
      if (candidate) {
        const alert = await this.alertsService.create(this.user, candidate);
        this.clientHub.publishToUser(this.user.id, { type: 'alert.created', payload: alert }, 'critical');
      }

      const now = Date.now();
      const lastEmit = this.liveSpreadEmissionAt.get(pairId) ?? 0;
      if (now - lastEmit > 1000) {
        const spotTick = this.tickStore.get(pair.spotInstrument!.instrumentKey);
        const futureTick = this.tickStore.get(pair.futureInstrument!.instrumentKey);
        if (spotTick && futureTick) {
          this.clientHub.publishToUser(this.user.id, {
            type: 'scanner.spread',
            payload: {
              pairId: pair.id,
              symbol: pair.symbol,
              spread: Number((spotTick.price - futureTick.price).toFixed(2)),
              spotPrice: spotTick.price,
              futurePrice: futureTick.price,
              futureExpiry: pair.futureExpiryDate,
              observedAt: new Date(Math.max(spotTick.observedAt.getTime(), futureTick.observedAt.getTime())).toISOString()
            }
          });
          this.liveSpreadEmissionAt.set(pairId, now);
        }
      }
    }

    this.runtime.backendLatencyMs = Date.now() - started;
  }
}

export class ScannerOrchestrator {
  private readonly workers = new Map<string, UserScannerWorker>();
  private lastInstrumentSyncAt: string | null = null;

  constructor(
    private readonly dataSource: DataSource,
    private readonly oauthService: UpstoxOAuthService,
    private readonly upstoxApiClient: UpstoxApiClient,
    private readonly pairingService: PairingService,
    private readonly settingsService: SettingsService,
    private readonly alertsService: AlertsService,
    private readonly clientHub: ClientHub,
    private readonly instrumentService: InstrumentService,
    private readonly systemService: SystemService
  ) {}

  async start(): Promise<void> {
    await this.syncInstruments();
    await this.startWorkers();
    cron.schedule(env.INSTRUMENT_SYNC_CRON, () => {
      void this.syncInstruments();
    });
  }

  async refreshUser(user: User): Promise<void> {
    await this.pairingService.refreshForUser(user);
    const worker = this.workers.get(user.id);
    if (worker) {
      await worker.refresh();
    } else {
      const connectionRepo = this.dataSource.getRepository(BrokerConnection);
      const connection = await connectionRepo.findOne({ where: { user: { id: user.id }, broker: 'UPSTOX', status: 'connected' }, relations: { user: true } });
      if (connection) {
        const nextWorker = this.createWorker(user, connection);
        this.workers.set(user.id, nextWorker);
        await nextWorker.start();
      }
    }
  }

  getRuntimeSnapshot(userId: string): RuntimeSnapshot {
    const runtime = this.workers.get(userId)?.runtime;
    return runtime
      ? { ...runtime, lastInstrumentSyncAt: this.lastInstrumentSyncAt }
      : {
          subscribedInstrumentCount: 0,
          lastTickAt: null,
          backendLatencyMs: 0,
          websocketState: 'closed',
          marketDataState: 'idle',
          lastInstrumentSyncAt: this.lastInstrumentSyncAt,
          marketStatus: {}
        };
  }

  private async syncInstruments(): Promise<void> {
    const count = await this.instrumentService.syncBodInstruments();
    this.lastInstrumentSyncAt = new Date().toISOString();
    await this.systemService.logEvent('instrument.sync', `Synced ${count} instruments`, 'info', { count });
  }

  private async startWorkers(): Promise<void> {
    const repo = this.dataSource.getRepository(BrokerConnection);
    const connections = await repo.find({ where: { broker: 'UPSTOX', status: 'connected' }, relations: { user: true } });
    for (const connection of connections) {
      const worker = this.createWorker(connection.user, connection);
      this.workers.set(connection.user.id, worker);
      await worker.start();
    }
  }

  private createWorker(user: User, connection: BrokerConnection): UserScannerWorker {
    return new UserScannerWorker(
      user,
      connection,
      this.oauthService,
      this.upstoxApiClient,
      this.pairingService,
      this.settingsService,
      this.alertsService,
      this.clientHub
    );
  }
}
''')

w('apps/api/src/routes/index.ts', '''
import type { FastifyInstance, FastifyRequest } from 'fastify';
import { bootstrapSessionRequestSchema, type UpsertWatchlistItemDto, type UserSettingsDto } from '@fo-scanner/shared';
import { AppError } from '../common/errors';
import type { AppContext } from '../app';

export const registerRoutes = async (app: FastifyInstance, context: AppContext): Promise<void> => {
  const requireAuth = async (request: FastifyRequest) => {
    await request.jwtVerify();
    request.auth = await context.sessionService.authenticate(request.user as { sub?: string; sid?: string });
  };

  app.get('/health/live', async () => ({ status: 'ok' }));
  app.get('/health/ready', async () => ({ status: 'ok' }));

  app.post('/v1/session/bootstrap', async (request) => {
    const input = bootstrapSessionRequestSchema.parse(request.body ?? {});
    return context.sessionService.bootstrap(input, {
      userAgent: request.headers['user-agent'],
      ipAddress: request.ip
    });
  });

  app.get('/v1/auth/status', { preHandler: requireAuth }, async (request) => {
    return context.oauthService.getAuthStatus(request.auth.user.id);
  });

  app.get('/v1/brokers/upstox/connect-url', { preHandler: requireAuth }, async (request) => {
    const query = request.query as { frontendRedirectUri?: string };
    const frontendRedirectUri = query.frontendRedirectUri || context.env.FRONTEND_WEB_URL;
    return {
      url: await context.oauthService.buildConnectUrl(request.auth.user, frontendRedirectUri)
    };
  });

  app.get('/v1/brokers/upstox/callback', async (request, reply) => {
    const query = request.query as { code?: string; state?: string };
    const redirectUri = await context.oauthService.handleCallback(query.code, query.state);
    return reply.redirect(redirectUri);
  });

  app.delete('/v1/brokers/upstox/connection', { preHandler: requireAuth }, async (request) => {
    await context.oauthService.disconnect(request.auth.user.id);
    return { success: true };
  });

  app.get('/v1/dashboard/summary', { preHandler: requireAuth }, async (request) => {
    return context.systemService.getSummary(request.auth.user);
  });

  app.get('/v1/alerts', { preHandler: requireAuth }, async (request) => {
    const query = request.query as { limit?: string; symbol?: string };
    return context.alertsService.history(request.auth.user, Number(query.limit ?? 100), query.symbol);
  });

  app.post('/v1/alerts/:id/ack', { preHandler: requireAuth }, async (request) => {
    const params = request.params as { id: string };
    await context.alertsService.acknowledge(request.auth.user, params.id);
    return { success: true };
  });

  app.get('/v1/watchlist', { preHandler: requireAuth }, async (request) => {
    return context.watchlistService.list(request.auth.user);
  });

  app.post('/v1/watchlist', { preHandler: requireAuth }, async (request) => {
    const payload = request.body as UpsertWatchlistItemDto;
    const result = await context.watchlistService.upsert(request.auth.user, payload);
    await context.scannerOrchestrator.refreshUser(request.auth.user);
    return result;
  });

  app.delete('/v1/watchlist/:id', { preHandler: requireAuth }, async (request) => {
    const params = request.params as { id: string };
    await context.watchlistService.remove(request.auth.user, params.id);
    await context.scannerOrchestrator.refreshUser(request.auth.user);
    return { success: true };
  });

  app.get('/v1/instruments/search', { preHandler: requireAuth }, async (request) => {
    const query = request.query as { q?: string };
    if (!query.q?.trim()) {
      throw new AppError('Query is required', 400, 'SEARCH_QUERY_REQUIRED');
    }
    return context.instrumentService.search(query.q);
  });

  app.get('/v1/settings', { preHandler: requireAuth }, async (request) => {
    return context.settingsService.getForUser(request.auth.user);
  });

  app.put('/v1/settings', { preHandler: requireAuth }, async (request) => {
    const payload = request.body as UserSettingsDto;
    const result = await context.settingsService.updateForUser(request.auth.user, payload);
    await context.scannerOrchestrator.refreshUser(request.auth.user);
    return result;
  });

  app.get('/v1/system/status', { preHandler: requireAuth }, async (request) => {
    return context.systemService.getStatus(request.auth.user);
  });

  app.get('/v1/ws/live', { websocket: true }, async (socket, request) => {
    const query = request.query as { token?: string };
    if (!query.token) {
      socket.close(4001, 'Missing token');
      return;
    }

    try {
      const payload = await request.server.jwt.verify<{ sub?: string; sid?: string }>(query.token);
      const auth = await context.sessionService.authenticate(payload);
      context.clientHub.connect(auth.user.id, socket as any);
      socket.send(JSON.stringify({ type: 'system.heartbeat', payload: { now: new Date().toISOString() } }));
    } catch {
      socket.close(4001, 'Unauthorized');
    }
  });
};
''')

w('apps/api/src/types/fastify.d.ts', '''
import type { AuthContext } from '../modules/auth/session.service';

declare module 'fastify' {
  interface FastifyRequest {
    auth: AuthContext;
  }
}
''')

w('apps/api/src/app.ts', '''
import Fastify from 'fastify';
import cors from '@fastify/cors';
import helmet from '@fastify/helmet';
import jwt from '@fastify/jwt';
import websocket from '@fastify/websocket';
import rateLimit from '@fastify/rate-limit';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import { env } from './config/env';
import { logger } from './common/logger';
import { isAppError } from './common/errors';
import { buildDataSource } from './infrastructure/db/data-source';
import { SessionService } from './modules/auth/session.service';
import { UpstoxOAuthService } from './modules/auth/oauth.service';
import { UpstoxApiClient } from './infrastructure/providers/upstox/upstox-api-client';
import { InstrumentService } from './modules/instruments/instrument.service';
import { PairingService } from './modules/market/pairing.service';
import { SettingsService } from './modules/settings/settings.service';
import { AlertsService } from './modules/alerts/alerts.service';
import { ClientHub } from './infrastructure/realtime/client-hub';
import { SystemService } from './modules/system/system.service';
import { ScannerOrchestrator } from './modules/market/scanner-orchestrator.service';
import { registerRoutes } from './routes/index';

export type AppContext = {
  env: typeof env;
  sessionService: SessionService;
  oauthService: UpstoxOAuthService;
  instrumentService: InstrumentService;
  watchlistService: import('./modules/watchlist/watchlist.service').WatchlistService;
  settingsService: SettingsService;
  alertsService: AlertsService;
  systemService: SystemService;
  scannerOrchestrator: ScannerOrchestrator;
  clientHub: ClientHub;
};

export const buildApp = async () => {
  const app = Fastify({ loggerInstance: logger });
  const dataSource = buildDataSource();
  await dataSource.initialize();
  await dataSource.runMigrations();

  await app.register(cors, { origin: env.CORS_ORIGIN.split(',') });
  await app.register(helmet);
  await app.register(rateLimit, { max: 100, timeWindow: '1 minute' });
  await app.register(jwt, { secret: env.APP_JWT_SECRET });
  await app.register(websocket);
  await app.register(swagger, { openapi: { info: { title: 'F&O Scanner API', version: '1.0.0' } } });
  await app.register(swaggerUi, { routePrefix: '/docs' });

  const clientHub = new ClientHub();
  const upstoxApiClient = new UpstoxApiClient();
  const instrumentService = new InstrumentService(dataSource, upstoxApiClient);
  const pairingService = new PairingService(dataSource, instrumentService);
  const settingsService = new SettingsService(dataSource);
  const alertsService = new AlertsService(dataSource);
  const sessionService = new SessionService(dataSource, app.jwt.sign.bind(app.jwt));
  const oauthService = new UpstoxOAuthService(dataSource, upstoxApiClient);
  const placeholderSystemService = {
    logEvent: async () => undefined
  } as unknown as SystemService;
  const scannerOrchestrator = new ScannerOrchestrator(
    dataSource,
    oauthService,
    upstoxApiClient,
    pairingService,
    settingsService,
    alertsService,
    clientHub,
    instrumentService,
    placeholderSystemService
  );
  const systemService = new SystemService(dataSource, scannerOrchestrator);
  (scannerOrchestrator as any).systemService = systemService;
  const { WatchlistService } = await import('./modules/watchlist/watchlist.service');
  const watchlistService = new WatchlistService(dataSource, pairingService);

  const context: AppContext = {
    env,
    sessionService,
    oauthService,
    instrumentService,
    watchlistService,
    settingsService,
    alertsService,
    systemService,
    scannerOrchestrator,
    clientHub
  };

  app.setErrorHandler((error, _request, reply) => {
    if (isAppError(error)) {
      return reply.status(error.statusCode).send({
        error: error.code,
        message: error.message,
        details: error.details ?? null
      });
    }

    app.log.error({ err: error }, 'Unhandled API error');
    return reply.status(500).send({
      error: 'INTERNAL_SERVER_ERROR',
      message: 'An unexpected error occurred'
    });
  });

  await registerRoutes(app, context);

  app.addHook('onClose', async () => {
    await dataSource.destroy();
  });

  await scannerOrchestrator.start();

  return app;
};
''')

w('apps/api/src/index.ts', '''
import { buildApp } from './app';
import { env } from './config/env';
import { logger } from './common/logger';

const main = async () => {
  const app = await buildApp();
  await app.listen({ port: env.PORT, host: '0.0.0.0' });
  logger.info({ port: env.PORT }, 'API server listening');

  const shutdown = async () => {
    logger.info('Shutting down API server');
    await app.close();
    process.exit(0);
  };

  process.on('SIGINT', () => void shutdown());
  process.on('SIGTERM', () => void shutdown());
};

void main().catch((error) => {
  logger.error({ err: error }, 'Failed to start API');
  process.exit(1);
});
''')

w('apps/api/src/seeds/bootstrap.ts', '''
import { buildDataSource } from '../infrastructure/db/data-source';
import { User } from '../infrastructure/db/entities/user.entity';
import { UserSetting } from '../infrastructure/db/entities/user-setting.entity';
import { Watchlist } from '../infrastructure/db/entities/watchlist.entity';

const main = async () => {
  const dataSource = buildDataSource();
  await dataSource.initialize();
  const userRepo = dataSource.getRepository(User);
  const settingsRepo = dataSource.getRepository(UserSetting);
  const watchRepo = dataSource.getRepository(Watchlist);

  let user = await userRepo.findOne({ where: { deviceId: 'local-dev-trader' } });
  if (!user) {
    user = await userRepo.save(userRepo.create({ deviceId: 'local-dev-trader', displayName: 'Local Trader', status: 'active' }));
  }

  const settings = await settingsRepo.findOne({ where: { user: { id: user.id } }, relations: { user: true } });
  if (!settings) {
    await settingsRepo.save(settingsRepo.create({ user, threshold: 10, cooldownMs: 30000, freshnessMs: 10000, preferredExchange: 'NSE', darkMode: true, exchanges: ['NSE'], segments: ['NSE_EQ', 'NSE_FO'] }));
  }

  const existing = await watchRepo.count({ where: { user: { id: user.id } } });
  if (!existing) {
    await watchRepo.save([
      watchRepo.create({ user, symbol: 'RELIANCE', exchange: 'NSE', segment: 'NSE_FO', preferredMonthOffset: 0, enabled: true }),
      watchRepo.create({ user, symbol: 'TCS', exchange: 'NSE', segment: 'NSE_FO', preferredMonthOffset: 0, enabled: true })
    ]);
  }

  await dataSource.destroy();
};

void main();
''')

w('apps/api/src/migrations/1710000000000-InitialSchema.ts', '''
import { MigrationInterface, QueryRunner } from 'typeorm';

export class InitialSchema1710000000000 implements MigrationInterface {
  name = 'InitialSchema1710000000000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`CREATE TABLE IF NOT EXISTS users (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      "deviceId" varchar(120) NOT NULL UNIQUE,
      "displayName" varchar(120) NOT NULL DEFAULT 'Trader',
      status varchar(30) NOT NULL DEFAULT 'active'
    )`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS app_sessions (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      "sessionKey" varchar(120) NOT NULL UNIQUE,
      "userId" uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      "userAgent" varchar(255),
      "ipAddress" varchar(64),
      "expiresAt" timestamptz NOT NULL,
      "isActive" boolean NOT NULL DEFAULT true
    )`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS broker_connections (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      "userId" uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      broker varchar(20) NOT NULL DEFAULT 'UPSTOX',
      status varchar(40) NOT NULL DEFAULT 'idle',
      "brokerUserId" varchar(120),
      "accountName" varchar(120),
      "connectedAt" timestamptz,
      "tokenExpiresAt" timestamptz,
      "lastHeartbeatAt" timestamptz,
      "lastAuthorizedAt" timestamptz
    )`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS broker_access_tokens (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      "connectionId" uuid NOT NULL REFERENCES broker_connections(id) ON DELETE CASCADE,
      "cipherText" text NOT NULL,
      iv varchar(64) NOT NULL,
      "authTag" varchar(64) NOT NULL,
      "extendedCipherText" text,
      "extendedIv" varchar(64),
      "extendedAuthTag" varchar(64),
      "expiresAt" timestamptz NOT NULL,
      "isActive" boolean NOT NULL DEFAULT true
    )`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS instruments (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      "instrumentKey" varchar(120) NOT NULL UNIQUE,
      exchange varchar(20) NOT NULL,
      segment varchar(20) NOT NULL,
      "instrumentType" varchar(40) NOT NULL,
      "tradingSymbol" varchar(120) NOT NULL,
      "shortName" varchar(120),
      name varchar(120),
      "underlyingKey" varchar(120),
      "underlyingType" varchar(20),
      "expiryDate" date,
      "lotSize" float,
      "minimumLot" float,
      "tickSize" float,
      isin varchar(60),
      "isTradable" boolean NOT NULL DEFAULT true,
      metadata jsonb NOT NULL DEFAULT '{}'::jsonb
    )`);

    await queryRunner.query(`CREATE INDEX IF NOT EXISTS idx_instruments_underlying ON instruments("underlyingKey")`);
    await queryRunner.query(`CREATE INDEX IF NOT EXISTS idx_instruments_symbol ON instruments("tradingSymbol")`);
    await queryRunner.query(`CREATE INDEX IF NOT EXISTS idx_instruments_segment_type ON instruments(segment, "instrumentType")`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS watchlists (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      "userId" uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      symbol varchar(60) NOT NULL,
      exchange varchar(20) NOT NULL DEFAULT 'NSE',
      segment varchar(20) NOT NULL DEFAULT 'NSE_FO',
      "preferredMonthOffset" integer NOT NULL DEFAULT 0,
      enabled boolean NOT NULL DEFAULT true,
      UNIQUE("userId", symbol)
    )`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS instrument_pairs (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      "userId" uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      symbol varchar(60) NOT NULL,
      "spotInstrumentId" uuid REFERENCES instruments(id),
      "futureInstrumentId" uuid REFERENCES instruments(id),
      "monthType" varchar(20) NOT NULL DEFAULT 'near',
      "futureExpiryDate" date,
      status varchar(30) NOT NULL DEFAULT 'paired',
      enabled boolean NOT NULL DEFAULT true,
      UNIQUE("userId", symbol)
    )`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS alerts (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      "userId" uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      "pairId" uuid NOT NULL REFERENCES instrument_pairs(id) ON DELETE CASCADE,
      spread float NOT NULL,
      threshold float NOT NULL,
      "spotPrice" float NOT NULL,
      "futurePrice" float NOT NULL,
      "freshnessMs" integer NOT NULL,
      "dedupeKey" varchar(160) NOT NULL,
      "triggeredAt" timestamptz NOT NULL,
      "acknowledgedAt" timestamptz
    )`);
    await queryRunner.query(`CREATE INDEX IF NOT EXISTS idx_alerts_user_time ON alerts("userId", "triggeredAt")`);
    await queryRunner.query(`CREATE INDEX IF NOT EXISTS idx_alerts_dedupe ON alerts("dedupeKey")`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS user_settings (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      "userId" uuid NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
      threshold float NOT NULL DEFAULT 10,
      "cooldownMs" integer NOT NULL DEFAULT 30000,
      "freshnessMs" integer NOT NULL DEFAULT 10000,
      "preferredExchange" varchar(20) NOT NULL DEFAULT 'NSE',
      "darkMode" boolean NOT NULL DEFAULT true,
      exchanges jsonb NOT NULL DEFAULT '["NSE"]'::jsonb,
      segments jsonb NOT NULL DEFAULT '["NSE_EQ","NSE_FO"]'::jsonb
    )`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS oauth_states (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      state varchar(120) NOT NULL UNIQUE,
      "userId" uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      broker varchar(20) NOT NULL DEFAULT 'UPSTOX',
      "frontendRedirectUri" varchar(255) NOT NULL,
      "expiresAt" timestamptz NOT NULL,
      "consumedAt" timestamptz
    )`);

    await queryRunner.query(`CREATE TABLE IF NOT EXISTS system_events (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      "createdAt" timestamptz NOT NULL DEFAULT now(),
      "updatedAt" timestamptz NOT NULL DEFAULT now(),
      level varchar(20) NOT NULL,
      type varchar(80) NOT NULL,
      message varchar(255) NOT NULL,
      source varchar(80) NOT NULL DEFAULT 'system',
      payload jsonb NOT NULL DEFAULT '{}'::jsonb
    )`);
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query('DROP TABLE IF EXISTS system_events');
    await queryRunner.query('DROP TABLE IF EXISTS oauth_states');
    await queryRunner.query('DROP TABLE IF EXISTS user_settings');
    await queryRunner.query('DROP TABLE IF EXISTS alerts');
    await queryRunner.query('DROP TABLE IF EXISTS instrument_pairs');
    await queryRunner.query('DROP TABLE IF EXISTS watchlists');
    await queryRunner.query('DROP TABLE IF EXISTS instruments');
    await queryRunner.query('DROP TABLE IF EXISTS broker_access_tokens');
    await queryRunner.query('DROP TABLE IF EXISTS broker_connections');
    await queryRunner.query('DROP TABLE IF EXISTS app_sessions');
    await queryRunner.query('DROP TABLE IF EXISTS users');
  }
}
''')

w('apps/api/src/tests/setup.ts', '''
process.env.NODE_ENV = 'test';
process.env.PORT = '3001';
process.env.LOG_LEVEL = 'silent';
process.env.APP_BASE_URL = 'http://localhost:3000';
process.env.FRONTEND_WEB_URL = 'http://localhost:19006';
process.env.FRONTEND_DEEP_LINK_BASE = 'fo-scanner://auth/upstox-callback';
process.env.CORS_ORIGIN = 'http://localhost:19006';
process.env.DATABASE_URL = 'postgres://test:test@localhost:5432/test';
process.env.APP_JWT_SECRET = 'test-test-test-test-test-test-test-test';
process.env.TOKEN_ENCRYPTION_SECRET = 'test-token-secret-test-token-secret';
process.env.UPSTOX_CLIENT_ID = 'client';
process.env.UPSTOX_CLIENT_SECRET = 'secret';
process.env.UPSTOX_REDIRECT_URI = 'http://localhost:3000/v1/brokers/upstox/callback';
process.env.UPSTOX_AUTH_DIALOG_URL = 'https://api.upstox.com/v2/login/authorization/dialog';
process.env.UPSTOX_TOKEN_URL = 'https://api.upstox.com/v2/login/authorization/token';
process.env.UPSTOX_MARKET_AUTHORIZE_V3_URL = 'https://api.upstox.com/v3/feed/market-data-feed/authorize';
process.env.UPSTOX_BOD_INSTRUMENTS_URL = 'https://assets.upstox.com/test.json.gz';
''')

print('Backend generated.')
