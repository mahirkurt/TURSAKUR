#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Simplified Data Processor
=================================

Toplanan ham verileri işler, temizler ve birleştirir.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
import sys

class SimpleDataProcessor:
    """TURSAKUR ham verilerini işler ve temizler"""
    
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.data_dir = self.scripts_dir.parent / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        
        # Ensure directories exist
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging setup
        log_file = self.data_dir / "processing.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_raw_data(self) -> Dict[str, List[Dict]]:
        """Ham veri dosyalarını yükler"""
        self.logger.info("Ham veriler yükleniyor...")
        
        raw_data = {}
        
        # Raw data directory'deki tüm JSON dosyalarını bul
        json_files = list(self.raw_data_dir.glob("*.json"))
        
        for file_path in json_files:
            source_name = file_path.stem
            self.logger.info(f"Yükleniyor: {source_name}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Veri yapısına göre kayıtları çıkar
                    if isinstance(data, dict):
                        if 'veriler' in data:  # Sağlık Bakanlığı formatı
                            all_records = []
                            for key, records in data['veriler'].items():
                                for record in records:
                                    record['kategori'] = key
                                    all_records.append(record)
                            records = all_records
                        else:
                            records = data.get('kayitlar', data.get('data', data.get('facilities', [])))
                    elif isinstance(data, list):
                        records = data
                    else:
                        self.logger.warning(f"Bilinmeyen veri formatı: {source_name}")
                        records = []
                    
                    raw_data[source_name] = records
                    self.logger.info(f"✅ {source_name}: {len(records)} kayıt yüklendi")
                    
            except Exception as e:
                self.logger.error(f"❌ {source_name} yüklenemedi: {e}")
                raw_data[source_name] = []
        
        total_records = sum(len(records) for records in raw_data.values())
        self.logger.info(f"Toplam ham veri: {total_records:,} kayıt, {len(raw_data)} kaynak")
        
        return raw_data

    def normalize_record(self, raw_record: Dict, source: str) -> Dict:
        """Ham kaydı standart formata dönüştürür"""
        
        # Temel alanları çıkar
        name = (
            raw_record.get('ad') or 
            raw_record.get('name') or 
            raw_record.get('kurum_adi') or 
            raw_record.get('facility_name') or 
            ""
        )
        
        facility_type = (
            raw_record.get('tur') or 
            raw_record.get('type') or 
            raw_record.get('kurum_turu') or 
            raw_record.get('kategori') or
            ""
        )
        
        province = (
            raw_record.get('il') or 
            raw_record.get('province') or 
            raw_record.get('sehir') or
            ""
        )
        
        district = (
            raw_record.get('ilce') or 
            raw_record.get('district') or 
            ""
        )
        
        address = (
            raw_record.get('adres') or 
            raw_record.get('address') or 
            ""
        )
        
        phone = (
            raw_record.get('telefon') or 
            raw_record.get('phone') or 
            ""
        )
        
        website = (
            raw_record.get('website') or 
            raw_record.get('web_site') or 
            ""
        )
        
        # Koordinatlar
        latitude = raw_record.get('enlem') or raw_record.get('latitude')
        longitude = raw_record.get('boylam') or raw_record.get('longitude')
        
        try:
            latitude = float(latitude) if latitude is not None else None
            longitude = float(longitude) if longitude is not None else None
        except (ValueError, TypeError):
            latitude = longitude = None
        
        # Standart kayıt oluştur
        normalized = {
            'name': name.strip() if name else "",
            'facility_type': facility_type.strip() if facility_type else "Sağlık Kuruluşu",
            'province': province.strip() if province else "",
            'district': district.strip() if district else "",
            'address': address.strip() if address else "",
            'phone': phone.strip() if phone else None,
            'website': website.strip() if website else None,
            'latitude': latitude,
            'longitude': longitude,
            'sources': [source],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        return normalized

    def save_processed_data(self, records: List[Dict]):
        """İşlenmiş veriyi kaydeder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Supabase formatında kaydet
        supabase_file = self.processed_data_dir / f"supabase_ready_{timestamp}.json"
        
        with open(supabase_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"İşlenmiş veri kaydedildi: {supabase_file}")
        self.logger.info(f"Toplam kayıt: {len(records)}")

    def process(self) -> bool:
        """Ana işleme fonksiyonu"""
        try:
            self.logger.info("TURSAKUR 2.0 veri işleme başlıyor...")
            
            # 1. Ham verileri yükle
            raw_data = self.load_raw_data()
            if not raw_data:
                self.logger.error("Ham veri bulunamadı!")
                return False
            
            # 2. Tüm kayıtları normalize et
            processed_records = []
            for source, records in raw_data.items():
                for record in records:
                    normalized = self.normalize_record(record, source)
                    if normalized['name']:  # İsmi olan kayıtları al
                        processed_records.append(normalized)
            
            self.logger.info(f"İşlenen kayıt sayısı: {len(processed_records)}")
            
            # 3. Veriyi kaydet
            self.save_processed_data(processed_records)
            
            self.logger.info("✅ Veri işleme başarıyla tamamlandı!")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Veri işleme hatası: {e}")
            return False

def main():
    """Ana fonksiyon"""
    processor = SimpleDataProcessor()
    success = processor.process()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
