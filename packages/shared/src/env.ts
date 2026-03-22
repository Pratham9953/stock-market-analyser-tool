import { z } from 'zod';

export const mobilePublicEnvSchema = z.object({
  EXPO_PUBLIC_API_URL: z.string().url(),
  EXPO_PUBLIC_WS_URL: z.string(),
  EXPO_PUBLIC_UPSTOX_CALLBACK_URL: z.string(),
  EXPO_PUBLIC_APP_NAME: z.string().default('F&O Backwardation Scanner')
});

export type MobilePublicEnv = z.infer<typeof mobilePublicEnvSchema>;
