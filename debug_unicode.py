#!/usr/bin/env python3
"""
Unicode character problemi debug eden script
"""

import json
import unicodedata

def debug_unicode():
    # Ana veri dosyasını oku
    with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("=== UNICODE DEBUG ===")
    
    # il_kodu=0 olan kayıtları bul
    zero_records = [record for record in data['kurumlar'] if record.get('il_kodu', -1) == 0]
    print(f"il_kodu=0 olan kayıt sayısı: {len(zero_records)}")
    
    # İl kodları sözlüğü - HAKKARİ ile
    il_kodlari = {
        'ADANA': 1, 'ADIYAMAN': 2, 'AFYONKARAHİSAR': 3, 'AĞRI': 4, 'AMASYA': 5,
        'ANKARA': 6, 'ANTALYA': 7, 'ARTVİN': 8, 'AYDIN': 9, 'BALIKESİR': 10,
        'BİLECİK': 11, 'BİNGÖL': 12, 'BİTLİS': 13, 'BOLU': 14, 'BURDUR': 15,
        'BURSA': 16, 'ÇANAKKALE': 17, 'ÇANKIRI': 18, 'ÇORUM': 19, 'DENİZLİ': 20,
        'DİYARBAKIR': 21, 'EDİRNE': 22, 'ELAZIĞ': 23, 'ERZİNCAN': 24, 'ERZURUM': 25,
        'ESKİŞEHİR': 26, 'GAZİANTEP': 27, 'GİRESUN': 28, 'GÜMÜŞHANE': 29, 'HAKKARİ': 30,
        'HATAY': 31, 'ISPARTA': 32, 'MERSİN': 33, 'İSTANBUL': 34, 'İZMİR': 35,
        'KARS': 36, 'KASTAMONU': 37, 'KAYSERİ': 38, 'KIRKLARELİ': 39, 'KIRŞEHİR': 40,
        'KOCAELİ': 41, 'KONYA': 42, 'KÜTAHYA': 43, 'MALATYA': 44, 'MANİSA': 45,
        'KAHRAMANMARAŞ': 46, 'MARDİN': 47, 'MUĞLA': 48, 'MUŞ': 49, 'NEVŞEHİR': 50,
        'NİĞDE': 51, 'ORDU': 52, 'RİZE': 53, 'SAKARYA': 54, 'SAMSUN': 55,
        'SİİRT': 56, 'SİNOP': 57, 'SİVAS': 58, 'TEKİRDAĞ': 59, 'TOKAT': 60,
        'TRABZON': 61, 'TUNCELİ': 62, 'ŞANLIURFA': 63, 'UŞAK': 64, 'VAN': 65,
        'YOZGAT': 66, 'ZONGULDAK': 67, 'AKSARAY': 68, 'BAYBURT': 69, 'KARAMAN': 70,
        'KIRIKKALE': 71, 'BATMAN': 72, 'ŞIRNAK': 73, 'BARTIN': 74, 'ARDAHAN': 75,
        'IĞDIR': 76, 'YALOVA': 77, 'KARABÜK': 78, 'KİLİS': 79, 'OSMANİYE': 80,
        'DÜZCE': 81
    }
    
    print("\n=== Problematik kayıtlar ===")
    for i, record in enumerate(zero_records[:3]):
        print(f"\nKayıt {i+1}:")
        il_adi = record.get('il_adi', '')
        print(f"  Kurum: {record.get('kurum_adi', 'N/A')}")
        print(f"  il_adi: '{il_adi}'")
        print(f"  il_adi repr: {repr(il_adi)}")
        print(f"  Byte codes: {[ord(c) for c in il_adi]}")
        print(f"  Unicode names: {[unicodedata.name(c, 'UNKNOWN') for c in il_adi]}")
        
        # Normalizasyon testi
        normalized = il_adi.upper().strip()
        print(f"  Upper: {repr(normalized)}")
        
        nfd = unicodedata.normalize('NFD', normalized)
        print(f"  NFD: {repr(nfd)}")
        print(f"  NFD bytes: {[ord(c) for c in nfd]}")
        
        cleaned = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
        print(f"  Combining temizlendi: {repr(cleaned)}")
        
        nfc = unicodedata.normalize('NFC', cleaned)
        print(f"  NFC: {repr(nfc)}")
        
        # Dictionary'de var mı?
        print(f"  Dictionary'de '{nfc}' var mı: {nfc in il_kodlari}")
        
        # Tüm dictionary key'leri kontrol et
        matches = [key for key in il_kodlari.keys() if 'HAKKAR' in key]
        print(f"  Benzer key'ler: {matches}")

if __name__ == "__main__":
    debug_unicode()
