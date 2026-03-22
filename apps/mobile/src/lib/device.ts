import * as Application from 'expo-application';
import { storage } from './storage';

const fallbackDeviceId = () => `web-${Math.random().toString(36).slice(2)}-${Date.now()}`;

export const getOrCreateDeviceId = async (): Promise<string> => {
  const existing = await storage.getDeviceId();
  if (existing) return existing;
  const generated = Application.getAndroidId?.() || Application.applicationId || fallbackDeviceId();
  await storage.setDeviceId(generated);
  return generated;
};
