/**
 * Data Loader Module
 * Sağlık kurumları verilerini yükler ve yönetir
 */

class DataLoader {
    constructor() {
        this.data = null;
        this.filteredData = null;
        this.currentPage = 1;
        this.itemsPerPage = 24;
        this.isLoading = false;
        this.viewMode = 'card'; // Default view mode
    }

    /**
     * Ana veri dosyasını yükler
     */
    async loadData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading(true);

        try {
            // Root'tan data dosyasını yükle
            const response = await fetch('data/turkiye_saglik_kuruluslari.json');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const jsonData = await response.json();
            
            // Veri yapısını kontrol et
            if (jsonData.kurumlar && Array.isArray(jsonData.kurumlar)) {
                this.data = jsonData;
                this.filteredData = jsonData.kurumlar;
                
                // Meta bilgileri güncelle
                this.updateMetaInfo(jsonData.meta);
                
                // UI'ı güncelle
                this.updateStats();
                this.populateFilters();
                this.setupFilters();
                this.renderResults();
                
                console.log(`✅ ${jsonData.kurumlar.length} kurum yüklendi`);
                
            } else {
                throw new Error('Geçersiz veri formatı');
            }

        } catch (error) {
            console.error('Veri yükleme hatası:', error);
            this.showError('Veriler yüklenirken bir hata oluştu. Lütfen sayfayı yenileyin.');
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }

    /**
     * Loading durumunu göster/gizle
     */
    showLoading(show) {
        const loadingSpinner = document.getElementById('loading-spinner');
        const resultsContainer = document.getElementById('results-container');
        
        if (loadingSpinner) {
            loadingSpinner.style.display = show ? 'flex' : 'none';
        }
        
        if (resultsContainer) {
            resultsContainer.style.display = show ? 'none' : 'block';
        }
    }

    /**
     * İstatistikleri güncelle
     */
    updateStats() {
        if (!this.data) return;

        const totalInstitutions = document.getElementById('total-institutions');
        const totalProvinces = document.getElementById('total-provinces');
        const totalTypes = document.getElementById('total-types');

        if (totalInstitutions) {
            totalInstitutions.textContent = this.data.kurumlar.length.toLocaleString('tr-TR');
        }

        if (totalProvinces) {
            const uniqueProvinces = new Set(this.data.kurumlar.map(k => k.il_adi));
            totalProvinces.textContent = uniqueProvinces.size;
        }

        if (totalTypes) {
            const uniqueTypes = new Set(this.data.kurumlar.map(k => k.kurum_tipi));
            totalTypes.textContent = uniqueTypes.size;
        }
    }

    /**
     * Sonuçları render et
     */
    renderResults() {
        if (!this.filteredData) return;

        const resultsContainer = document.getElementById('results-container');
        const resultsCount = document.getElementById('results-count');

        if (!resultsContainer) {
            console.error('results-container elementi bulunamadı');
            return;
        }

        // Sonuç sayısını güncelle
        if (resultsCount) {
            resultsCount.textContent = `${this.filteredData.length.toLocaleString('tr-TR')} sonuç bulundu`;
        }

        // Sonuç yoksa
        if (this.filteredData.length === 0) {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <span class="material-symbols-outlined">search_off</span>
                    <h3>Sonuç bulunamadı</h3>
                    <p>Arama kriterlerinizi değiştirerek tekrar deneyin.</p>
                </div>
            `;
            return;
        }

        // Sayfalama hesapla
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.filteredData.slice(startIndex, endIndex);

        // View mode'a göre render et
        if (this.viewMode === 'list') {
            this.renderListView(pageData, resultsContainer);
        } else if (this.viewMode === 'map') {
            this.renderMapView(pageData, resultsContainer);
        } else {
            // Default: card view
            this.renderCardView(pageData, resultsContainer);
        }

        // Sayfalamayı güncelle
        this.renderPagination();
    }

    /**
     * Kurum kartı oluştur
     */
    createInstitutionCard(kurum) {
        const hasPhone = kurum.telefon && kurum.telefon.trim();
        const typeColor = kurum.kurum_tipi_renk || '#424242';

        return `
            <div class="institution-card" data-id="${kurum.kurum_id}" onclick="dataLoader.showInstitutionDetail('${kurum.kurum_id}')">
                <div class="institution-type" style="background-color: ${typeColor}">${kurum.kurum_tipi}</div>
                <h3>${kurum.kurum_adi}</h3>
                
                <div class="institution-location">
                    <span class="material-symbols-outlined">location_on</span>
                    <span>${kurum.ilce_adi}, ${kurum.il_adi}</span>
                </div>
                
                ${hasPhone ? `
                    <div class="institution-phone">
                        <span class="material-symbols-outlined">phone</span>
                        <span>${kurum.telefon}</span>
                    </div>
                ` : ''}
                
                <div class="card-click-hint">
                    <span class="material-symbols-outlined">info</span>
                    <span>Detaylar için tıklayın</span>
                </div>
            </div>
        `;
    }

    /**
     * Liste öğesi oluştur
     */
    createInstitutionListItem(kurum) {
        const hasPhone = kurum.telefon && kurum.telefon.trim();
        const hasWebsite = kurum.web_sitesi && kurum.web_sitesi.trim();
        const typeColor = kurum.kurum_tipi_renk || '#424242';

        return `
            <div class="institution-list-item" data-id="${kurum.kurum_id}" onclick="dataLoader.showInstitutionDetail('${kurum.kurum_id}')">
                <div class="institution-type-badge" style="background-color: ${typeColor}">
                    ${kurum.kurum_tipi}
                </div>
                <div class="institution-info">
                    <h3>${kurum.kurum_adi}</h3>
                    <div class="institution-details">
                        <div class="detail-item">
                            <span class="material-symbols-outlined">location_on</span>
                            <span>${kurum.adres || `${kurum.ilce_adi}, ${kurum.il_adi}`}</span>
                        </div>
                        ${hasPhone ? `
                            <div class="detail-item">
                                <span class="material-symbols-outlined">phone</span>
                                <span>${kurum.telefon}</span>
                            </div>
                        ` : ''}
                        ${hasWebsite ? `
                            <div class="detail-item">
                                <span class="material-symbols-outlined">language</span>
                                <span>${kurum.web_sitesi}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="list-item-action">
                    <span class="material-symbols-outlined">arrow_forward_ios</span>
                </div>
            </div>
        `;
    }

    /**
     * Harita öğesi oluştur
     */
    createInstitutionMapItem(kurum) {
        const typeColor = kurum.kurum_tipi_renk || '#424242';
        const hasCoords = kurum.koordinat_lat && kurum.koordinat_lon;

        return `
            <div class="institution-map-item" data-id="${kurum.kurum_id}" onclick="dataLoader.showInstitutionDetail('${kurum.kurum_id}')">
                <div class="map-marker" style="background-color: ${typeColor}">
                    <span class="material-symbols-outlined">location_on</span>
                </div>
                <div class="map-info">
                    <h4>${kurum.kurum_adi}</h4>
                    <p>${kurum.ilce_adi}, ${kurum.il_adi}</p>
                    ${hasCoords ? `<small>Koordinat: ${kurum.koordinat_lat}, ${kurum.koordinat_lon}</small>` : '<small>Koordinat bilgisi yok</small>'}
                </div>
            </div>
        `;
    }

    /**
     * Kurum detayını ID ile al
     */
    getInstitutionById(id) {
        if (!this.data) return null;
        return this.data.kurumlar.find(k => k.kurum_id === id);
    }

    /**
     * Sayfalama render et
     */
    renderPagination() {
        const pagination = document.getElementById('pagination');
        if (!pagination || !this.filteredData) return;

        const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);

        if (totalPages <= 1) {
            pagination.style.display = 'none';
            return;
        }

        pagination.style.display = 'flex';
        // Sayfalama mantığı burada geliştirilecek
    }

    /**
     * Belirli sayfaya git
     */
    goToPage(page) {
        this.currentPage = page;
        this.renderResults();
        
        // Sayfanın üstüne kaydır
        document.querySelector('.results-section').scrollIntoView({ 
            behavior: 'smooth' 
        });
    }

    /**
     * Meta bilgileri güncelle
     */
    updateMetaInfo(meta) {
        if (!meta) return;
        
        // Son güncelleme tarihini göster
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement && meta.last_updated) {
            lastUpdateElement.textContent = new Date(meta.last_updated).toLocaleDateString('tr-TR');
        }
        
        // Footer'daki son güncelleme
        const lastUpdateFooter = document.getElementById('last-update-footer');
        if (lastUpdateFooter && meta.last_updated) {
            lastUpdateFooter.textContent = `Son güncelleme: ${new Date(meta.last_updated).toLocaleDateString('tr-TR')}`;
        }
        
        // Veri kaynağı bilgisini göster
        const dataSourceElement = document.getElementById('data-source');
        if (dataSourceElement && meta.description) {
            dataSourceElement.textContent = meta.description;
        }
    }

    /**
     * Hata mesajı göster
     */
    showError(message) {
        // Mevcut error container'ı kontrol et
        let errorContainer = document.getElementById('error-container');
        
        if (!errorContainer) {
            // Error container oluştur
            errorContainer = document.createElement('div');
            errorContainer.id = 'error-container';
            errorContainer.className = 'error-container';
            
            // Ana content'in başına ekle
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.insertBefore(errorContainer, mainContent.firstChild);
            }
        }
        
        errorContainer.innerHTML = `
            <div class="error-card">
                <span class="material-symbols-outlined">error</span>
                <div class="error-content">
                    <h3>Bir Hata Oluştu</h3>
                    <p>${message}</p>
                    <button class="md-button-filled" onclick="location.reload()">
                        Sayfayı Yenile
                    </button>
                </div>
            </div>
        `;
        
        errorContainer.style.display = 'block';
    }

    /**
     * Filtreleri doldur
     */
    populateFilters() {
        if (!this.data) return;

        // İl filtresini doldur
        const cityFilter = document.getElementById('city-filter');
        if (cityFilter) {
            const cities = [...new Set(this.data.kurumlar.map(k => k.il_adi))].sort();
            cityFilter.innerHTML = '<option value="">Tüm İller</option>' +
                cities.map(city => `<option value="${city}">${city}</option>`).join('');
        }

        // Kurum tipi filtresini doldur
        const typeFilter = document.getElementById('type-filter');
        if (typeFilter) {
            const types = [...new Set(this.data.kurumlar.map(k => k.kurum_tipi))].sort();
            typeFilter.innerHTML = '<option value="">Tüm Kurum Tipleri</option>' +
                types.map(type => `<option value="${type}">${type}</option>`).join('');
        }
    }

    /**
     * Arama ve filtreleme
     */
    setupFilters() {
        const searchInput = document.getElementById('search-input');
        const cityFilter = document.getElementById('city-filter');
        const typeFilter = document.getElementById('type-filter');
        const clearFilters = document.getElementById('clear-filters');

        if (searchInput) {
            searchInput.addEventListener('input', () => this.applyFilters());
        }

        if (cityFilter) {
            cityFilter.addEventListener('change', () => this.applyFilters());
        }

        if (typeFilter) {
            typeFilter.addEventListener('change', () => this.applyFilters());
        }

        if (clearFilters) {
            clearFilters.addEventListener('click', () => this.clearAllFilters());
        }
    }

    /**
     * Filtreleri uygula
     */
    applyFilters() {
        if (!this.data) return;

        const searchValue = document.getElementById('search-input')?.value.toLowerCase() || '';
        const cityValue = document.getElementById('city-filter')?.value || '';
        const typeValue = document.getElementById('type-filter')?.value || '';

        this.filteredData = this.data.kurumlar.filter(kurum => {
            const matchesSearch = !searchValue || 
                kurum.kurum_adi.toLowerCase().includes(searchValue) ||
                kurum.il_adi.toLowerCase().includes(searchValue) ||
                kurum.ilce_adi.toLowerCase().includes(searchValue);

            const matchesCity = !cityValue || kurum.il_adi === cityValue;
            const matchesType = !typeValue || kurum.kurum_tipi === typeValue;

            return matchesSearch && matchesCity && matchesType;
        });

        this.currentPage = 1;
        this.renderResults();
    }

    /**
     * Tüm filtreleri temizle
     */
    clearAllFilters() {
        const searchInput = document.getElementById('search-input');
        const cityFilter = document.getElementById('city-filter');
        const typeFilter = document.getElementById('type-filter');

        if (searchInput) searchInput.value = '';
        if (cityFilter) cityFilter.value = '';
        if (typeFilter) typeFilter.value = '';

        this.filteredData = this.data ? this.data.kurumlar : [];
        this.currentPage = 1;
        this.renderResults();
    }

    /**
     * Kurum detayını göster
     */
    showInstitutionDetail(kurumId) {
        const kurum = this.getInstitutionById(kurumId);
        if (!kurum) return;

        const modal = document.createElement('div');
        modal.className = 'institution-detail-modal';
        modal.innerHTML = this.createInstitutionDetailHTML(kurum);
        
        document.body.appendChild(modal);
        
        // Modal kapatma fonksiyonu
        const closeModal = (e) => {
            e.stopPropagation();
            if (modal.parentNode) {
                document.body.removeChild(modal);
            }
        };
        
        // X butonuna tıklama
        const closeBtn = modal.querySelector('.close-modal');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal);
        }
        
        // Backdrop'a tıklayınca kapatma
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('institution-detail-backdrop')) {
                closeModal(e);
            }
        });
        
        // Modal içeriği tıklanınca event propagation'ı durdur
        const modalContent = modal.querySelector('.institution-detail-content');
        if (modalContent) {
            modalContent.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
        
        // ESC tuşu ile kapatma
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                closeModal(e);
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    /**
     * Kurum detay HTML'i oluştur
     */
    createInstitutionDetailHTML(kurum) {
        const hasCoordinates = kurum.koordinat_lat && kurum.koordinat_lon;
        const hasPhone = kurum.telefon && kurum.telefon.trim();
        const hasWebsite = kurum.web_sitesi && kurum.web_sitesi.trim();

        return `
            <div class="institution-detail-backdrop">
                <div class="institution-detail-content">
                    <div class="institution-detail-header">
                        <div class="institution-header-info">
                            <div class="institution-type-badge" style="background-color: ${kurum.kurum_tipi_renk || '#424242'}">
                                ${kurum.kurum_tipi}
                            </div>
                            <h2>${kurum.kurum_adi}</h2>
                        </div>
                        <button class="close-modal icon-button">
                            <span class="material-symbols-outlined">close</span>
                        </button>
                    </div>
                    
                    <div class="institution-detail-body">
                        <div class="detail-section">
                            <div class="detail-item">
                                <span class="material-symbols-outlined">badge</span>
                                <div class="detail-content">
                                    <label>Kurum ID</label>
                                    <span>${kurum.kurum_id}</span>
                                </div>
                            </div>
                            
                            <div class="detail-item">
                                <span class="material-symbols-outlined">location_on</span>
                                <div class="detail-content">
                                    <label>Konum</label>
                                    <span>${kurum.ilce_adi}, ${kurum.il_adi}</span>
                                </div>
                            </div>
                            
                            ${kurum.adres ? `
                                <div class="detail-item">
                                    <span class="material-symbols-outlined">home</span>
                                    <div class="detail-content">
                                        <label>Adres</label>
                                        <span>${kurum.adres}</span>
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${hasPhone ? `
                                <div class="detail-item">
                                    <span class="material-symbols-outlined">phone</span>
                                    <div class="detail-content">
                                        <label>Telefon</label>
                                        <a href="tel:${kurum.telefon}">${kurum.telefon}</a>
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${hasWebsite ? `
                                <div class="detail-item">
                                    <span class="material-symbols-outlined">language</span>
                                    <div class="detail-content">
                                        <label>Web Sitesi</label>
                                        <a href="${kurum.web_sitesi}" target="_blank">${kurum.web_sitesi}</a>
                                    </div>
                                </div>
                            ` : ''}
                            
                            <div class="detail-item">
                                <span class="material-symbols-outlined">source</span>
                                <div class="detail-content">
                                    <label>Veri Kaynağı</label>
                                    <span>${kurum.veri_kaynagi || 'Resmi Kaynak'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-item">
                                <span class="material-symbols-outlined">update</span>
                                <div class="detail-content">
                                    <label>Son Güncelleme</label>
                                    <span>${new Date(kurum.son_guncelleme).toLocaleDateString('tr-TR')}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="detail-actions">
                            ${hasPhone ? `
                                <button class="md-button-filled" onclick="window.open('tel:${kurum.telefon}')">
                                    <span class="material-symbols-outlined">call</span>
                                    Ara
                                </button>
                            ` : ''}
                            
                            ${hasWebsite ? `
                                <button class="md-button-outlined" onclick="window.open('${kurum.web_sitesi}', '_blank')">
                                    <span class="material-symbols-outlined">language</span>
                                    Web Sitesi
                                </button>
                            ` : ''}
                            
                            ${hasCoordinates ? `
                                <button class="md-button-outlined" onclick="window.open('https://maps.google.com/?q=${kurum.koordinat_lat},${kurum.koordinat_lon}', '_blank')">
                                    <span class="material-symbols-outlined">directions</span>
                                    Haritada Göster
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * View mode ayarla
     */
    setViewMode(mode) {
        this.viewMode = mode;
    }

    /**
     * Kart görünümü render et
     */
    renderCardView(pageData, resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="results-grid">
                ${pageData.map(kurum => this.createInstitutionCard(kurum)).join('')}
            </div>
        `;
    }

    /**
     * Liste görünümü render et
     */
    renderListView(pageData, resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="results-list">
                ${pageData.map(kurum => this.createInstitutionListItem(kurum)).join('')}
            </div>
        `;
    }

    /**
     * Harita görünümü render et
     */
    renderMapView(pageData, resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="map-container">
                <div class="map-placeholder">
                    <span class="material-symbols-outlined">map</span>
                    <h3>Harita Görünümü</h3>
                    <p>Harita entegrasyonu geliştirme aşamasındadır.</p>
                    <div class="institutions-on-map">
                        ${pageData.map(kurum => this.createInstitutionMapItem(kurum)).join('')}
                    </div>
                </div>
            </div>
        `;
    }
}

// Global instance
const dataLoader = new DataLoader();
