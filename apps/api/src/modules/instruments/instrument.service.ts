import { DataSource, In } from 'typeorm';
import { Instrument } from '../../infrastructure/db/entities/instrument.entity';
import { UpstoxApiClient } from '../../infrastructure/providers/upstox/upstox-api-client';
import type { InstrumentSummary } from '@fo-scanner/shared';
import { logger } from '../../common/logger';

const parseExpiry = (value: unknown): string | null => {
  if (typeof value !== 'string' || !value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString().slice(0, 10);
};

export class InstrumentService {
  constructor(private readonly dataSource: DataSource, private readonly upstox: UpstoxApiClient) {}

  async syncBodInstruments(): Promise<number> {
    const repo = this.dataSource.getRepository(Instrument);
    const rows = await this.upstox.downloadBodInstruments();
    const entities = rows.map((row) =>
      repo.create({
        instrumentKey: row.instrument_key,
        exchange: row.exchange,
        segment: row.segment,
        instrumentType: row.instrument_type,
        tradingSymbol: row.trading_symbol,
        shortName: typeof row.short_name === 'string' ? row.short_name : null,
        name: typeof row.name === 'string' ? row.name : null,
        underlyingKey: typeof row.underlying_key === 'string' ? row.underlying_key : null,
        underlyingType: typeof row.underlying_type === 'string' ? row.underlying_type : null,
        expiryDate: parseExpiry(row.expiry),
        lotSize: typeof row.lot_size === 'number' ? row.lot_size : null,
        minimumLot: typeof row.minimum_lot === 'number' ? row.minimum_lot : null,
        tickSize: typeof row.tick_size === 'number' ? row.tick_size : null,
        isin: typeof row.isin === 'string' ? row.isin : null,
        isTradable: true,
        metadata: row
      })
    );

    const chunkSize = 1000;
    for (let offset = 0; offset < entities.length; offset += chunkSize) {
      const chunk = entities.slice(offset, offset + chunkSize);
      await repo
        .createQueryBuilder()
        .insert()
        .into(Instrument)
        .values(chunk)
        .orUpdate(
          [
            'exchange',
            'segment',
            'instrumentType',
            'tradingSymbol',
            'shortName',
            'name',
            'underlyingKey',
            'underlyingType',
            'expiryDate',
            'lotSize',
            'minimumLot',
            'tickSize',
            'isin',
            'metadata',
            'updatedAt'
          ],
          ['instrumentKey']
        )
        .execute();
    }

    logger.info({ count: entities.length }, 'Instrument catalog synced');
    return entities.length;
  }

  async search(query: string, limit = 20): Promise<InstrumentSummary[]> {
    const repo = this.dataSource.getRepository(Instrument);
    const rows = await repo
      .createQueryBuilder('instrument')
      .where('instrument.tradingSymbol ILIKE :query OR instrument.shortName ILIKE :query OR instrument.name ILIKE :query', {
        query: `%${query.trim()}%`
      })
      .orderBy('instrument.expiryDate', 'ASC', 'NULLS LAST')
      .limit(limit)
      .getMany();

    return rows.map((row) => this.toSummary(row));
  }

  async getByKeys(instrumentKeys: string[]): Promise<Instrument[]> {
    const repo = this.dataSource.getRepository(Instrument);
    return repo.find({ where: { instrumentKey: In(instrumentKeys) } });
  }

  toSummary(instrument: Instrument): InstrumentSummary {
    return {
      id: instrument.id,
      instrumentKey: instrument.instrumentKey,
      exchange: instrument.exchange,
      segment: instrument.segment,
      instrumentType: instrument.instrumentType,
      tradingSymbol: instrument.tradingSymbol,
      shortName: instrument.shortName,
      underlyingKey: instrument.underlyingKey,
      expiryDate: instrument.expiryDate,
      lotSize: instrument.lotSize
    };
  }
}
