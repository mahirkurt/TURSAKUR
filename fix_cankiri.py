#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Çankırı İl Hatası Düzeltme Scripti
"""

import json
from datetime import datetime

def fix_cankiri_assignments():
    """Yanlış ile atanmış Çankırı kurumlarını düzelt"""
    
    # Ana veriyi yükle
    with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    kurumlar = data['kurumlar']
    fixed_count = 0
    
    print("🔧 ÇANKIRI İL ATAMA HATASI DÜZELTMESİ")
    print("=" * 50)
    
    # Çankırı ile ilgili kurum adlarını tara
    cankiri_keywords = [
        'çankırı', 'ilgaz', 'çerkeş', 'kurşunlu', 'kızılırmak', 
        'şabanözü', 'orta', 'atkaracalar', 'eldivan', 'yapraklı'
    ]
    
    for kurum in kurumlar:
        kurum_adi = kurum.get('kurum_adi', '').lower()
        il_adi = kurum.get('il_adi', '')
        
        # Eğer kurum adında Çankırı ilçe/merkez isimleri geçiyorsa
        for keyword in cankiri_keywords:
            if keyword in kurum_adi:
                # Ama il adı Çankırı değilse
                if il_adi != 'Çankırı':
                    print(f"🔄 {kurum['kurum_adi']}")
                    print(f"   Eski il: {il_adi} → Yeni il: Çankırı")
                    
                    # Düzelt
                    kurum['il_adi'] = 'Çankırı'
                    kurum['il_kodu'] = 18
                    
                    # İlçe bilgisini de düzelt
                    if 'ilgaz' in kurum_adi:
                        kurum['ilce_adi'] = 'Ilgaz'
                    elif 'çerkeş' in kurum_adi:
                        kurum['ilce_adi'] = 'Çerkeş'
                    elif 'kurşunlu' in kurum_adi:
                        kurum['ilce_adi'] = 'Kurşunlu'
                    elif 'kızılırmak' in kurum_adi:
                        kurum['ilce_adi'] = 'Kızılırmak'
                    elif 'şabanözü' in kurum_adi:
                        kurum['ilce_adi'] = 'Şabanözü'
                    elif 'orta' in kurum_adi and 'orta ilçe' in kurum_adi:
                        kurum['ilce_adi'] = 'Orta'
                    elif 'atkaracalar' in kurum_adi:
                        kurum['ilce_adi'] = 'Atkaracalar'
                    elif 'çankırı' in kurum_adi and 'merkez' not in kurum['ilce_adi'].lower():
                        kurum['ilce_adi'] = 'Merkez'
                    
                    fixed_count += 1
                break
    
    # Ayrıca özel Çankırı hastanelerini de kontrol et
    for kurum in kurumlar:
        kurum_adi = kurum.get('kurum_adi', '').lower()
        if 'çankiri' in kurum_adi or 'karateki̇n' in kurum_adi.lower():
            if kurum.get('il_adi') != 'Çankırı':
                print(f"🏥 Özel hastane düzeltiliyor: {kurum['kurum_adi']}")
                kurum['il_adi'] = 'Çankırı'
                kurum['il_kodu'] = 18
                if not kurum.get('ilce_adi') or kurum['ilce_adi'].lower() == 'merkez':
                    kurum['ilce_adi'] = 'Merkez'
                fixed_count += 1
    
    # Eklediğimiz demo kurumu kaldır (artık gerçek veriler var)
    demo_removed = False
    for i, kurum in enumerate(kurumlar):
        if kurum.get('veri_kaynagi') == 'Eksik İl Tamamlama':
            print(f"🗑️ Demo kurum kaldırılıyor: {kurum['kurum_adi']}")
            kurumlar.pop(i)
            demo_removed = True
            break
    
    # Meta bilgileri güncelle
    unique_provinces = set(k['il_adi'] for k in kurumlar)
    unique_types = set(k['kurum_tipi'] for k in kurumlar)
    
    data['meta']['toplam_kurum'] = len(kurumlar)
    data['meta']['toplam_il'] = len(unique_provinces)
    data['meta']['toplam_kurum_tipi'] = len(unique_types)
    data['meta']['son_guncelleme'] = datetime.now().strftime('%Y-%m-%d')
    
    # Kaydet
    with open('data/turkiye_saglik_kuruluslari.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Sonuç raporu
    print(f"\n✅ DÜZELTME TAMAMLANDI!")
    print(f"🔧 Düzeltilen kurum sayısı: {fixed_count}")
    if demo_removed:
        print(f"🗑️ Demo kurum kaldırıldı")
    print(f"📊 Toplam kurum: {len(kurumlar)}")
    print(f"🗺️ Toplam il: {len(unique_provinces)}")
    
    # Çankırı kurumlarını listele
    cankiri_kurumlar = [k for k in kurumlar if k.get('il_adi') == 'Çankırı']
    print(f"\n🏥 ÇANKIRI HASTANELERİ ({len(cankiri_kurumlar)} adet):")
    for i, kurum in enumerate(cankiri_kurumlar, 1):
        print(f"   {i:2d}. {kurum['kurum_adi']}")
        print(f"       📍 {kurum['ilce_adi']}, Çankırı")
    
    return len(cankiri_kurumlar)

if __name__ == "__main__":
    cankiri_count = fix_cankiri_assignments()
    print(f"\n🎉 Çankırı artık {cankiri_count} kurumla tam kapsamda!")
