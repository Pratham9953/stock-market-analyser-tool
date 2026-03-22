import React from 'react';
import { Text } from 'react-native';
import { LoadingState, Screen, SectionHeader } from '@fo-scanner/ui';
import { useBootstrap } from '../src/hooks/use-bootstrap';

export default function IndexScreen() {
  const bootstrap = useBootstrap();

  return (
    <Screen>
      <SectionHeader title="Realtime F&O Scanner" subtitle="Bootstrapping local app session and restoring market connectivity." />
      {bootstrap.isError ? <Text>{String(bootstrap.error)}</Text> : <LoadingState label="Preparing your scanner workspace..." />}
    </Screen>
  );
}
