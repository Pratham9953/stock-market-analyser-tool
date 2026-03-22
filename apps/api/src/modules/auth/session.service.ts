import { randomUUID } from 'node:crypto';
import { DataSource } from 'typeorm';
import { env } from '../../config/env';
import { User } from '../../infrastructure/db/entities/user.entity';
import { AppSession } from '../../infrastructure/db/entities/app-session.entity';
import { UserSetting } from '../../infrastructure/db/entities/user-setting.entity';
import { BrokerConnection } from '../../infrastructure/db/entities/broker-connection.entity';
import { AppError } from '../../common/errors';
import type { SessionBootstrapResponse } from '@fo-scanner/shared';

export type AuthContext = {
  user: User;
  session: AppSession;
};

export class SessionService {
  constructor(
    private readonly dataSource: DataSource,
    private readonly signToken: (payload: Record<string, string>) => string | Promise<string>
  ) {}

  async bootstrap(
    input: { deviceId: string; displayName?: string },
    meta: { userAgent?: string; ipAddress?: string }
  ): Promise<SessionBootstrapResponse> {
    const userRepo = this.dataSource.getRepository(User);
    const settingsRepo = this.dataSource.getRepository(UserSetting);
    const sessionRepo = this.dataSource.getRepository(AppSession);
    const brokerRepo = this.dataSource.getRepository(BrokerConnection);

    const normalizedDeviceId = input.deviceId.trim();
    let user = await userRepo.findOne({ where: { deviceId: normalizedDeviceId } });

    if (!user) {
      user = await userRepo.save(
        userRepo.create({
          deviceId: normalizedDeviceId,
          displayName: input.displayName?.trim() || 'Trader',
          status: 'active'
        })
      );
    } else if (input.displayName?.trim() && input.displayName.trim() !== user.displayName) {
      user.displayName = input.displayName.trim();
      user = await userRepo.save(user);
    }

    let settings = await settingsRepo.findOne({ where: { user: { id: user.id } }, relations: { user: true } });
    if (!settings) {
      settings = await settingsRepo.save(
        settingsRepo.create({
          user,
          threshold: env.DEFAULT_ALERT_THRESHOLD,
          cooldownMs: env.DEFAULT_ALERT_COOLDOWN_MS,
          freshnessMs: env.DEFAULT_TICK_FRESHNESS_MS,
          preferredExchange: 'NSE',
          darkMode: true,
          exchanges: ['NSE'],
          segments: ['NSE_EQ', 'NSE_FO']
        })
      );
    }

    const session = await sessionRepo.save(
      sessionRepo.create({
        user,
        sessionKey: randomUUID(),
        userAgent: meta.userAgent ?? null,
        ipAddress: meta.ipAddress ?? null,
        expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
        isActive: true
      })
    );

    const token = await this.signToken({ sub: user.id, sid: session.sessionKey });
    const brokerConnection = await brokerRepo.findOne({ where: { user: { id: user.id }, broker: 'UPSTOX' } });

    return {
      token,
      user: {
        id: user.id,
        deviceId: user.deviceId,
        displayName: user.displayName,
        createdAt: user.createdAt.toISOString()
      },
      brokerConnection: brokerConnection
        ? {
            id: brokerConnection.id,
            broker: brokerConnection.broker,
            status: brokerConnection.status,
            brokerUserId: brokerConnection.brokerUserId,
            accountName: brokerConnection.accountName,
            tokenExpiresAt: brokerConnection.tokenExpiresAt?.toISOString() ?? null,
            connectedAt: brokerConnection.connectedAt?.toISOString() ?? null,
            lastHeartbeatAt: brokerConnection.lastHeartbeatAt?.toISOString() ?? null
          }
        : null,
      settings: {
        threshold: settings.threshold,
        cooldownMs: settings.cooldownMs,
        freshnessMs: settings.freshnessMs,
        preferredExchange: settings.preferredExchange,
        darkMode: settings.darkMode
      }
    };
  }

  async authenticate(payload: { sub?: string; sid?: string }): Promise<AuthContext> {
    if (!payload.sub || !payload.sid) {
      throw new AppError('Invalid session token', 401, 'INVALID_SESSION');
    }

    const sessionRepo = this.dataSource.getRepository(AppSession);
    const session = await sessionRepo.findOne({
      where: { sessionKey: payload.sid, isActive: true },
      relations: { user: true }
    });

    if (!session || session.expiresAt.getTime() < Date.now()) {
      throw new AppError('Session expired', 401, 'SESSION_EXPIRED');
    }

    if (session.user.id !== payload.sub || session.user.status !== 'active') {
      throw new AppError('Session not valid for user', 401, 'SESSION_INVALID_USER');
    }

    return { user: session.user, session };
  }
}
