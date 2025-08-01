#!/usr/bin/env python3
"""
Data Loading Script for TURSAKUR 2.0 Supabase Migration
Mevcut JSON verilerini Supabase veritabanına yükler.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from scripts.supabase_client import get_supabase_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataMigrationManager:
    """Manages data migration from JSON files to Supabase"""
    
    def __init__(self):
        self.supabase = get_supabase_manager()
        self.data_dir = Path(__file__).parent.parent / 'data'
        
    def load_json_file(self, filename: str) -> List[Dict]:
        """Load institutions from JSON file"""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            logger.error(f"Dosya bulunamadı: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                logger.info(f"JSON dosyası yüklendi: {filename} - {len(data)} kayıt")
                return data
            elif isinstance(data, dict):
                # If it's a dict, try to extract institutions array
                if 'institutions' in data:
                    institutions = data['institutions']
                    logger.info(f"JSON dosyası yüklendi: {filename} - {len(institutions)} kayıt")
                    return institutions
                elif 'data' in data:
                    institutions = data['data']
                    logger.info(f"JSON dosyası yüklendi: {filename} - {len(institutions)} kayıt")
                    return institutions
                else:
                    # Assume the dict itself is an institution
                    logger.info(f"JSON dosyası yüklendi: {filename} - 1 kayıt")
                    return [data]
            else:
                logger.warning(f"Beklenmeyen veri formatı: {type(data)}")
                return []
                
        except Exception as e:
            logger.error(f"JSON dosyası okuma hatası: {e}")
            return []
    
    def migrate_main_dataset(self) -> Dict[str, int]:
        """Migrate main turkiye_saglik_kuruluslari.json dataset"""
        logger.info("=== Ana veri kümesi migrasyonu başlatılıyor ===")
        
        # Try different possible filenames
        possible_files = [
            'turkiye_saglik_kuruluslari.json',
            'turkiye_saglik_kuruluslari_merged.json',
            'turkey_geo_data.json'
        ]
        
        institutions = []
        for filename in possible_files:
            file_institutions = self.load_json_file(filename)
            if file_institutions:
                institutions.extend(file_institutions)
                logger.info(f"✅ {filename} dosyasından {len(file_institutions)} kuruluş yüklendi")
        
        if not institutions:
            logger.error("❌ Hiçbir veri dosyası bulunamadı!")
            return {'total': 0, 'inserted': 0, 'errors': 0, 'success_rate': 0}
        
        # Remove duplicates based on a unique field
        unique_institutions = []
        seen_ids = set()
        seen_names = set()
        
        for inst in institutions:
            # Create unique identifier
            unique_id = inst.get('id') or inst.get('external_id')
            name = inst.get('isim', '').strip().lower()
            
            if unique_id and unique_id not in seen_ids:
                seen_ids.add(unique_id)
                unique_institutions.append(inst)
            elif name and name not in seen_names:
                seen_names.add(name)
                unique_institutions.append(inst)
        
        logger.info(f"📊 Toplam: {len(institutions)}, Benzersiz: {len(unique_institutions)}")
        
        # Migrate to Supabase
        return self.supabase.bulk_insert_institutions(unique_institutions)
    
    def migrate_backup_data(self) -> Dict[str, int]:
        """Migrate backup data if available"""
        logger.info("=== Yedek veri migrasyonu kontrol ediliyor ===")
        
        backup_dir = self.data_dir / 'backup'
        if not backup_dir.exists():
            logger.info("Yedek klasörü bulunamadı, atlanıyor.")
            return {'total': 0, 'inserted': 0, 'errors': 0, 'success_rate': 0}
        
        total_results = {'total': 0, 'inserted': 0, 'errors': 0}
        
        # Look for JSON files in backup directory
        for json_file in backup_dir.glob('*.json'):
            logger.info(f"Yedek dosya işleniyor: {json_file.name}")
            
            institutions = self.load_json_file(f'backup/{json_file.name}')
            if institutions:
                # Use upsert for backup data to avoid duplicates
                for inst in institutions:
                    result = self.supabase.upsert_institution(inst)
                    total_results['total'] += 1
                    if result:
                        total_results['inserted'] += 1
                    else:
                        total_results['errors'] += 1
        
        if total_results['total'] > 0:
            total_results['success_rate'] = (total_results['inserted'] / total_results['total']) * 100
        
        return total_results
    
    def verify_migration(self) -> Dict[str, any]:
        """Verify migration success"""
        logger.info("=== Migrasyon doğrulaması ===")
        
        try:
            stats = self.supabase.get_statistics()
            
            verification = {
                'total_records': stats.get('total_count', 0),
                'types_found': len(stats.get('type_counts', {})),
                'provinces_found': len(stats.get('province_counts', {})),
                'top_types': dict(sorted(
                    stats.get('type_counts', {}).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]),
                'top_provinces': dict(sorted(
                    stats.get('province_counts', {}).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10])
            }
            
            logger.info(f"✅ Toplam kayıt: {verification['total_records']}")
            logger.info(f"✅ Kuruluş tipi sayısı: {verification['types_found']}")
            logger.info(f"✅ İl sayısı: {verification['provinces_found']}")
            
            return verification
            
        except Exception as e:
            logger.error(f"Doğrulama hatası: {e}")
            return {}
    
    def run_full_migration(self) -> Dict[str, any]:
        """Run complete migration process"""
        logger.info("🚀 TURSAKUR 2.0 Veri Migrasyonu Başlatılıyor")
        
        # Test connection first
        if not self.supabase.test_connection():
            logger.error("❌ Veritabanı bağlantısı başarısız, migrasyon durduruluyor")
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            # Main migration
            main_results = self.migrate_main_dataset()
            logger.info(f"Ana veri migrasyonu tamamlandı: {main_results}")
            
            # Backup migration
            backup_results = self.migrate_backup_data()
            if backup_results['total'] > 0:
                logger.info(f"Yedek veri migrasyonu tamamlandı: {backup_results}")
            
            # Verification
            verification = self.verify_migration()
            
            # Summary
            summary = {
                'success': True,
                'main_migration': main_results,
                'backup_migration': backup_results,
                'verification': verification,
                'timestamp': self.supabase.get_statistics().get('last_updated')
            }
            
            logger.info("🎉 Migrasyon başarıyla tamamlandı!")
            return summary
            
        except Exception as e:
            logger.error(f"Migrasyon hatası: {e}")
            return {'success': False, 'error': str(e)}

def main():
    """Main execution function"""
    print("🔄 TURSAKUR 2.0 Supabase Veri Migrasyonu")
    print("=" * 50)
    
    # Initialize migration manager
    migration_manager = DataMigrationManager()
    
    # Run migration
    results = migration_manager.run_full_migration()
    
    # Display results
    if results.get('success'):
        print("\n✅ MİGRASYON BAŞARILI!")
        print(f"📊 Ana veri: {results['main_migration']['inserted']} kayıt eklendi")
        
        if results['backup_migration']['total'] > 0:
            print(f"💾 Yedek veri: {results['backup_migration']['inserted']} kayıt eklendi")
        
        verification = results.get('verification', {})
        print(f"🏥 Toplam kuruluş: {verification.get('total_records', 0)}")
        print(f"🏛️ Kuruluş tipi: {verification.get('types_found', 0)}")
        print(f"🗺️ İl sayısı: {verification.get('provinces_found', 0)}")
        
        # Show top types
        if verification.get('top_types'):
            print("\n📋 En çok kuruluş tipi:")
            for tip, sayi in list(verification['top_types'].items())[:5]:
                print(f"   {tip}: {sayi}")
                
    else:
        print(f"\n❌ MİGRASYON BAŞARISIZ: {results.get('error')}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
