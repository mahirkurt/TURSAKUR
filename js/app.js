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
        this.isLoading = false;
        this.loadingProgress = 0;
        this.init();
    }

    async init() {
        // Show loading with progress
        if (window.UXEnhancer) {
            window.UXEnhancer.showLoading('Sağlık kuruluşları yükleniyor...', true);
        }
        
        this.initializeTheme(); // Tema başlatma
        this.updateLoadingProgress(25);
        
        await this.loadData();
        this.updateLoadingProgress(75);
        
        this.setupEventListeners();
        this.createFilters();
        this.updateLoadingProgress(90);
        
        // Başlangıçta sonuçları gösterme - sadece filtreleme sonrası göster
        this.hideLoading();
        this.showInitialMessage();
        this.updateLoadingProgress(100);
        
        // Hide loading overlay
        setTimeout(() => {
            if (window.UXEnhancer) {
                window.UXEnhancer.hideLoading();
            }
        }, 500);
    }
    
    updateLoadingProgress(percentage) {
        if (window.UXEnhancer) {
            window.UXEnhancer.updateLoadingProgress(percentage);
        }
    }

    async loadData() {
        try {
            this.isLoading = true;
            const response = await fetch('data/turkiye_saglik_kuruluslari.json');
            const result = await response.json();
            this.data = result.kurumlar || [];
            this.filteredData = [...this.data];
            this.updateStats(result.metadata);
            this.isLoading = false;
            
            // Track performance
            if (window.UXEnhancer) {
                window.UXEnhancer.performanceMetrics.dataLoadTime = performance.now();
            }
        } catch (error) {
            console.error('Veri yüklenirken hata:', error);
            this.showError('Veriler yüklenemedi');
            this.isLoading = false;
            
            if (window.UXEnhancer) {
                window.UXEnhancer.showNotification('Veriler yüklenemedi. Lütfen sayfayı yenileyin.', 'warning', 5000);
            }
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

        // Kurum tipi chip filtreleri
        document.querySelectorAll('.filter-chip-compact[data-type]').forEach(chip => {
            chip.addEventListener('click', (e) => {
                // Önceki aktif chip'i kaldır
                document.querySelectorAll('.filter-chip-compact').forEach(c => c.classList.remove('active'));
                
                // Yeni chip'i aktif yap
                chip.classList.add('active');
                
                const type = chip.dataset.type;
                this.filters.type = type === 'ALL' ? '' : type;
                this.applyFilters();
                this.updateActiveFilters();
            });
        });

        // İl seçimi
        document.getElementById('provinceFilter').addEventListener('change', (e) => {
            this.filters.province = e.target.value;
            this.filters.district = ''; // İl değiştiğinde ilçeyi sıfırla
            this.updateDistrictFilter();
            this.applyFilters();
            this.updateActiveFilters();
        });

        // İlçe seçimi
        document.getElementById('districtFilter').addEventListener('change', (e) => {
            this.filters.district = e.target.value;
            this.applyFilters();
            this.updateActiveFilters();
        });

        // Filtreleri temizleme
        const clearFiltersBtn = document.getElementById('clear-filters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearAllFilters();
            });
        }

        // Tema değiştirici
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Modal kapatma
        document.getElementById('modal-close').addEventListener('click', () => {
            this.closeModal();
        });
        
        document.getElementById('institution-modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.closeModal();
            }
        });
    }

    createFilters() {
        this.createLocationSelectors();
    }

    createLocationSelectors() {
        // İl seçici doldur
        const provinces = this.getUniqueProvinces();
        const provinceSelect = document.getElementById('provinceFilter');
        
        // Önce mevcut option'ları temizle (default option hariç)
        const options = provinceSelect.querySelectorAll('option:not(:first-child)');
        options.forEach(option => option.remove());
        
        provinces.forEach(province => {
            if (province && province.trim()) {
                const option = document.createElement('option');
                option.value = province;
                option.textContent = province;
                provinceSelect.appendChild(option);
            }
        });
        
        console.log(`✅ ${provinces.length} il seçenekleri eklendi`);
    }

    updateDistrictFilter() {
        const districtSelect = document.getElementById('districtFilter');
        
        // İlçe seçiciyi temizle
        districtSelect.innerHTML = '<option value="">İlçe Seçin</option>';
        
        if (this.filters.province) {
            // İlçe seçiciyi etkinleştir
            districtSelect.disabled = false;
            
            // Seçili ile ait ilçeleri getir
            const districts = this.getDistrictsByProvince(this.filters.province);
            
            districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district;
                option.textContent = district;
                districtSelect.appendChild(option);
            });
        } else {
            // İl seçilmemişse ilçe seçiciyi devre dışı bırak
            districtSelect.disabled = true;
        }
    }
    
    onProvinceChange(selectedProvince) {
        const districtSelect = document.getElementById('district-select');
        
        // İlçe seçiciyi temizle
        districtSelect.innerHTML = '<option value="">Tüm İlçeler</option>';
        
        if (selectedProvince) {
            // İlçe seçiciyi etkinleştir
            districtSelect.disabled = false;
            
            // Seçili ile ait ilçeleri getir
            const districts = this.getDistrictsByProvince(selectedProvince);
            
            districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district;
                option.textContent = district;
                districtSelect.appendChild(option);
            });
            
            // İl filtresini uygula
            this.filters.province = selectedProvince;
            this.filters.district = '';
        } else {
            // İl seçilmemişse ilçe seçiciyi devre dışı bırak
            districtSelect.disabled = true;
            districtSelect.innerHTML = '<option value="">İlçe seçmek için önce il seçin</option>';
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
        chip.className = 'filter-chip-compact';
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
        
        // Create cards with animation support
        const cardsHTML = this.filteredData.map(item => this.createInstitutionCard(item)).join('');
        container.innerHTML = cardsHTML;
        
        // Setup intersection observer for animations if UXEnhancer is available
        if (window.UXEnhancer) {
            // Small delay to allow DOM to update
            setTimeout(() => {
                window.UXEnhancer.observeElements();
            }, 50);
        }
        
        // Track render performance
        if (window.UXEnhancer) {
            window.UXEnhancer.performanceMetrics.renderTime = performance.now();
        }
    }

    createInstitutionCard(item) {
        const typeClass = this.getTypeClass(item.kurum_tipi);
        return `
            <div class="institution-card hospital-card" data-id="${item.kurum_id}">
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
                    <button class="action-button detail-btn" onclick="app.showInstitutionDetail('${item.kurum_id}')">
                        <span class="material-symbols-outlined">info</span>
                        Detay
                    </button>
                    ${item.telefon ? `<button class="action-button" onclick="window.open('tel:${item.telefon}')">
                        <span class="material-symbols-outlined">call</span>
                        Ara
                    </button>` : ''}
                    ${item.web_sitesi ? `<button class="action-button" onclick="window.open('${item.web_sitesi}', '_blank')">
                        <span class="material-symbols-outlined">language</span>
                        Web
                    </button>` : ''}
                    ${item.koordinat_lat && item.koordinat_lon ? `<button class="action-button" onclick="window.open('map.html?hospital=${item.kurum_id}', '_blank')">
                        <span class="material-symbols-outlined">map</span>
                        Harita
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
            'AGIZ_DIS_SAGLIGI_MERKEZI': 'agiz-dis-sagligi-merkezi',
            'EGITIM_ARASTIRMA_HASTANESI': 'egitim-arastirma-hastanesi',
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
        // İl adlarını normalize et ve duplicate'leri kaldır
        const provinces = this.data.map(item => {
            let province = item.il_adi || '';
            // Normalize et (büyük harf, trim)
            province = province.trim().toUpperCase();
            return province;
        });
        
        // Unique yap ve sırala
        const uniqueProvinces = [...new Set(provinces)]
            .filter(p => p && p.length > 0)
            .sort((a, b) => a.localeCompare(b, 'tr'));
        
        console.log(`📊 ${uniqueProvinces.length} unique il bulundu`);
        return uniqueProvinces;
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
        document.getElementById('provinceFilter').value = '';
        
        // İlçe seçiciyi sıfırla ve devre dışı bırak
        const districtSelect = document.getElementById('districtFilter');
        districtSelect.value = '';
        districtSelect.disabled = true;
        districtSelect.innerHTML = '<option value="">İlçe Seçin</option>';
        
        document.querySelectorAll('.filter-chip-compact').forEach(chip => {
            chip.classList.remove('active');
        });
        document.querySelector('.filter-chip-compact[data-type="ALL"]').classList.add('active');
        
        this.applyFilters();
        this.updateActiveFilters();
    }

    clearAllFilters() {
        // Filtreleri sıfırla
        this.filters = {
            search: '',
            type: '',
            province: '',
            district: ''
        };

        // UI elementlerini sıfırla
        document.getElementById('search-input').value = '';
        document.getElementById('provinceFilter').value = '';
        document.getElementById('districtFilter').value = '';
        document.getElementById('districtFilter').disabled = true;

        // Chip seçimlerini sıfırla
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.classList.remove('active');
        });
        document.querySelector('.filter-chip-compact[data-type="ALL"]').classList.add('active');

        // Filtreleri uygula
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
        const footerLogo = document.querySelector('.footer-logo');
        const icon = themeToggle.querySelector('.material-symbols-outlined');
        
        // Toggle dark mode class
        const isDarkMode = body.classList.toggle('dark-mode');
        
        // Update theme icon
        icon.textContent = isDarkMode ? 'light_mode' : 'dark_mode';
        
        // Update logos based on theme
        if (isDarkMode) {
            logo.src = 'assets/logos/TURSAKUR-Light.png';
            if (footerLogo) footerLogo.src = 'assets/logos/TURSAKUR-Light.png';
            body.style.colorScheme = 'dark';
        } else {
            logo.src = 'assets/logos/TURSAKUR-Color.png';
            if (footerLogo) footerLogo.src = 'assets/logos/TURSAKUR-Color.png';
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
        
        const logo = document.getElementById('app-logo');
        const footerLogo = document.querySelector('.footer-logo');
        
        if (shouldUseDark) {
            document.body.classList.add('dark-mode');
            document.body.style.colorScheme = 'dark';
            logo.src = 'assets/logos/TURSAKUR-Light.png';
            if (footerLogo) footerLogo.src = 'assets/logos/TURSAKUR-Light.png';
            document.querySelector('#theme-toggle .material-symbols-outlined').textContent = 'light_mode';
        } else {
            logo.src = 'assets/logos/TURSAKUR-Color.png';
            if (footerLogo) footerLogo.src = 'assets/logos/TURSAKUR-Color.png';
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
        const activeFiltersContainer = document.getElementById('active-filters-minimal');
        const activeFilterTags = document.getElementById('active-filter-tags');
        
        // Container varsa temizle
        if (activeFilterTags) {
            activeFilterTags.innerHTML = '';
        }
        
        let hasActiveFilters = false;
        
        // Tip filtresi
        if (this.filters.type) {
            const tag = document.createElement('div');
            tag.className = 'active-filter-tag';
            tag.textContent = this.formatType(this.filters.type);
            activeFilterTags.appendChild(tag);
            hasActiveFilters = true;
        }
        
        // İl filtresi
        if (this.filters.province) {
            const tag = document.createElement('div');
            tag.className = 'active-filter-tag';
            tag.textContent = this.filters.province;
            activeFilterTags.appendChild(tag);
            hasActiveFilters = true;
        }
        
        // İlçe filtresi
        if (this.filters.district) {
            const tag = document.createElement('div');
            tag.className = 'active-filter-tag';
            tag.textContent = this.filters.district;
            activeFilterTags.appendChild(tag);
            hasActiveFilters = true;
        }
        
        // Arama filtresi
        if (this.filters.search && this.filters.search.trim()) {
            const tag = document.createElement('div');
            tag.className = 'active-filter-tag';
            tag.textContent = `"${this.filters.search}"`;
            activeFilterTags.appendChild(tag);
            hasActiveFilters = true;
        }
        
        // Container'ı göster/gizle
        if (activeFiltersContainer) {
            activeFiltersContainer.style.display = hasActiveFilters ? 'flex' : 'none';
        }
        
        // Update filter counts
        this.updateFilterCounts();
    }

    updateFilterCounts() {
        const typeCounts = {
            'ALL': this.data.length,
            'DEVLET_HASTANESI': this.data.filter(item => item.kurum_tipi === 'DEVLET_HASTANESI').length,
            'OZEL_HASTANE': this.data.filter(item => item.kurum_tipi === 'OZEL_HASTANE').length,
            'UNIVERSITE_HASTANESI': this.data.filter(item => item.kurum_tipi === 'UNIVERSITE_HASTANESI').length,
            'EGITIM_ARASTIRMA_HASTANESI': this.data.filter(item => item.kurum_tipi === 'EGITIM_ARASTIRMA_HASTANESI').length,
            'AGIZ_DIS_SAGLIGI_MERKEZI': this.data.filter(item => item.kurum_tipi === 'AGIZ_DIS_SAGLIGI_MERKEZI').length
        };
        
        // Update count displays
        Object.keys(typeCounts).forEach(type => {
            const countElement = document.getElementById(`count-${type.toLowerCase().replace(/_/g, '-')}`);
            if (countElement) {
                countElement.textContent = typeCounts[type];
            }
        });
    }
    
    removeFilter(filterType) {
        this.filters[filterType] = '';
        
        if (filterType === 'search') {
            document.getElementById('search-input').value = '';
        } else if (filterType === 'province') {
            document.getElementById('province-select').value = '';
            // İlçe seçiciyi sıfırla ve devre dışı bırak
            const districtSelect = document.getElementById('district-select');
            districtSelect.value = '';
            districtSelect.disabled = true;
            districtSelect.innerHTML = '<option value="">İlçe seçmek için önce il seçin</option>';
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

    showInstitutionDetail(kurumId) {
        const institution = this.data.find(item => item.kurum_id === kurumId);
        if (!institution) return;

        const modal = document.getElementById('institution-modal-overlay');
        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.getElementById('modal-content');

        modalTitle.textContent = institution.kurum_adi;
        
        modalContent.innerHTML = `
            <div class="detail-section">
                <div class="detail-title">
                    <span class="material-symbols-outlined">business</span>
                    Genel Bilgiler
                </div>
                <div class="detail-row">
                    <div class="detail-label">Kurum Adı</div>
                    <div class="detail-value large">${institution.kurum_adi}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Kurum Türü</div>
                    <div class="detail-value">
                        <span class="institution-type-badge ${this.getTypeClass(institution.kurum_tipi)}">
                            ${this.formatType(institution.kurum_tipi)}
                        </span>
                    </div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Kurum ID</div>
                    <div class="detail-value">${institution.kurum_id}</div>
                </div>
            </div>

            <div class="detail-section">
                <div class="detail-title">
                    <span class="material-symbols-outlined">location_on</span>
                    Konum Bilgileri
                </div>
                <div class="detail-row">
                    <div class="detail-label">İl</div>
                    <div class="detail-value">${institution.il_adi} (${institution.il_kodu})</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">İlçe</div>
                    <div class="detail-value">${institution.ilce_adi}</div>
                </div>
                ${institution.adres ? `
                <div class="detail-row">
                    <div class="detail-label">Adres</div>
                    <div class="detail-value">${institution.adres}</div>
                </div>
                ` : ''}
                ${institution.koordinat_lat && institution.koordinat_lon ? `
                <div class="detail-row">
                    <div class="detail-label">Koordinatlar</div>
                    <div class="detail-value">${institution.koordinat_lat}, ${institution.koordinat_lon}</div>
                </div>
                ` : ''}
            </div>

            <div class="detail-section">
                <div class="detail-title">
                    <span class="material-symbols-outlined">contact_phone</span>
                    İletişim Bilgileri
                </div>
                ${institution.telefon ? `
                <div class="detail-row">
                    <div class="detail-label">Telefon</div>
                    <div class="detail-value">
                        <a href="tel:${institution.telefon}" style="color: var(--md-sys-color-primary); text-decoration: none;">
                            ${institution.telefon}
                        </a>
                    </div>
                </div>
                ` : ''}
                ${institution.web_sitesi ? `
                <div class="detail-row">
                    <div class="detail-label">Web Sitesi</div>
                    <div class="detail-value">
                        <a href="${institution.web_sitesi}" target="_blank" style="color: var(--md-sys-color-primary); text-decoration: none;">
                            ${institution.web_sitesi}
                        </a>
                    </div>
                </div>
                ` : ''}
            </div>

            <div class="detail-section">
                <div class="detail-title">
                    <span class="material-symbols-outlined">database</span>
                    Veri Kaynağı
                </div>
                <div class="detail-row">
                    <div class="detail-label">Kaynak</div>
                    <div class="detail-value">${institution.veri_kaynagi}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Son Güncelleme</div>
                    <div class="detail-value">${institution.son_guncelleme}</div>
                </div>
            </div>
        `;

        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    closeModal() {
        const modal = document.getElementById('institution-modal-overlay');
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

// Uygulama başlat
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new HealthInstitutionsApp();
});