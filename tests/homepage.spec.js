// tests/homepage.spec.js
import { test, expect } from '@playwright/test';

/**
 * TURSAKUR 2.0 - Homepage & Basic Functionality Tests
 * Tests for main page loading, UI components, and initial data fetch
 */

test.describe('TURSAKUR Homepage', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to homepage before each test
    await page.goto('/');
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
  });

  test('should load homepage successfully', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/TURSAKUR/);
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('TURSAKUR');
    
    // Check Material Design 3 theme is applied
    await expect(page.locator('body')).toHaveClass(/material-theme/);
  });

  test('should display main navigation components', async ({ page }) => {
    // Check search input
    await expect(page.locator('input[placeholder*="hastane"]')).toBeVisible();
    
    // Check filter panel exists
    await expect(page.locator('[data-testid="filter-panel"]')).toBeVisible();
    
    // Check map container
    await expect(page.locator('#map')).toBeVisible();
    
    // Check results area
    await expect(page.locator('[data-testid="results-list"]')).toBeVisible();
  });

  test('should load without console errors', async ({ page }) => {
    const consoleErrors = [];
    
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    await page.reload();
    await page.waitForTimeout(3000); // Wait for async operations
    
    // Filter out known acceptable errors
    const criticalErrors = consoleErrors.filter(error => 
      !error.includes('React DevTools') && 
      !error.includes('Download the React DevTools') &&
      !error.includes('favicon.ico')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('should display loading state initially', async ({ page }) => {
    // Reload to catch loading state
    await page.reload();
    
    // Should show loading indicator
    const loadingElement = page.locator('[data-testid="loading"]');
    await expect(loadingElement).toBeVisible({ timeout: 1000 });
  });

});

test.describe('Responsive Design', () => {
  
  test('should work on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check mobile-friendly layout
    await expect(page.locator('.filter-panel')).toBeVisible();
    await expect(page.locator('#map')).toBeVisible();
    
    // Mobile-specific UI elements
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
  });

  test('should work on tablet devices', async ({ page }) => {
    // Set tablet viewport  
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    
    // Check tablet layout
    await expect(page.locator('.main-content')).toBeVisible();
    await expect(page.locator('#map')).toBeVisible();
  });

});
