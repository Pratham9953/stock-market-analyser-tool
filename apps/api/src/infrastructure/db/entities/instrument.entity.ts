import { Column, Entity, Index, OneToMany } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { InstrumentPair } from './instrument-pair.entity';

@Entity('instruments')
@Index(['instrumentKey'], { unique: true })
@Index(['underlyingKey'])
@Index(['tradingSymbol'])
@Index(['segment', 'instrumentType'])
export class Instrument extends BaseEntityWithAudit {
  @Column({ type: 'varchar', length: 120 })
  instrumentKey!: string;

  @Column({ type: 'varchar', length: 20 })
  exchange!: string;

  @Column({ type: 'varchar', length: 20 })
  segment!: string;

  @Column({ type: 'varchar', length: 40 })
  instrumentType!: string;

  @Column({ type: 'varchar', length: 120 })
  tradingSymbol!: string;

  @Column({ type: 'varchar', length: 120, nullable: true })
  shortName!: string | null;

  @Column({ type: 'varchar', length: 120, nullable: true })
  name!: string | null;

  @Column({ type: 'varchar', length: 120, nullable: true })
  underlyingKey!: string | null;

  @Column({ type: 'varchar', length: 20, nullable: true })
  underlyingType!: string | null;

  @Column({ type: 'date', nullable: true })
  expiryDate!: string | null;

  @Column({ type: 'float', nullable: true })
  lotSize!: number | null;

  @Column({ type: 'float', nullable: true })
  minimumLot!: number | null;

  @Column({ type: 'float', nullable: true })
  tickSize!: number | null;

  @Column({ type: 'varchar', length: 60, nullable: true })
  isin!: string | null;

  @Column({ type: 'boolean', default: true })
  isTradable!: boolean;

  @Column({ type: 'jsonb', default: {} })
  metadata!: Record<string, unknown>;

  @OneToMany(() => InstrumentPair, (pair) => pair.spotInstrument)
  spotPairs!: InstrumentPair[];

  @OneToMany(() => InstrumentPair, (pair) => pair.futureInstrument)
  futurePairs!: InstrumentPair[];
}
