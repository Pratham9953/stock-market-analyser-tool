import AsyncStorage from '@react-native-async-storage/async-storage';

const SESSION_TOKEN_KEY = 'fo-scanner.session.token';
const DEVICE_ID_KEY = 'fo-scanner.device.id';

export const storage = {
  getSessionToken: () => AsyncStorage.getItem(SESSION_TOKEN_KEY),
  setSessionToken: (value: string) => AsyncStorage.setItem(SESSION_TOKEN_KEY, value),
  clearSessionToken: () => AsyncStorage.removeItem(SESSION_TOKEN_KEY),
  getDeviceId: () => AsyncStorage.getItem(DEVICE_ID_KEY),
  setDeviceId: (value: string) => AsyncStorage.setItem(DEVICE_ID_KEY, value)
};
