#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Çankırı Hastaneleri Arama Scripti
Tüm veri kaynaklarını titizlikle incele
"""

import json
import csv
import re
from typing import List, Dict

def search_in_json(filepath: str, search_terms: List[str]) -> List[Dict]:
    """JSON dosyasında Çankırı ile ilgili kayıtları ara"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = []
        
        # Eğer liste ise
        if isinstance(data, list):
            items = data
        # Eğer dict içinde 'kurumlar' anahtarı varsa
        elif isinstance(data, dict) and 'kurumlar' in data:
            items = data['kurumlar']
        # Eğer dict içinde başka anahtar varsa
        elif isinstance(data, dict):
            items = []
            for key, value in data.items():
                if isinstance(value, list):
                    items.extend(value)
                elif isinstance(value, dict):
                    items.append(value)
        else:
            return []
        
        for item in items:
            if isinstance(item, dict):
                # Tüm değerleri string'e çevir ve birleştir
                text = ' '.join(str(v).lower() for v in item.values() if v)
                
                # Çankırı ile ilgili terimleri ara
                for term in search_terms:
                    if term in text:
                        results.append(item)
                        break
        
        return results
        
    except Exception as e:
        print(f"❌ {filepath} okuma hatası: {e}")
        return []

def search_in_csv(filepath: str, search_terms: List[str]) -> List[Dict]:
    """CSV dosyasında Çankırı ile ilgili kayıtları ara"""
    try:
        results = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Tüm değerleri birleştir
                text = ' '.join(str(v).lower() for v in row.values() if v)
                
                # Çankırı ile ilgili terimleri ara
                for term in search_terms:
                    if term in text:
                        results.append(dict(row))
                        break
        
        return results
        
    except Exception as e:
        print(f"❌ {filepath} okuma hatası: {e}")
        return []

def deep_search_cankiri():
    """Çankırı hastanelerini tüm kaynaklarda ara"""
    
    # Çankırı ile ilgili arama terimleri
    search_terms = [
        'çankırı', 'cankiri', 'çankiri', 'cankırı',
        'çankırı merkez', 'çankırı devlet', 'çankırı hastane',
        'çankırı doktor', 'çankırı sağlık'
    ]
    
    print("🔍 ÇANKIRI HASTANELERİ ARAŞTIRMASI")
    print("=" * 50)
    
    # Raw data dosyalarını incele
    raw_files = [
        ('data/raw/saglik_bakanligi_tesisleri.json', 'json'),
        ('data/raw/saglik_bakanligi_tesisleri.csv', 'csv'),
        ('data/raw/ozel_hastaneler.json', 'json'),
        ('data/raw/ozel_hastaneler.csv', 'csv'),
        ('data/raw/trhastane_data.json', 'json'),
        ('data/raw/universite_hastaneleri.json', 'json'),
        ('data/raw/vikipedia_gelismis_kesfet.json', 'json'),
        ('data/raw/wikipedia_hospitals.json', 'json')
    ]
    
    all_results = []
    
    for filepath, file_type in raw_files:
        print(f"\n📁 {filepath} kontrol ediliyor...")
        
        if file_type == 'json':
            results = search_in_json(filepath, search_terms)
        else:
            results = search_in_csv(filepath, search_terms)
        
        if results:
            print(f"✅ {len(results)} Çankırı kaydı bulundu!")
            for i, result in enumerate(results[:5], 1):  # İlk 5'ini göster
                # En önemli alanları çıkar
                name = result.get('kurum_adi', result.get('name', result.get('KURUM_ADI', 'İsimsiz')))
                location = result.get('il_adi', result.get('province', result.get('İL_ADI', 'Bilinmiyor')))
                addr = result.get('adres', result.get('address', result.get('ADRES', '')))
                
                print(f"   {i}. {name}")
                print(f"      📍 {location}")
                if addr and len(addr) > 10:
                    print(f"      🏠 {addr[:100]}...")
                
                all_results.append({
                    'kaynak': filepath,
                    'kurum': result
                })
        else:
            print(f"❌ Çankırı kaydı bulunamadı")
    
    # Ana veritabanında da kontrol et
    print(f"\n📊 ANA VERİTABANI KONTROLÜ")
    print("-" * 30)
    
    main_results = search_in_json('data/turkiye_saglik_kuruluslari.json', search_terms)
    print(f"Ana veritabanında Çankırı kayıtları: {len(main_results)}")
    
    for result in main_results:
        print(f"  • {result.get('kurum_adi', 'İsimsiz')} - {result.get('il_adi', 'Bilinmiyor')}")
    
    # Sonuç özeti
    print(f"\n📋 SONUÇ ÖZETİ")
    print("=" * 30)
    print(f"Toplam Çankırı kaydı bulundu: {len(all_results)}")
    print(f"Ana veritabanında: {len(main_results)}")
    
    if all_results:
        print("\n💡 ÖNERİLER:")
        print("1. Raw data'daki Çankırı kayıtlarını process_data.py ile tekrar işleyin")
        print("2. İl adı normalizasyonunu kontrol edin")
        print("3. Eksik kayıtları manuel olarak ana veritabanına ekleyin")
        
        # En iyi sonuçları kaydet
        best_results = []
        for item in all_results[:10]:  # En iyi 10 sonuç
            kurum = item['kurum']
            if any(term in str(kurum).lower() for term in ['hastane', 'hospital', 'sağlık', 'health']):
                best_results.append(kurum)
        
        if best_results:
            with open('temp_cankiri_results.json', 'w', encoding='utf-8') as f:
                json.dump(best_results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 En iyi {len(best_results)} sonuç temp_cankiri_results.json dosyasına kaydedildi")
    
    else:
        print("\n⚠️ UYARI: Hiçbir raw data'da Çankırı kaydı bulunamadı!")
        print("Bu beklenmedik bir durum. Veri kaynaklarını kontrol edin.")

if __name__ == "__main__":
    deep_search_cankiri()
