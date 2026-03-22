import { Column, Entity, Index } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';

@Entity('system_events')
@Index(['type', 'createdAt'])
export class SystemEvent extends BaseEntityWithAudit {
  @Column({ type: 'varchar', length: 20 })
  level!: 'info' | 'warning' | 'critical';

  @Column({ type: 'varchar', length: 80 })
  type!: string;

  @Column({ type: 'varchar', length: 255 })
  message!: string;

  @Column({ type: 'varchar', length: 80, default: 'system' })
  source!: string;

  @Column({ type: 'jsonb', default: {} })
  payload!: Record<string, unknown>;
}
