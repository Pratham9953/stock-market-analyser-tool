import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { Instrument } from './instrument.entity';

@Entity('instrument_pairs')
@Index(['userId', 'symbol'], { unique: true })
export class InstrumentPair extends BaseEntityWithAudit {
  @Column({ type: 'uuid' })
  userId!: string;

  @Column({ type: 'varchar', length: 60 })
  symbol!: string;

  @ManyToOne(() => Instrument, (instrument) => instrument.spotPairs, { eager: true, nullable: true })
  spotInstrument!: Instrument | null;

  @ManyToOne(() => Instrument, (instrument) => instrument.futurePairs, { eager: true, nullable: true })
  futureInstrument!: Instrument | null;

  @Column({ type: 'varchar', length: 20, default: 'near' })
  monthType!: 'near' | 'next' | 'far';

  @Column({ type: 'date', nullable: true })
  futureExpiryDate!: string | null;

  @Column({ type: 'varchar', length: 30, default: 'paired' })
  status!: 'paired' | 'missing_spot' | 'missing_future';

  @Column({ type: 'boolean', default: true })
  enabled!: boolean;
}
