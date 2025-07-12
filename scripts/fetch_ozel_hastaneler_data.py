#!/usr/bin/env python3
"""
Özel Hastaneler Veri Çekme Betiği
Sağlık Bakanlığı Özel Hastaneler Daire Başkanlığı'nın web sitesinden özel hastane verilerini çeker ve işler.
"""

import requests
import pandas as pd
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
from bs4 import BeautifulSoup
import re

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OzelHastanelerDataFetcher:
    """Özel hastaneler verilerini çeken sınıf."""
    
    def __init__(self):
        self.base_url = "https://shgmozelhasdb.saglik.gov.tr/TR-53567/ozel-hastane-listesi-faal.html"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # İl kodu eşlemeleri
        self.il_kodu_mapping = {
            'ADANA': 1, 'ADIYAMAN': 2, 'AFYONKARAHİSAR': 3, 'AĞRI': 4, 'AMASYA': 5,
            'ANKARA': 6, 'ANTALYA': 7, 'ARTVİN': 8, 'AYDIN': 9, 'BALIKESİR': 10,
            'BİLECİK': 11, 'BİNGÖL': 12, 'BİTLİS': 13, 'BOLU': 14, 'BURDUR': 15,
            'BURSA': 16, 'ÇANAKKALE': 17, 'ÇANKIRI': 18, 'ÇORUM': 19, 'DENİZLİ': 20,
            'DİYARBAKIR': 21, 'EDİRNE': 22, 'ELAZIĞ': 23, 'ERZİNCAN': 24, 'ERZURUM': 25,
            'ESKİŞEHİR': 26, 'GAZİANTEP': 27, 'GİRESUN': 28, 'GÜMÜŞHANE': 29, 'HAKKARİ': 30,
            'HATAY': 31, 'ISPARTA': 32, 'MERSİN': 33, 'İSTANBUL': 34, 'İZMİR': 35,
            'KARS': 36, 'KASTAMONU': 37, 'KAYSERİ': 38, 'KIRKLARELİ': 39, 'KIRŞEHİR': 40,
            'KOCAELİ': 41, 'KONYA': 42, 'KÜTAHYA': 43, 'MALATYA': 44, 'MANİSA': 45,
            'KAHRAMANMARAŞ': 46, 'MARDİN': 47, 'MUĞLA': 48, 'MUŞ': 49, 'NEVŞEHİR': 50,
            'NİĞDE': 51, 'ORDU': 52, 'RİZE': 53, 'SAKARYA': 54, 'SAMSUN': 55,
            'SİİRT': 56, 'SİNOP': 57, 'SİVAS': 58, 'TEKİRDAĞ': 59, 'TOKAT': 60,
            'TRABZON': 61, 'TUNCELİ': 62, 'ŞANLIURFA': 63, 'UŞAK': 64, 'VAN': 65,
            'YOZGAT': 66, 'ZONGULDAK': 67, 'AKSARAY': 68, 'BAYBURT': 69, 'KARAMAN': 70,
            'KIRIKKALE': 71, 'BATMAN': 72, 'ŞIRNAK': 73, 'BARTIN': 74, 'ARDAHAN': 75,
            'IĞDIR': 76, 'YALOVA': 77, 'KARABÜK': 78, 'KİLİS': 79, 'OSMANİYE': 80,
            'DÜZCE': 81
        }
        
        # Kurum tipi standartlaştırması
        self.kurum_tipi_mapping = {
            'Özel Genel Hastane': 'Özel Genel Hastane',
            'Özel Göz Hastanesi': 'Özel Göz Hastanesi', 
            'Özel Kadın Hastalıkları ve Doğum Hastane': 'Özel Kadın Hastalıkları ve Doğum Hastanesi',
            'Özel Ruh Sağlığı ve Hastalıkları Hastane': 'Özel Ruh Sağlığı ve Hastalıkları Hastanesi',
            'Özel Fizik Tedavi ve Rehabilitasyon Hst.': 'Özel Fizik Tedavi ve Rehabilitasyon Hastanesi',
            'Özel Kalp Hastanesi': 'Özel Kalp Hastanesi',
            'Özel Diş Hastanesi': 'Özel Diş Hastanesi',
            'Özel Doğum Hastanesi': 'Özel Doğum Hastanesi',
            'Özel Kalp ve Damar Cerrahisi Hastanesi': 'Özel Kalp ve Damar Cerrahisi Hastanesi',
            'Özel Ortopedi ve Travmatoloji Hastanesi': 'Özel Ortopedi ve Travmatoloji Hastanesi',
            'Özel Göğüs Hastalıkları Hastanesi': 'Özel Göğüs Hastalıkları Hastanesi',
            'Lösemili Çocuklar Hastanesi': 'Özel Çocuk Hastanesi'
        }

    def create_hash(self, content: str) -> str:
        """İçerik için hash oluşturur."""
        return hashlib.md5(content.encode()).hexdigest()

    def is_content_changed(self, new_hash: str, hash_file: str) -> bool:
        """İçeriğin değişip değişmediğini kontrol eder."""
        if not os.path.exists(hash_file):
            return True
            
        try:
            with open(hash_file, 'r', encoding='utf-8') as f:
                old_hash = f.read().strip()
            return old_hash != new_hash
        except Exception as e:
            logger.warning(f"Hash dosyası okunamadı: {e}")
            return True

    def save_hash(self, hash_value: str, hash_file: str):
        """Hash değerini kaydeder."""
        try:
            with open(hash_file, 'w', encoding='utf-8') as f:
                f.write(hash_value)
        except Exception as e:
            logger.error(f"Hash kaydedilemedi: {e}")

    def fetch_page_content(self) -> Optional[str]:
        """Web sayfasından içeriği çeker."""
        try:
            logger.info(f"Web sayfası çekiliyor: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            logger.info(f"Sayfa başarıyla çekildi. Boyut: {len(response.text)} karakter")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Web sayfası çekilemedi: {e}")
            return None

    def parse_html_table(self, html_content: str) -> List[Dict[str, str]]:
        """HTML tablosunu parçalar ve veri listesi döndürür."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Tabloyu bul
            table = soup.find('table')
            if not table:
                logger.error("HTML içinde tablo bulunamadı")
                return []
            
            hospitals = []
            
            # Tablo satırlarını işle
            rows = table.find_all('tr')
            for i, row in enumerate(rows):
                # İlk satır başlık satırı
                if i == 0:
                    continue
                    
                cells = row.find_all('td')
                if len(cells) < 4:
                    continue
                
                il = cells[0].get_text(strip=True)
                ilce = cells[1].get_text(strip=True)
                ad = cells[2].get_text(strip=True)
                kurum_tipi = cells[3].get_text(strip=True)
                
                # Boş satırları atla
                if not il or not ad:
                    continue
                
                hospitals.append({
                    'il': il,
                    'ilce': ilce, 
                    'ad': ad,
                    'kurum_tipi': kurum_tipi
                })
            
            logger.info(f"Toplam {len(hospitals)} özel hastane verisi işlendi")
            return hospitals
            
        except Exception as e:
            logger.error(f"HTML tablosu parçalanamadı: {e}")
            return []

    def standardize_hospital_data(self, hospital_data: Dict[str, str]) -> Dict[str, Any]:
        """Hastane verisini standart formata dönüştürür."""
        il = hospital_data['il'].upper().strip()
        ilce = hospital_data['ilce'].strip()
        ad = hospital_data['ad'].strip()
        kurum_tipi = hospital_data['kurum_tipi'].strip()
        
        # İl kodunu al
        il_kodu = self.il_kodu_mapping.get(il, 0)
        
        # Kurum tipini standartlaştır
        standart_tip = self.kurum_tipi_mapping.get(kurum_tipi, kurum_tipi)
        
        # Kurum ID oluştur: TR-[il_kodu]-OZEL-[sıra_no]
        kurum_id = f"TR-{il_kodu:02d}-OZEL-{len(ad):03d}"
        
        return {
            'kurum_id': kurum_id,
            'kurum_adi': ad,
            'kurum_tipi': standart_tip,
            'il_kodu': il_kodu,
            'il_adi': il,
            'ilce_adi': ilce,
            'adres': f"{ilce}/{il}",  # Tam adres bilgisi yok, genel konum
            'telefon': '',  # Web sayfasında telefon bilgisi yok
            'koordinat_lat': None,  # Koordinat bilgisi yok
            'koordinat_lon': None,
            'web_sitesi': '',  # Web sitesi bilgisi yok
            'veri_kaynagi': 'T.C. Sağlık Bakanlığı - Özel Hastaneler Daire Başkanlığı',
            'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
            'kaynak_url': self.base_url
        }

    def process_data(self) -> List[Dict[str, Any]]:
        """Tüm veri işleme sürecini yönetir."""
        # Web sayfasını çek
        html_content = self.fetch_page_content()
        if not html_content:
            return []
        
        # İçerik değişikliğini kontrol et
        content_hash = self.create_hash(html_content)
        hash_file = 'data/raw/ozel_hastaneler_hash.json'
        
        # Hash dizinini oluştur
        os.makedirs(os.path.dirname(hash_file), exist_ok=True)
        
        if not self.is_content_changed(content_hash, hash_file):
            logger.info("İçerik değişmemiş, mevcut veri kullanılacak")
            return self.load_existing_data()
        
        # HTML tablosunu parçala
        raw_hospitals = self.parse_html_table(html_content)
        if not raw_hospitals:
            return []
        
        # Veriyi standartlaştır
        processed_hospitals = []
        for hospital in raw_hospitals:
            try:
                standardized = self.standardize_hospital_data(hospital)
                processed_hospitals.append(standardized)
            except Exception as e:
                logger.warning(f"Hastane verisi işlenemedi: {hospital.get('ad', 'Unknown')} - {e}")
                continue
        
        # Sonuçları kaydet
        self.save_data(processed_hospitals)
        self.save_hash(content_hash, hash_file)
        
        logger.info(f"Toplam {len(processed_hospitals)} özel hastane verisi işlendi ve kaydedildi")
        return processed_hospitals

    def load_existing_data(self) -> List[Dict[str, Any]]:
        """Mevcut veriyi yükler."""
        json_file = 'data/raw/ozel_hastaneler.json'
        try:
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Mevcut {len(data)} özel hastane verisi yüklendi")
                return data
        except Exception as e:
            logger.error(f"Mevcut veri yüklenemedi: {e}")
        return []

    def save_data(self, hospitals: List[Dict[str, Any]]):
        """Veriyi JSON ve CSV formatlarında kaydeder."""
        base_dir = 'data/raw'
        os.makedirs(base_dir, exist_ok=True)
        
        # JSON formatında kaydet
        json_file = os.path.join(base_dir, 'ozel_hastaneler.json')
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(hospitals, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON veri kaydedildi: {json_file}")
        except Exception as e:
            logger.error(f"JSON veri kaydedilemedi: {e}")
        
        # CSV formatında kaydet
        csv_file = os.path.join(base_dir, 'ozel_hastaneler.csv')
        try:
            df = pd.DataFrame(hospitals)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            logger.info(f"CSV veri kaydedildi: {csv_file}")
        except Exception as e:
            logger.error(f"CSV veri kaydedilemedi: {e}")

def main():
    """Ana fonksiyon."""
    try:
        fetcher = OzelHastanelerDataFetcher()
        hospitals = fetcher.process_data()
        
        if hospitals:
            print(f"\n✅ Başarı! {len(hospitals)} özel hastane verisi işlendi.")
            
            # İstatistikler
            il_stats = {}
            tip_stats = {}
            
            for hospital in hospitals:
                il = hospital['il_adi']
                tip = hospital['kurum_tipi']
                
                il_stats[il] = il_stats.get(il, 0) + 1
                tip_stats[tip] = tip_stats.get(tip, 0) + 1
            
            print("\n📊 İl Bazında Dağılım (İlk 10):")
            for il, count in sorted(il_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {il}: {count} hastane")
            
            print("\n🏥 Kurum Tipi Dağılımı:")
            for tip, count in sorted(tip_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"  {tip}: {count} hastane")
                
        else:
            print("❌ Veri işlenemedi.")
            
    except Exception as e:
        logger.error(f"Ana süreç hatası: {e}")
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main()
