import React from 'react';
import { EmptyState, Screen, SectionHeader } from '@fo-scanner/ui';
import { LiveSpreadList } from '../../src/components/LiveSpreadList';
import { useLiveStore } from '../../src/store/live-store';

export default function ScannerScreen() {
  const spreads = Object.values(useLiveStore((state) => state.spreads));
  return (
    <Screen>
      <SectionHeader title="Live scanner" subtitle="Streaming spot-vs-near-future spreads from the backend websocket." />
      {spreads.length ? <LiveSpreadList /> : <EmptyState title="No live spreads yet" subtitle="Connect Upstox and add watchlist symbols to start receiving realtime spreads." />}
    </Screen>
  );
}
