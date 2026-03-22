import React from 'react';
import { Text, View } from 'react-native';
import { Badge, Card, MetricCard, Screen, SectionHeader, Sparkline, useTheme } from '@fo-scanner/ui';
import { useDashboard } from '../../src/hooks/use-dashboard';
import { ResponsiveGrid } from '../../src/components/ResponsiveGrid';
import { useLiveStore } from '../../src/store/live-store';

export default function DashboardScreen() {
  const theme = useTheme();
  const { data, isLoading } = useDashboard();
  const spreads = Object.values(useLiveStore((state) => state.spreads)).map((item) => item.spread);

  return (
    <Screen>
      <SectionHeader title="Dashboard" subtitle="Realtime summary of broker connectivity, live subscriptions, and active backwardation opportunities." />
      {isLoading || !data ? null : (
        <ResponsiveGrid>
          <MetricCard label="Active connection" value={data.activeConnection ? 'Online' : 'Offline'} helper={data.marketDataState} tone={data.activeConnection ? 'success' : 'warning'} />
          <MetricCard label="Subscribed symbols" value={String(data.subscribedInstrumentCount)} helper={`Threshold ${data.threshold}`} />
          <MetricCard label="Active watchlist" value={String(data.activeWatchlistCount)} helper={`WS ${data.websocketState}`} />
          <MetricCard label="Live alerts" value={String(data.liveAlertCount)} helper={`${data.backendLatencyMs}ms backend`} tone={data.liveAlertCount ? 'danger' : 'accent'} />
        </ResponsiveGrid>
      )}
      <Card>
        <Badge label={data?.marketDataState ?? 'loading'} tone={data?.marketDataState === 'connected' ? 'success' : 'warning'} />
        <Text style={{ color: theme.text, fontSize: 18, fontWeight: '700' }}>Spread activity</Text>
        <Sparkline points={spreads.length ? spreads : [0, 0, 0, 0]} width={260} height={64} />
        <Text style={{ color: theme.muted }}>Last tick {data?.lastTickAt ?? '—'}</Text>
      </Card>
      <Card>
        <Text style={{ color: theme.text, fontSize: 18, fontWeight: '700' }}>Realtime behavior</Text>
        <View style={{ gap: 8 }}>
          <Text style={{ color: theme.muted }}>• Broker auth state, websocket fanout, and market-feed state are shown together so reconnect issues are obvious.</Text>
          <Text style={{ color: theme.muted }}>• Live spreads are throttled visually to avoid noisy flashing while critical alerts still push immediately.</Text>
        </View>
      </Card>
    </Screen>
  );
}
