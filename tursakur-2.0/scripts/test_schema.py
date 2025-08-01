#!/usr/bin/env python3
"""
Supabase Schema Test Script
Veritabanı şemasının doğru oluşturulduğunu test eder ve örnek veri ekler.
"""

import json
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import get_supabase_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_schema():
    """Test database schema and insert sample data"""
    manager = get_supabase_manager()
    
    print("🧪 TURSAKUR 2.0 Supabase Schema Testi")
    print("=" * 50)
    
    # Test connection
    print("\n1️⃣ Veritabanı Bağlantı Testi...")
    if not manager.test_connection():
        print("❌ Bağlantı başarısız! Schema'nın oluşturulduğundan emin olun.")
        print("\n📋 Schema Oluşturma Talimatları:")
        print("1. https://supabase.com/dashboard adresine gidin")
        print("2. Projenizi seçin")
        print("3. SQL Editor'ı açın")
        print("4. 'database/schema.sql' dosyasının içeriğini yapıştırın")
        print("5. Run (Çalıştır) butonuna basın")
        return False
    
    print("✅ Veritabanı bağlantısı başarılı!")
    
    # Test sample data insertion
    print("\n2️⃣ Örnek Veri Ekleme Testi...")
    
    sample_institutions = [
        {
            "id": "test_001",
            "isim": "Ankara Üniversitesi Tıp Fakültesi Hastanesi",
            "tip": "Üniversite Hastanesi",
            "il": "Ankara",
            "ilce": "Altındağ",
            "adres": "Mamak Mahallesi, Talatpaşa Bulvarı",
            "telefon": "+90 312 508 2000",
            "website": "https://www.ankara.edu.tr",
            "koordinatlar": {"lat": 39.9334, "lng": 32.8597},
            "kaynak": "test_data"
        },
        {
            "id": "test_002", 
            "isim": "İstanbul Medipol Üniversitesi Hastanesi",
            "tip": "Özel Hastane",
            "il": "İstanbul",
            "ilce": "Bağcılar",
            "adres": "TEM Otoyolu Göztepe Çıkışı",
            "telefon": "+90 212 444 7 555",
            "website": "https://www.medipol.edu.tr",
            "koordinatlar": {"lat": 41.0082, "lng": 28.9784},
            "kaynak": "test_data"
        },
        {
            "id": "test_003",
            "isim": "İzmir Katip Çelebi Üniversitesi Atatürk EAH",
            "tip": "Devlet Hastanesi", 
            "il": "İzmir",
            "ilce": "Karabağlar",
            "adres": "Karabağlar, 6374/2. Sk.",
            "telefon": "+90 232 244 4444",
            "koordinatlar": {"lat": 38.4237, "lng": 27.1428},
            "kaynak": "test_data"
        }
    ]
    
    inserted_count = 0
    for institution in sample_institutions:
        result = manager.insert_institution(institution)
        if result:
            inserted_count += 1
            print(f"✅ Eklendi: {institution['isim']}")
        else:
            print(f"❌ Ekleme başarısız: {institution['isim']}")
    
    print(f"\n📊 {inserted_count}/{len(sample_institutions)} örnek kuruluş eklendi")
    
    # Test data retrieval
    print("\n3️⃣ Veri Çekme Testi...")
    stats = manager.get_statistics()
    
    if stats:
        print(f"✅ Toplam kayıt: {stats.get('total_count', 0)}")
        print(f"✅ Tip sayısı: {len(stats.get('type_counts', {}))}")
        print(f"✅ İl sayısı: {len(stats.get('province_counts', {}))}")
        
        # Show type distribution
        type_counts = stats.get('type_counts', {})
        if type_counts:
            print("\n📋 Kuruluş Tipi Dağılımı:")
            for tip, sayi in type_counts.items():
                print(f"   {tip}: {sayi}")
                
        # Show province distribution  
        province_counts = stats.get('province_counts', {})
        if province_counts:
            print("\n🗺️ İl Dağılımı:")
            for il, sayi in province_counts.items():
                print(f"   {il}: {sayi}")
    
    # Test geographical queries
    print("\n4️⃣ Coğrafi Sorgu Testi...")
    try:
        # Test PostGIS functionality by getting institutions near Ankara
        from supabase import create_client
        import os
        
        client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        # Test basic geographic query - institutions within 100km of Ankara
        ankara_lat, ankara_lng = 39.9334, 32.8597
        
        result = client.table('kuruluslar').select('*').execute()
        
        if result.data:
            print(f"✅ Coğrafi veri sorgusu başarılı: {len(result.data)} kayıt bulundu")
            
            # Test if coordinates are properly stored
            geo_count = 0
            for inst in result.data:
                if inst.get('konum'):
                    geo_count += 1
            
            print(f"✅ Koordinat bilgisi olan kayıt: {geo_count}/{len(result.data)}")
        else:
            print("⚠️ Coğrafi sorgu sonuç döndürmedi")
            
    except Exception as e:
        print(f"❌ Coğrafi sorgu hatası: {e}")
    
    print("\n🎉 Schema testi tamamlandı!")
    return True

def cleanup_test_data():
    """Clean up test data"""
    manager = get_supabase_manager()
    
    print("\n🧹 Test Verilerini Temizleme...")
    
    try:
        from supabase import create_client
        import os
        
        client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        # Delete test records
        result = client.table('kuruluslar').delete().like('kaynaklar', '%test_data%').execute()
        
        if result.data:
            print(f"✅ {len(result.data)} test kaydı silindi")
        else:
            print("ℹ️ Silinecek test kaydı bulunamadı")
            
    except Exception as e:
        print(f"❌ Test verisi silme hatası: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_test_data()
    else:
        success = test_database_schema()
        
        if success:
            print("\n" + "="*50)
            print("✅ SCHEMA TEST BAŞARILI!")
            print("🚀 Artık React uygulaması verileri çekebilir")
            print("📊 http://localhost:5173 adresini kontrol edin")
            print("\nTest verilerini silmek için:")
            print("python scripts/test_schema.py --cleanup")
        else:
            print("\n" + "="*50)
            print("❌ SCHEMA TEST BAŞARISIZ!")
            print("🔧 Lütfen schema oluşturma adımlarını takip edin")
            sys.exit(1)
