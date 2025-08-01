import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase } from '../lib/supabase'

/**
 * Sağlık kuruluşlarını getir
 * Talimatnameler/mimari.md'deki akıllı arama ve filtreleme destekli
 */
export function useInstitutions(filters = {}) {
  return useQuery({
    queryKey: ['institutions', filters],
    queryFn: async () => {
      let query = supabase
        .from('kuruluslar')
        .select('*')
        .eq('aktif', true)

      // Filtreler uygula
      if (filters.search) {
        query = query.or(`isim_standart.ilike.%${filters.search}%,adres_yapilandirilmis->>il.ilike.%${filters.search}%,adres_yapilandirilmis->>ilce.ilike.%${filters.search}%`)
      }

      if (filters.il) {
        query = query.eq('adres_yapilandirilmis->>il', filters.il)
      }

      if (filters.ilce) {
        query = query.eq('adres_yapilandirilmis->>ilce', filters.ilce)
      }

      if (filters.tip && filters.tip.length > 0) {
        query = query.in('tip', filters.tip)
      }

      // Coğrafi sınırlama (harita "Bu Alanda Ara" özelliği için)
      if (filters.bounds) {
        const { northEast, southWest } = filters.bounds
        // PostGIS ST_MakeEnvelope kullanarak
        query = query.rpc('institutions_within_bounds', {
          ne_lat: northEast.lat,
          ne_lng: northEast.lng,
          sw_lat: southWest.lat,
          sw_lng: southWest.lng
        })
      }

      // Mesafe filtresi (kullanıcı konumuna göre)
      if (filters.nearLocation && filters.radius) {
        query = query.rpc('institutions_near_location', {
          lat: filters.nearLocation.lat,
          lng: filters.nearLocation.lng,
          radius_km: filters.radius
        })
      }

      // Sıralama
      const orderBy = filters.sortBy || 'isim_standart'
      const ascending = filters.sortOrder !== 'desc'
      query = query.order(orderBy, { ascending })

      // Sayfalama
      if (filters.page && filters.pageSize) {
        const from = (filters.page - 1) * filters.pageSize
        const to = from + filters.pageSize - 1
        query = query.range(from, to)
      }

      const { data, error, count } = await query

      if (error) {
        throw new Error(`Kurum verileri alınamadı: ${error.message}`)
      }

      return {
        institutions: data || [],
        total: count || data?.length || 0
      }
    },
    staleTime: 5 * 60 * 1000, // 5 dakika
    cacheTime: 10 * 60 * 1000, // 10 dakika
  })
}

/**
 * Tek bir kurum detayını getir
 */
export function useInstitution(id) {
  return useQuery({
    queryKey: ['institution', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('kuruluslar')
        .select('*')
        .eq('id', id)
        .single()

      if (error) {
        throw new Error(`Kurum detayı alınamadı: ${error.message}`)
      }

      return data
    },
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 dakika
  })
}

/**
 * İl listesini getir (filtreleme için)
 */
export function useProvinces() {
  return useQuery({
    queryKey: ['provinces'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('kuruluslar')
        .select('adres_yapilandirilmis->>il')
        .not('adres_yapilandirilmis->>il', 'is', null)
        .eq('aktif', true)

      if (error) {
        throw new Error(`İl listesi alınamadı: ${error.message}`)
      }

      // Unique iller ve sayıları
      const provinces = data
        .map(item => item.il)
        .filter(Boolean)
        .reduce((acc, il) => {
          acc[il] = (acc[il] || 0) + 1
          return acc
        }, {})

      return Object.entries(provinces)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => a.name.localeCompare(b.name, 'tr'))
    },
    staleTime: 15 * 60 * 1000, // 15 dakika
  })
}

/**
 * İlçe listesini getir (seçili ile göre)
 */
export function useDistricts(selectedProvince) {
  return useQuery({
    queryKey: ['districts', selectedProvince],
    queryFn: async () => {
      let query = supabase
        .from('kuruluslar')
        .select('adres_yapilandirilmis->>ilce')
        .not('adres_yapilandirilmis->>ilce', 'is', null)
        .eq('aktif', true)

      if (selectedProvince) {
        query = query.eq('adres_yapilandirilmis->>il', selectedProvince)
      }

      const { data, error } = await query

      if (error) {
        throw new Error(`İlçe listesi alınamadı: ${error.message}`)
      }

      // Unique ilçeler ve sayıları
      const districts = data
        .map(item => item.ilce)
        .filter(Boolean)
        .reduce((acc, ilce) => {
          acc[ilce] = (acc[ilce] || 0) + 1
          return acc
        }, {})

      return Object.entries(districts)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => a.name.localeCompare(b.name, 'tr'))
    },
    enabled: !!selectedProvince,
    staleTime: 15 * 60 * 1000, // 15 dakika
  })
}

/**
 * Kurum tiplerini getir (filtreleme için)
 */
export function useInstitutionTypes() {
  return useQuery({
    queryKey: ['institution-types'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('kuruluslar')
        .select('tip')
        .not('tip', 'is', null)
        .eq('aktif', true)

      if (error) {
        throw new Error(`Kurum tipleri alınamadı: ${error.message}`)
      }

      // Unique tipler ve sayıları
      const types = data
        .map(item => item.tip)
        .filter(Boolean)
        .reduce((acc, tip) => {
          acc[tip] = (acc[tip] || 0) + 1
          return acc
        }, {})

      return Object.entries(types)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count) // Sayıya göre sırala
    },
    staleTime: 15 * 60 * 1000, // 15 dakika
  })
}

/**
 * İstatistikler getir (dashboard için)
 */
export function useStatistics() {
  return useQuery({
    queryKey: ['statistics'],
    queryFn: async () => {
      // Toplam kurum sayısı
      const { count: totalCount, error: totalError } = await supabase
        .from('kuruluslar')
        .select('*', { count: 'exact', head: true })
        .eq('aktif', true)

      if (totalError) {
        throw new Error(`İstatistik alınamadı: ${totalError.message}`)
      }

      // Tip bazında sayılar
      const { data: typeData, error: typeError } = await supabase
        .from('kuruluslar')
        .select('tip')
        .eq('aktif', true)

      if (typeError) {
        throw new Error(`Tip istatistikleri alınamadı: ${typeError.message}`)
      }

      const typeStats = typeData
        .filter(item => item.tip)
        .reduce((acc, item) => {
          acc[item.tip] = (acc[item.tip] || 0) + 1
          return acc
        }, {})

      // İl bazında sayılar (top 10)
      const { data: provinceData, error: provinceError } = await supabase
        .from('kuruluslar')
        .select('adres_yapilandirilmis->>il')
        .eq('aktif', true)

      if (provinceError) {
        throw new Error(`İl istatistikleri alınamadı: ${provinceError.message}`)
      }

      const provinceStats = provinceData
        .map(item => item.il)
        .filter(Boolean)
        .reduce((acc, il) => {
          acc[il] = (acc[il] || 0) + 1
          return acc
        }, {})

      const topProvinces = Object.entries(provinceStats)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([name, count]) => ({ name, count }))

      return {
        total: totalCount,
        byType: typeStats,
        topProvinces
      }
    },
    staleTime: 30 * 60 * 1000, // 30 dakika
  })
}

/**
 * Veri güncelleme mutation (gelecekteki kullanıcı katkısı için)
 */
export function useUpdateInstitution() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, updates }) => {
      const { data, error } = await supabase
        .from('kuruluslar')
        .update(updates)
        .eq('id', id)
        .select()
        .single()

      if (error) {
        throw new Error(`Kurum güncellenemedi: ${error.message}`)
      }

      return data
    },
    onSuccess: (data) => {
      // Cache'i güncelle
      queryClient.invalidateQueries({ queryKey: ['institutions'] })
      queryClient.setQueryData(['institution', data.id], data)
    },
  })
}
