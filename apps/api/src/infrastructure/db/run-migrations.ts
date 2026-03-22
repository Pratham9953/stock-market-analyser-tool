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
