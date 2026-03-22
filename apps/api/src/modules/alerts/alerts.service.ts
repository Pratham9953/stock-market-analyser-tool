import { DataSource } from 'typeorm';
import { Alert } from '../../infrastructure/db/entities/alert.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import type { AlertHistoryItemDto } from '@fo-scanner/shared';
import type { SpreadCandidate } from '../market/spread-detector.service';

export class AlertsService {
  constructor(private readonly dataSource: DataSource) {}

  async create(user: User, candidate: SpreadCandidate): Promise<AlertHistoryItemDto> {
    const repo = this.dataSource.getRepository(Alert);
    const alert = await repo.save(
      repo.create({
        user,
        pair: candidate.pair,
        spread: candidate.spread,
        threshold: candidate.threshold,
        spotPrice: candidate.spotPrice,
        futurePrice: candidate.futurePrice,
        freshnessMs: candidate.freshnessMs,
        dedupeKey: candidate.dedupeKey,
        triggeredAt: candidate.observedAt,
        acknowledgedAt: null
      })
    );
    return this.toDto(alert);
  }

  async history(user: User, limit = 100, symbol?: string): Promise<AlertHistoryItemDto[]> {
    const repo = this.dataSource.getRepository(Alert);
    const qb = repo
      .createQueryBuilder('alert')
      .leftJoinAndSelect('alert.pair', 'pair')
      .where('alert.userId = :userId', { userId: user.id })
      .orderBy('alert.triggeredAt', 'DESC')
      .limit(limit);

    if (symbol?.trim()) {
      qb.andWhere('pair.symbol = :symbol', { symbol: symbol.trim().toUpperCase() });
    }

    const alerts = await qb.getMany();
    return alerts.map((item) => this.toDto(item));
  }

  async acknowledge(user: User, alertId: string): Promise<void> {
    const repo = this.dataSource.getRepository(Alert);
    await repo.update({ id: alertId, user: { id: user.id } }, { acknowledgedAt: new Date() });
  }

  toDto(alert: Alert): AlertHistoryItemDto {
    return {
      id: alert.id,
      pairId: alert.pair.id,
      symbol: alert.pair.symbol,
      spread: alert.spread,
      threshold: alert.threshold,
      spotPrice: alert.spotPrice,
      futurePrice: alert.futurePrice,
      futureExpiry: alert.pair.futureExpiryDate,
      triggeredAt: alert.triggeredAt.toISOString(),
      freshnessMs: alert.freshnessMs,
      dedupeKey: alert.dedupeKey,
      acknowledgedAt: alert.acknowledgedAt?.toISOString() ?? null
    };
  }
}
