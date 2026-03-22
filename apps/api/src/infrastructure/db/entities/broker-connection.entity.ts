import { Column, Entity, Index, ManyToOne, OneToMany } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { User } from './user.entity';
import { BrokerAccessToken } from './broker-access-token.entity';

@Entity('broker_connections')
export class BrokerConnection extends BaseEntityWithAudit {
  @ManyToOne(() => User, (user) => user.brokerConnections, { onDelete: 'CASCADE' })
  user!: User;

  @Index()
  @Column({ type: 'varchar', length: 20, default: 'UPSTOX' })
  broker!: 'UPSTOX';

  @Column({ type: 'varchar', length: 40, default: 'idle' })
  status!: 'idle' | 'connecting' | 'connected' | 'expired' | 'error';

  @Index()
  @Column({ type: 'varchar', length: 120, nullable: true })
  brokerUserId!: string | null;

  @Column({ type: 'varchar', length: 120, nullable: true })
  accountName!: string | null;

  @Column({ type: 'timestamptz', nullable: true })
  connectedAt!: Date | null;

  @Column({ type: 'timestamptz', nullable: true })
  tokenExpiresAt!: Date | null;

  @Column({ type: 'timestamptz', nullable: true })
  lastHeartbeatAt!: Date | null;

  @Column({ type: 'timestamptz', nullable: true })
  lastAuthorizedAt!: Date | null;

  @OneToMany(() => BrokerAccessToken, (token) => token.connection)
  tokens!: BrokerAccessToken[];
}
