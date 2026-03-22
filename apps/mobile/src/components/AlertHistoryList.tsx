import React from 'react';
import { Pressable, Text, View } from 'react-native';
import { Badge, Card, useTheme } from '@fo-scanner/ui';
import { formatCurrency, formatDateTime } from '@fo-scanner/shared';
import type { AlertHistoryItemDto } from '@fo-scanner/shared';

export const AlertHistoryList = ({ alerts, onAcknowledge }: { alerts: AlertHistoryItemDto[]; onAcknowledge?: (alertId: string) => void }) => {
  const theme = useTheme();
  return (
    <View style={{ gap: 12 }}>
      {alerts.map((alert) => (
        <Card key={alert.id}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={{ color: theme.text, fontSize: 16, fontWeight: '700' }}>{alert.symbol}</Text>
            <Badge label={`${alert.spread.toFixed(2)} INR`} tone={alert.acknowledgedAt ? 'neutral' : 'danger'} />
          </View>
          <Text style={{ color: theme.muted }}>Threshold {alert.threshold.toFixed(2)} · Freshness {alert.freshnessMs}ms</Text>
          <Text style={{ color: theme.muted }}>Spot {formatCurrency(alert.spotPrice)} · Future {formatCurrency(alert.futurePrice)}</Text>
          <Text style={{ color: theme.muted }}>Triggered {formatDateTime(alert.triggeredAt)}</Text>
          {!alert.acknowledgedAt && onAcknowledge ? (
            <Pressable onPress={() => onAcknowledge(alert.id)} style={{ paddingVertical: 8 }}>
              <Text style={{ color: theme.accent, fontWeight: '700' }}>Acknowledge</Text>
            </Pressable>
          ) : null}
        </Card>
      ))}
    </View>
  );
};
