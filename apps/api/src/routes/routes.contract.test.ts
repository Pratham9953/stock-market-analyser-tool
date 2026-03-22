import Fastify from 'fastify';
import jwt from '@fastify/jwt';
import websocket from '@fastify/websocket';
import { registerRoutes } from './index';

describe('route contracts', () => {
  it('bootstraps a session through the public route', async () => {
    const app = Fastify();
    await app.register(jwt, { secret: 'test-test-test-test-test-test-test-test' });
    await app.register(websocket);

    await registerRoutes(app, {
      env: {} as never,
      sessionService: {
        bootstrap: vi.fn(async () => ({
          token: 'jwt',
          user: { id: '550e8400-e29b-41d4-a716-446655440000', deviceId: 'device-123456', displayName: 'Trader', createdAt: new Date().toISOString() },
          brokerConnection: null,
          settings: { threshold: 10, cooldownMs: 30000, freshnessMs: 10000, preferredExchange: 'NSE', darkMode: true }
        })),
        authenticate: vi.fn()
      } as never,
      oauthService: { getAuthStatus: vi.fn(), buildConnectUrl: vi.fn(), handleCallback: vi.fn(), disconnect: vi.fn() } as never,
      instrumentService: { search: vi.fn() } as never,
      watchlistService: { list: vi.fn(), upsert: vi.fn(), remove: vi.fn() } as never,
      settingsService: { getForUser: vi.fn(), updateForUser: vi.fn() } as never,
      alertsService: { history: vi.fn(), acknowledge: vi.fn() } as never,
      systemService: { getSummary: vi.fn(), getStatus: vi.fn() } as never,
      scannerOrchestrator: { refreshUser: vi.fn() } as never,
      clientHub: { connect: vi.fn() } as never
    });

    const response = await app.inject({
      method: 'POST',
      url: '/v1/session/bootstrap',
      payload: { deviceId: 'device-123456' }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json().token).toBe('jwt');
  });
});
