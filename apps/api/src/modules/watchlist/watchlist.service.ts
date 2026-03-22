import { DataSource } from 'typeorm';
import { upsertWatchlistItemSchema, type UpsertWatchlistItemDto, type WatchlistItemDto } from '@fo-scanner/shared';
import { Watchlist } from '../../infrastructure/db/entities/watchlist.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import { PairingService } from '../market/pairing.service';

export class WatchlistService {
  constructor(private readonly dataSource: DataSource, private readonly pairingService: PairingService) {}

  async list(user: User): Promise<WatchlistItemDto[]> {
    return this.pairingService.listForUser(user);
  }

  async upsert(user: User, input: UpsertWatchlistItemDto): Promise<WatchlistItemDto[]> {
    const parsed = upsertWatchlistItemSchema.parse(input);
    const repo = this.dataSource.getRepository(Watchlist);
    const existing = await repo.findOne({ where: { user: { id: user.id }, symbol: parsed.symbol.toUpperCase() }, relations: { user: true } });

    if (existing) {
      Object.assign(existing, {
        symbol: parsed.symbol.toUpperCase(),
        exchange: parsed.exchange,
        segment: parsed.segment,
        preferredMonthOffset: parsed.preferredMonthOffset,
        enabled: parsed.enabled
      });
      await repo.save(existing);
    } else {
      await repo.save(
        repo.create({
          user,
          symbol: parsed.symbol.toUpperCase(),
          exchange: parsed.exchange,
          segment: parsed.segment,
          preferredMonthOffset: parsed.preferredMonthOffset,
          enabled: parsed.enabled
        })
      );
    }

    await this.pairingService.refreshForUser(user);
    return this.pairingService.listForUser(user);
  }

  async remove(user: User, watchlistId: string): Promise<void> {
    const repo = this.dataSource.getRepository(Watchlist);
    await repo.delete({ id: watchlistId, user: { id: user.id } });
    await this.pairingService.refreshForUser(user);
  }
}
