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
