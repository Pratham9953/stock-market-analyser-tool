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
