import crypto from 'node:crypto';
import { env } from '../../config/env';

export type EncryptedPayload = {
  cipherText: string;
  iv: string;
  authTag: string;
};

const key = crypto.createHash('sha256').update(env.TOKEN_ENCRYPTION_SECRET).digest();

export const encryptSecret = (value: string): EncryptedPayload => {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const encrypted = Buffer.concat([cipher.update(value, 'utf8'), cipher.final()]);
  return {
    cipherText: encrypted.toString('base64'),
    iv: iv.toString('base64'),
    authTag: cipher.getAuthTag().toString('base64')
  };
};

export const decryptSecret = (payload: EncryptedPayload): string => {
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, Buffer.from(payload.iv, 'base64'));
  decipher.setAuthTag(Buffer.from(payload.authTag, 'base64'));
  const decrypted = Buffer.concat([
    decipher.update(Buffer.from(payload.cipherText, 'base64')),
    decipher.final()
  ]);
  return decrypted.toString('utf8');
};
