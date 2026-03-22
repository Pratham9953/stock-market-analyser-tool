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
