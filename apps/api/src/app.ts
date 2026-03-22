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
import { WatchlistService } from './modules/watchlist/watchlist.service';
import { registerRoutes } from './routes/index';

export type AppContext = {
  env: typeof env;
  sessionService: SessionService;
  oauthService: UpstoxOAuthService;
  instrumentService: InstrumentService;
  watchlistService: WatchlistService;
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
  const scannerOrchestrator = new ScannerOrchestrator(
    dataSource,
    oauthService,
    upstoxApiClient,
    pairingService,
    settingsService,
    alertsService,
    clientHub,
    instrumentService
  );
  const systemService = new SystemService(dataSource, scannerOrchestrator);
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
      return reply.status(error.statusCode).send({ error: error.code, message: error.message, details: error.details ?? null });
    }
    app.log.error({ err: error }, 'Unhandled API error');
    return reply.status(500).send({ error: 'INTERNAL_SERVER_ERROR', message: 'An unexpected error occurred' });
  });

  await registerRoutes(app, context);

  app.addHook('onClose', async () => {
    await dataSource.destroy();
  });

  await scannerOrchestrator.start();
  return app;
};
