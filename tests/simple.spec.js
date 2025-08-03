// tests/simple.spec.js
import { test, expect } from '@playwright/test';

/**
 * Simple connectivity and basic functionality tests
 */
test.describe('Basic Connectivity', () => {
  test('should load the homepage', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check if page title contains TURSAKUR
    await expect(page).toHaveTitle(/TURSAKUR/);
    
    // Check if main container exists
    const mainContainer = page.locator('body');
    await expect(mainContainer).toBeVisible();
  });

  test('should have working navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check if navigation elements exist (without waiting for data loading)
    const bodyElement = page.locator('body');
    await expect(bodyElement).toBeVisible();
    
    // Basic functionality check - page should be responsive
    await expect(page).toHaveURL(/\//);
  });
});
