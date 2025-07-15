#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Üç Aylık Otomatik Güncelleme Modülü

Bu modül, 3 ayda bir çalışarak tüm sağlık kurumu verilerini günceller,
değişiklikleri analiz eder ve raporlar.

Author: TURSAKUR Team
Version: 1.0.0
Date: 2025-01-14
"""

import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple
import difflib
from dataclasses import dataclass, asdict
from pathlib import Path

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/quarterly_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class HealthInstitution:
    """Sağlık kurumu veri yapısı"""
    kurum_id: str
    kurum_adi: str
    kurum_tipi: str
    il_kodu: int
    il_adi: str
    ilce_adi: str
    adres: str
    telefon: str
    koordinat_lat: float
    koordinat_lon: float
    web_sitesi: str
    veri_kaynagi: str
    son_guncelleme: str

@dataclass
class ChangeAnalysis:
    """Değişiklik analizi veri yapısı"""
    new_institutions: List[HealthInstitution]
    removed_institutions: List[HealthInstitution]
    modified_institutions: List[Tuple[HealthInstitution, HealthInstitution]]  # (old, new)
    unchanged_count: int

class QuarterlyUpdater:
    """Üç aylık güncelleme sınıfı"""
    
    def __init__(self):
        self.backup_dir = f"backups/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        self.current_data_file = 'data/turkiye_saglik_kuruluslari.json'
        self.temp_data_file = 'data/turkiye_saglik_kuruluslari_temp.json'
        
    def should_run_update(self) -> bool:
        """Güncellemenin çalıştırılıp çalıştırılmayacağını kontrol et"""
        
        # Son güncelleme tarihini kontrol et
        metadata_file = 'data/update_metadata.json'
        
        if not os.path.exists(metadata_file):
            logger.info("İlk güncelleme - çalıştırılacak")
            return True
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            last_update = datetime.fromisoformat(metadata.get('last_update', '2020-01-01'))
            next_update = last_update + timedelta(days=90)  # 3 ay
            
            if datetime.now() >= next_update:
                logger.info(f"Son güncelleme: {last_update.strftime('%Y-%m-%d')}, güncelleme zamanı geldi")
                return True
            else:
                logger.info(f"Henüz güncelleme zamanı değil. Sonraki güncelleme: {next_update.strftime('%Y-%m-%d')}")
                return False
                
        except Exception as e:
            logger.warning(f"Metadata kontrol hatası: {e} - Güncelleme çalıştırılacak")
            return True
    
    def create_backup(self) -> bool:
        """Mevcut verilerin yedeğini oluştur"""
        try:
            logger.info(f"Backup oluşturuluyor: {self.backup_dir}")
            
            # Backup dizinini oluştur
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Ana veri dosyasını yedekle
            if os.path.exists(self.current_data_file):
                backup_file = os.path.join(self.backup_dir, 'turkiye_saglik_kuruluslari.json')
                shutil.copy2(self.current_data_file, backup_file)
                logger.info(f"Ana veri dosyası yedeklendi: {backup_file}")
            
            # Raw data klasörünü yedekle
            raw_data_dir = 'data/raw'
            if os.path.exists(raw_data_dir):
                backup_raw_dir = os.path.join(self.backup_dir, 'raw')
                shutil.copytree(raw_data_dir, backup_raw_dir)
                logger.info(f"Raw data klasörü yedeklendi: {backup_raw_dir}")
            
            # Log dosyalarını yedekle
            logs_dir = 'logs'
            if os.path.exists(logs_dir):
                backup_logs_dir = os.path.join(self.backup_dir, 'logs')
                shutil.copytree(logs_dir, backup_logs_dir)
                logger.info(f"Log dosyaları yedeklendi: {backup_logs_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"Backup oluşturma hatası: {e}")
            return False
    
    def load_current_data(self) -> List[HealthInstitution]:
        """Mevcut veriyi yükle"""
        try:
            if not os.path.exists(self.current_data_file):
                logger.info("Mevcut veri dosyası bulunamadı - ilk çalıştırma")
                return []
            
            with open(self.current_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            institutions = []
            for item in data:
                institution = HealthInstitution(**item)
                institutions.append(institution)
            
            logger.info(f"Mevcut veri yüklendi: {len(institutions)} kurum")
            return institutions
            
        except Exception as e:
            logger.error(f"Mevcut veri yükleme hatası: {e}")
            return []
    
    def run_data_collection(self) -> bool:
        """Yeni veri toplama işlemini çalıştır"""
        try:
            logger.info("Yeni veri toplama işlemi başlatılıyor...")
            
            collection_script = 'scripts/fetch_all_sources.py'
            
            if not os.path.exists(collection_script):
                logger.error(f"Veri toplama script'i bulunamadı: {collection_script}")
                return False
            
            # Veri toplama script'ini çalıştır
            result = subprocess.run(
                [sys.executable, collection_script],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=3600  # 1 saat timeout
            )
            
            if result.returncode == 0:
                logger.info("Veri toplama başarıyla tamamlandı")
                
                # Yeni veriyi temp dosyaya taşı
                if os.path.exists(self.current_data_file):
                    shutil.move(self.current_data_file, self.temp_data_file)
                    logger.info("Yeni veri geçici dosyaya taşındı")
                
                return True
            else:
                logger.error(f"Veri toplama hatası: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Veri toplama timeout ile sonlandı")
            return False
        except Exception as e:
            logger.error(f"Veri toplama exception: {e}")
            return False
    
    def load_new_data(self) -> List[HealthInstitution]:
        """Yeni toplanan veriyi yükle"""
        try:
            if not os.path.exists(self.temp_data_file):
                logger.error("Yeni veri dosyası bulunamadı")
                return []
            
            with open(self.temp_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            institutions = []
            for item in data:
                institution = HealthInstitution(**item)
                institutions.append(institution)
            
            logger.info(f"Yeni veri yüklendi: {len(institutions)} kurum")
            return institutions
            
        except Exception as e:
            logger.error(f"Yeni veri yükleme hatası: {e}")
            return []
    
    def analyze_changes(self, old_data: List[HealthInstitution], 
                       new_data: List[HealthInstitution]) -> ChangeAnalysis:
        """Değişiklikleri analiz et"""
        logger.info("Değişiklik analizi başlatılıyor...")
        
        # ID bazında mapping oluştur
        old_by_id = {inst.kurum_id: inst for inst in old_data}
        new_by_id = {inst.kurum_id: inst for inst in new_data}
        
        # İsim bazında mapping (ID değişebilir)
        old_by_name = {self._normalize_name(inst.kurum_adi): inst for inst in old_data}
        new_by_name = {self._normalize_name(inst.kurum_adi): inst for inst in new_data}
        
        new_institutions = []
        removed_institutions = []
        modified_institutions = []
        unchanged_count = 0
        
        # Yeni kurumları bul
        for inst in new_data:
            if inst.kurum_id not in old_by_id:
                # İsim bazında da kontrol et
                norm_name = self._normalize_name(inst.kurum_adi)
                if norm_name not in old_by_name:
                    new_institutions.append(inst)
        
        # Kaldırılan kurumları bul
        for inst in old_data:
            if inst.kurum_id not in new_by_id:
                # İsim bazında da kontrol et
                norm_name = self._normalize_name(inst.kurum_adi)
                if norm_name not in new_by_name:
                    removed_institutions.append(inst)
        
        # Değiştirilen kurumları bul
        for inst_id in old_by_id:
            if inst_id in new_by_id:
                old_inst = old_by_id[inst_id]
                new_inst = new_by_id[inst_id]
                
                if self._has_significant_changes(old_inst, new_inst):
                    modified_institutions.append((old_inst, new_inst))
                else:
                    unchanged_count += 1
        
        analysis = ChangeAnalysis(
            new_institutions=new_institutions,
            removed_institutions=removed_institutions,
            modified_institutions=modified_institutions,
            unchanged_count=unchanged_count
        )
        
        logger.info(f"Değişiklik analizi tamamlandı:")
        logger.info(f"  Yeni: {len(new_institutions)}")
        logger.info(f"  Kaldırılan: {len(removed_institutions)}")
        logger.info(f"  Değiştirilen: {len(modified_institutions)}")
        logger.info(f"  Değişmeyen: {unchanged_count}")
        
        return analysis
    
    def _normalize_name(self, name: str) -> str:
        """Kurum adını normalize et"""
        if not name:
            return ""
        
        # Küçük harfe çevir ve fazla boşlukları kaldır
        normalized = name.lower().strip()
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _has_significant_changes(self, old_inst: HealthInstitution, 
                                new_inst: HealthInstitution) -> bool:
        """Anlamlı değişiklik olup olmadığını kontrol et"""
        
        # Önemli alanları karşılaştır
        significant_fields = [
            'kurum_adi', 'kurum_tipi', 'adres', 'telefon', 
            'koordinat_lat', 'koordinat_lon', 'web_sitesi'
        ]
        
        for field in significant_fields:
            old_value = getattr(old_inst, field)
            new_value = getattr(new_inst, field)
            
            # None değerleri boş string olarak kabul et
            old_value = old_value if old_value is not None else ""
            new_value = new_value if new_value is not None else ""
            
            if str(old_value).strip() != str(new_value).strip():
                return True
        
        return False
    
    def generate_change_report(self, analysis: ChangeAnalysis) -> str:
        """Değişiklik raporu oluştur"""
        
        report = f"""
=== TURSAKUR ÜÇ AYLIK GÜNCELLEME RAPORU ===
Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 DEĞİŞİKLİK ÖZETİ:
➕ Yeni kurumlar: {len(analysis.new_institutions)}
➖ Kaldırılan kurumlar: {len(analysis.removed_institutions)}
🔄 Güncellenen kurumlar: {len(analysis.modified_institutions)}
✅ Değişmeyen kurumlar: {analysis.unchanged_count}

Toplam kurum sayısı: {len(analysis.new_institutions) + len(analysis.removed_institutions) + 
                      len(analysis.modified_institutions) + analysis.unchanged_count}

"""
        
        # Yeni kurumlar
        if analysis.new_institutions:
            report += "📈 YENİ KURUMLAR:\n"
            for inst in analysis.new_institutions[:10]:  # İlk 10'u göster
                report += f"  ✅ {inst.kurum_adi} ({inst.il_adi}) - {inst.kurum_tipi}\n"
            
            if len(analysis.new_institutions) > 10:
                report += f"  ... ve {len(analysis.new_institutions) - 10} kurum daha\n"
            report += "\n"
        
        # Kaldırılan kurumlar
        if analysis.removed_institutions:
            report += "📉 KALDIRILAN KURUMLAR:\n"
            for inst in analysis.removed_institutions[:10]:  # İlk 10'u göster
                report += f"  ❌ {inst.kurum_adi} ({inst.il_adi}) - {inst.kurum_tipi}\n"
            
            if len(analysis.removed_institutions) > 10:
                report += f"  ... ve {len(analysis.removed_institutions) - 10} kurum daha\n"
            report += "\n"
        
        # Güncellenen kurumlar
        if analysis.modified_institutions:
            report += "🔄 GÜNCELLENENLİK KURUMLAR:\n"
            for old_inst, new_inst in analysis.modified_institutions[:5]:  # İlk 5'i göster
                report += f"  📝 {new_inst.kurum_adi} ({new_inst.il_adi})\n"
                
                # Değişiklikleri detaylandır
                changes = []
                if old_inst.kurum_adi != new_inst.kurum_adi:
                    changes.append(f"Ad: '{old_inst.kurum_adi}' → '{new_inst.kurum_adi}'")
                if old_inst.adres != new_inst.adres:
                    changes.append("Adres değişti")
                if old_inst.telefon != new_inst.telefon:
                    changes.append(f"Telefon: '{old_inst.telefon}' → '{new_inst.telefon}'")
                
                for change in changes[:3]:  # En fazla 3 değişiklik göster
                    report += f"     • {change}\n"
            
            if len(analysis.modified_institutions) > 5:
                report += f"  ... ve {len(analysis.modified_institutions) - 5} kurum daha\n"
            report += "\n"
        
        # İstatistikler
        total_changes = len(analysis.new_institutions) + len(analysis.removed_institutions) + len(analysis.modified_institutions)
        total_institutions = total_changes + analysis.unchanged_count
        
        if total_institutions > 0:
            change_rate = (total_changes / total_institutions) * 100
            report += f"📊 İSTATİSTİKLER:\n"
            report += f"Değişim oranı: {change_rate:.1f}%\n"
            report += f"Veri kalitesi: {'Yüksek' if change_rate < 10 else 'Orta' if change_rate < 25 else 'Düşük'}\n"
        
        report += f"\n⏱️  Güncelleme tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report
    
    def finalize_update(self, analysis: ChangeAnalysis) -> bool:
        """Güncellemeyi sonlandır"""
        try:
            # Yeni veriyi ana dosyaya taşı
            if os.path.exists(self.temp_data_file):
                shutil.move(self.temp_data_file, self.current_data_file)
                logger.info("Yeni veri ana dosyaya taşındı")
            
            # Metadata güncelle
            metadata = {
                'last_update': datetime.now().isoformat(),
                'new_institutions': len(analysis.new_institutions),
                'removed_institutions': len(analysis.removed_institutions),
                'modified_institutions': len(analysis.modified_institutions),
                'unchanged_count': analysis.unchanged_count,
                'backup_location': self.backup_dir
            }
            
            with open('data/update_metadata.json', 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info("Metadata güncellendi")
            return True
            
        except Exception as e:
            logger.error(f"Güncelleme sonlandırma hatası: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """Eski backup'ları temizle"""
        try:
            backups_dir = Path('backups')
            if not backups_dir.exists():
                return
            
            # Backup klasörlerini tarihe göre sırala
            backup_dirs = [d for d in backups_dir.iterdir() if d.is_dir()]
            backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Fazla backup'ları sil
            for backup_dir in backup_dirs[keep_count:]:
                shutil.rmtree(backup_dir)
                logger.info(f"Eski backup silindi: {backup_dir}")
                
        except Exception as e:
            logger.warning(f"Backup temizleme hatası: {e}")

def main():
    """Ana fonksiyon"""
    try:
        logger.info("TURSAKUR üç aylık güncelleme kontrolleri başlatılıyor...")
        
        updater = QuarterlyUpdater()
        
        # Güncelleme gerekli mi kontrol et
        if not updater.should_run_update():
            logger.info("Güncelleme gerekli değil")
            return 0
        
        # 1. Backup oluştur
        print("💾 Mevcut veriler yedekleniyor...")
        if not updater.create_backup():
            logger.error("Backup oluşturulamadı - güncelleme iptal ediliyor")
            return 1
        
        # 2. Mevcut veriyi yükle
        print("📊 Mevcut veriler yükleniyor...")
        old_data = updater.load_current_data()
        
        # 3. Yeni veri toplama
        print("🔄 Yeni veriler toplanıyor...")
        if not updater.run_data_collection():
            logger.error("Veri toplama başarısız - güncelleme iptal ediliyor")
            return 1
        
        # 4. Yeni veriyi yükle
        print("📥 Yeni veriler yükleniyor...")
        new_data = updater.load_new_data()
        
        if not new_data:
            logger.error("Yeni veri yüklenemedi - güncelleme iptal ediliyor")
            return 1
        
        # 5. Değişiklikleri analiz et
        print("🔍 Değişiklikler analiz ediliyor...")
        analysis = updater.analyze_changes(old_data, new_data)
        
        # 6. Rapor oluştur
        report = updater.generate_change_report(analysis)
        print(report)
        
        # Raporu dosyaya kaydet
        report_file = f"logs/quarterly_report_{datetime.now().strftime('%Y-%m-%d')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 7. Güncellemeyi sonlandır
        print("✅ Güncelleme sonlandırılıyor...")
        if not updater.finalize_update(analysis):
            logger.error("Güncelleme sonlandırılamadı")
            return 1
        
        # 8. Eski backup'ları temizle
        updater.cleanup_old_backups()
        
        logger.info("Üç aylık güncelleme başarıyla tamamlandı!")
        return 0
        
    except Exception as e:
        logger.error(f"Ana fonksiyon kritik hatası: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
