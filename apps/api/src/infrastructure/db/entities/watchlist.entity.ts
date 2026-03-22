import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';

@Entity('watchlists')
@Index(['user', 'symbol'], { unique: true })
export class Watchlist extends BaseEntityWithAudit {
  @ManyToOne(() => User, (user) => user.watchlistEntries, { onDelete: 'CASCADE' })
  user!: User;

  @Column({ type: 'varchar', length: 60 })
  symbol!: string;

  @Column({ type: 'varchar', length: 20, default: 'NSE' })
  exchange!: string;

  @Column({ type: 'varchar', length: 20, default: 'NSE_FO' })
  segment!: string;

  @Column({ type: 'integer', default: 0 })
  preferredMonthOffset!: number;

  @Column({ type: 'boolean', default: true })
  enabled!: boolean;
}
