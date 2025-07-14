#!/usr/bin/env python3
"""
SGK SHS ve Sigorta Şirketleri Yeni Veri Kaynakları Keşif Scripti
==============================================================

Yeni keşfedilen SGK ve sigorta şirketi veri kaynakları:
1. E-Devlet SGK borç sorgulama sistemleri
2. Sigorta şirketlerinin anlaşmalı sağlık kuruluşları listeleri
3. Hekim mesleki sorumluluk sigortası veritabanları
4. Özel sigorta şirketlerinin panel sistemleri
5. MHRS sistemine entegre sağlık kuruluşları
"""

import requests
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SGKSigortaYeniKaynaklar:
    """SGK ve sigorta şirketleri için yeni veri kaynaklarını çeken sınıf."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Büyük sigorta şirketleri ve anlaşmalı kuruluş listeleri
        self.sigorta_sirketleri = {
            'aksigorta': {
                'base_url': 'https://www.aksigorta.com.tr',
                'anlasmalı_url': '/saglik/anlasmalı-saglik-kuruluslari',
                'name': 'Ak Sigorta'
            },
            'allianz': {
                'base_url': 'https://www.allianz.com.tr',
                'anlasmalı_url': '/tr_TR/bireysel/saglik-sigortasi/anlasmalı-kurumlar.html',
                'name': 'Allianz Sigorta'
            },
            'sompo': {
                'base_url': 'https://www.somposigorta.com.tr',
                'anlasmalı_url': '/anlasmalı-saglik-kuruluslari',
                'name': 'Sompo Sigorta'
            },
            'anadolu': {
                'base_url': 'https://www.anadolusigorta.com.tr',
                'anlasmalı_url': '/saglik-sigortasi/anlasmalı-saglik-kuruluslari',
                'name': 'Anadolu Sigorta'
            },
            'mapfre': {
                'base_url': 'https://www.mapfreassist.com.tr',
                'anlasmalı_url': '/saglik-kuruluslari',
                'name': 'Mapfre Sigorta'
            },
            'gunes': {
                'base_url': 'https://www.gunessigortasi.com.tr',
                'anlasmalı_url': '/saglik/anlasmalı-hastaneler',
                'name': 'Güneş Sigorta'
            },
            'euroins': {
                'base_url': 'https://www.euroins.com.tr',
                'anlasmalı_url': '/saglik-sigortasi/anlasmalı-kurumlar',
                'name': 'Euroins Sigorta'
            }
        }
        
        # Alternatif SGK veri kaynakları
        self.sgk_alternatif_kaynaklar = {
            'e_devlet_sms': 'https://www.turkiye.gov.tr/sgk-borcu-sorgulama',
            'mhrs_entegrasyon': 'https://www.mhrs.gov.tr',
            'tip_merkezi_birlikleri': [
                'https://www.tobb.org.tr',  # TOBB sağlık sektörü
                'https://www.iso.org.tr',   # İSO sağlık komisyonu
            ]
        }
        
        # Sağlık birlik ve dernekleri
        self.saglik_birlikleri = {
            'ttb': 'https://www.ttb.org.tr',  # Türk Tabipler Birliği
            'sted': 'https://www.sted.org.tr',  # Sağlık Turizmini Geliştirme Derneği
            'tusev': 'https://www.tusev.org.tr',  # Türkiye Üçüncü Sektör Vakfı
            'ohsad': 'http://www.ohsad.org',  # Özel Hastaneler ve Sağlık Kuruluşları Derneği
        }
        
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_sigorta_anlasmalı_kurumlar(self, sigorta_key: str, sigorta_info: Dict) -> List[Dict]:
        """Bir sigorta şirketinin anlaşmalı sağlık kuruluşlarını çek"""
        institutions = []
        
        try:
            company_name = sigorta_info['name']
            logger.info(f"Sigorta şirketi taranıyor: {company_name}")
            
            # Farklı URL kombinasyonlarını dene
            possible_urls = [
                sigorta_info['base_url'] + sigorta_info['anlasmalı_url'],
                sigorta_info['base_url'] + '/anlasmalı-kurumlar',
                sigorta_info['base_url'] + '/saglik/hastaneler',
                sigorta_info['base_url'] + '/saglik-kuruluslari',
                sigorta_info['base_url'] + '/provider-network',
                sigorta_info['base_url'] + '/health-institutions'
            ]
            
            for url in possible_urls:
                try:
                    response = self.session.get(url, timeout=20)
                    if response.status_code == 200:
                        institutions.extend(self._parse_sigorta_page(response.text, company_name, url))
                        break  # Başarılı olursa diğer URL'leri deneme
                except Exception:
                    continue
            
            if institutions:
                logger.info(f"✅ {company_name}: {len(institutions)} anlaşmalı kurum bulundu")
            
        except Exception as e:
            logger.warning(f"Sigorta şirketi hatası {sigorta_key}: {e}")
        
        return institutions
    
    def _parse_sigorta_page(self, html_content: str, company_name: str, url: str) -> List[Dict]:
        """Sigorta şirketi sayfasını parse et"""
        institutions = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Farklı yapılarda kurum isimlerini ara
            search_patterns = [
                {'tag': 'div', 'class_contains': 'hospital'},
                {'tag': 'div', 'class_contains': 'kurum'},
                {'tag': 'li', 'class_contains': 'provider'},
                {'tag': 'td', 'text_contains': 'hastane'},
                {'tag': 'span', 'class_contains': 'institution'}
            ]
            
            for pattern in search_patterns:
                elements = soup.find_all(pattern['tag'])
                
                for element in elements:
                    text = element.get_text(strip=True)
                    
                    # Hastane/kurum ismi pattern'lerini kontrol et
                    if self._is_health_institution(text):
                        institution = {
                            'kurum_adi': self._clean_institution_name(text),
                            'kurum_tipi': self._determine_institution_type(text),
                            'veri_kaynagi': f'{company_name} Anlaşmalı Kuruluşlar',
                            'sigorta_sirket': company_name,
                            'kaynak_url': url,
                            'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
                        }
                        
                        # Şehir bilgisini çıkarmaya çalış
                        city = self._extract_city_from_text(text)
                        if city:
                            institution['il_adi'] = city
                        
                        institutions.append(institution)
            
            # Excel/PDF linklerini de kontrol et
            doc_links = soup.find_all('a', href=re.compile(r'\.(xlsx?|pdf)$', re.I))
            for link in doc_links:
                href = link.get('href')
                link_text = link.get_text(strip=True)
                
                if any(keyword in link_text.lower() for keyword in ['liste', 'kurum', 'hastane', 'anlasmalı']):
                    if not href.startswith('http'):
                        href = url.rsplit('/', 1)[0] + '/' + href.lstrip('/')
                    
                    logger.info(f"✓ {company_name} dosyası bulundu: {link_text} - {href}")
                    # Bu dosyaları parse edebiliriz
                    
        except Exception as e:
            logger.error(f"Sigorta sayfa parse hatası: {e}")
        
        return institutions
    
    def _is_health_institution(self, text: str) -> bool:
        """Metnin sağlık kurumu olup olmadığını kontrol et"""
        text_lower = text.lower()
        health_keywords = [
            'hastane', 'hospital', 'tıp merkezi', 'medical', 'sağlık', 'health',
            'poliklinik', 'clinic', 'diyaliz', 'dialysis', 'laboratuvar', 'lab',
            'eczane', 'pharmacy', 'diş', 'dental', 'göz', 'eye', 'kalp', 'heart'
        ]
        
        return any(keyword in text_lower for keyword in health_keywords) and len(text) > 5
    
    def _clean_institution_name(self, raw_name: str) -> str:
        """Kurum adını temizle"""
        clean_name = raw_name.strip()
        clean_name = re.sub(r'\s+', ' ', clean_name)
        clean_name = re.sub(r'[^\w\s-.]', '', clean_name)
        
        # Çok kısa veya geçersiz isimleri filtrele
        if len(clean_name) < 5:
            return ''
        
        return clean_name.title()
    
    def _determine_institution_type(self, text: str) -> str:
        """Kurum türünü belirle"""
        text_lower = text.lower()
        
        if 'üniversite' in text_lower:
            return 'Üniversite Hastanesi'
        elif 'özel' in text_lower and 'hastane' in text_lower:
            return 'Özel Hastane'
        elif 'devlet' in text_lower or 'kamu' in text_lower:
            return 'Devlet Hastanesi'
        elif 'tıp merkezi' in text_lower or 'medical' in text_lower:
            return 'Tıp Merkezi'
        elif 'poliklinik' in text_lower:
            return 'Poliklinik'
        elif 'diyaliz' in text_lower:
            return 'Diyaliz Merkezi'
        elif 'laboratuvar' in text_lower:
            return 'Laboratuvar'
        elif 'eczane' in text_lower:
            return 'Eczane'
        else:
            return 'Sağlık Kurumu'
    
    def _extract_city_from_text(self, text: str) -> Optional[str]:
        """Metinden şehir adını çıkar"""
        major_cities = [
            'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana',
            'Konya', 'Gaziantep', 'Kayseri', 'Eskişehir', 'Mersin',
            'Kocaeli', 'Trabzon', 'Samsun', 'Diyarbakır', 'Malatya'
        ]
        
        text_lower = text.lower()
        for city in major_cities:
            if city.lower() in text_lower:
                return city
        
        return None
    
    def fetch_saglik_birlikleri_data(self) -> List[Dict]:
        """Sağlık birlik ve derneklerinden veri çek"""
        all_data = []
        
        for birlik_key, birlik_url in self.saglik_birlikleri.items():
            try:
                logger.info(f"Sağlık birliği taranıyor: {birlik_key}")
                
                response = self.session.get(birlik_url, timeout=20)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Üye listesi, kurum dizini gibi bölümleri ara
                member_links = soup.find_all('a', href=re.compile(r'(uye|member|kurum|hastane)', re.I))
                
                for link in member_links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if 'liste' in text.lower() or 'directory' in text.lower():
                        if not href.startswith('http'):
                            href = birlik_url + href
                        
                        logger.info(f"✓ {birlik_key} üye listesi bulundu: {text}")
                        # Bu linkleri takip edip parse edebiliriz
                
            except Exception as e:
                logger.warning(f"Sağlık birliği hatası {birlik_key}: {e}")
        
        return all_data
    
    def fetch_all_sgk_sigorta_sources(self) -> List[Dict]:
        """Tüm SGK ve sigorta veri kaynaklarını çek"""
        all_institutions = []
        
        logger.info("🏛️ SGK ve sigorta şirketleri yeni veri kaynakları taranıyor...")
        
        # 1. Sigorta şirketlerinin anlaşmalı kuruluşları
        for sigorta_key, sigorta_info in self.sigorta_sirketleri.items():
            institutions = self.fetch_sigorta_anlasmalı_kurumlar(sigorta_key, sigorta_info)
            all_institutions.extend(institutions)
        
        logger.info(f"✅ Sigorta şirketleri: {len(all_institutions)} kurum")
        
        # 2. Sağlık birlik ve dernekleri
        birlik_data = self.fetch_saglik_birlikleri_data()
        all_institutions.extend(birlik_data)
        logger.info(f"✅ Sağlık birlikleri: {len(birlik_data)} kurum")
        
        # Duplikatları temizle
        unique_institutions = []
        seen_names = set()
        
        for institution in all_institutions:
            name_key = institution['kurum_adi'].lower().strip()
            if name_key not in seen_names and len(name_key) > 5:
                seen_names.add(name_key)
                unique_institutions.append(institution)
        
        logger.info(f"🎯 Toplam benzersiz SGK/Sigorta kurumu: {len(unique_institutions)}")
        return unique_institutions
    
    def save_data(self, institutions: List[Dict]):
        """Verileri kaydet"""
        json_file = os.path.join(self.data_dir, 'sgk_sigorta_yeni_kaynaklar.json')
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(institutions, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 SGK/Sigorta verileri kaydedildi: {json_file}")

def main():
    """Ana fonksiyon"""
    logger.info("SGK ve sigorta şirketleri yeni veri kaynakları keşfi başlıyor...")
    
    fetcher = SGKSigortaYeniKaynaklar()
    
    try:
        institutions = fetcher.fetch_all_sgk_sigorta_sources()
        
        if institutions:
            fetcher.save_data(institutions)
            
            # İstatistikler
            companies = {}
            types = {}
            
            for institution in institutions:
                company = institution.get('sigorta_sirket', 'Bilinmiyor')
                inst_type = institution.get('kurum_tipi', 'Bilinmiyor')
                
                companies[company] = companies.get(company, 0) + 1
                types[inst_type] = types.get(inst_type, 0) + 1
            
            logger.info("🏢 Sigorta şirketi bazlı dağılım:")
            for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   - {company}: {count}")
            
            logger.info("🏥 Kurum türü bazlı dağılım:")
            for inst_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   - {inst_type}: {count}")
                
            logger.info("✅ SGK ve sigorta şirketleri yeni kaynaklar işlemi tamamlandı!")
        else:
            logger.warning("❌ Hiç SGK/sigorta kurumu bulunamadı!")
            
    except Exception as e:
        logger.error(f"❌ İşlem başarısız: {e}")

if __name__ == "__main__":
    main()
