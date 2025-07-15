#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TURSAKUR Basit Final Rapor
"""

import json
import os
from datetime import datetime

def simple_final_report():
    """Basit final rapor oluştur"""
    
    print("🏥 TURSAKUR - TÜRKİYE SAĞLIK KURULUŞLARI FİNAL RAPORU")
    print("=" * 60)
    
    # Ana veri dosyasını yükle
    try:
        with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Ana veri dosyası başarıyla yüklendi")
        
        # Metadata'dan bilgileri al
        metadata = data.get('metadata', {})
        kurumlar = data.get('kurumlar', [])
        
        print(f"\n📊 GENEL BİLGİLER:")
        print(f"   • Toplam Kurum: {len(kurumlar):,}")
        print(f"   • Toplam İl: {metadata.get('total_iller', 'N/A')}")
        print(f"   • Son Güncelleme: {metadata.get('son_guncelleme', 'N/A')}")
        
        # Kurum tipi dağılımı
        if 'istatistikler' in metadata and 'kurum_tipi_dagilimi' in metadata['istatistikler']:
            kurum_tipleri = metadata['istatistikler']['kurum_tipi_dagilimi']
            print(f"\n🏥 KURUM TİPİ DAĞILIMI:")
            for tip, sayi in sorted(kurum_tipleri.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {tip}: {sayi:,} kurum")
        
        # Veri kaynakları
        if 'veri_kaynaklari' in metadata:
            print(f"\n📁 VERİ KAYNAKLARI:")
            for kaynak in metadata['veri_kaynaklari']:
                print(f"   • {kaynak}")
        
        # Raw dosya analizi
        print(f"\n📂 HAM VERİ DOSYALARI:")
        raw_files = [
            "saglik_bakanligi_tesisleri.json",
            "ozel_hastaneler.json", 
            "universite_hastaneleri.json",
            "trhastane_universite_hastaneleri.json"
        ]
        
        for file in raw_files:
            file_path = f"data/raw/{file}"
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)
                    file_size = os.path.getsize(file_path) / 1024
                    print(f"   • {file}: {len(raw_data)} kayıt ({file_size:.1f} KB)")
                except:
                    print(f"   • {file}: Okunamadı")
            else:
                print(f"   • {file}: Dosya bulunamadı")
        
        # Veri kalitesi analizi
        koordinat_var = sum(1 for k in kurumlar if k.get('koordinat_lat') and k.get('koordinat_lon'))
        telefon_var = sum(1 for k in kurumlar if k.get('telefon') and k.get('telefon').strip())
        web_var = sum(1 for k in kurumlar if k.get('web_sitesi') and k.get('web_sitesi').strip())
        
        print(f"\n📍 VERİ KALİTESİ ANALİZİ:")
        print(f"   • Koordinat bilgisi olan: {koordinat_var:,} (%{koordinat_var/len(kurumlar)*100:.1f})")
        print(f"   • Telefon bilgisi olan: {telefon_var:,} (%{telefon_var/len(kurumlar)*100:.1f})")
        print(f"   • Web sitesi olan: {web_var:,} (%{web_var/len(kurumlar)*100:.1f})")
        
        print(f"\n✅ TURSAKUR v2.0 BAŞARIYLA FİNALİZE EDİLMİŞTİR!")
        print(f"🎯 Türkiye'nin en kapsamlı sağlık kuruluşları veritabanı hazır!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    simple_final_report()
