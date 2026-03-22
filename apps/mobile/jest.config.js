module.exports = {
  preset: 'jest-expo',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|expo(nent)?|@expo|expo-router|react-native-svg|@tanstack)/)'
  ],
  moduleNameMapper: {
    '^@fo-scanner/shared$': '<rootDir>/../../packages/shared/src/index.ts',
    '^@fo-scanner/ui$': '<rootDir>/../../packages/ui/src/index.tsx'
  }
};
