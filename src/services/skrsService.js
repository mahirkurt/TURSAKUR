/**
 * SKRS (Sağlık Kodlama Referans Servisi) Entegrasyon Modülü
 * Sağlık Bakanlığı'nın resmi WSDL servislerini kullanır
 * 
 * Servisler:
 * - SKRSKurumveKurulus: Tüm sağlık kurum ve kuruluşları
 * - SKRSIl: 81 ilin standart kodları
 * - SKRSKlinikKodlari: Tıp branşları
 */

import { supabase } from '../lib/supabase';

// SKRS WSDL Endpoint'leri
const SKRS_ENDPOINTS = {
  KURUM_KURULUS: 'https://skrs.saglik.gov.tr/servis/SKRSKurumveKurulus.svc?wsdl',
  IL: 'https://skrs.saglik.gov.tr/servis/SKRSIl.svc?wsdl',
  KLINIK_KODLARI: 'https://skrs.saglik.gov.tr/servis/SKRSKlinikKodlari.svc?wsdl'
};

// SOAP istekleri için XML template'leri
const SOAP_TEMPLATES = {
  KURUM_KURULUS: `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <SKRSKurumveKuruluslariGetir xmlns="http://tempuri.org/" />
  </soap:Body>
</soap:Envelope>`,

  IL: `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <SKRSIlleriGetir xmlns="http://tempuri.org/" />
  </soap:Body>
</soap:Envelope>`,

  KLINIK_KODLARI: `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <SKRSKlinikKodlariniGetir xmlns="http://tempuri.org/" />
  </soap:Body>
</soap:Envelope>`
};

/**
 * SOAP isteği gönder
 * @param {string} endpoint - WSDL endpoint'i
 * @param {string} soapAction - SOAP Action header'ı  
 * @param {string} xmlBody - SOAP XML body
 * @returns {Promise<Document>} XML response
 */
async function sendSOAPRequest(endpoint, soapAction, xmlBody) {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': soapAction,
        'Accept': 'text/xml'
      },
      body: xmlBody
    });

    if (!response.ok) {
      throw new Error(`SKRS API Hatası: ${response.status} ${response.statusText}`);
    }

    const xmlText = await response.text();
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
    
    // XML parsing hatalarını kontrol et
    const parseError = xmlDoc.querySelector('parsererror');
    if (parseError) {
      throw new Error(`XML Parse Hatası: ${parseError.textContent}`);
    }

    return xmlDoc;
  } catch (error) {
    console.error('SOAP İsteği Hatası:', error);
    throw new Error(`SKRS servisi ile bağlantı kurulamadı: ${error.message}`);
  }
}

/**
 * XML'den veri çıkar
 * @param {Document} xmlDoc - XML document
 * @param {string} tagName - Çıkarılacak tag adı
 * @returns {Array} Veri dizisi
 */
function extractDataFromXML(xmlDoc, tagName) {
  const items = xmlDoc.querySelectorAll(tagName);
  const data = [];
  
  items.forEach(item => {
    const obj = {};
    Array.from(item.children).forEach(child => {
      obj[child.tagName] = child.textContent;
    });
    data.push(obj);
  });
  
  return data;
}

/**
 * SKRS'den tüm sağlık kurum ve kuruluşlarını getir
 * @returns {Promise<Array>} Kurum listesi
 */
export async function fetchSKRSInstitutions() {
  console.log('🏥 SKRS Kurum ve Kuruluşlar getiriliyor...');
  
  const xmlDoc = await sendSOAPRequest(
    SKRS_ENDPOINTS.KURUM_KURULUS.replace('?wsdl', ''),
    'http://tempuri.org/SKRSKurumveKuruluslariGetir',
    SOAP_TEMPLATES.KURUM_KURULUS
  );
  
  // XML'den kurum verilerini çıkar
  const institutions = extractDataFromXML(xmlDoc, 'KurumKurulus');
  
  console.log(`✅ SKRS'den ${institutions.length} kurum alındı`);
  return institutions;
}

/**
 * SKRS'den tüm illeri getir
 * @returns {Promise<Array>} İl listesi
 */
export async function fetchSKRSProvinces() {
  console.log('📍 SKRS İller getiriliyor...');
  
  const xmlDoc = await sendSOAPRequest(
    SKRS_ENDPOINTS.IL.replace('?wsdl', ''),
    'http://tempuri.org/SKRSIlleriGetir',
    SOAP_TEMPLATES.IL
  );
  
  const provinces = extractDataFromXML(xmlDoc, 'Il');
  
  console.log(`✅ SKRS'den ${provinces.length} il alındı`);
  return provinces;
}

/**
 * SKRS'den tüm tıp branşlarını getir
 * @returns {Promise<Array>} Branş listesi
 */
export async function fetchSKRSSpecialties() {
  console.log('🩺 SKRS Klinik Kodları getiriliyor...');
  
  const xmlDoc = await sendSOAPRequest(
    SKRS_ENDPOINTS.KLINIK_KODLARI.replace('?wsdl', ''),
    'http://tempuri.org/SKRSKlinikKodlariniGetir',
    SOAP_TEMPLATES.KLINIK_KODLARI
  );
  
  const specialties = extractDataFromXML(xmlDoc, 'KlinikKod');
  
  console.log(`✅ SKRS'den ${specialties.length} branş alındı`);
  return specialties;
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
