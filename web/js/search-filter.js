/**
 * Search and Filter Module
 * Arama ve filtreleme işlevlerini yönetir
 */

class SearchFilter {
    constructor() {
        this.searchTerm = '';
        this.selectedCity = '';
        this.selectedDistrict = '';
        this.selectedType = '';
        this.searchTimeout = null;
        this.searchDelay = 300; // ms
    }

    /**
     * Arama ve filtreleme event listener'larını başlat
     */
    init() {
        this.bindEvents();
        this.setupAdvancedSearch();
    }

    /**
     * Event listener'ları bağla
     */
    bindEvents() {
        // Ana arama kutusu
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });

            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch();
                }
            });
        }

        // Arama butonu
        const searchButton = document.getElementById('search-button');
        if (searchButton) {
            searchButton.addEventListener('click', () => {
                this.performSearch();
            });
        }

        // Temizle butonu
        const clearButton = document.getElementById('clear-search');
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearAllFilters();
            });
        }

        // Filtre seçimleri
        const cityFilter = document.getElementById('city-filter');
        if (cityFilter) {
            cityFilter.addEventListener('change', (e) => {
                this.selectedCity = e.target.value;
                dataLoader.updateDistrictFilter(this.selectedCity);
                this.selectedDistrict = ''; // İlçe seçimini sıfırla
                const districtFilter = document.getElementById('district-filter');
                if (districtFilter) districtFilter.value = '';
                this.applyFilters();
            });
        }

        const districtFilter = document.getElementById('district-filter');
        if (districtFilter) {
            districtFilter.addEventListener('change', (e) => {
                this.selectedDistrict = e.target.value;
                this.applyFilters();
            });
        }

        const typeFilter = document.getElementById('type-filter');
        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => {
                this.selectedType = e.target.value;
                this.applyFilters();
            });
        }

        // Gelişmiş arama toggle
        const advancedToggle = document.getElementById('advanced-search-toggle');
        if (advancedToggle) {
            advancedToggle.addEventListener('click', () => {
                this.toggleAdvancedSearch();
            });
        }
    }

    /**
     * Gelişmiş arama panelini ayarla
     */
    setupAdvancedSearch() {
        const advancedPanel = document.getElementById('advanced-search');
        if (advancedPanel) {
            // Panel başlangıçta kapalı
            advancedPanel.style.display = 'none';
        }
    }

    /**
     * Arama işlemini ele al (debounce ile)
     */
    handleSearch(term) {
        this.searchTerm = term;

        // Önceki timeout'u iptal et
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        // Yeni timeout ayarla
        this.searchTimeout = setTimeout(() => {
            this.performSearch();
        }, this.searchDelay);
    }

    /**
     * Arama işlemini gerçekleştir
     */
    performSearch() {
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        this.applyFilters();
    }

    /**
     * Tüm filtreleri uygula
     */
    applyFilters() {
        if (!dataLoader.data) return;

        let filtered = [...dataLoader.data.kurumlar];

        // Metin araması
        if (this.searchTerm.trim()) {
            const searchTerms = this.searchTerm.toLowerCase().trim().split(/\s+/);
            filtered = filtered.filter(kurum => {
                const searchableText = [
                    kurum.kurum_adi,
                    kurum.kurum_tipi,
                    kurum.il_adi,
                    kurum.ilce_adi,
                    kurum.adres
                ].join(' ').toLowerCase();

                return searchTerms.every(term => searchableText.includes(term));
            });
        }

        // İl filtresi
        if (this.selectedCity) {
            filtered = filtered.filter(kurum => kurum.il_adi === this.selectedCity);
        }

        // İlçe filtresi
        if (this.selectedDistrict) {
            filtered = filtered.filter(kurum => kurum.ilce_adi === this.selectedDistrict);
        }

        // Kurum tipi filtresi
        if (this.selectedType) {
            filtered = filtered.filter(kurum => kurum.kurum_tipi === this.selectedType);
        }

        // Sonuçları güncelle
        dataLoader.filteredData = filtered;
        dataLoader.currentPage = 1; // İlk sayfaya dön
        dataLoader.renderResults();

        // Aktif filtreleri göster
        this.updateActiveFilters();
    }

    /**
     * Aktif filtreleri göster
     */
    updateActiveFilters() {
        const activeFiltersContainer = document.getElementById('active-filters');
        if (!activeFiltersContainer) return;

        const activeFilters = [];

        // Arama terimi
        if (this.searchTerm.trim()) {
            activeFilters.push({
                type: 'search',
                label: `Arama: "${this.searchTerm}"`,
                action: () => this.clearSearch()
            });
        }

        // İl filtresi
        if (this.selectedCity) {
            activeFilters.push({
                type: 'city',
                label: `İl: ${this.selectedCity}`,
                action: () => this.clearCityFilter()
            });
        }

        // İlçe filtresi
        if (this.selectedDistrict) {
            activeFilters.push({
                type: 'district',
                label: `İlçe: ${this.selectedDistrict}`,
                action: () => this.clearDistrictFilter()
            });
        }

        // Kurum tipi filtresi
        if (this.selectedType) {
            activeFilters.push({
                type: 'type',
                label: `Tip: ${this.selectedType}`,
                action: () => this.clearTypeFilter()
            });
        }

        // HTML oluştur
        if (activeFilters.length > 0) {
            activeFiltersContainer.innerHTML = `
                <div class="active-filters-header">
                    <span>Aktif Filtreler:</span>
                    <button class="text-button" onclick="searchFilter.clearAllFilters()">
                        Tümünü Temizle
                    </button>
                </div>
                <div class="active-filters-list">
                    ${activeFilters.map((filter, index) => `
                        <div class="filter-chip">
                            <span>${filter.label}</span>
                            <button class="filter-remove" onclick="searchFilter.removeFilter('${filter.type}')" title="Kaldır">
                                <span class="material-symbols-outlined">close</span>
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;
            activeFiltersContainer.style.display = 'block';
        } else {
            activeFiltersContainer.style.display = 'none';
        }
    }

    /**
     * Belirli filtreyi kaldır
     */
    removeFilter(type) {
        switch (type) {
            case 'search':
                this.clearSearch();
                break;
            case 'city':
                this.clearCityFilter();
                break;
            case 'district':
                this.clearDistrictFilter();
                break;
            case 'type':
                this.clearTypeFilter();
                break;
        }
    }

    /**
     * Aramayı temizle
     */
    clearSearch() {
        this.searchTerm = '';
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.value = '';
        this.applyFilters();
    }

    /**
     * İl filtresini temizle
     */
    clearCityFilter() {
        this.selectedCity = '';
        this.selectedDistrict = '';
        const cityFilter = document.getElementById('city-filter');
        const districtFilter = document.getElementById('district-filter');
        
        if (cityFilter) cityFilter.value = '';
        if (districtFilter) {
            districtFilter.value = '';
            districtFilter.disabled = true;
        }
        
        this.applyFilters();
    }

    /**
     * İlçe filtresini temizle
     */
    clearDistrictFilter() {
        this.selectedDistrict = '';
        const districtFilter = document.getElementById('district-filter');
        if (districtFilter) districtFilter.value = '';
        this.applyFilters();
    }

    /**
     * Kurum tipi filtresini temizle
     */
    clearTypeFilter() {
        this.selectedType = '';
        const typeFilter = document.getElementById('type-filter');
        if (typeFilter) typeFilter.value = '';
        this.applyFilters();
    }

    /**
     * Tüm filtreleri temizle
     */
    clearAllFilters() {
        this.searchTerm = '';
        this.selectedCity = '';
        this.selectedDistrict = '';
        this.selectedType = '';

        // UI elementlerini temizle
        const searchInput = document.getElementById('search-input');
        const cityFilter = document.getElementById('city-filter');
        const districtFilter = document.getElementById('district-filter');
        const typeFilter = document.getElementById('type-filter');

        if (searchInput) searchInput.value = '';
        if (cityFilter) cityFilter.value = '';
        if (districtFilter) {
            districtFilter.value = '';
            districtFilter.disabled = true;
        }
        if (typeFilter) typeFilter.value = '';

        this.applyFilters();
    }

    /**
     * Gelişmiş arama panelini aç/kapat
     */
    toggleAdvancedSearch() {
        const advancedPanel = document.getElementById('advanced-search');
        const toggleButton = document.getElementById('advanced-search-toggle');
        const toggleIcon = toggleButton?.querySelector('.material-symbols-outlined');

        if (!advancedPanel) return;

        const isOpen = advancedPanel.style.display === 'block';

        if (isOpen) {
            // Kapat
            advancedPanel.style.display = 'none';
            if (toggleIcon) toggleIcon.textContent = 'expand_more';
            if (toggleButton) toggleButton.setAttribute('aria-expanded', 'false');
        } else {
            // Aç
            advancedPanel.style.display = 'block';
            if (toggleIcon) toggleIcon.textContent = 'expand_less';
            if (toggleButton) toggleButton.setAttribute('aria-expanded', 'true');
        }
    }

    /**
     * Arama önerileri göster
     */
    showSearchSuggestions(term) {
        if (!term.trim() || !dataLoader.data) return;

        // Kurumlar içinde arama yap
        const suggestions = dataLoader.data.kurumlar
            .filter(kurum => 
                kurum.kurum_adi.toLowerCase().includes(term.toLowerCase())
            )
            .slice(0, 5) // İlk 5 sonuç
            .map(kurum => kurum.kurum_adi);

        // Benzersiz önerileri al
        const uniqueSuggestions = [...new Set(suggestions)];

        // Önerileri göster (bu fonksiyon UI'da implement edilecek)
        this.renderSearchSuggestions(uniqueSuggestions);
    }

    /**
     * Arama önerilerini render et
     */
    renderSearchSuggestions(suggestions) {
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (!suggestionsContainer) return;

        if (suggestions.length === 0) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        suggestionsContainer.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item" onclick="searchFilter.selectSuggestion('${suggestion}')">
                <span class="material-symbols-outlined">search</span>
                <span>${suggestion}</span>
            </div>
        `).join('');

        suggestionsContainer.style.display = 'block';
    }

    /**
     * Öneriyi seç
     */
    selectSuggestion(suggestion) {
        this.searchTerm = suggestion;
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.value = suggestion;
        
        // Önerileri gizle
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (suggestionsContainer) suggestionsContainer.style.display = 'none';
        
        this.performSearch();
    }

    /**
     * URL'den parametreleri yükle
     */
    loadFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        
        this.searchTerm = urlParams.get('q') || '';
        this.selectedCity = urlParams.get('city') || '';
        this.selectedDistrict = urlParams.get('district') || '';
        this.selectedType = urlParams.get('type') || '';

        // UI'ı güncelle
        const searchInput = document.getElementById('search-input');
        const cityFilter = document.getElementById('city-filter');
        const districtFilter = document.getElementById('district-filter');
        const typeFilter = document.getElementById('type-filter');

        if (searchInput) searchInput.value = this.searchTerm;
        if (cityFilter) cityFilter.value = this.selectedCity;
        if (typeFilter) typeFilter.value = this.selectedType;

        // İlçe filtresini güncelle
        if (this.selectedCity) {
            dataLoader.updateDistrictFilter(this.selectedCity);
            if (districtFilter) districtFilter.value = this.selectedDistrict;
        }
    }

    /**
     * URL'yi güncelle
     */
    updateURL() {
        const params = new URLSearchParams();
        
        if (this.searchTerm) params.set('q', this.searchTerm);
        if (this.selectedCity) params.set('city', this.selectedCity);
        if (this.selectedDistrict) params.set('district', this.selectedDistrict);
        if (this.selectedType) params.set('type', this.selectedType);

        const newURL = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
        window.history.replaceState({}, '', newURL);
    }
}

// Global instance
const searchFilter = new SearchFilter();
