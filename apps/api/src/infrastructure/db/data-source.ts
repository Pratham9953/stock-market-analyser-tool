import 'reflect-metadata';
import { DataSource } from 'typeorm';
import { env } from '../../config/env';
import { Alert } from './entities/alert.entity';
import { AppSession } from './entities/app-session.entity';
import { BrokerAccessToken } from './entities/broker-access-token.entity';
import { BrokerConnection } from './entities/broker-connection.entity';
import { Instrument } from './entities/instrument.entity';
import { InstrumentPair } from './entities/instrument-pair.entity';
import { OAuthState } from './entities/oauth-state.entity';
import { SystemEvent } from './entities/system-event.entity';
import { UserSetting } from './entities/user-setting.entity';
import { User } from './entities/user.entity';
import { Watchlist } from './entities/watchlist.entity';
import { InitialSchema1710000000000 } from '../../migrations/1710000000000-InitialSchema';

export const buildDataSource = () =>
  new DataSource({
    type: 'postgres',
    url: env.DATABASE_URL,
    synchronize: false,
    logging: false,
    entities: [
      User,
      AppSession,
      BrokerConnection,
      BrokerAccessToken,
      Instrument,
      InstrumentPair,
      Alert,
      Watchlist,
      UserSetting,
      OAuthState,
      SystemEvent
    ],
    migrations: [InitialSchema1710000000000]
  });
