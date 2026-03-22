import { DataSource } from 'typeorm';
import { UserSetting } from '../../infrastructure/db/entities/user-setting.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import { env } from '../../config/env';
import { userSettingsSchema, type UserSettingsDto } from '@fo-scanner/shared';

export class SettingsService {
  constructor(private readonly dataSource: DataSource) {}

  async getForUser(user: User): Promise<UserSettingsDto> {
    const repo = this.dataSource.getRepository(UserSetting);
    let settings = await repo.findOne({ where: { user: { id: user.id } }, relations: { user: true } });
    if (!settings) {
      settings = await repo.save(
        repo.create({
          user,
          threshold: env.DEFAULT_ALERT_THRESHOLD,
          cooldownMs: env.DEFAULT_ALERT_COOLDOWN_MS,
          freshnessMs: env.DEFAULT_TICK_FRESHNESS_MS,
          preferredExchange: 'NSE',
          darkMode: true,
          exchanges: ['NSE'],
          segments: ['NSE_EQ', 'NSE_FO']
        })
      );
    }
    return userSettingsSchema.parse({
      threshold: settings.threshold,
      cooldownMs: settings.cooldownMs,
      freshnessMs: settings.freshnessMs,
      preferredExchange: settings.preferredExchange,
      darkMode: settings.darkMode,
      exchanges: settings.exchanges,
      segments: settings.segments
    });
  }

  async updateForUser(user: User, input: UserSettingsDto): Promise<UserSettingsDto> {
    const repo = this.dataSource.getRepository(UserSetting);
    const parsed = userSettingsSchema.parse(input);
    let settings = await repo.findOne({ where: { user: { id: user.id } }, relations: { user: true } });
    if (!settings) {
      settings = repo.create({ user, ...parsed });
    } else {
      Object.assign(settings, parsed);
    }
    await repo.save(settings);
    return parsed;
  }
}
