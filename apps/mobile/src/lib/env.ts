import { mobilePublicEnvSchema } from '@fo-scanner/shared';

export const mobileEnv = mobilePublicEnvSchema.parse({
  EXPO_PUBLIC_API_URL: process.env.EXPO_PUBLIC_API_URL,
  EXPO_PUBLIC_WS_URL: process.env.EXPO_PUBLIC_WS_URL,
  EXPO_PUBLIC_UPSTOX_CALLBACK_URL: process.env.EXPO_PUBLIC_UPSTOX_CALLBACK_URL,
  EXPO_PUBLIC_APP_NAME: process.env.EXPO_PUBLIC_APP_NAME
});
