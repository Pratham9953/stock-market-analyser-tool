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
