import React, { PropsWithChildren } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  useColorScheme,
  View,
  type StyleProp,
  type ViewStyle
} from 'react-native';
import Svg, { Path, Polyline } from 'react-native-svg';

const palette = {
  light: {
    background: '#F4F7FB',
    surface: '#FFFFFF',
    border: '#D7E1EE',
    text: '#0B1F35',
    muted: '#63758C',
    accent: '#1B74F4',
    success: '#168A52',
    warning: '#D97706',
    danger: '#D14343'
  },
  dark: {
    background: '#07111F',
    surface: '#0E1A2B',
    border: '#22324A',
    text: '#F6F9FC',
    muted: '#A8B5C7',
    accent: '#58A6FF',
    success: '#4ADE80',
    warning: '#FDBA74',
    danger: '#F87171'
  }
} as const;

export const useTheme = () => {
  const scheme = useColorScheme() === 'dark' ? 'dark' : 'light';
  return palette[scheme];
};

export const Screen = ({ children }: PropsWithChildren) => {
  const theme = useTheme();
  return <ScrollView style={{ flex: 1, backgroundColor: theme.background }} contentContainerStyle={styles.screen}>{children}</ScrollView>;
};

export const Card = ({ children, style }: PropsWithChildren<{ style?: StyleProp<ViewStyle> }>) => {
  const theme = useTheme();
  return <View style={[styles.card, { backgroundColor: theme.surface, borderColor: theme.border }, style]}>{children}</View>;
};

export const SectionHeader = ({ title, subtitle }: { title: string; subtitle?: string }) => {
  const theme = useTheme();
  return (
    <View style={styles.sectionHeader}>
      <Text style={[styles.sectionTitle, { color: theme.text }]}>{title}</Text>
      {subtitle ? <Text style={[styles.sectionSubtitle, { color: theme.muted }]}>{subtitle}</Text> : null}
    </View>
  );
};

export const Badge = ({ label, tone = 'neutral' }: { label: string; tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'accent' }) => {
  const theme = useTheme();
  const colors = {
    neutral: theme.muted,
    success: theme.success,
    warning: theme.warning,
    danger: theme.danger,
    accent: theme.accent
  } as const;
  return (
    <View style={[styles.badge, { borderColor: colors[tone] }]}>
      <Text style={[styles.badgeText, { color: colors[tone] }]}>{label}</Text>
    </View>
  );
};

export const PrimaryButton = ({ title, onPress, disabled }: { title: string; onPress: () => void; disabled?: boolean }) => {
  const theme = useTheme();
  return (
    <Pressable onPress={onPress} disabled={disabled} style={[styles.button, { backgroundColor: disabled ? theme.border : theme.accent }]}> 
      <Text style={[styles.buttonText, { color: '#FFFFFF' }]}>{title}</Text>
    </Pressable>
  );
};

export const MetricCard = ({ label, value, helper, tone = 'accent' }: { label: string; value: string; helper?: string; tone?: 'accent' | 'success' | 'warning' | 'danger' }) => {
  const theme = useTheme();
  const toneColor = { accent: theme.accent, success: theme.success, warning: theme.warning, danger: theme.danger }[tone];
  return (
    <Card style={styles.metricCard}>
      <Text style={[styles.metricLabel, { color: theme.muted }]}>{label}</Text>
      <Text style={[styles.metricValue, { color: theme.text }]}>{value}</Text>
      {helper ? <Text style={[styles.metricHelper, { color: toneColor }]}>{helper}</Text> : null}
    </Card>
  );
};

export const EmptyState = ({ title, subtitle }: { title: string; subtitle: string }) => {
  const theme = useTheme();
  return (
    <Card>
      <Text style={[styles.emptyTitle, { color: theme.text }]}>{title}</Text>
      <Text style={[styles.emptySubtitle, { color: theme.muted }]}>{subtitle}</Text>
    </Card>
  );
};

export const LoadingState = ({ label }: { label: string }) => {
  const theme = useTheme();
  return (
    <Card>
      <Text style={[styles.emptySubtitle, { color: theme.muted }]}>{label}</Text>
    </Card>
  );
};

export const Sparkline = ({ points, width = 140, height = 40 }: { points: number[]; width?: number; height?: number }) => {
  const theme = useTheme();
  if (points.length < 2) {
    return (
      <Svg width={width} height={height}>
        <Path d={`M0 ${height / 2} L${width} ${height / 2}`} stroke={theme.border} strokeWidth={2} fill="none" />
      </Svg>
    );
  }

  const min = Math.min(...points);
  const max = Math.max(...points);
  const span = max - min || 1;
  const stepX = width / Math.max(points.length - 1, 1);
  const path = points
    .map((point, index) => {
      const x = index * stepX;
      const y = height - ((point - min) / span) * height;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <Svg width={width} height={height}>
      <Polyline points={path} stroke={theme.accent} strokeWidth={2.5} fill="none" strokeLinejoin="round" strokeLinecap="round" />
    </Svg>
  );
};

export const DataRow = ({ label, value }: { label: string; value: string }) => {
  const theme = useTheme();
  return (
    <View style={[styles.dataRow, { borderBottomColor: theme.border }]}> 
      <Text style={[styles.dataLabel, { color: theme.muted }]}>{label}</Text>
      <Text style={[styles.dataValue, { color: theme.text }]}>{value}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  screen: {
    padding: 16,
    gap: 16
  },
  card: {
    borderRadius: 20,
    borderWidth: 1,
    padding: 16,
    gap: 10,
    shadowOpacity: 0.08,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
    elevation: 2
  },
  sectionHeader: {
    gap: 4
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700'
  },
  sectionSubtitle: {
    fontSize: 14,
    lineHeight: 20
  },
  badge: {
    alignSelf: 'flex-start',
    borderRadius: 999,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 5
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600'
  },
  button: {
    borderRadius: 16,
    paddingVertical: 14,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center'
  },
  buttonText: {
    fontSize: 15,
    fontWeight: '700'
  },
  metricCard: {
    minWidth: 180,
    flex: 1
  },
  metricLabel: {
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.7
  },
  metricValue: {
    fontSize: 28,
    fontWeight: '800'
  },
  metricHelper: {
    fontSize: 13,
    fontWeight: '600'
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '700'
  },
  emptySubtitle: {
    fontSize: 14,
    lineHeight: 20
  },
  dataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: StyleSheet.hairlineWidth
  },
  dataLabel: {
    fontSize: 13,
    fontWeight: '500'
  },
  dataValue: {
    fontSize: 13,
    fontWeight: '700'
  }
});
