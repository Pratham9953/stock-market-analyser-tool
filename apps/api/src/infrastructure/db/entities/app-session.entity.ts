import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';

@Entity('app_sessions')
export class AppSession extends BaseEntityWithAudit {
  @Index({ unique: true })
  @Column({ type: 'varchar', length: 120 })
  sessionKey!: string;

  @ManyToOne(() => User, (user) => user.sessions, { onDelete: 'CASCADE' })
  user!: User;

  @Column({ type: 'varchar', length: 255, nullable: true })
  userAgent!: string | null;

  @Column({ type: 'varchar', length: 64, nullable: true })
  ipAddress!: string | null;

  @Column({ type: 'timestamptz' })
  expiresAt!: Date;

  @Column({ type: 'boolean', default: true })
  isActive!: boolean;
}
