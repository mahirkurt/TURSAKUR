#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Üniversite Hastaneleri Veri Çekme Scripti
=========================================

Bu script sadece üniversite hastanelerini çeker - basit ve güvenilir yaklaşım.
Veri Kaynağı: trhastane.com üniversite hastaneleri sayfası
"""

import os
import json
import hashlib
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional
import time
import re

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fetch_universite_hastaneleri.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniversiteHastaneleriFetcher:
    """Sadece üniversite hastanelerini çeken basit sınıf"""
    
    def __init__(self):
        self.base_url = "https://www.trhastane.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # İl kodları
        self.il_kodlari = {
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

    def get_university_hospitals_from_main_page(self) -> List[Dict]:
        """Ana sayfadan üniversite hastanelerini çek"""
        url = f"{self.base_url}/universite-hastaneleri-listesi.html"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            hospitals = []
            
            # Sayfadaki üniversite hastanesi linklerini bul
            hospital_links = soup.find_all('a', href=re.compile(r'universitesi.*hastanesi.*\.html$', re.I))
            
            logger.info(f"Ana sayfada {len(hospital_links)} üniversite hastanesi bulundu")
            
            for link in hospital_links[:20]:  # İlk 20 hastane
                try:
                    hospital_name = link.get_text(strip=True)
                    hospital_url = link.get('href')
                    
                    if not hospital_url.startswith('http'):
                        hospital_url = self.base_url + hospital_url
                    
                    # Basit veri oluştur
                    hospital_data = {
                        'kurum_adi': hospital_name,
                        'kurum_tipi': 'Üniversite Hastanesi',
                        'veri_kaynagi': 'trhastane.com',
                        'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
                        'web_sitesi': hospital_url
                    }
                    
                    # Şehir bilgisini addan çıkarmaya çalış
                    if 'ankara' in hospital_name.lower():
                        hospital_data['il_adi'] = 'Ankara'
                    elif 'istanbul' in hospital_name.lower():
                        hospital_data['il_adi'] = 'İstanbul'
                    elif 'izmir' in hospital_name.lower():
                        hospital_data['il_adi'] = 'İzmir'
                    elif 'bursa' in hospital_name.lower():
                        hospital_data['il_adi'] = 'Bursa'
                    elif 'antalya' in hospital_name.lower():
                        hospital_data['il_adi'] = 'Antalya'
                    elif 'konya' in hospital_name.lower():
                        hospital_data['il_adi'] = 'Konya'
                    elif 'adana' in hospital_name.lower():
                        hospital_data['il_adi'] = 'Adana'
                    elif 'gaziantep' in hospital_name.lower():
                        hospital_data['il_adi'] = 'Gaziantep'
                    elif 'kayseri' in hospital_name.lower():
                        hospital_data['il_adi'] = 'Kayseri'
                    elif 'eskişehir' in hospital_name.lower() or 'eskisehir' in hospital_name.lower():
                        hospital_data['il_adi'] = 'Eskişehir'
                    else:
                        hospital_data['il_adi'] = 'Bilinmiyor'
                    
                    hospitals.append(hospital_data)
                    logger.info(f"✓ {hospital_name}")
                    
                    time.sleep(0.1)  # Çok kısa bekleme
                    
                except Exception as e:
                    logger.warning(f"Hastane işleme hatası: {e}")
                    continue
            
            return hospitals
            
        except Exception as e:
            logger.error(f"Ana sayfa çekme hatası: {e}")
            return []

    def get_known_university_hospitals(self) -> List[Dict]:
        """Bilinen üniversite hastanelerinin listesi - fallback"""
        known_hospitals = [
            {
                'kurum_adi': 'Hacettepe Üniversitesi Hastanesi',
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': 'Ankara',
                'il_kodu': self.il_kodlari.get('Ankara', 6),
                'ilce_adi': 'Altındağ',
                'adres': 'Hacettepe Üniversitesi Hastaneleri, Sıhhiye, Altındağ/Ankara',
                'telefon': '+903123051000',
                'web_sitesi': 'https://www.hacettepe.edu.tr',
                'veri_kaynagi': 'Manuel - Bilinen Kurum',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'kurum_adi': 'Ankara Üniversitesi Tıp Fakültesi İbni Sina Hastanesi',
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': 'Ankara',
                'il_kodu': self.il_kodlari.get('Ankara', 6),
                'ilce_adi': 'Altındağ',
                'adres': 'Ankara Üniversitesi İbn-i Sina Hastanesi, Sıhhiye, Altındağ/Ankara',
                'telefon': '+903123103333',
                'web_sitesi': 'https://hastane.ankara.edu.tr',
                'veri_kaynagi': 'Manuel - Bilinen Kurum',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'kurum_adi': 'İstanbul Üniversitesi İstanbul Tıp Fakültesi Hastanesi',
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': 'İstanbul',
                'il_kodu': self.il_kodlari.get('İstanbul', 34),
                'ilce_adi': 'Fatih',
                'adres': 'İstanbul Üniversitesi İstanbul Tıp Fakültesi, Çapa, Fatih/İstanbul',
                'web_sitesi': 'https://itfhastanesi.istanbul.edu.tr',
                'veri_kaynagi': 'Manuel - Bilinen Kurum',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'kurum_adi': 'Ege Üniversitesi Tıp Fakültesi Hastanesi',
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': 'İzmir',
                'il_kodu': self.il_kodlari.get('İzmir', 35),
                'ilce_adi': 'Bornova',
                'adres': 'Ege Üniversitesi Hastanesi, Kazımdirik Mah., Bornova/İzmir',
                'web_sitesi': 'https://hastane.ege.edu.tr',
                'veri_kaynagi': 'Manuel - Bilinen Kurum',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'kurum_adi': 'Uludağ Üniversitesi Tıp Fakültesi Hastanesi',
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': 'Bursa',
                'il_kodu': self.il_kodlari.get('Bursa', 16),
                'ilce_adi': 'Nilüfer',
                'adres': 'Uludağ Üniversitesi Tıp Fakültesi Hastanesi, Görükle Kampüsü, Nilüfer/Bursa',
                'web_sitesi': 'https://hastane.uludag.edu.tr',
                'veri_kaynagi': 'Manuel - Bilinen Kurum',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'kurum_adi': 'Çukurova Üniversitesi Tıp Fakültesi Balcalı Hastanesi',
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': 'Adana',
                'il_kodu': self.il_kodlari.get('Adana', 1),
                'ilce_adi': 'Sarıçam',
                'adres': 'Çukurova Üniversitesi Balcalı Hastanesi, Balcalı, Sarıçam/Adana',
                'web_sitesi': 'https://hastane.cu.edu.tr',
                'veri_kaynagi': 'Manuel - Bilinen Kurum',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'kurum_adi': 'Selçuk Üniversitesi Tıp Fakültesi Hastanesi',
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': 'Konya',
                'il_kodu': self.il_kodlari.get('Konya', 42),
                'ilce_adi': 'Selçuklu',
                'adres': 'Selçuk Üniversitesi Tıp Fakültesi Hastanesi, Alaeddin Keykubat Kampüsü, Selçuklu/Konya',
                'web_sitesi': 'https://hastane.selcuk.edu.tr',
                'veri_kaynagi': 'Manuel - Bilinen Kurum',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'kurum_adi': 'Erciyes Üniversitesi Tıp Fakültesi Hastanesi',
                'kurum_tipi': 'Üniversite Hastanesi',
                'il_adi': 'Kayseri',
                'il_kodu': self.il_kodlari.get('Kayseri', 38),
                'ilce_adi': 'Melikgazi',
                'adres': 'Erciyes Üniversitesi Tıp Fakültesi Hastanesi, Talas Yolu, Melikgazi/Kayseri',
                'web_sitesi': 'https://hastane.erciyes.edu.tr',
                'veri_kaynagi': 'Manuel - Bilinen Kurum',
                'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
            }
        ]
        
        return known_hospitals

    def generate_facility_id(self, facility: Dict) -> str:
        """Kurum için benzersiz ID üret"""
        # İl kodu haritası (sadece gerekli iller)
        il_kodlari = {
            'ankara': '06', 'istanbul': '34', 'izmir': '35', 'bursa': '16',
            'adana': '01', 'konya': '42', 'antalya': '07', 'kayseri': '38',
            'gaziantep': '27', 'eskişehir': '26', 'bilinmiyor': '99'
        }
        
        il_adi = facility.get('il_adi', '').lower()
        kurum_adi = facility.get('kurum_adi', '')
        
        il_kodu = il_kodlari.get(il_adi, '99')
        tip_kodu = 'UH'  # Üniversite Hastanesi
        
        # Sıra numarası için hash kullan
        hash_input = f"{kurum_adi}{il_adi}".lower()
        hash_digest = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        sira_no = hash_digest[:4].upper()
        
        return f"TR-{il_kodu}-{tip_kodu}-{sira_no}"

    def save_data(self, hospitals: List[Dict]) -> str:
        """Verileri JSON formatında kaydet"""
        # ID'leri ekle
        for hospital in hospitals:
            hospital['kurum_id'] = self.generate_facility_id(hospital)
        
        # Dosya yolu
        json_file = os.path.join(self.data_dir, 'universite_hastaneleri.json')
        
        # JSON kaydet
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(hospitals, f, ensure_ascii=False, indent=2)
        
        return json_file

def main():
    """Ana fonksiyon - basit ve güvenilir"""
    logger.info("Üniversite hastaneleri veri çekme başlıyor...")
    
    fetcher = UniversiteHastaneleriFetcher()
    
    try:
        # Önce web'den çekmeyi dene
        hospitals = fetcher.get_university_hospitals_from_main_page()
        
        # Eğer web'den çekemediyse, bilinen listeyi kullan
        if not hospitals:
            logger.warning("Web'den veri çekilemedi, bilinen liste kullanılıyor")
            hospitals = fetcher.get_known_university_hospitals()
        
        if not hospitals:
            logger.error("Hiç üniversite hastanesi verisi elde edilemedi!")
            return
        
        # Verileri kaydet
        json_file = fetcher.save_data(hospitals)
        
        logger.info(f"✅ İşlem tamamlandı!")
        logger.info(f"📊 Toplam üniversite hastanesi: {len(hospitals)}")
        logger.info(f"💾 JSON dosyası: {json_file}")
        
        # İl bazlı dağılım
        city_stats = {}
        for hospital in hospitals:
            city = hospital.get('il_adi', 'Bilinmiyor')
            city_stats[city] = city_stats.get(city, 0) + 1
        
        logger.info("🏙️ İl bazlı dağılım:")
        for city, count in sorted(city_stats.items()):
            logger.info(f"  - {city}: {count}")
        
    except Exception as e:
        logger.error(f"İşlem hatası: {e}")
        raise

if __name__ == "__main__":
    main()
