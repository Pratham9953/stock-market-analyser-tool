import { decryptSecret, encryptSecret } from './crypto';

describe('token crypto', () => {
  it('round-trips encrypted broker tokens', () => {
    const encrypted = encryptSecret('super-secret-token');
    const decrypted = decryptSecret(encrypted);
    expect(decrypted).toBe('super-secret-token');
  });
});
