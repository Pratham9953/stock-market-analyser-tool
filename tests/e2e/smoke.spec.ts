import { test, expect } from '@playwright/test';

test('web shell renders connect or dashboard copy', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText(/Realtime F&O Scanner|Connect Upstox|Dashboard/i)).toBeVisible();
});
