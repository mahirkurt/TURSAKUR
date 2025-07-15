#!/usr/bin/env python3
"""
İl adı normalizasyon script'i
Duplicate ve case sensitivity problemlerini çözer
"""

import json
import re
from typing import Dict, Set

def normalize_province_name(province: str) -> str:
    """İl adını normalize et"""
    if not province:
        return ""
    
    # Türkçe karakterleri düzelt
    replacements = {
        'i̇': 'İ',
        'I': 'I',
        'ı': 'ı',
        'İ': 'İ'
    }
    
    normalized = province.strip()
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    # İl adını büyük harfe çevir
    normalized = normalized.upper()
    
    # Özel düzeltmeler
    special_cases = {
        'AFYONKARAHİSAR': 'AFYONKARAHİSAR',
        'AFYONKARAHİSAR': 'AFYONKARAHİSAR',
        'Afyonkarahi̇sar': 'AFYONKARAHİSAR',
        'KAHRAMANMARAŞ': 'KAHRAMANMARAŞ',
        'Kahramanmaraş': 'KAHRAMANMARAŞ',
        'Kayseri̇': 'KAYSERİ',
        'ŞANLIURFA': 'ŞANLIURFA',
        'Şanliurfa': 'ŞANLIURFA'
    }
    
    if normalized in special_cases:
        normalized = special_cases[normalized]
    
    return normalized

def fix_province_names():
    """Ana veri dosyasındaki il adlarını düzelt"""
    try:
        # Ana veri dosyasını yükle
        with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"🔍 {len(data)} sağlık kurumu verisi yüklendi")
        
        # İl adlarını analiz et
        province_stats = {}
        for item in data:
            original = item.get('il_adi', '')
            normalized = normalize_province_name(original)
            
            if original != normalized:
                if original not in province_stats:
                    province_stats[original] = {'count': 0, 'normalized': normalized}
                province_stats[original]['count'] += 1
        
        if province_stats:
            print(f"\n📊 Düzeltilecek il adları ({len(province_stats)} farklı):")
            for original, info in sorted(province_stats.items()):
                print(f"  {original} → {info['normalized']} ({info['count']} kurum)")
        
        # İl adlarını düzelt
        fixed_count = 0
        for item in data:
            original = item.get('il_adi', '')
            normalized = normalize_province_name(original)
            
            if original != normalized:
                item['il_adi'] = normalized
                fixed_count += 1
        
        # Unique il sayısını kontrol et
        unique_provinces = sorted(set([item['il_adi'] for item in data]))
        print(f"\n✅ Toplam unique il sayısı: {len(unique_provinces)}")
        print(f"🔧 {fixed_count} kurum kaydının il adı düzeltildi")
        
        # Dosyayı kaydet
        with open('data/turkiye_saglik_kuruluslari.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Ana veri dosyası güncellendi")
        
        # İl listesini yazdır
        print(f"\n📋 Güncel il listesi:")
        for i, province in enumerate(unique_provinces, 1):
            print(f"  {i:2d}. {province}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    print("🚀 İl adı normalizasyonu başlatılıyor...")
    print("=" * 60)
    
    if fix_province_names():
        print("\n🎊 İl adı normalizasyonu tamamlandı!")
    else:
        print("\n❌ İl adı normalizasyonu başarısız!")
