#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TR Hastane Web Sitesi Veri Çekme Scripti
========================================

Bu script trhastane.com sitesinden sağlık kuruluşları verilerini çeker.
Özellikle resmi kaynaklarda eksik olan üniversite hastaneleri, tıp merkezleri,
diyaliz merkezleri gibi özel kategorilerdeki kuruluşları hedefler.

Veri Kaynağı: https://www.trhastane.com/
Güncelleme: 3 ayda bir otomatik
"""

import os
import json
import hashlib
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time
import re

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fetch_trhastane.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TRHastaneDataFetcher:
    """TR Hastane web sitesinden veri çeken sınıf"""
    
    def __init__(self):
        self.base_url = "https://www.trhastane.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Sadece en önemli ve eksik kategoriler - hızlı yaklaşım
        self.target_categories = [
            'universite-hastaneleri',  # En öncelikli - resmi kaynaklarda eksik
            'tip-merkezleri'           # İkinci öncelikli - özel sağlık merkezleri
        ]
        
        # Büyük şehirler öncelik - çoğu kurum buralarda
        self.priority_cities = [
            'istanbul', 'ankara', 'izmir', 'bursa', 'antalya', 
            'adana', 'konya', 'gaziantep', 'kayseri', 'eskisehir'
        ]
        
        # Kurum tipi eşleştirmeleri
        self.facility_type_mapping = {
            'universite-hastaneleri': 'Üniversite Hastanesi',
            'tip-merkezleri': 'Tıp Merkezi'
        }
        
        # Timeout ve retry ayarları
        self.timeout = 10
        self.max_retries = 2
        self.rate_limit = 0.5  # Saniye cinsinden bekleme

    def get_all_cities(self) -> List[str]:
        """Türkiye'deki tüm illeri getir"""
        cities = [
            'adana', 'adiyaman', 'afyonkarahisar', 'agri', 'aksaray', 'amasya', 'ankara', 
            'antalya', 'ardahan', 'artvin', 'aydin', 'balikesir', 'bartin', 'batman', 
            'bayburt', 'bilecik', 'bingol', 'bitlis', 'bolu', 'burdur', 'bursa', 'canakkale',
            'cankiri', 'corum', 'denizli', 'diyarbakir', 'duzce', 'edirne', 'elazig', 
            'erzincan', 'erzurum', 'eskisehir', 'gaziantep', 'giresun', 'gumushane', 
            'hakkari', 'hatay', 'igdir', 'isparta', 'istanbul', 'izmir', 'kahramanmaras',
            'karabuk', 'karaman', 'kars', 'kastamonu', 'kayseri', 'kilis', 'kirikkale',
            'kirklareli', 'kirsehir', 'kocaeli', 'konya', 'kutahya', 'malatya', 'manisa',
            'mardin', 'mersin', 'mugla', 'mus', 'nevsehir', 'nigde', 'ordu', 'osmaniye',
            'rize', 'sakarya', 'samsun', 'sanliurfa', 'siirt', 'sinop', 'sirnak', 'sivas',
            'tekirdag', 'tokat', 'trabzon', 'tunceli', 'usak', 'van', 'yalova', 'yozgat', 'zonguldak'
        ]
        return cities

    def fetch_page_with_retry(self, url: str, max_retries: int = None) -> Optional[BeautifulSoup]:
        """Sayfa çekme ile yeniden deneme - daha hızlı"""
        if max_retries is None:
            max_retries = self.max_retries
            
        for attempt in range(max_retries):
            try:
                time.sleep(self.rate_limit)  # Rate limiting
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                response.encoding = 'utf-8'
                return BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                logger.warning(f"Deneme {attempt + 1}/{max_retries} başarısız: {url} - {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Kısa bekleme
                else:
                    logger.error(f"Sayfa çekilemedi: {url}")
                    return None

    def extract_facility_details(self, facility_url: str) -> Optional[Dict]:
        """Kurum detay sayfasından bilgileri çıkar - hızlı versiyon"""
        soup = self.fetch_page_with_retry(facility_url, max_retries=1)  # Tek deneme
        if not soup:
            return None
            
        try:
            facility_info = {}
            
            # Sayfa başlığından kurum adını çıkar
            title_element = soup.find('h1') or soup.find('title')
            if title_element:
                title_text = title_element.get_text(strip=True)
                # Sayfa başlığından kurum adını temizle
                if ' - ' in title_text:
                    title_text = title_text.split(' - ')[0]
                facility_info['kurum_adi'] = title_text
            
            # Temel bilgileri hızlıca çıkar
            info_spans = soup.find_all(['span', 'div'], string=re.compile(r'(KURUM ADI|KATEGORİ|ŞEHİR|İLÇE|ADRES|TELEFON)', re.I))
            
            for span in info_spans:
                parent = span.parent
                if parent:
                    text = parent.get_text(strip=True)
                    
                    if 'KATEGORİ' in text.upper():
                        # Kategori bilgisini çıkar
                        parts = text.split(':')
                        if len(parts) > 1:
                            facility_info['kurum_tipi'] = parts[1].strip()
                    
                    elif 'ŞEHİR' in text.upper() or 'İL:' in text.upper():
                        parts = text.split(':')
                        if len(parts) > 1:
                            facility_info['il_adi'] = parts[1].strip()
                    
                    elif 'İLÇE' in text.upper():
                        parts = text.split(':')
                        if len(parts) > 1:
                            facility_info['ilce_adi'] = parts[1].strip()
                    
                    elif 'TELEFON' in text.upper():
                        parts = text.split(':')
                        if len(parts) > 1:
                            facility_info['telefon'] = self.format_phone(parts[1].strip())
            
            # Koordinat bilgilerini çıkar (harita linkinden)
            map_link = soup.find('a', href=re.compile(r'maps\.google\.com'))
            if map_link:
                href = map_link.get('href', '')
                coord_match = re.search(r'daddr=([0-9.-]+),([0-9.-]+)', href)
                if coord_match:
                    facility_info['koordinat_lat'] = float(coord_match.group(1))
                    facility_info['koordinat_lon'] = float(coord_match.group(2))
            
            return facility_info if facility_info.get('kurum_adi') else None
            
        except Exception as e:
            logger.error(f"Kurum detayları çıkarılırken hata: {facility_url} - {e}")
            return None

    def format_phone(self, phone: str) -> str:
        """Telefon numarasını standart formata çevir"""
        if not phone:
            return ""
        
        # Sadece rakamları al
        digits = re.sub(r'[^\d]', '', phone)
        
        # Türkiye format kontrolü
        if digits.startswith('90'):
            digits = digits[2:]
        elif digits.startswith('0'):
            digits = digits[1:]
        
        if len(digits) == 10:
            return f"+90{digits}"
        
        return phone  # Orijinal formatı döndür

    def get_city_facilities(self, city: str, category: str) -> List[Dict]:
        """Belirli bir şehir ve kategorideki kuruluşları getir - optimized"""
        facilities = []
        
        # Kategori sayfası URL'si
        category_url = f"{self.base_url}/{city}-{category}-listesi.html"
        
        soup = self.fetch_page_with_retry(category_url, max_retries=1)
        if not soup:
            return facilities
        
        # Kurum linklerini bul
        facility_links = soup.find_all('a', href=re.compile(r'/[^/]+-\d+\.html$'))
        
        logger.info(f"{city.title()} - {category}: {len(facility_links)} kurum bulundu")
        
        # Sadece ilk 10 kurumu işle (hızlı yaklaşım)
        for i, link in enumerate(facility_links[:10]):
            facility_url = link.get('href')
            if not facility_url.startswith('http'):
                facility_url = self.base_url + facility_url
            
            # Kurum adını URL'den de çıkarmaya çalış (fallback)
            url_name = facility_url.split('/')[-1].replace('.html', '').replace('-', ' ').title()
            
            facility_data = self.extract_facility_details(facility_url)
            if facility_data:
                # Şehir ve kategori bilgilerini ekle
                facility_data['il_adi'] = city.title()
                if not facility_data.get('kurum_tipi'):
                    facility_data['kurum_tipi'] = self.facility_type_mapping.get(category, 'Sağlık Kurumu')
                
                facility_data['veri_kaynagi'] = 'trhastane.com'
                facility_data['son_guncelleme'] = datetime.now().strftime('%Y-%m-%d')
                
                facilities.append(facility_data)
            else:
                # Minimal veri ile ekleme (URL'den çıkarılan bilgiler)
                minimal_data = {
                    'kurum_adi': url_name,
                    'kurum_tipi': self.facility_type_mapping.get(category, 'Sağlık Kurumu'),
                    'il_adi': city.title(),
                    'veri_kaynagi': 'trhastane.com (minimal)',
                    'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
                }
                facilities.append(minimal_data)
                
            # Minimal rate limiting
            if i < len(facility_links) - 1:
                time.sleep(0.2)
        
        return facilities

    def fetch_all_data(self) -> List[Dict]:
        """Sadece öncelikli şehirler ve kategorilerden veri çek - hızlı versiyon"""
        all_facilities = []
        
        total_operations = len(self.priority_cities) * len(self.target_categories)
        current_operation = 0
        
        logger.info(f"Hızlı veri çekme: {len(self.priority_cities)} öncelikli şehir, {len(self.target_categories)} kategori")
        
        for city in self.priority_cities:
            for category in self.target_categories:
                current_operation += 1
                logger.info(f"İşlem {current_operation}/{total_operations}: {city.title()} - {category}")
                
                try:
                    facilities = self.get_city_facilities(city, category)
                    all_facilities.extend(facilities)
                    
                    # İlerleme bilgisi
                    if facilities:
                        logger.info(f"✓ {len(facilities)} kurum eklendi")
                    
                except Exception as e:
                    logger.error(f"Şehir işleme hatası {city}-{category}: {e}")
                    continue
                
                # Categories arası kısa bekleme
                time.sleep(0.5)
        
        logger.info(f"Toplam {len(all_facilities)} kurum çekildi (hızlı mod)")
        return all_facilities

    def generate_facility_id(self, facility: Dict) -> str:
        """Kurum için benzersiz ID üret"""
        # İl kodu haritası (resmi plaka kodları)
        il_kodlari = {
            'adana': '01', 'adiyaman': '02', 'afyonkarahisar': '03', 'agri': '04',
            'aksaray': '68', 'amasya': '05', 'ankara': '06', 'antalya': '07',
            'ardahan': '75', 'artvin': '08', 'aydin': '09', 'balikesir': '10',
            'bartin': '74', 'batman': '72', 'bayburt': '69', 'bilecik': '11',
            'bingol': '12', 'bitlis': '13', 'bolu': '14', 'burdur': '15',
            'bursa': '16', 'canakkale': '17', 'cankiri': '18', 'corum': '19',
            'denizli': '20', 'diyarbakir': '21', 'duzce': '81', 'edirne': '22',
            'elazig': '23', 'erzincan': '24', 'erzurum': '25', 'eskisehir': '26',
            'gaziantep': '27', 'giresun': '28', 'gumushane': '29', 'hakkari': '30',
            'hatay': '31', 'igdir': '76', 'isparta': '32', 'istanbul': '34',
            'izmir': '35', 'kahramanmaras': '46', 'karabuk': '78', 'karaman': '70',
            'kars': '36', 'kastamonu': '37', 'kayseri': '38', 'kilis': '79',
            'kirikkale': '71', 'kirklareli': '39', 'kirsehir': '40', 'kocaeli': '41',
            'konya': '42', 'kutahya': '43', 'malatya': '44', 'manisa': '45',
            'mardin': '47', 'mersin': '33', 'mugla': '48', 'mus': '49',
            'nevsehir': '50', 'nigde': '51', 'ordu': '52', 'osmaniye': '80',
            'rize': '53', 'sakarya': '54', 'samsun': '55', 'sanliurfa': '63',
            'siirt': '56', 'sinop': '57', 'sirnak': '73', 'sivas': '58',
            'tekirdag': '59', 'tokat': '60', 'trabzon': '61', 'tunceli': '62',
            'usak': '64', 'van': '65', 'yalova': '77', 'yozgat': '66', 'zonguldak': '67'
        }
        
        # Tip kodları
        tip_kodlari = {
            'Üniversite Hastanesi': 'UH',
            'Tıp Merkezi': 'TM',
            'Diyaliz Merkezi': 'DM',
            'Fizik Tedavi ve Rehabilitasyon Merkezi': 'FT',
            'Göz Hastalıkları Merkezi': 'GH',
            'Onkoloji Merkezi': 'ON',
            'Tüp Bebek Merkezi': 'TB',
            'Psikiyatri Merkezi': 'PS'
        }
        
        il_adi = facility.get('il_adi', '').lower()
        kurum_tipi = facility.get('kurum_tipi', '')
        kurum_adi = facility.get('kurum_adi', '')
        
        il_kodu = il_kodlari.get(il_adi, '99')
        tip_kodu = tip_kodlari.get(kurum_tipi, 'SK')
        
        # Sıra numarası için hash kullan
        hash_input = f"{kurum_adi}{il_adi}{kurum_tipi}".lower()
        hash_digest = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        sira_no = hash_digest[:4].upper()
        
        return f"TR-{il_kodu}-{tip_kodu}-{sira_no}"

    def save_data(self, facilities: List[Dict]) -> Tuple[str, str]:
        """Verileri JSON ve CSV formatlarında kaydet"""
        # ID'leri ekle
        for facility in facilities:
            facility['kurum_id'] = self.generate_facility_id(facility)
        
        # Dosya yolları
        json_file = os.path.join(self.data_dir, 'trhastane_data.json')
        csv_file = os.path.join(self.data_dir, 'trhastane_data.csv')
        hash_file = os.path.join(self.data_dir, 'trhastane_hash.json')
        
        # JSON kaydet
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(facilities, f, ensure_ascii=False, indent=2)
        
        # CSV kaydet
        if facilities:
            import pandas as pd
            df = pd.DataFrame(facilities)
            df.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Hash kaydet
        data_str = json.dumps(facilities, sort_keys=True, ensure_ascii=False)
        data_hash = hashlib.md5(data_str.encode('utf-8')).hexdigest()
        
        hash_data = {
            'hash': data_hash,
            'timestamp': datetime.now().isoformat(),
            'count': len(facilities)
        }
        
        with open(hash_file, 'w', encoding='utf-8') as f:
            json.dump(hash_data, f, ensure_ascii=False, indent=2)
        
        return json_file, csv_file

    def has_data_changed(self) -> bool:
        """Verinin değişip değişmediğini kontrol et - hızlı güncellemeler için"""
        hash_file = os.path.join(self.data_dir, 'trhastane_hash.json')
        
        if not os.path.exists(hash_file):
            return True
        
        try:
            with open(hash_file, 'r', encoding='utf-8') as f:
                old_hash_data = json.load(f)
            
            # 1 aydan eski ise güncelle (daha sık güncelleme)
            old_timestamp = datetime.fromisoformat(old_hash_data['timestamp'])
            if (datetime.now() - old_timestamp).days > 30:
                logger.info("1 aydan eski veri - güncelleme gerekli")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Hash kontrolünde hata: {e}")
            return True

def main():
    """Ana fonksiyon - hızlı ve güvenilir veri çekme"""
    logger.info("TR Hastane hızlı veri çekme işlemi başlıyor...")
    logger.info("🎯 Hedef: Üniversite hastaneleri ve tıp merkezleri (öncelikli şehirler)")
    
    fetcher = TRHastaneDataFetcher()
    
    # Veri değişikliği kontrolü
    if not fetcher.has_data_changed():
        logger.info("Veri güncel - güncelleme yapılmıyor")
        return
    
    try:
        # Hızlı veri çekme
        start_time = datetime.now()
        facilities = fetcher.fetch_all_data()
        end_time = datetime.now()
        
        if not facilities:
            logger.warning("Hiç veri çekilemedi!")
            return
        
        # Verileri kaydet
        json_file, csv_file = fetcher.save_data(facilities)
        
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"✅ İşlem tamamlandı! ({duration:.1f} saniye)")
        logger.info(f"📊 Toplam kurum sayısı: {len(facilities)}")
        logger.info(f"💾 JSON dosyası: {json_file}")
        logger.info(f"💾 CSV dosyası: {csv_file}")
        
        # Kategori bazlı istatistikler
        category_stats = {}
        city_stats = {}
        for facility in facilities:
            category = facility.get('kurum_tipi', 'Diğer')
            city = facility.get('il_adi', 'Bilinmiyor')
            category_stats[category] = category_stats.get(category, 0) + 1
            city_stats[city] = city_stats.get(city, 0) + 1
        
        logger.info("📈 Kategori bazlı dağılım:")
        for category, count in sorted(category_stats.items()):
            logger.info(f"  - {category}: {count}")
            
        logger.info("🏙️  Şehir bazlı dağılım:")
        for city, count in sorted(city_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  - {city}: {count}")
        
    except Exception as e:
        logger.error(f"Veri çekme işleminde hata: {e}")
        # Kısmi veri bile olsa kaydet
        if 'facilities' in locals() and facilities:
            logger.info("Kısmi veri kaydediliyor...")
            fetcher.save_data(facilities)
        raise

if __name__ == "__main__":
    main()
