import { Column, Entity, Index, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';

@Entity('oauth_states')
export class OAuthState extends BaseEntityWithAudit {
  @Index({ unique: true })
  @Column({ type: 'varchar', length: 120 })
  state!: string;

  @ManyToOne(() => User, (user) => user.oauthStates, { onDelete: 'CASCADE' })
  user!: User;

  @Column({ type: 'varchar', length: 20, default: 'UPSTOX' })
  broker!: 'UPSTOX';

  @Column({ type: 'varchar', length: 255 })
  frontendRedirectUri!: string;

  @Column({ type: 'timestamptz' })
  expiresAt!: Date;

  @Column({ type: 'timestamptz', nullable: true })
  consumedAt!: Date | null;
}
