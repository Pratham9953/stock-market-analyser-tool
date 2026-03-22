import { Column, Entity, ManyToOne } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { BrokerConnection } from './broker-connection.entity';

@Entity('broker_access_tokens')
export class BrokerAccessToken extends BaseEntityWithAudit {
  @ManyToOne(() => BrokerConnection, (connection) => connection.tokens, { onDelete: 'CASCADE' })
  connection!: BrokerConnection;

  @Column({ type: 'text' })
  cipherText!: string;

  @Column({ type: 'varchar', length: 64 })
  iv!: string;

  @Column({ type: 'varchar', length: 64 })
  authTag!: string;

  @Column({ type: 'text', nullable: true })
  extendedCipherText!: string | null;

  @Column({ type: 'varchar', length: 64, nullable: true })
  extendedIv!: string | null;

  @Column({ type: 'varchar', length: 64, nullable: true })
  extendedAuthTag!: string | null;

  @Column({ type: 'timestamptz' })
  expiresAt!: Date;

  @Column({ type: 'boolean', default: true })
  isActive!: boolean;
}
