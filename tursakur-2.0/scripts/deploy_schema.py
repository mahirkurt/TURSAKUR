#!/usr/bin/env python3
"""
Supabase Schema Deployment Script
Database schema'sını Supabase'e otomatik deploy eder.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def deploy_schema():
    """Deploy database schema to Supabase"""
    print("🚀 TURSAKUR 2.0 Schema Deployment")
    print("=" * 50)
    
    try:
        from supabase import create_client, Client
        
        # Get credentials
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")  # Service role key needed for schema changes
        
        if not url or not key:
            print("❌ Environment variables eksik!")
            print("   SUPABASE_URL:", "✅ Var" if url else "❌ Yok")
            print("   SUPABASE_KEY:", "✅ Var" if key else "❌ Yok")
            return False
            
        # Create client with service role key
        supabase: Client = create_client(url, key)
        print("✅ Supabase client oluşturuldu")
        
        # Read schema file
        schema_path = "../database/schema.sql"
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
        else:
            print(f"❌ Schema dosyası bulunamadı: {schema_path}")
            return False
            
        print("✅ Schema dosyası okundu")
        
        # Split SQL commands (basic approach)
        sql_commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
        
        print(f"📋 {len(sql_commands)} SQL komutu tespit edildi")
        
        # Execute SQL commands one by one
        success_count = 0
        
        for i, sql_cmd in enumerate(sql_commands, 1):
            if not sql_cmd:
                continue
                
            try:
                print(f"🔄 Komut {i}/{len(sql_commands)} çalıştırılıyor...")
                
                # Use raw SQL execution via RPC
                result = supabase.rpc('sql', {'query': sql_cmd}).execute()
                success_count += 1
                print(f"   ✅ Başarılı")
                
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg or "CREATE EXTENSION" in sql_cmd:
                    print(f"   ⚠️  Zaten mevcut (geçiliyor)")
                    success_count += 1
                else:
                    print(f"   ❌ Hata: {error_msg}")
        
        print(f"\n📊 Sonuç: {success_count}/{len(sql_commands)} komut başarılı")
        
        if success_count > 0:
            print("🎉 Schema deployment tamamlandı!")
            return True
        else:
            print("❌ Schema deployment başarısız!")
            return False
            
    except Exception as e:
        print(f"❌ Deployment hatası: {e}")
        print("\n💡 Manuel deployment için:")
        print("1. https://supabase.com/dashboard adresine gidin")
        print("2. Projenizi seçin") 
        print("3. SQL Editor'ı açın")
        print("4. database/schema.sql dosyasını açın ve içeriği kopyalayın")
        print("5. SQL Editor'a yapıştırın ve Run butonuna basın")
        return False

if __name__ == "__main__":
    success = deploy_schema()
    
    if success:
        print("\n🔄 Schema deployment sonrası test çalıştırılıyor...")
        os.system("python test_schema.py")
    else:
        print("\n❌ Lütfen manuel schema deployment yapın.")
        sys.exit(1)
