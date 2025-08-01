/**
 * TURSAKUR 2.0 - Supabase Configuration
 * =====================================
 * 
 * Frontend Supabase client konfigürasyonu
 */

// Supabase client import (CDN'den yüklenecek)
// <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>

class SupabaseConfig {
    constructor() {
        // Supabase credentials (production'da environment variables'dan gelecek)
        this.supabaseUrl = 'https://your-project-id.supabase.co';
        this.supabaseAnonKey = 'your-anon-key-here';
        
        // Supabase client initialize
        this.supabase = null;
        this.isInitialized = false;
        
        this.init();
    }
    
    async init() {
        try {
            // Check if Supabase is loaded
            if (typeof window.supabase === 'undefined') {
                console.warn('⚠️ Supabase client yüklenmedi, test modu çalışıyor');
                this.initTestMode();
                return;
            }
            
            // Initialize Supabase client
            this.supabase = window.supabase.createClient(
                this.supabaseUrl, 
                this.supabaseAnonKey
            );
            
            this.isInitialized = true;
            console.log('✅ Supabase client başlatıldı');
            
        } catch (error) {
            console.error('❌ Supabase initialization hatası:', error);
            this.initTestMode();
        }
    }
    
    initTestMode() {
        console.log('📋 Test modu - Mock Supabase client');
        this.isInitialized = true;
        
        // Mock Supabase client
        this.supabase = {
            from: (table) => ({
                select: (columns = '*') => ({
                    execute: () => this.getMockData(table, columns)
                }),
                eq: (column, value) => ({
                    execute: () => this.getMockFilteredData(table, column, value)
                }),
                range: (from, to) => ({
                    execute: () => this.getMockPaginatedData(table, from, to)
                })
            })
        };
    }
    
    // Test data for development
    getMockData(table, columns) {
        if (table === 'health_facilities') {
            return Promise.resolve({
                data: [
                    {
                        id: 1,
                        name: 'Ankara Şehir Hastanesi',
                        facility_type: 'Şehir Hastanesi',
                        province: 'Ankara',
                        district: 'Çankaya',
                        address: 'Ankara Şehir Hastanesi, Çankaya/Ankara',
                        phone: '0312 xxx xxxx',
                        website: 'https://ankarashehir.saglik.gov.tr',
                        latitude: 39.9334,
                        longitude: 32.8597,
                        sources: ['saglik_bakanligi']
                    },
                    {
                        id: 2,
                        name: 'Hacettepe Üniversitesi Hastanesi',
                        facility_type: 'Üniversite Hastanesi',
                        province: 'Ankara',
                        district: 'Altındağ',
                        address: 'Hacettepe Üniversitesi, Altındağ/Ankara',
                        phone: '0312 305 xxxx',
                        website: 'https://www.hacettepe.edu.tr',
                        latitude: 39.9400,
                        longitude: 32.8600,
                        sources: ['universite_hastaneleri']
                    },
                    {
                        id: 3,
                        name: 'İstanbul Şişli Etfal Hastanesi',
                        facility_type: 'Devlet Hastanesi',
                        province: 'İstanbul',
                        district: 'Şişli',
                        address: 'Şişli Etfal Hastanesi, Şişli/İstanbul',
                        phone: '0212 xxx xxxx',
                        website: 'https://sislientfal.saglik.gov.tr',
                        latitude: 41.0500,
                        longitude: 28.9800,
                        sources: ['saglik_bakanligi']
                    }
                ],
                error: null
            });
        }
        
        return Promise.resolve({ data: [], error: null });
    }
    
    getMockFilteredData(table, column, value) {
        return this.getMockData(table).then(result => {
            const filtered = result.data.filter(item => 
                item[column] && item[column].toLowerCase().includes(value.toLowerCase())
            );
            return { data: filtered, error: null };
        });
    }
    
    getMockPaginatedData(table, from, to) {
        return this.getMockData(table).then(result => {
            const paginated = result.data.slice(from, to + 1);
            return { data: paginated, error: null };
        });
    }
    
    // Public API methods
    async getHealthFacilities(filters = {}) {
        if (!this.isInitialized) {
            await this.init();
        }
        
        try {
            let query = this.supabase.from('health_facilities').select('*');
            
            // Apply filters
            if (filters.province) {
                query = query.eq('province', filters.province);
            }
            
            if (filters.facility_type) {
                query = query.eq('facility_type', filters.facility_type);
            }
            
            if (filters.search) {
                query = query.or(`name.ilike.%${filters.search}%,address.ilike.%${filters.search}%`);
            }
            
            // Pagination
            if (filters.limit) {
                const from = (filters.page || 0) * filters.limit;
                const to = from + filters.limit - 1;
                query = query.range(from, to);
            }
            
            const result = await query.execute();
            
            if (result.error) {
                console.error('Supabase sorgu hatası:', result.error);
                return { data: [], error: result.error };
            }
            
            return { data: result.data || [], error: null };
            
        } catch (error) {
            console.error('getHealthFacilities hatası:', error);
            return { data: [], error: error.message };
        }
    }
    
    async getProvinces() {
        if (!this.isInitialized) {
            await this.init();
        }
        
        try {
            // Get distinct provinces
            const result = await this.supabase
                .from('health_facilities')
                .select('province')
                .execute();
            
            if (result.error) {
                console.error('Province sorgu hatası:', result.error);
                return ['Ankara', 'İstanbul', 'İzmir']; // Fallback
            }
            
            // Extract unique provinces
            const provinces = [...new Set(result.data.map(item => item.province))];
            return provinces.sort();
            
        } catch (error) {
            console.error('getProvinces hatası:', error);
            return ['Ankara', 'İstanbul', 'İzmir']; // Fallback
        }
    }
    
    async getFacilityTypes() {
        if (!this.isInitialized) {
            await this.init();
        }
        
        try {
            const result = await this.supabase
                .from('health_facilities')
                .select('facility_type')
                .execute();
            
            if (result.error) {
                return [
                    'Devlet Hastanesi',
                    'Üniversite Hastanesi',
                    'Özel Hastane',
                    'Şehir Hastanesi'
                ]; // Fallback
            }
            
            const types = [...new Set(result.data.map(item => item.facility_type))];
            return types.sort();
            
        } catch (error) {
            console.error('getFacilityTypes hatası:', error);
            return ['Devlet Hastanesi', 'Üniversite Hastanesi']; // Fallback
        }
    }
}

// Global instance
window.tursakurSupabase = new SupabaseConfig();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupabaseConfig;
}
