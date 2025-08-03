
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('PostDeployValidation_2025-08-02', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('https://tursakur.vercel.app');

    // Click element
    await page.click('#province-select');

    // Click element
    await page.click('[data-testid="harita-tab"], a[href*="harita"]');

    // Take screenshot
    await page.screenshot({ path: 'final_harita_test.png', { fullPage: true } });
});