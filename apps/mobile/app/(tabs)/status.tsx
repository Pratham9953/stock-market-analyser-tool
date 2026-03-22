import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Badge, Card, DataRow, EmptyState, Screen, SectionHeader } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';

export default function StatusScreen() {
  const { data } = useQuery({ queryKey: ['system-status'], queryFn: () => api.getSystemStatus(), refetchInterval: 5000 });
  if (!data) {
    return (
      <Screen>
        <SectionHeader title="System status" subtitle="Backend, database, websocket, broker auth, and market-feed diagnostics." />
        <EmptyState title="Waiting for status" subtitle="Status will load once the authenticated API session is ready." />
      </Screen>
    );
  }

  return (
    <Screen>
      <SectionHeader title="System status" subtitle="Backend, database, websocket, broker auth, and market-feed diagnostics." />
      <Card>
        <Badge label={data.backend} tone={data.backend === 'ok' ? 'success' : 'warning'} />
        <DataRow label="Database" value={data.database} />
        <DataRow label="Broker auth" value={data.brokerAuth} />
        <DataRow label="Websocket" value={data.websocket} />
        <DataRow label="Market feed" value={data.marketFeed} />
        <DataRow label="Instrument sync" value={data.instrumentSyncAt ?? '—'} />
      </Card>
      {data.recentEvents.map((event) => (
        <Card key={event.id}>
          <Badge label={event.level} tone={event.level === 'critical' ? 'danger' : event.level === 'warning' ? 'warning' : 'accent'} />
          <DataRow label={event.type} value={event.createdAt} />
          <DataRow label="Message" value={event.message} />
        </Card>
      ))}
    </Screen>
  );
}
