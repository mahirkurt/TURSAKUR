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
            const count = uniqueProvinces.size;
            totalProvinces.textContent = count;
            
            // 81 il kontrolü - görsel feedback
            const provincesContainer = totalProvinces.closest('.stat-card');
            if (provincesContainer) {
                if (count === 81) {
                    provincesContainer.style.background = 'linear-gradient(135deg, #4CAF50, #66BB6A)';
                    provincesContainer.style.color = 'white';
                    provincesContainer.title = 'Türkiye\'nin tüm 81 ili kapsanıyor! 🎉';
                } else {
                    provincesContainer.style.background = '';
                    provincesContainer.style.color = '';
                    provincesContainer.title = `${count} il kapsanıyor (81 hedef)`;
                }
            }
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

        if (!resultsContainer) return;

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

        // Kartları render et
        resultsContainer.innerHTML = `
            <div class="results-grid">
                ${pageData.map(kurum => this.createInstitutionCard(kurum)).join('')}
            </div>
        `;

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
                </div>
                
                <div class="card-content">
                    <h3 class="institution-name">${kurum.kurum_adi}</h3>
                    
                    <div class="institution-location">
                        <span class="material-symbols-outlined">location_on</span>
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
                        </button>
                    ` : ''}
                    
                    ${hasWebsite ? `
                        <button class="action-button" onclick="window.open('${kurum.web_sitesi}', '_blank')">
                            <span class="material-symbols-outlined">language</span>
                        </button>
                    ` : ''}
                    
                    ${hasCoordinates ? `
                        <button class="action-button" onclick="window.open('https://maps.google.com/?q=${kurum.koordinat_lat},${kurum.koordinat_lon}', '_blank')">
                            <span class="material-symbols-outlined">directions</span>
                        </button>
                    ` : ''}
                    
                    <button class="action-button primary" onclick="showInstitutionDetail('${kurum.kurum_id}')">
                        <span class="material-symbols-outlined">info</span>
                    </button>
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
}

// Global instance
const dataLoader = new DataLoader();
