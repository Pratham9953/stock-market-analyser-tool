import { MigrationInterface, QueryRunner } from 'typeorm';

export class InitialSchema1710000000000 implements MigrationInterface {
  name = 'InitialSchema1710000000000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query('CREATE EXTENSION IF NOT EXISTS pgcrypto');
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
