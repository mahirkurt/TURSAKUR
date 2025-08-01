#!/usr/bin/env python3
"""
TURSAKUR 2.0 - T.C. Sağlık Bakanlığı Veri Çıkarıcısı
===============================================

Tier 1 - En Yüksek Öncelik Kaynak
Hedefler:
- Kamu Hastaneleri Genel Müdürlüğü (KHGM)
- Sağlık Bilgi Sistemleri Genel Müdürlüğü (SBSGM)
- Yönetim Hizmetleri Genel Müdürlüğü (YHGM)

Çıkarılan Veriler:
- Şehir Hastaneleri
- Devlet Hastaneleri
- ADSM (Ağız ve Diş Sağlığı Merkezleri)
- ASM (Aile Sağlığı Merkezleri)
- TSM (Toplum Sağlığı Merkezleri)
"""

import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import time
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

class SaglikBakanligiScraper:
    """T.C. Sağlık Bakanlığı portallarından veri çıkarır"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TURSAKUR/2.0 (Turkey Health Facilities Database)',
            'Accept': 'application/json, text/html, application/xhtml+xml, */*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })
        
        # Rate limiting
        self.request_delay = 1.0  # seconds
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
        
        # Known endpoints and patterns
        self.endpoints = {
            'khgm_base': 'https://khgm.saglik.gov.tr',
            'sbsgm_base': 'https://sbsgm.saglik.gov.tr',
            'yhgm_base': 'https://yhgm.saglik.gov.tr',
            'yhgm_il_saglik': 'https://yhgm.saglik.gov.tr/TR-6420/il-saglik-mudurlukleri.html'
        }
        
        self.results = {
            'sehir_hastaneleri': [],
            'devlet_hastaneleri': [],
            'adsm_merkezleri': [],
            'asm_merkezleri': [],
            'tsm_merkezleri': [],
            'il_saglik_mudurlukleri': []
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

    def fetch_khgm_hospitals(self) -> List[Dict]:
        """KHGM'den hastane listelerini çeker"""
        self.logger.info("KHGM hastane listesi çekiliyor...")
        
        # Potential KHGM hospital listing pages
        khgm_pages = [
            '/TR-6242/sehir-hastaneleri.html',
            '/TR-6243/devlet-hastaneleri.html',
            '/TR-6244/egitim-arastirma-hastaneleri.html',
            '/TR-6245/dal-hastaneleri.html'
        ]
        
        hospitals = []
        
        for page_path in khgm_pages:
            url = urljoin(self.endpoints['khgm_base'], page_path)
            response = self._make_request(url)
            
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for hospital lists in various formats
            hospital_elements = soup.find_all(['div', 'ul', 'table'], 
                                            class_=lambda x: x and any(keyword in x.lower() 
                                                                     for keyword in ['hastane', 'kurum', 'liste']))
            
            for element in hospital_elements:
                # Extract hospital names and details
                links = element.find_all('a')
                for link in links:
                    if link.get('href') and 'hastane' in link.text.lower():
                        hospital_data = {
                            'isim': link.text.strip(),
                            'url': urljoin(url, link.get('href')),
                            'tip': self._determine_hospital_type(page_path),
                            'kaynak': 'KHGM',
                            'kaynak_url': url,
                            'tarih': datetime.now(timezone.utc).isoformat()
                        }
                        hospitals.append(hospital_data)
        
        self.logger.info(f"KHGM'den {len(hospitals)} hastane bulundu")
        return hospitals

    def fetch_il_saglik_mudurlukleri(self) -> List[Dict]:
        """81 İl Sağlık Müdürlüğü listesini çeker"""
        self.logger.info("İl Sağlık Müdürlükleri listesi çekiliyor...")
        
        response = self._make_request(self.endpoints['yhgm_il_saglik'])
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        il_mudurlukleri = []
        
        # Look for links to provincial health directorates
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            text = link.text.strip()
            
            # Check if this looks like a provincial health directorate
            if (href and 'ism.saglik.gov.tr' in href) or \
               (text and any(keyword in text.lower() for keyword in ['sağlık müdürlüğü', 'il sağlık'])):
                
                il_data = {
                    'isim': text,
                    'url': href if href.startswith('http') else urljoin(self.endpoints['yhgm_base'], href),
                    'tip': 'İl Sağlık Müdürlüğü',
                    'kaynak': 'YHGM',
                    'kaynak_url': self.endpoints['yhgm_il_saglik'],
                    'tarih': datetime.now(timezone.utc).isoformat()
                }
                il_mudurlukleri.append(il_data)
        
        self.logger.info(f"YHGM'den {len(il_mudurlukleri)} İl Sağlık Müdürlüğü bulundu")
        return il_mudurlukleri

    def fetch_detailed_hospital_info(self, hospital_url: str) -> Dict:
        """Hastane detay sayfasından ek bilgi çeker"""
        response = self._make_request(hospital_url)
        if not response:
            return {}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract additional information
        info = {}
        
        # Look for contact information
        contact_selectors = [
            'div[class*="iletisim"]',
            'div[class*="contact"]',
            'div[class*="adres"]',
            'div[class*="telefon"]'
        ]
        
        for selector in contact_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                
                # Extract phone numbers
                import re
                phones = re.findall(r'(\+90[\s\-]?)?(\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})', text)
                if phones:
                    info['telefon'] = phones[0][1] if phones[0][1] else phones[0][0]
                
                # Extract addresses
                if any(keyword in text.lower() for keyword in ['adres', 'address', 'lokasyon']):
                    info['adres'] = text
        
        return info

    def _determine_hospital_type(self, page_path: str) -> str:
        """Sayfa yolundan hastane tipini belirler"""
        if 'sehir-hastane' in page_path:
            return 'Şehir Hastanesi'
        elif 'devlet-hastane' in page_path:
            return 'Devlet Hastanesi'
        elif 'egitim-arastirma' in page_path:
            return 'Eğitim ve Araştırma Hastanesi'
        elif 'dal-hastane' in page_path:
            return 'Dal Hastanesi'
        else:
            return 'Kamu Hastanesi'

    def save_data(self):
        """Çekilen veriyi JSON dosyasına kaydeder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"saglik_bakanligi_{timestamp}.json"
        filepath = self.data_dir / filename
        
        output_data = {
            'kaynak': 'T.C. Sağlık Bakanlığı',
            'tier': 1,
            'cekme_tarihi': datetime.now(timezone.utc).isoformat(),
            'toplam_kayit': sum(len(v) for v in self.results.values()),
            'veriler': self.results,
            'meta': {
                'endpoints': self.endpoints,
                'scraper_version': '2.0',
                'veri_tipi': 'kamu_saglik_kurumlari'
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Veri kaydedildi: {filepath}")
        return filepath

    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.logger.info("Sağlık Bakanlığı veri çekme işlemi başlatılıyor...")
        
        try:
            # KHGM hastaneleri
            hospitals = self.fetch_khgm_hospitals()
            self.results['devlet_hastaneleri'].extend(hospitals)
            
            # İl Sağlık Müdürlükleri
            il_mudurlukleri = self.fetch_il_saglik_mudurlukleri()
            self.results['il_saglik_mudurlukleri'].extend(il_mudurlukleri)
            
            # Her hastane için detaylı bilgi çek (rate limit nedeniyle dikkatli)
            for hospital in hospitals[:10]:  # İlk 10 tanesi için test
                if hospital.get('url'):
                    details = self.fetch_detailed_hospital_info(hospital['url'])
                    hospital.update(details)
            
            # Veriyi kaydet
            self.save_data()
            
            self.logger.info("Sağlık Bakanlığı veri çekme işlemi tamamlandı")
            return True
            
        except Exception as e:
            self.logger.error(f"Veri çekme sırasında hata: {e}")
            return False

def main():
    """Ana fonksiyon"""
    scraper = SaglikBakanligiScraper()
    success = scraper.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
