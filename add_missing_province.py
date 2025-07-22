#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eksik İl Tamamlama Scripti
"""

import json
from datetime import datetime

def add_missing_province():
    # Veriyi yükle
    with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Çankırı kurumu ekle
    cankiri_kurum = {
        "kurum_id": "TR-18-DEV-001",
        "kurum_adi": "Çankırı Devlet Hastanesi",
        "kurum_tipi": "Devlet Hastanesi",
        "il_kodu": 18,
        "il_adi": "Çankırı",
        "ilce_adi": "Merkez",
        "adres": "Çankırı Merkez",
        "telefon": "",
        "koordinat_lat": 40.6013,
        "koordinat_lon": 33.6134,
        "web_sitesi": "",
        "veri_kaynagi": "Eksik İl Tamamlama",
        "son_guncelleme": datetime.now().strftime('%Y-%m-%d'),
        "kurum_tipi_renk": "#1976D2",
        "kurum_tipi_text_renk": "#FFFFFF"
    }
    
    # Kurumu ekle
    data['kurumlar'].append(cankiri_kurum)
    
    # Meta bilgileri güncelle
    data['meta']['toplam_kurum'] = len(data['kurumlar'])
    data['meta']['toplam_il'] = len(set(k['il_adi'] for k in data['kurumlar']))
    data['meta']['son_guncelleme'] = datetime.now().strftime('%Y-%m-%d')
    
    # Kaydet
    with open('data/turkiye_saglik_kuruluslari.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Çankırı kurumu eklendi!")
    print(f"📊 Toplam kurum: {len(data['kurumlar'])}")
    print(f"🗺️ Toplam il: {len(set(k['il_adi'] for k in data['kurumlar']))}")

if __name__ == "__main__":
    add_missing_province()
