import React from 'react';
import { Text, View } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import { useRouter } from 'expo-router';
import { Badge, Card, PrimaryButton, Screen, SectionHeader, useTheme } from '@fo-scanner/ui';
import { api } from '../src/lib/api';
import { mobileEnv } from '../src/lib/env';
import { useSessionStore } from '../src/store/session-store';

export default function ConnectScreen() {
  const router = useRouter();
  const theme = useTheme();
  const session = useSessionStore((state) => state.session);
  const [loading, setLoading] = React.useState(false);

  const handleConnect = async () => {
    try {
      setLoading(true);
      const { url } = await api.getConnectUrl(mobileEnv.EXPO_PUBLIC_UPSTOX_CALLBACK_URL);
      const result = await WebBrowser.openAuthSessionAsync(url, mobileEnv.EXPO_PUBLIC_UPSTOX_CALLBACK_URL);
      if (result.type === 'success') {
        router.replace('/auth/upstox-callback');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <SectionHeader title="Connect Upstox" subtitle="Use hosted Upstox OAuth, exchange the auth code on the backend, and start V3 market-feed streaming." />
      <Card>
        <Badge label={session?.brokerConnection?.status ?? 'idle'} tone={session?.brokerConnection?.status === 'connected' ? 'success' : 'warning'} />
        <Text style={{ color: theme.text, fontSize: 18, fontWeight: '700' }}>Broker connection required</Text>
        <Text style={{ color: theme.muted, lineHeight: 22 }}>
          The scanner only subscribes after a valid Upstox account is linked. OAuth state and token storage are handled by the backend.
        </Text>
        <PrimaryButton title={loading ? 'Opening Upstox…' : 'Connect Upstox'} onPress={() => void handleConnect()} disabled={loading} />
      </Card>
      <View style={{ gap: 8 }}>
        <PrimaryButton title="Continue in offline shell" onPress={() => router.replace('/(tabs)/dashboard')} />
      </View>
    </Screen>
  );
}
