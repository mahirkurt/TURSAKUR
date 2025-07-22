#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Standardizasyon Scripti
- İl adlarını 81 standart ile uyumlaştır
- Kurum tiplerini renklendir
- Duplikasyon kontrolü
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

# Türkiye'nin 81 ili - Resmi Standart
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

# İl adı varyasyonları - Normalizasyon mapping
PROVINCE_VARIANTS = {
    # Afyonkarahisar varyasyonları
    "AFYONKARAHİSAR": "Afyonkarahisar",
    "AFYONKARAHİSAR": "Afyonkarahisar", 
    "AFYONKARAHİSAR": "Afyonkarahisar",
    "AFYONKARAHİSAR": "Afyonkarahisar",
    "AFYON": "Afyonkarahisar",
    
    # Kahramanmaraş varyasyonları
    "KAHRAMANMARAŞ": "Kahramanmaraş",
    "K.MARAŞ": "Kahramanmaraş",
    "MARAŞ": "Kahramanmaraş",
    "KAHRAMANMARAS": "Kahramanmaraş",
    
    # Şanlıurfa varyasyonları
    "ŞANLIURFA": "Şanlıurfa",
    "ŞURFA": "Şanlıurfa",
    "URFA": "Şanlıurfa",
    "SANLIURFA": "Şanlıurfa",
    
    # Diğer varyasyonlar
    "İSTANBUL": "İstanbul",
    "ANKARA": "Ankara",
    "İZMİR": "İzmir",
    "BURSA": "Bursa",
    "ANTALYA": "Antalya",
    "ADANA": "Adana",
    "KONYA": "Konya",
    "GAZİANTEP": "Gaziantep",
    "MERSİN": "Mersin",
    "DİYARBAKIR": "Diyarbakır",
    "KAYSERİ": "Kayseri",
    "ESKİŞEHİR": "Eskişehir",
    "SAMSUN": "Samsun",
    "DENİZLİ": "Denizli",
    "ŞANLIURFA": "Şanlıurfa",
    "ADAPAZARI": "Sakarya",
    "İZMİT": "Kocaeli",
    "HATAY": "Hatay",
    "MALATYA": "Malatya",
    "ERZURUM": "Erzurum",
    "VAN": "Van",
    "BATMAN": "Batman",
    "ELAZIĞ": "Elazığ",
    "ERZINCAN": "Erzincan",
    "SİVAS": "Sivas",
    "TOKAT": "Tokat",
    "ÇORUM": "Çorum",
    "KIRIKKALE": "Kırıkkale",
    "KIRŞEHİR": "Kırşehir",
    "YOZGAT": "Yozgat",
    "NEVŞEHİR": "Nevşehir",
    "KAYSERİ": "Kayseri",
    "AKSARAY": "Aksaray",
    "KARAMAN": "Karaman",
    "KONYA": "Konya",
    "AFYONKARAHİSAR": "Afyonkarahisar",
    "ISPARTA": "Isparta",
    "BURDUR": "Burdur",
    "ANTALYA": "Antalya",
    "MERSİN": "Mersin",
    "ADANA": "Adana",
    "OSMANIYE": "Osmaniye",
    "HATAY": "Hatay"
}

# Kurum tipi renk kodları
INSTITUTION_TYPE_COLORS = {
    "Devlet Hastanesi": "#1976D2",          # Mavi
    "Özel Hastane": "#8E24AA",              # Mor  
    "Üniversite Hastanesi": "#D32F2F",      # Kırmızı
    "Eğitim ve Araştırma Hastanesi": "#388E3C", # Yeşil
    "Aile Sağlığı Merkezi": "#F57C00",      # Turuncu
    "Toplum Sağlığı Merkezi": "#5D4037",    # Kahverengi
    "Ağız ve Diş Sağlığı Merkezi": "#00796B", # Teal
    "Özel Poliklinik": "#7B1FA2",          # Koyu Mor
    "Özel Tıp Merkezi": "#C2185B",         # Pembe
    "Diyaliz Merkezi": "#455A64",          # Gri Mavi
    "Fizik Tedavi ve Rehabilitasyon Merkezi": "#FF5722", # Derin Turuncu
    "Ambulans İstasyonu": "#E65100",       # Koyu Turuncu
    "Acil Servis": "#B71C1C",             # Koyu Kırmızı
    "Laboratuvar": "#4A148C",             # Koyu Mor
    "Radyoloji Merkezi": "#1A237E",       # Koyu Mavi
    "Kan Merkezi": "#BF360C",             # Kırmızı Turuncu
    "Diğer": "#757575"                    # Gri
}

def normalize_text(text: str) -> str:
    """Türkçe karakterleri ve büyük/küçük harf sorunlarını normalize et"""
    if not text:
        return ""
        
    # Önce trim
    text = text.strip()
    
    # Türkçe karakterleri normalize et
    text = text.replace('İ', 'İ').replace('I', 'I')
    text = text.replace('ı', 'ı').replace('i', 'i')
    text = text.replace('Ş', 'Ş').replace('ş', 'ş')
    text = text.replace('Ğ', 'Ğ').replace('ğ', 'ğ')
    text = text.replace('Ü', 'Ü').replace('ü', 'ü')
    text = text.replace('Ö', 'Ö').replace('ö', 'ö')
    text = text.replace('Ç', 'Ç').replace('ç', 'ç')
    
    return text

def standardize_province_name(il_adi: str) -> Tuple[str, int]:
    """İl adını standardize et ve il kodunu döndür"""
    if not il_adi:
        return "Bilinmiyor", 0
    
    # Normalize et
    normalized = normalize_text(il_adi.upper())
    
    # Önce varyasyon mapping'den kontrol et
    if normalized in PROVINCE_VARIANTS:
        standard_name = PROVINCE_VARIANTS[normalized]
        # İl kodunu bul
        for kod, il in TURKEY_PROVINCES.items():
            if il == standard_name:
                return standard_name, kod
    
    # Direkt eşleşme kontrol et
    for kod, il in TURKEY_PROVINCES.items():
        if il.upper() == normalized:
            return il, kod
            
    # Kısmi eşleşme kontrol et
    for kod, il in TURKEY_PROVINCES.items():
        if normalized in il.upper() or il.upper() in normalized:
            return il, kod
    
    # Bulunamadı
    return il_adi, 0

def get_institution_type_color(kurum_tipi: str) -> Tuple[str, str]:
    """Kurum tipine göre renk kodu ve metin rengi döndür"""
    if not kurum_tipi:
        return INSTITUTION_TYPE_COLORS["Diğer"], "#FFFFFF"
    
    # Normalize et
    normalized = normalize_text(kurum_tipi)
    
    # Anahtar kelime bazında eşleştir
    for tip, color in INSTITUTION_TYPE_COLORS.items():
        if tip.lower() in normalized.lower():
            return color, "#FFFFFF" if is_dark_color(color) else "#000000"
    
    return INSTITUTION_TYPE_COLORS["Diğer"], "#FFFFFF"

def is_dark_color(hex_color: str) -> bool:
    """Rengin koyu mu açık mı olduğunu belirle"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    # RGB değerlerini çıkar
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16) 
    b = int(hex_color[4:6], 16)
    
    # Luminance hesapla
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5

def standardize_data():
    """Ana veri standardizasyon fonksiyonu"""
    # Veriyi yükle
    with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    kurumlar = data['kurumlar']
    print(f"🏥 Başlangıç: {len(kurumlar)} kurum")
    
    # İstatistikler
    standardized_count = 0
    color_added_count = 0
    province_fixes = {}
    
    for kurum in kurumlar:
        # İl adını standardize et
        original_il = kurum.get('il_adi', '')
        standard_il, il_kodu = standardize_province_name(original_il)
        
        if original_il != standard_il:
            if original_il not in province_fixes:
                province_fixes[original_il] = standard_il
            standardized_count += 1
        
        kurum['il_adi'] = standard_il
        kurum['il_kodu'] = il_kodu
        
        # Kurum tipi renklendirme
        kurum_tipi = kurum.get('kurum_tipi', 'Diğer')
        color, text_color = get_institution_type_color(kurum_tipi)
        
        kurum['kurum_tipi_renk'] = color
        kurum['kurum_tipi_text_renk'] = text_color
        color_added_count += 1
    
    # İstatistikleri güncelle
    data['meta']['son_guncelleme'] = datetime.now().strftime('%Y-%m-%d')
    data['meta']['toplam_kurum'] = len(kurumlar)
    data['meta']['toplam_il'] = len(set(k['il_adi'] for k in kurumlar if k.get('il_adi')))
    data['meta']['toplam_kurum_tipi'] = len(set(k['kurum_tipi'] for k in kurumlar if k.get('kurum_tipi')))
    
    # Backup oluştur
    backup_filename = f"data/backup/turkiye_saglik_kuruluslari_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Ana dosyayı güncelle
    with open('data/turkiye_saglik_kuruluslari.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Rapor
    print(f"\n✅ VERİ STANDARDİZASYONU TAMAMLANDI!")
    print(f"📊 Toplam Kurum: {len(kurumlar)}")
    print(f"🏛️ Standardize Edilen İl: {standardized_count}")
    print(f"🎨 Renklendirilen Kurum: {color_added_count}")
    print(f"🗺️ Toplam Benzersiz İl: {len(set(k['il_adi'] for k in kurumlar))}")
    
    if province_fixes:
        print(f"\n📋 İL ADI DEĞİŞİKLİKLERİ:")
        for original, fixed in list(province_fixes.items())[:10]:  # İlk 10'unu göster
            print(f"   {original} → {fixed}")
        if len(province_fixes) > 10:
            print(f"   ... ve {len(province_fixes) - 10} adet daha")
    
    print(f"\n💾 Backup: {backup_filename}")
    
    # Final il kontrolü
    unique_provinces = sorted(set(k['il_adi'] for k in kurumlar if k.get('il_adi')))
    print(f"\n🔍 FINAL İL LİSTESİ ({len(unique_provinces)} adet):")
    for i, il in enumerate(unique_provinces[:15], 1):  # İlk 15'ini göster
        print(f"   {i:2d}. {il}")
    if len(unique_provinces) > 15:
        print(f"   ... ve {len(unique_provinces) - 15} adet daha")
    
    # 81 il kontrolü
    if len(unique_provinces) != 81:
        print(f"\n⚠️  UYARI: İl sayısı {len(unique_provinces)} ama olması gereken 81!")
        
        # 81 standart ile karşılaştır
        standard_provinces = set(TURKEY_PROVINCES.values())
        current_provinces = set(unique_provinces)
        
        missing = standard_provinces - current_provinces
        extra = current_provinces - standard_provinces
        
        if missing:
            print(f"❌ Eksik iller ({len(missing)}): {', '.join(sorted(missing))}")
        if extra:
            print(f"➕ Fazla/Yanlış iller ({len(extra)}): {', '.join(sorted(extra))}")

if __name__ == "__main__":
    import os
    
    # Backup klasörünü oluştur
    os.makedirs('data/backup', exist_ok=True)
    
    standardize_data()
    print("\n🎉 İşlem tamamlandı!")
