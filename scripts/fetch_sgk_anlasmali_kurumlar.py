#!/usr/bin/env python3
"""
TURSAKUR 2.0 - SGK Anlaşmalı Sağlık Hizmeti Sunucuları Çıkarıcısı
==============================================================

Tier 1 - En Yüksek Öncelik Kaynak
Hedef: SGK ile anlaşmalı tüm sağlık hizmeti sunucuları

Çıkarılan Veriler:
- Özel Hastaneler
- Tıp Merkezleri  
- Diyaliz Merkezleri
- Kaplıcalar
- Diğer anlaşmalı kurumlar
"""

import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import re
from urllib.parse import urljoin

# BeautifulSoup for HTML parsing
from bs4 import BeautifulSoup

# Selenium for form submissions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SGKScraper:
    """SGK Anlaşmalı Sağlık Hizmeti Sunucuları çıkarır"""
    
    def __init__(self):
        self.base_url = "https://gss.sgk.gov.tr"
        self.search_url = f"{self.base_url}/SaglikHizmetSunuculari/pages/shsAnlasmaliKurumSorgu.faces"
        
        # Chrome options for Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--user-agent=TURSAKUR/2.0 (Turkey Health Facilities Database)')
        
        # Data storage
        self.data_dir = Path(__file__).parent.parent / "data" / "raw"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Turkish provinces
        self.provinces = [
            "ADANA", "ADIYAMAN", "AFYONKARAHİSAR", "AĞRI", "AKSARAY", "AMASYA", 
            "ANKARA", "ANTALYA", "ARDAHAN", "ARTVİN", "AYDIN", "BALIKESİR", 
            "BARTIN", "BATMAN", "BAYBURT", "BİLECİK", "BİNGÖL", "BİTLİS", 
            "BOLU", "BURDUR", "BURSA", "ÇANAKKALE", "ÇANKIRI", "ÇORUM", 
            "DENİZLİ", "DİYARBAKIR", "DÜZCE", "EDİRNE", "ELAZIĞ", "ERZİNCAN", 
            "ERZURUM", "ESKİŞEHİR", "GAZİANTEP", "GİRESUN", "GÜMÜŞHANE", 
            "HAKKARİ", "HATAY", "IĞDIR", "ISPARTA", "İSTANBUL", "İZMİR", 
            "KAHRAMANMARAŞ", "KARABÜK", "KARAMAN", "KARS", "KASTAMONU", "KAYSERİ", 
            "KIRIKKALE", "KIRKLARELİ", "KIRŞEHİR", "KOCAELİ", "KONYA", "KÜTAHYA", 
            "MALATYA", "MANİSA", "MARDİN", "MERSİN", "MUĞLA", "MUŞ", 
            "NEVŞEHİR", "NİĞDE", "ORDU", "OSMANİYE", "RİZE", "SAKARYA", 
            "SAMSUN", "SİİRT", "SİNOP", "SİVAS", "ŞANLIURFA", "ŞIRNAK", 
            "TEKİRDAĞ", "TOKAT", "TRABZON", "TUNCELİ", "UŞAK", "VAN", 
            "YALOVA", "YOZGAT", "ZONGULDAK"
        ]
        
        # Institution types to search for
        self.institution_types = [
            "Hastane",
            "Tıp Merkezi", 
            "Diyaliz Merkezi",
            "Fizik Tedavi ve Rehabilitasyon Merkezi",
            "Görüntüleme Merkezi",
            "Laboratuvar",
            "Eczane",
            "Optisyen",
            "İşitme Cihazı",
            "Ortez Protez",
            "Ağız ve Diş Sağlığı Merkezi"
        ]
        
        self.results = []

    def setup_driver(self) -> webdriver.Chrome:
        """Chrome WebDriver'ı başlatır"""
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            return driver
        except Exception as e:
            self.logger.error(f"WebDriver başlatılamadı: {e}")
            raise

    def wait_for_page_load(self, driver: webdriver.Chrome, timeout: int = 30):
        """Sayfanın yüklenmesini bekler"""
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # Additional wait for dynamic content
        except TimeoutException:
            self.logger.warning("Sayfa yükleme timeout")

    def search_institutions(self, driver: webdriver.Chrome, province: str, institution_type: str) -> List[Dict]:
        """Belirli il ve kurum tipi için arama yapar"""
        self.logger.info(f"Arama yapılıyor: {province} - {institution_type}")
        
        try:
            # Navigate to search page
            driver.get(self.search_url)
            self.wait_for_page_load(driver)
            
            # Select province
            try:
                province_select = Select(driver.find_element(By.ID, "form1:il"))
                province_select.select_by_visible_text(province)
                time.sleep(1)  # Wait for districts to load
            except NoSuchElementException:
                self.logger.warning(f"İl seçimi bulunamadı: {province}")
                return []
            
            # Select institution type if available
            try:
                type_select = Select(driver.find_element(By.ID, "form1:kurumTuru"))
                type_select.select_by_visible_text(institution_type)
                time.sleep(1)
            except NoSuchElementException:
                self.logger.warning(f"Kurum türü seçimi bulunamadı: {institution_type}")
            
            # Submit search
            try:
                search_button = driver.find_element(By.ID, "form1:btnSorgula")
                search_button.click()
                self.wait_for_page_load(driver)
            except NoSuchElementException:
                self.logger.warning("Arama butonu bulunamadı")
                return []
            
            # Parse results
            return self.parse_search_results(driver, province, institution_type)
            
        except Exception as e:
            self.logger.error(f"Arama hatası ({province} - {institution_type}): {e}")
            return []

    def parse_search_results(self, driver: webdriver.Chrome, province: str, institution_type: str) -> List[Dict]:
        """Arama sonuçlarını parse eder"""
        institutions = []
        
        try:
            # Look for results table
            results_table = driver.find_element(By.CSS_SELECTOR, "table[class*='sonuc'], table[class*='result']")
            rows = results_table.find_elements(By.TAG_NAME, "tr")
            
            # Skip header row
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 4:  # Minimum expected columns
                    institution_data = {
                        'isim': cells[0].text.strip() if len(cells) > 0 else "",
                        'adres': cells[1].text.strip() if len(cells) > 1 else "",
                        'telefon': cells[2].text.strip() if len(cells) > 2 else "",
                        'tip': institution_type,
                        'il': province,
                        'sgk_kodu': cells[3].text.strip() if len(cells) > 3 else "",
                        'sgk_anlasmasi': True,
                        'kaynak': 'SGK',
                        'kaynak_url': self.search_url,
                        'tarih': datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Clean and validate data
                    if institution_data['isim'] and institution_data['isim'] != '-':
                        institutions.append(institution_data)
            
        except NoSuchElementException:
            self.logger.info(f"Sonuç bulunamadı: {province} - {institution_type}")
        except Exception as e:
            self.logger.error(f"Sonuç parse hatası: {e}")
        
        self.logger.info(f"Bulunan kurum sayısı: {len(institutions)}")
        return institutions

    def clean_phone_number(self, phone: str) -> Optional[str]:
        """Telefon numarasını temizler ve standardize eder"""
        if not phone or phone == '-':
            return None
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Add +90 prefix if missing
        if cleaned.startswith('0'):
            cleaned = '+90' + cleaned[1:]
        elif not cleaned.startswith('+90') and len(cleaned) == 10:
            cleaned = '+90' + cleaned
        
        return cleaned if len(cleaned) >= 13 else None

    def save_data(self):
        """Çekilen veriyi JSON dosyasına kaydeder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"sgk_anlasmali_kurumlar_{timestamp}.json"
        filepath = self.data_dir / filename
        
        # Clean phone numbers
        for institution in self.results:
            if institution.get('telefon'):
                institution['telefon'] = self.clean_phone_number(institution['telefon'])
        
        output_data = {
            'kaynak': 'SGK Anlaşmalı Sağlık Hizmeti Sunucuları',
            'tier': 1,
            'cekme_tarihi': datetime.now(timezone.utc).isoformat(),
            'toplam_kayit': len(self.results),
            'veriler': self.results,
            'meta': {
                'search_url': self.search_url,
                'searched_provinces': len(self.provinces),
                'searched_types': len(self.institution_types),
                'scraper_version': '2.0',
                'veri_tipi': 'sgk_anlasmali_kurumlar'
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Veri kaydedildi: {filepath}")
        return filepath

    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.logger.info("SGK Anlaşmalı Kurumlar veri çekme işlemi başlatılıyor...")
        
        driver = None
        try:
            driver = self.setup_driver()
            
            # Search for each province and institution type combination
            total_searches = len(self.provinces) * len(self.institution_types)
            current_search = 0
            
            for province in self.provinces:
                for institution_type in self.institution_types:
                    current_search += 1
                    self.logger.info(f"İlerleme: {current_search}/{total_searches}")
                    
                    institutions = self.search_institutions(driver, province, institution_type)
                    self.results.extend(institutions)
                    
                    # Rate limiting - wait between searches
                    time.sleep(2)
            
            # Remove duplicates based on SGK code and name
            self.remove_duplicates()
            
            # Save data
            self.save_data()
            
            self.logger.info(f"SGK veri çekme işlemi tamamlandı. Toplam: {len(self.results)} kurum")
            return True
            
        except Exception as e:
            self.logger.error(f"SGK veri çekme sırasında hata: {e}")
            return False
        finally:
            if driver:
                driver.quit()

    def remove_duplicates(self):
        """Çift kayıtları kaldırır"""
        seen = set()
        unique_results = []
        
        for institution in self.results:
            # Create a unique key based on name and SGK code
            key = (institution.get('isim', '').strip().upper(), 
                  institution.get('sgk_kodu', '').strip())
            
            if key not in seen and institution.get('isim'):
                seen.add(key)
                unique_results.append(institution)
        
        removed_count = len(self.results) - len(unique_results)
        self.results = unique_results
        
        if removed_count > 0:
            self.logger.info(f"{removed_count} çift kayıt kaldırıldı")

def main():
    """Ana fonksiyon"""
    scraper = SGKScraper()
    success = scraper.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
