// Türkiye Sağlık Kuruluşları - Ana Uygulama
class HealthInstitutionsApp {
    constructor() {
        this.data = [];
        this.filteredData = [];
        this.filters = {
            search: '',
            type: '',
            province: '',
            district: ''
        };
        this.init();
    }

    async init() {
        this.initializeTheme(); // Tema başlatma
        await this.loadData();
        this.setupEventListeners();
        this.createFilters();
        // Başlangıçta sonuçları gösterme - sadece filtreleme sonrası göster
        this.hideLoading();
        this.showInitialMessage();
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
            this.updateActiveFilters();
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
        this.createLocationSelectors();
    }

    createTypeFilters() {
        const types = this.getUniqueTypes();
        const container = document.getElementById('type-filters');
        
        types.forEach(type => {
            const count = this.data.filter(item => item.kurum_tipi === type).length;
            const chip = this.createFilterChip(this.formatTypeName(type), count, 'type', type);
            container.appendChild(chip);
        });
    }

    createLocationSelectors() {
        // İl seçici doldur
        const provinces = this.getUniqueProvinces();
        const provinceSelect = document.getElementById('province-select');
        
        provinces.forEach(province => {
            const option = document.createElement('option');
            option.value = province;
            option.textContent = province;
            provinceSelect.appendChild(option);
        });
        
        // İl seçici event listener
        provinceSelect.addEventListener('change', (e) => {
            this.onProvinceChange(e.target.value);
        });
        
        // İlçe seçici event listener
        document.getElementById('district-select').addEventListener('change', (e) => {
            this.onDistrictChange(e.target.value);
        });
    }
    
    onProvinceChange(selectedProvince) {
        const districtContainer = document.getElementById('district-filter-container');
        const districtSelect = document.getElementById('district-select');
        
        // İlçe seçiciyi temizle
        districtSelect.innerHTML = '<option value="">Tüm İlçeler</option>';
        
        if (selectedProvince) {
            // Seçili ile ait ilçeleri getir
            const districts = this.getDistrictsByProvince(selectedProvince);
            
            districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district;
                option.textContent = district;
                districtSelect.appendChild(option);
            });
            
            // İlçe seçiciyi göster
            districtContainer.style.display = 'block';
            
            // İl filtresini uygula
            this.filters.province = selectedProvince;
            this.filters.district = '';
        } else {
            // İlçe seçiciyi gizle
            districtContainer.style.display = 'none';
            this.filters.province = '';
            this.filters.district = '';
        }
        
        this.applyFilters();
        this.updateActiveFilters();
    }
    
    onDistrictChange(selectedDistrict) {
        this.filters.district = selectedDistrict;
        this.applyFilters();
        this.updateActiveFilters();
    }
    
    getDistrictsByProvince(province) {
        const districts = [...new Set(
            this.data
                .filter(item => item.il_adi === province)
                .map(item => item.ilce_adi)
        )].sort();
        return districts;
    }

    createFilterChip(text, count, type, originalValue = null) {
        const chip = document.createElement('button');
        chip.className = 'filter-chip';
        chip.dataset.filter = type;
        chip.dataset.value = originalValue || text;
        
        // İkon ekle (kurum tipi için)
        let icon = '';
        if (type === 'type') {
            const typeValue = originalValue || text;
            if (typeValue.includes('DEVLET')) icon = '<span class="material-symbols-outlined">local_hospital</span>';
            else if (typeValue.includes('OZEL')) icon = '<span class="material-symbols-outlined">business</span>';
            else if (typeValue.includes('UNIVERSITE')) icon = '<span class="material-symbols-outlined">school</span>';
            else if (typeValue.includes('AGIZ') || typeValue.includes('DIS')) icon = '<span class="material-symbols-outlined">dentistry</span>';
            else if (typeValue.includes('EGITIM') || typeValue.includes('ARASTIRMA')) icon = '<span class="material-symbols-outlined">science</span>';
            else icon = '<span class="material-symbols-outlined">healing</span>';
        }
        
        chip.innerHTML = `${icon}${text} <span class="chip-count">${count}</span>`;
        
        chip.addEventListener('click', () => {
            this.toggleFilter(type, originalValue || text, chip);
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
        this.updateActiveFilters();
    }

    applyFilters() {
        this.filteredData = this.data.filter(item => {
            const searchMatch = !this.filters.search || 
                item.kurum_adi.toLowerCase().includes(this.filters.search.toLowerCase()) ||
                item.il_adi.toLowerCase().includes(this.filters.search.toLowerCase()) ||
                item.ilce_adi.toLowerCase().includes(this.filters.search.toLowerCase());
            
            const typeMatch = !this.filters.type || item.kurum_tipi === this.filters.type;
            const provinceMatch = !this.filters.province || item.il_adi === this.filters.province;
            const districtMatch = !this.filters.district || item.ilce_adi === this.filters.district;
            
            return searchMatch && typeMatch && provinceMatch && districtMatch;
        });
        
        this.renderResults();
        this.updateResultsCount();
    }

    renderResults() {
        const container = document.getElementById('results-grid');
        const noResults = document.getElementById('no-results');
        
        // Eğer hiçbir filtre yoksa başlangıç mesajını göster
        const hasAnyFilter = this.filters.search || this.filters.type || this.filters.province || this.filters.district;
        
        if (!hasAnyFilter) {
            this.showInitialMessage();
            return;
        }
        
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
        const typeClass = this.getTypeClass(item.kurum_tipi);
        return `
            <div class="institution-card">
                <div class="card-header">
                    <span class="institution-type" data-type="${item.kurum_tipi}">${this.formatType(item.kurum_tipi)}</span>
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

    getTypeClass(type) {
        const typeMap = {
            'DEVLET_HASTANESI': 'devlet-hastanesi',
            'OZEL_HASTANE': 'ozel-hastane', 
            'UNIVERSITE_HASTANESI': 'universite-hastanesi',
            'GENEL': 'genel'
        };
        return typeMap[type] || 'genel';
    }

    formatType(type) {
        // _ karakterlerini kaldır ve düzgün formatlama
        const typeMap = {
            'DEVLET_HASTANESI': 'Devlet Hastanesi',
            'OZEL_HASTANE': 'Özel Hastane', 
            'UNIVERSITE_HASTANESI': 'Üniversite Hastanesi',
            'AGIZ_DIS_SAGLIGI_MERKEZI': 'Ağız ve Diş Sağlığı Merkezi',
            'EGITIM_ARASTIRMA_HASTANESI': 'Eğitim ve Araştırma Hastanesi',
            'GENEL': 'Genel Sağlık Kurumu'
        };
        
        // Eğer type map'te varsa formatlanmış halini döndür
        if (typeMap[type]) {
            return typeMap[type];
        }
        
        // Yoksa _ karakterlerini boşlukla değiştir ve kelime başlarını büyük harf yap
        return type.replace(/_/g, ' ')
                   .toLowerCase()
                   .split(' ')
                   .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                   .join(' ');
    }

    formatTypeName(type) {
        return this.formatType(type);
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
        this.filters = { search: '', type: '', province: '', district: '' };
        document.getElementById('search-input').value = '';
        document.getElementById('province-select').value = '';
        document.getElementById('district-select').value = '';
        document.getElementById('district-filter-container').style.display = 'none';
        
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.classList.remove('active');
        });
        
        this.applyFilters();
        this.updateActiveFilters();
    }

    updateClearButton() {
        const hasFilters = this.filters.search || this.filters.type || this.filters.province;
        document.getElementById('clear-filters').style.display = hasFilters ? 'flex' : 'none';
    }

    updateResultsCount(customMessage = null) {
        const resultsCountElement = document.getElementById('results-count');
        if (customMessage) {
            resultsCountElement.textContent = customMessage;
        } else {
            resultsCountElement.textContent = `${this.filteredData.length} kurum gösteriliyor`;
        }
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
        const body = document.body;
        const themeToggle = document.getElementById('theme-toggle');
        const logo = document.getElementById('app-logo');
        const icon = themeToggle.querySelector('.material-symbols-outlined');
        
        // Toggle dark mode class
        const isDarkMode = body.classList.toggle('dark-mode');
        
        // Update theme icon
        icon.textContent = isDarkMode ? 'light_mode' : 'dark_mode';
        
        // Update logo based on theme - her zaman color logo kullan
        logo.src = 'assets/logos/TURSAKUR-Color.png';
        if (isDarkMode) {
            body.style.colorScheme = 'dark';
        } else {
            body.style.colorScheme = 'light';
        }
        
        // Save theme preference
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        
        // Add visual feedback
        themeToggle.style.transform = 'scale(0.9)';
        setTimeout(() => {
            themeToggle.style.transform = 'scale(1)';
        }, 150);
    }

    initializeTheme() {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const shouldUseDark = savedTheme === 'dark' || (!savedTheme && prefersDark);
        
        if (shouldUseDark) {
            document.body.classList.add('dark-mode');
            document.body.style.colorScheme = 'dark';
            document.getElementById('app-logo').src = 'assets/logos/TURSAKUR-Color.png'; // Her zaman color logo
            document.querySelector('#theme-toggle .material-symbols-outlined').textContent = 'light_mode';
        } else {
            document.getElementById('app-logo').src = 'assets/logos/TURSAKUR-Color.png'; // Her zaman color logo
        }
    }

    showInitialMessage() {
        const container = document.getElementById('results-grid');
        const noResults = document.getElementById('no-results');
        
        container.innerHTML = `
            <div class="initial-message">
                <div class="initial-content">
                    <span class="material-symbols-outlined">search</span>
                    <h3>Arama Yapın veya Filtre Seçin</h3>
                    <p>Türkiye'deki sağlık kuruluşlarını aramak için yukarıdaki arama kutusunu kullanın veya filtreleri seçin.</p>
                    <div class="quick-actions">
                        <button class="quick-action-btn" onclick="app.quickFilter('type', 'DEVLET_HASTANESI')">
                            Devlet Hastaneleri
                        </button>
                        <button class="quick-action-btn" onclick="app.quickFilter('type', 'OZEL_HASTANE')">
                            Özel Hastaneler
                        </button>
                        <button class="quick-action-btn" onclick="app.quickFilter('type', 'UNIVERSITE_HASTANESI')">
                            Üniversite Hastaneleri
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        noResults.style.display = 'none';
        this.updateResultsCount('Arama yapmak için filtreleri kullanın');
    }

    quickFilter(type, value) {
        this.filters[type] = value;
        
        // Aktif filter chip'ini güncelle
        document.querySelectorAll(`[data-filter="${type}"]`).forEach(chip => {
            chip.classList.remove('active');
            if (chip.dataset.value === value) {
                chip.classList.add('active');
            }
        });
        
        this.applyFilters();
        this.updateClearButton();
    }

    updateActiveFilters() {
        const activeFiltersContainer = document.getElementById('active-filters');
        const activeFilterChips = document.getElementById('active-filter-chips');
        
        // Mevcut chip'leri temizle
        activeFilterChips.innerHTML = '';
        
        let hasActiveFilters = false;
        
        // Tip filtresi
        if (this.filters.type) {
            const chip = document.createElement('div');
            chip.className = 'active-filter-chip';
            chip.innerHTML = `
                ${this.formatType(this.filters.type)}
                <span class="remove-filter material-symbols-outlined" onclick="app.removeFilter('type')">close</span>
            `;
            activeFilterChips.appendChild(chip);
            hasActiveFilters = true;
        }
        
        // İl filtresi
        if (this.filters.province) {
            const chip = document.createElement('div');
            chip.className = 'active-filter-chip';
            chip.innerHTML = `
                ${this.filters.province}
                <span class="remove-filter material-symbols-outlined" onclick="app.removeFilter('province')">close</span>
            `;
            activeFilterChips.appendChild(chip);
            hasActiveFilters = true;
        }
        
        // İlçe filtresi
        if (this.filters.district) {
            const chip = document.createElement('div');
            chip.className = 'active-filter-chip';
            chip.innerHTML = `
                ${this.filters.district}
                <span class="remove-filter material-symbols-outlined" onclick="app.removeFilter('district')">close</span>
            `;
            activeFilterChips.appendChild(chip);
            hasActiveFilters = true;
        }
        
        // Arama filtresi
        if (this.filters.search) {
            const chip = document.createElement('div');
            chip.className = 'active-filter-chip';
            chip.innerHTML = `
                "${this.filters.search}"
                <span class="remove-filter material-symbols-outlined" onclick="app.removeFilter('search')">close</span>
            `;
            activeFilterChips.appendChild(chip);
            hasActiveFilters = true;
        }
        
        // Active filters bölümünü göster/gizle
        activeFiltersContainer.style.display = hasActiveFilters ? 'block' : 'none';
    }
    
    removeFilter(filterType) {
        this.filters[filterType] = '';
        
        if (filterType === 'search') {
            document.getElementById('search-input').value = '';
        } else if (filterType === 'province') {
            document.getElementById('province-select').value = '';
            document.getElementById('district-filter-container').style.display = 'none';
            this.filters.district = '';
        } else if (filterType === 'district') {
            document.getElementById('district-select').value = '';
        } else if (filterType === 'type') {
            // Type filter chip'ini pasif yap
            document.querySelectorAll('[data-filter="type"]').forEach(chip => {
                chip.classList.remove('active');
            });
        }
        
        this.applyFilters();
        this.updateActiveFilters();
    }
}

// Uygulama başlat
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new HealthInstitutionsApp();
});