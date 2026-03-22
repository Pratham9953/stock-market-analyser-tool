import React from 'react';
import { useRouter } from 'expo-router';
import { LoadingState, Screen, SectionHeader } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';
import { useSessionStore } from '../../src/store/session-store';

export default function UpstoxCallbackScreen() {
  const router = useRouter();
  const session = useSessionStore((state) => state.session);
  const setSession = useSessionStore((state) => state.setSession);

  React.useEffect(() => {
    const refresh = async () => {
      if (!session) {
        router.replace('/');
        return;
      }
      const authStatus = await api.getAuthStatus();
      setSession({ ...session, brokerConnection: authStatus.brokerConnection, settings: session.settings, user: session.user, token: session.token });
      router.replace('/(tabs)/dashboard');
    };
    void refresh();
  }, [router, session, setSession]);

  return (
    <Screen>
      <SectionHeader title="Finalizing Upstox link" subtitle="Refreshing broker status and restarting live subscriptions." />
      <LoadingState label="Just a moment…" />
    </Screen>
  );
}
