#!/usr/bin/env python3
"""
TURSAKUR Supabase Quick Test Script
Hızlı bağlantı ve temel işlevsellik testi
"""

import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Supabase bağlantısını test et"""
    print("🔄 Supabase bağlantısı test ediliyor...")
    
    try:
        from supabase import create_client, Client
        
        # Environment variables
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("❌ Environment variables eksik!")
            print("   SUPABASE_URL:", "✅ Var" if url else "❌ Yok")
            print("   SUPABASE_ANON_KEY:", "✅ Var" if key else "❌ Yok")
            return False
            
        # Create client
        supabase: Client = create_client(url, key)
        print("✅ Supabase client oluşturuldu")
        
        # Test basic connection
        response = supabase.table('kuruluslar').select("count").execute()
        print("✅ Veritabanı bağlantısı başarılı")
        
        return True
        
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False

def test_table_structure():
    """Tablo yapısını test et"""
    print("\n🔄 Tablo yapısı kontrol ediliyor...")
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("❌ SUPABASE_URL veya SUPABASE_ANON_KEY environment variable'ları bulunamadı")
            return False
            
        supabase: Client = create_client(url, key)
        
        # Test select query
        response = supabase.table('kuruluslar').select("*").limit(1).execute()
        
        if response.data:
            print("✅ Kuruluslar tablosu erişilebilir")
            print(f"   Örnek kayıt: {len(response.data)} adet")
        else:
            print("⚠️  Kuruluslar tablosu boş")
            
        return True
        
    except Exception as e:
        print(f"❌ Tablo hatası: {e}")
        if "does not exist" in str(e):
            print("   💡 Schema henüz deploy edilmemiş olabilir")
        return False

def test_sample_insert():
    """Örnek veri ekleme testi"""
    print("\n🔄 Örnek veri ekleme test ediliyor...")
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("❌ Environment variables bulunamadı")
            return False
            
        supabase: Client = create_client(url, key)
        
        # Test data
        test_data = {
            "kurum_id": "TR-TEST-001",
            "kurum_adi": "Test Sağlık Ocağı",
            "kurum_tipi": "Sağlık Ocağı",
            "il_adi": "İstanbul",
            "ilce_adi": "Kadıköy",
            "koordinat_lat": 40.9926,
            "koordinat_lon": 29.0284,
            "veri_kaynagi": "Test Script"
        }
        
        # Insert test data
        response = supabase.table('kuruluslar').upsert(test_data).execute()
        
        if response.data:
            print("✅ Test verisi başarıyla eklendi")
            print(f"   Kayıt ID: {response.data[0]['kurum_id']}")
        else:
            print("⚠️  Veri ekleme yanıt vermedi")
            
        return True
        
    except Exception as e:
        print(f"❌ Veri ekleme hatası: {e}")
        return False

def test_geographic_query():
    """Coğrafi sorgu testi"""
    print("\n🔄 Coğrafi sorgu test ediliyor...")
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("❌ Environment variables bulunamadı")
            return False
            
        supabase: Client = create_client(url, key)
        
        # Test geographic function (if available)
        response = supabase.rpc('search_within_radius', {
            'center_lat': 41.0082,
            'center_lon': 28.9784,
            'radius_meters': 50000
        }).execute()
        
        print("✅ Coğrafi fonksiyon çalışıyor")
        print(f"   Bulunan kurum sayısı: {len(response.data) if response.data else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Coğrafi sorgu hatası: {e}")
        if "does not exist" in str(e):
            print("   💡 Coğrafi fonksiyon henüz oluşturulmamış")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 TURSAKUR Supabase Hızlı Test")
    print("=" * 40)
    
    # Check dependencies
    try:
        import supabase
        print("✅ Supabase library kurulu")
    except ImportError:
        print("❌ Supabase library bulunamadı")
        print("   Kurulum: pip install supabase")
        return
    
    # Run tests
    tests = [
        ("Bağlantı Testi", test_supabase_connection),
        ("Tablo Yapısı", test_table_structure),
        ("Veri Ekleme", test_sample_insert),
        ("Coğrafi Sorgu", test_geographic_query)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} beklenmeyen hata: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST SONUÇLARI:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Toplam: {passed}/{len(results)} test başarılı")
    
    if passed == len(results):
        print("🎉 Tüm testler başarılı! Supabase entegrasyonu hazır.")
    else:
        print("⚠️  Bazı testler başarısız. Lütfen yukarıdaki hataları inceleyin.")

if __name__ == "__main__":
    main()
