#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Test Verisi Oluşturucu
=====================================

Supabase entegrasyonu için test verisi oluşturur.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

class TestDataGenerator:
    """Test verisi oluşturucu"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data" / "raw"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_sample_hospitals(self, count: int = 50) -> List[Dict]:
        """Örnek hastane verisi oluşturur"""
        
        provinces = [
            'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya', 'Gaziantep',
            'Mersin', 'Diyarbakır', 'Kayseri', 'Eskişehir', 'Urfa', 'Malatya', 'Erzurum',
            'Van', 'Batman', 'Elazığ', 'Denizli', 'Sivas', 'Çorum', 'Aydın'
        ]
        
        hospital_types = [
            'Devlet Hastanesi', 'Üniversite Hastanesi', 'Özel Hastane', 
            'Eğitim ve Araştırma Hastanesi', 'Şehir Hastanesi', 'Dal Hastanesi'
        ]
        
        hospital_names = [
            'Devlet Hastanesi', 'Şehir Hastanesi', 'Üniversite Hastanesi',
            'Eğitim ve Araştırma Hastanesi', 'Kadın Doğum Hastanesi',
            'Çocuk Hastanesi', 'Göğüs Hastalıkları Hastanesi', 'Kalp Hastanesi',
            'Onkoloji Hastanesi', 'Fizik Tedavi Hastanesi'
        ]
        
        hospitals = []
        
        for i in range(count):
            province = provinces[i % len(provinces)]
            hospital_type = hospital_types[i % len(hospital_types)]
            base_name = hospital_names[i % len(hospital_names)]
            
            # Koordinatlar (Türkiye sınırları içinde)
            lat = 36.0 + (i % 7) * 1.2  # 36-42 arası
            lng = 26.0 + (i % 15) * 1.3  # 26-45 arası
            
            hospital = {
                'ad': f"{province} {base_name}",
                'tur': hospital_type,
                'il': province,
                'ilce': f"Merkez" if i % 3 == 0 else f"İlçe {i % 5 + 1}",
                'adres': f"{province} ili, örnek adres {i + 1}",
                'telefon': f"0312 {400 + i:03d} {10 + i % 90:02d} {i % 100:02d}",
                'website': f"https://www.{province.lower()}-hastane{i}.gov.tr",
                'latitude': round(lat, 6),
                'longitude': round(lng, 6),
                'kaynak': 'test_data',
                'aktif': True,
                'yatak_sayisi': 50 + (i * 10) % 500,
                'acil_servis': i % 3 == 0,
                'yoğun_bakim': i % 4 == 0
            }
            
            hospitals.append(hospital)
        
        return hospitals

    def generate_test_files(self):
        """Test veri dosyalarını oluşturur"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Sağlık Bakanlığı test verisi
        saglik_bakanligi_data = {
            'kaynak': 'T.C. Sağlık Bakanlığı (Test)',
            'tier': 1,
            'cekme_tarihi': datetime.now(timezone.utc).isoformat(),
            'toplam_kayit': 30,
            'kayitlar': self.generate_sample_hospitals(30)
        }
        
        saglik_file = self.data_dir / f"saglik_bakanligi_{timestamp}.json"
        with open(saglik_file, 'w', encoding='utf-8') as f:
            json.dump(saglik_bakanligi_data, f, ensure_ascii=False, indent=2)
        
        # SGK test verisi
        sgk_data = {
            'kaynak': 'SGK Anlaşmalı Kurumlar (Test)',
            'tier': 1,
            'cekme_tarihi': datetime.now(timezone.utc).isoformat(),
            'toplam_kayit': 25,
            'kayitlar': self.generate_sample_hospitals(25)
        }
        
        sgk_file = self.data_dir / f"sgk_anlasmali_{timestamp}.json"
        with open(sgk_file, 'w', encoding='utf-8') as f:
            json.dump(sgk_data, f, ensure_ascii=False, indent=2)
        
        # Üniversite hastaneleri test verisi
        university_hospitals = []
        for i in range(15):
            hospital = self.generate_sample_hospitals(1)[0]
            hospital['ad'] = hospital['ad'].replace('Devlet Hastanesi', 'Üniversite Hastanesi')
            hospital['tur'] = 'Üniversite Hastanesi'
            hospital['universite'] = f"Test Üniversitesi {i + 1}"
            university_hospitals.append(hospital)
        
        uni_data = {
            'kaynak': 'Üniversite Hastaneleri (Test)',
            'tier': 1,
            'cekme_tarihi': datetime.now(timezone.utc).isoformat(),
            'toplam_kayit': 15,
            'kayitlar': university_hospitals
        }
        
        uni_file = self.data_dir / f"universite_hastaneleri_{timestamp}.json"
        with open(uni_file, 'w', encoding='utf-8') as f:
            json.dump(uni_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Test veri dosyaları oluşturuldu:")
        self.logger.info(f"  - {saglik_file}")
        self.logger.info(f"  - {sgk_file}")
        self.logger.info(f"  - {uni_file}")
        
        return [saglik_file, sgk_file, uni_file]

def main():
    """Ana fonksiyon"""
    generator = TestDataGenerator()
    files = generator.generate_test_files()
    print(f"✅ {len(files)} test veri dosyası oluşturuldu")
    return True

if __name__ == "__main__":
    main()
