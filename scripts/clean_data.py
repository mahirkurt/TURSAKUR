#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Temizleme ve Standartlaştırma Scripti
- İl/İlçe isimlerini standartlaştır
- Kurum isimlerini title case'e çevir
- Kurum tiplerini renklendir
"""

import json
import re
from datetime import datetime

# Türkiye idari yapısı - İl ve İlçe isimleri
TURKEY_PROVINCES = {
    1: "Adana", 2: "Adıyaman", 3: "Afyonkarahisar", 4: "Ağrı", 5: "Amasya",
    6: "Ankara", 7: "Antalya", 8: "Artvin", 9: "Aydın", 10: "Balıkesir",
    11: "Bilecik", 12: "Bingöl", 13: "Bitlis", 14: "Bolu", 15: "Burdur",
    16: "Bursa", 17: "Çanakkale", 18: "Çankırı", 19: "Çorum", 20: "Denizli",
    21: "Diyarbakır", 22: "Edirne", 23: "Elazığ", 24: "Erzincan", 25: "Erzurum",
    26: "Eskişehir", 27: "Gaziantep", 28: "Giresun", 29: "Gümüşhane", 30: "Hakkâri",
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
    "Devlet Hastanesi": "#1976D2",          # Mavi
    "Özel Hastane": "#8E24AA",              # Mor
    "Üniversite Hastanesi": "#D32F2F",      # Kırmızı
    "Eğitim ve Araştırma Hastanesi": "#F57C00",  # Turuncu
    "Aile Sağlığı Merkezi": "#388E3C",      # Yeşil
    "Toplum Sağlığı Merkezi": "#00796B",    # Teal
    "Ağız ve Diş Sağlığı Merkezi": "#7B1FA2",    # Koyu Mor
    "Fizik Tedavi ve Rehabilitasyon": "#5D4037",  # Kahverengi
    "Ruh Sağlığı Hastanesi": "#455A64",     # Gri
    "Doğum ve Çocuk Bakımevi": "#E91E63",   # Pembe
    "Diğer": "#424242"                      # Varsayılan gri
}

def normalize_text(text):
    """Metin standardizasyonu"""
    if not text:
        return ""
    
    # Unicode normalizasyonu
    text = text.strip()
    
    # Türkçe karakter düzeltmeleri
    replacements = {
        'İ': 'İ', 'I': 'I', 'i': 'i', 'ı': 'ı',
        'Ğ': 'Ğ', 'ğ': 'ğ', 'Ü': 'Ü', 'ü': 'ü',
        'Ş': 'Ş', 'ş': 'ş', 'Ç': 'Ç', 'ç': 'ç',
        'Ö': 'Ö', 'ö': 'ö',
        'Yüreği̇R': 'Yüreğir',
        'ADIYAMAN': 'Adıyaman',
        'AFYON': 'Afyonkarahisar'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def title_case_institution_name(name):
    """Kurum ismini title case'e çevir"""
    if not name:
        return ""
    
    # Normalize et
    name = normalize_text(name)
    
    # T.C. düzeltmesi önce yap
    name = name.replace('T.c.', 'T.C.').replace('t.c.', 'T.C.').replace('Tc.', 'T.C.')
    
    # Özel durumlar
    special_words = {
        'sağlık', 'bakanlığı', 'hastanesi', 'hastane',
        'devlet', 'özel', 'üniversite', 'üniversitesi', 'eğitim',
        'araştırma', 'tıp', 'fakültesi', 'merkezi', 'merkez',
        'aile', 'toplum', 'ağız', 'diş', 'fizik', 'tedavi',
        'rehabilitasyon', 'ruh', 'doğum', 'çocuk', 'bakımevi'
    }
    
    # Kelime kelime işle
    words = name.split()
    result = []
    
    for word in words:
        word_lower = word.lower()
        if word == 'T.C.':
            # T.C. özel durumu - büyük harfle bırak
            result.append('T.C.')
        elif word_lower in special_words:
            # Özel kelimeler için title case
            result.append(word.capitalize())
        else:
            # Normal title case
            result.append(word.capitalize())
    
    return ' '.join(result)

def standardize_province_district(il_kodu, il_adi, ilce_adi):
    """İl ve ilçe isimlerini standartlaştır"""
    # İl adını il koduna göre düzelt
    correct_il_adi = TURKEY_PROVINCES.get(il_kodu, il_adi)
    
    # İlçe adını normalize et
    correct_ilce_adi = normalize_text(ilce_adi) if ilce_adi else ""
    correct_ilce_adi = title_case_institution_name(correct_ilce_adi)
    
    return correct_il_adi, correct_ilce_adi

def get_institution_type_color(kurum_tipi):
    """Kurum tipine göre renk kodu al"""
    # Normalize et ve eşleştir
    kurum_tipi_normalized = normalize_text(kurum_tipi)
    
    for tip, color in INSTITUTION_TYPE_COLORS.items():
        if tip.lower() in kurum_tipi_normalized.lower():
            return color
    
    return INSTITUTION_TYPE_COLORS["Diğer"]

def clean_data():
    """Ana veri temizleme fonksiyonu"""
    print("🧹 Veri temizleme başlıyor...")
    
    # Veri dosyasını yükle
    with open('public/data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Toplam {len(data['kurumlar'])} kurum yüklendi")
    
    # Her kurumu temizle
    for i, kurum in enumerate(data['kurumlar']):
        # İl/İlçe standardizasyonu
        il_adi, ilce_adi = standardize_province_district(
            kurum['il_kodu'], 
            kurum['il_adi'], 
            kurum['ilce_adi']
        )
        kurum['il_adi'] = il_adi
        kurum['ilce_adi'] = ilce_adi
        
        # Kurum adını title case'e çevir
        kurum['kurum_adi'] = title_case_institution_name(kurum['kurum_adi'])
        
        # Kurum tipi rengi ekle
        kurum['kurum_tipi_renk'] = get_institution_type_color(kurum['kurum_tipi'])
        
        # Adres bilgisini güncelle
        if kurum['adres']:
            kurum['adres'] = normalize_text(kurum['adres'])
        
        # Progress
        if (i + 1) % 100 == 0:
            print(f"  ✅ {i + 1} kurum işlendi...")
    
    # Meta bilgileri güncelle
    data['meta']['last_updated'] = datetime.now().isoformat()
    data['meta']['version'] = "1.1"
    data['meta']['description'] = "Türkiye Sağlık Kuruluşları Açık Veritabanı - Güncellenmiş"
    
    # Güncellenmiş veriyi kaydet
    with open('public/data/turkiye_saglik_kuruluslari.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ Veri temizleme tamamlandı!")
    print(f"📁 Güncellenmiş dosya: public/data/turkiye_saglik_kuruluslari.json")

if __name__ == "__main__":
    clean_data()
