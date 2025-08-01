#!/usr/bin/env python3
"""
Supabase Database Client - TURSAKUR 2.0
Supabase veritabanı bağlantısı ve temel operasyonlar için yardımcı modül.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from supabase import create_client, Client
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseManager:
    """Supabase database operations manager"""
    
    def __init__(self):
        """Initialize Supabase client"""
        try:
            self.url = os.getenv('SUPABASE_URL')
            self.key = os.getenv('SUPABASE_KEY')
            
            if not self.url or not self.key:
                raise ValueError("Supabase URL ve KEY çevre değişkenleri gerekli")
                
            self.client: Client = create_client(self.url, self.key)
            logger.info("Supabase client başarıyla oluşturuldu")
            
        except Exception as e:
            logger.error(f"Supabase client oluşturulurken hata: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Test basic connection with a simple query
            result = self.client.table('kuruluslar').select('count', count='exact').limit(1).execute()
            logger.info(f"Veritabanı bağlantısı başarılı. Toplam kayıt: {result.count}")
            return True
        except Exception as e:
            logger.error(f"Veritabanı bağlantı testi başarısız: {e}")
            return False
    
    def insert_institution(self, institution: Dict) -> Optional[Dict]:
        """Insert a single institution"""
        try:
            # Prepare data according to schema
            data = self._prepare_institution_data(institution)
            
            result = self.client.table('kuruluslar').insert(data).execute()
            
            if result.data:
                logger.info(f"Kuruluş başarıyla eklendi: {data.get('isim_standart')}")
                return result.data[0]
            else:
                logger.warning(f"Kuruluş eklenirken veri döndürülmedi: {data.get('isim_standart')}")
                return None
                
        except Exception as e:
            logger.error(f"Kuruluş eklenirken hata: {e}")
            return None
    
    def bulk_insert_institutions(self, institutions: List[Dict], batch_size: int = 100) -> Dict[str, int]:
        """Insert multiple institutions in batches"""
        total = len(institutions)
        inserted = 0
        errors = 0
        
        logger.info(f"Toplu ekleme başlatılıyor: {total} kuruluş, {batch_size} batch boyutu")
        
        for i in range(0, total, batch_size):
            batch = institutions[i:i + batch_size]
            
            try:
                # Prepare batch data
                batch_data = [self._prepare_institution_data(inst) for inst in batch]
                
                # Insert batch
                result = self.client.table('kuruluslar').insert(batch_data).execute()
                
                if result.data:
                    batch_inserted = len(result.data)
                    inserted += batch_inserted
                    logger.info(f"Batch {i//batch_size + 1}: {batch_inserted} kuruluş eklendi")
                else:
                    errors += len(batch)
                    logger.warning(f"Batch {i//batch_size + 1}: Veri döndürülmedi")
                    
            except Exception as e:
                errors += len(batch)
                logger.error(f"Batch {i//batch_size + 1} hatası: {e}")
        
        return {
            'total': total,
            'inserted': inserted,
            'errors': errors,
            'success_rate': (inserted / total * 100) if total > 0 else 0
        }
    
    def upsert_institution(self, institution: Dict) -> Optional[Dict]:
        """Insert or update institution based on external_id"""
        try:
            data = self._prepare_institution_data(institution)
            
            # Use upsert with external_id as conflict resolution
            result = self.client.table('kuruluslar').upsert(
                data,
                on_conflict='external_id'
            ).execute()
            
            if result.data:
                logger.info(f"Kuruluş başarıyla upsert edildi: {data.get('isim_standart')}")
                return result.data[0]
            else:
                logger.warning(f"Upsert sırasında veri döndürülmedi: {data.get('isim_standart')}")
                return None
                
        except Exception as e:
            logger.error(f"Upsert sırasında hata: {e}")
            return None
    
    def get_institution_by_external_id(self, external_id: str) -> Optional[Dict]:
        """Get institution by external_id"""
        try:
            result = self.client.table('kuruluslar').select('*').eq('external_id', external_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"External ID ile kuruluş getirme hatası: {e}")
            return None
    
    def get_institutions_count(self) -> int:
        """Get total count of institutions"""
        try:
            result = self.client.table('kuruluslar').select('count', count='exact').execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Kuruluş sayısı getirme hatası: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            # Total count
            total_result = self.client.table('kuruluslar').select('count', count='exact').execute()
            total_count = total_result.count or 0
            
            # Count by type
            type_result = self.client.table('kuruluslar').select('tip').execute()
            type_counts = {}
            
            if type_result.data:
                for institution in type_result.data:
                    tip = institution.get('tip', 'Diğer')
                    type_counts[tip] = type_counts.get(tip, 0) + 1
            
            # Count by province
            province_result = self.client.table('kuruluslar').select('adres_yapilandirilmis').execute()
            province_counts = {}
            
            if province_result.data:
                for institution in province_result.data:
                    adres = institution.get('adres_yapilandirilmis', {})
                    if isinstance(adres, dict):
                        il = adres.get('il', 'Bilinmeyen')
                        province_counts[il] = province_counts.get(il, 0) + 1
            
            return {
                'total_count': total_count,
                'type_counts': type_counts,
                'province_counts': province_counts,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"İstatistik getirme hatası: {e}")
            return {}
    
    def clear_all_data(self) -> bool:
        """Clear all institutions (use with caution!)"""
        try:
            # Get all IDs first
            result = self.client.table('kuruluslar').select('id').execute()
            
            if not result.data:
                logger.info("Silinecek veri bulunamadı")
                return True
            
            # Delete all records
            delete_result = self.client.table('kuruluslar').delete().neq('id', 0).execute()
            
            logger.info(f"Tüm veriler silindi: {len(result.data)} kayıt")
            return True
            
        except Exception as e:
            logger.error(f"Veri silme hatası: {e}")
            return False
    
    def _prepare_institution_data(self, institution: Dict) -> Dict:
        """Prepare institution data according to database schema"""
        try:
            # Extract coordinates if available
            konum = None
            if 'koordinatlar' in institution:
                koordinatlar = institution['koordinatlar']
                if isinstance(koordinatlar, dict) and 'lat' in koordinatlar and 'lng' in koordinatlar:
                    # PostGIS Point format: POINT(longitude latitude)
                    konum = f"POINT({koordinatlar['lng']} {koordinatlar['lat']})"
                elif isinstance(koordinatlar, list) and len(koordinatlar) >= 2:
                    # Array format [lng, lat]
                    konum = f"POINT({koordinatlar[0]} {koordinatlar[1]})"
            
            # Prepare structured data
            prepared_data = {
                'external_id': str(institution.get('id', '')),
                'isim_standart': institution.get('isim', '').strip(),
                'isim_resmi': institution.get('resmi_isim', institution.get('isim', '')).strip(),
                'tip': institution.get('tip', institution.get('kurum_turu', 'Bilinmeyen')),
                'adres_yapilandirilmis': {
                    'il': institution.get('il', ''),
                    'ilce': institution.get('ilce', ''),
                    'mahalle': institution.get('mahalle', ''),
                    'cadde_sokak': institution.get('adres', ''),
                    'posta_kodu': institution.get('posta_kodu', ''),
                    'tam_adres': institution.get('tam_adres', institution.get('adres', ''))
                },
                'iletisim': {
                    'telefon': institution.get('telefon', ''),
                    'fax': institution.get('fax', ''),
                    'email': institution.get('email', ''),
                    'website': institution.get('website', '')
                },
                'metaveri': {
                    'kaynak': institution.get('kaynak', 'bilinmiyor'),
                    'veri_kalitesi': institution.get('veri_kalitesi', 'orta'),
                    'son_dogrulama': institution.get('son_dogrulama'),
                    'notlar': institution.get('notlar', ''),
                    'orijinal_veri': institution.get('orijinal_veri', {})
                }
            }
            
            # Add geometry if available
            if konum:
                prepared_data['konum'] = konum
            
            # Clean empty values
            prepared_data = self._clean_empty_values(prepared_data)
            
            return prepared_data
            
        except Exception as e:
            logger.error(f"Veri hazırlama hatası: {e}")
            raise
    
    def _clean_empty_values(self, data: Dict) -> Dict:
        """Clean empty string values from nested dictionaries"""
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    cleaned_nested = self._clean_empty_values(value)
                    if cleaned_nested:  # Only add if not empty
                        cleaned[key] = cleaned_nested
                elif isinstance(value, str):
                    if value.strip():  # Only add non-empty strings
                        cleaned[key] = value.strip()
                elif value is not None:  # Add non-None values
                    cleaned[key] = value
            return cleaned
        return data

# Global instance
supabase_manager = SupabaseManager()

def get_supabase_manager() -> SupabaseManager:
    """Get global Supabase manager instance"""
    return supabase_manager

# Convenience functions
def test_connection() -> bool:
    """Test database connection"""
    return supabase_manager.test_connection()

def load_institutions_to_supabase(institutions: List[Dict]) -> Dict[str, int]:
    """Load institutions to Supabase database"""
    return supabase_manager.bulk_insert_institutions(institutions)

def get_database_statistics() -> Dict[str, Any]:
    """Get database statistics"""
    return supabase_manager.get_statistics()

if __name__ == "__main__":
    # Test the connection
    if test_connection():
        print("✅ Supabase bağlantısı başarılı!")
        
        # Show statistics
        stats = get_database_statistics()
        print(f"📊 Veritabanı İstatistikleri:")
        print(f"   Toplam kuruluş: {stats.get('total_count', 0)}")
        print(f"   Tip sayısı: {len(stats.get('type_counts', {}))}")
        print(f"   İl sayısı: {len(stats.get('province_counts', {}))}")
    else:
        print("❌ Supabase bağlantısı başarısız!")
