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
