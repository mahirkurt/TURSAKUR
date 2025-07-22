#!/usr/bin/env python3
"""
Türkiye Sağlık Kuruluşları - Otomatik Veri Güncelleme
Tüm çalışan scriptleri sırayla çalıştırır ve veritabanını günceller.
"""

import subprocess
import sys
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomaticDataUpdater:
    """Otomatik veri güncelleme sınıfı."""
    
    def __init__(self):
        self.scripts_dir = "scripts"
        self.success_count = 0
        self.total_count = 0
        
        # Çalıştırılacak scriptler (öncelik sırasına göre)
        self.scripts = [
            {
                'file': 'fetch_trhastane_data.py',
                'name': 'TR Hastane Verileri',
                'priority': 1,
                'expected_output': 'trhastane_data.json'
            },
            {
                'file': 'fetch_universite_hastaneleri.py', 
                'name': 'Üniversite Hastaneleri',
                'priority': 2,
                'expected_output': 'universite_hastaneleri.json'
            },
            {
                'file': 'fetch_vikipedia_gelismis_kesfet.py',
                'name': 'Vikipedia Gelişmiş Keşif',
                'priority': 3,
                'expected_output': 'vikipedia_gelismis_kesfet.json'
            },
            {
                'file': 'fetch_sgk_sigorta_yeni_kaynaklar.py',
                'name': 'SGK ve Sigorta Kaynakları',
                'priority': 4,
                'expected_output': 'sgk_sigorta_yeni_kaynaklar.json',
                'optional': True  # Server sorunları olabilir
            },
            {
                'file': 'fetch_saglik_bakanligi_yeni_kaynaklar.py',
                'name': 'Sağlık Bakanlığı Yeni Kaynaklar',
                'priority': 5,
                'expected_output': 'saglik_bakanligi_yeni_kaynaklar.json',
                'optional': True  # Server sorunları olabilir
            },
            {
                'file': 'fetch_ozel_hastaneler_yeni_kaynaklar.py',
                'name': 'Özel Hastaneler Yeni Kaynaklar',
                'priority': 6,
                'expected_output': 'ozel_hastaneler_yeni_kaynaklar.json',
                'optional': True  # Server sorunları olabilir
            }
        ]
    
    def run_script(self, script: dict) -> bool:
        """Bir scripti çalıştır ve sonucunu kontrol et."""
        script_path = os.path.join(self.scripts_dir, script['file'])
        
        if not os.path.exists(script_path):
            logger.warning(f"❌ Script bulunamadı: {script['file']}")
            return False
        
        logger.info(f"🚀 Çalıştırılıyor: {script['name']}")
        logger.info(f"   Dosya: {script['file']}")
        
        try:
            # Scripti çalıştır
            result = subprocess.run([
                sys.executable, script_path
            ], capture_output=True, text=True, timeout=1800)  # 30 dakika timeout
            
            # Çıktıyı kontrol et
            if result.returncode == 0:
                logger.info(f"✅ {script['name']} başarılı")
                
                # Output dosyasını kontrol et
                if self.check_output_file(script):
                    logger.info(f"   📁 Çıktı dosyası oluşturuldu: {script['expected_output']}")
                    return True
                else:
                    logger.warning(f"   ⚠️ Çıktı dosyası bulunamadı: {script['expected_output']}")
                    return script.get('optional', False)  # Optional scriptler için ok
            else:
                # Hata durumu
                logger.error(f"❌ {script['name']} başarısız")
                logger.error(f"   Hata kodu: {result.returncode}")
                if result.stderr:
                    logger.error(f"   Hata: {result.stderr[:500]}")
                
                return script.get('optional', False)  # Optional scriptler için devam et
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {script['name']} zaman aşımı (30dk)")
            return script.get('optional', False)
        except Exception as e:
            logger.error(f"💥 {script['name']} çalıştırma hatası: {e}")
            return script.get('optional', False)
    
    def check_output_file(self, script: dict) -> bool:
        """Script çıktı dosyasının var olup olmadığını kontrol et."""
        output_path = os.path.join('data', 'raw', script['expected_output'])
        return os.path.exists(output_path)
    
    def run_data_processing(self) -> bool:
        """Ana veri işleme scriptini çalıştır."""
        logger.info("🔄 Ana veri işleme başlıyor...")
        
        try:
            result = subprocess.run([
                sys.executable, os.path.join(self.scripts_dir, 'process_data.py')
            ], capture_output=True, text=True, timeout=300)  # 5 dakika timeout
            
            if result.returncode == 0:
                logger.info("✅ Ana veri işleme başarılı")
                return True
            else:
                logger.error(f"❌ Ana veri işleme başarısız: {result.stderr[:500]}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Ana veri işleme hatası: {e}")
            return False
    
    def copy_to_public(self) -> bool:
        """Güncellenmiş veriyi public klasörüne kopyala."""
        logger.info("📁 Public klasörüne kopyalama...")
        
        try:
            import shutil
            
            source = 'data/turkiye_saglik_kuruluslari.json'
            destination = 'public/data/turkiye_saglik_kuruluslari.json'
            
            if os.path.exists(source):
                shutil.copy2(source, destination)
                logger.info(f"✅ Dosya kopyalandı: {destination}")
                return True
            else:
                logger.error(f"❌ Kaynak dosya bulunamadı: {source}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Kopyalama hatası: {e}")
            return False
    
    def run_all_updates(self):
        """Tüm güncellemeleri sırayla çalıştır."""
        start_time = datetime.now()
        logger.info("🎯 TÜRKİYE SAĞLIK KURULUŞLARI - OTOMATİK VERİ GÜNCELLEMESİ")
        logger.info("=" * 70)
        logger.info(f"🕐 Başlangıç zamanı: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        
        # 1. Tüm data collection scriptlerini çalıştır
        logger.info("📊 VERİ TOPLAMA AŞAMASI")
        logger.info("-" * 30)
        
        for script in self.scripts:
            self.total_count += 1
            if self.run_script(script):
                self.success_count += 1
            logger.info("")  # Boş satır
        
        # 2. Ana veri işleme
        logger.info("🔄 VERİ İŞLEME AŞAMASI")
        logger.info("-" * 25)
        processing_success = self.run_data_processing()
        logger.info("")
        
        # 3. Public klasörüne kopyalama
        logger.info("📁 DEPLOY HAZIRLIĞI")
        logger.info("-" * 20)
        copy_success = self.copy_to_public()
        logger.info("")
        
        # Sonuç özeti
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("🎊 İŞLEM SONUCU")
        logger.info("=" * 20)
        logger.info(f"✅ Başarılı scriptler: {self.success_count}/{self.total_count}")
        logger.info(f"🔄 Veri işleme: {'✅ Başarılı' if processing_success else '❌ Başarısız'}")
        logger.info(f"📁 Deploy hazırlığı: {'✅ Başarılı' if copy_success else '❌ Başarısız'}")
        logger.info(f"⏱️ Toplam süre: {duration}")
        logger.info("")
        
        if processing_success and copy_success:
            logger.info("🚀 VERİTABANI HAZIR - Firebase deploy için:")
            logger.info("   firebase deploy --only hosting")
            return True
        else:
            logger.error("❌ İşlem tamamlanamadı!")
            return False

def main():
    """Ana fonksiyon."""
    updater = AutomaticDataUpdater()
    success = updater.run_all_updates()
    
    if success:
        logger.info("✨ Otomatik güncelleme tamamlandı!")
        sys.exit(0)
    else:
        logger.error("💥 Otomatik güncelleme başarısız!")
        sys.exit(1)

if __name__ == "__main__":
    main()
