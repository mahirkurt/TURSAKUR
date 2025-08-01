#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Supabase Veri Yükleme Modülü

Talimatnameler/veri.md'deki Load sürecini uygular.
İşlenmiş, temiz ve tekilleştirilmiş veriyi Supabase PostgreSQL veritabanına aktarır.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd

# Environment variables yükle
load_dotenv()

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/supabase_upload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SupabaseDataLoader:
    """
    Supabase veritabanına veri yükleme sınıfı.
    
    Veri talimatındaki ilkeler:
    - Upsert metoduyla mevcut kayıtları güncelle, yenilerini ekle
    - Kaynak izlenebilirliği koru
    - Coğrafi verileri PostGIS formatında kaydet
    """
    
    def __init__(self):
        """Supabase client'ını başlat."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL ve SUPABASE_KEY environment variables gerekli")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase client başlatıldı")
    
    def standardize_institution_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ham veriyi Supabase şemasına uygun formata dönüştür.
        
        Args:
            raw_data: Mevcut JSON format verisi
            
        Returns:
            Supabase şemasına uygun veri
        """
        try:
            # UUID oluştur (eğer yoksa)
            institution_id = raw_data.get('kurum_id') or str(uuid.uuid4())
            
            # Adres bilgilerini yapılandır
            adres_yapilandirilmis = {
                "tam_adres": raw_data.get('adres', ''),
                "il": raw_data.get('il_adi', ''),
                "ilce": raw_data.get('ilce_adi', ''),
                "mahalle": raw_data.get('mahalle', ''),
                "posta_kodu": raw_data.get('posta_kodu', ''),
                "aciklama": raw_data.get('adres_aciklama', '')
            }
            
            # İletişim bilgilerini yapılandır
            iletisim = {
                "telefon_1": raw_data.get('telefon', ''),
                "telefon_2": raw_data.get('telefon_2', ''),
                "faks": raw_data.get('faks', ''),
                "email": raw_data.get('email', ''),
                "website": raw_data.get('web_sitesi', '')
            }
            
            # Coğrafi konum (PostGIS Point format)
            konum = None
            if raw_data.get('koordinat_lat') and raw_data.get('koordinat_lon'):
                # PostGIS için WKT (Well-Known Text) formatı
                konum = f"POINT({raw_data['koordinat_lon']} {raw_data['koordinat_lat']})"
            
            # Kaynak bilgilerini yapılandır
            kaynaklar = []
            if raw_data.get('veri_kaynagi'):
                kaynaklar.append({
                    "kaynak_id": raw_data.get('veri_kaynagi', 'unknown'),
                    "kaynaktaki_isim": raw_data.get('kurum_adi', ''),
                    "url": raw_data.get('kaynak_url', ''),
                    "son_gorulme_tarihi": datetime.now(timezone.utc).isoformat()
                })
            
            # Meta veri
            meta_veri = {
                "yatak_kapasitesi": raw_data.get('yatak_sayisi'),
                "sgk_anlasmasi": raw_data.get('sgk_anlasmali', False),
                "bolumler": raw_data.get('bolumler', []),
                "logo_url": raw_data.get('logo_url', ''),
                "hizmet_turleri": raw_data.get('hizmet_turleri', [])
            }
            
            # Supabase formatında veri
            supabase_data = {
                "id": institution_id,
                "isim_standart": raw_data.get('kurum_adi', ''),
                "tip": raw_data.get('kurum_tipi', ''),
                "alt_tip": raw_data.get('alt_tip', ''),
                "adres_yapilandirilmis": adres_yapilandirilmis,
                "iletisim": iletisim,
                "konum": konum,
                "kaynaklar": kaynaklar,
                "meta_veri": meta_veri,
                "aktif": True
            }
            
            return supabase_data
            
        except Exception as e:
            logger.error(f"Veri standardizasyonu hatası: {e}")
            raise
    
    def upsert_institutions(self, institutions: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Kurum verilerini Supabase'e upsert et.
        
        Args:
            institutions: Standartlaştırılmış kurum verileri listesi
            
        Returns:
            Başarı istatistikleri
        """
        stats = {"inserted": 0, "updated": 0, "errors": 0}
        
        try:
            logger.info(f"{len(institutions)} kurum verisi işlenmeye başlandı")
            
            # Batch olarak işle (Supabase'in limit'i 1000)
            batch_size = 500
            for i in range(0, len(institutions), batch_size):
                batch = institutions[i:i + batch_size]
                
                try:
                    # Upsert işlemi
                    result = self.client.table('kuruluslar').upsert(
                        batch, 
                        on_conflict='id'
                    ).execute()
                    
                    if result.data:
                        stats["inserted"] += len(result.data)
                        logger.info(f"Batch {i//batch_size + 1} başarıyla işlendi: {len(result.data)} kayıt")
                    
                except Exception as batch_error:
                    logger.error(f"Batch {i//batch_size + 1} hatası: {batch_error}")
                    stats["errors"] += len(batch)
            
            logger.info(f"Veri yükleme tamamlandı: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Upsert işlemi genel hatası: {e}")
            raise
    
    def load_from_json(self, json_file_path: str) -> Dict[str, int]:
        """
        JSON dosyasından veri oku ve Supabase'e yükle.
        
        Args:
            json_file_path: İşlenmiş JSON veri dosyası yolu
            
        Returns:
            Yükleme istatistikleri
        """
        try:
            logger.info(f"JSON dosyası okunuyor: {json_file_path}")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Veri formatını kontrol et
            institutions_raw = data.get('kurumlar', data) if isinstance(data, dict) else data
            
            if not isinstance(institutions_raw, list):
                raise ValueError("Beklenmeyen veri formatı: kurum listesi bulunamadı")
            
            logger.info(f"{len(institutions_raw)} ham kurum verisi bulundu")
            
            # Veriyi standardize et
            institutions_standardized = []
            for raw_institution in institutions_raw:
                try:
                    standardized = self.standardize_institution_data(raw_institution)
                    institutions_standardized.append(standardized)
                except Exception as e:
                    logger.warning(f"Kurum standardizasyon hatası: {e}")
                    continue
            
            logger.info(f"{len(institutions_standardized)} kurum standardize edildi")
            
            # Supabase'e yükle
            return self.upsert_institutions(institutions_standardized)
            
        except Exception as e:
            logger.error(f"JSON yükleme hatası: {e}")
            raise
    
    def validate_schema(self) -> bool:
        """
        Supabase şemasının doğru kurulduğunu kontrol et.
        
        Returns:
            Şema validasyon durumu
        """
        try:
            # Basit bir test sorgusu
            result = self.client.table('kuruluslar').select('id').limit(1).execute()
            logger.info("Supabase şema validasyonu başarılı")
            return True
            
        except Exception as e:
            logger.error(f"Şema validasyon hatası: {e}")
            return False


def main():
    """Ana fonksiyon - mevcut JSON verisini Supabase'e yükle."""
    try:
        loader = SupabaseDataLoader()
        
        # Şema validasyonu
        if not loader.validate_schema():
            logger.error("Supabase şeması doğru kurulmamış. schema.sql'i çalıştırın.")
            return
        
        # Mevcut veriyi yükle
        json_file = "data/turkiye_saglik_kuruluslari_merged.json"
        if os.path.exists(json_file):
            stats = loader.load_from_json(json_file)
            logger.info(f"Veri yükleme başarıyla tamamlandı: {stats}")
        else:
            logger.warning(f"Veri dosyası bulunamadı: {json_file}")
            
    except Exception as e:
        logger.error(f"Ana fonksiyon hatası: {e}")
        raise


if __name__ == "__main__":
    main()
