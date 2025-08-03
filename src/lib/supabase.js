// TURSAKUR 2.0 - Supabase Client (Production Mode)
import { createClient } from '@supabase/supabase-js'

// Environment variables from .env file - REAL SUPABASE CREDENTIALS
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://moamwmxcpgjvyyawlygw.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vYW13bXhjcGdqdnl5YXdseWd3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwMzA1NzgsImV4cCI6MjA2OTYwNjU3OH0.w88NfzOopSYo8Q23ypWaknnaZcSXnV0WPtiE2-ePGfU'

// Create Supabase client with PRODUCTION credentials
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: false, // No authentication needed for this app
  },
  db: {
    schema: 'public'
  },
  global: {
    headers: {
      'Content-Type': 'application/json',
      'Prefer': 'return=representation'
    }
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})

// Enhanced query function with retry mechanism
export async function queryWithRetry(queryFn, maxRetries = 3, delay = 1000) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await queryFn()
      
      if (result.error) {
        if (attempt === maxRetries) {
          throw new Error(`Supabase query failed after ${maxRetries} attempts: ${result.error.message}`)
        }
        console.warn(`Query attempt ${attempt} failed:`, result.error.message)
        await new Promise(resolve => setTimeout(resolve, delay * attempt))
        continue
      }
      
      return result
    } catch (err) {
      if (attempt === maxRetries) {
        throw err
      }
      console.warn(`Query attempt ${attempt} failed:`, err.message)
      await new Promise(resolve => setTimeout(resolve, delay * attempt))
    }
  }
}

// Test mode fallback data
const TEST_FACILITIES = [
  {
    id: 1,
    name: 'Ankara Şehir Hastanesi',
    facility_type: 'Şehir Hastanesi',
    province: 'Ankara',
    district: 'Çankaya',
    address: 'Ankara Şehir Hastanesi, Bilkent/Ankara',
    phone: '0312 552 60 00',
    website: 'https://ankarashehir.saglik.gov.tr',
    latitude: 39.8667,
    longitude: 32.7333,
    sources: ['saglik_bakanligi']
  },
  {
    id: 2,
    name: 'Hacettepe Üniversitesi Hastanesi',
    facility_type: 'Üniversite Hastanesi',
    province: 'Ankara',
    district: 'Altındağ',
    address: 'Hacettepe Üniversitesi, Sıhhiye/Ankara',
    phone: '0312 305 10 00',
    website: 'https://www.hacettepe.edu.tr',
    latitude: 39.9400,
    longitude: 32.8600,
    sources: ['universite_hastaneleri']
  },
  {
    id: 3,
    name: 'Gazi Üniversitesi Hastanesi',
    facility_type: 'Üniversite Hastanesi',
    province: 'Ankara',
    district: 'Yenimahalle',
    address: 'Gazi Üniversitesi, Beşevler/Ankara',
    phone: '0312 202 50 00',
    website: 'https://www.gazi.edu.tr',
    latitude: 39.9100,
    longitude: 32.8000,
    sources: ['universite_hastaneleri']
  },
  {
    id: 4,
    name: 'İstanbul Şişli Etfal Hastanesi',
    facility_type: 'Devlet Hastanesi',
    province: 'İstanbul',
    district: 'Şişli',
    address: 'Şişli Etfal Hastanesi, Şişli/İstanbul',
    phone: '0212 373 50 00',
    website: 'https://sislientfal.saglik.gov.tr',
    latitude: 41.0500,
    longitude: 28.9800,
    sources: ['saglik_bakanligi']
  },
  {
    id: 5,
    name: 'Acıbadem Maslak Hastanesi',
    facility_type: 'Özel Hastane',
    province: 'İstanbul',
    district: 'Sarıyer',
    address: 'Büyükdere Cad. No:40, Maslak/İstanbul',
    phone: '0212 304 44 44',
    website: 'https://www.acibadem.com.tr',
    latitude: 41.1100,
    longitude: 29.0100,
    sources: ['ozel_hastane']
  },
  {
    id: 6,
    name: 'Ege Üniversitesi Hastanesi',
    facility_type: 'Üniversite Hastanesi',
    province: 'İzmir',
    district: 'Bornova',
    address: 'Ege Üniversitesi, Bornova/İzmir',
    phone: '0232 390 10 00',
    website: 'https://www.ege.edu.tr',
    latitude: 38.4600,
    longitude: 27.2200,
    sources: ['universite_hastaneleri']
  }
]

// API Functions with fallback to test data
export const healthFacilitiesAPI = {
  // Map Supabase kuruluslar table to frontend expected names
  mapRecordFromSupabase(record) {
    return {
      id: record.id,
      name: record.isim_standart || record.isim_resmi,
      facility_type: record.tip,
      province: record.adres_yapilandirilmis?.il || '',
      district: record.adres_yapilandirilmis?.ilce || '',
      address: record.adres_yapilandirilmis?.tam_adres || '',
      phone: record.iletisim?.telefon || '',
      website: record.iletisim?.website || '',
      latitude: null, // PostGIS koordinat ayrıştırması gerekir
      longitude: null, // PostGIS koordinat ayrıştırması gerekir
      sources: [record.metaveri?.kaynak || 'bilinmeyen'],
      created_at: record.created_at,
      updated_at: record.updated_at
    }
  },

  // Get all health facilities with optional filters
  async getAll(filters = {}) {
    try {
      let query = supabase.from('kuruluslar').select('*')
      
      // Apply filters using kuruluslar table JSONB structure
      if (filters.province) {
        query = query.eq('adres_yapilandirilmis->>il', filters.province)
      }
      
      if (filters.facility_type) {
        query = query.eq('tip', filters.facility_type)
      }
      
      if (filters.search) {
        query = query.or(`isim_standart.ilike.%${filters.search}%,adres_yapilandirilmis->>tam_adres.ilike.%${filters.search}%`)
      }
      
      // Only active facilities
      query = query.eq('aktif', true)
      
      // Pagination
      if (filters.limit) {
        const from = (filters.page || 0) * filters.limit
        const to = from + filters.limit - 1
        query = query.range(from, to)
      }
      
      const { data, error } = await query
      
      if (error) {
        console.warn('Supabase error, using test data:', error)
        return this.getTestData(filters)
      }
      
      // Map Supabase records to frontend format
      return (data || []).map(record => this.mapRecordFromSupabase(record))
      
    } catch (error) {
      console.warn('API error, using test data:', error)
      return this.getTestData(filters)
    }
  },
  
  // Get test data with filters applied
  getTestData(filters = {}) {
    let data = [...TEST_FACILITIES]
    
    if (filters.province) {
      data = data.filter(f => f.province === filters.province)
    }
    
    if (filters.facility_type) {
      data = data.filter(f => f.facility_type === filters.facility_type)
    }
    
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      data = data.filter(f => 
        f.name.toLowerCase().includes(searchLower) ||
        f.address.toLowerCase().includes(searchLower)
      )
    }
    
    if (filters.limit) {
      const start = (filters.page || 0) * filters.limit
      data = data.slice(start, start + filters.limit)
    }
    
    return data
  },
  
  // Get unique provinces
  async getProvinces() {
    try {
      const { data, error } = await supabase
        .from('kuruluslar')
        .select('adres_yapilandirilmis')
        .neq('adres_yapilandirilmis', null)
      
      if (error) {
        return [...new Set(TEST_FACILITIES.map(f => f.province))].sort()
      }
      
      const provinces = data
        .map(item => item.adres_yapilandirilmis?.il)
        .filter(il => il && il.trim())
      
      return [...new Set(provinces)].sort()
      
    } catch {
      return [...new Set(TEST_FACILITIES.map(f => f.province))].sort()
    }
  },
  
  // Get unique facility types
  async getFacilityTypes() {
    try {
      const { data, error } = await supabase
        .from('kuruluslar')
        .select('tip')
        .neq('tip', null)
      
      if (error) {
        return [...new Set(TEST_FACILITIES.map(f => f.facility_type))].sort()
      }
      
      return [...new Set(data.map(item => item.tip).filter(tip => tip))].sort()
      
    } catch {
      return [...new Set(TEST_FACILITIES.map(f => f.facility_type))].sort()
    }
  },
  
  // Get statistics
  async getStatistics() {
    try {
      const facilities = await this.getAll()
      
      const stats = {
        total: facilities.length,
        byProvince: this.groupBy(facilities, 'province'),
        byType: this.groupBy(facilities, 'facility_type'),
        withCoordinates: facilities.filter(f => f.latitude && f.longitude).length,
        withPhone: facilities.filter(f => f.phone).length,
        withWebsite: facilities.filter(f => f.website).length
      }
      
      return stats
      
    } catch (error) {
      console.error('Statistics error:', error)
      return {
        total: 0,
        byProvince: {},
        byType: {},
        withCoordinates: 0,
        withPhone: 0,
        withWebsite: 0
      }
    }
  },
  
  // Utility function to group array by key
  groupBy(array, key) {
    return array.reduce((groups, item) => {
      const group = item[key] || 'Diğer'
      groups[group] = (groups[group] || 0) + 1
      return groups
    }, {})
  }
}

export default supabase
