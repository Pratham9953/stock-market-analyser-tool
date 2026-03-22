import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import protobuf from 'protobufjs';

const root = protobuf.parse(
  readFileSync(join(process.cwd(), 'apps/api/src/infrastructure/providers/upstox/market-data-v3.proto'), 'utf8')
).root;

export const FeedResponseType = root.lookupType(
  'com.upstox.marketdatafeederv3udapi.rpc.proto.FeedResponse'
);
