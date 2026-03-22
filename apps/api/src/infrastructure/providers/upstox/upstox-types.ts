export type UpstoxTokenResponse = {
  email: string;
  exchanges: string[];
  products: string[];
  broker: 'UPSTOX';
  user_id: string;
  user_name: string;
  order_types: string[];
  user_type: string;
  poa: boolean;
  is_active: boolean;
  access_token: string;
  extended_token?: string;
};

export type UpstoxMarketAuthorizeResponse = {
  status: 'success' | 'error';
  data: {
    authorized_redirect_uri: string;
  };
};

export type UpstoxInstrumentRecord = {
  segment: string;
  name?: string;
  exchange: string;
  isin?: string;
  instrument_type: string;
  instrument_key: string;
  lot_size?: number;
  minimum_lot?: number;
  exchange_token?: string;
  tick_size?: number;
  trading_symbol: string;
  short_name?: string;
  security_type?: string;
  expiry?: string;
  underlying_key?: string;
  underlying_type?: string;
  [key: string]: unknown;
};

export type NormalizedTick = {
  instrumentKey: string;
  price: number;
  observedAt: Date;
  requestMode: string;
};
