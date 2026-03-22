from pathlib import Path
from textwrap import dedent

root = Path('/mnt/data/fo-backwardation-scanner')

def w(path: str, content: str):
    file_path = root / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(dedent(content).lstrip('\n'), encoding='utf-8')

# Root files
w('AGENTS.md', '''
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
''')

w('package.json', '''
{
  "name": "fo-backwardation-scanner",
  "private": true,
  "version": "1.0.0",
  "packageManager": "pnpm@10.2.1",
  "scripts": {
    "dev": "turbo run dev --parallel --continue --filter=@fo-scanner/api --filter=@fo-scanner/mobile",
    "build": "turbo run build",
    "lint": "turbo run lint",
    "typecheck": "turbo run typecheck",
    "test": "turbo run test",
    "clean": "turbo run clean && rimraf node_modules .turbo",
    "docker:up": "docker compose up --build -d",
    "docker:down": "docker compose down -v",
    "prepare": "husky"
  },
  "devDependencies": {
    "@playwright/test": "^1.53.0",
    "@types/node": "^22.15.30",
    "eslint": "^9.28.0",
    "husky": "^9.1.7",
    "lint-staged": "^15.5.2",
    "prettier": "^3.5.3",
    "rimraf": "^6.0.1",
    "turbo": "^2.5.3",
    "typescript": "^5.8.3"
  },
  "lint-staged": {
    "*.{ts,tsx,js,jsx,json,md,yml,yaml}": [
      "prettier --write"
    ],
    "apps/**/*.{ts,tsx}": [
      "eslint --fix"
    ],
    "packages/**/*.{ts,tsx}": [
      "eslint --fix"
    ]
  }
}
''')

w('pnpm-workspace.yaml', '''
packages:
  - apps/*
  - packages/*
''')

w('turbo.json', '''
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".expo/**", "build/**", "coverage/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^lint"]
    },
    "typecheck": {
      "dependsOn": ["^typecheck"]
    },
    "test": {
      "dependsOn": ["^test"],
      "outputs": ["coverage/**", "playwright-report/**"]
    },
    "clean": {
      "cache": false
    }
  }
}
''')

w('tsconfig.base.json', '''
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "skipLibCheck": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "baseUrl": ".",
    "paths": {
      "@fo-scanner/shared": ["packages/shared/src/index.ts"],
      "@fo-scanner/shared/*": ["packages/shared/src/*"],
      "@fo-scanner/ui": ["packages/ui/src/index.ts"],
      "@fo-scanner/testing": ["packages/testing/src/index.ts"],
      "@fo-scanner/config/*": ["packages/config/*"]
    }
  }
}
''')

w('.editorconfig', '''
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true
''')

w('.gitignore', '''
node_modules
.pnpm-store
.turbo
.env
.env.*
!.env.example
coverage
playwright-report
.test-results
.next
.expo
expo-env.d.ts
apps/mobile/dist
apps/api/dist
packages/*/dist
postgres-data
.DS_Store
*.log
''')

w('.npmrc', '''
auto-install-peers=true
strict-peer-dependencies=false
''')

w('prettier.config.cjs', '''
module.exports = require('./packages/config/prettier.cjs');
''')

w('eslint.config.mjs', '''
import config from './packages/config/eslint/base.mjs';

export default config;
''')

w('Makefile', '''
.PHONY: install dev build lint typecheck test docker-up docker-down

install:
	pnpm install

dev:
	pnpm dev

build:
	pnpm build

lint:
	pnpm lint

typecheck:
	pnpm typecheck

test:
	pnpm test

docker-up:
	pnpm docker:up

docker-down:
	pnpm docker:down
''')

w('.husky/pre-commit', '''
#!/usr/bin/env sh
pnpm lint-staged
''')

w('docker-compose.yml', '''
services:
  postgres:
    image: postgres:16-alpine
    container_name: fo_scanner_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: fo_scanner
      POSTGRES_USER: fo_scanner
      POSTGRES_PASSWORD: fo_scanner
    ports:
      - "5432:5432"
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fo_scanner -d fo_scanner"]
      interval: 10s
      timeout: 5s
      retries: 10

  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
    env_file:
      - apps/api/.env.example
    environment:
      DATABASE_URL: postgres://fo_scanner:fo_scanner@postgres:5432/fo_scanner
      APP_BASE_URL: http://localhost:3000
      FRONTEND_WEB_URL: http://localhost:19006
      CORS_ORIGIN: http://localhost:19006,http://localhost:8081
    ports:
      - "3000:3000"

  web:
    build:
      context: .
      dockerfile: apps/mobile/Dockerfile
    depends_on:
      - api
    env_file:
      - apps/mobile/.env.example
    environment:
      EXPO_PUBLIC_API_URL: http://localhost:3000
      EXPO_PUBLIC_WS_URL: ws://localhost:3000/v1/ws/live
      EXPO_PUBLIC_UPSTOX_CALLBACK_URL: http://localhost:19006/auth/upstox-callback
      EXPO_PUBLIC_APP_NAME: F&O Backwardation Scanner
    ports:
      - "19006:19006"
''')

w('.github/workflows/ci.yml', '''
name: CI

on:
  push:
    branches: [main, master]
  pull_request:

jobs:
  test-build:
    runs-on: ubuntu-latest
    timeout-minutes: 25
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 10.2.1

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile=false

      - name: Lint
        run: pnpm lint

      - name: Typecheck
        run: pnpm typecheck

      - name: Test
        run: pnpm test

      - name: Build
        run: pnpm build
''')

# packages/config
w('packages/config/package.json', '''
{
  "name": "@fo-scanner/config",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "exports": {
    "./eslint/base": "./eslint/base.mjs",
    "./prettier": "./prettier.cjs",
    "./tsconfig/base": "./tsconfig/base.json",
    "./tsconfig/node": "./tsconfig/node.json",
    "./tsconfig/react-native": "./tsconfig/react-native.json"
  }
}
''')

w('packages/config/eslint/base.mjs', '''
import js from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactNative from 'eslint-plugin-react-native';

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: process.cwd()
      },
      globals: {
        ...globals.node,
        ...globals.browser
      }
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-native': reactNative
    },
    settings: {
      react: {
        version: 'detect'
      }
    },
    rules: {
      '@typescript-eslint/consistent-type-imports': 'error',
      '@typescript-eslint/no-misused-promises': ['error', { checksVoidReturn: false }],
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/require-await': 'off',
      'react/react-in-jsx-scope': 'off',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'error'
    }
  },
  {
    files: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off'
    }
  },
  {
    ignores: ['**/dist/**', '**/coverage/**', '**/.expo/**', '**/playwright-report/**']
  }
);
''')

w('packages/config/prettier.cjs', '''
module.exports = {
  semi: true,
  singleQuote: true,
  trailingComma: 'none',
  printWidth: 100
};
''')

w('packages/config/tsconfig/base.json', '''
{
  "extends": "../../../tsconfig.base.json",
  "compilerOptions": {
    "composite": false
  }
}
''')

w('packages/config/tsconfig/node.json', '''
{
  "extends": "./base.json",
  "compilerOptions": {
    "lib": ["ES2022"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "types": ["node"]
  }
}
''')

w('packages/config/tsconfig/react-native.json', '''
{
  "extends": "./base.json",
  "compilerOptions": {
    "jsx": "react-jsx",
    "lib": ["ES2022", "DOM"],
    "types": ["react", "react-native", "jest"]
  }
}
''')

# packages/shared
w('packages/shared/package.json', '''
{
  "name": "@fo-scanner/shared",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "main": "src/index.ts",
  "types": "src/index.ts",
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "lint": "eslint src --ext .ts",
    "typecheck": "tsc --project tsconfig.json --noEmit",
    "test": "vitest run --passWithNoTests",
    "clean": "rimraf dist"
  },
  "dependencies": {
    "zod": "^3.24.4"
  },
  "devDependencies": {
    "rimraf": "^6.0.1",
    "tsup": "^8.5.0",
    "vitest": "^3.2.4"
  }
}
''')

w('packages/shared/tsconfig.json', '''
{
  "extends": "../config/tsconfig/base.json",
  "compilerOptions": {
    "outDir": "dist"
  },
  "include": ["src/**/*.ts"]
}
''')

w('packages/shared/src/contracts.ts', '''
import { z } from 'zod';

export const brokerNameSchema = z.enum(['UPSTOX']);
export const connectionStatusSchema = z.enum(['idle', 'connecting', 'connected', 'expired', 'error']);
export const systemHealthSchema = z.enum(['ok', 'degraded', 'error']);
export const alertSeveritySchema = z.enum(['info', 'warning', 'critical']);

export const bootstrapSessionRequestSchema = z.object({
  deviceId: z.string().min(6),
  displayName: z.string().trim().min(1).max(120).optional()
});

export const userSchema = z.object({
  id: z.string().uuid(),
  deviceId: z.string(),
  displayName: z.string(),
  createdAt: z.string()
});

export const brokerConnectionSchema = z.object({
  id: z.string().uuid(),
  broker: brokerNameSchema,
  status: connectionStatusSchema,
  brokerUserId: z.string().nullable(),
  accountName: z.string().nullable(),
  tokenExpiresAt: z.string().nullable(),
  connectedAt: z.string().nullable(),
  lastHeartbeatAt: z.string().nullable()
});

export const sessionBootstrapResponseSchema = z.object({
  token: z.string(),
  user: userSchema,
  brokerConnection: brokerConnectionSchema.nullable(),
  settings: z.object({
    threshold: z.number(),
    cooldownMs: z.number(),
    freshnessMs: z.number(),
    preferredExchange: z.string(),
    darkMode: z.boolean()
  })
});

export const instrumentSummarySchema = z.object({
  id: z.string().uuid(),
  instrumentKey: z.string(),
  exchange: z.string(),
  segment: z.string(),
  instrumentType: z.string(),
  tradingSymbol: z.string(),
  shortName: z.string().nullable(),
  underlyingKey: z.string().nullable(),
  expiryDate: z.string().nullable(),
  lotSize: z.number().nullable()
});

export const watchlistItemSchema = z.object({
  id: z.string().uuid(),
  symbol: z.string(),
  exchange: z.string(),
  segment: z.string(),
  enabled: z.boolean(),
  preferredMonthOffset: z.number().int().min(0).max(2),
  spotInstrument: instrumentSummarySchema.nullable(),
  futureInstrument: instrumentSummarySchema.nullable(),
  updatedAt: z.string()
});

export const upsertWatchlistItemSchema = z.object({
  symbol: z.string().trim().min(1),
  exchange: z.string().trim().default('NSE'),
  segment: z.string().trim().default('NSE_FO'),
  preferredMonthOffset: z.number().int().min(0).max(2).default(0),
  enabled: z.boolean().default(true)
});

export const alertHistoryItemSchema = z.object({
  id: z.string().uuid(),
  pairId: z.string().uuid(),
  symbol: z.string(),
  spread: z.number(),
  threshold: z.number(),
  spotPrice: z.number(),
  futurePrice: z.number(),
  futureExpiry: z.string().nullable(),
  triggeredAt: z.string(),
  freshnessMs: z.number(),
  dedupeKey: z.string(),
  acknowledgedAt: z.string().nullable()
});

export const dashboardSummarySchema = z.object({
  activeConnection: z.boolean(),
  subscribedInstrumentCount: z.number().int(),
  activeWatchlistCount: z.number().int(),
  liveAlertCount: z.number().int(),
  lastTickAt: z.string().nullable(),
  backendLatencyMs: z.number(),
  websocketState: z.enum(['connected', 'connecting', 'closed']),
  marketDataState: connectionStatusSchema,
  threshold: z.number()
});

export const userSettingsSchema = z.object({
  threshold: z.number().min(0).max(100000),
  cooldownMs: z.number().int().min(1000).max(900000),
  freshnessMs: z.number().int().min(1000).max(300000),
  preferredExchange: z.string().min(2).max(20),
  darkMode: z.boolean(),
  exchanges: z.array(z.string()).default(['NSE']),
  segments: z.array(z.string()).default(['NSE_EQ', 'NSE_FO'])
});

export const dashboardStatusSchema = z.object({
  backend: systemHealthSchema,
  database: systemHealthSchema,
  brokerAuth: connectionStatusSchema,
  websocket: z.enum(['connected', 'connecting', 'closed']),
  marketFeed: connectionStatusSchema,
  instrumentSyncAt: z.string().nullable(),
  marketStatus: z.record(z.string(), z.string()),
  recentEvents: z.array(
    z.object({
      id: z.string().uuid(),
      level: alertSeveritySchema,
      type: z.string(),
      message: z.string(),
      createdAt: z.string()
    })
  )
});

export const authStatusResponseSchema = z.object({
  sessionActive: z.boolean(),
  brokerConnection: brokerConnectionSchema.nullable(),
  reauthRequired: z.boolean(),
  connectUrl: z.string().nullable()
});

export type BootstrapSessionRequest = z.infer<typeof bootstrapSessionRequestSchema>;
export type SessionBootstrapResponse = z.infer<typeof sessionBootstrapResponseSchema>;
export type InstrumentSummary = z.infer<typeof instrumentSummarySchema>;
export type WatchlistItemDto = z.infer<typeof watchlistItemSchema>;
export type UpsertWatchlistItemDto = z.infer<typeof upsertWatchlistItemSchema>;
export type AlertHistoryItemDto = z.infer<typeof alertHistoryItemSchema>;
export type DashboardSummaryDto = z.infer<typeof dashboardSummarySchema>;
export type UserSettingsDto = z.infer<typeof userSettingsSchema>;
export type DashboardStatusDto = z.infer<typeof dashboardStatusSchema>;
export type AuthStatusResponseDto = z.infer<typeof authStatusResponseSchema>;
export type BrokerConnectionDto = z.infer<typeof brokerConnectionSchema>;
''')

w('packages/shared/src/events.ts', '''
import { z } from 'zod';
import { alertHistoryItemSchema, dashboardStatusSchema, dashboardSummarySchema } from './contracts';

export const liveSpreadEventSchema = z.object({
  type: z.literal('scanner.spread'),
  payload: z.object({
    pairId: z.string().uuid(),
    symbol: z.string(),
    spread: z.number(),
    spotPrice: z.number(),
    futurePrice: z.number(),
    futureExpiry: z.string().nullable(),
    observedAt: z.string()
  })
});

export const alertCreatedEventSchema = z.object({
  type: z.literal('alert.created'),
  payload: alertHistoryItemSchema
});

export const dashboardSummaryEventSchema = z.object({
  type: z.literal('dashboard.summary'),
  payload: dashboardSummarySchema
});

export const systemStatusEventSchema = z.object({
  type: z.literal('system.status'),
  payload: dashboardStatusSchema
});

export const heartbeatEventSchema = z.object({
  type: z.literal('system.heartbeat'),
  payload: z.object({
    now: z.string()
  })
});

export const websocketEventSchema = z.discriminatedUnion('type', [
  liveSpreadEventSchema,
  alertCreatedEventSchema,
  dashboardSummaryEventSchema,
  systemStatusEventSchema,
  heartbeatEventSchema
]);

export type LiveSpreadEvent = z.infer<typeof liveSpreadEventSchema>;
export type AlertCreatedEvent = z.infer<typeof alertCreatedEventSchema>;
export type DashboardSummaryEvent = z.infer<typeof dashboardSummaryEventSchema>;
export type SystemStatusEvent = z.infer<typeof systemStatusEventSchema>;
export type HeartbeatEvent = z.infer<typeof heartbeatEventSchema>;
export type WebsocketEvent = z.infer<typeof websocketEventSchema>;
''')

w('packages/shared/src/env.ts', '''
import { z } from 'zod';

export const mobilePublicEnvSchema = z.object({
  EXPO_PUBLIC_API_URL: z.string().url(),
  EXPO_PUBLIC_WS_URL: z.string(),
  EXPO_PUBLIC_UPSTOX_CALLBACK_URL: z.string(),
  EXPO_PUBLIC_APP_NAME: z.string().default('F&O Backwardation Scanner')
});

export type MobilePublicEnv = z.infer<typeof mobilePublicEnvSchema>;
''')

w('packages/shared/src/utils.ts', '''
export const formatCurrency = (value: number): string =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  }).format(value);

export const formatDateTime = (value: string | null): string => {
  if (!value) return '—';
  return new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(new Date(value));
};

export const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));
''')

w('packages/shared/src/index.ts', '''
export * from './contracts';
export * from './events';
export * from './env';
export * from './utils';
''')

# packages/ui
w('packages/ui/package.json', '''
{
  "name": "@fo-scanner/ui",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "main": "src/index.ts",
  "types": "src/index.ts",
  "scripts": {
    "build": "tsup src/index.tsx --format esm,cjs --dts",
    "lint": "eslint src --ext .ts,.tsx",
    "typecheck": "tsc --project tsconfig.json --noEmit",
    "test": "vitest run --passWithNoTests",
    "clean": "rimraf dist"
  },
  "dependencies": {
    "react": "19.1.0",
    "react-native": "0.81.0",
    "react-native-svg": "15.12.1"
  },
  "devDependencies": {
    "@types/react": "^19.1.8",
    "rimraf": "^6.0.1",
    "tsup": "^8.5.0",
    "vitest": "^3.2.4"
  }
}
''')

w('packages/ui/tsconfig.json', '''
{
  "extends": "../config/tsconfig/react-native.json",
  "compilerOptions": {
    "outDir": "dist"
  },
  "include": ["src/**/*.ts", "src/**/*.tsx"]
}
''')

w('packages/ui/src/index.tsx', '''
import React, { PropsWithChildren } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  useColorScheme,
  View,
  type StyleProp,
  type ViewStyle
} from 'react-native';
import Svg, { Path, Polyline } from 'react-native-svg';

const palette = {
  light: {
    background: '#F4F7FB',
    surface: '#FFFFFF',
    border: '#D7E1EE',
    text: '#0B1F35',
    muted: '#63758C',
    accent: '#1B74F4',
    success: '#168A52',
    warning: '#D97706',
    danger: '#D14343'
  },
  dark: {
    background: '#07111F',
    surface: '#0E1A2B',
    border: '#22324A',
    text: '#F6F9FC',
    muted: '#A8B5C7',
    accent: '#58A6FF',
    success: '#4ADE80',
    warning: '#FDBA74',
    danger: '#F87171'
  }
} as const;

export const useTheme = () => {
  const scheme = useColorScheme() === 'dark' ? 'dark' : 'light';
  return palette[scheme];
};

export const Screen = ({ children }: PropsWithChildren) => {
  const theme = useTheme();
  return <ScrollView style={{ flex: 1, backgroundColor: theme.background }} contentContainerStyle={styles.screen}>{children}</ScrollView>;
};

export const Card = ({ children, style }: PropsWithChildren<{ style?: StyleProp<ViewStyle> }>) => {
  const theme = useTheme();
  return <View style={[styles.card, { backgroundColor: theme.surface, borderColor: theme.border }, style]}>{children}</View>;
};

export const SectionHeader = ({ title, subtitle }: { title: string; subtitle?: string }) => {
  const theme = useTheme();
  return (
    <View style={styles.sectionHeader}>
      <Text style={[styles.sectionTitle, { color: theme.text }]}>{title}</Text>
      {subtitle ? <Text style={[styles.sectionSubtitle, { color: theme.muted }]}>{subtitle}</Text> : null}
    </View>
  );
};

export const Badge = ({ label, tone = 'neutral' }: { label: string; tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'accent' }) => {
  const theme = useTheme();
  const colors = {
    neutral: theme.muted,
    success: theme.success,
    warning: theme.warning,
    danger: theme.danger,
    accent: theme.accent
  } as const;
  return (
    <View style={[styles.badge, { borderColor: colors[tone] }]}>
      <Text style={[styles.badgeText, { color: colors[tone] }]}>{label}</Text>
    </View>
  );
};

export const PrimaryButton = ({ title, onPress, disabled }: { title: string; onPress: () => void; disabled?: boolean }) => {
  const theme = useTheme();
  return (
    <Pressable onPress={onPress} disabled={disabled} style={[styles.button, { backgroundColor: disabled ? theme.border : theme.accent }]}> 
      <Text style={[styles.buttonText, { color: '#FFFFFF' }]}>{title}</Text>
    </Pressable>
  );
};

export const MetricCard = ({ label, value, helper, tone = 'accent' }: { label: string; value: string; helper?: string; tone?: 'accent' | 'success' | 'warning' | 'danger' }) => {
  const theme = useTheme();
  const toneColor = { accent: theme.accent, success: theme.success, warning: theme.warning, danger: theme.danger }[tone];
  return (
    <Card style={styles.metricCard}>
      <Text style={[styles.metricLabel, { color: theme.muted }]}>{label}</Text>
      <Text style={[styles.metricValue, { color: theme.text }]}>{value}</Text>
      {helper ? <Text style={[styles.metricHelper, { color: toneColor }]}>{helper}</Text> : null}
    </Card>
  );
};

export const EmptyState = ({ title, subtitle }: { title: string; subtitle: string }) => {
  const theme = useTheme();
  return (
    <Card>
      <Text style={[styles.emptyTitle, { color: theme.text }]}>{title}</Text>
      <Text style={[styles.emptySubtitle, { color: theme.muted }]}>{subtitle}</Text>
    </Card>
  );
};

export const LoadingState = ({ label }: { label: string }) => {
  const theme = useTheme();
  return (
    <Card>
      <Text style={[styles.emptySubtitle, { color: theme.muted }]}>{label}</Text>
    </Card>
  );
};

export const Sparkline = ({ points, width = 140, height = 40 }: { points: number[]; width?: number; height?: number }) => {
  const theme = useTheme();
  if (points.length < 2) {
    return (
      <Svg width={width} height={height}>
        <Path d={`M0 ${height / 2} L${width} ${height / 2}`} stroke={theme.border} strokeWidth={2} fill="none" />
      </Svg>
    );
  }

  const min = Math.min(...points);
  const max = Math.max(...points);
  const span = max - min || 1;
  const stepX = width / Math.max(points.length - 1, 1);
  const path = points
    .map((point, index) => {
      const x = index * stepX;
      const y = height - ((point - min) / span) * height;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <Svg width={width} height={height}>
      <Polyline points={path} stroke={theme.accent} strokeWidth={2.5} fill="none" strokeLinejoin="round" strokeLinecap="round" />
    </Svg>
  );
};

export const DataRow = ({ label, value }: { label: string; value: string }) => {
  const theme = useTheme();
  return (
    <View style={[styles.dataRow, { borderBottomColor: theme.border }]}> 
      <Text style={[styles.dataLabel, { color: theme.muted }]}>{label}</Text>
      <Text style={[styles.dataValue, { color: theme.text }]}>{value}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  screen: {
    padding: 16,
    gap: 16
  },
  card: {
    borderRadius: 20,
    borderWidth: 1,
    padding: 16,
    gap: 10,
    shadowOpacity: 0.08,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
    elevation: 2
  },
  sectionHeader: {
    gap: 4
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700'
  },
  sectionSubtitle: {
    fontSize: 14,
    lineHeight: 20
  },
  badge: {
    alignSelf: 'flex-start',
    borderRadius: 999,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 5
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600'
  },
  button: {
    borderRadius: 16,
    paddingVertical: 14,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center'
  },
  buttonText: {
    fontSize: 15,
    fontWeight: '700'
  },
  metricCard: {
    minWidth: 180,
    flex: 1
  },
  metricLabel: {
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.7
  },
  metricValue: {
    fontSize: 28,
    fontWeight: '800'
  },
  metricHelper: {
    fontSize: 13,
    fontWeight: '600'
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '700'
  },
  emptySubtitle: {
    fontSize: 14,
    lineHeight: 20
  },
  dataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: StyleSheet.hairlineWidth
  },
  dataLabel: {
    fontSize: 13,
    fontWeight: '500'
  },
  dataValue: {
    fontSize: 13,
    fontWeight: '700'
  }
});
''')

# packages/testing
w('packages/testing/package.json', '''
{
  "name": "@fo-scanner/testing",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "main": "src/index.ts",
  "types": "src/index.ts",
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "lint": "eslint src --ext .ts,.tsx",
    "typecheck": "tsc --project tsconfig.json --noEmit",
    "test": "vitest run --passWithNoTests",
    "clean": "rimraf dist"
  },
  "dependencies": {
    "@tanstack/react-query": "^5.81.5",
    "@testing-library/react-native": "^13.2.0",
    "msw": "^2.10.2",
    "react": "19.1.0",
    "react-native": "0.81.0"
  },
  "devDependencies": {
    "@types/react": "^19.1.8",
    "rimraf": "^6.0.1",
    "tsup": "^8.5.0",
    "vitest": "^3.2.4"
  }
}
''')

w('packages/testing/tsconfig.json', '''
{
  "extends": "../config/tsconfig/react-native.json",
  "compilerOptions": {
    "outDir": "dist"
  },
  "include": ["src/**/*.ts", "src/**/*.tsx"]
}
''')

w('packages/testing/src/index.tsx', '''
import React, { PropsWithChildren } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react-native';

export const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

export const renderWithProviders = (ui: React.ReactElement) => {
  const client = createTestQueryClient();

  const Wrapper = ({ children }: PropsWithChildren) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;

  return render(ui, { wrapper: Wrapper });
};
''')

print('Root and packages generated.')
