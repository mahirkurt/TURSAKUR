#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Özel Hastane Zincirleri Veri Çıkarıcısı
===================================================

Tier 2 - Doğrulama ve Zenginleştirme Kaynak
Hedefler:
- Acıbadem Sağlık Grubu
- Medical Park Hastaneler Grubu  
- Memorial Sağlık Grubu
- Medicana Sağlık Grubu
- Dünyagöz Hastaneler Grubu
- Diğer büyük özel hastane zincirleri

Çıkarılan Veriler:
- Hastane isimleri ve lokasyonları
- İletişim bilgileri (telefon, web, email)
- Sunulan özel hizmetler
- Bölüm listeleri
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

class OzelHastaneZincirleriScraper:
    """Özel hastane zincirlerinden veri çıkarır"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TURSAKUR/2.0 (Turkey Health Facilities Database)',
            'Accept': 'application/json, text/html, application/xhtml+xml, */*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })
        
        # Hospital chains configuration
        self.hospital_chains = {
            'acibadem': {
                'name': 'Acıbadem Sağlık Grubu',
                'base_url': 'https://www.acibadem.com.tr',
                'hospitals_page': '/hastaneler/',
                'selectors': {
                    'hospital_list': '.hospital-list, .hastane-liste, [class*="hospital"], [class*="hastane"]',
                    'hospital_item': '.hospital-item, .hastane-item, .hospital-card, .hastane-card',
                    'name': 'h2, h3, .hospital-name, .hastane-adi',
                    'address': '.address, .adres, .location, .lokasyon',
                    'phone': '.phone, .telefon',
                    'link': 'a'
                }
            },
            'medical_park': {
                'name': 'Medical Park Hastaneler Grubu',
                'base_url': 'https://www.medicalpark.com.tr',
                'hospitals_page': '/hastanelerimiz',
                'selectors': {
                    'hospital_list': '.hospitals-list, .hastane-liste',
                    'hospital_item': '.hospital-item, .hastane-item',
                    'name': 'h2, h3, .hospital-name',
                    'address': '.address, .adres',
                    'phone': '.phone, .telefon',
                    'link': 'a'
                }
            },
            'memorial': {
                'name': 'Memorial Sağlık Grubu',
                'base_url': 'https://www.memorial.com.tr',
                'hospitals_page': '/hastaneler',
                'selectors': {
                    'hospital_list': '.hospital-list, .hastane-liste',
                    'hospital_item': '.hospital-item, .hastane-item',
                    'name': 'h2, h3, .hospital-name',
                    'address': '.address, .adres',
                    'phone': '.phone, .telefon',
                    'link': 'a'
                }
            },
            'medicana': {
                'name': 'Medicana Sağlık Grubu',
                'base_url': 'https://www.medicana.com.tr',
                'hospitals_page': '/hastanelerimiz',
                'selectors': {
                    'hospital_list': '.hospitals, .hastaneler',
                    'hospital_item': '.hospital, .hastane',
                    'name': 'h2, h3, .name, .isim',
                    'address': '.address, .adres',
                    'phone': '.phone, .telefon',
                    'link': 'a'
                }
            },
            'dunyagoz': {
                'name': 'Dünyagöz Hastaneler Grubu',
                'base_url': 'https://www.dunyagoz.com',
                'hospitals_page': '/subelerimiz',
                'selectors': {
                    'hospital_list': '.branches, .subeler, .hospitals',
                    'hospital_item': '.branch, .sube, .hospital',
                    'name': 'h2, h3, .branch-name, .sube-adi',
                    'address': '.address, .adres',
                    'phone': '.phone, .telefon',
                    'link': 'a'
                }
            }
        }
        
        # Rate limiting
        self.request_delay = 2.0  # More conservative for private sites
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
        
        self.results = {}

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

    def scrape_hospital_chain(self, chain_id: str, config: Dict) -> List[Dict]:
        """Belirli bir hastane zincirini kazır"""
        self.logger.info(f"Kazınıyor: {config['name']}")
        
        hospitals = []
        
        # Main hospitals page
        hospitals_url = urljoin(config['base_url'], config['hospitals_page'])
        response = self._make_request(hospitals_url)
        
        if not response:
            return hospitals
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors to find hospital lists
        hospital_containers = []
        for selector in config['selectors']['hospital_list'].split(', '):
            containers = soup.select(selector)
            if containers:
                hospital_containers.extend(containers)
        
        # If no specific containers found, look for common patterns
        if not hospital_containers:
            hospital_containers = soup.find_all(['div', 'section', 'ul'], 
                                              class_=lambda x: x and any(keyword in x.lower() 
                                                                       for keyword in ['hospital', 'hastane', 'branch', 'sube']))
        
        for container in hospital_containers:
            # Find individual hospital items
            hospital_items = []
            for selector in config['selectors']['hospital_item'].split(', '):
                items = container.select(selector)
                if items:
                    hospital_items.extend(items)
            
            # If no specific items found, look for links and cards
            if not hospital_items:
                hospital_items = container.find_all(['div', 'li', 'article'], 
                                                  class_=lambda x: x and any(keyword in x.lower() 
                                                                           for keyword in ['item', 'card', 'hospital', 'hastane']))
            
            for item in hospital_items:
                hospital_data = self._extract_hospital_data(item, config, chain_id)
                if hospital_data and hospital_data.get('isim'):
                    hospitals.append(hospital_data)
        
        # Also try to find hospitals from sitemap or other pages
        additional_hospitals = self._find_additional_hospitals(config, chain_id)
        hospitals.extend(additional_hospitals)
        
        self.logger.info(f"{config['name']}'den {len(hospitals)} hastane bulundu")
        return hospitals

    def _extract_hospital_data(self, item, config: Dict, chain_id: str) -> Optional[Dict]:
        """Hastane item'ından veri çıkarır"""
        try:
            # Extract name
            name_element = None
            for selector in config['selectors']['name'].split(', '):
                name_element = item.select_one(selector)
                if name_element:
                    break
            
            if not name_element:
                # Fallback: look for any heading or strong text
                name_element = item.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
            
            if not name_element:
                return None
            
            hospital_name = name_element.get_text(strip=True)
            if not hospital_name or len(hospital_name) < 3:
                return None
            
            # Extract link
            link_element = item.find('a')
            hospital_url = None
            if link_element and link_element.get('href'):
                href = link_element.get('href')
                if href.startswith('http'):
                    hospital_url = href
                else:
                    hospital_url = urljoin(config['base_url'], href)
            
            # Extract address
            address = None
            for selector in config['selectors']['address'].split(', '):
                address_element = item.select_one(selector)
                if address_element:
                    address = address_element.get_text(strip=True)
                    break
            
            # Extract phone
            phone = None
            for selector in config['selectors']['phone'].split(', '):
                phone_element = item.select_one(selector)
                if phone_element:
                    phone = self._clean_phone_number(phone_element.get_text(strip=True))
                    break
            
            # If no structured phone found, search in text
            if not phone:
                item_text = item.get_text()
                phone_match = re.search(r'(\+90[\s\-]?)?(\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})', item_text)
                if phone_match:
                    phone = self._clean_phone_number(phone_match.group(0))
            
            # Build hospital data
            hospital_data = {
                'isim': hospital_name,
                'zincir': config['name'],
                'zincir_id': chain_id,
                'tip': 'Özel Hastane',
                'kaynak': config['name'],
                'kaynak_url': urljoin(config['base_url'], config['hospitals_page']),
                'tarih': datetime.now(timezone.utc).isoformat()
            }
            
            if hospital_url:
                hospital_data['website'] = hospital_url
            if address:
                hospital_data['adres'] = address
            if phone:
                hospital_data['telefon'] = phone
            
            # Get additional details if URL available
            if hospital_url:
                details = self._get_hospital_details(hospital_url)
                hospital_data.update(details)
            
            return hospital_data
            
        except Exception as e:
            self.logger.warning(f"Hastane verisi çıkarılırken hata: {e}")
            return None

    def _get_hospital_details(self, hospital_url: str) -> Dict:
        """Hastane detay sayfasından ek bilgi çeker"""
        details = {}
        
        response = self._make_request(hospital_url)
        if not response:
            return details
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for departments/services
        dept_keywords = ['bölüm', 'department', 'servis', 'service', 'hizmet', 'uzmanlık']
        dept_elements = soup.find_all(['div', 'section', 'ul'], 
                                    class_=lambda x: x and any(keyword in x.lower() for keyword in dept_keywords))
        
        departments = []
        for element in dept_elements:
            dept_items = element.find_all(['li', 'div', 'span'])
            for item in dept_items:
                dept_text = item.get_text(strip=True)
                if dept_text and len(dept_text) > 5 and len(dept_text) < 100:
                    if any(medical_keyword in dept_text.lower() for medical_keyword in 
                          ['kardiyoloji', 'nöroloji', 'onkoloji', 'ortopedi', 'üroloji', 'göz', 'kulak']):
                        departments.append(dept_text)
        
        if departments:
            details['bolumler'] = list(set(departments))
        
        # Look for contact information in structured data
        contact_elements = soup.find_all(['div', 'section'], 
                                       class_=lambda x: x and any(keyword in x.lower() 
                                                                 for keyword in ['contact', 'iletisim', 'adres']))
        
        for element in contact_elements:
            text = element.get_text()
            
            # Email
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            if email_match and not details.get('email'):
                details['email'] = email_match.group(0)
            
            # Additional phone numbers
            phone_matches = re.findall(r'(\+90[\s\-]?)?(\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})', text)
            if phone_matches and not details.get('telefon'):
                details['telefon'] = self._clean_phone_number(phone_matches[0][0] + phone_matches[0][1])
        
        return details

    def _find_additional_hospitals(self, config: Dict, chain_id: str) -> List[Dict]:
        """Sitemap veya diğer sayfalardan ek hastane bulur"""
        additional_hospitals = []
        
        # Try sitemap
        sitemap_urls = [
            urljoin(config['base_url'], '/sitemap.xml'),
            urljoin(config['base_url'], '/sitemap_index.xml'),
            urljoin(config['base_url'], '/robots.txt')
        ]
        
        for sitemap_url in sitemap_urls:
            response = self._make_request(sitemap_url)
            if response:
                # Look for hospital-related URLs
                hospital_urls = re.findall(r'<loc>(.*?hospital.*?)</loc>', response.text, re.IGNORECASE)
                hospital_urls.extend(re.findall(r'<loc>(.*?hastane.*?)</loc>', response.text, re.IGNORECASE))
                
                for url in hospital_urls[:10]:  # Limit to first 10
                    hospital_data = self._scrape_individual_hospital(url, config, chain_id)
                    if hospital_data:
                        additional_hospitals.append(hospital_data)
        
        return additional_hospitals

    def _scrape_individual_hospital(self, url: str, config: Dict, chain_id: str) -> Optional[Dict]:
        """Tekil hastane sayfasını kazır"""
        response = self._make_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract hospital name from title or heading
        title = soup.find('title')
        h1 = soup.find('h1')
        
        hospital_name = None
        if h1:
            hospital_name = h1.get_text(strip=True)
        elif title:
            hospital_name = title.get_text(strip=True)
        
        if not hospital_name:
            return None
        
        return {
            'isim': hospital_name,
            'zincir': config['name'],
            'zincir_id': chain_id,
            'tip': 'Özel Hastane',
            'website': url,
            'kaynak': config['name'],
            'kaynak_url': url,
            'tarih': datetime.now(timezone.utc).isoformat()
        }

    def _clean_phone_number(self, phone: str) -> Optional[str]:
        """Telefon numarasını temizler ve standardize eder"""
        if not phone:
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
        filename = f"ozel_hastane_zincirleri_{timestamp}.json"
        filepath = self.data_dir / filename
        
        total_hospitals = sum(len(hospitals) for hospitals in self.results.values())
        
        output_data = {
            'kaynak': 'Özel Hastane Zincirleri Web Siteleri',
            'tier': 2,
            'cekme_tarihi': datetime.now(timezone.utc).isoformat(),
            'toplam_kayit': total_hospitals,
            'veriler': self.results,
            'meta': {
                'chains_scraped': list(self.results.keys()),
                'scraper_version': '2.0',
                'veri_tipi': 'ozel_hastane_zincirleri'
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Veri kaydedildi: {filepath}")
        return filepath

    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.logger.info("Özel hastane zincirleri veri çekme işlemi başlatılıyor...")
        
        try:
            for chain_id, config in self.hospital_chains.items():
                hospitals = self.scrape_hospital_chain(chain_id, config)
                self.results[chain_id] = hospitals
                
                # Rate limiting between chains
                time.sleep(3)
            
            # Save data
            self.save_data()
            
            total_hospitals = sum(len(hospitals) for hospitals in self.results.values())
            self.logger.info(f"Özel hastane zincirleri veri çekme işlemi tamamlandı. Toplam: {total_hospitals} hastane")
            return True
            
        except Exception as e:
            self.logger.error(f"Özel hastane zincirleri veri çekme sırasında hata: {e}")
            return False

def main():
    """Ana fonksiyon"""
    scraper = OzelHastaneZincirleriScraper()
    success = scraper.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
