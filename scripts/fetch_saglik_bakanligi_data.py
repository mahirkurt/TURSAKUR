#!/usr/bin/env python3
"""
Sağlık Bakanlığı Excel Veri Çekme Betiği
Sağlık Bakanlığı'nın resmi Excel dosyasından sağlık tesisi verilerini çeker ve işler.
"""

import requests
import pandas as pd
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
from urllib.parse import urlparse
import re

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SaglikBakanligiDataFetcher:
    """Sağlık Bakanlığı Excel verilerini çeken sınıf."""
    
    def __init__(self):
        self.excel_url = "https://dosyamerkez.saglik.gov.tr/Eklenti/45020/0/saglik-tesisleri-listesi-02022023xls.xls"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Kurum tipi eşlemeleri
        self.kurum_tipi_mapping = {
            'HASTANE': 'Devlet Hastanesi',
            'ÜNIVERSITE HASTANESİ': 'Üniversite Hastanesi',
            'EĞİTİM VE ARAŞTIRMA HASTANESİ': 'Eğitim ve Araştırma Hastanesi',
            'ÖZEL HASTANE': 'Özel Hastane',
            'ASM': 'Aile Sağlığı Merkezi',
            'TSM': 'Toplum Sağlığı Merkezi',
            'ADSM': 'Ağız ve Diş Sağlığı Merkezi',
            'ÖZEL POLİKLİNİK': 'Özel Poliklinik',
            'TIP MERKEZİ': 'Özel Tıp Merkezi',
            'DİYALİZ': 'Diyaliz Merkezi',
            'FİZİK TEDAVİ': 'Fizik Tedavi ve Rehabilitasyon Merkezi',
            'AMBULANS': 'Ambulans İstasyonu'
        }
        
        # İl kodu eşlemeleri
        self.il_kodu_mapping = {
            'ADANA': 1, 'ADIYAMAN': 2, 'AFYONKARAHİSAR': 3, 'AĞRI': 4, 'AMASYA': 5,
            'ANKARA': 6, 'ANTALYA': 7, 'ARTVİN': 8, 'AYDIN': 9, 'BALIKESİR': 10,
            'BİLECİK': 11, 'BİNGÖL': 12, 'BİTLİS': 13, 'BOLU': 14, 'BURDUR': 15,
            'BURSA': 16, 'ÇANAKKALE': 17, 'ÇANKIRI': 18, 'ÇORUM': 19, 'DENİZLİ': 20,
            'DİYARBAKIR': 21, 'EDİRNE': 22, 'ELAZIĞ': 23, 'ERZİNCAN': 24, 'ERZURUM': 25,
            'ESKİŞEHİR': 26, 'GAZİANTEP': 27, 'GİRESUN': 28, 'GÜMÜŞHANE': 29, 'HAKKÂRİ': 30,
            'HATAY': 31, 'ISPARTA': 32, 'MERSİN': 33, 'İSTANBUL': 34, 'İZMİR': 35,
            'KARS': 36, 'KASTAMONU': 37, 'KAYSERİ': 38, 'KIRKLARELİ': 39, 'KIRŞEHİR': 40,
            'KOCAELİ': 41, 'KONYA': 42, 'KÜTAHYA': 43, 'MALATYA': 44, 'MANİSA': 45,
            'KAHRAMANMARAŞ': 46, 'MARDİN': 47, 'MUĞLA': 48, 'MUŞ': 49, 'NEVŞEHİR': 50,
            'NİĞDE': 51, 'ORDU': 52, 'RİZE': 53, 'SAKARYA': 54, 'SAMSUN': 55,
            'SİİRT': 56, 'SİNOP': 57, 'SİVAS': 58, 'TEKİRDAĞ': 59, 'TOKAT': 60,
            'TRABZON': 61, 'TUNCELİ': 62, 'ŞANLIURFA': 63, 'UŞAK': 64, 'VAN': 65,
            'YOZGAT': 66, 'ZONGULDAK': 67, 'AKSARAY': 68, 'BAYBURT': 69, 'KARAMAN': 70,
            'KIRIKKALE': 71, 'BATMAN': 72, 'ŞIRNAK': 73, 'BARTIN': 74, 'ARDAHAN': 75,
            'IĞDIR': 76, 'YALOVA': 77, 'KARABÜK': 78, 'KİLİS': 79, 'OSMANİYE': 80, 'DÜZCE': 81
        }
    
    def download_excel_file(self, output_path: str) -> bool:
        """Excel dosyasını indirir."""
        try:
            logger.info(f"Excel dosyası indiriliyor: {self.excel_url}")
            
            response = self.session.get(self.excel_url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Dosya boyutunu kontrol et
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                logger.info(f"Dosya boyutu: {size_mb:.2f} MB")
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"✅ Excel dosyası indirildi: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Excel dosyası indirilemedi: {e}")
            return False
    
    def read_excel_data(self, file_path: str) -> pd.DataFrame:
        """Excel dosyasını okur ve DataFrame döner."""
        try:
            logger.info("Excel dosyası okunuyor...")
            
            # Farklı sheet'leri dene
            excel_file = pd.ExcelFile(file_path)
            logger.info(f"Excel sheet'leri: {excel_file.sheet_names}")
            
            # İlk sheet'i oku (genellikle ana veri burada)
            df = pd.read_excel(file_path, sheet_name=0)
            
            logger.info(f"✅ Excel okundu: {len(df)} satır, {len(df.columns)} sütun")
            logger.info(f"Sütunlar: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Excel okunamadı: {e}")
            raise
    
    def clean_and_map_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Veriyi temizler ve standart formata dönüştürür."""
        logger.info("Veri temizleme ve eşleme başlıyor...")
        
        # Sütun adlarını standardize et
        df.columns = df.columns.str.strip().str.upper()
        
        # Sağlık Bakanlığı Excel yapısına göre direct mapping
        column_mapping = {}
        if 'KURUM ADI' in df.columns:
            column_mapping['KURUM ADI'] = 'kurum_adi'
        elif 'KURUM KODU' in df.columns:
            # İlk sheet'te kurum kodu ile kurum adı karışık, kurum adını kurum kodu sütunundan al
            column_mapping['KURUM KODU'] = 'kurum_adi'
        
        if 'İL' in df.columns:
            column_mapping['İL'] = 'il_adi'
        if 'İLÇE' in df.columns:
            column_mapping['İLÇE'] = 'ilce_adi'
        if 'KURUM TÜRÜ' in df.columns:
            column_mapping['KURUM TÜRÜ'] = 'kurum_tipi'
        
        # Sütunları yeniden adlandır
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        # Eğer kurum_adi hala yoksa, en uygun sütunu bul
        if 'kurum_adi' not in df.columns:
            # 5. sütun genellikle kurum adı ('KURUM ADI')
            if len(df.columns) >= 5:
                df['kurum_adi'] = df.iloc[:, 4]  # 5. sütun (0-indexli)
        
        # İl bilgisi yoksa 3. sütunu kullan
        if 'il_adi' not in df.columns and len(df.columns) >= 3:
            df['il_adi'] = df.iloc[:, 2]  # 3. sütun (0-indexli)
        
        # Kurum tipi yoksa 7. sütunu kullan
        if 'kurum_tipi' not in df.columns and len(df.columns) >= 7:
            df['kurum_tipi'] = df.iloc[:, 6]  # 7. sütun (0-indexli)
        
        # İlçe bilgisi yoksa 4. sütunu kullan
        if 'ilce_adi' not in df.columns and len(df.columns) >= 4:
            df['ilce_adi'] = df.iloc[:, 3]  # 4. sütun (0-indexli)
        
        # Veriyi temizle
        cleaned_data = []
        
        for _, row in df.iterrows():
            try:
                # Temel bilgileri al
                kurum_adi = self._clean_text(row.get('kurum_adi', ''))
                il_adi = self._clean_text(row.get('il_adi', ''))
                
                # Boş satırları atla
                if not kurum_adi or not il_adi or kurum_adi.isdigit():
                    continue
                
                # İl kodunu bul
                il_kodu = self.il_kodu_mapping.get(il_adi.upper(), 0)
                
                # Kurum tipini belirle
                kurum_tipi_raw = self._clean_text(row.get('kurum_tipi', ''))
                kurum_tipi = self._determine_kurum_tipi(kurum_adi, kurum_tipi_raw)
                
                # Temizlenmiş veri
                clean_row = {
                    'kurum_id': '',  # Sonra generate edilecek
                    'kurum_adi': kurum_adi,
                    'kurum_tipi': kurum_tipi,
                    'il_kodu': il_kodu,
                    'il_adi': il_adi.title(),
                    'ilce_adi': self._clean_text(row.get('ilce_adi', '')).title(),
                    'adres': self._clean_text(row.get('adres', '')),
                    'telefon': self._clean_phone(row.get('telefon', '')),
                    'koordinat_lat': None,
                    'koordinat_lon': None,
                    'web_sitesi': '',
                    'veri_kaynagi': 'Sağlık Bakanlığı Resmi Excel Listesi',
                    'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
                }
                
                cleaned_data.append(clean_row)
                
            except Exception as e:
                logger.warning(f"Satır işlenirken hata: {e}")
                continue
        
        result_df = pd.DataFrame(cleaned_data)
        logger.info(f"✅ {len(result_df)} satır temizlendi")
        
        return result_df
    
    def _clean_text(self, text: Any) -> str:
        """Metin verisini temizler."""
        if text is None:
            return ''
        
        # pandas.Series kontrolü
        if hasattr(text, 'empty'):
            if text.empty:
                return ''
            # Series ise ilk değeri al
            text = text.iloc[0] if len(text) > 0 else ''
        
        # pandas NaN kontrolü
        if pd.isna(text):
            return ''
        
        text = str(text).strip()
        # Çoklu boşlukları tek boşluğa çevir
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _clean_phone(self, phone: Any) -> str:
        """Telefon numarasını temizler."""
        if phone is None:
            return ''
        
        # pandas.Series kontrolü
        if hasattr(phone, 'empty'):
            if phone.empty:
                return ''
            phone = phone.iloc[0] if len(phone) > 0 else ''
        
        # pandas NaN kontrolü
        if pd.isna(phone):
            return ''
        
        phone = str(phone).strip()
        # Sadece rakamları al
        digits = re.sub(r'[^\d]', '', phone)
        
        # Türkiye formatına çevir
        if digits.startswith('90') and len(digits) == 12:
            return f"+{digits}"
        elif digits.startswith('0') and len(digits) == 11:
            return f"+90{digits[1:]}"
        elif len(digits) == 10:
            return f"+90{digits}"
        
        return phone if phone else ''
    
    def _determine_kurum_tipi(self, kurum_adi: str, kurum_tipi_col: str = '') -> str:
        """Kurum adından veya tip sütunundan kurum tipini belirler."""
        text = f"{kurum_adi} {kurum_tipi_col}".upper()
        
        # Öncelik sırasıyla kontrol et
        if any(keyword in text for keyword in ['ÜNİVERSİTE', 'TIP FAKÜLTESİ']):
            return 'Üniversite Hastanesi'
        elif any(keyword in text for keyword in ['EĞİTİM', 'ARAŞTIRMA']):
            return 'Eğitim ve Araştırma Hastanesi'
        elif any(keyword in text for keyword in ['ÖZEL', 'PRIVATE']):
            if 'HASTANE' in text:
                return 'Özel Hastane'
            elif any(keyword in text for keyword in ['POLİKLİNİK', 'KLINIK']):
                return 'Özel Poliklinik'
            else:
                return 'Özel Tıp Merkezi'
        elif any(keyword in text for keyword in ['ASM', 'AİLE SAĞLIĞI']):
            return 'Aile Sağlığı Merkezi'
        elif any(keyword in text for keyword in ['TSM', 'TOPLUM SAĞLIĞI']):
            return 'Toplum Sağlığı Merkezi'
        elif any(keyword in text for keyword in ['ADSM', 'AĞIZ', 'DİŞ']):
            return 'Ağız ve Diş Sağlığı Merkezi'
        elif any(keyword in text for keyword in ['DİYALİZ']):
            return 'Diyaliz Merkezi'
        elif any(keyword in text for keyword in ['FİZİK TEDAVİ', 'REHABİLİTASYON']):
            return 'Fizik Tedavi ve Rehabilitasyon Merkezi'
        elif any(keyword in text for keyword in ['AMBULANS']):
            return 'Ambulans İstasyonu'
        elif any(keyword in text for keyword in ['HASTANE', 'HASTANESİ']):
            return 'Devlet Hastanesi'
        else:
            return 'Devlet Hastanesi'  # Varsayılan
    
    def generate_file_hash(self, file_path: str) -> str:
        """Dosya hash'i üretir."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"Hash üretilirken hata: {e}")
            return ''
    
    def save_processed_data(self, df: pd.DataFrame, output_dir: str):
        """İşlenmiş veriyi kaydeder."""
        os.makedirs(output_dir, exist_ok=True)
        
        # CSV olarak kaydet
        csv_file = os.path.join(output_dir, 'saglik_bakanligi_tesisleri.csv')
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        logger.info(f"✅ CSV kaydedildi: {csv_file}")
        
        # JSON olarak kaydet
        json_file = os.path.join(output_dir, 'saglik_bakanligi_tesisleri.json')
        df.to_json(json_file, orient='records', force_ascii=False, indent=2)
        logger.info(f"✅ JSON kaydedildi: {json_file}")
        
        return csv_file, json_file

def main():
    """Ana fonksiyon."""
    logger.info("Sağlık Bakanlığı veri çekme işlemi başlıyor...")
    
    fetcher = SaglikBakanligiDataFetcher()
    
    # Geçici dosya yolları
    excel_file = 'temp_saglik_tesisleri.xls'
    output_dir = 'data/raw'
    
    try:
        # Excel dosyasını indir
        if not fetcher.download_excel_file(excel_file):
            raise Exception("Excel dosyası indirilemedi")
        
        # Excel'den tüm sheet'leri oku ve birleştir
        excel_file_obj = pd.ExcelFile(excel_file)
        all_data = []
        
        for sheet_name in excel_file_obj.sheet_names:
            logger.info(f"Sheet işleniyor: {sheet_name}")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Boş satırları temizle
            df = df.dropna(how='all')
            
            if len(df) > 0:
                # Her sheet için veri temizle
                cleaned_df = fetcher.clean_and_map_data(df)
                if len(cleaned_df) > 0:
                    all_data.append(cleaned_df)
        
        # Tüm veriyi birleştir
        if not all_data:
            raise Exception("Hiçbir sheet'ten veri çekilemedi")
        
        cleaned_df = pd.concat(all_data, ignore_index=True)
        
        if len(cleaned_df) == 0:
            raise Exception("Temizlenmiş veri bulunamadı")
        
        # Veriyi kaydet
        csv_file, json_file = fetcher.save_processed_data(cleaned_df, output_dir)
        
        # İstatistikler
        logger.info("=== ÖZET ===")
        logger.info(f"📊 Toplam tesis: {len(cleaned_df)}")
        logger.info(f"🏥 Kurum tipi dağılımı:")
        for tip, count in cleaned_df['kurum_tipi'].value_counts().head(10).items():
            logger.info(f"  {tip}: {count}")
        logger.info(f"🗺️ İl dağılımı (ilk 10):")
        for il, count in cleaned_df['il_adi'].value_counts().head(10).items():
            logger.info(f"  {il}: {count}")
        
        # Hash bilgisini kaydet
        file_hash = fetcher.generate_file_hash(excel_file)
        hash_info = {
            'download_date': datetime.now().isoformat(),
            'file_hash': file_hash,
            'record_count': len(cleaned_df),
            'source_url': fetcher.excel_url
        }
        
        with open(os.path.join(output_dir, 'saglik_bakanligi_hash.json'), 'w', encoding='utf-8') as f:
            json.dump(hash_info, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ Tüm işlemler tamamlandı!")
        
    except Exception as e:
        logger.error(f"❌ İşlem başarısız: {e}")
        raise
    
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(excel_file):
            os.remove(excel_file)
            logger.info("🗑️ Geçici dosya temizlendi")

if __name__ == "__main__":
    main()
