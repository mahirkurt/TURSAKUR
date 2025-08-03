#!/usr/bin/env python3
"""
Supabase veritabanı durum kontrolü
"""

import json
from supabase import create_client

def main():
    print("🔍 Supabase Veritabanı Durum Kontrolü")
    print("=" * 50)
    
    # Supabase bağlantısı
    supabase = create_client(
        'https://moamwmxcpgjvyyawlygw.supabase.co',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vYW13bXhjcGdqdnl5YXdseWd3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwMzA1NzgsImV4cCI6MjA2OTYwNjU3OH0.w88NfzOopSYo8Q23ypWaknnaZcSXnV0WPtiE2-ePGfU'
    )
    
    # Test health_facilities tablosu
    print("1. health_facilities tablosu:")
    try:
        result1 = supabase.table('health_facilities').select('*').limit(5).execute()
        print(f"   ✅ Toplam kayıt: {len(result1.data)}")
        if result1.data:
            print(f"   📝 Örnek kayıt: {result1.data[0]}")
    except Exception as e:
        print(f"   ❌ Hata: {e}")
    
    print()
    
    # Test kuruluslar tablosu
    print("2. kuruluslar tablosu:")
    try:
        result2 = supabase.table('kuruluslar').select('*').limit(5).execute()
        print(f"   ✅ Toplam kayıt: {len(result2.data)}")
        if result2.data:
            print(f"   📝 Örnek kayıt: {result2.data[0]}")
    except Exception as e:
        print(f"   ❌ Hata: {e}")
    
    print()
    
    # Mevcut tabloları listele
    print("3. Mevcut tablolar:")
    try:
        # PostgreSQL system catalog sorgusu
        result3 = supabase.rpc('get_table_list').execute()
        print(f"   📋 Bulunan tablolar: {result3.data}")
    except Exception as e:
        print(f"   ⚠️ Tablo listesi alınamadı: {e}")
        print("   💡 Bu normal - RPC fonksiyonu olmayabilir")

if __name__ == "__main__":
    main()
