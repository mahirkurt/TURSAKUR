#!/usr/bin/env python3
"""
Vikipedia Sağlık Kuruluşları Gelişmiş Veri Kaynakları Scripti
=============================================================

Vikipedia'daki sağlık kuruluşları verilerini genişletme:
1. Türkiye'deki hastaneler kategorisi ve alt kategorileri
2. Üniversite hastaneleri listesi
3. Şehir bazlı hastane listeleri
4. Sağlık kuruluşları infobox verileri
5. Wikidata entegrasyonu ile koordinat ve detay bilgileri
"""

import requests
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
import urllib.parse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VikipediaGelismisKesfet:
    """Vikipedia'dan gelişmiş sağlık kuruluşları verilerini çeken sınıf."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TursakurBot/1.0 (https://github.com/turkiye-saglik-kuruluslari; info@turkiye-saglik.org)'
        })
        
        # Wikipedia API endpoints
        self.wiki_api = 'https://tr.wikipedia.org/api/rest_v1'
        self.wikidata_api = 'https://www.wikidata.org/w/api.php'
        
        # Sağlık kuruluşları ile ilgili Vikipedia kategorileri
        self.wiki_categories = {
            'hastaneler': [
                'Kategori:Türkiye\'deki hastaneler',
                'Kategori:İstanbul\'daki hastaneler',
                'Kategori:Ankara\'daki hastaneler',
                'Kategori:İzmir\'deki hastaneler',
                'Kategori:Bursa\'daki hastaneler',
                'Kategori:Antalya\'daki hastaneler',
                'Kategori:Adana\'daki hastaneler'
            ],
            'universite_hastaneleri': [
                'Kategori:Türkiye\'deki üniversite hastaneleri',
                'Kategori:Tıp fakülteleri'
            ],
            'saglik_kuruluslari': [
                'Kategori:Türkiye\'deki sağlık kuruluşları',
                'Kategori:Sağlık bakanlığı hastaneleri',
                'Kategori:Özel hastaneler'
            ],
            'tip_fakulteleri': [
                'Kategori:Türkiye\'deki tıp fakülteleri',
                'Kategori:Tıp eğitimi'
            ]
        }
        
        # Şehir bazlı sağlık kuruluşları arama listesi
        self.major_cities = [
            'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya',
            'Gaziantep', 'Kayseri', 'Eskişehir', 'Mersin', 'Kocaeli', 'Trabzon',
            'Samsun', 'Diyarbakır', 'Malatya', 'Erzurum', 'Van', 'Denizli',
            'Sakarya', 'Tekirdağ', 'Balıkesir', 'Kütahya', 'Manisa', 'Hatay'
        ]
        
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_category_members(self, category: str) -> List[str]:
        """Vikipedia kategorisindeki üyeleri çek"""
        members = []
        
        try:
            # MediaWiki API kullanarak kategori üyelerini al
            params = {
                'action': 'query',
                'list': 'categorymembers',
                'cmtitle': category,
                'cmlimit': 500,
                'format': 'json'
            }
            
            response = self.session.get('https://tr.wikipedia.org/w/api.php', params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'query' in data and 'categorymembers' in data['query']:
                for member in data['query']['categorymembers']:
                    title = member['title']
                    # Sadece ana ad alanındaki sayfaları al (Kategori: vs. Şablon: hariç)
                    if ':' not in title or title.startswith('Kategori:'):
                        continue
                    members.append(title)
                    
            logger.info(f"✓ {category}: {len(members)} üye bulundu")
            
        except Exception as e:
            logger.warning(f"Kategori üyeleri alınamadı {category}: {e}")
        
        return members
    
    def fetch_page_info(self, page_title: str) -> Optional[Dict]:
        """Vikipedia sayfasından detay bilgileri çek"""
        try:
            # Sayfa içeriğini al
            encoded_title = urllib.parse.quote(page_title.replace(' ', '_'))
            url = f"https://tr.wikipedia.org/wiki/{encoded_title}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Infobox verilerini çıkar
            infobox = soup.find('table', class_='infobox')
            info_data = {}
            
            if infobox:
                rows = infobox.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        info_data[key] = value
            
            # Koordinat bilgilerini ara
            coordinates = self._extract_coordinates(soup)
            
            # Sayfa kategorilerini al
            categories = []
            cat_links = soup.find_all('a', href=re.compile(r'/wiki/Kategori:'))
            for link in cat_links:
                cat_text = link.get_text(strip=True)
                if any(keyword in cat_text.lower() for keyword in ['hastane', 'sağlık', 'tıp', 'hospital']):
                    categories.append(cat_text)
            
            institution_data = {
                'kurum_adi': page_title,
                'wiki_url': url,
                'infobox_data': info_data,
                'koordinatlar': coordinates,
                'kategoriler': categories,
                'veri_kaynagi': 'Vikipedia Gelişmiş Keşif',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Infobox'tan ek bilgileri çıkar
            institution_data.update(self._parse_infobox_details(info_data))
            
            return institution_data
            
        except Exception as e:
            logger.warning(f"Sayfa bilgileri alınamadı {page_title}: {e}")
            return None
    
    def _extract_coordinates(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Sayfadan koordinat bilgilerini çıkar"""
        # Geo microformat'ı ara
        geo_span = soup.find('span', class_='geo')
        if geo_span:
            coord_text = geo_span.get_text(strip=True)
            coords = coord_text.split(';')
            if len(coords) == 2:
                try:
                    lat = float(coords[0].strip())
                    lon = float(coords[1].strip())
                    return {'lat': lat, 'lon': lon}
                except ValueError:
                    pass
        
        # Koordinat linklerini ara
        coord_links = soup.find_all('a', href=re.compile(r'geohack|maps\.google'))
        for link in coord_links:
            href = link.get('href')
            # URL'den koordinatları çıkarmaya çalış
            lat_match = re.search(r'lat[=:]([0-9.-]+)', href)
            lon_match = re.search(r'lon[=:]([0-9.-]+)', href)
            
            if lat_match and lon_match:
                try:
                    lat = float(lat_match.group(1))
                    lon = float(lon_match.group(1))
                    return {'lat': lat, 'lon': lon}
                except ValueError:
                    pass
        
        return None
    
    def _parse_infobox_details(self, infobox_data: Dict) -> Dict:
        """Infobox verilerinden standart alanları çıkar"""
        details = {}
        
        # Yaygın infobox alan isimleri
        field_mappings = {
            'kuruluş': 'kurulus_tarihi',
            'kuruluş tarihi': 'kurulus_tarihi',
            'established': 'kurulus_tarihi',
            'açılış': 'kurulus_tarihi',
            'konum': 'adres',
            'adres': 'adres',
            'location': 'adres',
            'address': 'adres',
            'yatak sayısı': 'yatak_sayisi',
            'beds': 'yatak_sayisi',
            'capacity': 'yatak_sayisi',
            'telefon': 'telefon',
            'phone': 'telefon',
            'web sitesi': 'web_sitesi',
            'website': 'web_sitesi',
            'internet sitesi': 'web_sitesi',
            'tip': 'kurum_tipi',
            'type': 'kurum_tipi',
            'türü': 'kurum_tipi',
            'speciality': 'uzmanlik_alani',
            'uzmanlık': 'uzmanlik_alani',
            'dal': 'uzmanlik_alani'
        }
        
        for original_key, value in infobox_data.items():
            key_lower = original_key.lower().strip()
            
            # Eşleşen alanı bul
            for search_key, standard_field in field_mappings.items():
                if search_key in key_lower:
                    details[standard_field] = value.strip()
                    break
        
        # Kurum türünü belirle
        if 'kurum_tipi' not in details:
            details['kurum_tipi'] = self._determine_institution_type_from_infobox(infobox_data)
        
        return details
    
    def _determine_institution_type_from_infobox(self, infobox_data: Dict) -> str:
        """Infobox verilerinden kurum türünü belirle"""
        combined_text = ' '.join(infobox_data.values()).lower()
        
        if 'üniversite' in combined_text:
            return 'Üniversite Hastanesi'
        elif 'özel' in combined_text:
            return 'Özel Hastane'
        elif 'devlet' in combined_text or 'kamu' in combined_text:
            return 'Devlet Hastanesi'
        elif 'eğitim' in combined_text or 'araştırma' in combined_text:
            return 'Eğitim ve Araştırma Hastanesi'
        elif 'çocuk' in combined_text:
            return 'Çocuk Hastanesi'
        elif 'kadın' in combined_text or 'doğum' in combined_text:
            return 'Kadın Doğum Hastanesi'
        elif 'kalp' in combined_text or 'kardiyoloji' in combined_text:
            return 'Kardiyoloji Hastanesi'
        elif 'onkoloji' in combined_text or 'kanser' in combined_text:
            return 'Onkoloji Hastanesi'
        else:
            return 'Hastane'
    
    def search_city_hospitals(self, city_name: str) -> List[str]:
        """Şehir bazlı hastane arama"""
        hospitals = []
        
        try:
            # Şehir + hastane kombinasyonu ile arama
            search_terms = [
                f"{city_name} hastaneleri",
                f"{city_name} sağlık kuruluşları",
                f"{city_name} tıp merkezi",
                f"Liste:{city_name} hastaneleri"
            ]
            
            for term in search_terms:
                params = {
                    'action': 'query',
                    'list': 'search',
                    'srsearch': term,
                    'srlimit': 50,
                    'format': 'json'
                }
                
                response = self.session.get('https://tr.wikipedia.org/w/api.php', params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'query' in data and 'search' in data['query']:
                    for result in data['query']['search']:
                        title = result['title']
                        snippet = result.get('snippet', '')
                        
                        # Sağlık kuruluşu olup olmadığını kontrol et
                        if self._is_health_related(title, snippet):
                            hospitals.append(title)
            
            # Duplikatları temizle
            hospitals = list(set(hospitals))
            logger.info(f"✓ {city_name}: {len(hospitals)} hastane bulundu")
            
        except Exception as e:
            logger.warning(f"Şehir araması başarısız {city_name}: {e}")
        
        return hospitals
    
    def _is_health_related(self, title: str, snippet: str) -> bool:
        """Başlık ve snippet'in sağlık kurumuyla ilgili olup olmadığını kontrol et"""
        combined_text = (title + ' ' + snippet).lower()
        
        health_keywords = [
            'hastane', 'hospital', 'sağlık', 'health', 'tıp', 'medical',
            'poliklinik', 'clinic', 'merkez', 'center', 'üniversitesi',
            'fakültesi', 'araştırma', 'eğitim', 'özel', 'devlet'
        ]
        
        return any(keyword in combined_text for keyword in health_keywords)
    
    def fetch_wikidata_details(self, page_title: str) -> Optional[Dict]:
        """Wikidata'dan ek detayları çek"""
        try:
            # Önce Vikipedia'dan Wikidata ID'sini al
            params = {
                'action': 'query',
                'titles': page_title,
                'prop': 'pageprops',
                'format': 'json'
            }
            
            response = self.session.get('https://tr.wikipedia.org/w/api.php', params=params)
            data = response.json()
            
            wikidata_id = None
            if 'query' in data and 'pages' in data['query']:
                for page_id, page_data in data['query']['pages'].items():
                    if 'pageprops' in page_data and 'wikibase_item' in page_data['pageprops']:
                        wikidata_id = page_data['pageprops']['wikibase_item']
                        break
            
            if not wikidata_id:
                return None
            
            # Wikidata'dan detayları al
            wikidata_params = {
                'action': 'wbgetentities',
                'ids': wikidata_id,
                'format': 'json',
                'languages': 'tr|en'
            }
            
            wikidata_response = self.session.get(self.wikidata_api, params=wikidata_params)
            wikidata_data = wikidata_response.json()
            
            if 'entities' in wikidata_data and wikidata_id in wikidata_data['entities']:
                entity = wikidata_data['entities'][wikidata_id]
                
                details = {
                    'wikidata_id': wikidata_id
                }
                
                # Claims'den yararlı bilgileri çıkar
                if 'claims' in entity:
                    claims = entity['claims']
                    
                    # Koordinatlar (P625)
                    if 'P625' in claims:
                        coord_claim = claims['P625'][0]
                        if 'mainsnak' in coord_claim and 'datavalue' in coord_claim['mainsnak']:
                            coords = coord_claim['mainsnak']['datavalue']['value']
                            details['wikidata_koordinatlar'] = {
                                'lat': coords['latitude'],
                                'lon': coords['longitude']
                            }
                    
                    # Kuruluş tarihi (P571)
                    if 'P571' in claims:
                        founding_claim = claims['P571'][0]
                        if 'mainsnak' in founding_claim and 'datavalue' in founding_claim['mainsnak']:
                            details['wikidata_kurulus_tarihi'] = founding_claim['mainsnak']['datavalue']['value']['time']
                
                return details
                
        except Exception as e:
            logger.warning(f"Wikidata detayları alınamadı {page_title}: {e}")
        
        return None
    
    def fetch_all_wikipedia_sources(self) -> List[Dict]:
        """Tüm Vikipedia kaynaklarından sağlık kuruluşlarını çek"""
        all_institutions = []
        
        logger.info("🔍 Vikipedia gelişmiş keşif başlıyor...")
        
        # 1. Kategori bazlı tarama
        all_pages = set()
        for category_group, categories in self.wiki_categories.items():
            logger.info(f"📂 {category_group} kategorileri taranıyor...")
            
            for category in categories:
                members = self.fetch_category_members(category)
                all_pages.update(members)
        
        logger.info(f"✅ Kategori taraması: {len(all_pages)} benzersiz sayfa")
        
        # 2. Şehir bazlı arama
        for city in self.major_cities:
            city_hospitals = self.search_city_hospitals(city)
            all_pages.update(city_hospitals)
        
        logger.info(f"✅ Şehir araması sonrası: {len(all_pages)} benzersiz sayfa")
        
        # 3. Her sayfa için detay bilgileri çek
        for i, page_title in enumerate(all_pages, 1):
            if i % 10 == 0:
                logger.info(f"İşleniyor: {i}/{len(all_pages)}")
            
            page_info = self.fetch_page_info(page_title)
            if page_info:
                # Wikidata detaylarını da ekle
                wikidata_info = self.fetch_wikidata_details(page_title)
                if wikidata_info:
                    page_info.update(wikidata_info)
                
                all_institutions.append(page_info)
        
        logger.info(f"🎯 Toplam işlenen Vikipedia kurumu: {len(all_institutions)}")
        return all_institutions
    
    def save_data(self, institutions: List[Dict]):
        """Verileri kaydet"""
        json_file = os.path.join(self.data_dir, 'vikipedia_gelismis_kesfet.json')
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(institutions, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Vikipedia gelişmiş verileri kaydedildi: {json_file}")

def main():
    """Ana fonksiyon"""
    logger.info("Vikipedia sağlık kuruluşları gelişmiş keşfi başlıyor...")
    
    fetcher = VikipediaGelismisKesfet()
    
    try:
        institutions = fetcher.fetch_all_wikipedia_sources()
        
        if institutions:
            fetcher.save_data(institutions)
            
            # İstatistikler
            types = {}
            cities = {}
            with_coords = 0
            with_wikidata = 0
            
            for institution in institutions:
                inst_type = institution.get('kurum_tipi', 'Bilinmiyor')
                types[inst_type] = types.get(inst_type, 0) + 1
                
                # Şehir bilgisi çıkar
                for city in fetcher.major_cities:
                    if city.lower() in institution['kurum_adi'].lower():
                        cities[city] = cities.get(city, 0) + 1
                        break
                
                if institution.get('koordinatlar') or institution.get('wikidata_koordinatlar'):
                    with_coords += 1
                
                if institution.get('wikidata_id'):
                    with_wikidata += 1
            
            logger.info("🏥 Kurum türü bazlı dağılım:")
            for inst_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   - {inst_type}: {count}")
            
            logger.info("🏙️ Şehir bazlı dağılım (top 10):")
            for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
                logger.info(f"   - {city}: {count}")
            
            logger.info(f"📍 Koordinat bilgisi olan: {with_coords}")
            logger.info(f"🔗 Wikidata entegrasyonu olan: {with_wikidata}")
                
            logger.info("✅ Vikipedia gelişmiş keşif işlemi tamamlandı!")
        else:
            logger.warning("❌ Hiç Vikipedia kurumu bulunamadı!")
            
    except Exception as e:
        logger.error(f"❌ İşlem başarısız: {e}")

if __name__ == "__main__":
    main()
