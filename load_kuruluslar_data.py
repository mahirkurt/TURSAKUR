#!/usr/bin/env python3
"""
TURSAKUR - Kuruluslar tablosuna veri yükleme
Mevcut kuruluslar tablosuna complex JSONB formatında veri yükler
"""

import json
import os
import logging
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🚀 TURSAKUR - Kuruluslar Veri Yükleme")
    print("=" * 50)
    
    # Supabase bağlantısı
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
    
    # Ana veri dosyasını yükle
    with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    kurumlar = data['kurumlar']
    print(f"📊 Toplam kurum: {len(kurumlar)}")
    
    # Mevcut verileri temizle
    try:
        supabase.table('kuruluslar').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("🗑️ Mevcut veriler temizlendi")
    except Exception as e:
        print(f"⚠️ Temizleme uyarısı: {e}")
    
    # Batch yükleme
    batch_size = 50
    total_uploaded = 0
    
    for i in range(0, len(kurumlar), batch_size):
        batch = kurumlar[i:i + batch_size]
        batch_data = []
        
        for kurum in batch:
            # Kuruluslar tablosu JSONB formatına dönüştür
            transformed = {
                'isim_standart': kurum.get('kurum_adi', '').strip(),
                'isim_resmi': kurum.get('kurum_adi', '').strip(),
                'tip': kurum.get('kurum_tipi', 'Bilinmeyen'),
                'aktif': True,
                'adres_yapilandirilmis': {
                    'il': kurum.get('il_adi', ''),
                    'ilce': kurum.get('ilce_adi', ''),
                    'tam_adres': kurum.get('adres', ''),
                    'posta_kodu': kurum.get('posta_kodu', ''),
                    'mahalle': kurum.get('mahalle', '')
                },
                'iletisim': {
                    'telefon': kurum.get('telefon', ''),
                    'website': kurum.get('web_sitesi', ''),
                    'email': kurum.get('email', ''),
                    'fax': kurum.get('fax', '')
                },
                'metaveri': {
                    'kaynak': kurum.get('veri_kaynagi', 'ana_veri'),
                    'veri_kalitesi': 'orta',
                    'orijinal_veri': kurum
                }
            }
            
            # PostGIS Point oluştur (eğer koordinat varsa)
            if kurum.get('koordinat_lat') and kurum.get('koordinat_lon'):
                try:
                    lat = float(kurum['koordinat_lat'])
                    lon = float(kurum['koordinat_lon'])
                    # PostGIS WKT format: POINT(longitude latitude)
                    transformed['konum'] = f"POINT({lon} {lat})"
                except:
                    pass
            
            # Boş değerleri temizle
            if transformed['isim_standart']:
                batch_data.append(transformed)
        
        # Batch yükle
        if batch_data:
            try:
                result = supabase.table('kuruluslar').insert(batch_data).execute()
                uploaded = len(result.data) if result.data else 0
                total_uploaded += uploaded
                print(f"✅ Batch {i//batch_size + 1}: {uploaded}/{len(batch_data)} kurum yüklendi")
            except Exception as e:
                print(f"❌ Batch {i//batch_size + 1} hatası: {e}")
    
    print(f"🎉 Toplam {total_uploaded} kurum yüklendi!")
    
    # Doğrulama
    try:
        count_result = supabase.table('kuruluslar').select('*', count='exact').execute()
        print(f"📊 Veritabanındaki toplam kayıt: {count_result.count}")
        
        # Örnek kayıtlar
        if count_result.data:
            print("📝 Örnek kayıtlar:")
            for i, record in enumerate(count_result.data[:3]):
                print(f"   {i+1}. {record['isim_standart']} - {record['adres_yapilandirilmis']['il']}")
    except Exception as e:
        print(f"⚠️ Doğrulama hatası: {e}")
    
    return total_uploaded > 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Veri yükleme başarılı!")
        print("🔄 Şimdi frontend'i düzeltiyorum...")
    else:
        print("\n❌ Veri yükleme başarısız!")
