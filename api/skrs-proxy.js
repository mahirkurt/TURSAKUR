/**
 * SKRS Proxy API Endpoint
 * CORS sorununu çözmek için backend proxy servisi
 * Vercel Edge Functions kullanır
 */

export const config = {
  runtime: 'edge',
};

// SKRS WSDL Endpoint'leri
const SKRS_ENDPOINTS = {
  KURUM_KURULUS: 'https://skrs.saglik.gov.tr/servis/SKRSKurumveKurulus.svc',
  IL: 'https://skrs.saglik.gov.tr/servis/SKRSIl.svc',
  KLINIK_KODLARI: 'https://skrs.saglik.gov.tr/servis/SKRSKlinikKodlari.svc'
};

// SOAP XML Template'leri
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
 * SOAP isteği gönder (Backend'de)
 */
async function sendSOAPRequest(endpoint, soapAction, xmlBody) {
  try {
    console.log(`📡 SKRS SOAP isteği: ${endpoint}`);
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': soapAction,
        'Accept': 'text/xml',
        'User-Agent': 'TURSAKUR-SKRS-Client/1.0'
      },
      body: xmlBody
    });

    if (!response.ok) {
      throw new Error(`SKRS API Hatası: ${response.status} ${response.statusText}`);
    }

    const xmlText = await response.text();
    console.log(`✅ SKRS yanıt alındı, boyut: ${xmlText.length} karakter`);
    
    return xmlText;
  } catch (error) {
    console.error('❌ SOAP İsteği Hatası:', error);
    throw new Error(`SKRS servisi ile bağlantı kurulamadı: ${error.message}`);
  }
}

/**
 * XML'den JSON'a dönüştür
 */
function parseXMLToJSON(xmlText) {
  try {
    // Basit XML parsing (production'da daha güçlü parser kullanılmalı)
    const results = [];
    
    // XML içeriğini satırlara böl ve veri çıkar
    const lines = xmlText.split('\n');
    let currentItem = {};
    let inItem = false;
    
    for (const line of lines) {
      const trimmed = line.trim();
      
      // Item başlangıcı
      if (trimmed.includes('<') && (
        trimmed.includes('KurumKurulus') ||
        trimmed.includes('Il>') ||
        trimmed.includes('KlinikKod')
      )) {
        if (Object.keys(currentItem).length > 0) {
          results.push({ ...currentItem });
        }
        currentItem = {};
        inItem = true;
      }
      
      // Veri alanları
      if (inItem && trimmed.includes('<') && trimmed.includes('>')) {
        const tagMatch = trimmed.match(/<([^>]+)>([^<]*)<\/[^>]+>/);
        if (tagMatch) {
          const [, tagName, value] = tagMatch;
          currentItem[tagName] = value;
        }
      }
    }
    
    // Son item'i ekle
    if (Object.keys(currentItem).length > 0) {
      results.push(currentItem);
    }
    
    console.log(`🔄 XML parse tamamlandı: ${results.length} kayıt`);
    return results;
    
  } catch (error) {
    console.error('❌ XML Parse Hatası:', error);
    throw new Error(`XML işleme hatası: ${error.message}`);
  }
}

/**
 * Main API Handler
 */
export default async function handler(request) {
  // CORS Headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Content-Type': 'application/json'
  };

  // Preflight OPTIONS request
  if (request.method === 'OPTIONS') {
    return new Response(null, { 
      status: 200, 
      headers: corsHeaders 
    });
  }

  try {
    const url = new URL(request.url);
    const service = url.searchParams.get('service');
    
    if (!service) {
      return new Response(
        JSON.stringify({ 
          error: 'Service parametresi gerekli. Kullanım: ?service=kurum|il|klinik' 
        }), 
        { 
          status: 400, 
          headers: corsHeaders 
        }
      );
    }

    let endpoint, soapAction, xmlBody, serviceName;

    switch (service.toLowerCase()) {
      case 'kurum':
        endpoint = SKRS_ENDPOINTS.KURUM_KURULUS;
        soapAction = 'http://tempuri.org/SKRSKurumveKuruluslariGetir';
        xmlBody = SOAP_TEMPLATES.KURUM_KURULUS;
        serviceName = 'KURUM_KURULUS';
        break;
        
      case 'il':
        endpoint = SKRS_ENDPOINTS.IL;
        soapAction = 'http://tempuri.org/SKRSIlleriGetir';
        xmlBody = SOAP_TEMPLATES.IL;
        serviceName = 'IL';
        break;
        
      case 'klinik':
        endpoint = SKRS_ENDPOINTS.KLINIK_KODLARI;
        soapAction = 'http://tempuri.org/SKRSKlinikKodlariniGetir';
        xmlBody = SOAP_TEMPLATES.KLINIK_KODLARI;
        serviceName = 'KLINIK_KODLARI';
        break;
        
      default:
        return new Response(
          JSON.stringify({ 
            error: 'Geçersiz servis. Kullanılabilir: kurum, il, klinik' 
          }), 
          { 
            status: 400, 
            headers: corsHeaders 
          }
        );
    }

    console.log(`🚀 SKRS ${serviceName} servisi çağrılıyor...`);

    // SOAP isteği gönder
    const xmlResponse = await sendSOAPRequest(endpoint, soapAction, xmlBody);
    
    // XML'i JSON'a dönüştür
    const jsonData = parseXMLToJSON(xmlResponse);
    
    const response = {
      success: true,
      service: serviceName,
      count: jsonData.length,
      data: jsonData,
      timestamp: new Date().toISOString()
    };

    console.log(`✅ SKRS ${serviceName} başarıyla tamamlandı: ${jsonData.length} kayıt`);

    return new Response(
      JSON.stringify(response), 
      { 
        status: 200, 
        headers: corsHeaders 
      }
    );

  } catch (error) {
    console.error('❌ SKRS Proxy Hatası:', error);
    
    return new Response(
      JSON.stringify({ 
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      }), 
      { 
        status: 500, 
        headers: corsHeaders 
      }
    );
  }
}
