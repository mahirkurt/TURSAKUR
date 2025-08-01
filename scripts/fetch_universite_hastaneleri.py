#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Üniversite Hastaneleri Veri Çıkarıcısı
==================================================

Tier 1 - En Yüksek Öncelik Kaynak
Hedef: YÖK ve Üniversite web sitelerinden üniversite hastaneleri

Çıkarılan Veriler:
- Üniversite Hastaneleri
- Tıp Fakültesi Hastaneleri  
- Araştırma ve Uygulama Hastaneleri
- Diş Hekimliği Fakültesi Hastaneleri
"""

import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import time
import re
from urllib.parse import urljoin, urlparse

# BeautifulSoup for HTML parsing
from bs4 import BeautifulSoup

# Selenium for JavaScript-heavy pages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class UniversiteHastaneleriScraper:
    """Üniversite hastanelerini çıkarır"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TURSAKUR/2.0 (Turkey Health Facilities Database)',
            'Accept': 'application/json, text/html, application/xhtml+xml, */*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })
        
        # YÖK Atlas endpoints
        self.yok_atlas_base = "https://yokatlas.yok.gov.tr"
        self.yok_programs_url = f"{self.yok_atlas_base}/lisans-bolum.php?b=10166"  # Tıp programı
        
        # Chrome options for Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # Rate limiting
        self.request_delay = 1.0
        self.last_request_time = 0
        
        # Data storage
        self.data_dir = Path(__file__).parent.parent / "data" / "raw"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.results = {
            'universities': [],
            'hospitals': [],
            'medical_faculties': [],
            'dental_faculties': []
        }

    def _rate_limit(self):
        """Rate limiting implementation"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()

    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Rate-limited HTTP request with error handling"""
        self._rate_limit()
        
        try:
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None

    def fetch_medical_universities_from_yok(self) -> List[Dict]:
        """YÖK Atlas'tan tıp fakültesi olan üniversiteleri çeker"""
        self.logger.info("YÖK Atlas'tan tıp fakültesi olan üniversiteler çekiliyor...")
        
        response = self._make_request(self.yok_programs_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        universities = []
        
        # Look for university tables or lists
        university_elements = soup.find_all(['table', 'div'], 
                                          class_=lambda x: x and any(keyword in x.lower() 
                                                                   for keyword in ['universite', 'university', 'table']))
        
        for element in university_elements:
            # Extract university names and links
            links = element.find_all('a')
            for link in links:
                href = link.get('href')
                text = link.text.strip()
                
                if href and text and 'üniversite' in text.lower():
                    university_data = {
                        'isim': text,
                        'yok_url': urljoin(self.yok_atlas_base, href) if not href.startswith('http') else href,
                        'tip': 'Üniversite',
                        'tip_detay': 'Tıp Fakültesi Var',
                        'kaynak': 'YÖK Atlas',
                        'kaynak_url': self.yok_programs_url,
                        'tarih': datetime.now(timezone.utc).isoformat()
                    }
                    universities.append(university_data)
        
        # Also try to extract from text content
        text_content = soup.get_text()
        university_patterns = [
            r'(\w+\s+ÜNİVERSİTESİ)',
            r'(\w+\s+UNIVERSITY)',
            r'(\w+\s+ÜNİVERSİTESİ\s+TIP\s+FAKÜLTESİ)'
        ]
        
        for pattern in university_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                university_name = match.strip()
                if university_name and len(university_name) > 5:
                    university_data = {
                        'isim': university_name,
                        'yok_url': self.yok_programs_url,
                        'tip': 'Üniversite',
                        'tip_detay': 'Tıp Fakültesi Var',
                        'kaynak': 'YÖK Atlas Text',
                        'kaynak_url': self.yok_programs_url,
                        'tarih': datetime.now(timezone.utc).isoformat()
                    }
                    universities.append(university_data)
        
        # Remove duplicates
        seen = set()
        unique_universities = []
        for uni in universities:
            key = uni['isim'].upper().strip()
            if key not in seen and len(key) > 5:
                seen.add(key)
                unique_universities.append(uni)
        
        self.logger.info(f"YÖK Atlas'tan {len(unique_universities)} üniversite bulundu")
        return unique_universities

    def get_university_website(self, university_name: str) -> Optional[str]:
        """Üniversite adından resmi web sitesini bulmaya çalışır"""
        # Common patterns for Turkish university websites
        name_clean = re.sub(r'\s+ÜNİVERSİTESİ.*', '', university_name, flags=re.IGNORECASE).strip()
        name_parts = name_clean.lower().split()
        
        possible_domains = [
            f"https://www.{name_parts[0]}.edu.tr",
            f"https://{name_parts[0]}.edu.tr",
            f"https://www.{''.join(name_parts[:2])}.edu.tr" if len(name_parts) > 1 else None,
            f"https://{''.join(name_parts[:2])}.edu.tr" if len(name_parts) > 1 else None
        ]
        
        for domain in possible_domains:
            if domain:
                response = self._make_request(domain)
                if response and response.status_code == 200:
                    return domain
        
        return None

    def scrape_university_hospitals(self, university_name: str, website_url: str) -> List[Dict]:
        """Üniversite web sitesinden hastane bilgilerini çeker"""
        if not website_url:
            return []
        
        self.logger.info(f"Hastane bilgileri çekiliyor: {university_name}")
        
        hospitals = []
        
        # Common hospital-related page patterns
        hospital_pages = [
            '/hastane',
            '/hastaneler',
            '/tip-fakultesi',
            '/saglik',
            '/arastirma-hastanesi',
            '/uygulama-hastanesi',
            '/dis-hekimligi'
        ]
        
        for page_path in hospital_pages:
            url = urljoin(website_url, page_path)
            response = self._make_request(url)
            
            if not response:
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for hospital information
            hospital_elements = soup.find_all(['div', 'section', 'article'], 
                                            class_=lambda x: x and any(keyword in x.lower() 
                                                                     for keyword in ['hastane', 'hospital', 'medical', 'tip']))
            
            for element in hospital_elements:
                text = element.get_text(strip=True)
                
                # Extract hospital names
                hospital_patterns = [
                    r'(\w+.*?HASTANE(?:Sİ)?)',
                    r'(\w+.*?TIP\s+FAKÜLTESİ\s+HASTANE(?:Sİ)?)',
                    r'(\w+.*?ARAŞTIRMA\s+HASTANE(?:Sİ)?)',
                    r'(\w+.*?UYGULAMA\s+HASTANE(?:Sİ)?)'
                ]
                
                for pattern in hospital_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        hospital_name = match.strip()
                        if hospital_name and len(hospital_name) > 10:
                            # Extract contact information
                            contact_info = self._extract_contact_info(element)
                            
                            hospital_data = {
                                'isim': hospital_name,
                                'universite': university_name,
                                'tip': 'Üniversite Hastanesi',
                                'tip_detay': self._determine_hospital_subtype(hospital_name),
                                'kaynak': 'Üniversite Web Sitesi',
                                'kaynak_url': url,
                                'universite_website': website_url,
                                'tarih': datetime.now(timezone.utc).isoformat(),
                                **contact_info
                            }
                            hospitals.append(hospital_data)
        
        return hospitals

    def _extract_contact_info(self, element) -> Dict:
        """HTML elementinden iletişim bilgilerini çıkarır"""
        text = element.get_text()
        contact_info = {}
        
        # Phone numbers
        phone_pattern = r'(\+90[\s\-]?)?(\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['telefon'] = phones[0][1] if phones[0][1] else phones[0][0]
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Addresses (basic extraction)
        address_keywords = ['adres', 'address', 'mahalle', 'sokak', 'cadde', 'bulvar']
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in address_keywords):
                if len(line.strip()) > 20 and len(line.strip()) < 200:
                    contact_info['adres'] = line.strip()
                    break
        
        return contact_info

    def _determine_hospital_subtype(self, hospital_name: str) -> str:
        """Hastane adından alt tipini belirler"""
        name_lower = hospital_name.lower()
        
        if 'araştırma' in name_lower and 'uygulama' in name_lower:
            return 'Araştırma ve Uygulama Hastanesi'
        elif 'araştırma' in name_lower:
            return 'Araştırma Hastanesi'
        elif 'uygulama' in name_lower:
            return 'Uygulama Hastanesi'
        elif 'tıp fakültesi' in name_lower:
            return 'Tıp Fakültesi Hastanesi'
        elif 'diş hekimliği' in name_lower:
            return 'Diş Hekimliği Fakültesi Hastanesi'
        else:
            return 'Üniversite Hastanesi'

    def save_data(self):
        """Çekilen veriyi JSON dosyasına kaydeder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"universite_hastaneleri_{timestamp}.json"
        filepath = self.data_dir / filename
        
        output_data = {
            'kaynak': 'YÖK ve Üniversite Web Siteleri',
            'tier': 1,
            'cekme_tarihi': datetime.now(timezone.utc).isoformat(),
            'toplam_kayit': sum(len(v) for v in self.results.values()),
            'veriler': self.results,
            'meta': {
                'yok_atlas_url': self.yok_programs_url,
                'scraper_version': '2.0',
                'veri_tipi': 'universite_hastaneleri'
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Veri kaydedildi: {filepath}")
        return filepath

    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.logger.info("Üniversite hastaneleri veri çekme işlemi başlatılıyor...")
        
        try:
            # YÖK Atlas'tan üniversiteleri çek
            universities = self.fetch_medical_universities_from_yok()
            self.results['universities'] = universities
            
            # Her üniversite için web sitesini bul ve hastane bilgilerini çek
            for university in universities[:20]:  # İlk 20 üniversite için test
                website = self.get_university_website(university['isim'])
                if website:
                    university['website'] = website
                    hospitals = self.scrape_university_hospitals(university['isim'], website)
                    self.results['hospitals'].extend(hospitals)
                    
                    # Rate limiting
                    time.sleep(2)
            
            # Veriyi kaydet
            self.save_data()
            
            self.logger.info("Üniversite hastaneleri veri çekme işlemi tamamlandı")
            return True
            
        except Exception as e:
            self.logger.error(f"Üniversite hastaneleri veri çekme sırasında hata: {e}")
            return False

def main():
    """Ana fonksiyon"""
    scraper = UniversiteHastaneleriScraper()
    success = scraper.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
