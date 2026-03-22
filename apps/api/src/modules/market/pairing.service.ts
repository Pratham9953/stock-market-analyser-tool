import { DataSource, Repository } from 'typeorm';
import { Instrument } from '../../infrastructure/db/entities/instrument.entity';
import { InstrumentPair } from '../../infrastructure/db/entities/instrument-pair.entity';
import { Watchlist } from '../../infrastructure/db/entities/watchlist.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import { InstrumentService } from '../instruments/instrument.service';
import type { WatchlistItemDto } from '@fo-scanner/shared';

const FUTURE_TYPES = ['FUT', 'FUTIDX', 'FUTSTK'];

const normalizeSymbol = (symbol: string): string => symbol.trim().toUpperCase();

export class PairingService {
  constructor(private readonly dataSource: DataSource, private readonly instrumentService: InstrumentService) {}

  async refreshForUser(user: User): Promise<void> {
    const watchlistRepo = this.dataSource.getRepository(Watchlist);
    const pairRepo = this.dataSource.getRepository(InstrumentPair);
    const instrumentRepo = this.dataSource.getRepository(Instrument);
    const watchlist = await watchlistRepo.find({ where: { user: { id: user.id } }, relations: { user: true } });

    for (const item of watchlist) {
      const spotInstrument = await this.findSpotInstrument(instrumentRepo, item.symbol, item.exchange);
      const futureInstrument = spotInstrument
        ? await this.findFutureInstrument(instrumentRepo, spotInstrument, item.preferredMonthOffset)
        : null;

      const status = spotInstrument ? (futureInstrument ? 'paired' : 'missing_future') : 'missing_spot';
      const existing = await pairRepo.findOne({ where: { userId: user.id, symbol: normalizeSymbol(item.symbol) } });
      const record = existing ?? pairRepo.create({ userId: user.id, symbol: normalizeSymbol(item.symbol) });
      record.spotInstrument = spotInstrument;
      record.futureInstrument = futureInstrument;
      record.status = status;
      record.futureExpiryDate = futureInstrument?.expiryDate ?? null;
      record.monthType = item.preferredMonthOffset === 0 ? 'near' : item.preferredMonthOffset === 1 ? 'next' : 'far';
      record.enabled = item.enabled;
      await pairRepo.save(record);
    }
  }

  async listForUser(user: User): Promise<WatchlistItemDto[]> {
    const watchlistRepo = this.dataSource.getRepository(Watchlist);
    const pairRepo = this.dataSource.getRepository(InstrumentPair);
    const watchlistItems = await watchlistRepo.find({ where: { user: { id: user.id } }, relations: { user: true } });

    const result: WatchlistItemDto[] = [];
    for (const watchItem of watchlistItems) {
      const pair = await pairRepo.findOne({
        where: { userId: user.id, symbol: normalizeSymbol(watchItem.symbol) },
        relations: { spotInstrument: true, futureInstrument: true }
      });
      result.push({
        id: watchItem.id,
        symbol: normalizeSymbol(watchItem.symbol),
        exchange: watchItem.exchange,
        segment: watchItem.segment,
        enabled: watchItem.enabled,
        preferredMonthOffset: watchItem.preferredMonthOffset,
        spotInstrument: pair?.spotInstrument ? this.instrumentService.toSummary(pair.spotInstrument) : null,
        futureInstrument: pair?.futureInstrument ? this.instrumentService.toSummary(pair.futureInstrument) : null,
        updatedAt: watchItem.updatedAt.toISOString()
      });
    }

    return result;
  }

  async getPairsForUser(userId: string): Promise<InstrumentPair[]> {
    const pairRepo = this.dataSource.getRepository(InstrumentPair);
    return pairRepo.find({
      where: { userId, enabled: true, status: 'paired' },
      relations: { spotInstrument: true, futureInstrument: true }
    });
  }

  private async findSpotInstrument(
    instrumentRepo: Repository<Instrument>,
    symbol: string,
    exchange: string
  ): Promise<Instrument | null> {
    const normalized = normalizeSymbol(symbol);
    return instrumentRepo
      .createQueryBuilder('instrument')
      .where('instrument.exchange = :exchange', { exchange })
      .andWhere("instrument.segment IN ('NSE_EQ','BSE_EQ','NSE_INDEX','BSE_INDEX')")
      .andWhere("instrument.instrumentType IN ('EQ','INDEX')")
      .andWhere('(UPPER(instrument.tradingSymbol) = :symbol OR UPPER(COALESCE(instrument.shortName, instrument.name, instrument.tradingSymbol)) = :symbol)', {
        symbol: normalized
      })
      .orderBy("CASE WHEN instrument.instrumentType = 'EQ' THEN 0 ELSE 1 END", 'ASC')
      .addOrderBy('instrument.tradingSymbol', 'ASC')
      .getOne();
  }

  private async findFutureInstrument(
    instrumentRepo: Repository<Instrument>,
    spotInstrument: Instrument,
    monthOffset: number
  ): Promise<Instrument | null> {
    const futureRows = await instrumentRepo
      .createQueryBuilder('instrument')
      .where('instrument.underlyingKey = :underlyingKey', { underlyingKey: spotInstrument.instrumentKey })
      .andWhere('instrument.segment IN (:...segments)', { segments: ['NSE_FO', 'BSE_FO'] })
      .andWhere('instrument.instrumentType IN (:...types)', { types: FUTURE_TYPES })
      .andWhere('instrument.expiryDate >= CURRENT_DATE')
      .orderBy('instrument.expiryDate', 'ASC')
      .getMany();

    return futureRows[monthOffset] ?? null;
  }
}
