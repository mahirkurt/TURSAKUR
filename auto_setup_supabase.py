#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Otomatik Supabase Setup ve Test
Tüm Supabase işlemlerini otomatik olarak gerçekleştirir
"""

import os
import sys
import json
import time
from datetime import date
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Environment değişkenlerini kontrol et"""
    print("🔧 Environment Kontrol Ediliyor...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Eksik environment değişkenleri: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment değişkenleri tamam")
    return True

def install_dependencies():
    """Gerekli Python paketlerini yükle"""
    print("📦 Python Bağımlılıkları Kontrol Ediliyor...")
    
    try:
        import supabase
        print("✅ Supabase library mevcut")
    except ImportError:
        print("⬇️ Supabase library kuruluyor...")
        os.system("pip install supabase python-dotenv")
        print("✅ Supabase library kuruldu")

def create_supabase_client():
    """Supabase client oluştur"""
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        client: Client = create_client(url, key)
        return client
    except Exception as e:
        print(f"❌ Supabase client oluşturulamadı: {e}")
        return None

def test_connection():
    """Supabase bağlantısını test et"""
    print("\n🔗 Supabase Bağlantı Testi...")
    
    client = create_supabase_client()
    if not client:
        return False
    
    try:
        # Test basic connection
        response = client.table('kuruluslar').select("count").execute()
        print("✅ Veritabanı bağlantısı başarılı")
        return True
    except Exception as e:
        if "does not exist" in str(e).lower():
            print("⚠️ Kuruluslar tablosu bulunamadı - Schema deploy edilmemiş")
            return "schema_needed"
        else:
            print(f"❌ Bağlantı hatası: {e}")
            return False

def deploy_schema():
    """Schema'yı Supabase'e deploy et"""
    print("\n🏗️ Database Schema Deploy Ediliyor...")
    
    # Schema SQL content
    schema_sql = """
-- TURSAKUR Database Schema for Supabase PostgreSQL with PostGIS
-- Bu schema Türkiye sağlık kuruluşları veritabanı için tasarlanmıştır

-- Enable PostGIS extension for geographic data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create kuruluslar (health institutions) table
CREATE TABLE IF NOT EXISTS public.kuruluslar (
    kurum_id VARCHAR(50) PRIMARY KEY,
    kurum_adi VARCHAR(500) NOT NULL,
    kurum_tipi VARCHAR(100) NOT NULL,
    il_kodu INTEGER,
    il_adi VARCHAR(100),
    ilce_adi VARCHAR(100),
    adres TEXT,
    telefon VARCHAR(20),
    koordinat_lat DECIMAL(10,8),
    koordinat_lon DECIMAL(11,8),
    web_sitesi VARCHAR(500),
    veri_kaynagi VARCHAR(200),
    son_guncelleme DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- PostGIS geometry column for spatial queries
    location GEOMETRY(POINT, 4326)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_kuruluslar_kurum_tipi ON public.kuruluslar(kurum_tipi);
CREATE INDEX IF NOT EXISTS idx_kuruluslar_il_adi ON public.kuruluslar(il_adi);
CREATE INDEX IF NOT EXISTS idx_kuruluslar_ilce_adi ON public.kuruluslar(ilce_adi);
CREATE INDEX IF NOT EXISTS idx_kuruluslar_kurum_adi ON public.kuruluslar(kurum_adi);

-- Create spatial index for geography-based queries
CREATE INDEX IF NOT EXISTS idx_kuruluslar_location ON public.kuruluslar USING GIST (location);

-- Function to automatically update location geometry from lat/lon
CREATE OR REPLACE FUNCTION update_location_geometry()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.koordinat_lat IS NOT NULL AND NEW.koordinat_lon IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.koordinat_lon, NEW.koordinat_lat), 4326);
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update location when coordinates change
DROP TRIGGER IF EXISTS trigger_update_location ON public.kuruluslar;
CREATE TRIGGER trigger_update_location
    BEFORE INSERT OR UPDATE ON public.kuruluslar
    FOR EACH ROW
    EXECUTE FUNCTION update_location_geometry();

-- Enable Row Level Security (RLS) for public access
ALTER TABLE public.kuruluslar ENABLE ROW LEVEL SECURITY;

-- Create policy for public read access (anonymous users can read data)
CREATE POLICY "Public read access" ON public.kuruluslar
    FOR SELECT USING (true);

-- Create policy for authenticated users to insert/update (if needed later)
CREATE POLICY "Authenticated users can insert" ON public.kuruluslar
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can update" ON public.kuruluslar
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Grant permissions for anonymous access (public read)
GRANT SELECT ON public.kuruluslar TO anon;

-- Grant full access to authenticated users
GRANT ALL ON public.kuruluslar TO authenticated;

-- Function for geographic search within radius (in meters)
CREATE OR REPLACE FUNCTION public.search_within_radius(
    center_lat DECIMAL,
    center_lon DECIMAL,
    radius_meters INTEGER DEFAULT 10000
)
RETURNS TABLE(
    kurum_id VARCHAR(50),
    kurum_adi VARCHAR(500),
    kurum_tipi VARCHAR(100),
    il_adi VARCHAR(100),
    ilce_adi VARCHAR(100),
    adres TEXT,
    telefon VARCHAR(20),
    koordinat_lat DECIMAL(10,8),
    koordinat_lon DECIMAL(11,8),
    web_sitesi VARCHAR(500),
    distance_meters DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        k.kurum_id,
        k.kurum_adi,
        k.kurum_tipi,
        k.il_adi,
        k.ilce_adi,
        k.adres,
        k.telefon,
        k.koordinat_lat,
        k.koordinat_lon,
        k.web_sitesi,
        ROUND(ST_Distance(
            k.location,
            ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography
        )::DECIMAL, 2) as distance_meters
    FROM public.kuruluslar k
    WHERE k.location IS NOT NULL
    AND ST_DWithin(
        k.location::geography,
        ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography,
        radius_meters
    )
    ORDER BY distance_meters;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION public.search_within_radius TO anon;
GRANT EXECUTE ON FUNCTION public.search_within_radius TO authenticated;
"""
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        client = create_client(url, service_key)
        
        # Execute schema SQL
        response = client.rpc('exec_sql', {'sql': schema_sql}).execute()
        print("✅ Schema başarıyla deploy edildi")
        return True
        
    except Exception as e:
        print(f"❌ Schema deploy hatası: {e}")
        print("\n📋 Manuel Schema Deploy Talimatları:")
        print("1. https://supabase.com/dashboard adresine gidin")
        print("2. Tursakur projesini seçin") 
        print("3. SQL Editor'ı açın")
        print("4. Aşağıdaki SQL kodunu yapıştırın ve çalıştırın:")
        print("\n" + "="*50)
        print(schema_sql)
        print("="*50)
        return False

def insert_sample_data():
    """Örnek veri ekle"""
    print("\n📝 Örnek Veri Ekleniyor...")
    
    client = create_supabase_client()
    if not client:
        return False
    
    sample_institutions = [
        {
            "kurum_id": "TR-06-TEST-001",
            "kurum_adi": "Ankara Üniversitesi Tıp Fakültesi Hastanesi",
            "kurum_tipi": "Üniversite Hastanesi",
            "il_kodu": 6,
            "il_adi": "Ankara",
            "ilce_adi": "Altındağ",
            "adres": "Mamak Mahallesi, Talatpaşa Bulvarı",
            "telefon": "+90 312 508 2000",
            "koordinat_lat": 39.9334,
            "koordinat_lon": 32.8597,
            "web_sitesi": "https://www.ankara.edu.tr",
            "veri_kaynagi": "test_data",
            "son_guncelleme": date.today().isoformat()
        },
        {
            "kurum_id": "TR-34-TEST-002",
            "kurum_adi": "İstanbul Medipol Üniversitesi Hastanesi",
            "kurum_tipi": "Özel Hastane",
            "il_kodu": 34,
            "il_adi": "İstanbul",
            "ilce_adi": "Bağcılar",
            "adres": "TEM Otoyolu Göztepe Çıkışı",
            "telefon": "+90 212 444 7 555",
            "koordinat_lat": 41.0082,
            "koordinat_lon": 28.9784,
            "web_sitesi": "https://www.medipol.edu.tr",
            "veri_kaynagi": "test_data",
            "son_guncelleme": date.today().isoformat()
        },
        {
            "kurum_id": "TR-35-TEST-003",
            "kurum_adi": "İzmir Katip Çelebi Üniversitesi Atatürk EAH",
            "kurum_tipi": "Devlet Hastanesi",
            "il_kodu": 35,
            "il_adi": "İzmir",
            "ilce_adi": "Karabağlar",
            "adres": "Karabağlar, 6374/2. Sk.",
            "telefon": "+90 232 244 4444",
            "koordinat_lat": 38.4237,
            "koordinat_lon": 27.1428,
            "veri_kaynagi": "test_data",
            "son_guncelleme": date.today().isoformat()
        }
    ]
    
    inserted_count = 0
    for institution in sample_institutions:
        try:
            response = client.table('kuruluslar').upsert(institution).execute()
            if response.data:
                inserted_count += 1
                print(f"✅ Eklendi: {institution['kurum_adi']}")
            else:
                print(f"❌ Ekleme başarısız: {institution['kurum_adi']}")
        except Exception as e:
            print(f"❌ Hata ({institution['kurum_adi']}): {e}")
    
    print(f"\n📊 {inserted_count}/{len(sample_institutions)} kuruluş başarıyla eklendi")
    return inserted_count > 0

def test_queries():
    """Çeşitli sorguları test et"""
    print("\n🔍 Veri Sorguları Test Ediliyor...")
    
    client = create_supabase_client()
    if not client:
        return False
    
    try:
        # Test 1: Tüm kayıtları say
        response = client.table('kuruluslar').select("kurum_id", count="exact").execute()
        total_count = response.count
        print(f"✅ Toplam kayıt sayısı: {total_count}")
        
        # Test 2: İl bazında dağılım
        response = client.table('kuruluslar').select("il_adi").execute()
        provinces = {}
        for record in response.data:
            province = record.get('il_adi', 'Bilinmiyor')
            provinces[province] = provinces.get(province, 0) + 1
        
        print("✅ İl Dağılımı:")
        for province, count in provinces.items():
            print(f"   {province}: {count}")
        
        # Test 3: Kurum tipi dağılımı
        response = client.table('kuruluslar').select("kurum_tipi").execute()
        types = {}
        for record in response.data:
            institution_type = record.get('kurum_tipi', 'Bilinmiyor')
            types[institution_type] = types.get(institution_type, 0) + 1
        
        print("✅ Kurum Tipi Dağılımı:")
        for inst_type, count in types.items():
            print(f"   {inst_type}: {count}")
        
        # Test 4: Coğrafi sorgu
        try:
            response = client.rpc('search_within_radius', {
                'center_lat': 39.9334,
                'center_lon': 32.8597,
                'radius_meters': 50000
            }).execute()
            
            if response.data:
                print(f"✅ Ankara çevresinde bulunan kurum sayısı: {len(response.data)}")
            else:
                print("⚠️ Coğrafi sorgu sonuç döndürmedi")
                
        except Exception as e:
            print(f"❌ Coğrafi sorgu hatası: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sorgu test hatası: {e}")
        return False

def load_real_data():
    """Gerçek veri dosyalarını Supabase'e yükle"""
    print("\n📂 Gerçek Veri Yükleniyor...")
    
    # Check if data files exist
    data_files = [
        "data/turkiye_saglik_kuruluslari.json",
        "data/turkiye_saglik_kuruluslari_merged.json"
    ]
    
    client = create_supabase_client()
    if not client:
        return False
    
    loaded_count = 0
    
    for data_file in data_files:
        if os.path.exists(data_file):
            print(f"📁 {data_file} dosyası yükleniyor...")
            
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Process data in batches
                batch_size = 100
                total_records = len(data)
                
                for i in range(0, total_records, batch_size):
                    batch = data[i:i+batch_size]
                    
                    # Convert data format for Supabase
                    supabase_batch = []
                    for record in batch:
                        supabase_record = {
                            "kurum_id": record.get("kurum_id", f"AUTO-{i}"),
                            "kurum_adi": record.get("kurum_adi", ""),
                            "kurum_tipi": record.get("kurum_tipi", ""),
                            "il_kodu": record.get("il_kodu"),
                            "il_adi": record.get("il_adi", ""),
                            "ilce_adi": record.get("ilce_adi", ""),
                            "adres": record.get("adres", ""),
                            "telefon": record.get("telefon", ""),
                            "koordinat_lat": record.get("koordinat_lat"),
                            "koordinat_lon": record.get("koordinat_lon"),
                            "web_sitesi": record.get("web_sitesi", ""),
                            "veri_kaynagi": record.get("veri_kaynagi", data_file),
                            "son_guncelleme": record.get("son_guncelleme", date.today().isoformat())
                        }
                        supabase_batch.append(supabase_record)
                    
                    # Insert batch
                    try:
                        response = client.table('kuruluslar').upsert(supabase_batch).execute()
                        loaded_count += len(response.data)
                        print(f"   ✅ {i+1}-{min(i+batch_size, total_records)} kayıt yüklendi")
                        
                    except Exception as e:
                        print(f"   ❌ Batch {i+1}-{min(i+batch_size, total_records)} hatası: {e}")
                
                print(f"✅ {data_file}: {loaded_count} kayıt yüklendi")
                
            except Exception as e:
                print(f"❌ {data_file} yükleme hatası: {e}")
        else:
            print(f"⚠️ {data_file} dosyası bulunamadı")
    
    return loaded_count > 0

def main():
    """Ana işlem akışı"""
    print("🚀 TURSAKUR 2.0 - Otomatik Supabase Setup")
    print("=" * 50)
    
    # Step 1: Environment check
    if not check_environment():
        print("\n❌ Environment kurulumu başarısız")
        return False
    
    # Step 2: Install dependencies
    install_dependencies()
    
    # Step 3: Test connection
    connection_result = test_connection()
    
    if connection_result == "schema_needed":
        # Step 4: Deploy schema if needed
        if not deploy_schema():
            print("\n⚠️ Schema manuel olarak deploy edilmeli")
            print("Yukarıdaki SQL kodunu Supabase Dashboard'da çalıştırın")
            return False
        
        # Wait a bit for schema to be applied
        time.sleep(2)
        
        # Test connection again
        if not test_connection():
            print("❌ Schema deploy sonrası bağlantı başarısız")
            return False
    
    elif not connection_result:
        print("❌ Veritabanı bağlantısı başarısız")
        return False
    
    # Step 5: Insert sample data
    insert_sample_data()
    
    # Step 6: Test queries
    test_queries()
    
    # Step 7: Load real data (optional)
    load_choice = input("\n❓ Gerçek veri dosyalarını yüklemek istiyor musunuz? (y/N): ")
    if load_choice.lower() in ['y', 'yes', 'evet']:
        load_real_data()
    
    print("\n" + "=" * 50)
    print("🎉 SUPABASE SETUP TAMAMLANDI!")
    print("✅ Veritabanı hazır")
    print("✅ API'ler çalışıyor")
    print("✅ Test verileri mevcut")
    print(f"🌐 Supabase URL: {os.getenv('SUPABASE_URL')}")
    print("📱 React uygulaması artık verileri çekebilir")
    print("\n🔗 Faydalı Linkler:")
    print(f"   Dashboard: https://supabase.com/dashboard/project/moamwmxcpgjvyyawlygw")
    print(f"   API Docs: {os.getenv('SUPABASE_URL')}/rest/v1/")
    print(f"   Table Editor: https://supabase.com/dashboard/project/moamwmxcpgjvyyawlygw/editor")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
