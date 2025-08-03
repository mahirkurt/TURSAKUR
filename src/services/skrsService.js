/**
 * SKRS (Sağlık Kodlama Referans Servisi) Entegrasyon Modülü
 * Sağlık Bakanlığı'nın resmi WSDL servislerini kullanır
 * CORS sorununu çözmek için backend proxy kullanır
 * 
 * Servisler:
 * - SKRSKurumveKurulus: Tüm sağlık kurum ve kuruluşları
 * - SKRSIl: 81 ilin standart kodları
 * - SKRSKlinikKodlari: Tıp branşları
 */

import { supabase } from '../lib/supabase';

// Proxy API endpoint (Vercel serverless function)
const PROXY_BASE_URL = '/api/skrs-proxy';

/**
 * Proxy API üzerinden SKRS servisini çağır
 * @param {string} service - Servis tipi (kurum, il, klinik)
 * @returns {Promise<Object>} API yanıtı
 */
async function callSKRSProxy(service) {
  try {
    console.log(`📡 SKRS ${service} servisi proxy üzerinden çağrılıyor...`);
    
    const response = await fetch(`${PROXY_BASE_URL}?service=${service}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Proxy API Hatası: ${response.status} - ${errorData.error || response.statusText}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(`SKRS Servisi Hatası: ${data.error}`);
    }
    
    console.log(`✅ SKRS ${service} başarıyla alındı: ${data.count} kayıt`);
    return data;
    
  } catch (error) {
    console.error(`❌ SKRS ${service} Hatası:`, error);
    throw new Error(`SKRS ${service} servisi çağrılamadı: ${error.message}`);
  }
}

/**
 * SKRS'den tüm sağlık kurum ve kuruluşlarını getir
 * @returns {Promise<Array>} Kurum listesi
 */
export async function fetchSKRSInstitutions() {
  console.log('🏥 SKRS Kurum ve Kuruluşlar getiriliyor...');
  
  const result = await callSKRSProxy('kurum');
  console.log(`✅ SKRS'den ${result.count} kurum alındı`);
  return result.data;
}

/**
 * SKRS'den tüm illeri getir
 * @returns {Promise<Array>} İl listesi
 */
export async function fetchSKRSProvinces() {
  console.log('📍 SKRS İller getiriliyor...');
  
  const result = await callSKRSProxy('il');
  console.log(`✅ SKRS'den ${result.count} il alındı`);
  return result.data;
}

/**
 * SKRS'den tüm tıp branşlarını getir
 * @returns {Promise<Array>} Branş listesi
 */
export async function fetchSKRSSpecialties() {
  console.log('🩺 SKRS Klinik Kodları getiriliyor...');
  
  const result = await callSKRSProxy('klinik');
  console.log(`✅ SKRS'den ${result.count} branş alındı`);
  return result.data;
}

/**
 * SKRS verilerini yerel formata dönüştür
 * @param {Array} skrsInstitutions - SKRS kurum verileri
 * @param {Array} skrsProvinces - SKRS il verileri
 * @returns {Array} Dönüştürülmüş veri
 */
export function transformSKRSData(skrsInstitutions, skrsProvinces) {
  console.log('🔄 SKRS verileri dönüştürülüyor...');
  
  // İl kodlarını mapping'e çevir
  const provinceMap = {};
  skrsProvinces.forEach(province => {
    provinceMap[province.KODU] = province.ADI;
  });
  
  // Kurumları dönüştür
  const transformedData = skrsInstitutions.map(institution => ({
    // SKRS orijinal alanları
    skrs_kodu: institution.KODU,
    skrs_adi: institution.ADI,
    skrs_il_kodu: institution.ILKODU,
    skrs_ilce_kodu: institution.ILCEKODU,
    skrs_kurum_tur_kodu: institution.KURUMTURKODU,
    
    // Mevcut sistemle uyumlu alanlar
    isim_standart: institution.ADI,
    tip: getInstitutionType(institution.KURUMTURKODU),
    adres_yapilandirilmis: {
      il: provinceMap[institution.ILKODU] || '',
      ilce: institution.ILCEKODU || '',
      skrs_il_kodu: institution.ILKODU,
      skrs_ilce_kodu: institution.ILCEKODU
    },
    metaveri: {
      kaynak: 'SKRS',
      guncelleme_tarihi: new Date().toISOString(),
      skrs_kurum_tur_kodu: institution.KURUMTURKODU,
      veri_kalitesi: 'resmi'
    },
    aktif: true,
    
    // Ek alanlar
    id: `skrs_${institution.KODU}`,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }));
  
  console.log(`✅ ${transformedData.length} kurum dönüştürüldü`);
  return transformedData;
}

/**
 * SKRS kurum türü kodunu anlamlı türe dönüştür
 * @param {string} kurumTurKodu - SKRS kurum tür kodu
 * @returns {string} Anlamlı tür adı
 */
function getInstitutionType(kurumTurKodu) {
  const typeMapping = {
    '1': 'Devlet Hastanesi',
    '2': 'Özel Hastane',
    '3': 'Üniversite Hastanesi',
    '4': 'Aile Sağlığı Merkezi',
    '5': 'Laboratuvar',
    '6': 'Eczane',
    '7': 'Sağlık Ocağı',
    '8': 'Diş Kliniği',
    '9': 'Fizik Tedavi Merkezi',
    '10': 'Diyaliz Merkezi'
  };
  
  return typeMapping[kurumTurKodu] || 'Sağlık Kuruluşu';
}

/**
 * SKRS verilerini Supabase'e kaydet
 * @param {Array} transformedData - Dönüştürülmüş SKRS verileri
 * @returns {Promise<Object>} Kaydetme sonucu
 */
export async function saveSKRSDataToSupabase(transformedData) {
  console.log('💾 SKRS verileri Supabase\'e kaydediliyor...');
  
  try {
    // Chunk'lara böl (Supabase limitleri için)
    const chunkSize = 1000;
    const chunks = [];
    
    for (let i = 0; i < transformedData.length; i += chunkSize) {
      chunks.push(transformedData.slice(i, i + chunkSize));
    }
    
    let totalInserted = 0;
    let totalErrors = 0;
    
    for (let i = 0; i < chunks.length; i++) {
      console.log(`📦 Chunk ${i + 1}/${chunks.length} kaydediliyor...`);
      
      const { error } = await supabase
        .from('kuruluslar')
        .upsert(chunks[i], { 
          onConflict: 'id',
          ignoreDuplicates: false 
        });
      
      if (error) {
        console.error(`❌ Chunk ${i + 1} kaydetme hatası:`, error);
        totalErrors += chunks[i].length;
      } else {
        totalInserted += chunks[i].length;
        console.log(`✅ Chunk ${i + 1} başarıyla kaydedildi`);
      }
    }
    
    const result = {
      success: totalErrors === 0,
      totalProcessed: transformedData.length,
      totalInserted,
      totalErrors,
      message: `SKRS entegrasyonu tamamlandı. ${totalInserted} kurum kaydedildi, ${totalErrors} hata.`
    };
    
    console.log('🎉 SKRS veri entegrasyonu tamamlandı:', result);
    return result;
    
  } catch (error) {
    console.error('❌ SKRS veri kaydetme hatası:', error);
    throw new Error(`Veri kaydetme başarısız: ${error.message}`);
  }
}

/**
 * Tam SKRS entegrasyonu çalıştır
 * @returns {Promise<Object>} Entegrasyon sonucu
 */
export async function runFullSKRSIntegration() {
  try {
    console.log('🚀 SKRS Tam Entegrasyonu başlatılıyor...');
    
    // 1. SKRS verilerini çek
    const [institutions, provinces, specialties] = await Promise.all([
      fetchSKRSInstitutions(),
      fetchSKRSProvinces(),
      fetchSKRSSpecialties()
    ]);
    
    // 2. Verileri dönüştür
    const transformedData = transformSKRSData(institutions, provinces);
    
    // 3. Supabase'e kaydet
    const saveResult = await saveSKRSDataToSupabase(transformedData);
    
    return {
      ...saveResult,
      skrsStats: {
        institutions: institutions.length,
        provinces: provinces.length,
        specialties: specialties.length
      }
    };
    
  } catch (error) {
    console.error('❌ SKRS Entegrasyonu Hatası:', error);
    throw error;
  }
}
