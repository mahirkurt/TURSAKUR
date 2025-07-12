#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_character_normalization():
    """Karakter normalleştirme testi"""
    test_il = "Hakkari̇"
    
    print(f"Orijinal: '{test_il}'")
    print(f"Karakterler: {[ord(c) for c in test_il]}")
    
    # Normalize et
    normalized = test_il.upper().strip()
    print(f"Upper: '{normalized}'")
    print(f"Upper karakterler: {[ord(c) for c in normalized]}")
    
    # Özel karakterleri temizle
    normalized = normalized.replace('İ', 'I').replace('Ş', 'S').replace('Ğ', 'G')
    normalized = normalized.replace('Ü', 'U').replace('Ö', 'O').replace('Ç', 'C')
    normalized = normalized.replace('Ḋ', 'I').replace('İ', 'I')  # Noktalı i çeşitleri
    normalized = normalized.replace('Ì', 'I').replace('Í', 'I')  # Aksanlı i çeşitleri
    normalized = normalized.replace(chr(775), '')  # Unicode combining character
    
    print(f"Temizlenmiş: '{normalized}'")
    print(f"Temizlenmiş karakterler: {[ord(c) for c in normalized]}")
    
    # HAKKARİ ile karşılaştır
    expected = "HAKKARİ"
    print(f"Beklenen: '{expected}'")
    print(f"Beklenen karakterler: {[ord(c) for c in expected]}")
    
    print(f"Eşit mi? {normalized == expected}")

if __name__ == '__main__':
    test_character_normalization()
