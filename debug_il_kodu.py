#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def find_zero_il_kodu():
    """0 il_kodu olan kurumları bul"""
    with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print('İl kodu 0 olan kurumlar:')
    count = 0
    for i, kurum in enumerate(data['kurumlar']):
        if kurum.get('il_kodu') == 0:
            count += 1
            print(f'{count}. {kurum.get("kurum_adi", "")} - {kurum.get("il_adi", "")} - {kurum.get("ilce_adi", "")}')
            if count >= 10:  # İlk 10'unu göster
                break
    
    print(f'Toplam {count} kurum il_kodu 0 olan kayıt bulundu.')

if __name__ == '__main__':
    find_zero_il_kodu()
