#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Acil Supabase Veri Yükleme
Ana veri dosyasından direkt veritabanına kurumları yükler
"""

import json
import os
import logging
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Ana veri yükleme fonksiyonu"""
    print("🚀 TURSAKUR Acil Veri Yükleme")
    print("=" * 50)
    
    # Supabase bağlantısı
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials bulunamadı!")
        return False
        
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase client oluşturuldu")
    
    # Ana veri dosyasını yükle
    data_file = Path("data/turkiye_saglik_kuruluslari.json")
    
    if not data_file.exists():
        print(f"❌ Veri dosyası bulunamadı: {data_file}")
        return False
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'kurumlar' not in data:
        print("❌ Veri dosyasında 'kurumlar' anahtarı bulunamadı!")
        return False
        
    kurumlar = data['kurumlar']
    print(f"📊 Toplam kurum sayısı: {len(kurumlar)}")
    
    # İlk 3 kurumu kontrol et
    if kurumlar:
        print(f"📝 İlk kurum örneği: {kurumlar[0]}")
    
    # Supabase'de tablo oluştur/kontrol et
    try:
        # health_facilities tablosunu oluştur
        create_table_sql = """
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
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_health_facilities_province ON health_facilities(province);
        CREATE INDEX IF NOT EXISTS idx_health_facilities_type ON health_facilities(facility_type);
        """
        
        print("📋 Tablo şeması oluşturuluyor...")
        print("⚠️  Not: Tablo şeması manuel olarak Supabase dashboard'da oluşturulmalı")
        print("🔗 Dashboard: https://supabase.com/dashboard/project/moamwmxcpgjvyyawlygw/editor")
        
    except Exception as e:
        print(f"⚠️ Tablo oluşturma uyarısı: {e}")
    
    # Verileri dönüştür ve yükle
    batch_size = 100
    total_uploaded = 0
    
    print("🔄 Veri yükleme başlıyor...")
    
    # Önce mevcut verileri temizle
    try:
        delete_result = supabase.table('health_facilities').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("🗑️ Mevcut veriler temizlendi")
    except Exception as e:
        print(f"⚠️ Mevcut veri temizleme uyarısı: {e}")
    
    # Batch olarak yükle
    for i in range(0, len(kurumlar), batch_size):
        batch = kurumlar[i:i + batch_size]
        
        # Batch'i Supabase formatına dönüştür
        batch_data = []
        for kurum in batch:
            transformed = {
                'name': kurum.get('kurum_adi', '').strip(),
                'facility_type': kurum.get('kurum_tipi', 'Bilinmeyen'),
                'province': kurum.get('il_adi', '').strip(),
                'district': kurum.get('ilce_adi', '').strip() if kurum.get('ilce_adi') else None,
                'address': kurum.get('adres', '').strip() if kurum.get('adres') else None,
                'phone': kurum.get('telefon', '').strip() if kurum.get('telefon') else None,
                'website': kurum.get('web_sitesi', '').strip() if kurum.get('web_sitesi') else None,
                'latitude': float(kurum['koordinat_lat']) if kurum.get('koordinat_lat') else None,
                'longitude': float(kurum['koordinat_lon']) if kurum.get('koordinat_lon') else None,
                'sources': [kurum.get('veri_kaynagi', 'bilinmeyen')],
                'is_active': True
            }
            
            # Boş string'leri None yap
            for key, value in list(transformed.items()):
                if value == '':
                    transformed[key] = None
            
            # Gerekli alanları kontrol et
            if transformed.get('name') and transformed.get('province'):
                batch_data.append(transformed)
        
        # Batch'i yükle
        try:
            result = supabase.table('health_facilities').insert(batch_data).execute()
            if result.data:
                uploaded = len(result.data)
                total_uploaded += uploaded
                print(f"✅ Batch {i//batch_size + 1}: {uploaded} kurum yüklendi")
            else:
                print(f"⚠️ Batch {i//batch_size + 1}: Veri döndürülmedi")
        except Exception as e:
            print(f"❌ Batch {i//batch_size + 1} hatası: {e}")
    
    print(f"🎉 Toplam {total_uploaded} kurum Supabase'e yüklendi!")
    
    # Doğrulama
    try:
        count_result = supabase.table('health_facilities').select('count', count='exact').execute()
        print(f"📊 Veritabanındaki toplam kayıt: {count_result.count}")
        
        # Örnek kayıtları getir
        sample_result = supabase.table('health_facilities').select('*').limit(3).execute()
        print(f"📝 Örnek kayıtlar: {len(sample_result.data)} adet")
        for record in sample_result.data:
            print(f"   - {record['name']} ({record['facility_type']}) - {record['province']}")
    except Exception as e:
        print(f"⚠️ Doğrulama hatası: {e}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Veri yükleme tamamlandı!")
        print("🌐 Test için: https://tursakur.vercel.app")
    else:
        print("\n❌ Veri yükleme başarısız!")
