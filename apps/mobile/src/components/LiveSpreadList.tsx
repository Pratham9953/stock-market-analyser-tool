import React from 'react';
import { Text, View } from 'react-native';
import { Card, Badge, useTheme } from '@fo-scanner/ui';
import { formatCurrency, formatDateTime } from '@fo-scanner/shared';
import { useLiveStore } from '../store/live-store';

export const LiveSpreadList = () => {
  const theme = useTheme();
  const spreads = Object.values(useLiveStore((state) => state.spreads)).sort((a, b) => b.spread - a.spread);

  return (
    <View style={{ gap: 12 }}>
      {spreads.map((spread) => (
        <Card key={spread.pairId}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={{ color: theme.text, fontSize: 17, fontWeight: '700' }}>{spread.symbol}</Text>
            <Badge label={`${spread.spread.toFixed(2)} INR`} tone={spread.spread >= 10 ? 'danger' : 'accent'} />
          </View>
          <Text style={{ color: theme.muted }}>Spot {formatCurrency(spread.spotPrice)} · Future {formatCurrency(spread.futurePrice)}</Text>
          <Text style={{ color: theme.muted }}>Observed {formatDateTime(spread.observedAt)}</Text>
        </Card>
      ))}
    </View>
  );
};
