#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otomatik Coğrafi Düzeltme ve Eşleme Sistemi
Mevcut verileri Türkiye'nin resmi 81 il ve ilçe verileriyle eşler
"""

import json
import logging
from typing import Dict, List, Optional
from turkey_geo_mapper import TurkeyGeoMapper

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('geo_correction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GeoCorrector:
    """Coğrafi veri düzeltici sınıfı"""
    
    def __init__(self):
        self.mapper = TurkeyGeoMapper()
        self.corrections_made = []
        self.invalid_records = []
        self.stats = {
            "total_processed": 0,
            "corrected": 0,
            "invalid": 0,
            "unchanged": 0
        }
    
    def correct_institution_geography(self, institution: Dict) -> Dict:
        """Bir kurumun coğrafi bilgilerini düzelt"""
        original = institution.copy()
        
        # Mevcut il ve ilçe bilgileri
        current_province = institution.get('il_adi', '')
        current_district = institution.get('ilce_adi', '')
        current_il_kodu = institution.get('il_kodu')
        
        # Coğrafi doğrulama
        validation = self.mapper.validate_geography(current_province, current_district)
        
        if validation["valid"]:
            # Düzeltmeleri uygula
            institution['il_kodu'] = validation["province_code"]
            institution['il_adi'] = validation["province_name"]
            institution['ilce_adi'] = validation["district_name"]
            
            # İstatistikleri güncelle
            if validation["corrections"]:
                self.stats["corrected"] += 1
                self.corrections_made.append({
                    "kurum_id": institution.get('kurum_id', 'unknown'),
                    "kurum_adi": institution.get('kurum_adi', 'unknown'),
                    "original": {
                        "il_kodu": current_il_kodu,
                        "il_adi": current_province,
                        "ilce_adi": current_district
                    },
                    "corrected": {
                        "il_kodu": validation["province_code"],
                        "il_adi": validation["province_name"],
                        "ilce_adi": validation["district_name"]
                    },
                    "corrections": validation["corrections"]
                })
                
                logger.info(f"✅ Düzeltildi: {institution.get('kurum_adi', 'unknown')} - "
                           f"{current_province}/{current_district} → "
                           f"{validation['province_name']}/{validation['district_name']}")
            else:
                self.stats["unchanged"] += 1
        else:
            self.stats["invalid"] += 1
            self.invalid_records.append({
                "kurum_id": institution.get('kurum_id', 'unknown'),
                "kurum_adi": institution.get('kurum_adi', 'unknown'),
                "il_adi": current_province,
                "ilce_adi": current_district,
                "reason": "Geçersiz coğrafi bilgi"
            })
            
            logger.warning(f"❌ Geçersiz coğrafi bilgi: {institution.get('kurum_adi', 'unknown')} - "
                          f"{current_province}/{current_district}")
        
        self.stats["total_processed"] += 1
        return institution
    
    def process_data_file(self, input_file: str, output_file: str) -> Dict:
        """Veri dosyasını işle ve düzelt"""
        logger.info(f"🔄 Coğrafi düzeltme başlatılıyor: {input_file}")
        
        try:
            # Veriyi yükle
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Meta veriyi kontrol et
            if isinstance(data, dict) and 'kurumlar' in data:
                institutions = data['kurumlar']
                metadata = data.get('metadata', {})
            else:
                institutions = data if isinstance(data, list) else []
                metadata = {}
            
            logger.info(f"📊 Toplam {len(institutions)} kurum yüklendi")
            
            # Her kurumu işle
            corrected_institutions = []
            for i, institution in enumerate(institutions, 1):
                if i % 100 == 0:
                    logger.info(f"⏳ İşlendi: {i}/{len(institutions)}")
                
                corrected = self.correct_institution_geography(institution)
                corrected_institutions.append(corrected)
            
            # Metadata'yı güncelle
            metadata.update({
                "total_kurumlar": len(corrected_institutions),
                "total_iller": 81,  # Türkiye'nin resmi il sayısı
                "geo_correction_applied": True,
                "geo_correction_stats": self.stats.copy()
            })
            
            # Sonucu kaydet
            result_data = {
                "metadata": metadata,
                "kurumlar": corrected_institutions
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Coğrafi düzeltme tamamlandı: {output_file}")
            return self.get_summary()
            
        except Exception as e:
            logger.error(f"❌ Hata: {e}")
            raise
    
    def get_summary(self) -> Dict:
        """Düzeltme özetini döndür"""
        return {
            "stats": self.stats,
            "corrections_count": len(self.corrections_made),
            "invalid_count": len(self.invalid_records),
            "success_rate": (self.stats["total_processed"] - self.stats["invalid"]) / max(1, self.stats["total_processed"]) * 100
        }
    
    def export_correction_report(self, report_file: str):
        """Düzeltme raporunu dışa aktar"""
        report = {
            "summary": self.get_summary(),
            "corrections": self.corrections_made,
            "invalid_records": self.invalid_records,
            "geographic_standards": {
                "total_provinces": 81,
                "source": "T.C. İçişleri Bakanlığı",
                "note": "Türkiye'nin resmi 81 il ve bağlı ilçeleri kullanılmıştır"
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📋 Düzeltme raporu kaydedildi: {report_file}")

def main():
    """Ana fonksiyon"""
    print("🗺️ OTOMATİK COĞRAFİ DÜZELTME SİSTEMİ")
    print("=" * 50)
    print("Türkiye'nin resmi 81 il ve ilçe verilerine göre düzeltme yapılıyor...")
    
    corrector = GeoCorrector()
    
    try:
        # Ana veri dosyasını düzelt
        summary = corrector.process_data_file(
            'data/turkiye_saglik_kuruluslari.json',
            'data/turkiye_saglik_kuruluslari_geo_corrected.json'
        )
        
        # Rapor oluştur
        corrector.export_correction_report('geo_correction_report.json')
        
        # Özet rapor
        print("\n📋 DÜZELTME ÖZETİ")
        print("=" * 30)
        print(f"Toplam işlenen: {summary['stats']['total_processed']}")
        print(f"Düzeltilen: {summary['stats']['corrected']}")
        print(f"Değişmeyen: {summary['stats']['unchanged']}")
        print(f"Geçersiz: {summary['stats']['invalid']}")
        print(f"Başarı oranı: {summary['success_rate']:.1f}%")
        
        if summary['corrections_count'] > 0:
            print(f"\n✅ {summary['corrections_count']} coğrafi düzeltme yapıldı")
            
        if summary['invalid_count'] > 0:
            print(f"\n⚠️ {summary['invalid_count']} geçersiz kayıt tespit edildi")
        
        print(f"\n💡 Artık sistemde Türkiye'nin resmi 81 ili standardında veri var!")
        
    except Exception as e:
        logger.error(f"❌ Düzeltme hatası: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
