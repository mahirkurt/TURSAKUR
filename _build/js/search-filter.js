/**
 * Search and Filter Module
 * Arama ve filtreleme işlevlerini yönetir
 */

class SearchFilter {
    constructor() {
        this.searchTerm = '';
        this.activeFilters = new Set();
    }

    /**
     * Arama ve filtreleme event listener'larını başlat
     */
    init() {
        this.bindEvents();
        this.setupFilterChips();
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
        }

        // Arama temizle butonu
        const clearSearch = document.getElementById('clear-search');
        if (clearSearch) {
            clearSearch.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Tüm filtreleri temizle
        const clearFilters = document.getElementById('clear-filters');
        if (clearFilters) {
            clearFilters.addEventListener('click', () => {
                this.clearAllFilters();
            });
        }

        // Sıralama
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.sortResults(e.target.value);
            });
        }
    }

    /**
     * Filtre chiplerini ayarla
     */
    setupFilterChips() {
        if (!dataLoader.data) return;

        this.setupTypeFilters();
        this.setupProvinceFilters();
    }

    /**
     * Kurum tipi filtrelerini ayarla
     */
    setupTypeFilters() {
        const typeFiltersContainer = document.getElementById('type-filters');
        if (!typeFiltersContainer) return;

        // Benzersiz kurum tiplerini al ve renk bilgileriyle birleştir
        const typeData = {};
        dataLoader.data.kurumlar.forEach(k => {
            if (k.kurum_tipi && k.kurum_tipi.trim()) {
                if (!typeData[k.kurum_tipi]) {
                    typeData[k.kurum_tipi] = {
                        count: 0,
                        color: k.kurum_tipi_renk || '#757575',
                        textColor: k.kurum_tipi_text_renk || '#FFFFFF'
                    };
                }
                typeData[k.kurum_tipi].count++;
            }
        });

        const types = Object.entries(typeData)
            .sort((a, b) => b[1].count - a[1].count); // Sayıya göre sırala

        typeFiltersContainer.innerHTML = types.map(([type, data]) => `
            <button class="filter-chip" 
                    data-filter="type" 
                    data-value="${type}"
                    style="--chip-color: ${data.color}; --chip-text-color: ${data.textColor};">
                ${type}
                <span class="chip-count">${data.count}</span>
            </button>
        `).join('');

        // Event listener'lar ekle
        typeFiltersContainer.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                this.toggleFilter('type', chip.dataset.value, chip);
            });
        });
    }

    /**
     * İl filtrelerini ayarla
     */
    setupProvinceFilters() {
        const provinceFiltersContainer = document.getElementById('province-filters');
        if (!provinceFiltersContainer) return;

        // Tüm illeri sayılarıyla birlikte al
        const provinceCounts = {};
        dataLoader.data.kurumlar.forEach(k => {
            if (k.il_adi) {
                provinceCounts[k.il_adi] = (provinceCounts[k.il_adi] || 0) + 1;
            }
        });

        // En çok kurum olan 25 ili göster
        const topProvinces = Object.entries(provinceCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 25)
            .map(([province, count]) => ({ province, count }));

        provinceFiltersContainer.innerHTML = topProvinces.map(({province, count}) => `
            <button class="filter-chip" data-filter="province" data-value="${province}">
                ${province}
                <span class="chip-count">${count}</span>
            </button>
        `).join('');

        // Event listener'lar ekle
        provinceFiltersContainer.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                this.toggleFilter('province', chip.dataset.value, chip);
            });
        });
    }

    /**
     * Filter toggle işlemi
     */
    toggleFilter(filterType, value, chipElement) {
        const filterKey = `${filterType}:${value}`;
        
        if (this.activeFilters.has(filterKey)) {
            // Filtreyi kaldır
            this.activeFilters.delete(filterKey);
            chipElement.classList.remove('active');
        } else {
            // Aynı tip filtrelerden sadece bir tane olabilir
            const existingFilter = Array.from(this.activeFilters).find(f => f.startsWith(filterType + ':'));
            if (existingFilter) {
                this.activeFilters.delete(existingFilter);
                // Önceki chip'i deaktive et
                const prevChip = document.querySelector(`[data-filter="${filterType}"][data-value="${existingFilter.split(':')[1]}"]`);
                if (prevChip) prevChip.classList.remove('active');
            }
            
            // Yeni filtreyi ekle
            this.activeFilters.add(filterKey);
            chipElement.classList.add('active');
        }

        this.applyFilters();
        this.updateFilterControls();
    }

    /**
     * Arama işlemini ele al
     */
    handleSearch(term) {
        this.searchTerm = term.trim();
        
        // Arama temizle butonunu göster/gizle
        const clearSearch = document.getElementById('clear-search');
        if (clearSearch) {
            clearSearch.style.display = this.searchTerm ? 'block' : 'none';
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
        if (this.searchTerm) {
            const searchTerms = this.searchTerm.toLowerCase().split(/\s+/);
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

        // Aktif filtreleri uygula
        this.activeFilters.forEach(filter => {
            const [filterType, value] = filter.split(':');
            
            if (filterType === 'type') {
                filtered = filtered.filter(kurum => kurum.kurum_tipi === value);
            } else if (filterType === 'province') {
                filtered = filtered.filter(kurum => kurum.il_adi === value);
            }
        });

        // Sonuçları güncelle
        dataLoader.filteredData = filtered;
        dataLoader.currentPage = 1;
        dataLoader.renderResults();
    }

    /**
     * Sonuçları sırala
     */
    sortResults(sortBy) {
        if (!dataLoader.filteredData) return;

        dataLoader.filteredData.sort((a, b) => {
            switch (sortBy) {
                case 'name':
                    return a.kurum_adi.localeCompare(b.kurum_adi, 'tr');
                case 'type':
                    return a.kurum_tipi.localeCompare(b.kurum_tipi, 'tr');
                case 'province':
                    return a.il_adi.localeCompare(b.il_adi, 'tr');
                default:
                    return 0;
            }
        });

        dataLoader.renderResults();
    }

    /**
     * Arama temizle
     */
    clearSearch() {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.value = '';
        }
        
        const clearSearch = document.getElementById('clear-search');
        if (clearSearch) {
            clearSearch.style.display = 'none';
        }

        this.searchTerm = '';
        this.applyFilters();
    }

    /**
     * Tüm filtreleri temizle
     */
    clearAllFilters() {
        // Arama temizle
        this.clearSearch();
        
        // Aktif filtreleri temizle
        this.activeFilters.clear();
        
        // Chip'leri deaktive et
        document.querySelectorAll('.filter-chip.active').forEach(chip => {
            chip.classList.remove('active');
        });

        this.applyFilters();
        this.updateFilterControls();
    }

    /**
     * Filtre kontrollerini güncelle
     */
    updateFilterControls() {
        const clearFilters = document.getElementById('clear-filters');
        if (clearFilters) {
            const hasActiveFilters = this.activeFilters.size > 0 || this.searchTerm;
            clearFilters.style.display = hasActiveFilters ? 'block' : 'none';
        }
    }
}

// Global instance
const searchFilter = new SearchFilter();
