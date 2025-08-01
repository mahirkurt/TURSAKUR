#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Test Data Generator
=================================

Development ve test amaçlı örnek sağlık kuruluşu verisi oluşturur.
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

def create_test_data():
    """Test verisi oluşturur"""
    
    # Test data directory
    scripts_dir = Path(__file__).parent
    data_dir = scripts_dir.parent / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Örnek iller ve kuruluş türleri
    provinces = [
        "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", 
        "Adana", "Konya", "Gaziantep", "Kayseri", "Mersin"
    ]
    
    facility_types = [
        "Devlet Hastanesi", "Özel Hastane", "Üniversite Hastanesi",
        "Aile Sağlık Merkezi", "Poliklinik", "Sağlık Ocağı",
        "Tıp Merkezi", "Diyaliz Merkezi"
    ]
    
    # Test facilities oluştur
    test_facilities = []
    
    for i in range(100):
        province = random.choice(provinces)
        facility_type = random.choice(facility_types)
        
        facility = {
            "ad": f"{province} {facility_type} {i+1}",
            "tur": facility_type,
            "il": province,
            "ilce": f"{province} Merkez",
            "adres": f"Test Mahallesi, Test Sokak No:{i+1}, {province}",
            "telefon": f"0312{random.randint(100, 999)}{random.randint(1000, 9999)}",
            "website": f"https://hastane{i+1}.saglik.gov.tr",
            "enlem": 39.9334 + random.uniform(-5, 5),
            "boylam": 32.8597 + random.uniform(-10, 10),
            "kaynak": "test_data",
            "tarih": datetime.now(timezone.utc).isoformat()
        }
        
        test_facilities.append(facility)
    
    # Sağlık Bakanlığı formatında kaydet
    saglik_bakanligi_data = {
        'kaynak': 'T.C. Sağlık Bakanlığı (Test Data)',
        'tier': 1,
        'cekme_tarihi': datetime.now(timezone.utc).isoformat(),
        'toplam_kayit': len(test_facilities),
        'veriler': {
            'devlet_hastaneleri': test_facilities[:50],
            'ozel_hastaneler': test_facilities[50:80],
            'asm_merkezleri': test_facilities[80:],
            'il_saglik_mudurlukleri': []
        },
        'meta': {
            'endpoints': {'test': 'test'},
            'scraper_version': '2.0-test',
            'veri_tipi': 'test_saglik_kurumlari'
        }
    }
    
    # Dosyaya kaydet
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"saglik_bakanligi_{timestamp}.json"
    filepath = data_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(saglik_bakanligi_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Test verisi oluşturuldu: {filepath}")
    print(f"📊 Toplam kayıt: {len(test_facilities)}")
    
    return filepath

if __name__ == "__main__":
    create_test_data()
