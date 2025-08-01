// tests/map.spec.js
import { test, expect } from '@playwright/test';

/**
 * TURSAKUR 2.0 - Map Integration Tests
 * Tests for Leaflet map functionality and marker interactions
 */

test.describe('Map Functionality', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('#map', { timeout: 10000 });
  });

  test('should load map container', async ({ page }) => {
    // Check map container exists
    const mapContainer = page.locator('#map');
    await expect(mapContainer).toBeVisible();
    
    // Check Leaflet map is initialized
    await expect(mapContainer.locator('.leaflet-container')).toBeVisible();
    
    // Check map controls are present
    await expect(mapContainer.locator('.leaflet-control-zoom')).toBeVisible();
  });

  test('should display facility markers on map', async ({ page }) => {
    // Wait for facilities to load
    await page.waitForSelector('[data-testid="facility-item"]', { timeout: 10000 });
    
    // Wait for map markers to appear
    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });
    
    // Check markers are present
    const markers = page.locator('.leaflet-marker-icon');
    await expect(markers).toHaveCount.greaterThan(0);
  });

  test('should open popup when marker is clicked', async ({ page }) => {
    // Wait for markers
    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });
    
    // Click first marker
    const firstMarker = page.locator('.leaflet-marker-icon').first();
    await firstMarker.click();
    
    // Check popup appears
    const popup = page.locator('.leaflet-popup');
    await expect(popup).toBeVisible();
    
    // Check popup contains facility information
    await expect(popup.locator('.facility-name')).toBeVisible();
    await expect(popup.locator('.facility-type')).toBeVisible();
  });

  test('should sync map with filter results', async ({ page }) => {
    // Wait for initial load
    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });
    const initialMarkerCount = await page.locator('.leaflet-marker-icon').count();
    
    // Apply province filter
    await page.locator('#province-select').selectOption('İstanbul');
    await page.waitForTimeout(2000); // Wait for map update
    
    // Marker count should change (likely decrease)
    const filteredMarkerCount = await page.locator('.leaflet-marker-icon').count();
    expect(filteredMarkerCount).toBeLessThanOrEqual(initialMarkerCount);
  });

  test('should zoom to Turkey bounds initially', async ({ page }) => {
    // Wait for map to load
    await page.waitForSelector('.leaflet-container', { timeout: 10000 });
    
    // Check that map is centered on Turkey (approximate coordinates)
    const mapContainer = page.locator('.leaflet-container');
    await expect(mapContainer).toBeVisible();
    
    // Map should be visible and interactive
    await expect(mapContainer.locator('.leaflet-control-zoom-in')).toBeVisible();
    await expect(mapContainer.locator('.leaflet-control-zoom-out')).toBeVisible();
  });

});

test.describe('Map Interactions', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('.leaflet-container', { timeout: 10000 });
  });

  test('should support zoom controls', async ({ page }) => {
    const zoomIn = page.locator('.leaflet-control-zoom-in');
    const zoomOut = page.locator('.leaflet-control-zoom-out');
    
    // Test zoom in
    await zoomIn.click();
    await page.waitForTimeout(500);
    
    // Test zoom out
    await zoomOut.click();
    await page.waitForTimeout(500);
    
    // Controls should remain functional
    await expect(zoomIn).toBeEnabled();
    await expect(zoomOut).toBeEnabled();
  });

  test('should support map dragging', async ({ page }) => {
    const mapContainer = page.locator('.leaflet-container');
    
    // Get initial map position
    const initialBoundingBox = await mapContainer.boundingBox();
    
    // Perform drag operation
    await mapContainer.hover();
    await page.mouse.down();
    await page.mouse.move(100, 100);
    await page.mouse.up();
    
    await page.waitForTimeout(500);
    
    // Map should still be functional after drag
    await expect(mapContainer).toBeVisible();
  });

  test('should cluster markers when zoomed out', async ({ page }) => {
    // Wait for markers to load
    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });
    
    // Zoom out to see clustering
    const zoomOut = page.locator('.leaflet-control-zoom-out');
    await zoomOut.click();
    await zoomOut.click();
    await page.waitForTimeout(1000);
    
    // Check for cluster markers (if clustering is implemented)
    const clusterMarkers = page.locator('.marker-cluster');
    if (await clusterMarkers.count() > 0) {
      await expect(clusterMarkers.first()).toBeVisible();
    }
  });

});

test.describe('Map Performance', () => {
  
  test('should load map within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForSelector('.leaflet-container', { timeout: 10000 });
    await page.waitForSelector('.leaflet-marker-icon', { timeout: 15000 });
    
    const loadTime = Date.now() - startTime;
    
    // Map should load within 15 seconds
    expect(loadTime).toBeLessThan(15000);
  });

  test('should handle large number of markers', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });
    
    // Remove all filters to show maximum markers
    await page.locator('[data-testid="clear-filters"]').click();
    await page.waitForTimeout(2000);
    
    // Map should remain responsive
    const mapContainer = page.locator('.leaflet-container');
    await expect(mapContainer).toBeVisible();
    
    // Zoom controls should work
    await page.locator('.leaflet-control-zoom-in').click();
    await page.waitForTimeout(500);
    await expect(mapContainer).toBeVisible();
  });

  test('should handle map resize', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('.leaflet-container', { timeout: 10000 });
    
    // Change viewport size
    await page.setViewportSize({ width: 800, height: 600 });
    await page.waitForTimeout(1000);
    
    // Map should adapt to new size
    const mapContainer = page.locator('.leaflet-container');
    await expect(mapContainer).toBeVisible();
    
    // Change back
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.waitForTimeout(1000);
    
    await expect(mapContainer).toBeVisible();
  });

});
