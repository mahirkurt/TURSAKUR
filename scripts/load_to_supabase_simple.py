#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Supabase Data Loader
===================================

İşlenmiş veriyi Supabase PostgreSQL veritabanına yükler.
"""

import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Supabase client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("❌ Supabase client yüklü değil. 'pip install supabase' çalıştırın.")

# Environment variables
from dotenv import load_dotenv
load_dotenv()

class SupabaseLoader:
    """Supabase'e veri yükleme sınıfı"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.processed_dir = self.data_dir / "processed"
        
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.data_dir / "supabase_loading.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Supabase configuration
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not SUPABASE_AVAILABLE:
            self.logger.error("Supabase client mevcut değil!")
            return
        
        if not self.supabase_url or not self.supabase_key:
            self.logger.warning("Supabase credentials bulunamadı. Test modu çalışıyor.")
            self.supabase = None
        else:
            try:
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                self.logger.info("✅ Supabase client başlatıldı")
            except Exception as e:
                self.logger.error(f"Supabase client başlatılamadı: {e}")
                self.supabase = None

    def load_processed_data(self) -> List[Dict]:
        """En son işlenmiş veriyi yükler"""
        # En son processed dosyayı bul
        json_files = list(self.processed_dir.glob("tursakur_processed_*.json"))
        
        if not json_files:
            self.logger.error("İşlenmiş veri dosyası bulunamadı!")
            return []
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        self.logger.info(f"Yükleniyor: {latest_file}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Facilities array'ini çıkar
            facilities = data.get('facilities', [])
            self.logger.info(f"Yüklenen kayıt sayısı: {len(facilities)}")
            
            return facilities
            
        except Exception as e:
            self.logger.error(f"Veri yükleme hatası: {e}")
            return []

    def create_table_schema(self):
        """Supabase'de tablo şemasını oluşturur"""
        if not self.supabase:
            self.logger.info("📋 Test modu - Tablo şeması:")
            schema_sql = """
            CREATE TABLE IF NOT EXISTS health_facilities (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                facility_type TEXT,
                province TEXT,
                district TEXT,
                address TEXT,
                phone TEXT,
                website TEXT,
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                sources TEXT[],
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            
            -- Indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_health_facilities_province ON health_facilities(province);
            CREATE INDEX IF NOT EXISTS idx_health_facilities_type ON health_facilities(facility_type);
            CREATE INDEX IF NOT EXISTS idx_health_facilities_location ON health_facilities(latitude, longitude);
            """
            print(schema_sql)
            return True
        
        # Supabase SQL execution (requires RPC or direct SQL access)
        self.logger.info("✅ Tablo şeması hazır (manuel oluşturulmalı)")
        return True

    def transform_for_supabase(self, facilities: List[Dict]) -> List[Dict]:
        """Veriyi Supabase formatına dönüştürür"""
        transformed = []
        
        for facility in facilities:
            # Supabase record format
            record = {
                'name': facility.get('name', ''),
                'facility_type': facility.get('facility_type', ''),
                'province': facility.get('province', ''),
                'district': facility.get('district', ''),
                'address': facility.get('address', ''),
                'phone': facility.get('phone'),
                'website': facility.get('website'),
                'latitude': facility.get('latitude'),
                'longitude': facility.get('longitude'),
                'sources': facility.get('sources', [facility.get('source', 'unknown')]),
                'created_at': facility.get('created_at', datetime.now(timezone.utc).isoformat()),
                'updated_at': facility.get('updated_at', datetime.now(timezone.utc).isoformat())
            }
            
            # Null değerleri temizle
            record = {k: v for k, v in record.items() if v is not None and v != ''}
            
            # Ensure required fields
            if record.get('name') and record.get('province'):
                transformed.append(record)
        
        self.logger.info(f"Transformation: {len(facilities)} -> {len(transformed)} kayıt")
        return transformed

    def upload_to_supabase(self, records: List[Dict]) -> bool:
        """Veriyi Supabase'e yükler"""
        if not self.supabase:
            self.logger.info("📤 Test modu - Supabase upload simülasyonu")
            self.logger.info(f"Yüklenecek kayıt sayısı: {len(records)}")
            
            # İlk 3 kaydı göster
            for i, record in enumerate(records[:3]):
                self.logger.info(f"Örnek kayıt {i+1}: {record['name']} - {record['province']}")
            
            self.logger.info("✅ Test upload başarılı")
            return True
        
        try:
            # Batch upload (Supabase 1000 kayıt limitı)
            batch_size = 1000
            total_uploaded = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                # Upsert operation
                result = self.supabase.table('health_facilities').upsert(
                    batch, 
                    on_conflict='name,province'  # Duplicate prevention
                ).execute()
                
                if result.data:
                    total_uploaded += len(batch)
                    self.logger.info(f"✅ Batch {i//batch_size + 1}: {len(batch)} kayıt yüklendi")
                else:
                    self.logger.error(f"❌ Batch {i//batch_size + 1} upload başarısız")
            
            self.logger.info(f"🎉 Toplam {total_uploaded} kayıt Supabase'e yüklendi!")
            return True
            
        except Exception as e:
            self.logger.error(f"Supabase upload hatası: {e}")
            return False

    def run(self) -> bool:
        """Ana yükleme fonksiyonu"""
        self.logger.info("🚀 Supabase veri yükleme başlatılıyor...")
        
        try:
            # 1. İşlenmiş veriyi yükle
            facilities = self.load_processed_data()
            if not facilities:
                return False
            
            # 2. Tablo şemasını kontrol et
            self.create_table_schema()
            
            # 3. Veriyi transform et
            records = self.transform_for_supabase(facilities)
            if not records:
                self.logger.error("Transform edilebilir kayıt bulunamadı!")
                return False
            
            # 4. Supabase'e yükle
            success = self.upload_to_supabase(records)
            
            if success:
                self.logger.info("✅ Supabase veri yükleme tamamlandı!")
            else:
                self.logger.error("❌ Supabase veri yükleme başarısız!")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Genel hata: {e}")
            return False

def main():
    """Ana fonksiyon"""
    loader = SupabaseLoader()
    success = loader.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
