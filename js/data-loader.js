/* eslint-env browser, node */
/**
 * TURSAKUR 2.0 - Data Loader
 * ===========================
 * 
 * Supabase'den veri çeken ve UI'ya besleyen modül
 */

class TursakurDataLoader {
    constructor() {
        this.supabase = window.tursakurSupabase;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
        
        // Event system
        this.eventTarget = new EventTarget();
        
        console.log('📊 TURSAKUR Data Loader başlatıldı');
    }
    
    // Event listeners
    on(event, callback) {
        this.eventTarget.addEventListener(event, callback);
    }
    
    emit(event, data) {
        this.eventTarget.dispatchEvent(new CustomEvent(event, { detail: data }));
    }
    
    // Cache management
    getCacheKey(method, params = {}) {
        return `${method}_${JSON.stringify(params)}`;
    }
    
    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        return null;
    }
    
    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
    
    // Main data loading methods
    async loadHealthFacilities(filters = {}) {
        const cacheKey = this.getCacheKey('facilities', filters);
        const cached = this.getFromCache(cacheKey);
        
        if (cached) {
            console.log('📋 Cache\'den veri yüklendi');
            this.emit('facilitiesLoaded', cached);
            return cached;
        }
        
        try {
            console.log('🔄 Sağlık kuruluşları yükleniyor...', filters);
            this.emit('loadingStarted', { type: 'facilities' });
            
            const result = await this.supabase.getHealthFacilities(filters);
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            const facilities = result.data || [];
            
            // Process and enrich data
            const processedFacilities = this.processFacilities(facilities);
            
            // Cache result
            this.setCache(cacheKey, processedFacilities);
            
            console.log(`✅ ${processedFacilities.length} sağlık kuruluşu yüklendi`);
            this.emit('facilitiesLoaded', processedFacilities);
            
            return processedFacilities;
            
        } catch (error) {
            console.error('❌ Veri yükleme hatası:', error);
            this.emit('loadingError', { type: 'facilities', error: error.message });
            return [];
        } finally {
            this.emit('loadingFinished', { type: 'facilities' });
        }
    }
    
    async loadProvinces() {
        const cacheKey = this.getCacheKey('provinces');
        const cached = this.getFromCache(cacheKey);
        
        if (cached) {
            return cached;
        }
        
        try {
            const provinces = await this.supabase.getProvinces();
            this.setCache(cacheKey, provinces);
            
            console.log(`📍 ${provinces.length} il yüklendi`);
            this.emit('provincesLoaded', provinces);
            
            return provinces;
            
        } catch (error) {
            console.error('❌ İl listesi yükleme hatası:', error);
            return ['Ankara', 'İstanbul', 'İzmir']; // Fallback
        }
    }
    
    async loadFacilityTypes() {
        const cacheKey = this.getCacheKey('facilityTypes');
        const cached = this.getFromCache(cacheKey);
        
        if (cached) {
            return cached;
        }
        
        try {
            const types = await this.supabase.getFacilityTypes();
            this.setCache(cacheKey, types);
            
            console.log(`🏥 ${types.length} kuruluş tipi yüklendi`);
            this.emit('facilityTypesLoaded', types);
            
            return types;
            
        } catch (error) {
            console.error('❌ Kuruluş tipi yükleme hatası:', error);
            return ['Devlet Hastanesi', 'Üniversite Hastanesi', 'Özel Hastane'];
        }
    }
    
    // Data processing
    processFacilities(facilities) {
        return facilities.map(facility => {
            // Add computed fields
            const processed = {
                ...facility,
                
                // Display name
                displayName: this.createDisplayName(facility),
                
                // Search text for filtering
                searchText: this.createSearchText(facility),
                
                // Coordinates validation
                hasValidCoordinates: this.hasValidCoordinates(facility),
                
                // Distance (will be calculated when needed)
                distance: null,
                
                // Contact info availability
                hasContact: !!(facility.phone || facility.website),
                
                // Source info
                sourceInfo: this.getSourceInfo(facility.sources || [])
            };
            
            return processed;
        });
    }
    
    createDisplayName(facility) {
        const parts = [];
        
        if (facility.name) {
            parts.push(facility.name);
        }
        
        if (facility.district && facility.province) {
            parts.push(`${facility.district}/${facility.province}`);
        } else if (facility.province) {
            parts.push(facility.province);
        }
        
        return parts.join(' - ');
    }
    
    createSearchText(facility) {
        const searchFields = [
            facility.name,
            facility.facility_type,
            facility.province,
            facility.district,
            facility.address
        ];
        
        return searchFields
            .filter(field => field)
            .join(' ')
            .toLowerCase()
            .replace(/[^\w\s]/gi, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }
    
    hasValidCoordinates(facility) {
        const lat = parseFloat(facility.latitude);
        const lng = parseFloat(facility.longitude);
        
        return !isNaN(lat) && !isNaN(lng) && 
               lat >= 35.5 && lat <= 42.5 && 
               lng >= 25.5 && lng <= 45.0;
    }
    
    getSourceInfo(sources) {
        const sourceLabels = {
            'saglik_bakanligi': 'Sağlık Bakanlığı',
            'sgk_anlasmali': 'SGK Anlaşmalı',
            'universite_hastaneleri': 'Üniversite',
            'ozel_hastane': 'Özel Hastane',
            'google_places': 'Google Places',
            'test_data': 'Test Verisi'
        };
        
        return sources.map(source => sourceLabels[source] || source);
    }
    
    // Search and filtering
    async searchFacilities(query, filters = {}) {
        if (!query || query.length < 2) {
            return this.loadHealthFacilities(filters);
        }
        
        const searchFilters = {
            ...filters,
            search: query
        };
        
        return this.loadHealthFacilities(searchFilters);
    }
    
    // Location-based queries
    async getFacilitiesNear(latitude, longitude, radiusKm = 10) {
        try {
            // Get all facilities first (in production, this would be a spatial query)
            const facilities = await this.loadHealthFacilities();
            
            // Filter by distance
            const nearbyFacilities = facilities
                .filter(facility => facility.hasValidCoordinates)
                .map(facility => {
                    const distance = this.calculateDistance(
                        latitude, longitude,
                        facility.latitude, facility.longitude
                    );
                    return { ...facility, distance };
                })
                .filter(facility => facility.distance <= radiusKm)
                .sort((a, b) => a.distance - b.distance);
            
            console.log(`📍 ${nearbyFacilities.length} yakın kuruluş bulundu (${radiusKm}km)`);
            this.emit('nearbyFacilitiesLoaded', nearbyFacilities);
            
            return nearbyFacilities;
            
        } catch (error) {
            console.error('❌ Yakın kuruluş arama hatası:', error);
            return [];
        }
    }
    
    // Distance calculation (Haversine formula)
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in kilometers
        const dLat = this.toRadians(lat2 - lat1);
        const dLon = this.toRadians(lon2 - lon1);
        
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
        
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    toRadians(degrees) {
        return degrees * (Math.PI / 180);
    }
    
    // Statistics
    async getStatistics() {
        try {
            const facilities = await this.loadHealthFacilities();
            
            const stats = {
                totalFacilities: facilities.length,
                byProvince: this.groupBy(facilities, 'province'),
                byType: this.groupBy(facilities, 'facility_type'),
                withCoordinates: facilities.filter(f => f.hasValidCoordinates).length,
                withContact: facilities.filter(f => f.hasContact).length,
                lastUpdated: new Date().toISOString()
            };
            
            console.log('📊 İstatistikler:', stats);
            this.emit('statisticsLoaded', stats);
            
            return stats;
            
        } catch (error) {
            console.error('❌ İstatistik hesaplama hatası:', error);
            return null;
        }
    }
    
    groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key] || 'Diğer';
            groups[group] = (groups[group] || 0) + 1;
            return groups;
        }, {});
    }
    
    // Cache management
    clearCache() {
        this.cache.clear();
        console.log('🗑️ Cache temizlendi');
    }
    
    // Initialization
    async initialize() {
        try {
            console.log('🚀 TURSAKUR Data Loader başlatılıyor...');
            
            // Wait for Supabase
            if (!this.supabase || !this.supabase.isInitialized) {
                await new Promise(resolve => {
                    const checkInterval = setInterval(() => {
                        if (this.supabase && this.supabase.isInitialized) {
                            clearInterval(checkInterval);
                            resolve();
                        }
                    }, 100);
                });
            }
            
            // Pre-load essential data
            await Promise.all([
                this.loadProvinces(),
                this.loadFacilityTypes()
            ]);
            
            console.log('✅ TURSAKUR Data Loader hazır');
            this.emit('initialized');
            
        } catch (error) {
            console.error('❌ Data Loader başlatma hatası:', error);
            this.emit('initializationError', error);
        }
    }
}

// Global instance
window.tursakurDataLoader = new TursakurDataLoader();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.tursakurDataLoader.initialize();
    });
} else {
    window.tursakurDataLoader.initialize();
}

// Export for module systems
/* eslint-disable no-undef */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TursakurDataLoader;
}
/* eslint-enable no-undef */
