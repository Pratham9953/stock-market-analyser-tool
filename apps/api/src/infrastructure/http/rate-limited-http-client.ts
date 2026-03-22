import axios, { AxiosInstance } from 'axios';
import axiosRetry from 'axios-retry';
import Bottleneck from 'bottleneck';
import { logger } from '../../common/logger';

export class RateLimitedHttpClient {
  private readonly client: AxiosInstance;
  private readonly limiter: Bottleneck;

  constructor(baseURL?: string) {
    this.client = axios.create({ baseURL, timeout: 15_000 });
    axiosRetry(this.client, {
      retries: 3,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => axiosRetry.isNetworkOrIdempotentRequestError(error) || error.response?.status === 429
    });
    this.limiter = new Bottleneck({
      maxConcurrent: 5,
      minTime: 25,
      reservoir: 500,
      reservoirRefreshAmount: 500,
      reservoirRefreshInterval: 60_000
    });
  }

  async request<T>(factory: () => Promise<T>): Promise<T> {
    return this.limiter.schedule(factory).catch((error) => {
      logger.warn({ err: error }, 'Rate-limited HTTP request failed');
      throw error;
    });
  }

  get axios(): AxiosInstance {
    return this.client;
  }
}
