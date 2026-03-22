import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';
import { InstrumentPair } from './instrument-pair.entity';

@Entity('alerts')
@Index(['user', 'triggeredAt'])
@Index(['dedupeKey'])
export class Alert extends BaseEntityWithAudit {
  @ManyToOne(() => User, (user) => user.alerts, { onDelete: 'CASCADE', eager: true })
  user!: User;

  @ManyToOne(() => InstrumentPair, { eager: true, nullable: false, onDelete: 'CASCADE' })
  pair!: InstrumentPair;

  @Column({ type: 'float' })
  spread!: number;

  @Column({ type: 'float' })
  threshold!: number;

  @Column({ type: 'float' })
  spotPrice!: number;

  @Column({ type: 'float' })
  futurePrice!: number;

  @Column({ type: 'integer' })
  freshnessMs!: number;

  @Column({ type: 'varchar', length: 160 })
  dedupeKey!: string;

  @Column({ type: 'timestamptz' })
  triggeredAt!: Date;

  @Column({ type: 'timestamptz', nullable: true })
  acknowledgedAt!: Date | null;
}
