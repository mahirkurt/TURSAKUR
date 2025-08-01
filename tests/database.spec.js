// tests/database.spec.js
import { test, expect } from '@playwright/test';

/**
 * TURSAKUR 2.0 - Database Integration Tests
 * Tests for Supabase API connectivity and data fetching
 */

test.describe('Supabase Database Integration', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should fetch health facilities from Supabase', async ({ page }) => {
    // Wait for data to load
    await page.waitForSelector('[data-testid="facility-item"]', { timeout: 10000 });
    
    // Check that facilities are displayed
    const facilityItems = page.locator('[data-testid="facility-item"]');
    await expect(facilityItems).toHaveCount.greaterThan(0);
    
    // Check first facility has required fields
    const firstFacility = facilityItems.first();
    await expect(firstFacility.locator('.facility-name')).toBeVisible();
    await expect(firstFacility.locator('.facility-type')).toBeVisible();
    await expect(firstFacility.locator('.facility-location')).toBeVisible();
  });

  test('should load provinces from database', async ({ page }) => {
    // Open province filter
    await page.locator('#province-select').click();
    
    // Wait for options to load
    await page.waitForSelector('#province-select option[value="İstanbul"]', { timeout: 5000 });
    
    // Check common provinces exist
    const istanbulOption = page.locator('#province-select option[value="İstanbul"]');
    const ankaraOption = page.locator('#province-select option[value="Ankara"]');
    const izmirOption = page.locator('#province-select option[value="İzmir"]');
    
    await expect(istanbulOption).toBeVisible();
    await expect(ankaraOption).toBeVisible();
    await expect(izmirOption).toBeVisible();
  });

  test('should load facility types from database', async ({ page }) => {
    // Wait for facility types to load in checkboxes
    await page.waitForSelector('input[type="checkbox"]', { timeout: 5000 });
    
    // Check common facility types exist
    const hospitalCheckbox = page.locator('text=Hastane').locator('input[type="checkbox"]');
    const clinicCheckbox = page.locator('text=Klinik').locator('input[type="checkbox"]');
    
    await expect(hospitalCheckbox).toBeVisible();
    await expect(clinicCheckbox).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock network failure
    await page.route('**/rest/v1/kuruluslar*', route => {
      route.abort();
    });
    
    await page.reload();
    await page.waitForTimeout(3000);
    
    // Should show fallback/error state
    const errorMessage = page.locator('[data-testid="error-message"]');
    const fallbackData = page.locator('[data-testid="fallback-data"]');
    
    // Either error message or fallback data should be shown
    await expect(errorMessage.or(fallbackData)).toBeVisible();
  });

  test('should display database statistics', async ({ page }) => {
    // Wait for stats to load
    await page.waitForSelector('[data-testid="stats-panel"]', { timeout: 10000 });
    
    const statsPanel = page.locator('[data-testid="stats-panel"]');
    await expect(statsPanel).toBeVisible();
    
    // Check stats display numbers
    await expect(statsPanel.locator('.total-count')).toContainText(/\d+/);
    await expect(statsPanel.locator('.province-count')).toContainText(/\d+/);
    await expect(statsPanel.locator('.type-count')).toContainText(/\d+/);
  });

});

test.describe('Real-time Data Validation', () => {

  test('should validate data consistency', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Get total count from stats
    const statsText = await page.locator('[data-testid="total-count"]').textContent();
    const totalFromStats = parseInt(statsText.match(/\d+/)[0]);
    
    // Count actual displayed items
    const facilityItems = page.locator('[data-testid="facility-item"]');
    const displayedCount = await facilityItems.count();
    
    // Counts should match (considering pagination)
    expect(displayedCount).toBeGreaterThan(0);
    expect(totalFromStats).toBeGreaterThanOrEqual(displayedCount);
  });

  test('should validate coordinate data', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="facility-item"]', { timeout: 10000 });
    
    // Check that facilities with coordinates are displayed on map
    const facilitiesWithCoords = page.locator('[data-testid="facility-item"][data-has-coords="true"]');
    const coordCount = await facilitiesWithCoords.count();
    
    if (coordCount > 0) {
      // Map should show markers
      const mapMarkers = page.locator('.leaflet-marker-icon');
      await expect(mapMarkers).toHaveCount.greaterThan(0);
    }
  });

});
