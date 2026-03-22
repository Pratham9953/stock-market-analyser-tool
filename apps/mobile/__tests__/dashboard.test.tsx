import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react-native';
import DashboardScreen from '../app/(tabs)/dashboard';

jest.mock('../src/hooks/use-dashboard', () => ({
  useDashboard: () => ({
    data: {
      activeConnection: true,
      subscribedInstrumentCount: 4,
      activeWatchlistCount: 2,
      liveAlertCount: 1,
      lastTickAt: new Date().toISOString(),
      backendLatencyMs: 12,
      websocketState: 'connected',
      marketDataState: 'connected',
      threshold: 10
    },
    isLoading: false
  })
}));

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>
);

describe('DashboardScreen', () => {
  it('renders dashboard heading', () => {
    const screen = render(<DashboardScreen />, { wrapper: Wrapper });
    expect(screen.getByText(/Dashboard/i)).toBeTruthy();
  });
});
