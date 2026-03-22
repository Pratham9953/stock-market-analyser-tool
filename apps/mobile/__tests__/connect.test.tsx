import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react-native';
import ConnectScreen from '../app/connect';

jest.mock('../src/lib/api', () => ({
  api: {
    getConnectUrl: jest.fn(async () => ({ url: 'https://example.com' }))
  }
}));

jest.mock('expo-web-browser', () => ({
  openAuthSessionAsync: jest.fn(async () => ({ type: 'dismiss' }))
}));

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>
);

describe('ConnectScreen', () => {
  it('renders broker connection CTA', () => {
    const screen = render(<ConnectScreen />, { wrapper: Wrapper });
    expect(screen.getByText(/Connect Upstox/i)).toBeTruthy();
  });
});
