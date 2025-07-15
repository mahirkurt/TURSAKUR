#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İl Sağlık Müdürlükleri Web Sitelerinden Sağlık Kurumları Verilerini Çekme Modülü

Bu modül, Türkiye'deki 81 il sağlık müdürlüğünün resmi web sitelerinden
sağlık kurumlarına ait verileri otomatik olarak çeker ve işler.

Author: TURSAKUR Team
Version: 1.0.0
Date: 2025-01-14
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
import time
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/il_saglik_mudurlukeri.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class HealthInstitution:
    """Sağlık kurumu veri yapısı"""
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
    web_sitesi: Optional[str]
    veri_kaynagi: str
    son_guncelleme: str

class HealthDepartmentScraper:
    """İl Sağlık Müdürlükleri Web Scraper Sınıfı"""
    
    def __init__(self):
        self.session = self._create_session()
        self.il_kodlari = self._load_il_kodlari()
        self.collected_data = []
        
    def _create_session(self) -> requests.Session:
        """Güvenli HTTP session oluştur"""
        session = requests.Session()
        
        # Retry stratejisi
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _load_il_kodlari(self) -> Dict[str, int]:
        """İl kodları haritasını yükle"""
        return {
            'Adana': 1, 'Adıyaman': 2, 'Afyonkarahisar': 3, 'Ağrı': 4, 'Amasya': 5,
            'Ankara': 6, 'Antalya': 7, 'Artvin': 8, 'Aydın': 9, 'Balıkesir': 10,
            'Bilecik': 11, 'Bingöl': 12, 'Bitlis': 13, 'Bolu': 14, 'Burdur': 15,
            'Bursa': 16, 'Çanakkale': 17, 'Çankırı': 18, 'Çorum': 19, 'Denizli': 20,
            'Diyarbakır': 21, 'Edirne': 22, 'Elazığ': 23, 'Erzincan': 24, 'Erzurum': 25,
            'Eskişehir': 26, 'Gaziantep': 27, 'Giresun': 28, 'Gümüşhane': 29, 'Hakkari': 30,
            'Hatay': 31, 'Isparta': 32, 'Mersin': 33, 'İstanbul': 34, 'İzmir': 35,
            'Kars': 36, 'Kastamonu': 37, 'Kayseri': 38, 'Kırklareli': 39, 'Kırşehir': 40,
            'Kocaeli': 41, 'Konya': 42, 'Kütahya': 43, 'Malatya': 44, 'Manisa': 45,
            'Kahramanmaraş': 46, 'Mardin': 47, 'Muğla': 48, 'Muş': 49, 'Nevşehir': 50,
            'Niğde': 51, 'Ordu': 52, 'Rize': 53, 'Sakarya': 54, 'Samsun': 55,
            'Siirt': 56, 'Sinop': 57, 'Sivas': 58, 'Tekirdağ': 59, 'Tokat': 60,
            'Trabzon': 61, 'Tunceli': 62, 'Şanlıurfa': 63, 'Uşak': 64, 'Van': 65,
            'Yozgat': 66, 'Zonguldak': 67, 'Aksaray': 68, 'Bayburt': 69, 'Karaman': 70,
            'Kırıkkale': 71, 'Batman': 72, 'Şırnak': 73, 'Bartın': 74, 'Ardahan': 75,
            'Iğdır': 76, 'Yalova': 77, 'Karabük': 78, 'Kilis': 79, 'Osmaniye': 80,
            'Düzce': 81
        }
    
    def _generate_kurum_id(self, kurum_adi: str, il_kodu: int, kurum_tipi: str) -> str:
        """Kurum ID oluştur"""
        # Kurum tipine göre kod
        tip_kodlari = {
            'Devlet Hastanesi': 'DH',
            'Üniversite Hastanesi': 'UH',
            'Eğitim ve Araştırma Hastanesi': 'EAH',
            'Aile Sağlığı Merkezi': 'ASM',
            'Toplum Sağlığı Merkezi': 'TSM',
            'Ağız ve Diş Sağlığı Merkezi': 'ADSM',
            'İlçe Devlet Hastanesi': 'IDH',
            'Fizik Tedavi Hastanesi': 'FTH',
            'Doğum ve Çocuk Hastanesi': 'DCH',
            'Ruh Sağlığı Hastanesi': 'RSH',
            'Göğüs Hastalıkları Hastanesi': 'GHH',
            'Kardiyoloji Hastanesi': 'KH',
            'Onkoloji Hastanesi': 'OH',
            'Diğer': 'DG'
        }
        
        tip_kodu = tip_kodlari.get(kurum_tipi, 'DG')
        
        # Hash oluştur
        hash_input = f"{kurum_adi}{il_kodu}{kurum_tipi}".encode('utf-8')
        hash_suffix = hashlib.md5(hash_input).hexdigest()[:4].upper()
        
        return f"TR-{il_kodu:02d}-{tip_kodu}-{hash_suffix}"
    
    def _clean_text(self, text: str) -> str:
        """Metni temizle"""
        if not text:
            return ""
        
        # HTML etiketlerini kaldır
        text = re.sub(r'<[^>]+>', '', text)
        
        # Fazla boşlukları kaldır
        text = re.sub(r'\s+', ' ', text)
        
        # Özel karakterleri düzelt
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        
        return text.strip()
    
    def _extract_phone(self, text: str) -> str:
        """Telefon numarasını çıkar ve formatla"""
        if not text:
            return ""
        
        # Telefon numarası pattern'leri
        phone_patterns = [
            r'(\+90\s?)?(\d{3})\s?(\d{3})\s?(\d{2})\s?(\d{2})',
            r'(\d{4})\s?(\d{3})\s?(\d{2})\s?(\d{2})',
            r'(\d{3})\s?(\d{3})\s?(\d{4})'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                numbers = ''.join(filter(str.isdigit, match.group()))
                if len(numbers) == 10:
                    return f"+90{numbers}"
                elif len(numbers) == 11 and numbers.startswith('0'):
                    return f"+90{numbers[1:]}"
        
        return ""
    
    def _categorize_institution_type(self, name: str, content: str = "") -> str:
        """Kurum tipini belirle"""
        name_lower = name.lower()
        content_lower = content.lower()
        
        combined_text = f"{name_lower} {content_lower}"
        
        if any(keyword in combined_text for keyword in ['üniversite', 'tıp fakültesi', 'med fak']):
            return 'Üniversite Hastanesi'
        elif any(keyword in combined_text for keyword in ['eğitim', 'araştırma', 'eah']):
            return 'Eğitim ve Araştırma Hastanesi'
        elif any(keyword in combined_text for keyword in ['aile sağlığı', 'asm', 'aile hekimliği']):
            return 'Aile Sağlığı Merkezi'
        elif any(keyword in combined_text for keyword in ['toplum sağlığı', 'tsm', 'halk sağlığı']):
            return 'Toplum Sağlığı Merkezi'
        elif any(keyword in combined_text for keyword in ['ağız', 'diş', 'adsm', 'oral']):
            return 'Ağız ve Diş Sağlığı Merkezi'
        elif any(keyword in combined_text for keyword in ['fizik tedavi', 'ftr', 'rehabilitasyon']):
            return 'Fizik Tedavi Hastanesi'
        elif any(keyword in combined_text for keyword in ['doğum', 'çocuk', 'kadın', 'jinekolog']):
            return 'Doğum ve Çocuk Hastanesi'
        elif any(keyword in combined_text for keyword in ['ruh sağlığı', 'psikiyatri', 'akıl']):
            return 'Ruh Sağlığı Hastanesi'
        elif any(keyword in combined_text for keyword in ['göğüs', 'verem', 'tüberküloz']):
            return 'Göğüs Hastalıkları Hastanesi'
        elif any(keyword in combined_text for keyword in ['kalp', 'kardiyoloji', 'damar']):
            return 'Kardiyoloji Hastanesi'
        elif any(keyword in combined_text for keyword in ['onkoloji', 'kanser', 'tümör']):
            return 'Onkoloji Hastanesi'
        elif any(keyword in combined_text for keyword in ['ilçe', 'district']):
            return 'İlçe Devlet Hastanesi'
        elif any(keyword in combined_text for keyword in ['hastane', 'hospital']):
            return 'Devlet Hastanesi'
        else:
            return 'Diğer'
    
    def _scrape_health_institutions_from_page(self, url: str, il_adi: str) -> List[HealthInstitution]:
        """Belirli bir sayfadan sağlık kurumlarını çek"""
        try:
            logger.info(f"{il_adi} için veri çekiliyor: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            institutions = []
            
            # Farklı sayfa yapıları için multiple selector strategy
            selectors = [
                # Genel hastane listesi
                'div.hastane-listesi li',
                'ul.hastane-listesi li',
                '.hastane-item',
                '.kurum-item',
                
                # Menü yapısı
                'nav a[href*="hastane"]',
                'nav a[href*="saglik"]',
                'menu a[href*="hastane"]',
                
                # İçerik alanları
                '.content a[href*="hastane"]',
                '.main-content a[href*="saglik"]',
                'article a[href*="hastane"]',
                
                # Liste yapıları
                'ul li a[href*="hastane"]',
                'ol li a[href*="saglik"]',
                
                # Genel link arama
                'a[href*="hastane"]',
                'a[href*="saglik"]'
            ]
            
            found_institutions = set()
            
            for selector in selectors:
                elements = soup.select(selector)
                
                for element in elements:
                    try:
                        # Link metni ve href'i al
                        if element.name == 'a':
                            text = self._clean_text(element.get_text())
                            href = element.get('href', '') or ''
                        else:
                            link = element.find('a')
                            if link:
                                text = self._clean_text(link.get_text())
                                href = link.get('href', '') or ''
                            else:
                                text = self._clean_text(element.get_text())
                                href = ''
                        
                        # Kurumu filtrele
                        if self._is_health_institution(text):
                            # Detay sayfasını çek
                            if href and isinstance(href, str):
                                detail_url = urljoin(url, href)
                            else:
                                detail_url = url
                            institution_data = self._extract_institution_details(
                                detail_url, text, il_adi
                            )
                            
                            if institution_data and institution_data.kurum_adi not in found_institutions:
                                institutions.append(institution_data)
                                found_institutions.add(institution_data.kurum_adi)
                                logger.info(f"Kurum bulundu: {institution_data.kurum_adi}")
                    
                    except Exception as e:
                        logger.warning(f"Element işlenirken hata: {e}")
                        continue
            
            # Ana sayfa içeriğinden de metin analizi yap
            main_content = soup.find('main') or soup.find('div', class_='content') or soup.body
            if main_content:
                text_content = self._clean_text(main_content.get_text())
                institutions.extend(self._extract_institutions_from_text(text_content, il_adi, url))
            
            logger.info(f"{il_adi} için {len(institutions)} kurum bulundu")
            return institutions
            
        except Exception as e:
            logger.error(f"{il_adi} ({url}) için veri çekilemedi: {e}")
            return []
    
    def _is_health_institution(self, text: str) -> bool:
        """Metnin sağlık kurumu olup olmadığını kontrol et"""
        if not text or len(text) < 5:
            return False
        
        text_lower = text.lower()
        
        # Pozitif keywords
        positive_keywords = [
            'hastane', 'hospital', 'sağlık', 'health', 'merkez', 'center',
            'poliklinik', 'klinik', 'clinic', 'dispanser', 'hekim', 'doktor',
            'tıp', 'medical', 'asm', 'tsm', 'adsm', 'ftr'
        ]
        
        # Negatif keywords
        negative_keywords = [
            'haber', 'duyuru', 'açıklama', 'basın', 'medya', 'etkinlik',
            'toplantı', 'seminer', 'kurs', 'eğitim', 'yarışma', 'müze',
            'anı', 'galeri', 'fotoğraf', 'video'
        ]
        
        # Pozitif keyword var mı?
        has_positive = any(keyword in text_lower for keyword in positive_keywords)
        
        # Negatif keyword var mı?
        has_negative = any(keyword in text_lower for keyword in negative_keywords)
        
        return has_positive and not has_negative
    
    def _extract_institution_details(self, url: str, name: str, il_adi: str) -> Optional[HealthInstitution]:
        """Kurum detaylarını çıkar"""
        try:
            soup = None
            content = ""
            
            if url.startswith('http'):
                response = self.session.get(url, timeout=20)
                soup = BeautifulSoup(response.content, 'html.parser')
                content = self._clean_text(soup.get_text())
            
            # Kurum bilgilerini çıkar
            kurum_adi = self._clean_text(name)
            kurum_tipi = self._categorize_institution_type(kurum_adi, content)
            il_kodu = self.il_kodlari.get(il_adi, 0)
            
            # Adres çıkarma
            adres = self._extract_address(content, soup)
            
            # Telefon çıkarma
            telefon = self._extract_phone(content)
            
            # İlçe belirleme
            ilce_adi = self._extract_district(adres, content)
            
            # Kurum ID oluştur
            kurum_id = self._generate_kurum_id(kurum_adi, il_kodu, kurum_tipi)
            
            return HealthInstitution(
                kurum_id=kurum_id,
                kurum_adi=kurum_adi,
                kurum_tipi=kurum_tipi,
                il_kodu=il_kodu,
                il_adi=il_adi,
                ilce_adi=ilce_adi,
                adres=adres,
                telefon=telefon,
                koordinat_lat=None,  # Geocoding sonrası eklenecek
                koordinat_lon=None,
                web_sitesi=url if url.startswith('http') else None,
                veri_kaynagi=f"İl Sağlık Müdürlüğü - {il_adi}",
                son_guncelleme=datetime.now().strftime('%Y-%m-%d')
            )
            
        except Exception as e:
            logger.warning(f"Kurum detayları çıkarılamadı ({name}): {e}")
            return None
    
    def _extract_address(self, content: str, soup: Optional[BeautifulSoup] = None) -> str:
        """Adres bilgisini çıkar"""
        if not content:
            return ""
        
        # Adres pattern'leri
        address_patterns = [
            r'Adres[:\s]+([^\n]+)',
            r'Address[:\s]+([^\n]+)',
            r'Bulvar[^\n]*',
            r'Caddesi[^\n]*',
            r'Sokak[^\n]*',
            r'Mahallesi[^\n]*'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1) if match.groups() else match.group())
        
        return ""
    
    def _extract_district(self, adres: str, content: str) -> str:
        """İlçe bilgisini çıkar"""
        # Adres ve içerikten ilçe adı çıkarmaya çalış
        if adres:
            # Adres içinde ilçe pattern'i ara
            ilce_match = re.search(r'(\w+)\s+(İlçesi|Merkez)', adres, re.IGNORECASE)
            if ilce_match:
                return ilce_match.group(1)
        
        return "Merkez"  # Default olarak Merkez
    
    def _extract_institutions_from_text(self, text: str, il_adi: str, base_url: str) -> List[HealthInstitution]:
        """Metin içinden kurumları çıkar"""
        institutions = []
        
        # Kurum ismi pattern'leri
        patterns = [
            r'(\w+\s+(?:Devlet\s+)?Hastanesi)',
            r'(\w+\s+Üniversitesi\s+Hastanesi)',
            r'(\w+\s+Aile\s+Sağlığı\s+Merkezi)',
            r'(\w+\s+Toplum\s+Sağlığı\s+Merkezi)',
        ]
        
        found_names = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                kurum_adi = self._clean_text(match)
                if kurum_adi and kurum_adi not in found_names:
                    institution = self._extract_institution_details(base_url, kurum_adi, il_adi)
                    if institution:
                        institutions.append(institution)
                        found_names.add(kurum_adi)
        
        return institutions
    
    def scrape_all_provinces(self) -> List[HealthInstitution]:
        """Tüm illerin verilerini çek"""
        
        # İl sağlık müdürlükleri URL'leri
        province_urls = {
            'Adana': 'https://adanaism.saglik.gov.tr/',
            'Adıyaman': 'https://adiyamanism.saglik.gov.tr/',
            'Afyonkarahisar': 'https://afyonkarahisarism.saglik.gov.tr/',
            'Ağrı': 'https://agriism.saglik.gov.tr/',
            'Aksaray': 'https://aksarayism.saglik.gov.tr/',
            'Amasya': 'https://amasyaism.saglik.gov.tr/',
            'Ankara': 'https://ankaraism.saglik.gov.tr/',
            'Antalya': 'https://antalyaism.saglik.gov.tr/',
            'Ardahan': 'https://ardahanism.saglik.gov.tr/',
            'Artvin': 'https://artvinism.saglik.gov.tr/',
            'Aydın': 'https://aydinism.saglik.gov.tr/',
            'Balıkesir': 'https://balikesirism.saglik.gov.tr/',
            'Bartın': 'https://bartinism.saglik.gov.tr/',
            'Batman': 'https://batmanism.saglik.gov.tr/',
            'Bayburt': 'https://bayburtism.saglik.gov.tr/',
            'Bilecik': 'https://bilecikism.saglik.gov.tr/',
            'Bingöl': 'https://bingolism.saglik.gov.tr/',
            'Bitlis': 'https://bitlisism.saglik.gov.tr/',
            'Bolu': 'https://boluism.saglik.gov.tr/',
            'Burdur': 'https://burdurism.saglik.gov.tr/',
            'Bursa': 'https://bursaism.saglik.gov.tr/',
            'Çanakkale': 'https://canakkaleism.saglik.gov.tr/',
            'Çankırı': 'https://cankiriism.saglik.gov.tr/',
            'Çorum': 'https://corumism.saglik.gov.tr/',
            'Denizli': 'https://denizliism.saglik.gov.tr/',
            'Diyarbakır': 'https://diyarbakirism.saglik.gov.tr/',
            'Düzce': 'https://duzceism.saglik.gov.tr/',
            'Edirne': 'https://edirneism.saglik.gov.tr/',
            'Elazığ': 'https://elazigism.saglik.gov.tr/',
            'Erzincan': 'https://erzincanism.saglik.gov.tr/',
            'Erzurum': 'https://erzurumism.saglik.gov.tr/',
            'Eskişehir': 'https://eskisehirism.saglik.gov.tr/',
            'Gaziantep': 'https://gaziantepism.saglik.gov.tr/',
            'Giresun': 'https://giresunism.saglik.gov.tr/',
            'Gümüşhane': 'https://gumushaneism.saglik.gov.tr/',
            'Hakkari': 'https://hakkariism.saglik.gov.tr/',
            'Hatay': 'https://hatayism.saglik.gov.tr/',
            'Iğdır': 'https://igdirism.saglik.gov.tr/',
            'Isparta': 'https://ispartaism.saglik.gov.tr/',
            'İstanbul': 'https://istanbulism.saglik.gov.tr/',
            'İzmir': 'https://izmirism.saglik.gov.tr/',
            'Kahramanmaraş': 'https://kahramanmarasism.saglik.gov.tr/',
            'Karabük': 'https://karabukism.saglik.gov.tr/',
            'Karaman': 'https://karamanism.saglik.gov.tr/',
            'Kars': 'https://karsism.saglik.gov.tr/',
            'Kastamonu': 'https://kastamonuism.saglik.gov.tr/',
            'Kayseri': 'https://kayseriism.saglik.gov.tr/',
            'Kırıkkale': 'https://kirikkaleism.saglik.gov.tr/',
            'Kırklareli': 'https://kirklareliism.saglik.gov.tr/',
            'Kırşehir': 'https://kirsehirism.saglik.gov.tr/',
            'Kilis': 'https://kilisism.saglik.gov.tr/',
            'Kocaeli': 'https://kocaeliism.saglik.gov.tr/',
            'Konya': 'https://konyaism.saglik.gov.tr/',
            'Kütahya': 'https://kutahyaism.saglik.gov.tr/',
            'Malatya': 'https://malatyaism.saglik.gov.tr/',
            'Manisa': 'https://manisaism.saglik.gov.tr/',
            'Mardin': 'https://mardinism.saglik.gov.tr/',
            'Mersin': 'https://mersinism.saglik.gov.tr/',
            'Muğla': 'https://muglaism.saglik.gov.tr/',
            'Muş': 'https://musism.saglik.gov.tr/',
            'Nevşehir': 'https://nevsehirism.saglik.gov.tr/',
            'Niğde': 'https://nigdeism.saglik.gov.tr/',
            'Ordu': 'https://orduism.saglik.gov.tr/',
            'Osmaniye': 'https://osmaniyeism.saglik.gov.tr/',
            'Rize': 'https://rizeism.saglik.gov.tr/',
            'Sakarya': 'https://sakaryaism.saglik.gov.tr/',
            'Samsun': 'https://samsunism.saglik.gov.tr/',
            'Siirt': 'https://siirtism.saglik.gov.tr/',
            'Sinop': 'https://sinopism.saglik.gov.tr/',
            'Sivas': 'https://sivasism.saglik.gov.tr/',
            'Şanlıurfa': 'https://sanliurfaism.saglik.gov.tr/',
            'Şırnak': 'https://sirnakism.saglik.gov.tr/',
            'Tekirdağ': 'https://tekirdagism.saglik.gov.tr/',
            'Tokat': 'https://tokatism.saglik.gov.tr/',
            'Trabzon': 'https://trabzonism.saglik.gov.tr/',
            'Tunceli': 'https://tunceliism.saglik.gov.tr/',
            'Uşak': 'https://usakism.saglik.gov.tr/',
            'Van': 'https://vanism.saglik.gov.tr/',
            'Yalova': 'https://yalovaism.saglik.gov.tr/',
            'Yozgat': 'https://yozgatism.saglik.gov.tr/',
            'Zonguldak': 'https://zonguldakism.saglik.gov.tr/'
        }
        
        all_institutions = []
        
        # Paralel işleme ile performans artışı
        def scrape_province(item):
            il_adi, url = item
            try:
                time.sleep(1)  # Rate limiting
                return self._scrape_health_institutions_from_page(url, il_adi)
            except Exception as e:
                logger.error(f"{il_adi} için scraping hatası: {e}")
                return []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_province = {
                executor.submit(scrape_province, item): item[0] 
                for item in province_urls.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_province):
                province_name = future_to_province[future]
                try:
                    institutions = future.result()
                    all_institutions.extend(institutions)
                    logger.info(f"{province_name} tamamlandı: {len(institutions)} kurum")
                except Exception as e:
                    logger.error(f"{province_name} için hata: {e}")
        
        return all_institutions
    
    def save_to_json(self, institutions: List[HealthInstitution], filename: str):
        """Verileri JSON dosyasına kaydet"""
        try:
            # HealthInstitution objelerini dict'e çevir
            data = [asdict(institution) for institution in institutions]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"{len(institutions)} kurum {filename} dosyasına kaydedildi")
            
        except Exception as e:
            logger.error(f"JSON kaydetme hatası: {e}")

def main():
    """Ana fonksiyon"""
    try:
        # Log dizinini oluştur
        import os
        os.makedirs('logs', exist_ok=True)
        
        logger.info("İl Sağlık Müdürlükleri veri çekme işlemi başlatılıyor...")
        
        scraper = HealthDepartmentScraper()
        institutions = scraper.scrape_all_provinces()
        
        # Verileri kaydet
        output_file = 'data/raw/il_saglik_mudurlukeri.json'
        scraper.save_to_json(institutions, output_file)
        
        logger.info(f"Toplam {len(institutions)} kurum başarıyla çekildi ve kaydedildi")
        
        # Özet bilgi
        print("\n=== İL SAĞLIK MÜDÜRLÜKLERİ VERİ ÇEKME ÖZETİ ===")
        print(f"Toplam kurum sayısı: {len(institutions)}")
        
        # İl bazında dağılım
        il_dagilim = {}
        for inst in institutions:
            il_dagilim[inst.il_adi] = il_dagilim.get(inst.il_adi, 0) + 1
        
        print("\nİl bazında dağılım:")
        for il, count in sorted(il_dagilim.items()):
            print(f"  {il}: {count} kurum")
        
        # Kurum tipi dağılımı
        tip_dagilim = {}
        for inst in institutions:
            tip_dagilim[inst.kurum_tipi] = tip_dagilim.get(inst.kurum_tipi, 0) + 1
        
        print("\nKurum tipi dağılımı:")
        for tip, count in sorted(tip_dagilim.items()):
            print(f"  {tip}: {count} kurum")
        
    except Exception as e:
        logger.error(f"Ana fonksiyon hatası: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
