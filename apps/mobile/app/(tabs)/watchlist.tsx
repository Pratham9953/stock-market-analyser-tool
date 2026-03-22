import React from 'react';
import { Pressable, Text, TextInput, View } from 'react-native';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Badge, Card, EmptyState, PrimaryButton, Screen, SectionHeader, useTheme } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';

export default function WatchlistScreen() {
  const theme = useTheme();
  const queryClient = useQueryClient();
  const [symbol, setSymbol] = React.useState('RELIANCE');
  const { data } = useQuery({ queryKey: ['watchlist'], queryFn: () => api.getWatchlist() });
  const mutation = useMutation({
    mutationFn: () => api.upsertWatchlist({ symbol, exchange: 'NSE', segment: 'NSE_FO', preferredMonthOffset: 0, enabled: true }),
    onSuccess: () => {
      setSymbol('');
      void queryClient.invalidateQueries({ queryKey: ['watchlist'] });
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
    }
  });

  return (
    <Screen>
      <SectionHeader title="Watchlist" subtitle="Manage underlying symbols that should be paired with spot and near-month futures contracts." />
      <Card>
        <TextInput value={symbol} onChangeText={setSymbol} placeholder="Enter symbol e.g. TCS" placeholderTextColor={theme.muted} style={{ borderColor: theme.border, borderWidth: 1, borderRadius: 14, padding: 14, color: theme.text }} />
        <PrimaryButton title={mutation.isPending ? 'Saving…' : 'Add symbol'} onPress={() => mutation.mutate()} disabled={!symbol.trim() || mutation.isPending} />
      </Card>
      {data?.length ? (
        <View style={{ gap: 12 }}>
          {data.map((item) => (
            <Card key={item.id}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text style={{ color: theme.text, fontWeight: '700', fontSize: 16 }}>{item.symbol}</Text>
                <Badge label={item.enabled ? 'enabled' : 'disabled'} tone={item.enabled ? 'success' : 'warning'} />
              </View>
              <Text style={{ color: theme.muted }}>Spot: {item.spotInstrument?.instrumentKey ?? 'unpaired'}</Text>
              <Text style={{ color: theme.muted }}>Future: {item.futureInstrument?.instrumentKey ?? 'unpaired'}</Text>
              <Pressable onPress={() => void api.deleteWatchlist(item.id).then(() => queryClient.invalidateQueries({ queryKey: ['watchlist'] }))}>
                <Text style={{ color: theme.danger, fontWeight: '700' }}>Remove</Text>
              </Pressable>
            </Card>
          ))}
        </View>
      ) : (
        <EmptyState title="No watchlist symbols" subtitle="Add one or more F&O underlyings to let the backend pair them with spot and futures contracts." />
      )}
    </Screen>
  );
}
