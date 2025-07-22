#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Temizleme ve Düzeltme Scripti
Ana veritabanındaki boş ve hatalı verileri temizler
"""

import json
import logging
from datetime import datetime

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_main_data():
    """Ana veri dosyasındaki hataları temizle"""
    
    logger.info("🧹 ANA VERİ TEMİZLEME BAŞLIYOR")
    
    # Ana veri dosyasını yükle
    with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    kurumlar = data['kurumlar']
    original_count = len(kurumlar)
    
    # Temizlenen veriler
    cleaned_kurumlar = []
    removed_count = 0
    fixed_count = 0
    
    for i, kurum in enumerate(kurumlar):
        try:
            # Kritik alanları kontrol et
            kurum_adi = kurum.get('kurum_adi', '').strip()
            il_adi = kurum.get('il_adi', '').strip()
            il_kodu = kurum.get('il_kodu', 0)
            
            # Eğer kurum adı yoksa, atla
            if not kurum_adi:
                logger.warning(f"⚠️ Kurum {i+1}: Kurum adı yok, atlanıyor")
                removed_count += 1
                continue
                
            # İl bilgisi eksikse, atla
            if not il_adi or il_kodu == 0:
                logger.warning(f"⚠️ Kurum {i+1}: {kurum_adi[:50]} - İl bilgisi eksik, atlanıyor")
                removed_count += 1
                continue
            
            # İlçe adını düzelt
            if not kurum.get('ilce_adi'):
                kurum['ilce_adi'] = 'Merkez'
                fixed_count += 1
            
            # Koordinatları kontrol et ve düzelt
            lat = kurum.get('koordinat_lat', 0)
            lon = kurum.get('koordinat_lon', 0)
            
            # Türkiye dışındaki koordinatlar varsa temizle
            if lat and lon:
                if not (35.8 <= lat <= 42.2 and 26.0 <= lon <= 45.0):
                    logger.warning(f"⚠️ Geçersiz koordinat: {kurum_adi[:30]} - ({lat}, {lon})")
                    kurum['koordinat_lat'] = 0
                    kurum['koordinat_lon'] = 0
                    fixed_count += 1
            
            # Telefon numarasını düzelt
            telefon = kurum.get('telefon', '')
            if telefon and not telefon.startswith('+90'):
                # Basit düzeltme
                if telefon.startswith('0'):
                    kurum['telefon'] = '+90' + telefon[1:]
                elif len(telefon) == 10 and telefon.isdigit():
                    kurum['telefon'] = '+90' + telefon
                fixed_count += 1
            
            # Temiz kurum listesine ekle
            cleaned_kurumlar.append(kurum)
            
        except Exception as e:
            logger.error(f"❌ Kurum {i+1} işlenirken hata: {e}")
            removed_count += 1
            continue
    
    # Meta bilgileri güncelle
    unique_provinces = set(k['il_adi'] for k in cleaned_kurumlar)
    unique_types = set(k['kurum_tipi'] for k in cleaned_kurumlar)
    
    data['kurumlar'] = cleaned_kurumlar
    data['meta'] = {
        'toplam_kurum': len(cleaned_kurumlar),
        'toplam_il': len(unique_provinces),
        'toplam_kurum_tipi': len(unique_types),
        'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
        'veri_kaynagi': ['Sağlık Bakanlığı', 'Özel Hastaneler', 'Üniversite Hastaneleri', 'Wikipedia'],
        'veri_guncelleme_aciklama': 'Çankırı il hatası düzeltildi, boş veriler temizlendi'
    }
    
    # Dosyayı kaydet
    with open('data/turkiye_saglik_kuruluslari.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Rapor
    logger.info(f"✅ VERİ TEMİZLEME TAMAMLANDI!")
    logger.info(f"📊 Orijinal kurum sayısı: {original_count}")
    logger.info(f"🧹 Temizlenen kurum sayısı: {len(cleaned_kurumlar)}")
    logger.info(f"🗑️ Kaldırılan kurum sayısı: {removed_count}")
    logger.info(f"🔧 Düzeltilen kurum sayısı: {fixed_count}")
    logger.info(f"🗺️ Toplam il sayısı: {len(unique_provinces)}")
    
    return len(cleaned_kurumlar)

def clean_raw_hash_files():
    """Raw klasöründeki hash dosyalarını temizle"""
    
    hash_files = [
        'data/raw/ozel_hastaneler_hash.json',
        'data/raw/saglik_bakanligi_hash.json', 
        'data/raw/trhastane_hash.json'
    ]
    
    for file_path in hash_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Sadece hash string'i varsa, geçerli JSON formatına çevir
            if content and not content.startswith('{'):
                hash_data = {
                    "file_hash": content.replace('"', ''),
                    "last_update": datetime.now().strftime('%Y-%m-%d')
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(hash_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"✅ Hash dosyası düzeltildi: {file_path}")
                
        except Exception as e:
            logger.warning(f"⚠️ Hash dosyası düzeltilmedi: {file_path} - {e}")

def main():
    """Ana fonksiyon"""
    
    # Raw hash dosyalarını düzelt
    clean_raw_hash_files()
    
    # Ana veriyi temizle
    final_count = clean_main_data()
    
    logger.info(f"🎉 Tüm temizleme işlemleri tamamlandı! Final kurum sayısı: {final_count}")
    
    return 0

if __name__ == "__main__":
    exit(main())
