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
    }

    /**
     * Ana veri dosyasını yükler
     */
    async loadData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading(true);

        try {
            const response = await fetch('../data/turkiye_saglik_kuruluslari.json');
            
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
        const loadingElement = document.getElementById('loading-state');
        const resultsGrid = document.getElementById('results-grid');
        
        if (loadingElement) {
            loadingElement.style.display = show ? 'flex' : 'none';
        }
        
        if (resultsGrid) {
            resultsGrid.style.display = show ? 'none' : 'grid';
        }
    }

    /**
     * Hata mesajı göster
     */
    showError(message) {
        const resultsGrid = document.getElementById('results-grid');
        if (resultsGrid) {
            resultsGrid.innerHTML = `
                <div class="error-state">
                    <span class="material-symbols-outlined error-icon">error</span>
                    <h3>Bir Hata Oluştu</h3>
                    <p>${message}</p>
                    <button class="primary-button" onclick="dataLoader.loadData()">
                        <span class="material-symbols-outlined">refresh</span>
                        Tekrar Dene
                    </button>
                </div>
            `;
        }
    }

    /**
     * Meta bilgileri güncelle
     */
    updateMetaInfo(meta) {
        if (!meta) return;

        // Son güncelleme tarihini güncelle
        const lastUpdatedElement = document.getElementById('last-updated');
        if (lastUpdatedElement && meta.last_updated) {
            const date = new Date(meta.last_updated);
            const today = new Date();
            const diffTime = Math.abs(today - date);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 1) {
                lastUpdatedElement.textContent = 'Bugün';
            } else if (diffDays < 7) {
                lastUpdatedElement.textContent = `${diffDays} gün önce`;
            } else {
                lastUpdatedElement.textContent = date.toLocaleDateString('tr-TR');
            }
        }
    }

    /**
     * İstatistikleri güncelle
     */
    updateStats() {
        if (!this.data) return;

        const totalCount = document.getElementById('total-count');
        const cityCount = document.getElementById('city-count');

        if (totalCount) {
            totalCount.textContent = this.data.kurumlar.length.toLocaleString('tr-TR');
        }

        if (cityCount) {
            const uniqueCities = new Set(this.data.kurumlar.map(k => k.il_adi));
            cityCount.textContent = uniqueCities.size;
        }
    }

    /**
     * Filtreleri doldur
     */
    populateFilters() {
        if (!this.data) return;

        this.populateCityFilter();
        this.populateTypeFilter();
    }

    /**
     * İl filtresini doldur
     */
    populateCityFilter() {
        const cityFilter = document.getElementById('city-filter');
        if (!cityFilter) return;

        // Benzersiz illeri al ve sırala
        const cities = [...new Set(this.data.kurumlar.map(k => k.il_adi))]
            .filter(city => city && city.trim())
            .sort((a, b) => a.localeCompare(b, 'tr'));

        // Mevcut seçimleri temizle (ilk option hariç)
        cityFilter.innerHTML = '<option value="">Tüm İller</option>';

        // Yeni seçenekleri ekle
        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            cityFilter.appendChild(option);
        });
    }

    /**
     * Kurum tipi filtresini doldur
     */
    populateTypeFilter() {
        const typeFilter = document.getElementById('type-filter');
        if (!typeFilter) return;

        // Benzersiz kurum tiplerini al ve sırala
        const types = [...new Set(this.data.kurumlar.map(k => k.kurum_tipi))]
            .filter(type => type && type.trim())
            .sort((a, b) => a.localeCompare(b, 'tr'));

        // Mevcut seçimleri temizle (ilk option hariç)
        typeFilter.innerHTML = '<option value="">Tüm Tipler</option>';

        // Yeni seçenekleri ekle
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            typeFilter.appendChild(option);
        });
    }

    /**
     * İlçe filtresini güncelle (seçilen ile göre)
     */
    updateDistrictFilter(selectedCity) {
        const districtFilter = document.getElementById('district-filter');
        if (!districtFilter) return;

        districtFilter.innerHTML = '<option value="">Tüm İlçeler</option>';

        if (!selectedCity || !this.data) {
            districtFilter.disabled = true;
            return;
        }

        // Seçilen ildeki benzersiz ilçeleri al
        const districts = [...new Set(
            this.data.kurumlar
                .filter(k => k.il_adi === selectedCity)
                .map(k => k.ilce_adi)
                .filter(district => district && district.trim())
        )].sort((a, b) => a.localeCompare(b, 'tr'));

        if (districts.length > 0) {
            districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district;
                option.textContent = district;
                districtFilter.appendChild(option);
            });
            districtFilter.disabled = false;
        } else {
            districtFilter.disabled = true;
        }
    }

    /**
     * Sonuçları render et
     */
    renderResults() {
        if (!this.filteredData) return;

        const resultsGrid = document.getElementById('results-grid');
        const resultsCount = document.getElementById('results-count');
        const noResults = document.getElementById('no-results');

        if (!resultsGrid) return;

        // Sonuç sayısını güncelle
        if (resultsCount) {
            resultsCount.textContent = `${this.filteredData.length.toLocaleString('tr-TR')} kurum`;
        }

        // Sonuç yoksa
        if (this.filteredData.length === 0) {
            resultsGrid.style.display = 'none';
            if (noResults) noResults.style.display = 'block';
            return;
        }

        // No results gizle
        if (noResults) noResults.style.display = 'none';
        resultsGrid.style.display = 'grid';

        // Sayfalama hesapla
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.filteredData.slice(startIndex, endIndex);

        // Kartları render et
        resultsGrid.innerHTML = pageData.map(kurum => this.createInstitutionCard(kurum)).join('');

        // Sayfalamayı güncelle
        this.renderPagination();
    }

    /**
     * Kurum kartı oluştur
     */
    createInstitutionCard(kurum) {
        const hasCoordinates = kurum.koordinat_lat && kurum.koordinat_lon;
        const hasPhone = kurum.telefon && kurum.telefon.trim();
        const hasWebsite = kurum.web_sitesi && kurum.web_sitesi.trim();

        return `
            <div class="institution-card" data-id="${kurum.kurum_id}">
                <div class="card-header">
                    <div class="institution-type">${kurum.kurum_tipi}</div>
                    <button class="icon-button card-menu" title="Daha fazla">
                        <span class="material-symbols-outlined">more_vert</span>
                    </button>
                </div>
                
                <div class="card-content">
                    <h3 class="institution-name">${kurum.kurum_adi}</h3>
                    
                    <div class="institution-location">
                        <span class="material-symbols-outlined location-icon">location_on</span>
                        <span>${kurum.ilce_adi}, ${kurum.il_adi}</span>
                    </div>
                    
                    ${kurum.adres ? `
                        <div class="institution-address">
                            <span class="material-symbols-outlined">home</span>
                            <span>${kurum.adres}</span>
                        </div>
                    ` : ''}
                </div>
                
                <div class="card-actions">
                    ${hasPhone ? `
                        <button class="action-button" onclick="window.open('tel:${kurum.telefon}')">
                            <span class="material-symbols-outlined">call</span>
                            <span>Ara</span>
                        </button>
                    ` : ''}
                    
                    ${hasWebsite ? `
                        <button class="action-button" onclick="window.open('${kurum.web_sitesi}', '_blank')">
                            <span class="material-symbols-outlined">language</span>
                            <span>Web</span>
                        </button>
                    ` : ''}
                    
                    ${hasCoordinates ? `
                        <button class="action-button" onclick="window.open('https://maps.google.com/?q=${kurum.koordinat_lat},${kurum.koordinat_lon}', '_blank')">
                            <span class="material-symbols-outlined">directions</span>
                            <span>Yol Tarifi</span>
                        </button>
                    ` : ''}
                    
                    <button class="action-button primary" onclick="showInstitutionDetail('${kurum.kurum_id}')">
                        <span class="material-symbols-outlined">info</span>
                        <span>Detaylar</span>
                    </button>
                </div>
            </div>
        `;
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

        let paginationHTML = '';

        // Önceki sayfa
        if (this.currentPage > 1) {
            paginationHTML += `
                <button class="pagination-button" onclick="dataLoader.goToPage(${this.currentPage - 1})">
                    <span class="material-symbols-outlined">chevron_left</span>
                </button>
            `;
        }

        // Sayfa numaraları
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        if (startPage > 1) {
            paginationHTML += `<button class="pagination-button" onclick="dataLoader.goToPage(1)">1</button>`;
            if (startPage > 2) {
                paginationHTML += `<span class="pagination-ellipsis">...</span>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button class="pagination-button ${i === this.currentPage ? 'active' : ''}" 
                        onclick="dataLoader.goToPage(${i})">${i}</button>
            `;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<span class="pagination-ellipsis">...</span>`;
            }
            paginationHTML += `<button class="pagination-button" onclick="dataLoader.goToPage(${totalPages})">${totalPages}</button>`;
        }

        // Sonraki sayfa
        if (this.currentPage < totalPages) {
            paginationHTML += `
                <button class="pagination-button" onclick="dataLoader.goToPage(${this.currentPage + 1})">
                    <span class="material-symbols-outlined">chevron_right</span>
                </button>
            `;
        }

        pagination.innerHTML = paginationHTML;
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
     * Kurum detayını ID ile al
     */
    getInstitutionById(id) {
        if (!this.data) return null;
        return this.data.kurumlar.find(k => k.kurum_id === id);
    }
}

// Global instance
const dataLoader = new DataLoader();
