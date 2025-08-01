#!/usr/bin/env python3
"""
Basit Supabase Bağlantı Testi
Manuel schema deploy sonrası bağlantıyı test eder
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_simple_connection():
    """Basit bağlantı testi"""
    print("🔧 Basit Supabase Bağlantı Testi")
    print("=" * 40)
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        print(f"📡 URL: {url}")
        print(f"🔑 Key: {key[:20] if key else 'None'}...")
        
        if not url or not key:
            print("❌ Environment değişkenleri eksik!")
            return False
            
        # Create client
        supabase: Client = create_client(url, key)
        print("✅ Supabase client oluşturuldu")
        
        # Test connection with health check
        response = supabase.table('kuruluslar').select("kurum_id").limit(1).execute()
        
        if response.data is not None:
            print("✅ Veritabanı bağlantısı başarılı!")
            print(f"📊 İlk kayıt sayısı: {len(response.data)}")
            
            if len(response.data) > 0:
                print(f"🏥 Örnek kurum ID: {response.data[0].get('kurum_id', 'N/A')}")
            
            return True
        else:
            print("⚠️ Bağlantı oldu ama veri yok")
            return False
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        
        if "does not exist" in str(e):
            print("\n💡 Çözüm:")
            print("1. https://supabase.com/dashboard/project/moamwmxcpgjvyyawlygw/sql adresine gidin")
            print("2. Yukarıdaki schema SQL'i yapıştırın ve çalıştırın")
            print("3. Bu scripti tekrar çalıştırın")
            
        elif "Invalid API key" in str(e):
            print("\n💡 API anahtarları kontrol edilmeli")
            
        return False

if __name__ == "__main__":
    test_simple_connection()
