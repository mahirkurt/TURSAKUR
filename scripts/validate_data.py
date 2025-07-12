#!/usr/bin/env python3
"""
Türkiye Sağlık Kuruluşları - Veri Doğrulama Betiği
Bu betik, raw klasöründeki JSON verilerinin şemaya uygunluğunu kontrol eder.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import logging

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Geçerli kurum tipleri (process edilmiş ana veri için)
VALID_KURUM_TIPLERI = [
    "Devlet Hastanesi",
    "Üniversite Hastanesi", 
    "Eğitim ve Araştırma Hastanesi",
    "Özel Hastane",
    "Aile Sağlığı Merkezi",
    "Toplum Sağlığı Merkezi",
    "Ağız ve Diş Sağlığı Merkezi",
    "Özel Poliklinik",
    "Özel Tıp Merkezi",
    "Diyaliz Merkezi",
    "Fizik Tedavi ve Rehabilitasyon Merkezi",
    "Ambulans İstasyonu"
]

# Raw veri için gevşek validasyon kuralları
RAW_DATA_VALIDATION = True

def validate_kurum_data(data: Dict[str, Any], is_raw: bool = False) -> List[str]:
    """Tek bir kurum verisini doğrular."""
    errors = []
    
    # Raw veri için daha az katı kurallar
    if is_raw:
        # Raw veri için sadece temel kontroller
        required_fields = ['kurum_adi', 'kurum_tipi']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Temel alan eksik: {field}")
        
        # Raw veri için kurum tipi kontrolü yapma (çünkü normalize edilecek)
        return errors
    
    # Ana veri için katı kurallar
    required_fields = [
        'kurum_id', 'kurum_adi', 'kurum_tipi', 'il_kodu', 
        'il_adi', 'ilce_adi', 'adres', 'son_guncelleme'
    ]
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Zorunlu alan eksik: {field}")
        elif not data[field]:
            errors.append(f"Boş alan: {field}")
    
    # Kurum ID formatı kontrolü
    if 'kurum_id' in data:
        kurum_id = data['kurum_id']
        if not kurum_id.startswith('TR-'):
            errors.append(f"Geçersiz kurum_id formatı: {kurum_id}")
    
    # İl kodu kontrolü
    if 'il_kodu' in data:
        try:
            il_kodu = int(data['il_kodu'])
            if not 1 <= il_kodu <= 81:
                errors.append(f"Geçersiz il_kodu: {il_kodu}")
        except (ValueError, TypeError):
            errors.append(f"İl kodu sayısal olmalı: {data['il_kodu']}")
    
    # Kurum tipi kontrolü
    if 'kurum_tipi' in data:
        if data['kurum_tipi'] not in VALID_KURUM_TIPLERI:
            errors.append(f"Geçersiz kurum_tipi: {data['kurum_tipi']}")
    
    # Telefon formatı kontrolü
    if 'telefon' in data and data['telefon']:
        telefon = data['telefon']
        if not telefon.startswith('+90'):
            errors.append(f"Telefon +90 ile başlamalı: {telefon}")
    
    # Koordinat kontrolü
    if 'koordinat_lat' in data and data['koordinat_lat']:
        try:
            lat = float(data['koordinat_lat'])
            if not 35.8 <= lat <= 42.1:  # Türkiye'nin kabaca enlem aralığı
                errors.append(f"Geçersiz enlem: {lat}")
        except (ValueError, TypeError):
            errors.append(f"Enlem sayısal olmalı: {data['koordinat_lat']}")
    
    if 'koordinat_lon' in data and data['koordinat_lon']:
        try:
            lon = float(data['koordinat_lon'])
            if not 25.7 <= lon <= 44.8:  # Türkiye'nin kabaca boylam aralığı
                errors.append(f"Geçersiz boylam: {lon}")
        except (ValueError, TypeError):
            errors.append(f"Boylam sayısal olmalı: {data['koordinat_lon']}")
    
    # Tarih formatı kontrolü
    if 'son_guncelleme' in data:
        try:
            datetime.strptime(data['son_guncelleme'], '%Y-%m-%d')
        except ValueError:
            errors.append(f"Geçersiz tarih formatı: {data['son_guncelleme']}")
    
    return errors

def validate_json_file(file_path: str) -> bool:
    """Bir JSON dosyasını doğrular."""
    logger.info(f"Doğrulanıyor: {file_path}")
    
    # Ana veritabanı dosyası mı yoksa raw veri mi?
    is_raw = "/raw/" in file_path.replace("\\", "/")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ana veri dosyası için özel yapı kontrolü
        if file_path.endswith("turkiye_saglik_kuruluslari.json"):
            if 'kurumlar' not in data:
                logger.error(f"Ana veri dosyasında 'kurumlar' anahtarı bulunamadı")
                return False
            kurumlar = data['kurumlar']
        # Tek kurum verisi mi yoksa liste mi?
        elif isinstance(data, list):
            kurumlar = data
        else:
            kurumlar = [data]
        
        total_errors = 0
        for i, kurum in enumerate(kurumlar):
            errors = validate_kurum_data(kurum, is_raw=is_raw)
            if errors:
                logger.error(f"Dosya: {file_path}, Kurum {i+1}:")
                for error in errors:
                    logger.error(f"  - {error}")
                total_errors += len(errors)
        
        if total_errors == 0:
            logger.info(f"✅ {file_path} - Doğrulama başarılı")
            return True
        else:
            if is_raw:
                logger.warning(f"⚠️ {file_path} - {total_errors} uyarı (raw veri)")
                return True  # Raw veri için uyarıları hata saymıyoruz
            else:
                logger.error(f"❌ {file_path} - {total_errors} hata bulundu")
                return False
    
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON format hatası - {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Dosya okuma hatası - {file_path}: {e}")
        return False

def main():
    """Ana fonksiyon - tüm dosyaları doğrular."""
    # Önce ana veri dosyasını kontrol et
    main_data_file = "data/turkiye_saglik_kuruluslari.json"
    
    successful = 0
    failed = 0
    
    if os.path.exists(main_data_file):
        logger.info("Ana veri dosyası kontrol ediliyor...")
        if validate_json_file(main_data_file):
            successful += 1
        else:
            failed += 1
    
    # Sonra raw dosyaları kontrol et
    raw_dir = "data/raw"
    
    if os.path.exists(raw_dir):
        json_files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]
        
        if json_files:
            logger.info(f"Raw klasöründe {len(json_files)} JSON dosyası bulundu")
            
            for json_file in json_files:
                file_path = os.path.join(raw_dir, json_file)
                if validate_json_file(file_path):
                    successful += 1
                else:
                    failed += 1
    
    logger.info(f"\n=== SONUÇ ===")
    logger.info(f"✅ Başarılı: {successful}")
    logger.info(f"❌ Başarısız: {failed}")
    
    if failed > 0:
        logger.error("Bazı dosyalarda kritik hatalar bulundu!")
        sys.exit(1)
    else:
        logger.info("Tüm dosyalar doğrulama testini geçti!")

if __name__ == "__main__":
    main()
