#!/usr/bin/env python3
"""
Türkiye Sağlık Kuruluşları - Veri İşleme
Raw klasöründeki verileri temizler, standardize eder ve tek dosyada birleştirir.
Türkiye'nin resmi 81 il sistemi ile coğrafi eşleme yapılır.
"""

import json
import os
import sys
import unicodedata
from datetime import datetime
from typing import List, Dict, Any
import logging

# Coğrafi eşleme sistemi
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from turkey_geo_mapper import TurkeyGeoMapper

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global coğrafi eşleyici
geo_mapper = TurkeyGeoMapper()

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

def get_il_kodu_from_il_adi(il_adi: str) -> int:
    """İl adından il kodunu bul - Yeni coğrafi eşleyiciyi kullan"""
    if not il_adi:
        return 0
    
    mapping = geo_mapper.map_province(il_adi)
    if mapping:
        return mapping[0]  # Il kodu
    
    return 0
        'KAHRAMANMARAŞ': 46, 'MARDİN': 47, 'MUĞLA': 48, 'MUŞ': 49, 'NEVŞEHİR': 50,
        'NİĞDE': 51, 'ORDU': 52, 'RİZE': 53, 'SAKARYA': 54, 'SAMSUN': 55,
        'SİİRT': 56, 'SİNOP': 57, 'SİVAS': 58, 'TEKİRDAĞ': 59, 'TOKAT': 60,
        'TRABZON': 61, 'TUNCELİ': 62, 'ŞANLIURFA': 63, 'UŞAK': 64, 'VAN': 65,
        'YOZGAT': 66, 'ZONGULDAK': 67, 'AKSARAY': 68, 'BAYBURT': 69, 'KARAMAN': 70,
        'KIRIKKALE': 71, 'BATMAN': 72, 'ŞIRNAK': 73, 'BARTIN': 74, 'ARDAHAN': 75,
        'IĞDIR': 76, 'YALOVA': 77, 'KARABÜK': 78, 'KİLİS': 79, 'OSMANİYE': 80,
        'DÜZCE': 81
    }
    
    # İl adını normalize et
    il_normalized = il_adi.upper().strip()
    
    # Özel karakterleri temizle
    il_normalized = il_normalized.replace('İ', 'I').replace('Ş', 'S').replace('Ğ', 'G')
    il_normalized = il_normalized.replace('Ü', 'U').replace('Ö', 'O').replace('Ç', 'C')
    il_normalized = il_normalized.replace('İ', 'I')  # Noktalı i
    
    # Alternatif isimler
    alternatifler = {
        'AFYON': 'AFYONKARAHİSAR',
        'K.MARAŞ': 'KAHRAMANMARAŞ',
        'MARAŞ': 'KAHRAMANMARAŞ',
        'KAHRAMANMARAS': 'KAHRAMANMARAŞ',
        'ŞURFA': 'ŞANLIURFA',
        'URFA': 'ŞANLIURFA',
        'SANLIURFA': 'ŞANLIURFA'
    }
    
    if il_normalized in alternatifler:
        il_normalized = alternatifler[il_normalized]
    
    return il_kodlari.get(il_normalized, 0)

def standardize_kurum_tipi(kurum_tipi: str) -> str:
    """Kurum tipini standardize et"""
    if not kurum_tipi:
        return 'Özel Hastane'
    
    # Kurum tipi standardizasyon haritası
    standardizations = {
        # Özel hastane çeşitleri
        'Özel Hastane': 'Özel Hastane',
        'Özel Genel Hastane': 'Özel Hastane',
        'Özel Göz Hastanesi': 'Özel Hastane',
        'Özel Kadın Hastalıkları ve Doğum Hastanesi': 'Özel Hastane',
        'Özel Fizik Tedavi ve Rehabilitasyon Hastanesi': 'Özel Hastane',
        'Özel Diş Hastanesi': 'Özel Hastane',
        'Özel Ruh Sağlığı ve Hastalıkları Hastanesi': 'Özel Hastane',
        'Özel Kalp Hastanesi': 'Özel Hastane',
        'Özel Çocuk Hastanesi': 'Özel Hastane',
        'Özel Göğüs Hastalıkları Hastanesi': 'Özel Hastane',
        'Özel Doğum Hastanesi': 'Özel Hastane',
        'Özel Kalp ve Damar Cerrahisi Hastanesi': 'Özel Hastane',
        'Özel Ortopedi ve Travmatoloji Hastanesi': 'Özel Hastane',
        
        # Devlet hastane çeşitleri
        'Devlet Hastanesi': 'Devlet Hastanesi',
        'Üniversite Hastanesi': 'Üniversite Hastanesi',
        'Eğitim ve Araştırma Hastanesi': 'Eğitim ve Araştırma Hastanesi',
        
        # Diğer tipler
        'Aile Sağlığı Merkezi': 'Aile Sağlığı Merkezi',
        'Toplum Sağlığı Merkezi': 'Toplum Sağlığı Merkezi',
        'Ağız ve Diş Sağlığı Merkezi': 'Ağız ve Diş Sağlığı Merkezi',
        'Özel Poliklinik': 'Özel Poliklinik',
        'Özel Tıp Merkezi': 'Özel Tıp Merkezi',
        'Diyaliz Merkezi': 'Diyaliz Merkezi',
        'Fizik Tedavi ve Rehabilitasyon Merkezi': 'Fizik Tedavi ve Rehabilitasyon Merkezi',
        'Ambulans İstasyonu': 'Ambulans İstasyonu'
    }
    
    return standardizations.get(kurum_tipi, 'Özel Hastane')

def clean_address(address: str, il_adi: str = None, ilce_adi: str = None) -> str:
    """Adresi temizler ve standardize eder."""
    if not address or str(address).strip() == "":
        # Boş adres durumunda il ve ilçe bilgisinden yapay adres oluştur
        if il_adi and ilce_adi:
            return f"{ilce_adi}, {il_adi}"
        elif il_adi:
            return f"Merkez, {il_adi}"
        else:
            return "Adres bilgisi mevcut değil"
    
    # Çoklu boşlukları tek boşluğa dönüştür
    cleaned = ' '.join(str(address).split())
    
    # Çok kısa adresleri (sadece il/ilçe adı gibi) için il/ilçe ekle
    if len(cleaned.strip()) < 10:
        if il_adi and ilce_adi:
            return f"{cleaned}, {ilce_adi}, {il_adi}"
        elif il_adi:
            return f"{cleaned}, {il_adi}"
        else:
            return cleaned.strip().title()
    
    # İlk harfi büyük yap
    return cleaned.strip().title()

def generate_kurum_id(kurum: Dict[str, Any], existing_ids: set) -> str:
    """Kurum için benzersiz ID üretir."""
    il_kodu = kurum.get('il_kodu', 0)
    kurum_tipi = kurum.get('kurum_tipi', '')
    
    # Tip kodları
    tip_kodlari = {
        'Devlet Hastanesi': 'DH',
        'Üniversite Hastanesi': 'UH',
        'Eğitim ve Araştırma Hastanesi': 'EH',
        'Özel Hastane': 'OH',
        'Özel Genel Hastane': 'OH',
        'Özel Göz Hastanesi': 'OGH',
        'Özel Kadın Hastalıkları ve Doğum Hastanesi': 'OKH',
        'Özel Fizik Tedavi ve Rehabilitasyon Hastanesi': 'OFTR',
        'Özel Diş Hastanesi': 'ODH',
        'Özel Ruh Sağlığı ve Hastalıkları Hastanesi': 'ORSH',
        'Özel Kalp Hastanesi': 'OKH',
        'Özel Çocuk Hastanesi': 'OCH',
        'Özel Göğüs Hastalıkları Hastanesi': 'OGHH',
        'Özel Doğum Hastanesi': 'ODH',
        'Özel Kalp ve Damar Cerrahisi Hastanesi': 'OKDCH',
        'Özel Ortopedi ve Travmatoloji Hastanesi': 'OOTH',
        'Aile Sağlığı Merkezi': 'ASM',
        'Toplum Sağlığı Merkezi': 'TSM',
        'Ağız ve Diş Sağlığı Merkezi': 'ADSM',
        'Özel Poliklinik': 'OP',
        'Özel Tıp Merkezi': 'OTM',
        'Diyaliz Merkezi': 'DM',
        'Fizik Tedavi ve Rehabilitasyon Merkezi': 'FTRM',
        'Ambulans İstasyonu': 'AI'
    }
    
    tip_kodu = tip_kodlari.get(kurum_tipi, 'OTHER')
    
    # Sıra numarası için sayaç
    counter = 1
    while True:
        kurum_id = f"TR-{il_kodu:02d}-{tip_kodu}-{counter:03d}"
        if kurum_id not in existing_ids:
            existing_ids.add(kurum_id)
            return kurum_id
        counter += 1

def process_raw_data(raw_dir: str) -> List[Dict[str, Any]]:
    """Raw klasöründeki tüm verileri öncelik sırasına göre işler."""
    all_kurumlar = []
    existing_ids = set()
    processed_names = set()  # Çift eklemeyi önlemek için
    
    if not os.path.exists(raw_dir):
        logger.error(f"Raw veri klasörü bulunamadı: {raw_dir}")
        return []
    
    # Öncelik sırasına göre dosya işleme
    file_patterns = [
        ('saglik_bakanligi_tesisleri.json', 1, 'Sağlık Bakanlığı'),       # En yüksek öncelik
        ('ozel_hastaneler.json', 2, 'Özel Hastaneler SHGM'),             # İkinci öncelik  
        ('universite_hastaneleri.json', 3, 'Üniversite Hastaneleri'),    # Üçüncü öncelik
        ('trhastane_data.json', 4, 'TR Hastane Supplementary'),          # Dördüncü öncelik - eksikleri tamamla
        ('vikipedia_gelismis_kesfet.json', 5, 'Vikipedia Gelişmiş'),     # Beşinci öncelik - ek detaylar
        ('wikipedia_hospitals.json', 6, 'Vikipedia Temel')               # Altıncı öncelik - eski vikipedia verileri
    ]
    
    logger.info("Dosya işleme öncelik sırası:")
    for filename, priority, description in file_patterns:
        logger.info(f"  {priority}. {description} ({filename})")
    
    # Her dosyayı öncelik sırasına göre işle
    for filename, priority, description in file_patterns:
        file_path = os.path.join(raw_dir, filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"Dosya bulunamadı: {filename}")
            continue
            
        logger.info(f"Öncelik {priority} - İşleniyor: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Tek kurum verisi mi yoksa liste mi?
            if isinstance(data, list):
                kurumlar = data
            else:
                kurumlar = [data]
            
            added_count = 0
            skipped_count = 0
            
            for kurum in kurumlar:
                # Vikipedia verilerini özel olarak işle
                if 'vikipedia' in filename.lower() or 'wikipedia' in filename.lower():
                    processed_kurum_raw = process_wikipedia_data(kurum)
                    if not processed_kurum_raw:  # Sağlık kurumu değilse atla
                        skipped_count += 1
                        continue
                    kurum = processed_kurum_raw
                
                # Kurum adı ile çift eklemeyi kontrol et
                kurum_adi = kurum.get('kurum_adi', '').strip().lower()
                il_adi = kurum.get('il_adi', '').strip().lower()
                
                # Basit çift ekleme kontrolü
                name_key = f"{kurum_adi}|{il_adi}"
                
                # Eğer bu kurum daha önce yüksek öncelikli kaynaktan eklendiyse, atla
                if name_key in processed_names and priority > 1:
                    skipped_count += 1
                    continue
                
                # Veri temizleme ve standardizasyon
                il_kodu_value = int(kurum.get('il_kodu', 0))
                if il_kodu_value == 0:
                    # İl kodunu il adından bul
                    il_kodu_value = get_il_kodu_from_il_adi(kurum.get('il_adi', ''))
                
                processed_kurum = {
                    'kurum_id': kurum.get('kurum_id', ''),
                    'kurum_adi': kurum.get('kurum_adi', '').strip(),
                    'kurum_tipi': standardize_kurum_tipi(kurum.get('kurum_tipi', '')),
                    'il_kodu': il_kodu_value,
                    'il_adi': kurum.get('il_adi', '').strip().title(),
                    'ilce_adi': kurum.get('ilce_adi', '').strip().title(),
                    'adres': clean_address(kurum.get('adres', ''), kurum.get('il_adi', ''), kurum.get('ilce_adi', '')),
                    'telefon': clean_phone_number(kurum.get('telefon', '')),
                    'koordinat_lat': float(kurum.get('koordinat_lat', 0)) if kurum.get('koordinat_lat') else None,
                    'koordinat_lon': float(kurum.get('koordinat_lon', 0)) if kurum.get('koordinat_lon') else None,
                    'web_sitesi': kurum.get('web_sitesi', '').strip(),
                    'veri_kaynagi': kurum.get('veri_kaynagi', '').strip(),
                    'son_guncelleme': kurum.get('son_guncelleme', datetime.now().strftime('%Y-%m-%d'))
                }
                
                # Kurum ID üret (eğer yoksa)
                if not processed_kurum['kurum_id']:
                    processed_kurum['kurum_id'] = generate_kurum_id(processed_kurum, existing_ids)
                else:
                    existing_ids.add(processed_kurum['kurum_id'])
                
                all_kurumlar.append(processed_kurum)
                processed_names.add(name_key)
                added_count += 1
            
            logger.info(f"  ✓ {added_count} kurum eklendi, {skipped_count} çift kayıt atlandı")
        
        except Exception as e:
            logger.error(f"Dosya işleme hatası - {filename}: {e}")
            continue
    
    # Son istatistikler
    logger.info(f"Toplam {len(all_kurumlar)} benzersiz kurum işlendi")
    return all_kurumlar

def save_processed_data(kurumlar: List[Dict[str, Any]], output_file: str):
    """İşlenmiş verileri kaydet."""
    try:
        # Output dosyasının tam yolunu kontrol et
        if not os.path.dirname(output_file):
            # Eğer sadece dosya adı verilmişse, data klasörüne kaydet
            output_file = os.path.join("data", output_file)
        
        # Data klasörü yoksa oluştur
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Ana veritabanı dosyasını oluştur
        database = {
            'meta': {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'total_records': len(kurumlar),
                'description': 'Türkiye Sağlık Kuruluşları Açık Veritabanı'
            },
            'kurumlar': kurumlar
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Ana veritabanı kaydedildi: {output_file}")
        
        # İstatistikler
        logger.info("=== İSTATİSTİKLER ===")
        kurum_tipleri = {}
        iller = {}
        
        for kurum in kurumlar:
            tip = kurum.get('kurum_tipi', 'Bilinmiyor')
            kurum_tipleri[tip] = kurum_tipleri.get(tip, 0) + 1
            
            il = kurum.get('il_adi', 'Bilinmiyor')
            iller[il] = iller.get(il, 0) + 1
        
        logger.info("Kurum Tipleri:")
        for tip, count in sorted(kurum_tipleri.items()):
            logger.info(f"  {tip}: {count}")
        
        logger.info(f"Toplam İl Sayısı: {len(iller)}")
        logger.info(f"En Çok Kurum Olan İl: {max(iller, key=iller.get)} ({max(iller.values())})")
        
    except Exception as e:
        logger.error(f"Kaydetme hatası: {e}")
        sys.exit(1)

def process_wikipedia_data(kurum: Dict) -> Dict:
    """Vikipedia verilerini özel olarak işle."""
    # Sadece gerçek sağlık kuruluşlarını filtrele
    kurum_adi = kurum.get('kurum_adi', '').strip()
    
    # Sağlık kurumu olmayan girişleri filtrele
    health_keywords = ['hastane', 'hospital', 'tıp merkezi', 'medical', 'sağlık', 'health', 
                      'poliklinik', 'clinic', 'üniversitesi hastanesi', 'eğitim ve araştırma']
    
    if not any(keyword in kurum_adi.lower() for keyword in health_keywords):
        return None
    
    # Koordinatları vikipedia veya wikidata'dan al
    koordinat_lat = None
    koordinat_lon = None
    
    # Önce normal koordinatları kontrol et
    if kurum.get('koordinatlar'):
        coords = kurum['koordinatlar']
        if isinstance(coords, dict):
            koordinat_lat = coords.get('lat')
            koordinat_lon = coords.get('lon')
    
    # Wikidata koordinatlarını kontrol et
    if not koordinat_lat and kurum.get('wikidata_koordinatlar'):
        wikidata_coords = kurum['wikidata_koordinatlar']
        if isinstance(wikidata_coords, dict):
            koordinat_lat = wikidata_coords.get('lat')
            koordinat_lon = wikidata_coords.get('lon')
    
    # İl adını çıkarmaya çalış
    il_adi = kurum.get('il_adi', '')
    if not il_adi:
        # Kurum adından veya kategorilerden il çıkarmaya çalış
        categories = kurum.get('kategoriler', [])
        for category in categories:
            for city in ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana']:
                if city.lower() in category.lower() or city.lower() in kurum_adi.lower():
                    il_adi = city
                    break
            if il_adi:
                break
    
    # Infobox'dan ek bilgileri al
    infobox = kurum.get('infobox_data', {})
    
    # Web sitesi
    web_sitesi = kurum.get('web_sitesi', '') or infobox.get('web sitesi', '') or infobox.get('website', '')
    
    # Telefon
    telefon = kurum.get('telefon', '') or infobox.get('telefon', '') or infobox.get('phone', '')
    
    # Adres
    adres = kurum.get('adres', '') or infobox.get('adres', '') or infobox.get('konum', '') or infobox.get('location', '')
    
    return {
        'kurum_adi': kurum_adi,
        'kurum_tipi': kurum.get('kurum_tipi', 'Hastane'),
        'il_adi': il_adi,
        'ilce_adi': '',
        'adres': adres,
        'telefon': telefon,
        'koordinat_lat': koordinat_lat,
        'koordinat_lon': koordinat_lon,
        'web_sitesi': web_sitesi,
        'veri_kaynagi': kurum.get('veri_kaynagi', 'Vikipedia'),
        'son_guncelleme': kurum.get('son_guncelleme', datetime.now().strftime('%Y-%m-%d')),
        'wikidata_id': kurum.get('wikidata_id', ''),
        'wiki_url': kurum.get('wiki_url', '')
    }

def main():
    """Ana fonksiyon."""
    raw_dir = "data/raw"
    output_file = "turkiye_saglik_kuruluslari.json"
    
    logger.info("Veri işleme başlıyor...")
    
    # Raw verileri işle
    kurumlar = process_raw_data(raw_dir)
    
    if not kurumlar:
        logger.warning("İşlenecek veri bulunamadı")
        return
    
    # İşlenmiş verileri kaydet
    save_processed_data(kurumlar, output_file)
    
    logger.info("Veri işleme tamamlandı!")

if __name__ == "__main__":
    main()
