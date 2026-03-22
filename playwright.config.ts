import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  retries: 1,
  use: {
    baseURL: 'http://127.0.0.1:19006',
    headless: true
  },
  webServer: {
    command: 'pnpm --filter @fo-scanner/mobile web',
    port: 19006,
    reuseExistingServer: true,
    timeout: 120000
  }
});
