#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Güçlü Veri Temizleme Scripti
- Unicode karakterleri normalize et
- İl adlarını kesin 81 standart ile eşleştir
- Kurum tiplerini renklendir
"""

import json
import unicodedata
import re
from datetime import datetime
from typing import Dict, List, Tuple

# Türkiye'nin 81 ili - Kesin Standart
TURKEY_PROVINCES = {
    1: "Adana", 2: "Adıyaman", 3: "Afyonkarahisar", 4: "Ağrı", 5: "Amasya",
    6: "Ankara", 7: "Antalya", 8: "Artvin", 9: "Aydın", 10: "Balıkesir",
    11: "Bilecik", 12: "Bingöl", 13: "Bitlis", 14: "Bolu", 15: "Burdur",
    16: "Bursa", 17: "Çanakkale", 18: "Çankırı", 19: "Çorum", 20: "Denizli",
    21: "Diyarbakır", 22: "Edirne", 23: "Elazığ", 24: "Erzincan", 25: "Erzurum",
    26: "Eskişehir", 27: "Gaziantep", 28: "Giresun", 29: "Gümüşhane", 30: "Hakkari",
    31: "Hatay", 32: "Isparta", 33: "Mersin", 34: "İstanbul", 35: "İzmir",
    36: "Kars", 37: "Kastamonu", 38: "Kayseri", 39: "Kırklareli", 40: "Kırşehir",
    41: "Kocaeli", 42: "Konya", 43: "Kütahya", 44: "Malatya", 45: "Manisa",
    46: "Kahramanmaraş", 47: "Mardin", 48: "Muğla", 49: "Muş", 50: "Nevşehir",
    51: "Niğde", 52: "Ordu", 53: "Rize", 54: "Sakarya", 55: "Samsun",
    56: "Siirt", 57: "Sinop", 58: "Sivas", 59: "Tekirdağ", 60: "Tokat",
    61: "Trabzon", 62: "Tunceli", 63: "Şanlıurfa", 64: "Uşak", 65: "Van",
    66: "Yozgat", 67: "Zonguldak", 68: "Aksaray", 69: "Bayburt", 70: "Karaman",
    71: "Kırıkkale", 72: "Batman", 73: "Şırnak", 74: "Bartın", 75: "Ardahan",
    76: "Iğdır", 77: "Yalova", 78: "Karabük", 79: "Kilis", 80: "Osmaniye",
    81: "Düzce"
}

# Kurum tipi renk kodları
INSTITUTION_TYPE_COLORS = {
    "Devlet Hastanesi": "#1976D2",
    "Özel Hastane": "#8E24AA", 
    "Üniversite Hastanesi": "#D32F2F",
    "Eğitim ve Araştırma Hastanesi": "#388E3C",
    "Aile Sağlığı Merkezi": "#F57C00",
    "Toplum Sağlığı Merkezi": "#5D4037",
    "Ağız ve Diş Sağlığı Merkezi": "#00796B",
    "Özel Poliklinik": "#7B1FA2",
    "Özel Tıp Merkezi": "#C2185B",
    "Diyaliz Merkezi": "#455A64",
    "Fizik Tedavi ve Rehabilitasyon Merkezi": "#FF5722",
    "Ambulans İstasyonu": "#E65100",
    "Diğer": "#757575"
}

def normalize_unicode_text(text: str) -> str:
    """Unicode karakterleri normalize et ve temizle"""
    if not text:
        return ""
    
    # Unicode normalize (NFD -> NFC)
    text = unicodedata.normalize('NFC', text.strip())
    
    # Yanlış Unicode kombinasyonları düzelt
    replacements = {
        # İ harfi düzeltmeleri
        'i̇': 'i', 'İ': 'İ', 'I': 'I', 'ı': 'ı',
        
        # Diğer Türkçe karakterler
        'ş': 'ş', 'Ş': 'Ş',
        'ğ': 'ğ', 'Ğ': 'Ğ', 
        'ü': 'ü', 'Ü': 'Ü',
        'ö': 'ö', 'Ö': 'Ö',
        'ç': 'ç', 'Ç': 'Ç',
        
        # Problematik kombinasyonlar
        'i̇': 'i', 'İ̇': 'İ',
        'ı̇': 'ı', 'İ': 'I',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def aggressive_province_match(il_name: str) -> Tuple[str, int]:
    """Agresif il eşleştirme - hem ASCII hem Unicode versiyonları dene"""
    if not il_name or il_name.lower() in ['bilinmiyor', 'unknown', '']:
        return "İstanbul", 34  # Varsayılan
    
    # Normalize et
    normalized = normalize_unicode_text(il_name).strip()
    
    # ASCII versiyonu da oluştur (fallback için)
    ascii_version = (
        normalized
        .replace('İ', 'I').replace('ı', 'i').replace('i', 'i')
        .replace('Ş', 'S').replace('ş', 's')
        .replace('Ğ', 'G').replace('ğ', 'g')
        .replace('Ü', 'U').replace('ü', 'u')
        .replace('Ö', 'O').replace('ö', 'o')
        .replace('Ç', 'C').replace('ç', 'c')
    )
    
    # Direkt eşleştirme dene
    candidates = [normalized, normalized.title(), normalized.upper(), normalized.lower()]
    
    for candidate in candidates:
        for kod, il in TURKEY_PROVINCES.items():
            if candidate == il:
                return il, kod
    
    # Kısmi eşleştirme (en az 3 karakter)
    if len(normalized) >= 3:
        for kod, il in TURKEY_PROVINCES.items():
            # Başlangıç eşleştirme
            if il.lower().startswith(normalized.lower()[:3]):
                return il, kod
            # İçerik eşleştirme  
            if normalized.lower() in il.lower() or il.lower() in normalized.lower():
                return il, kod
    
    # ASCII fallback
    for kod, il in TURKEY_PROVINCES.items():
        il_ascii = (
            il.replace('İ', 'I').replace('ı', 'i').replace('i', 'i')
            .replace('Ş', 'S').replace('ş', 's')
            .replace('Ğ', 'G').replace('ğ', 'g')
            .replace('Ü', 'U').replace('ü', 'u')  
            .replace('Ö', 'O').replace('ö', 'o')
            .replace('Ç', 'C').replace('ç', 'c')
        )
        if ascii_version.lower() == il_ascii.lower():
            return il, kod
    
    # Özel durumlar
    special_cases = {
        'istanbul': ('İstanbul', 34),
        'izmir': ('İzmir', 35),
        'ankara': ('Ankara', 6),
        'bursa': ('Bursa', 16),
        'antalya': ('Antalya', 7),
        'adana': ('Adana', 1),
        'konya': ('Konya', 42),
        'gaziantep': ('Gaziantep', 27),
        'mersin': ('Mersin', 33),
        'diyarbakir': ('Diyarbakır', 21),
        'kayseri': ('Kayseri', 38),
        'eskisehir': ('Eskişehir', 26),
        'samsun': ('Samsun', 55),
        'denizli': ('Denizli', 20),
        'sanliurfa': ('Şanlıurfa', 63),
        'urfa': ('Şanlıurfa', 63),
        'afyon': ('Afyonkarahisar', 3),
        'maras': ('Kahramanmaraş', 46),
        'k.maras': ('Kahramanmaraş', 46),
        'izmit': ('Kocaeli', 41),
        'adapazari': ('Sakarya', 54),
    }
    
    key = normalized.lower().replace(' ', '').replace('.', '').replace('-', '')
    if key in special_cases:
        return special_cases[key]
    
    # Son çare - en popüler ili ver
    print(f"⚠️  İl eşleştirilemedi: '{il_name}' -> '{normalized}' -> İstanbul")
    return "İstanbul", 34

def get_institution_type_color(kurum_tipi: str) -> Tuple[str, str]:
    """Kurum tipine göre renk ve metin rengi döndür"""
    if not kurum_tipi:
        return INSTITUTION_TYPE_COLORS["Diğer"], "#FFFFFF"
    
    normalized = normalize_unicode_text(kurum_tipi)
    
    # Anahtar kelime eşleştirme
    keywords = {
        "Devlet Hastanesi": ["devlet", "hastane", "devlet hastanesi"],
        "Özel Hastane": ["özel hastane", "private hospital"],
        "Üniversite Hastanesi": ["üniversite", "tıp fakülte", "university"],
        "Eğitim ve Araştırma Hastanesi": ["eğitim", "araştırma", "training"],
        "Aile Sağlığı Merkezi": ["aile sağlığı", "asm", "family health"],
        "Toplum Sağlığı Merkezi": ["toplum sağlığı", "tsm"],
        "Ağız ve Diş Sağlığı Merkezi": ["ağız", "diş", "adsm", "dental"],
        "Özel Poliklinik": ["özel poliklinik", "poliklinik"],
        "Özel Tıp Merkezi": ["özel tıp", "tıp merkezi"],
        "Diyaliz Merkezi": ["diyaliz", "dialysis"],
        "Fizik Tedavi ve Rehabilitasyon Merkezi": ["fizik tedavi", "rehabilitasyon"],
        "Ambulans İstasyonu": ["ambulans", "ambulance"]
    }
    
    text_lower = normalized.lower()
    for tip, kelimeler in keywords.items():
        for kelime in kelimeler:
            if kelime in text_lower:
                color = INSTITUTION_TYPE_COLORS[tip]
                return color, "#FFFFFF" if is_dark_color(color) else "#000000"
    
    return INSTITUTION_TYPE_COLORS["Diğer"], "#FFFFFF"

def is_dark_color(hex_color: str) -> bool:
    """Rengin koyu olup olmadığını kontrol et"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5

def deep_clean_data():
    """Güçlü veri temizleme"""
    # Veriyi yükle
    with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    kurumlar = data['kurumlar']
    print(f"🏥 Başlangıç: {len(kurumlar)} kurum")
    
    # İstatistikler
    fixed_provinces = {}
    
    for i, kurum in enumerate(kurumlar):
        # İl adını agresif eşleştir
        original_il = kurum.get('il_adi', '')
        standard_il, il_kodu = aggressive_province_match(original_il)
        
        if original_il != standard_il:
            if original_il not in fixed_provinces:
                fixed_provinces[original_il] = standard_il
        
        kurum['il_adi'] = standard_il
        kurum['il_kodu'] = il_kodu
        
        # Kurum tipi renklendirme
        kurum_tipi = kurum.get('kurum_tipi', 'Diğer')
        color, text_color = get_institution_type_color(kurum_tipi)
        
        kurum['kurum_tipi_renk'] = color
        kurum['kurum_tipi_text_renk'] = text_color
        
        # İlerleme göster
        if (i + 1) % 500 == 0 or i == len(kurumlar) - 1:
            print(f"⏳ İşlenen: {i + 1}/{len(kurumlar)}")
    
    # Meta bilgileri güncelle
    unique_provinces = sorted(set(k['il_adi'] for k in kurumlar))
    unique_types = sorted(set(k['kurum_tipi'] for k in kurumlar))
    
    data['meta']['son_guncelleme'] = datetime.now().strftime('%Y-%m-%d')
    data['meta']['toplam_kurum'] = len(kurumlar)
    data['meta']['toplam_il'] = len(unique_provinces)
    data['meta']['toplam_kurum_tipi'] = len(unique_types)
    
    # Backup
    backup_filename = f"data/backup/deep_clean_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Ana dosyayı kaydet
    with open('data/turkiye_saglik_kuruluslari.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Rapor
    print(f"\n✅ GÜÇLÜ TEMİZLEME TAMAMLANDI!")
    print(f"📊 Toplam Kurum: {len(kurumlar)}")
    print(f"🏛️ Düzeltilen İl Adı: {len(fixed_provinces)}")
    print(f"🗺️ Benzersiz İl Sayısı: {len(unique_provinces)}")
    print(f"🎨 Kurum Tipi Sayısı: {len(unique_types)}")
    
    if len(unique_provinces) == 81:
        print("🎉 MÜKEMMEL! Tam 81 il standardı sağlandı!")
    else:
        print(f"⚠️  İl sayısı: {len(unique_provinces)} (hedef: 81)")
    
    # Önemli değişiklikler
    if fixed_provinces:
        print(f"\n📋 BAŞLICA İL ADI DEĞİŞİKLİKLERİ:")
        for original, fixed in list(fixed_provinces.items())[:10]:
            print(f"   {original} → {fixed}")
        if len(fixed_provinces) > 10:
            print(f"   ... ve {len(fixed_provinces) - 10} adet daha")
    
    print(f"\n💾 Backup: {backup_filename}")
    
    # Final listesi
    print(f"\n🗺️  TÜRKIYE İLLERİ ({len(unique_provinces)} adet):")
    for i, il in enumerate(unique_provinces, 1):
        if i <= 20:  # İlk 20'yi göster
            print(f"   {i:2d}. {il}")
        elif i == 21:
            print(f"   ... ve {len(unique_provinces) - 20} adet daha")

if __name__ == "__main__":
    import os
    os.makedirs('data/backup', exist_ok=True)
    deep_clean_data()
    print("\n🎉 İşlem tamamlandı!")
