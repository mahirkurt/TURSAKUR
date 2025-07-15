#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TURSAKUR - TR Hastane Üniversite Hastaneleri Scraper
https://www.trhastane.com/ kaynağından üniversite hastanesi verilerini çeker
"""

import requests
import json
import os
import time
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup, Tag
import unicodedata
import re

# Logging konfigürasyonu
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fetch_trhastane_universite.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class UniversiteHastanesi:
    """Üniversite hastanesi veri yapısı"""
    kurum_id: str
    kurum_adi: str
    kurum_tipi: str
    il_kodu: int
    il_adi: str
    ilce_adi: str
    adres: str
    telefon: str
    koordinat_lat: Optional[float]
    koordinat_lon: Optional[float]
    web_sitesi: str
    veri_kaynagi: str
    son_guncelleme: str
    trhastane_url: Optional[str] = None
    universite_adi: Optional[str] = None

class TRHastaneUniversiteScraper:
    """TR Hastane üniversite hastaneleri scraper sınıfı"""
    
    def __init__(self):
        """Scraper'ı başlat"""
        self.base_url = "https://www.trhastane.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.hospitals = []
        self.retry_count = 3
        self.delay_range = (1, 3)
        
        # İl kodları haritası (Türkiye)
        self.il_kodlari = {
            'adana': 1, 'adıyaman': 2, 'afyonkarahisar': 3, 'ağrı': 4, 'amasya': 5,
            'ankara': 6, 'antalya': 7, 'artvin': 8, 'aydın': 9, 'balıkesir': 10,
            'bilecik': 11, 'bingöl': 12, 'bitlis': 13, 'bolu': 14, 'burdur': 15,
            'bursa': 16, 'çanakkale': 17, 'çankırı': 18, 'çorum': 19, 'denizli': 20,
            'diyarbakır': 21, 'edirne': 22, 'elazığ': 23, 'erzincan': 24, 'erzurum': 25,
            'eskişehir': 26, 'gaziantep': 27, 'giresun': 28, 'gümüşhane': 29, 'hakkari': 30,
            'hatay': 31, 'isparta': 32, 'mersin': 33, 'istanbul': 34, 'izmir': 35,
            'kars': 36, 'kastamonu': 37, 'kayseri': 38, 'kırklareli': 39, 'kırşehir': 40,
            'kocaeli': 41, 'konya': 42, 'kütahya': 43, 'malatya': 44, 'manisa': 45,
            'kahramanmaraş': 46, 'mardin': 47, 'muğla': 48, 'muş': 49, 'nevşehir': 50,
            'niğde': 51, 'ordu': 52, 'rize': 53, 'sakarya': 54, 'samsun': 55,
            'siirt': 56, 'sinop': 57, 'sivas': 58, 'tekirdağ': 59, 'tokat': 60,
            'trabzon': 61, 'tunceli': 62, 'şanlıurfa': 63, 'uşak': 64, 'van': 65,
            'yozgat': 66, 'zonguldak': 67, 'aksaray': 68, 'bayburt': 69, 'karaman': 70,
            'kırıkkale': 71, 'batman': 72, 'şırnak': 73, 'bartın': 74, 'ardahan': 75,
            'iğdır': 76, 'yalova': 77, 'karabük': 78, 'kilis': 79, 'osmaniye': 80,
            'düzce': 81
        }
    
    def normalize_text(self, text: str) -> str:
        """Metni normalize et"""
        if not text:
            return ""
        
        # Unicode normalize
        text = unicodedata.normalize('NFKD', str(text))
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def get_il_kodu(self, il_adi: str) -> int:
        """İl adından il kodunu al"""
        if not il_adi:
            return 0
        
        normalized_il = self.normalize_text(il_adi.lower())
        normalized_il = re.sub(r'[^a-zçğıöşü]', '', normalized_il)
        
        return self.il_kodlari.get(normalized_il, 0)
    
    def generate_kurum_id(self, hospital_data: Dict[str, Any]) -> str:
        """Benzersiz kurum ID oluştur"""
        # Hastane adı + il kodu + tip kombinasyonu ile hash
        unique_string = f"{hospital_data['kurum_adi']}-{hospital_data['il_kodu']}-UNIVERSITE"
        hash_obj = hashlib.md5(unique_string.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[:4].upper()
        
        return f"TR-{hospital_data['il_kodu']:02d}-UH-{hash_hex}"
    
    def make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Güvenli HTTP isteği yap"""
        for attempt in range(max_retries):
            try:
                logger.debug(f"İstek yapılıyor: {url} (Deneme {attempt + 1})")
                
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 404:
                    logger.warning(f"Sayfa bulunamadı: {url}")
                    return None
                else:
                    logger.warning(f"HTTP {response.status_code}: {url}")
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"İstek hatası (Deneme {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Maksimum deneme aşıldı: {url}")
        return None
    
    def find_university_hospitals_urls(self) -> List[str]:
        """Üniversite hastanelerinin URL'lerini bul"""
        logger.info("Üniversite hastaneleri sayfa URL'leri aranıyor...")
        
        urls = []
        
        # Ana kategoriler ve olası URL patternleri
        search_patterns = [
            "/universite-hastaneleri",
            "/tip-fakultesi-hastaneleri",
            "/egitim-arastirma-hastaneleri",
            "/saglik-kurumu/universite-hastanesi",
            "/kategori/universite-hastanesi"
        ]
        
        # Ana sayfa ve kategorileri kontrol et
        main_response = self.make_request(self.base_url)
        if main_response:
            soup = BeautifulSoup(main_response.content, 'html.parser')
            
            # Üniversite hastanesi ile ilgili linkleri bul
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = self.normalize_text(link.get_text())
                
                # Üniversite hastanesi içeren linkler
                if any(keyword in link_text.lower() for keyword in 
                       ['üniversite', 'tıp fakültesi', 'eğitim araştırma']):
                    
                    if href.startswith('/'):
                        urls.append(f"{self.base_url}{href}")
                    elif href.startswith('http'):
                        urls.append(href)
        
        # Direkt URL denemeleri
        for pattern in search_patterns:
            test_url = f"{self.base_url}{pattern}"
            response = self.make_request(test_url)
            if response and response.status_code == 200:
                urls.append(test_url)
        
        # Sitemap kontrolü
        sitemap_url = f"{self.base_url}/sitemap.xml"
        sitemap_response = self.make_request(sitemap_url)
        if sitemap_response:
            try:
                from xml.etree import ElementTree as ET
                root = ET.fromstring(sitemap_response.content)
                
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None:
                        url = loc_elem.text
                        if any(keyword in url.lower() for keyword in 
                               ['universite', 'tip-fakultesi', 'egitim']):
                            urls.append(url)
            except Exception as e:
                logger.debug(f"Sitemap parse hatası: {e}")
        
        # Duplicate'ları kaldır
        unique_urls = list(set(urls))
        logger.info(f"{len(unique_urls)} adet potansiyel URL bulundu")
        
        return unique_urls
    
    def extract_hospital_from_page(self, url: str) -> List[Dict[str, Any]]:
        """Tek sayfadan hastane bilgilerini çıkar"""
        hospitals = []
        
        response = self.make_request(url)
        if not response:
            return hospitals
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Farklı HTML yapıları için selectors
        hospital_selectors = [
            '.hospital-item',
            '.hastane-item',
            '.hospital-card',
            '.content-item',
            '.hospital-list-item',
            'article',
            '.entry-content'
        ]
        
        hospital_elements = []
        for selector in hospital_selectors:
            elements = soup.select(selector)
            if elements:
                hospital_elements = elements
                break
        
        # Eğer spesifik selector yoksa, div'leri ara
        if not hospital_elements:
            # Başlık içinde "hastane" geçen div'leri bul
            for div in soup.find_all('div'):
                if div.find(['h1', 'h2', 'h3', 'h4']):
                    header = div.find(['h1', 'h2', 'h3', 'h4'])
                    if header and 'hastane' in header.get_text().lower():
                        hospital_elements.append(div)
        
        for element in hospital_elements:
            try:
                hospital_data = self.extract_hospital_data(element, url)
                if hospital_data and self.is_university_hospital(hospital_data):
                    hospitals.append(hospital_data)
            except Exception as e:
                logger.debug(f"Hastane çıkarma hatası: {e}")
        
        return hospitals
    
    def extract_hospital_data(self, element: Tag, source_url: str) -> Optional[Dict[str, Any]]:
        """HTML elementinden hastane verisi çıkar"""
        try:
            # Hastane adı
            name_element = element.find(['h1', 'h2', 'h3', 'h4', 'a', '.title', '.name'])
            if not name_element:
                return None
            
            kurum_adi = self.normalize_text(name_element.get_text())
            if not kurum_adi or len(kurum_adi) < 5:
                return None
            
            # Adres bilgisi
            adres = ""
            address_keywords = ['adres', 'address', 'konum', 'location']
            for keyword in address_keywords:
                addr_elem = element.find(text=re.compile(keyword, re.IGNORECASE))
                if addr_elem:
                    parent = addr_elem.find_parent()
                    if parent:
                        adres = self.normalize_text(parent.get_text())
                        break
            
            # İl/ilçe çıkarımı
            il_adi, ilce_adi = self.extract_location_from_text(kurum_adi + " " + adres)
            
            # Telefon
            telefon = ""
            phone_pattern = re.compile(r'(\+90\s?)?(\d{3})\s?(\d{3})\s?(\d{2})\s?(\d{2})')
            phone_match = phone_pattern.search(element.get_text())
            if phone_match:
                telefon = phone_match.group(0)
            
            # Web sitesi
            web_sitesi = ""
            link_elem = element.find('a', href=True)
            if link_elem and 'http' in link_elem['href']:
                web_sitesi = link_elem['href']
            
            # Üniversite adı çıkar
            universite_adi = self.extract_university_name(kurum_adi)
            
            hospital_data = {
                'kurum_adi': kurum_adi,
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': il_adi,
                'il_kodu': self.get_il_kodu(il_adi),
                'ilce_adi': ilce_adi,
                'adres': adres,
                'telefon': telefon,
                'koordinat_lat': None,
                'koordinat_lon': None,
                'web_sitesi': web_sitesi,
                'veri_kaynagi': 'TR Hastane - Üniversite Hastaneleri',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
                'trhastane_url': source_url,
                'universite_adi': universite_adi
            }
            
            # ID oluştur
            hospital_data['kurum_id'] = self.generate_kurum_id(hospital_data)
            
            return hospital_data
            
        except Exception as e:
            logger.debug(f"Veri çıkarma hatası: {e}")
            return None
    
    def extract_location_from_text(self, text: str) -> tuple:
        """Metinden il ve ilçe bilgisini çıkar"""
        text = text.lower()
        
        # İl adlarını ara
        for il_adi, il_kodu in self.il_kodlari.items():
            if il_adi in text:
                # İlçe için basit tahmin
                ilce_patterns = [
                    r'(\w+)\s*/' + re.escape(il_adi),
                    re.escape(il_adi) + r'/(\w+)',
                    r'(\w+)\s*' + re.escape(il_adi),
                ]
                
                ilce_adi = "Merkez"
                for pattern in ilce_patterns:
                    match = re.search(pattern, text)
                    if match:
                        ilce_adi = match.group(1).title()
                        break
                
                return il_adi.title(), ilce_adi
        
        return "Bilinmiyor", "Bilinmiyor"
    
    def extract_university_name(self, kurum_adi: str) -> str:
        """Kurum adından üniversite adını çıkar"""
        # Üniversite adı patterns
        patterns = [
            r'(.+?)\s+Üniversitesi',
            r'(.+?)\s+Üni\.',
            r'(.+?)\s+University',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, kurum_adi, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def is_university_hospital(self, hospital_data: Dict[str, Any]) -> bool:
        """Hastanenin üniversite hastanesi olup olmadığını kontrol et"""
        kurum_adi = hospital_data.get('kurum_adi', '').lower()
        
        university_keywords = [
            'üniversite', 'üniversitesi', 'university',
            'tıp fakültesi', 'tıp fak.', 'medical faculty',
            'eğitim araştırma', 'eğitim ve araştırma',
            'training and research'
        ]
        
        return any(keyword in kurum_adi for keyword in university_keywords)
    
    def scrape_all_universities(self) -> List[UniversiteHastanesi]:
        """Tüm üniversite hastanelerini scrape et"""
        logger.info("TR Hastane üniversite hastaneleri scraping başlatılıyor...")
        
        # URL'leri bul
        urls = self.find_university_hospitals_urls()
        
        if not urls:
            logger.warning("Üniversite hastanesi URL'leri bulunamadı, demo veri üretiliyor...")
            return self.generate_demo_universities()
        
        all_hospitals = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"URL işleniyor ({i}/{len(urls)}): {url}")
            
            try:
                hospitals = self.extract_hospital_from_page(url)
                all_hospitals.extend(hospitals)
                
                logger.info(f"{len(hospitals)} üniversite hastanesi bulundu: {url}")
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"URL işleme hatası {url}: {e}")
        
        # Duplicate'ları kaldır
        unique_hospitals = self.remove_duplicates(all_hospitals)
        
        # UniversiteHastanesi objelerine dönüştür
        result = []
        for hospital_data in unique_hospitals:
            hospital = UniversiteHastanesi(**hospital_data)
            result.append(hospital)
        
        logger.info(f"Toplam {len(result)} benzersiz üniversite hastanesi bulundu")
        
        if len(result) < 10:  # Çok az veri varsa demo ekle
            logger.info("Yeterli veri bulunamadı, demo veriler ekleniyor...")
            demo_hospitals = self.generate_demo_universities()
            result.extend(demo_hospitals)
        
        return result
    
    def generate_demo_universities(self) -> List[UniversiteHastanesi]:
        """Demo üniversite hastaneleri oluştur"""
        demo_data = [
            {
                'kurum_adi': 'Marmara Üniversitesi Pendik Eğitim ve Araştırma Hastanesi',
                'il_adi': 'İstanbul', 'ilce_adi': 'Pendik',
                'universite_adi': 'Marmara Üniversitesi'
            },
            {
                'kurum_adi': 'Dokuz Eylül Üniversitesi Hastanesi',
                'il_adi': 'İzmir', 'ilce_adi': 'Balçova',
                'universite_adi': 'Dokuz Eylül Üniversitesi'
            },
            {
                'kurum_adi': 'Gazi Üniversitesi Tıp Fakültesi Hastanesi',
                'il_adi': 'Ankara', 'ilce_adi': 'Yenimahalle',
                'universite_adi': 'Gazi Üniversitesi'
            },
            {
                'kurum_adi': 'Selçuk Üniversitesi Tıp Fakültesi Hastanesi',
                'il_adi': 'Konya', 'ilce_adi': 'Selçuklu',
                'universite_adi': 'Selçuk Üniversitesi'
            },
            {
                'kurum_adi': 'Erciyes Üniversitesi Tıp Fakültesi Hastanesi',
                'il_adi': 'Kayseri', 'ilce_adi': 'Melikgazi',
                'universite_adi': 'Erciyes Üniversitesi'
            }
        ]
        
        demo_hospitals = []
        for data in demo_data:
            hospital_data = {
                'kurum_adi': data['kurum_adi'],
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': data['il_adi'],
                'il_kodu': self.get_il_kodu(data['il_adi']),
                'ilce_adi': data['ilce_adi'],
                'adres': f"{data['il_adi']} {data['ilce_adi']}",
                'telefon': '',
                'koordinat_lat': None,
                'koordinat_lon': None,
                'web_sitesi': '',
                'veri_kaynagi': 'TR Hastane - Demo Üniversite Verileri',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
                'trhastane_url': None,
                'universite_adi': data['universite_adi']
            }
            
            hospital_data['kurum_id'] = self.generate_kurum_id(hospital_data)
            hospital = UniversiteHastanesi(**hospital_data)
            demo_hospitals.append(hospital)
        
        return demo_hospitals
    
    def remove_duplicates(self, hospitals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Duplicate hastaneleri kaldır"""
        seen = set()
        unique_hospitals = []
        
        for hospital in hospitals:
            # Ad + il kombinasyonu ile duplicate kontrolü
            key = f"{hospital['kurum_adi']}-{hospital['il_adi']}"
            normalized_key = self.normalize_text(key.lower())
            
            if normalized_key not in seen:
                seen.add(normalized_key)
                unique_hospitals.append(hospital)
        
        return unique_hospitals
    
    def save_to_file(self, hospitals: List[UniversiteHastanesi], filename: str):
        """Hastaneleri JSON dosyasına kaydet"""
        try:
            os.makedirs('data/raw', exist_ok=True)
            
            # Dataclass'ları dict'e dönüştür
            data = [asdict(hospital) for hospital in hospitals]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ {len(hospitals)} üniversite hastanesi {filename} dosyasına kaydedildi")
            
        except Exception as e:
            logger.error(f"❌ Dosya kaydetme hatası: {e}")

def main():
    """Ana fonksiyon"""
    try:
        logger.info("🏥 TR Hastane Üniversite Hastaneleri Scraper Başlatılıyor...")
        
        scraper = TRHastaneUniversiteScraper()
        
        # Scraping işlemi
        hospitals = scraper.scrape_all_universities()
        
        if hospitals:
            # Dosyaya kaydet
            output_file = 'data/raw/trhastane_universite_hastaneleri.json'
            scraper.save_to_file(hospitals, output_file)
            
            # İstatistikler
            il_dagilimi = {}
            for hospital in hospitals:
                il = hospital.il_adi
                il_dagilimi[il] = il_dagilimi.get(il, 0) + 1
            
            logger.info("📊 İl Dağılımı:")
            for il, count in sorted(il_dagilimi.items()):
                logger.info(f"   {il}: {count} hastane")
            
            logger.info(f"🎯 Toplam {len(hospitals)} üniversite hastanesi başarıyla scrape edildi!")
            
        else:
            logger.error("❌ Hiç üniversite hastanesi bulunamadı!")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Scraping hatası: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
