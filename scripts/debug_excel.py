#!/usr/bin/env python3
"""
Sağlık Bakanlığı Excel dosyasının yapısını analiz eden debug betiği
"""

import pandas as pd
import requests
import os

def debug_excel():
    # Excel dosyasını indir
    url = "https://dosyamerkez.saglik.gov.tr/Eklenti/45020/0/saglik-tesisleri-listesi-02022023xls.xls"
    
    print("Excel dosyası indiriliyor...")
    response = requests.get(url, stream=True)
    
    with open("temp_debug.xls", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("Excel analiz ediliyor...")
    
    # Excel'i oku
    excel_file = pd.ExcelFile("temp_debug.xls")
    print(f"Sheet'ler: {excel_file.sheet_names}")
    
    for sheet_name in excel_file.sheet_names:
        print(f"\n=== SHEET: {sheet_name} ===")
        df = pd.read_excel("temp_debug.xls", sheet_name=sheet_name)
        
        print(f"Boyut: {len(df)} satır, {len(df.columns)} sütun")
        print(f"Sütun adları: {list(df.columns)}")
        
        print("\nİlk 5 satır:")
        print(df.head())
        
        print("\nSütun veri tipleri:")
        print(df.dtypes)
        
        # Null değerleri kontrol et
        print("\nBoş değer sayıları:")
        print(df.isnull().sum())
    
    # Dosyayı temizle
    os.unlink("temp_debug.xls")

if __name__ == "__main__":
    debug_excel()
