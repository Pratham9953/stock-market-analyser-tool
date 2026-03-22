import { Column, Entity, Index, OneToMany } from 'typeorm';
import { BaseEntityWithAudit } from './base.entity';
import { AppSession } from './app-session.entity';
import { BrokerConnection } from './broker-connection.entity';
import { Alert } from './alert.entity';
import { Watchlist } from './watchlist.entity';
import { UserSetting } from './user-setting.entity';
import { OAuthState } from './oauth-state.entity';

@Entity('users')
export class User extends BaseEntityWithAudit {
  @Index({ unique: true })
  @Column({ type: 'varchar', length: 120 })
  deviceId!: string;

  @Column({ type: 'varchar', length: 120, default: 'Trader' })
  displayName!: string;

  @Column({ type: 'varchar', length: 30, default: 'active' })
  status!: 'active' | 'disabled';

  @OneToMany(() => AppSession, (session) => session.user)
  sessions!: AppSession[];

  @OneToMany(() => BrokerConnection, (connection) => connection.user)
  brokerConnections!: BrokerConnection[];

  @OneToMany(() => Alert, (alert) => alert.user)
  alerts!: Alert[];

  @OneToMany(() => Watchlist, (watchlist) => watchlist.user)
  watchlistEntries!: Watchlist[];

  @OneToMany(() => OAuthState, (state) => state.user)
  oauthStates!: OAuthState[];

  @OneToMany(() => UserSetting, (setting) => setting.user)
  settings!: UserSetting[];
}
