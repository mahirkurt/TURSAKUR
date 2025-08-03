
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('ProductionDeploymentTest_2025-08-03', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('https://tursakur.vercel.app');

    // Click element
    await page.click('select[data-testid="province-filter"]');

    // Click element
    await page.click('a[href="/harita"]');

    // Take screenshot
    await page.screenshot({ path: 'production-deployment-success.png', { fullPage: true } });
});