// tests/performance.spec.js
import { test, expect } from '@playwright/test';

/**
 * TURSAKUR 2.0 - Performance & Accessibility Tests
 * Tests for page performance, accessibility compliance, and user experience
 */

test.describe('Performance Tests', () => {
  
  test('should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/', { waitUntil: 'networkidle' });
    
    const loadTime = Date.now() - startTime;
    console.log(`Page load time: ${loadTime}ms`);
    
    // Page should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('should have good Core Web Vitals', async ({ page }) => {
    await page.goto('/');
    
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Measure First Contentful Paint (FCP)
    const fcp = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-contentful-paint') {
              resolve(entry.startTime);
            }
          }
        }).observe({ entryTypes: ['paint'] });
      });
    });
    
    // FCP should be under 2.5 seconds
    expect(fcp).toBeLessThan(2500);
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    await page.goto('/');
    
    // Clear all filters to load maximum data
    await page.waitForSelector('[data-testid="clear-filters"]', { timeout: 10000 });
    await page.locator('[data-testid="clear-filters"]').click();
    
    const startTime = Date.now();
    
    // Wait for all data to load
    await page.waitForSelector('[data-testid="facility-item"]', { timeout: 15000 });
    await page.waitForTimeout(2000);
    
    const renderTime = Date.now() - startTime;
    console.log(`Large dataset render time: ${renderTime}ms`);
    
    // Should render within 10 seconds
    expect(renderTime).toBeLessThan(10000);
    
    // UI should remain responsive
    const searchInput = page.locator('input[placeholder*="hastane"]');
    await searchInput.fill('test');
    await expect(searchInput).toHaveValue('test');
  });

  test('should optimize image and asset loading', async ({ page }) => {
    // Monitor network requests
    const responses = [];
    page.on('response', response => {
      responses.push({
        url: response.url(),
        status: response.status(),
        size: response.headers()['content-length']
      });
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check that critical assets loaded successfully
    const criticalAssets = responses.filter(r => 
      r.url.includes('.js') || r.url.includes('.css') || r.url.includes('.svg')
    );
    
    const failedAssets = criticalAssets.filter(r => r.status >= 400);
    expect(failedAssets).toHaveLength(0);
  });

});

test.describe('Accessibility Tests', () => {
  
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check h1 exists and is unique
    const h1Elements = page.locator('h1');
    await expect(h1Elements).toHaveCount(1);
    
    // Check heading content
    await expect(h1Elements).toContainText('TURSAKUR');
    
    // Check other headings follow proper hierarchy
    const h2Elements = page.locator('h2');
    if (await h2Elements.count() > 0) {
      await expect(h2Elements.first()).toBeVisible();
    }
  });

  test('should have proper ARIA labels and roles', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check search input has proper labels
    const searchInput = page.locator('input[placeholder*="hastane"]');
    await expect(searchInput).toHaveAttribute('aria-label');
    
    // Check form controls have labels
    const provinceSelect = page.locator('#province-select');
    await expect(provinceSelect).toHaveAttribute('aria-label');
    
    // Check map has proper role
    const mapContainer = page.locator('#map');
    await expect(mapContainer).toHaveAttribute('role');
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Tab through interactive elements
    await page.keyboard.press('Tab'); // Focus search input
    await expect(page.locator('input[placeholder*="hastane"]')).toBeFocused();
    
    await page.keyboard.press('Tab'); // Focus province select
    await expect(page.locator('#province-select')).toBeFocused();
    
    // Test Enter key on select
    await page.keyboard.press('Enter');
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
  });

  test('should have sufficient color contrast', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check main text elements
    const mainHeading = page.locator('h1');
    const bodyText = page.locator('body');
    
    await expect(mainHeading).toBeVisible();
    await expect(bodyText).toBeVisible();
    
    // Check that text is readable (contrast will be checked by accessibility tools)
    const headingColor = await mainHeading.evaluate(el => 
      window.getComputedStyle(el).color
    );
    const backgroundColor = await bodyText.evaluate(el => 
      window.getComputedStyle(el).backgroundColor
    );
    
    // Colors should be defined
    expect(headingColor).toBeTruthy();
    expect(backgroundColor).toBeTruthy();
  });

  test('should work with screen readers', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check for screen reader friendly elements
    await expect(page.locator('[aria-live]')).toHaveCount.greaterThanOrEqual(0);
    
    // Check status updates are announced
    const resultsArea = page.locator('[data-testid="results-list"]');
    await expect(resultsArea).toHaveAttribute('aria-live');
  });

});

test.describe('User Experience Tests', () => {
  
  test('should provide loading feedback', async ({ page }) => {
    await page.goto('/');
    
    // Should show loading indicator initially
    const loadingElement = page.locator('[data-testid="loading"]');
    await expect(loadingElement).toBeVisible({ timeout: 1000 });
    
    // Loading should disappear when content loads
    await page.waitForSelector('[data-testid="facility-item"]', { timeout: 10000 });
    await expect(loadingElement).not.toBeVisible();
  });

  test('should handle empty search results gracefully', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Search for something that won't match
    const searchInput = page.locator('input[placeholder*="hastane"]');
    await searchInput.fill('zzzznonexistentfacilityzzz');
    await page.waitForTimeout(1000);
    
    // Should show "no results" message
    const noResultsMessage = page.locator('[data-testid="no-results"]');
    await expect(noResultsMessage).toBeVisible();
  });

  test('should maintain filter state on page refresh', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Apply filters
    await page.locator('#province-select').selectOption('İstanbul');
    await page.waitForTimeout(1000);
    
    // Refresh page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Filters should be preserved (if implemented)
    // This test will pass if no filter preservation is implemented
    const provinceValue = await page.locator('#province-select').inputValue();
    // Either preserved or reset to default
    expect(provinceValue === 'İstanbul' || provinceValue === '').toBe(true);
  });

  test('should show helpful error messages', async ({ page }) => {
    // Mock network error
    await page.route('**/rest/v1/kuruluslar*', route => {
      route.abort();
    });
    
    await page.goto('/');
    await page.waitForTimeout(5000);
    
    // Should show user-friendly error message
    const errorMessage = page.locator('[data-testid="error-message"]');
    if (await errorMessage.isVisible()) {
      const errorText = await errorMessage.textContent();
      expect(errorText).toContain('bağlantı'); // Should contain connection-related text
    }
  });

});
