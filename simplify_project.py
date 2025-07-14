#!/usr/bin/env python3
"""
Proje Basitleştirme - Gereksiz dosyaları temizle ve basit yapı oluştur
"""
import os
import shutil
import json

def create_simple_structure():
    """Basit ve fonksiyonel proje yapısı oluştur"""
    
    print("🧹 Proje basitleştirme başlıyor...")
    
    # Gereksiz dosyaları listele
    files_to_remove = [
        'add_missing_province.py',
        'debug_cankiri.py', 
        'debug_il_kodu.py',
        'debug_unicode.py',
        'deep_search_cankiri.py',
        'fix_cankiri.py',
        'clean_all_data.py',
        'final_deploy_check.py',
        'quick_syntax_check.py',
        'test_data_scripts.py',
        'temp_cankiri_results.json',
        'temp_debug.xls',
        'temp_function.py',
        'temp_stats.py',
        'test.html',
        'test_char.py',
        'test_results.json',
        'test_results.md',
        'pglite-debug.log',
        'fetch_trhastane.log',
        'fetch_universite_hastaneleri.log',
        'index-simple.html',
        'VISUAL_IMPROVEMENTS_REPORT.md',
        'FINAL_DURUM_RAPORU.md',
        'DEPLOY_REPORT.md'
    ]
    
    # Gereksiz klasörleri listele  
    dirs_to_remove = [
        'css',
        'web',
        'public',
        'assets',
        '__pycache__'
    ]
    
    # Dosyaları temizle
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"  ❌ {file}")
    
    # Klasörleri temizle
    for dir in dirs_to_remove:
        if os.path.exists(dir):
            shutil.rmtree(dir)
            print(f"  📁❌ {dir}/")
    
    # Basit klasör yapısını oluştur
    os.makedirs('src', exist_ok=True)
    os.makedirs('public', exist_ok=True)
    
    print("\n📁 Basit klasör yapısı:")
    print("├── data/                    # Veri dosyaları")
    print("├── src/                     # Kaynak kodlar")
    print("├── scripts/                 # Veri işleme scriptleri")
    print("├── styles/                  # CSS dosyaları") 
    print("├── js/                      # JavaScript dosyaları")
    print("├── public/                  # Deploy dosyaları")
    print("├── index.html               # Ana sayfa")
    print("├── turkey_geo_mapper.py     # Coğrafi eşleme sistemi")
    print("├── analyze_geographic_mapping.py  # Analiz sistemi")
    print("└── README.md                # Dokümantasyon")
    
    return True

def optimize_main_files():
    """Ana dosyaları optimize et"""
    
    print("\n🔧 Ana dosyalar optimize ediliyor...")
    
    # Ana HTML dosyasını basitleştir
    simple_html = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Türkiye Sağlık Kuruluşları</title>
    <link rel="stylesheet" href="styles/main.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
</head>
<body>
    <!-- Top App Bar -->
    <header class="top-app-bar">
        <div class="top-app-bar-content">
            <div style="display: flex; align-items: center;">
                <span class="material-symbols-outlined leading-icon">local_hospital</span>
                <h1 class="headline-small">Türkiye Sağlık Kuruluşları</h1>
            </div>
            <div class="top-app-bar-actions">
                <button class="icon-button" id="theme-toggle" title="Tema Değiştir">
                    <span class="material-symbols-outlined">dark_mode</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="container">
                <div class="hero-content">
                    <h2 class="display-small">Türkiye Sağlık Kuruluşları</h2>
                    <p class="body-large">Türkiye'deki tüm sağlık kuruluşlarına kolayca ulaşın</p>
                    <div class="stats-cards">
                        <div class="stat-card">
                            <span class="stat-number" id="total-institutions">-</span>
                            <span class="stat-label">Toplam Kurum</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">81</span>
                            <span class="stat-label">İl</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number" id="total-types">-</span>
                            <span class="stat-label">Kurum Tipi</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Search Section -->
        <section class="search-section">
            <div class="container">
                <div class="search-container">
                    <div class="search-bar">
                        <span class="material-symbols-outlined leading-icon">search</span>
                        <input type="text" class="search-input" id="search-input" placeholder="Hastane adı, il veya ilçe arayın...">
                    </div>
                    
                    <div class="filter-section">
                        <div class="filter-group">
                            <span class="filter-label">Kurum Tipi:</span>
                            <div class="chip-group" id="type-filters"></div>
                        </div>
                        
                        <div class="filter-group">
                            <span class="filter-label">İl:</span>
                            <div class="chip-group" id="province-filters"></div>
                        </div>
                        
                        <button class="filter-clear-btn" id="clear-filters" style="display: none;">
                            <span class="material-symbols-outlined">clear</span>
                            Filtreleri Temizle
                        </button>
                    </div>
                </div>
            </div>
        </section>

        <!-- Results Section -->
        <section class="results-section">
            <div class="container">
                <div class="results-header">
                    <div class="results-count" id="results-count">Yükleniyor...</div>
                    <div style="display: flex; gap: 16px; align-items: center;">
                        <select class="sort-select" id="sort-select">
                            <option value="name">Ada Göre</option>
                            <option value="province">İle Göre</option>
                            <option value="type">Türe Göre</option>
                        </select>
                    </div>
                </div>
                
                <div class="loading-spinner" id="loading">
                    <div class="spinner"></div>
                    <span>Veriler yükleniyor...</span>
                </div>
                
                <div class="results-grid" id="results-grid"></div>
                
                <div class="no-results" id="no-results" style="display: none;">
                    <span class="material-symbols-outlined">search_off</span>
                    <h3>Sonuç bulunamadı</h3>
                    <p>Arama kriterlerinizi değiştirip tekrar deneyin.</p>
                </div>
            </div>
        </section>
    </main>

    <script src="js/app.js"></script>
</body>
</html>'''

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(simple_html)
    
    print("  ✅ index.html basitleştirildi")
    
    # Package.json basitleştir
    simple_package = {
        "name": "tursakur",
        "version": "1.0.0",
        "description": "Türkiye Sağlık Kuruluşları Veritabanı",
        "main": "index.html",
        "scripts": {
            "build": "python scripts/process_data.py",
            "dev": "python -m http.server 8000",
            "deploy": "firebase deploy"
        },
        "keywords": ["türkiye", "sağlık", "hastane", "database"],
        "author": "TURSAKUR",
        "license": "MIT"
    }
    
    with open('package.json', 'w', encoding='utf-8') as f:
        json.dump(simple_package, f, indent=2, ensure_ascii=False)
    
    print("  ✅ package.json basitleştirildi")

def create_optimized_js():
    """Optimize edilmiş JavaScript dosyası oluştur"""
    
    optimized_js = '''// Türkiye Sağlık Kuruluşları - Ana Uygulama
class HealthInstitutionsApp {
    constructor() {
        this.data = [];
        this.filteredData = [];
        this.filters = {
            search: '',
            type: '',
            province: ''
        };
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.createFilters();
        this.renderResults();
        this.hideLoading();
    }

    async loadData() {
        try {
            const response = await fetch('data/turkiye_saglik_kuruluslari.json');
            const result = await response.json();
            this.data = result.kurumlar || [];
            this.filteredData = [...this.data];
            this.updateStats(result.metadata);
        } catch (error) {
            console.error('Veri yüklenirken hata:', error);
            this.showError('Veriler yüklenemedi');
        }
    }

    updateStats(metadata) {
        document.getElementById('total-institutions').textContent = metadata.total_kurumlar || this.data.length;
        document.getElementById('total-types').textContent = this.getUniqueTypes().length;
    }

    setupEventListeners() {
        // Arama
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.filters.search = e.target.value;
            this.applyFilters();
        });

        // Sıralama
        document.getElementById('sort-select').addEventListener('change', (e) => {
            this.sortResults(e.target.value);
        });

        // Filtreleri temizle
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });

        // Tema değiştirici
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });
    }

    createFilters() {
        this.createTypeFilters();
        this.createProvinceFilters();
    }

    createTypeFilters() {
        const types = this.getUniqueTypes();
        const container = document.getElementById('type-filters');
        
        types.forEach(type => {
            const count = this.data.filter(item => item.kurum_tipi === type).length;
            const chip = this.createFilterChip(type, count, 'type');
            container.appendChild(chip);
        });
    }

    createProvinceFilters() {
        const provinces = this.getUniqueProvinces();
        const container = document.getElementById('province-filters');
        
        provinces.slice(0, 10).forEach(province => { // İlk 10 il
            const count = this.data.filter(item => item.il_adi === province).length;
            const chip = this.createFilterChip(province, count, 'province');
            container.appendChild(chip);
        });
    }

    createFilterChip(text, count, type) {
        const chip = document.createElement('button');
        chip.className = 'filter-chip';
        chip.dataset.filter = type;
        chip.dataset.value = text;
        chip.innerHTML = `${text} <span class="chip-count">${count}</span>`;
        
        chip.addEventListener('click', () => {
            this.toggleFilter(type, text, chip);
        });
        
        return chip;
    }

    toggleFilter(type, value, element) {
        if (this.filters[type] === value) {
            this.filters[type] = '';
            element.classList.remove('active');
        } else {
            // Aynı tip filtreleri temizle
            document.querySelectorAll(`[data-filter="${type}"]`).forEach(chip => {
                chip.classList.remove('active');
            });
            
            this.filters[type] = value;
            element.classList.add('active');
        }
        
        this.applyFilters();
        this.updateClearButton();
    }

    applyFilters() {
        this.filteredData = this.data.filter(item => {
            const searchMatch = !this.filters.search || 
                item.kurum_adi.toLowerCase().includes(this.filters.search.toLowerCase()) ||
                item.il_adi.toLowerCase().includes(this.filters.search.toLowerCase()) ||
                item.ilce_adi.toLowerCase().includes(this.filters.search.toLowerCase());
            
            const typeMatch = !this.filters.type || item.kurum_tipi === this.filters.type;
            const provinceMatch = !this.filters.province || item.il_adi === this.filters.province;
            
            return searchMatch && typeMatch && provinceMatch;
        });
        
        this.renderResults();
        this.updateResultsCount();
    }

    renderResults() {
        const container = document.getElementById('results-grid');
        const noResults = document.getElementById('no-results');
        
        if (this.filteredData.length === 0) {
            container.style.display = 'none';
            noResults.style.display = 'block';
            return;
        }
        
        container.style.display = 'grid';
        noResults.style.display = 'none';
        
        container.innerHTML = this.filteredData.map(item => this.createInstitutionCard(item)).join('');
    }

    createInstitutionCard(item) {
        return `
            <div class="institution-card">
                <div class="card-header">
                    <span class="institution-type">${this.formatType(item.kurum_tipi)}</span>
                </div>
                <h3 class="institution-name">${item.kurum_adi}</h3>
                <div class="institution-location">
                    <span class="material-symbols-outlined">location_on</span>
                    <span>${item.il_adi} / ${item.ilce_adi}</span>
                </div>
                ${item.adres ? `<div class="institution-address">
                    <span class="material-symbols-outlined">home</span>
                    <span>${item.adres}</span>
                </div>` : ''}
                <div class="card-actions">
                    ${item.telefon ? `<button class="action-button" onclick="window.open('tel:${item.telefon}')">
                        <span class="material-symbols-outlined">call</span>
                        Ara
                    </button>` : ''}
                    ${item.web_sitesi ? `<button class="action-button" onclick="window.open('${item.web_sitesi}', '_blank')">
                        <span class="material-symbols-outlined">language</span>
                        Web
                    </button>` : ''}
                </div>
            </div>
        `;
    }

    formatType(type) {
        const types = {
            'DEVLET_HASTANESI': 'Devlet Hastanesi',
            'OZEL_HASTANE': 'Özel Hastane',
            'UNIVERSITE_HASTANESI': 'Üniversite Hastanesi',
            'GENEL': 'Genel'
        };
        return types[type] || type;
    }

    getUniqueTypes() {
        return [...new Set(this.data.map(item => item.kurum_tipi))].sort();
    }

    getUniqueProvinces() {
        return [...new Set(this.data.map(item => item.il_adi))].sort();
    }

    sortResults(criteria) {
        this.filteredData.sort((a, b) => {
            switch (criteria) {
                case 'name':
                    return a.kurum_adi.localeCompare(b.kurum_adi, 'tr');
                case 'province':
                    return a.il_adi.localeCompare(b.il_adi, 'tr');
                case 'type':
                    return a.kurum_tipi.localeCompare(b.kurum_tipi, 'tr');
                default:
                    return 0;
            }
        });
        this.renderResults();
    }

    clearFilters() {
        this.filters = { search: '', type: '', province: '' };
        document.getElementById('search-input').value = '';
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.classList.remove('active');
        });
        this.applyFilters();
        this.updateClearButton();
    }

    updateClearButton() {
        const hasFilters = this.filters.search || this.filters.type || this.filters.province;
        document.getElementById('clear-filters').style.display = hasFilters ? 'flex' : 'none';
    }

    updateResultsCount() {
        document.getElementById('results-count').textContent = 
            `${this.filteredData.length} kurum gösteriliyor`;
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    showError(message) {
        document.getElementById('loading').innerHTML = `
            <span class="material-symbols-outlined">error</span>
            <span>${message}</span>
        `;
    }

    toggleTheme() {
        // Tema değiştirme fonksiyonu - gelecekte implement edilecek
        console.log('Tema değiştirme özelliği gelecekte eklenecek');
    }
}

// Uygulama başlat
document.addEventListener('DOMContentLoaded', () => {
    new HealthInstitutionsApp();
});'''

    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(optimized_js)
    
    print("  ✅ js/app.js optimize edildi")

if __name__ == "__main__":
    if create_simple_structure():
        optimize_main_files()
        create_optimized_js()
        print("\n🎉 Proje başarıyla basitleştirildi!")
        print("\n📝 Sonraki adımlar:")
        print("1. python scripts/process_data.py  # Veri güncelle")
        print("2. firebase deploy  # Deploy et")
