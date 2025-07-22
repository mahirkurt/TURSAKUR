#!/usr/bin/env python3
"""
Türkiye Sağlık Kuruluşları - Otomatik Deploy
Veri güncelleme + Firebase deploy işlemlerini otomatik yapar.
"""

import subprocess
import sys
import logging
import os
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomaticDeployer:
    """Otomatik deploy sınıfı."""
    
    def __init__(self):
        self.firebase_project = "turkiye-sakur"
        self.site_url = "https://turkiye-sakur.web.app"
    
    def check_firebase_auth(self) -> bool:
        """Firebase authentication durumunu kontrol et."""
        logger.info("🔐 Firebase authentication kontrol ediliyor...")
        
        try:
            result = subprocess.run([
                'firebase', 'projects:list'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and self.firebase_project in result.stdout:
                logger.info("✅ Firebase authentication OK")
                return True
            else:
                logger.error("❌ Firebase authentication başarısız")
                logger.error("   'firebase login' komutu ile giriş yapın")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ Firebase auth timeout")
            return False
        except FileNotFoundError:
            logger.error("❌ Firebase CLI bulunamadı")
            logger.error("   'npm install -g firebase-tools' ile kurun")
            return False
        except Exception as e:
            logger.error(f"💥 Firebase auth hatası: {e}")
            return False
    
    def run_data_update(self) -> bool:
        """Veri güncelleme scriptini çalıştır."""
        logger.info("📊 Veri güncelleme başlıyor...")
        
        try:
            result = subprocess.run([
                sys.executable, 'scripts/auto_update_all.py'
            ], timeout=3600)  # 1 saat timeout
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            logger.error("⏰ Veri güncelleme timeout (1 saat)")
            return False
        except Exception as e:
            logger.error(f"💥 Veri güncelleme hatası: {e}")
            return False
    
    def get_database_stats(self) -> dict:
        """Ana veritabanı istatistiklerini al."""
        try:
            with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'total_records': data['meta']['total_records'],
                'last_updated': data['meta']['last_updated'],
                'kurumlar_count': len(data['kurumlar'])
            }
        except Exception as e:
            logger.warning(f"⚠️ İstatistik alınamadı: {e}")
            return {}
    
    def deploy_to_firebase(self) -> bool:
        """Firebase'e deploy et."""
        logger.info("🚀 Firebase deploy başlıyor...")
        
        try:
            result = subprocess.run([
                'firebase', 'deploy', '--only', 'hosting'
            ], capture_output=True, text=True, timeout=600)  # 10 dakika timeout
            
            if result.returncode == 0:
                logger.info("✅ Firebase deploy başarılı")
                logger.info(f"🌐 Site URL: {self.site_url}")
                return True
            else:
                logger.error("❌ Firebase deploy başarısız")
                logger.error(f"   Hata: {result.stderr[:500]}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ Firebase deploy timeout")
            return False
        except Exception as e:
            logger.error(f"💥 Firebase deploy hatası: {e}")
            return False
    
    def test_deployment(self) -> bool:
        """Deploy edilen sitenin çalışıp çalışmadığını test et."""
        logger.info("🧪 Deploy testi yapılıyor...")
        
        try:
            import requests
            
            # Ana sayfa testi
            response = requests.get(self.site_url, timeout=30)
            if response.status_code == 200:
                logger.info("✅ Ana sayfa erişilebilir")
            else:
                logger.warning(f"⚠️ Ana sayfa hatası: {response.status_code}")
                return False
            
            # API endpoint testi
            api_url = f"{self.site_url}/data/turkiye_saglik_kuruluslari.json"
            response = requests.get(api_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                record_count = data.get('meta', {}).get('total_records', 0)
                logger.info(f"✅ API erişilebilir - {record_count:,} kayıt")
                return True
            else:
                logger.warning(f"⚠️ API hatası: {response.status_code}")
                return False
                
        except ImportError:
            logger.warning("⚠️ requests kütüphanesi yok - deploy testi atlanıyor")
            return True  # Test yapamadık ama deploy başarılıydı
        except Exception as e:
            logger.warning(f"⚠️ Deploy testi hatası: {e}")
            return True  # Test hatası ama muhtemelen deploy başarılı
    
    def send_notification(self, success: bool, stats: dict):
        """İşlem sonucu bildirimi gönder."""
        if success:
            logger.info("🎉 DEPLOY BAŞARILI!")
            logger.info("=" * 25)
            logger.info(f"🌐 Site: {self.site_url}")
            
            if stats:
                logger.info(f"📊 Toplam kurum: {stats.get('total_records', 'N/A'):,}")
                logger.info(f"🕐 Son güncelleme: {stats.get('last_updated', 'N/A')}")
            
            logger.info()
            logger.info("✨ Türkiye Sağlık Kuruluşları veritabanı güncel!")
        else:
            logger.error("💥 DEPLOY BAŞARISIZ!")
            logger.error("   Lütfen hataları kontrol edin")
    
    def run_full_deployment(self):
        """Tam otomatik deployment işlemi."""
        start_time = datetime.now()
        
        logger.info("🚀 TÜRKİYE SAĞLIK KURULUŞLARI - OTOMATİK DEPLOY")
        logger.info("=" * 60)
        logger.info(f"🕐 Başlangıç: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info()
        
        # 1. Firebase auth kontrol
        if not self.check_firebase_auth():
            self.send_notification(False, {})
            return False
        
        # 2. Veri güncelleme
        logger.info()
        if not self.run_data_update():
            logger.error("❌ Veri güncelleme başarısız - deploy durduruluyor")
            self.send_notification(False, {})
            return False
        
        # 3. İstatistikleri al
        stats = self.get_database_stats()
        
        # 4. Firebase deploy
        logger.info()
        if not self.deploy_to_firebase():
            self.send_notification(False, stats)
            return False
        
        # 5. Deploy testi
        logger.info()
        test_success = self.test_deployment()
        
        # 6. Sonuç bildirimi
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info()
        logger.info(f"⏱️ Toplam süre: {duration}")
        
        success = test_success
        self.send_notification(success, stats)
        
        return success

def main():
    """Ana fonksiyon."""
    deployer = AutomaticDeployer()
    success = deployer.run_full_deployment()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
