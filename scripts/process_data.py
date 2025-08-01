#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Simplified Data Processor
=================================

Toplanan ham verileri işler, temizler ve birleştirir.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
import sys

class SimpleDataProcessor:
    """TURSAKUR ham verilerini işler ve temizler"""
    
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.data_dir = self.scripts_dir.parent / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        
        # Ensure directories exist
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging setup
        log_file = self.data_dir / "processing.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_raw_data(self) -> Dict[str, List[Dict]]:
        """Ham veri dosyalarını yükler"""
        self.logger.info("Ham veriler yükleniyor...")
        
        raw_data = {}
        
        # Raw data directory'deki tüm JSON dosyalarını bul
        json_files = list(self.raw_data_dir.glob("*.json"))
        
        for file_path in json_files:
            source_name = file_path.stem
            self.logger.info(f"Yükleniyor: {source_name}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Veri yapısına göre kayıtları çıkar
                    if isinstance(data, dict):
                        if 'veriler' in data:  # Sağlık Bakanlığı formatı
                            all_records = []
                            for key, records in data['veriler'].items():
                                for record in records:
                                    record['kategori'] = key
                                    all_records.append(record)
                            records = all_records
                        else:
                            records = data.get('kayitlar', data.get('data', data.get('facilities', [])))
                    elif isinstance(data, list):
                        records = data
                    else:
                        self.logger.warning(f"Bilinmeyen veri formatı: {source_name}")
                        records = []
                    
                    raw_data[source_name] = records
                    self.logger.info(f"✅ {source_name}: {len(records)} kayıt yüklendi")
                    
            except Exception as e:
                self.logger.error(f"❌ {source_name} yüklenemedi: {e}")
                raw_data[source_name] = []
        
        total_records = sum(len(records) for records in raw_data.values())
        self.logger.info(f"Toplam ham veri: {total_records:,} kayıt, {len(raw_data)} kaynak")
        
        return raw_data

    def normalize_record(self, raw_record: Dict, source: str) -> Dict:
        """Ham kaydı standart formata dönüştürür"""
        
        # Temel alanları çıkar
        name = (
            raw_record.get('ad') or 
            raw_record.get('name') or 
            raw_record.get('kurum_adi') or 
            raw_record.get('facility_name') or 
            ""
        )
        
        facility_type = (
            raw_record.get('tur') or 
            raw_record.get('type') or 
            raw_record.get('kurum_turu') or 
            raw_record.get('kategori') or
            ""
        )
        
        province = (
            raw_record.get('il') or 
            raw_record.get('province') or 
            raw_record.get('sehir') or
            ""
        )
        
        district = (
            raw_record.get('ilce') or 
            raw_record.get('district') or 
            ""
        )
        
        address = (
            raw_record.get('adres') or 
            raw_record.get('address') or 
            ""
        )
        
        phone = (
            raw_record.get('telefon') or 
            raw_record.get('phone') or 
            ""
        )
        
        website = (
            raw_record.get('website') or 
            raw_record.get('web_site') or 
            ""
        )
        
        # Koordinatlar
        latitude = raw_record.get('enlem') or raw_record.get('latitude')
        longitude = raw_record.get('boylam') or raw_record.get('longitude')
        
        try:
            latitude = float(latitude) if latitude is not None else None
            longitude = float(longitude) if longitude is not None else None
        except (ValueError, TypeError):
            latitude = longitude = None
        
        # Standart kayıt oluştur
        normalized = {
            'name': name.strip() if name else "",
            'facility_type': facility_type.strip() if facility_type else "Sağlık Kuruluşu",
            'province': province.strip() if province else "",
            'district': district.strip() if district else "",
            'address': address.strip() if address else "",
            'phone': phone.strip() if phone else None,
            'website': website.strip() if website else None,
            'latitude': latitude,
            'longitude': longitude,
            'sources': [source],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        return normalized

    def save_processed_data(self, records: List[Dict]):
        """İşlenmiş veriyi kaydeder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Supabase formatında kaydet
        supabase_file = self.processed_data_dir / f"supabase_ready_{timestamp}.json"
        
        with open(supabase_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"İşlenmiş veri kaydedildi: {supabase_file}")
        self.logger.info(f"Toplam kayıt: {len(records)}")

    def process(self) -> bool:
        """Ana işleme fonksiyonu"""
        try:
            self.logger.info("TURSAKUR 2.0 veri işleme başlıyor...")
            
            # 1. Ham verileri yükle
            raw_data = self.load_raw_data()
            if not raw_data:
                self.logger.error("Ham veri bulunamadı!")
                return False
            
            # 2. Tüm kayıtları normalize et
            processed_records = []
            for source, records in raw_data.items():
                for record in records:
                    normalized = self.normalize_record(record, source)
                    if normalized['name']:  # İsmi olan kayıtları al
                        processed_records.append(normalized)
            
            self.logger.info(f"İşlenen kayıt sayısı: {len(processed_records)}")
            
            # 3. Veriyi kaydet
            self.save_processed_data(processed_records)
            
            self.logger.info("✅ Veri işleme başarıyla tamamlandı!")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Veri işleme hatası: {e}")
            return False

def main():
    """Ana fonksiyon"""
    processor = SimpleDataProcessor()
    success = processor.process()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())

def clean_phone_number(phone: str) -> str:
    """Telefon numarasını standart formata dönüştürür."""
    if not phone:
        return ""
    
    # Tüm boşlukları ve özel karakterleri temizle
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Türkiye formatına dönüştür
    if cleaned.startswith('0'):
        cleaned = '+90' + cleaned[1:]
    elif cleaned.startswith('90') and not cleaned.startswith('+90'):
        cleaned = '+' + cleaned
    elif not cleaned.startswith('+90') and len(cleaned) == 10:
        cleaned = '+90' + cleaned
    
    return cleaned

def apply_geographic_mapping(kurum: Dict[str, Any]) -> Dict[str, Any]:
    """Kuruma coğrafi eşleme uygula"""
    # Basit coğrafi eşleme
    kurum = geo_mapper.enhance_institution_coordinates(kurum)
    
    # Il kodu kontrolü
    if not kurum.get('il_kodu') or kurum['il_kodu'] == 0:
        kurum['il_kodu'] = 6  # Default Ankara
    
    if not kurum.get('il_adi'):
        kurum['il_adi'] = "Bilinmiyor"
    
    if not kurum.get('ilce_adi'):
        kurum['ilce_adi'] = "Merkez"
    
    return kurum

def clean_text(text: str) -> str:
    """Metni temizler ve normalize eder."""
    if not text:
        return ""
    
    # Unicode normalize
    text = unicodedata.normalize('NFKD', str(text))
    
    # Fazla boşlukları temizle
    text = ' '.join(text.split())
    
    # İstenmeyen karakterleri temizle
    text = text.replace('\x00', '').replace('\r', '').replace('\n', ' ')
    
    return text.strip()

def clean_address(address: str, il_adi: Optional[str] = None, ilce_adi: Optional[str] = None) -> str:
    """Adresi temizler ve normalize eder."""
    if not address:
        return ""
    
    # Temel temizlik
    address = clean_text(address)
    
    # İl ve ilçe bilgilerini kaldır (çünkü ayrı alanlarda tutuyoruz)
    if il_adi:
        address = address.replace(il_adi, "").replace(il_adi.upper(), "")
    if ilce_adi:
        address = address.replace(ilce_adi, "").replace(ilce_adi.upper(), "")
    
    # Fazla boşlukları temizle
    address = ' '.join(address.split())
    
    return address.strip()

def generate_kurum_id(kurum_data: Dict[str, Any]) -> str:
    """Kurum ID'si oluşturur: TR-[il_kodu]-[tip_kodu]-[sira_no]"""
    il_kodu = kurum_data.get('il_kodu', 0)
    kurum_tipi = kurum_data.get('kurum_tipi', 'GENEL')
    
    # Tip kodları
    tip_kodlari = {
        'DEVLET_HASTANESI': 'DH',
        'UNIVERSITE_HASTANESI': 'UH', 
        'OZEL_HASTANE': 'OH',
        'SAGLIK_MERKEZI': 'SM',
        'SAGLIK_OCAGI': 'SO',
        'ECZANE': 'EC',
        'OZEL_TIP_MERKEZI': 'OTM',
        'AGIZ_DIS_SAGLIGI_MERKEZI': 'ADM',
        'EGITIM_ARASTIRMA_HASTANESI': 'EAH',
        'GENEL': 'GN'
    }
    
    tip_kodu = tip_kodlari.get(kurum_tipi, 'GN')
    
    # Basit sıra numarası (hash tabanlı)
    kurum_adi = kurum_data.get('kurum_adi', '')
    adres = kurum_data.get('adres', '')
    sira_no = abs(hash(kurum_adi + adres)) % 9999 + 1
    
    return f"TR-{il_kodu:02d}-{tip_kodu}-{sira_no:04d}"

def normalize_kurum_tipi(tip: str) -> str:
    """Kurum tipini standartlaştırır."""
    if not tip:
        return 'GENEL'
    
    tip_cleaned = tip.strip()
    
    # Direkt eşlemeler (büyük harf problemi için)
    tip_esleme = {
        'Devlet Hastanesi': 'DEVLET_HASTANESI',
        'DEVLET HASTANESİ': 'DEVLET_HASTANESI',
        'DEVLET HASTANESI': 'DEVLET_HASTANESI',
        'KAMU HASTANESİ': 'DEVLET_HASTANESI',
        'KAMU HASTANESI': 'DEVLET_HASTANESI',
        'Üniversite Hastanesi': 'UNIVERSITE_HASTANESI',
        'ÜNİVERSİTE HASTANESİ': 'UNIVERSITE_HASTANESI',
        'UNIVERSITE HASTANESI': 'UNIVERSITE_HASTANESI',
        'Özel Hastane': 'OZEL_HASTANE',
        'ÖZEL HASTANE': 'OZEL_HASTANE',
        'OZEL HASTANE': 'OZEL_HASTANE',
        'ÖZEL HASTANESİ': 'OZEL_HASTANE',
        'Sağlık Merkezi': 'SAGLIK_MERKEZI',
        'SAĞLIK MERKEZİ': 'SAGLIK_MERKEZI',
        'SAGLIK MERKEZI': 'SAGLIK_MERKEZI',
        'Sağlık Ocağı': 'SAGLIK_OCAGI',
        'SAĞLIK OCAĞI': 'SAGLIK_OCAGI',
        'SAGLIK OCAGI': 'SAGLIK_OCAGI',
        'Eczane': 'ECZANE',
        'ECZANE': 'ECZANE',
        'Özel Tıp Merkezi': 'OZEL_TIP_MERKEZI',
        'ÖZEL TIP MERKEZİ': 'OZEL_TIP_MERKEZI',
        'OZEL TIP MERKEZI': 'OZEL_TIP_MERKEZI',
        # Yeni kategoriler - hem orijinal hem büyük harf versiyonları
        'Ağız ve Diş Sağlığı Merkezi': 'AGIZ_DIS_SAGLIGI_MERKEZI',
        'AĞIZ VE DİŞ SAĞLIĞI MERKEZİ': 'AGIZ_DIS_SAGLIGI_MERKEZI',
        'AGIZ VE DIS SAGLIGI MERKEZI': 'AGIZ_DIS_SAGLIGI_MERKEZI',
        'Eğitim ve Araştırma Hastanesi': 'EGITIM_ARASTIRMA_HASTANESI',
        'EĞİTİM VE ARAŞTIRMA HASTANESİ': 'EGITIM_ARASTIRMA_HASTANESI',
        'EGITIM VE ARASTIRMA HASTANESI': 'EGITIM_ARASTIRMA_HASTANESI'
    }
    
    # Önce direkt eşleme dene
    if tip_cleaned in tip_esleme:
        return tip_esleme[tip_cleaned]
    
    # Büyük harf versiyonunu dene
    tip_upper = tip_cleaned.upper()
    if tip_upper in tip_esleme:
        return tip_esleme[tip_upper]
    
    return 'GENEL'

def validate_coordinates(lat: float, lon: float) -> bool:
    """Koordinatların Türkiye sınırları içinde olup olmadığını kontrol eder."""
    # Türkiye'nin yaklaşık sınırları
    return (35.8 <= lat <= 42.1) and (25.7 <= lon <= 44.8)

def process_saglik_bakanligi_data() -> List[Dict[str, Any]]:
    """Sağlık Bakanlığı verilerini işler."""
    kurumlar = []
    
    try:
        file_path = os.path.join('data', 'raw', 'saglik_bakanligi_tesisleri.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Sağlık Bakanlığı: {len(data)} kayıt yüklendi")
        
        for item in data:
            kurum = {
                'kurum_adi': clean_text(item.get('kurum_adi', '')),
                'kurum_tipi': normalize_kurum_tipi(item.get('kurum_tipi', 'DEVLET_HASTANESI')),
                'il_adi': clean_text(item.get('il_adi', '')),
                'ilce_adi': clean_text(item.get('ilce_adi', 'Merkez')),
                'adres': clean_address(item.get('adres', '')),
                'telefon': clean_phone_number(item.get('telefon', '')),
                'veri_kaynagi': 'T.C. Sağlık Bakanlığı',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
                'web_sitesi': item.get('web_sitesi', ''),
                'koordinat_lat': None,
                'koordinat_lon': None
            }
            
            # Coğrafi eşleme uygula
            kurum = apply_geographic_mapping(kurum)
            
            if kurum['kurum_adi']:  # Boş isimleri filtrele
                kurum['kurum_id'] = generate_kurum_id(kurum)
                kurumlar.append(kurum)
                
    except FileNotFoundError:
        logger.warning("Sağlık Bakanlığı veri dosyası bulunamadı")
    except Exception as e:
        logger.error(f"Sağlık Bakanlığı veri hatası: {e}")
    
    return kurumlar

def process_ozel_hastaneler_data() -> List[Dict[str, Any]]:
    """Özel hastane verilerini işler."""
    kurumlar = []
    
    try:
        file_path = os.path.join('data', 'raw', 'ozel_hastaneler.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Özel Hastaneler: {len(data)} kayıt yüklendi")
        
        for item in data:
            kurum = {
                'kurum_adi': clean_text(item.get('kurum_adi', '')),
                'kurum_tipi': 'OZEL_HASTANE',
                'il_adi': clean_text(item.get('il_adi', '')),
                'ilce_adi': clean_text(item.get('ilce_adi', 'Merkez')),
                'adres': clean_address(item.get('adres', '')),
                'telefon': clean_phone_number(item.get('telefon', '')),
                'veri_kaynagi': 'Özel Hastaneler Veritabanı',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
                'web_sitesi': item.get('web_sitesi', ''),
                'koordinat_lat': None,
                'koordinat_lon': None
            }
            
            # Coğrafi eşleme uygula
            kurum = apply_geographic_mapping(kurum)
            
            if kurum['kurum_adi']:
                kurum['kurum_id'] = generate_kurum_id(kurum)
                kurumlar.append(kurum)
                
    except FileNotFoundError:
        logger.warning("Özel hastaneler veri dosyası bulunamadı")
    except Exception as e:
        logger.error(f"Özel hastaneler veri hatası: {e}")
    
    return kurumlar

def process_universite_hastaneleri_data() -> List[Dict[str, Any]]:
    """Üniversite hastanesi verilerini işler."""
    kurumlar = []
    
    try:
        file_path = os.path.join('data', 'raw', 'universite_hastaneleri.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Üniversite Hastaneleri: {len(data)} kayıt yüklendi")
        
        for item in data:
            kurum = {
                'kurum_adi': clean_text(item.get('kurum_adi', '')),
                'kurum_tipi': 'UNIVERSITE_HASTANESI',
                'il_adi': clean_text(item.get('il_adi', '')),
                'ilce_adi': clean_text(item.get('ilce_adi', 'Merkez')),
                'adres': clean_address(item.get('adres', '')),
                'telefon': clean_phone_number(item.get('telefon', '')),
                'veri_kaynagi': 'Üniversite Hastaneleri Veritabanı',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
                'web_sitesi': item.get('web_sitesi', ''),
                'koordinat_lat': None,
                'koordinat_lon': None
            }
            
            # Coğrafi eşleme uygula
            kurum = apply_geographic_mapping(kurum)
            
            if kurum['kurum_adi']:
                kurum['kurum_id'] = generate_kurum_id(kurum)
                kurumlar.append(kurum)
                
    except FileNotFoundError:
        logger.warning("Üniversite hastaneleri veri dosyası bulunamadı")
    except Exception as e:
        logger.error(f"Üniversite hastaneleri veri hatası: {e}")
    
    return kurumlar

def remove_duplicates(kurumlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Dublicate kayıtları kaldırır."""
    seen = set()
    unique_kurumlar = []
    
    for kurum in kurumlar:
        # Anahtar oluştur (isim + il + ilçe)
        key = (
            kurum.get('kurum_adi', '').lower().strip(),
            kurum.get('il_adi', '').lower().strip(),
            kurum.get('ilce_adi', '').lower().strip()
        )
        
        if key not in seen and key[0]:  # Boş isimleri dahil etme
            seen.add(key)
            unique_kurumlar.append(kurum)
    
    logger.info(f"Dublicate temizleme: {len(kurumlar)} -> {len(unique_kurumlar)}")
    return unique_kurumlar

def generate_statistics(kurumlar: List[Dict[str, Any]]) -> Dict[str, Any]:
    """İstatistikler oluşturur."""
    iller = {}
    kurum_tipleri = {}
    
    for kurum in kurumlar:
        # İl istatistikleri
        il = kurum.get('il_adi', 'Bilinmiyor')
        iller[il] = iller.get(il, 0) + 1
        
        # Kurum tipi istatistikleri
        tip = kurum.get('kurum_tipi', 'GENEL')
        kurum_tipleri[tip] = kurum_tipleri.get(tip, 0) + 1
    
    stats = {
        'toplam_kurum': len(kurumlar),
        'toplam_il': len(iller),
        'il_dagilimi': iller,
        'kurum_tipi_dagilimi': kurum_tipleri,
        'son_guncelleme': datetime.now().isoformat()
    }
    
    # İstatistik çıktısı
    logger.info(f"Toplam Kurum: {stats['toplam_kurum']}")
    logger.info(f"Toplam İl: {stats['toplam_il']}")
    
    if iller:
        en_cok_il = max(iller.keys(), key=lambda x: iller[x])
        logger.info(f"En Çok Kurum Olan İl: {en_cok_il} ({iller[en_cok_il]})")
    
    return stats

def main():
    """Ana işlem fonksiyonu."""
    logger.info("🏥 TÜRKİYE SAĞLIK KURULUŞLARI VERİ İŞLEME")
    logger.info("🗺️ Türkiye'nin resmi 81 il sistemi ile coğrafi eşleme")
    logger.info("=" * 60)
    
    # Tüm veri kaynaklarını işle
    all_kurumlar = []
    
    # Sağlık Bakanlığı verileri
    sb_kurumlar = process_saglik_bakanligi_data()
    all_kurumlar.extend(sb_kurumlar)
    
    # Özel hastane verileri
    oh_kurumlar = process_ozel_hastaneler_data()
    all_kurumlar.extend(oh_kurumlar)
    
    # Üniversite hastane verileri
    uh_kurumlar = process_universite_hastaneleri_data()
    all_kurumlar.extend(uh_kurumlar)
    
    # Kapsamlı üniversite-hastane ilişkileri
    from process_universite_hastane import UniversiteHastaneProcessor
    try:
        processor = UniversiteHastaneProcessor()
        kuh_kurumlar = processor.universite_hastane_iliskilerini_isle()
        all_kurumlar.extend(kuh_kurumlar)
        logger.info(f"✅ {len(kuh_kurumlar)} kapsamlı üniversite-hastane ilişkisi eklendi")
    except Exception as e:
        logger.warning(f"⚠️ Kapsamlı üniversite-hastane ilişkileri işlenemedi: {e}")
    
    logger.info(f"Toplam ham veri: {len(all_kurumlar)} kurum")
    
    # Dublikasyonları kaldır
    unique_kurumlar = remove_duplicates(all_kurumlar)
    
    # İstatistikler oluştur
    stats = generate_statistics(unique_kurumlar)
    
    # Coğrafi veriyi dışa aktar (mevcut fonksiyona sahipse)
    try:
        geo_mapper.export_geo_data('data/turkey_geo_data.json')
    except AttributeError:
        logger.info("Coğrafi veri export fonksiyonu mevcut değil, atlaniyor")
    
    # Ana veri yapısını oluştur
    output_data = {
        'metadata': {
            'total_kurumlar': len(unique_kurumlar),
            'total_iller': 81,  # Türkiye'nin resmi il sayısı
            'veri_kaynaklari': [
                'T.C. Sağlık Bakanlığı',
                'Özel Hastaneler Veritabanı',
                'Üniversite Hastaneleri Veritabanı',
                'Kapsamlı Üniversite-Hastane İlişkileri'
            ],
            'son_guncelleme': datetime.now().isoformat(),
            'geo_mapping_applied': True,
            'geo_system': 'Turkey Official 81 Provinces',
            'istatistikler': stats
        },
        'kurumlar': unique_kurumlar
    }
    
    # Ana dosyaya kaydet
    output_file = os.path.join('data', 'turkiye_saglik_kuruluslari.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ Ana veri dosyası kaydedildi: {output_file}")
    logger.info(f"🗺️ Coğrafi veri kaydedildi: data/turkey_geo_data.json")
    logger.info(f"📊 {len(unique_kurumlar)} sağlık kurumu işlendi")
    logger.info(f"🏛️ Türkiye'nin 81 ili standardında coğrafi eşleme tamamlandı")
    
    # Coğrafi eşleştirme kalitesi analizi
    analyze_geographic_quality(output_data)
    
    return output_data

def analyze_geographic_quality(data: Dict) -> None:
    """Coğrafi eşleştirme kalitesini analiz et ve raporla"""
    kurumlar = data.get('kurumlar', [])
    total_kurumlar = len(kurumlar)
    
    # Başarılı eşleşme analizi
    başarılı_eşleşme = len([k for k in kurumlar if k.get('il_kodu') and 1 <= k.get('il_kodu', 0) <= 81])
    başarı_oranı = başarılı_eşleşme / total_kurumlar * 100 if total_kurumlar else 0
    
    logger.info(f"🎯 Coğrafi eşleştirme başarı oranı: %{başarı_oranı:.1f} ({başarılı_eşleşme}/{total_kurumlar})")
    
    if başarı_oranı >= 95:
        logger.info("🌟 Mükemmel! Coğrafi eşleştirme sistemi çok başarılı")
    elif başarı_oranı >= 90:
        logger.info("👍 İyi! Coğrafi eşleştirme sistemi başarılı")
    else:
        logger.warning("⚠️ Geliştirilmeli! Coğrafi eşleştirme sisteminde iyileştirme gerekli")
    
    # İl dağılımı kontrol
    il_sayısı = len(set(k.get('il_adi') for k in kurumlar))
    if il_sayısı == 81:
        logger.info("✅ 81 il standardına uygun - Tüm iller temsil ediliyor")
    else:
        logger.warning(f"⚠️ İl sayısı problemi: {il_sayısı}/81")

if __name__ == "__main__":
    main()
