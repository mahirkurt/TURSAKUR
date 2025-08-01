# TURSAKUR 2.0 - Test Documentation

## 🧪 Playwright Test Suite

### Test Kapsamı

#### 1. **Homepage Tests** (`tests/homepage.spec.js`)
- ✅ Sayfa yükleme testi
- ✅ UI komponentleri kontrolü  
- ✅ Responsive design testi
- ✅ Console hata kontrolü
- ✅ Loading state testi

#### 2. **Database Integration Tests** (`tests/database.spec.js`)
- ✅ Supabase API bağlantısı
- ✅ Veri çekme fonksiyonelliği
- ✅ İl/kurum tipi listeleme
- ✅ API hata yönetimi
- ✅ Data consistency validation

#### 3. **Filter & Search Tests** (`tests/filters.spec.js`)
- ✅ Arama fonksiyonelliği
- ✅ İl/ilçe filtreleme
- ✅ Kurum tipi filtreleme
- ✅ Kombinasyon filtreleri
- ✅ Filtre temizleme

#### 4. **Map Integration Tests** (`tests/map.spec.js`)
- ✅ Leaflet map yüklenme
- ✅ Marker gösterimi
- ✅ Popup interactions
- ✅ Map-filter synchronization
- ✅ Performance testing

#### 5. **Performance & Accessibility Tests** (`tests/performance.spec.js`)
- ✅ Sayfa yükleme hızı
- ✅ Core Web Vitals
- ✅ Accessibility compliance
- ✅ Keyboard navigation
- ✅ Screen reader support

### Test Commands

```bash
# Tüm testleri çalıştır
npm run test

# Browser görünür şekilde test
npm run test:headed

# Debug mode
npm run test:debug

# UI mode (interactive)
npm run test:ui

# Test raporu görüntüle
npm run test:report

# Playwright browsers kur
npm run test:install

# Test code generation
npm run test:codegen

# Smoke tests (sadece kritik testler)
npm run test:smoke

# CI için optimize edilmiş
npm run test:ci
```

### Test Data Attributes

Test'lerin doğru çalışması için aşağıdaki `data-testid` attribute'ları kullanılmıştır:

#### Core Components
- `data-testid="filter-panel"` - Filter panel container
- `data-testid="facility-item"` - Her sağlık kuruluşu kartı
- `data-testid="results-list"` - Sonuçlar listesi container
- `data-testid="loading"` - Loading spinner
- `data-testid="no-results"` - Sonuç bulunamadı mesajı
- `data-testid="clear-filters"` - Filtreleri temizle butonu

#### CSS Classes (Test Helper)
- `.facility-name` - Kurum adı
- `.facility-type` - Kurum tipi
- `.facility-location` - Konum bilgisi

### Supabase Test Configuration

Test'ler production Supabase instance'ını kullanmaktadır:
- **URL**: `https://moamwmxcpgjvyyawlygw.supabase.co`
- **Table**: `kuruluslar`
- **Test Data**: 3+ kayıt mevcut

### Test Environment

#### Local Development
```bash
# Development server başlat
npm run dev

# Parallel window'da testleri çalıştır
npm run test:headed
```

#### CI/CD (GitHub Actions)
- **Workflow**: `.github/workflows/playwright.yml`
- **Browsers**: Chromium, Firefox, WebKit, Mobile
- **Reports**: HTML report + artifacts
- **Lighthouse**: Performance monitoring

### Browser Support

| Browser | Desktop | Mobile | CI/CD |
|---------|---------|--------|-------|
| Chromium | ✅ | ✅ | ✅ |
| Firefox | ✅ | ❌ | ✅ |
| WebKit (Safari) | ✅ | ✅ | ✅ |

### Performance Benchmarks

#### Expected Metrics
- **Page Load**: < 5 seconds
- **First Contentful Paint**: < 2.5 seconds
- **Large Dataset Render**: < 10 seconds
- **Map Load**: < 15 seconds

#### Accessibility Standards
- **WCAG 2.1 AA Compliance**
- **Keyboard Navigation Support**
- **Screen Reader Compatibility**
- **Color Contrast Requirements**

### Test Utilities

#### Helper Functions (`tests/helpers/test-utils.js`)
```javascript
// Common operations
await waitForPageLoad(page);
await waitForSearchUpdate(page);
await clearAllFilters(page);
await selectProvince(page, 'İstanbul');
await performSearch(page, 'hastane');

// Error monitoring
const consoleMessages = setupConsoleMonitoring(page);
const criticalErrors = filterCriticalErrors(consoleMessages.errors);

// Performance testing
await simulateSlowNetwork(page);
await takeTimestampedScreenshot(page, 'test-name');
```

### Debugging

#### Test Failures
```bash
# Debug specific test
npx playwright test tests/homepage.spec.js --debug

# Run with trace
npx playwright test --trace on

# Generate report after failure
npm run test:report
```

#### Common Issues
1. **Timeout Errors**: Supabase API yavaş yanıt veriyorsa timeout artırılabilir
2. **Selector Not Found**: UI component'leri data-testid attribute'ları eksikse
3. **Network Errors**: CI'da Supabase credentials eksikse

### Continuous Integration

#### GitHub Actions
- **Trigger**: Push to main/develop, Pull requests
- **Parallel Jobs**: Full tests, Lighthouse, Smoke tests
- **Artifacts**: Test reports, screenshots, videos
- **Notifications**: Slack integration (optional)

#### Quality Gates
- ✅ All tests pass
- ✅ No critical console errors
- ✅ Performance benchmarks met
- ✅ Accessibility compliance

### Future Enhancements

#### Planned Tests
- [ ] End-to-end user journeys
- [ ] API integration testing
- [ ] Cross-browser visual regression
- [ ] Load testing with large datasets
- [ ] Mobile-specific interactions

#### Test Infrastructure
- [ ] Docker containers for consistent environments
- [ ] Parallel test execution optimization
- [ ] Test data management
- [ ] Automated visual testing

---

## 🎯 Test Execution Summary

**TURSAKUR 2.0** artık comprehensive test suite ile donatılmıştır:

- **5 Test Suites** - Homepage, Database, Filters, Map, Performance
- **30+ Test Cases** - Kritik fonksiyonellik coverage
- **Multiple Browsers** - Desktop + Mobile support
- **CI/CD Integration** - GitHub Actions workflow
- **Performance Monitoring** - Core Web Vitals tracking
- **Accessibility Testing** - WCAG compliance

Test'ler production Supabase ile entegre çalışarak gerçek veri akışını doğrular ve sistem güvenilirliğini sağlar.
