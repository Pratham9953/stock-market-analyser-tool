import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';

@Entity('user_settings')
@Index(['user'], { unique: true })
export class UserSetting extends BaseEntityWithAudit {
  @ManyToOne(() => User, (user) => user.settings, { onDelete: 'CASCADE' })
  user!: User;

  @Column({ type: 'float', default: 10 })
  threshold!: number;

  @Column({ type: 'integer', default: 30000 })
  cooldownMs!: number;

  @Column({ type: 'integer', default: 10000 })
  freshnessMs!: number;

  @Column({ type: 'varchar', length: 20, default: 'NSE' })
  preferredExchange!: string;

  @Column({ type: 'boolean', default: true })
  darkMode!: boolean;

  @Column({ type: 'jsonb', default: ['NSE'] })
  exchanges!: string[];

  @Column({ type: 'jsonb', default: ['NSE_EQ', 'NSE_FO'] })
  segments!: string[];
}
