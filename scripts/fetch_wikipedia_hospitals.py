#!/usr/bin/env python3
"""
Vikipedia Hastane Listesi Veri Çekme Scripti
============================================

Vikipedia'dan Türkiye'deki hastaneler listesini çeker.
İyi bir başlangıç noktası ve teyit kaynağı.
"""

import requests
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WikipediaHospitalFetcher:
    """Vikipedia'dan hastane listesi çeken sınıf."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; TurkiyeSaglikDB/1.0; +https://github.com/mahirkurt/TURSAKUR)'
        })
        
        # Vikipedia kategori sayfaları
        self.wiki_pages = [
            'https://tr.wikipedia.org/wiki/Kategori:Türkiye%27deki_hastaneler',
            'https://tr.wikipedia.org/wiki/Kategori:İstanbul%27daki_hastaneler',
            'https://tr.wikipedia.org/wiki/Kategori:Ankara%27daki_hastaneler',
            'https://tr.wikipedia.org/wiki/Kategori:İzmir%27deki_hastaneler'
        ]
        
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_hospital_list_from_category(self, url: str) -> List[Dict]:
        """Vikipedia kategori sayfasından hastane listesi çek"""
        hospitals = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Kategori listesindeki linkleri bul
            category_div = soup.find('div', class_='mw-category')
            if category_div:
                links = category_div.find_all('a')
                
                for link in links:
                    title = link.get('title', '')
                    href = link.get('href', '')
                    
                    if 'hastane' in title.lower() or 'hastane' in href.lower():
                        hospital = {
                            'kurum_adi': title,
                            'kurum_tipi': self._determine_hospital_type(title),
                            'il_adi': self._extract_city_from_url_or_title(url, title),
                            'veri_kaynagi': 'Vikipedia',
                            'wiki_url': f"https://tr.wikipedia.org{href}",
                            'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
                        }
                        hospitals.append(hospital)
                        
            logger.info(f"✓ {url}: {len(hospitals)} hastane bulundu")
            
        except Exception as e:
            logger.error(f"Vikipedia kategori hatası {url}: {e}")
        
        return hospitals
    
    def _determine_hospital_type(self, title: str) -> str:
        """Hastane türünü başlıktan çıkar"""
        title_lower = title.lower()
        
        if 'üniversite' in title_lower:
            return 'Üniversite Hastanesi'
        elif 'özel' in title_lower:
            return 'Özel Hastane'
        elif 'devlet' in title_lower or 'kamu' in title_lower:
            return 'Devlet Hastanesi'
        elif 'eğitim' in title_lower and 'araştırma' in title_lower:
            return 'Eğitim ve Araştırma Hastanesi'
        elif 'şehir' in title_lower:
            return 'Şehir Hastanesi'
        else:
            return 'Hastane'
    
    def _extract_city_from_url_or_title(self, url: str, title: str) -> str:
        """Şehir adını URL veya başlıktan çıkar"""
        # URL'den şehir adını çıkar
        if 'istanbul' in url.lower():
            return 'İstanbul'
        elif 'ankara' in url.lower():
            return 'Ankara'
        elif 'izmir' in url.lower():
            return 'İzmir'
        
        # Başlıktan şehir adını çıkar
        title_lower = title.lower()
        cities = [
            ('istanbul', 'İstanbul'), ('ankara', 'Ankara'), ('izmir', 'İzmir'),
            ('bursa', 'Bursa'), ('antalya', 'Antalya'), ('adana', 'Adana'),
            ('konya', 'Konya'), ('gaziantep', 'Gaziantep'), ('kayseri', 'Kayseri'),
            ('eskişehir', 'Eskişehir')
        ]
        
        for city_key, city_name in cities:
            if city_key in title_lower:
                return city_name
        
        return 'Bilinmiyor'
    
    def fetch_all_data(self) -> List[Dict]:
        """Tüm Vikipedia kaynaklarından veri çek"""
        all_hospitals = []
        
        for url in self.wiki_pages:
            hospitals = self.fetch_hospital_list_from_category(url)
            all_hospitals.extend(hospitals)
        
        # Duplikatları temizle
        unique_hospitals = []
        seen_names = set()
        
        for hospital in all_hospitals:
            name = hospital['kurum_adi'].lower().strip()
            if name not in seen_names:
                seen_names.add(name)
                unique_hospitals.append(hospital)
        
        logger.info(f"Toplam Vikipedia hastane verisi: {len(unique_hospitals)}")
        return unique_hospitals
    
    def save_data(self, hospitals: List[Dict]):
        """Verileri kaydet"""
        json_file = os.path.join(self.data_dir, 'wikipedia_hospitals.json')
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(hospitals, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Vikipedia hastane verileri kaydedildi: {json_file}")
        return json_file

def main():
    """Ana fonksiyon"""
    logger.info("Vikipedia hastane listesi çekme işlemi başlıyor...")
    
    fetcher = WikipediaHospitalFetcher()
    
    try:
        hospitals = fetcher.fetch_all_data()
        
        if hospitals:
            fetcher.save_data(hospitals)
            
            # İstatistikler
            types = {}
            cities = {}
            
            for hospital in hospitals:
                h_type = hospital['kurum_tipi']
                h_city = hospital['il_adi']
                
                types[h_type] = types.get(h_type, 0) + 1
                cities[h_city] = cities.get(h_city, 0) + 1
            
            logger.info(f"📊 Toplam: {len(hospitals)} hastane")
            logger.info("🏥 Tür bazlı dağılım:")
            for h_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   - {h_type}: {count}")
            
            logger.info("🏙️ Şehir bazlı dağılım:")
            for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
                logger.info(f"   - {city}: {count}")
                
            logger.info("✅ Vikipedia veri çekme işlemi tamamlandı!")
        else:
            logger.warning("❌ Hiç veri çekilemedi!")
            
    except Exception as e:
        logger.error(f"❌ İşlem başarısız: {e}")

if __name__ == "__main__":
    main()
