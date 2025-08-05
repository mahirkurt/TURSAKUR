/**
 * TURSAKUR 2.0 - Data Loader
 * ===========================
 * 
 * Lokal JSON dosyasından veri çeken ve UI'ya besleyen modül
 */

class TursakurDataLoader {
    constructor(jsonPath = 'data/turkiye_saglik_kuruluslari_merged.json') {
        this.jsonPath = jsonPath;
        this.allFacilities = [];
        this.isInitialized = false;
        console.log('📊 TURSAKUR Data Loader başlatıldı');
    }

    async _initializeData() {
        if (this.isInitialized) return;
        try {
            console.log(`Veri kaynağı yükleniyor: ${this.jsonPath}`);
            const response = await fetch(this.jsonPath);
            if (!response.ok) {
                throw new Error(`HTTP hatası! Durum: ${response.status}`);
            }
            const rawData = await response.json();
            
            // Veriyi normalize et: Türkçe anahtarları İngilizce'ye çevir ve ID'leri garantile
            this.allFacilities = rawData.map((facility, index) => ({
                id: facility.kurum_id || `tursakur-id-${index + 1}`,
                name: facility.kurum_adi,
                facility_type: facility.kurum_tipi,
                province: facility.il_adi,
                district: facility.ilce_adi,
                address: facility.adres,
                phone: facility.telefon,
                lat: facility.koordinat_lat,
                lon: facility.koordinat_lon,
                website: facility.web_sitesi,
                source: facility.veri_kaynagi,
                last_updated: facility.son_guncelleme,
                source_url: facility.kaynak_url
            }));

            this.isInitialized = true;
            console.log(`✅ ${this.allFacilities.length} sağlık kuruluşu başarıyla belleğe yüklendi ve normalize edildi.`);
        } catch (error) {
            console.error('❌ Ana veri kaynağı yüklenemedi:', error);
            this.allFacilities = [];
        }
    }
    
    async initializeApp() {
        await this._initializeData();
        // ID oluşturma mantığı _initializeData içine taşındığı için burası sadeleşti.
    }

    // Main data loading methods
    async loadHealthFacilities(filters = {}) {
        await this._initializeData();
        
        console.log('Sağlık kuruluşları filtreleniyor...', filters);
        
        let filteredData = [...this.allFacilities];

        // Arama filtresi (isim, il, ilçe, tip vb.)
        if (filters.search) {
            const query = filters.search.toLowerCase().trim();
            filteredData = filteredData.filter(f => 
                (f.name && f.name.toLowerCase().includes(query)) ||
                (f.province && f.province.toLowerCase().includes(query)) ||
                (f.district && f.district.toLowerCase().includes(query)) ||
                (f.facility_type && f.facility_type.toLowerCase().includes(query))
            );
        }

        // İl filtresi
        if (filters.province && filters.province !== 'all') {
            filteredData = filteredData.filter(f => f.province === filters.province);
        }

        // Kurum tipi filtresi
        if (filters.type && filters.type !== 'all') {
            filteredData = filteredData.filter(f => f.facility_type === filters.type);
        }
        
        console.log(`✅ Filtreleme sonucu: ${filteredData.length} kurum bulundu.`);
        return filteredData;
    }

    /**
     * Veri setindeki tüm benzersiz il (province) isimlerini döndürür.
     * @returns {Promise<Array<string>>} - Sıralanmış il isimleri dizisi.
     */
    async loadProvinces() {
        await this._initializeData();
        const provinces = new Set(this.allFacilities.map(f => f.province).filter(p => p));
        return [...provinces].sort((a, b) => a.localeCompare(b, 'tr'));
    }

    /**
     * Veri setindeki tüm benzersiz kurum tipi (facility_type) isimlerini döndürür.
     * @returns {Promise<Array<string>>} - Sıralanmış kurum tipi dizisi.
     */
    async loadFacilityTypes() {
        await this._initializeData();
        const types = new Set(this.allFacilities.map(f => f.facility_type).filter(t => t));
        return [...types].sort();
    }

    /**
     * Belirtilen ID'ye sahip sağlık kuruluşunu bulur.
     * @param {string} id - Aranacak kuruluşun ID'si.
     * @returns {Promise<Object|undefined>} - Bulunan kuruluş veya undefined.
     */
    async getFacilityById(id) {
        await this._initializeData();
        return this.allFacilities.find(f => f.id === id);
    }
}

// Global bir dataLoader örneği oluşturarak tüm scriptlerin erişebilmesini sağla
window.tursakurDataLoader = new TursakurDataLoader();
