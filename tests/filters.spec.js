// tests/filters.spec.js
import { test, expect } from '@playwright/test';

/**
 * TURSAKUR 2.0 - Filter & Search Functionality Tests
 * Tests for filtering, searching, and UI interactions
 */

test.describe('Search Functionality', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('[data-testid="facility-item"]', { timeout: 10000 });
  });

  test('should search for facilities by name', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="hastane"]');
    
    // Search for "hastane"
    await searchInput.fill('hastane');
    await page.waitForTimeout(1000); // Debounce delay
    
    // Results should be filtered
    const results = page.locator('[data-testid="facility-item"]');
    await expect(results).toHaveCount.greaterThan(0);
    
    // All results should contain "hastane" in name
    const firstResult = results.first();
    const facilityName = await firstResult.locator('.facility-name').textContent();
    expect(facilityName.toLowerCase()).toContain('hastane');
  });

  test('should search for facilities by location', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="hastane"]');
    
    // Search for "İstanbul"
    await searchInput.fill('İstanbul');
    await page.waitForTimeout(1000);
    
    // Results should be filtered to İstanbul
    const results = page.locator('[data-testid="facility-item"]');
    await expect(results).toHaveCount.greaterThan(0);
    
    // Check that results show İstanbul
    const firstResult = results.first();
    const facilityLocation = await firstResult.locator('.facility-location').textContent();
    expect(facilityLocation).toContain('İstanbul');
  });

  test('should clear search results', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="hastane"]');
    
    // Perform search
    await searchInput.fill('test');
    await page.waitForTimeout(1000);
    
    // Clear search
    await searchInput.clear();
    await page.waitForTimeout(1000);
    
    // All results should be shown again
    const results = page.locator('[data-testid="facility-item"]');
    await expect(results).toHaveCount.greaterThan(0);
  });

});

test.describe('Province Filter', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('[data-testid="facility-item"]', { timeout: 10000 });
  });

  test('should filter by province', async ({ page }) => {
    // Select İstanbul from province dropdown
    await page.locator('#province-select').selectOption('İstanbul');
    await page.waitForTimeout(1000);
    
    // Results should be filtered to İstanbul
    const results = page.locator('[data-testid="facility-item"]');
    await expect(results).toHaveCount.greaterThan(0);
    
    // All results should be from İstanbul
    const firstResult = results.first();
    const facilityLocation = await firstResult.locator('.facility-location').textContent();
    expect(facilityLocation).toContain('İstanbul');
  });

  test('should show districts when province selected', async ({ page }) => {
    // Select a province
    await page.locator('#province-select').selectOption('İstanbul');
    await page.waitForTimeout(1000);
    
    // District dropdown should appear
    const districtSelect = page.locator('#district-select');
    await expect(districtSelect).toBeVisible();
    
    // Should have district options
    await districtSelect.click();
    const districtOptions = page.locator('#district-select option');
    await expect(districtOptions).toHaveCount.greaterThan(1); // At least "Tüm İlçeler" + actual districts
  });

  test('should filter by district', async ({ page }) => {
    // Select province first
    await page.locator('#province-select').selectOption('İstanbul');
    await page.waitForTimeout(1000);
    
    // Wait for districts to load
    await page.waitForSelector('#district-select option[value!=""]', { timeout: 5000 });
    
    // Select first available district
    const districtOptions = page.locator('#district-select option[value!=""]');
    const firstDistrict = await districtOptions.first().getAttribute('value');
    
    if (firstDistrict) {
      await page.locator('#district-select').selectOption(firstDistrict);
      await page.waitForTimeout(1000);
      
      // Results should be filtered by district
      const results = page.locator('[data-testid="facility-item"]');
      if (await results.count() > 0) {
        const firstResult = results.first();
        const facilityLocation = await firstResult.locator('.facility-location').textContent();
        expect(facilityLocation).toContain(firstDistrict);
      }
    }
  });

});

test.describe('Facility Type Filter', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('[data-testid="facility-item"]', { timeout: 10000 });
  });

  test('should filter by facility type', async ({ page }) => {
    // Find first facility type checkbox
    const typeCheckbox = page.locator('.filter-checkboxes input[type="checkbox"]').first();
    const typeLabel = await typeCheckbox.locator('..').locator('.checkbox-text').textContent();
    const facilityType = typeLabel.split('(')[0].trim(); // Extract type name before count
    
    // Check the checkbox
    await typeCheckbox.check();
    await page.waitForTimeout(1000);
    
    // Results should be filtered by type
    const results = page.locator('[data-testid="facility-item"]');
    await expect(results).toHaveCount.greaterThan(0);
    
    // Check first result has correct type
    const firstResult = results.first();
    const facilityTypeText = await firstResult.locator('.facility-type').textContent();
    expect(facilityTypeText).toContain(facilityType);
  });

  test('should support multiple facility type selection', async ({ page }) => {
    // Select first two facility types
    const typeCheckboxes = page.locator('.filter-checkboxes input[type="checkbox"]');
    
    if (await typeCheckboxes.count() >= 2) {
      await typeCheckboxes.nth(0).check();
      await typeCheckboxes.nth(1).check();
      await page.waitForTimeout(1000);
      
      // Results should include both types
      const results = page.locator('[data-testid="facility-item"]');
      await expect(results).toHaveCount.greaterThan(0);
    }
  });

  test('should clear all filters', async ({ page }) => {
    // Apply some filters
    await page.locator('#province-select').selectOption('İstanbul');
    await page.locator('.filter-checkboxes input[type="checkbox"]').first().check();
    await page.waitForTimeout(1000);
    
    // Click clear filters button
    await page.locator('[data-testid="clear-filters"]').click();
    await page.waitForTimeout(1000);
    
    // All filters should be reset
    await expect(page.locator('#province-select')).toHaveValue('');
    await expect(page.locator('.filter-checkboxes input[type="checkbox"]:checked')).toHaveCount(0);
    
    // All results should be shown
    const results = page.locator('[data-testid="facility-item"]');
    await expect(results).toHaveCount.greaterThan(0);
  });

});

test.describe('Combined Filters', () => {
  
  test('should combine search and province filter', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('[data-testid="facility-item"]', { timeout: 10000 });
    
    // Apply province filter
    await page.locator('#province-select').selectOption('İstanbul');
    
    // Apply search
    const searchInput = page.locator('input[placeholder*="hastane"]');
    await searchInput.fill('hastane');
    await page.waitForTimeout(1000);
    
    // Results should match both criteria
    const results = page.locator('[data-testid="facility-item"]');
    if (await results.count() > 0) {
      const firstResult = results.first();
      const facilityName = await firstResult.locator('.facility-name').textContent();
      const facilityLocation = await firstResult.locator('.facility-location').textContent();
      
      expect(facilityName.toLowerCase()).toContain('hastane');
      expect(facilityLocation).toContain('İstanbul');
    }
  });

});
