#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Üniversite-Hastane İlişkileri İşleme Modülü
Bu modül kapsamlı üniversite-hastane ilişkilerini ana veri formatına çevirir
"""

import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversiteHastaneProcessor:
    """Üniversite-hastane ilişkilerini işleme sınıfı"""
    
    def __init__(self):
        self.il_kodlari = {
            "Adana": 1, "Adıyaman": 2, "Afyonkarahisar": 3, "Ağrı": 4, "Amasya": 5,
            "Ankara": 6, "Antalya": 7, "Artvin": 8, "Aydın": 9, "Balıkesir": 10,
            "Bilecik": 11, "Bingöl": 12, "Bitlis": 13, "Bolu": 14, "Burdur": 15,
            "Bursa": 16, "Çanakkale": 17, "Çankırı": 18, "Çorum": 19, "Denizli": 20,
            "Diyarbakır": 21, "Edirne": 22, "Elazığ": 23, "Erzincan": 24, "Erzurum": 25,
            "Eskişehir": 26, "Gaziantep": 27, "Giresun": 28, "Gümüşhane": 29, "Hakkari": 30,
            "Hatay": 31, "Isparta": 32, "Mersin": 33, "İstanbul": 34, "İzmir": 35,
            "Kars": 36, "Kastamonu": 37, "Kayseri": 38, "Kırklareli": 39, "Kırşehir": 40,
            "Kocaeli": 41, "Konya": 42, "Kütahya": 43, "Malatya": 44, "Manisa": 45,
            "Kahramanmaraş": 46, "Mardin": 47, "Muğla": 48, "Muş": 49, "Nevşehir": 50,
            "Niğde": 51, "Ordu": 52, "Rize": 53, "Sakarya": 54, "Samsun": 55,
            "Siirt": 56, "Sinop": 57, "Sivas": 58, "Tekirdağ": 59, "Tokat": 60,
            "Trabzon": 61, "Tunceli": 62, "Şanlıurfa": 63, "Uşak": 64, "Van": 65,
            "Yozgat": 66, "Zonguldak": 67, "Aksaray": 68, "Bayburt": 69, "Karaman": 70,
            "Kırıkkale": 71, "Batman": 72, "Şırnak": 73, "Bartın": 74, "Ardahan": 75,
            "Iğdır": 76, "Yalova": 77, "Karabük": 78, "Kilis": 79, "Osmaniye": 80, "Düzce": 81
        }
    
    def universite_hastane_iliskilerini_isle(self) -> List[Dict]:
        """Üniversite-hastane ilişkilerini ana formata çevir"""
        logger.info("🏥 Üniversite-hastane ilişkileri işleniyor...")
        
        try:
            # Kapsamlı üniversite-hastane ilişkileri dosyasını yükle
            with open('data/raw/kapsamli_universite_hastane_iliskileri.json', 'r', encoding='utf-8') as f:
                iliski_verileri = json.load(f)
            
            logger.info(f"📊 {len(iliski_verileri)} üniversite-hastane ilişkisi bulundu")
            
            ana_format_kurumlar = []
            
            for iliski in iliski_verileri:
                # Hastane için ana format kurum oluştur
                hastane = self.iliski_to_ana_format(iliski)
                if hastane:
                    ana_format_kurumlar.append(hastane)
                
                # Eğer anlaşmalı hastane ise, ayrıca üniversite bilgisini de kaydet
                if iliski.get('iliski_tip') == 'anlasmali':
                    # Hastane profiline üniversite bilgisini ekle
                    if hastane:
                        hastane['anlasmali_universiteler'] = iliski.get('universite_adi', '')
                        hastane['anlaşma_detay'] = iliski.get('anlaşma_detay', 'Tıp Fakültesi eğitim anlaşması')
            
            logger.info(f"✅ {len(ana_format_kurumlar)} kurum ana formata çevrildi")
            return ana_format_kurumlar
            
        except FileNotFoundError:
            logger.warning("⚠️ Kapsamlı üniversite-hastane ilişkileri dosyası bulunamadı")
            return []
        except Exception as e:
            logger.error(f"❌ Üniversite-hastane ilişkileri işlenirken hata: {e}")
            return []
    
    def iliski_to_ana_format(self, iliski: Dict) -> Optional[Dict]:
        """Bir üniversite-hastane ilişkisini ana formata çevir"""
        try:
            # İl kodunu bul
            il_adi = iliski.get('hastane_sehir', iliski.get('universite_sehir', 'Ankara'))
            il_kodu = self.il_kodlari.get(il_adi, 6)  # Default Ankara
            
            # Kurum tipini belirle
            kurum_tipi = self.iliski_tipinden_kurum_tipi_belirle(iliski)
            
            # Kurum ID oluştur
            kurum_id = self.kurum_id_olustur(il_kodu, kurum_tipi, iliski['hastane_adi'])
            
            # Ana format kurum
            kurum = {
                "kurum_id": kurum_id,
                "kurum_adi": iliski['hastane_adi'],
                "kurum_tipi": kurum_tipi,
                "il_kodu": il_kodu,
                "il_adi": il_adi,
                "ilce_adi": iliski.get('hastane_sehir', il_adi),
                "adres": iliski.get('hastane_adres', ''),
                "telefon": iliski.get('hastane_telefon', ''),
                "koordinat_lat": None,
                "koordinat_lon": None,
                "web_sitesi": iliski.get('hastane_web', ''),
                "veri_kaynagi": f"Kapsamlı Üniversite-Hastane İlişkileri: {iliski.get('veri_kaynagi', '')}",
                "son_guncelleme": "2025-07-15"
            }
            
            # Üniversite ile ilişki bilgilerini ekle
            if iliski.get('iliski_tip') == 'sahip':
                kurum['universite_sahibi'] = iliski['universite_adi']
                kurum['universite_tipi'] = iliski.get('universite_tip', 'devlet')
            elif iliski.get('iliski_tip') == 'anlasmali':
                kurum['anlasmali_universite'] = iliski['universite_adi']
                kurum['anlaşma_detay'] = iliski.get('anlaşma_detay', 'Tıp Fakültesi eğitim anlaşması')
            
            # Ek bilgiler
            if iliski.get('kuruluş_yili'):
                kurum['kuruluş_yili'] = iliski['kuruluş_yili']
            if iliski.get('yatak_sayisi'):
                kurum['yatak_sayisi'] = iliski['yatak_sayisi']
            
            return kurum
            
        except Exception as e:
            logger.warning(f"⚠️ İlişki işlenirken hata ({iliski.get('hastane_adi', 'N/A')}): {e}")
            return None
    
    def iliski_tipinden_kurum_tipi_belirle(self, iliski: Dict) -> str:
        """İlişki tipinden kurum tipini belirle"""
        hastane_tip = iliski.get('hastane_tip', '')
        iliski_tip = iliski.get('iliski_tip', '')
        
        if hastane_tip == 'universite_hastanesi' or iliski_tip == 'sahip':
            return 'UNIVERSITE_HASTANESI'
        elif hastane_tip == 'egitim_arastirma' or 'eğitim' in iliski.get('hastane_adi', '').lower():
            return 'EGITIM_ARASTIRMA_HASTANESI'
        elif hastane_tip == 'ozel':
            return 'OZEL_HASTANE'
        elif hastane_tip == 'devlet':
            return 'DEVLET_HASTANESI'
        else:
            # Default olarak üniversite hastanesi
            return 'UNIVERSITE_HASTANESI'
    
    def kurum_id_olustur(self, il_kodu: int, kurum_tipi: str, kurum_adi: str) -> str:
        """Kurum ID oluştur"""
        # Tip kodu
        tip_kodlari = {
            'UNIVERSITE_HASTANESI': 'UH',
            'EGITIM_ARASTIRMA_HASTANESI': 'EH',
            'OZEL_HASTANE': 'OH',
            'DEVLET_HASTANESI': 'DH',
            'AGIZ_DIS_SAGLIGI_MERKEZI': 'DM'
        }
        
        tip_kodu = tip_kodlari.get(kurum_tipi, 'GN')
        
        # Hash değeri (son 4 karakter)
        import hashlib
        hash_obj = hashlib.md5(kurum_adi.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[-4:].upper()
        
        return f"TR-{il_kodu:02d}-{tip_kodu}-{hash_hex}"

def main():
    """Ana fonksiyon"""
    processor = UniversiteHastaneProcessor()
    kurumlar = processor.universite_hastane_iliskilerini_isle()
    
    # Test amaçlı çıktı
    if kurumlar:
        print(f"\n✅ {len(kurumlar)} üniversite-hastane ilişkisi işlendi")
        print("\n📋 Örnek kurumlar:")
        for i, kurum in enumerate(kurumlar[:3]):
            print(f"   {i+1}. {kurum['kurum_adi']} ({kurum['kurum_tipi']})")
            if 'universite_sahibi' in kurum:
                print(f"      └─ Sahibi: {kurum['universite_sahibi']}")
            elif 'anlasmali_universite' in kurum:
                print(f"      └─ Anlaşmalı: {kurum['anlasmali_universite']}")

if __name__ == "__main__":
    main()
