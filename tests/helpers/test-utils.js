// tests/helpers/test-utils.js
/**
 * TURSAKUR 2.0 - Test Utilities
 * Common helper functions for Playwright tests
 */

export const SELECTORS = {
  // Navigation
  searchInput: 'input[placeholder*="hastane"]',
  provinceSelect: '#province-select',
  districtSelect: '#district-select',
  clearFiltersBtn: '[data-testid="clear-filters"]',
  
  // Content
  facilityItem: '[data-testid="facility-item"]',
  resultsList: '[data-testid="results-list"]',
  loading: '[data-testid="loading"]',
  noResults: '[data-testid="no-results"]',
  
  // Map
  map: '#map',
  mapContainer: '.leaflet-container',
  mapMarker: '.leaflet-marker-icon',
  mapPopup: '.leaflet-popup',
  
  // Filter panel
  filterPanel: '[data-testid="filter-panel"]',
  typeCheckbox: '.filter-checkboxes input[type="checkbox"]',
  
  // Card elements
  facilityName: '.facility-name',
  facilityType: '.facility-type',
  facilityLocation: '.facility-location'
};

export const TIMEOUTS = {
  short: 2000,
  medium: 5000,
  long: 10000,
  veryLong: 15000
};

export const TEST_DATA = {
  provinces: ['İstanbul', 'Ankara', 'İzmir'],
  searchTerms: ['hastane', 'klinik', 'sağlık'],
  facilityTypes: ['Hastane', 'Klinik', 'Sağlık Ocağı']
};

/**
 * Wait for page to be fully loaded with data
 */
export async function waitForPageLoad(page) {
  await page.waitForLoadState('networkidle');
  await page.waitForSelector(SELECTORS.facilityItem, { timeout: TIMEOUTS.long });
}

/**
 * Wait for search results to update
 */
export async function waitForSearchUpdate(page, timeout = TIMEOUTS.medium) {
  await page.waitForTimeout(1000); // Debounce delay
  // Wait for either results or no-results message
  await page.waitForSelector(`${SELECTORS.facilityItem}, ${SELECTORS.noResults}`, { timeout });
}

/**
 * Clear all filters and wait for update
 */
export async function clearAllFilters(page) {
  const clearBtn = page.locator(SELECTORS.clearFiltersBtn);
  if (await clearBtn.isVisible()) {
    await clearBtn.click();
    await waitForSearchUpdate(page);
  }
}

/**
 * Get facility count from results
 */
export async function getFacilityCount(page) {
  return await page.locator(SELECTORS.facilityItem).count();
}

/**
 * Apply province filter
 */
export async function selectProvince(page, province) {
  await page.locator(SELECTORS.provinceSelect).selectOption(province);
  await waitForSearchUpdate(page);
}

/**
 * Apply search query
 */
export async function performSearch(page, query) {
  const searchInput = page.locator(SELECTORS.searchInput);
  await searchInput.clear();
  await searchInput.fill(query);
  await waitForSearchUpdate(page);
}

/**
 * Check if facility type checkbox exists and select it
 */
export async function selectFacilityType(page, index = 0) {
  const checkboxes = page.locator(SELECTORS.typeCheckbox);
  const count = await checkboxes.count();
  
  if (count > index) {
    await checkboxes.nth(index).check();
    await waitForSearchUpdate(page);
    return true;
  }
  return false;
}

/**
 * Get text content from element or return empty string
 */
export async function getTextContent(locator) {
  try {
    return await locator.textContent() || '';
  } catch {
    return '';
  }
}

/**
 * Check if element is visible without throwing error
 */
export async function isVisible(locator) {
  try {
    return await locator.isVisible();
  } catch {
    return false;
  }
}

/**
 * Wait for map to be loaded and interactive
 */
export async function waitForMapLoad(page) {
  await page.waitForSelector(SELECTORS.mapContainer, { timeout: TIMEOUTS.long });
  await page.waitForSelector(SELECTORS.mapMarker, { timeout: TIMEOUTS.long });
}

/**
 * Check console for specific error types
 */
export function setupConsoleMonitoring(page) {
  const consoleMessages = {
    errors: [],
    warnings: [],
    logs: []
  };
  
  page.on('console', (msg) => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'error') {
      consoleMessages.errors.push(text);
    } else if (type === 'warning') {
      consoleMessages.warnings.push(text);
    } else {
      consoleMessages.logs.push(text);
    }
  });
  
  return consoleMessages;
}

/**
 * Filter critical errors (ignore known harmless errors)
 */
export function filterCriticalErrors(errors) {
  return errors.filter(error => 
    !error.includes('React DevTools') && 
    !error.includes('Download the React DevTools') &&
    !error.includes('favicon.ico') &&
    !error.includes('chrome-extension')
  );
}

/**
 * Take screenshot with timestamp
 */
export async function takeTimestampedScreenshot(page, name) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({ 
    path: `test-results/screenshots/${name}-${timestamp}.png`,
    fullPage: true 
  });
}

/**
 * Simulate slow network for performance testing
 */
export async function simulateSlowNetwork(page) {
  await page.route('**/*', async route => {
    await new Promise(resolve => setTimeout(resolve, 100)); // 100ms delay
    route.continue();
  });
}

/**
 * Mock API responses for testing error states
 */
export async function mockAPIError(page, endpoint = '**/rest/v1/kuruluslar*') {
  await page.route(endpoint, route => {
    route.abort();
  });
}

/**
 * Mock successful API responses with test data
 */
export async function mockAPISuccess(page, testData) {
  await page.route('**/rest/v1/kuruluslar*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(testData)
    });
  });
}

export default {
  SELECTORS,
  TIMEOUTS,
  TEST_DATA,
  waitForPageLoad,
  waitForSearchUpdate,
  clearAllFilters,
  getFacilityCount,
  selectProvince,
  performSearch,
  selectFacilityType,
  getTextContent,
  isVisible,
  waitForMapLoad,
  setupConsoleMonitoring,
  filterCriticalErrors,
  takeTimestampedScreenshot,
  simulateSlowNetwork,
  mockAPIError,
  mockAPISuccess
};
