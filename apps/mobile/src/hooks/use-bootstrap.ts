import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { getOrCreateDeviceId } from '../lib/device';
import { storage } from '../lib/storage';
import { liveWebsocketClient } from '../lib/ws';
import { useSessionStore } from '../store/session-store';
import { useLiveStore } from '../store/live-store';

export const useBootstrap = () => {
  const router = useRouter();
  const setSession = useSessionStore((state) => state.setSession);
  const ingestEvent = useLiveStore((state) => state.ingestEvent);

  const query = useQuery({
    queryKey: ['bootstrap'],
    queryFn: async () => {
      const deviceId = await getOrCreateDeviceId();
      const payload = await api.bootstrapSession({ deviceId, displayName: 'Local Trader' });
      await storage.setSessionToken(payload.token);
      setSession(payload);
      liveWebsocketClient.connect(payload.token);
      return payload;
    }
  });

  useEffect(() => liveWebsocketClient.subscribe(ingestEvent), [ingestEvent]);

  useEffect(() => {
    if (!query.data) return;
    if (query.data.brokerConnection?.status === 'connected') {
      router.replace('/(tabs)/dashboard');
    } else {
      router.replace('/connect');
    }
  }, [query.data, router]);

  return query;
};
