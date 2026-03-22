import React from 'react';
import { Switch, Text, TextInput, View } from 'react-native';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Card, PrimaryButton, Screen, SectionHeader, useTheme } from '@fo-scanner/ui';
import { api } from '../../src/lib/api';

export default function SettingsScreen() {
  const theme = useTheme();
  const { data } = useQuery({ queryKey: ['settings'], queryFn: () => api.getSettings() });
  const [threshold, setThreshold] = React.useState('10');
  const [cooldownMs, setCooldownMs] = React.useState('30000');
  const [freshnessMs, setFreshnessMs] = React.useState('10000');
  const [darkMode, setDarkMode] = React.useState(true);

  React.useEffect(() => {
    if (!data) return;
    setThreshold(String(data.threshold));
    setCooldownMs(String(data.cooldownMs));
    setFreshnessMs(String(data.freshnessMs));
    setDarkMode(data.darkMode);
  }, [data]);

  const mutation = useMutation({
    mutationFn: () =>
      api.updateSettings({
        threshold: Number(threshold),
        cooldownMs: Number(cooldownMs),
        freshnessMs: Number(freshnessMs),
        preferredExchange: data?.preferredExchange ?? 'NSE',
        darkMode,
        exchanges: data?.exchanges ?? ['NSE'],
        segments: data?.segments ?? ['NSE_EQ', 'NSE_FO']
      })
  });

  return (
    <Screen>
      <SectionHeader title="Settings" subtitle="Tune threshold, cooldown, freshness windows, and local display preferences." />
      <Card>
        <Text style={{ color: theme.text, fontWeight: '700' }}>Alert threshold (INR)</Text>
        <TextInput value={threshold} onChangeText={setThreshold} keyboardType="numeric" style={{ borderColor: theme.border, borderWidth: 1, borderRadius: 14, padding: 14, color: theme.text }} />
        <Text style={{ color: theme.text, fontWeight: '700' }}>Cooldown (ms)</Text>
        <TextInput value={cooldownMs} onChangeText={setCooldownMs} keyboardType="numeric" style={{ borderColor: theme.border, borderWidth: 1, borderRadius: 14, padding: 14, color: theme.text }} />
        <Text style={{ color: theme.text, fontWeight: '700' }}>Freshness window (ms)</Text>
        <TextInput value={freshnessMs} onChangeText={setFreshnessMs} keyboardType="numeric" style={{ borderColor: theme.border, borderWidth: 1, borderRadius: 14, padding: 14, color: theme.text }} />
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <Text style={{ color: theme.text, fontWeight: '700' }}>Dark mode preference</Text>
          <Switch value={darkMode} onValueChange={setDarkMode} />
        </View>
        <PrimaryButton title={mutation.isPending ? 'Saving…' : 'Save settings'} onPress={() => mutation.mutate()} disabled={mutation.isPending} />
      </Card>
    </Screen>
  );
}
