import zlib from 'node:zlib';
import { promisify } from 'node:util';
import { URLSearchParams } from 'node:url';
import { AppError } from '../../../common/errors';
import { RateLimitedHttpClient } from '../../http/rate-limited-http-client';
import { env } from '../../../config/env';
import type {
  UpstoxInstrumentRecord,
  UpstoxMarketAuthorizeResponse,
  UpstoxTokenResponse
} from './upstox-types';

const gunzip = promisify(zlib.gunzip);

export class UpstoxApiClient {
  private readonly http = new RateLimitedHttpClient();

  async exchangeAuthCode(code: string): Promise<UpstoxTokenResponse> {
    const data = new URLSearchParams({
      code,
      client_id: env.UPSTOX_CLIENT_ID,
      client_secret: env.UPSTOX_CLIENT_SECRET,
      redirect_uri: env.UPSTOX_REDIRECT_URI,
      grant_type: 'authorization_code'
    });

    const response = await this.http.request(() =>
      this.http.axios.post<UpstoxTokenResponse>(env.UPSTOX_TOKEN_URL, data, {
        headers: {
          accept: 'application/json',
          'content-type': 'application/x-www-form-urlencoded'
        }
      })
    );

    return response.data;
  }

  async getMarketFeedAuthorizeUrl(accessToken: string): Promise<string> {
    const response = await this.http.request(() =>
      this.http.axios.get<UpstoxMarketAuthorizeResponse>(env.UPSTOX_MARKET_AUTHORIZE_V3_URL, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          accept: 'application/json'
        }
      })
    );

    if (response.data.status !== 'success') {
      throw new AppError('Failed to authorize Upstox market feed', 502, 'UPSTOX_MARKET_FEED_AUTH_FAILED');
    }

    return response.data.data.authorized_redirect_uri;
  }

  async downloadBodInstruments(): Promise<UpstoxInstrumentRecord[]> {
    const response = await this.http.request(() =>
      this.http.axios.get<ArrayBuffer>(env.UPSTOX_BOD_INSTRUMENTS_URL, {
        responseType: 'arraybuffer',
        headers: { accept: 'application/json' }
      })
    );

    const raw = Buffer.from(response.data);
    const decoded = env.UPSTOX_BOD_INSTRUMENTS_URL.endsWith('.gz') ? await gunzip(raw) : raw;
    const parsed = JSON.parse(decoded.toString('utf8')) as UpstoxInstrumentRecord[];

    if (!Array.isArray(parsed)) {
      throw new AppError('Unexpected instrument file payload', 502, 'UPSTOX_INSTRUMENT_FILE_INVALID');
    }

    return parsed;
  }
}
