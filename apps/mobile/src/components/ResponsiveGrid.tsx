import React from 'react';
import { useWindowDimensions, View } from 'react-native';

export const ResponsiveGrid = ({ children }: { children: React.ReactNode }) => {
  const { width } = useWindowDimensions();
  const isWide = width >= 900;
  return <View style={{ flexDirection: isWide ? 'row' : 'column', flexWrap: 'wrap', gap: 12 }}>{children}</View>;
};
