import React from 'react';
import { RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { EmptyState, Screen, SectionHeader } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';
import { AlertHistoryList } from '../../src/components/AlertHistoryList';
import { useLiveStore } from '../../src/store/live-store';

export default function HistoryScreen() {
  const { data, isFetching, refetch } = useQuery({ queryKey: ['alert-history'], queryFn: () => api.getAlertHistory() });
  const setAlerts = useLiveStore((state) => state.setAlerts);

  React.useEffect(() => {
    if (data) setAlerts(data);
  }, [data, setAlerts]);

  const alerts = useLiveStore((state) => state.alerts);

  return (
    <Screen>
      <SectionHeader title="Alert history" subtitle="Persisted backwardation alerts with acknowledgement support and refresh behavior." />
      {alerts.length ? (
        <AlertHistoryList alerts={alerts} onAcknowledge={(id) => void api.acknowledgeAlert(id).then(() => refetch())} />
      ) : (
        <EmptyState title="No alerts yet" subtitle="Historical alerts will appear here after the first threshold breach is detected." />
      )}
    </Screen>
  );
}
