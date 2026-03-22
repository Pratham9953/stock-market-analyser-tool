import { randomUUID } from 'node:crypto';
import { DataSource } from 'typeorm';
import { env } from '../../config/env';
import { AppError } from '../../common/errors';
import { logger } from '../../common/logger';
import { decryptSecret, encryptSecret } from '../../infrastructure/security/crypto';
import { UpstoxApiClient } from '../../infrastructure/providers/upstox/upstox-api-client';
import { OAuthState } from '../../infrastructure/db/entities/oauth-state.entity';
import { BrokerConnection } from '../../infrastructure/db/entities/broker-connection.entity';
import { BrokerAccessToken } from '../../infrastructure/db/entities/broker-access-token.entity';
import { User } from '../../infrastructure/db/entities/user.entity';
import type { AuthStatusResponseDto, BrokerConnectionDto } from '@fo-scanner/shared';

const nextTokenExpiry = (): Date => {
  const now = new Date();
  const expiry = new Date(now);
  expiry.setHours(3, 30, 0, 0);
  if (expiry.getTime() <= now.getTime()) {
    expiry.setDate(expiry.getDate() + 1);
  }
  return expiry;
};

export class UpstoxOAuthService {
  constructor(private readonly dataSource: DataSource, private readonly apiClient: UpstoxApiClient) {}

  async buildConnectUrl(user: User, frontendRedirectUri: string): Promise<string> {
    const stateRepo = this.dataSource.getRepository(OAuthState);
    const state = randomUUID();
    await stateRepo.save(
      stateRepo.create({
        state,
        user,
        broker: 'UPSTOX',
        frontendRedirectUri,
        expiresAt: new Date(Date.now() + 10 * 60 * 1000),
        consumedAt: null
      })
    );

    const params = new URLSearchParams({
      response_type: 'code',
      client_id: env.UPSTOX_CLIENT_ID,
      redirect_uri: env.UPSTOX_REDIRECT_URI,
      state
    });

    return `${env.UPSTOX_AUTH_DIALOG_URL}?${params.toString()}`;
  }

  async handleCallback(code: string | undefined, stateValue: string | undefined): Promise<string> {
    if (!code || !stateValue) {
      throw new AppError('Missing code or state in callback', 400, 'UPSTOX_CALLBACK_INVALID');
    }

    const stateRepo = this.dataSource.getRepository(OAuthState);
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);
    const tokenRepo = this.dataSource.getRepository(BrokerAccessToken);

    const state = await stateRepo.findOne({ where: { state: stateValue }, relations: { user: true } });
    if (!state) {
      throw new AppError('OAuth state not found', 400, 'OAUTH_STATE_NOT_FOUND');
    }
    if (state.consumedAt || state.expiresAt.getTime() < Date.now()) {
      throw new AppError('OAuth state expired', 400, 'OAUTH_STATE_EXPIRED');
    }

    state.consumedAt = new Date();
    await stateRepo.save(state);

    const tokenResponse = await this.apiClient.exchangeAuthCode(code);
    const access = encryptSecret(tokenResponse.access_token);
    const extended = tokenResponse.extended_token ? encryptSecret(tokenResponse.extended_token) : null;

    let connection = await connectionRepo.findOne({
      where: { user: { id: state.user.id }, broker: 'UPSTOX' },
      relations: { user: true }
    });

    if (!connection) {
      connection = connectionRepo.create({
        user: state.user,
        broker: 'UPSTOX',
        status: 'connected'
      });
    }

    connection.status = 'connected';
    connection.brokerUserId = tokenResponse.user_id;
    connection.accountName = tokenResponse.user_name;
    connection.connectedAt = new Date();
    connection.lastAuthorizedAt = new Date();
    connection.tokenExpiresAt = nextTokenExpiry();
    connection.lastHeartbeatAt = new Date();
    connection = await connectionRepo.save(connection);

    await tokenRepo.update({ connection: { id: connection.id }, isActive: true }, { isActive: false });
    await tokenRepo.save(
      tokenRepo.create({
        connection,
        cipherText: access.cipherText,
        iv: access.iv,
        authTag: access.authTag,
        extendedCipherText: extended?.cipherText ?? null,
        extendedIv: extended?.iv ?? null,
        extendedAuthTag: extended?.authTag ?? null,
        expiresAt: connection.tokenExpiresAt,
        isActive: true
      })
    );

    logger.info({ userId: state.user.id, brokerUserId: tokenResponse.user_id }, 'Upstox connection linked');

    const url = new URL(state.frontendRedirectUri);
    url.searchParams.set('status', 'success');
    return url.toString();
  }

  async getAccessTokenForConnection(connectionId: string): Promise<string> {
    const tokenRepo = this.dataSource.getRepository(BrokerAccessToken);
    const token = await tokenRepo.findOne({
      where: { connection: { id: connectionId }, isActive: true },
      relations: { connection: true },
      order: { createdAt: 'DESC' }
    });

    if (!token) {
      throw new AppError('No active Upstox token found', 401, 'UPSTOX_TOKEN_MISSING');
    }

    if (token.expiresAt.getTime() <= Date.now()) {
      throw new AppError('Upstox token expired', 401, 'UPSTOX_TOKEN_EXPIRED');
    }

    return decryptSecret({
      cipherText: token.cipherText,
      iv: token.iv,
      authTag: token.authTag
    });
  }

  async getAuthStatus(userId: string): Promise<AuthStatusResponseDto> {
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);
    const connection = await connectionRepo.findOne({ where: { user: { id: userId }, broker: 'UPSTOX' } });
    const dto = connection ? this.toDto(connection) : null;
    return {
      sessionActive: true,
      brokerConnection: dto,
      reauthRequired: !connection || !connection.tokenExpiresAt || connection.tokenExpiresAt.getTime() <= Date.now(),
      connectUrl: null
    };
  }

  async disconnect(userId: string): Promise<void> {
    const connectionRepo = this.dataSource.getRepository(BrokerConnection);
    const tokenRepo = this.dataSource.getRepository(BrokerAccessToken);
    const connection = await connectionRepo.findOne({ where: { user: { id: userId }, broker: 'UPSTOX' }, relations: { user: true } });
    if (!connection) return;
    connection.status = 'idle';
    connection.tokenExpiresAt = null;
    await connectionRepo.save(connection);
    await tokenRepo.update({ connection: { id: connection.id }, isActive: true }, { isActive: false });
  }

  toDto(connection: BrokerConnection): BrokerConnectionDto {
    return {
      id: connection.id,
      broker: connection.broker,
      status: connection.status,
      brokerUserId: connection.brokerUserId,
      accountName: connection.accountName,
      tokenExpiresAt: connection.tokenExpiresAt?.toISOString() ?? null,
      connectedAt: connection.connectedAt?.toISOString() ?? null,
      lastHeartbeatAt: connection.lastHeartbeatAt?.toISOString() ?? null
    };
  }
}
