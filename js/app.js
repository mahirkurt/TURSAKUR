// Türkiye Sağlık Kuruluşları - Ana Uygulama
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
        this.initializeTheme(); // Tema başlatma
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
        const body = document.body;
        const themeToggle = document.getElementById('theme-toggle');
        const logo = document.getElementById('app-logo');
        const icon = themeToggle.querySelector('.material-symbols-outlined');
        
        // Toggle dark mode class
        const isDarkMode = body.classList.toggle('dark-mode');
        
        // Update theme icon
        icon.textContent = isDarkMode ? 'light_mode' : 'dark_mode';
        
        // Update logo based on theme
        if (isDarkMode) {
            logo.src = 'assets/logos/TURSAKUR-Dark.png';
            body.style.colorScheme = 'dark';
        } else {
            logo.src = 'assets/logos/TURSAKUR-Light.png';
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
            document.getElementById('app-logo').src = 'assets/logos/TURSAKUR-Dark.png';
            document.querySelector('#theme-toggle .material-symbols-outlined').textContent = 'light_mode';
        } else {
            document.getElementById('app-logo').src = 'assets/logos/TURSAKUR-Light.png';
        }
    }
}

// Uygulama başlat
document.addEventListener('DOMContentLoaded', () => {
    new HealthInstitutionsApp();
});