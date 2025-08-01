# TURSAKUR 2.0 - Playwright Test Suite

## 📋 Test Kapsamı

Bu test suite'i TURSAKUR 2.0 uygulamasının tüm kritik fonksiyonlarını kapsar:

### 🏠 Homepage Tests (`tests/homepage.spec.js`)
- ✅ Sayfa yükleme başarısı
- ✅ Ana navigasyon komponentleri
- ✅ Console hataları kontrolü
- ✅ Loading state'leri
- ✅ Responsive tasarım (mobile/tablet)

### 🗄️ Database Integration Tests (`tests/database.spec.js`)
- ✅ Supabase API bağlantısı
- ✅ Sağlık kuruluşları veri çekme
- ✅ İl listesi yükleme
- ✅ Kurum tipleri yükleme
- ✅ API hata yönetimi
- ✅ Veri tutarlılığı kontrolü
- ✅ Koordinat verileri doğrulama

### 🔍 Filter & Search Tests (`tests/filters.spec.js`)
- ✅ İsim arama fonksiyonu
- ✅ Lokasyon arama
- ✅ İl filtresi
- ✅ İlçe filtresi
- ✅ Kurum tipi filtreleri
- ✅ Kombinasyon filtreleri
- ✅ Filtre temizleme

### 🗺️ Map Integration Tests (`tests/map.spec.js`)
- ✅ Leaflet harita yükleme
- ✅ Marker gösterimi
- ✅ Popup etkileşimleri
- ✅ Filtre-harita senkronizasyonu
- ✅ Zoom kontrolleri
- ✅ Harita sürükleme
- ✅ Marker clustering
- ✅ Performance testleri

### ⚡ Performance & Accessibility (`tests/performance.spec.js`)
- ✅ Sayfa yükleme süresi (< 5 saniye)
- ✅ Core Web Vitals (FCP < 2.5s)
- ✅ Büyük veri setleri performansı
- ✅ Asset yükleme optimizasyonu
- ✅ Heading hiyerarşisi
- ✅ ARIA labels ve roller
- ✅ Klavye navigasyonu
- ✅ Renk kontrastı
- ✅ Screen reader uyumluluğu

## 🚀 Test Çalıştırma

### Tüm Testler
\`\`\`bash
npm run test
\`\`\`

### Görsel Mod (Headed)
\`\`\`bash
npm run test:headed
\`\`\`

### Debug Modu
\`\`\`bash
npm run test:debug
\`\`\`

### Test UI (İnteraktif)
\`\`\`bash
npm run test:ui
\`\`\`

### Test Raporu
\`\`\`bash
npm run test:report
\`\`\`

### Codegen (Test Kaydetme)
\`\`\`bash
npm run test:codegen
\`\`\`

## 🎯 Test Data Attributes

Tüm UI komponentlerine test-friendly data attributes eklendi:

### Ana Komponentler
- \`data-testid="filter-panel"\` - Filtre paneli
- \`data-testid="results-list"\` - Sonuç listesi
- \`data-testid="stats-panel"\` - İstatistik paneli
- \`data-testid="loading"\` - Yükleme göstergesi

### Facility Items
- \`data-testid="facility-item"\` - Kurum kartları
- \`.facility-name\` - Kurum adı
- \`.facility-type\` - Kurum tipi
- \`.facility-location\` - Konum bilgisi
- \`data-has-coords\` - Koordinat varlığı

### Filtreler
- \`#province-select\` - İl seçici
- \`#district-select\` - İlçe seçici
- \`data-testid="clear-filters"\` - Filtre temizleme
- \`.filter-checkboxes input[type="checkbox"]\` - Tip filtreleri

### States
- \`data-testid="no-results"\` - Sonuç bulunamadı
- \`data-testid="error-message"\` - Hata mesajları
- \`data-testid="total-count"\` - Toplam sayım

## 🔧 Konfigürasyon

### playwright.config.js
- ✅ Multi-browser support (Chrome, Firefox, Safari)
- ✅ Mobile device testing
- ✅ Automatic server startup
- ✅ Screenshot/video on failure
- ✅ HTML ve JSON reports

### Test Environment
- **Base URL**: http://localhost:5173
- **Timeout**: 2 dakika server startup
- **Parallelization**: Tam paralel
- **Retries**: CI'da 2, local'de 0

## 📊 Test Coverage

### Critical Paths
1. **Data Loading Flow**: Supabase → API → UI
2. **Search & Filter Flow**: Input → Processing → Results
3. **Map Integration**: Data → Markers → Interactions
4. **Performance**: Load times, responsiveness
5. **Accessibility**: WCAG compliance

### Browser Matrix
- ✅ **Desktop Chrome** (Primary)
- ✅ **Desktop Firefox** 
- ✅ **Desktop Safari**
- ✅ **Mobile Chrome** (Pixel 5)
- ✅ **Mobile Safari** (iPhone 12)

## 🐛 Common Issues & Solutions

### Test Failures

1. **"Element not found"**
   - Ensure data-testid attributes are correct
   - Check component rendering conditions
   - Verify loading states

2. **"Timeout waiting for element"**
   - Increase timeout for slow API calls
   - Check network connectivity
   - Verify Supabase credentials

3. **"Map not loading"**
   - Ensure Leaflet CSS/JS loaded
   - Check internet connection for map tiles
   - Verify coordinate data

### Environment Issues

1. **Port conflicts**
   - Default: http://localhost:5173
   - Change in playwright.config.js if needed

2. **Supabase connectivity**
   - Verify credentials in .env
   - Check network restrictions
   - Test API endpoints manually

## 📈 CI/CD Integration

GitHub Actions workflow automatically:
- ✅ Installs dependencies
- ✅ Installs Playwright browsers
- ✅ Starts development server
- ✅ Runs all tests
- ✅ Generates reports
- ✅ Artifacts screenshots/videos on failure

## 🎯 Best Practices

### Writing New Tests
1. Use descriptive test names
2. Include proper data-testid attributes
3. Test user workflows, not implementation
4. Handle loading states
5. Use appropriate timeouts

### Debugging
1. Use \`--debug\` flag for step-by-step
2. Use \`--headed\` to see browser
3. Add \`await page.pause()\` for manual inspection
4. Check console logs and network tabs

### Maintenance
1. Update selectors when UI changes
2. Review test coverage regularly
3. Keep test data current
4. Monitor test execution times

---

**TURSAKUR 2.0 Test Suite** - Comprehensive end-to-end testing for reliable production deployment! 🚀
