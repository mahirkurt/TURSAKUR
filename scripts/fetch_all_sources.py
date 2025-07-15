#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tüm Sağlık Kurumu Veri Kaynaklarını Birleştiren Ana Modül

Bu modül, tüm farklı kaynaklardan sağlık kurumu verilerini çeker,
mükerrer kayıtları birleştirir ve nihai veritabanını oluşturur.

Author: TURSAKUR Team
Version: 1.0.0
Date: 2025-01-14
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, List
import concurrent.futures

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fetch_all_sources.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthDataAggregator:
    """Sağlık veri toplama ve birleştirme sınıfı"""
    
    def __init__(self):
        self.sources = {
            'saglik_bakanligi': 'scripts/fetch_saglik_bakanligi_data.py',
            'ozel_hastaneler': 'scripts/fetch_ozel_hastaneler_data.py',
            'universite_hastaneleri': 'scripts/fetch_universite_hastaneleri.py',
            'trhastane_universite': 'scripts/fetch_trhastane_universite.py',
            'kapsamli_universite_hastane': 'scripts/fetch_kapsamli_universite_hastane.py',
            'il_saglik_mudurlukeri': 'scripts/fetch_il_saglik_mudurlukeri.py'
        }
        
        self.output_files = {
            'saglik_bakanligi': 'data/raw/saglik_bakanligi_tesisleri.json',
            'ozel_hastaneler': 'data/raw/ozel_hastaneler.json',
            'universite_hastaneleri': 'data/raw/universite_hastaneleri.json',
            'trhastane_universite': 'data/raw/trhastane_universite_hastaneleri.json',
            'kapsamli_universite_hastane': 'data/raw/kapsamli_universite_hastane_iliskileri.json',
            'il_saglik_mudurlukeri': 'data/raw/il_saglik_mudurlukeri.json'
        }
        
        self.results = {}
    
    def run_script(self, script_name: str, script_path: str) -> Dict:
        """Tek bir script'i çalıştır"""
        logger.info(f"{script_name} script'i çalıştırılıyor: {script_path}")
        
        try:
            # Python script'ini çalıştır
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=1800  # 30 dakika timeout
            )
            
            if result.returncode == 0:
                logger.info(f"{script_name} başarıyla tamamlandı")
                
                # Çıktı dosyasını kontrol et
                output_file = self.output_files.get(script_name)
                if output_file and os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    return {
                        'status': 'success',
                        'records': len(data),
                        'file': output_file,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                else:
                    return {
                        'status': 'success_no_output',
                        'records': 0,
                        'file': None,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
            else:
                logger.error(f"{script_name} hata ile sonlandı: {result.stderr}")
                return {
                    'status': 'error',
                    'records': 0,
                    'file': None,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"{script_name} timeout ile sonlandı")
            return {
                'status': 'timeout',
                'records': 0,
                'file': None,
                'stdout': '',
                'stderr': 'Script timeout ile sonlandı'
            }
        except Exception as e:
            logger.error(f"{script_name} beklenmeyen hata: {e}")
            return {
                'status': 'exception',
                'records': 0,
                'file': None,
                'stdout': '',
                'stderr': str(e)
            }
    
    def run_all_sources_parallel(self) -> Dict:
        """Tüm kaynakları paralel olarak çalıştır"""
        logger.info("Tüm veri kaynakları paralel olarak çalıştırılıyor...")
        
        # Dizinleri oluştur
        os.makedirs('data/raw', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Future'ları başlat
            future_to_source = {
                executor.submit(self.run_script, source_name, script_path): source_name
                for source_name, script_path in self.sources.items()
                if os.path.exists(script_path)
            }
            
            # Sonuçları topla
            for future in concurrent.futures.as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    result = future.result()
                    results[source_name] = result
                    logger.info(f"{source_name} tamamlandı: {result['records']} kayıt")
                except Exception as e:
                    logger.error(f"{source_name} exception: {e}")
                    results[source_name] = {
                        'status': 'exception',
                        'records': 0,
                        'file': None,
                        'stdout': '',
                        'stderr': str(e)
                    }
        
        return results
    
    def run_all_sources_sequential(self) -> Dict:
        """Tüm kaynakları sıralı olarak çalıştır"""
        logger.info("Tüm veri kaynakları sıralı olarak çalıştırılıyor...")
        
        # Dizinleri oluştur
        os.makedirs('data/raw', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        results = {}
        
        for source_name, script_path in self.sources.items():
            if os.path.exists(script_path):
                result = self.run_script(source_name, script_path)
                results[source_name] = result
                logger.info(f"{source_name} tamamlandı: {result['records']} kayıt")
            else:
                logger.warning(f"Script bulunamadı: {script_path}")
                results[source_name] = {
                    'status': 'not_found',
                    'records': 0,
                    'file': None,
                    'stdout': '',
                    'stderr': f'Script bulunamadı: {script_path}'
                }
        
        return results
    
    def merge_duplicates(self) -> Dict:
        """Mükerrer kayıtları birleştir"""
        logger.info("Mükerrer kayıtları birleştiriliyor...")
        
        merge_script = 'scripts/merge_duplicate_records.py'
        
        if not os.path.exists(merge_script):
            logger.error(f"Birleştirme script'i bulunamadı: {merge_script}")
            return {
                'status': 'error',
                'message': 'Birleştirme script\'i bulunamadı'
            }
        
        try:
            result = subprocess.run(
                [sys.executable, merge_script],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=600  # 10 dakika timeout
            )
            
            if result.returncode == 0:
                logger.info("Mükerrer kayıtlar başarıyla birleştirildi")
                
                # Birleştirilmiş dosyayı kontrol et
                merged_file = 'data/turkiye_saglik_kuruluslari_merged.json'
                if os.path.exists(merged_file):
                    with open(merged_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    return {
                        'status': 'success',
                        'records': len(data),
                        'file': merged_file,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                else:
                    return {
                        'status': 'success_no_output',
                        'records': 0,
                        'file': None,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
            else:
                logger.error(f"Birleştirme hatası: {result.stderr}")
                return {
                    'status': 'error',
                    'records': 0,
                    'file': None,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except Exception as e:
            logger.error(f"Birleştirme exception: {e}")
            return {
                'status': 'exception',
                'records': 0,
                'file': None,
                'stdout': '',
                'stderr': str(e)
            }
    
    def finalize_database(self) -> Dict:
        """Nihai veritabanını oluştur"""
        logger.info("Nihai veritabanı oluşturuluyor...")
        
        process_script = 'scripts/process_data.py'
        
        if not os.path.exists(process_script):
            logger.error(f"Veri işleme script'i bulunamadı: {process_script}")
            return {
                'status': 'error',
                'message': 'Veri işleme script\'i bulunamadı'
            }
        
        try:
            result = subprocess.run(
                [sys.executable, process_script],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5 dakika timeout
            )
            
            if result.returncode == 0:
                logger.info("Nihai veritabanı başarıyla oluşturuldu")
                
                # Final dosyayı kontrol et
                final_file = 'data/turkiye_saglik_kuruluslari.json'
                if os.path.exists(final_file):
                    with open(final_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    return {
                        'status': 'success',
                        'records': len(data),
                        'file': final_file,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                else:
                    return {
                        'status': 'success_no_output',
                        'records': 0,
                        'file': None,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
            else:
                logger.error(f"Veri işleme hatası: {result.stderr}")
                return {
                    'status': 'error',
                    'records': 0,
                    'file': None,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except Exception as e:
            logger.error(f"Veri işleme exception: {e}")
            return {
                'status': 'exception',
                'records': 0,
                'file': None,
                'stdout': '',
                'stderr': str(e)
            }
    
    def generate_summary_report(self, source_results: Dict, merge_result: Dict, final_result: Dict) -> str:
        """Özet rapor oluştur"""
        report = f"""
=== TURSAKUR VERİ TOPLAMA VE BİRLEŞTİRME RAPORU ===
Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 KAYNAK BAZLI VERİ TOPLAMA SONUÇLARI:
"""
        
        total_source_records = 0
        successful_sources = 0
        
        for source_name, result in source_results.items():
            status_icon = "✅" if result['status'] == 'success' else "❌"
            report += f"{status_icon} {source_name.replace('_', ' ').title()}: {result['records']} kayıt\n"
            
            if result['status'] == 'success':
                total_source_records += result['records']
                successful_sources += 1
            
            if result['stderr']:
                report += f"   ⚠️  Uyarı: {result['stderr'][:100]}...\n"
        
        report += f"\nToplam ham kayıt: {total_source_records}\n"
        report += f"Başarılı kaynak sayısı: {successful_sources}/{len(source_results)}\n"
        
        # Birleştirme sonuçları
        report += f"\n🔄 MÜKERRER KAYIT BİRLEŞTİRME:\n"
        if merge_result['status'] == 'success':
            report += f"✅ Birleştirme başarılı: {merge_result['records']} benzersiz kayıt\n"
            if total_source_records > 0:
                dedup_rate = ((total_source_records - merge_result['records']) / total_source_records) * 100
                report += f"📉 Mükerrer kayıt oranı: {dedup_rate:.1f}%\n"
        else:
            report += f"❌ Birleştirme hatası: {merge_result.get('stderr', 'Bilinmeyen hata')}\n"
        
        # Final sonuçlar
        report += f"\n🎯 FİNAL VERİTABANI:\n"
        if final_result['status'] == 'success':
            report += f"✅ Nihai veritabanı oluşturuldu: {final_result['records']} kayıt\n"
            report += f"📁 Dosya: {final_result['file']}\n"
        else:
            report += f"❌ Nihai veritabanı hatası: {final_result.get('stderr', 'Bilinmeyen hata')}\n"
        
        # Performans özeti
        report += f"\n📈 PERFORMANS ÖZETİ:\n"
        report += f"Ham veri → Benzersiz: {total_source_records} → {merge_result.get('records', 0)}\n"
        report += f"Benzersiz → Final: {merge_result.get('records', 0)} → {final_result.get('records', 0)}\n"
        
        if final_result.get('records', 0) > 0:
            report += f"Veri kalitesi: {(final_result['records'] / max(total_source_records, 1)) * 100:.1f}% tutarlılık\n"
        
        report += f"\n⏱️  İşlem tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report

def main():
    """Ana fonksiyon"""
    try:
        logger.info("TURSAKUR kapsamlı veri toplama işlemi başlatılıyor...")
        
        aggregator = HealthDataAggregator()
        
        # 1. Tüm kaynakları çalıştır
        print("📡 Veri kaynakları çalıştırılıyor...")
        source_results = aggregator.run_all_sources_sequential()  # Stable için sequential
        
        # 2. Mükerrer kayıtları birleştir
        print("🔄 Mükerrer kayıtlar birleştiriliyor...")
        merge_result = aggregator.merge_duplicates()
        
        # 3. Nihai veritabanını oluştur
        print("🎯 Nihai veritabanı oluşturuluyor...")
        final_result = aggregator.finalize_database()
        
        # 4. Rapor oluştur
        report = aggregator.generate_summary_report(source_results, merge_result, final_result)
        print(report)
        
        # Raporu dosyaya kaydet
        with open('logs/aggregation_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Genel başarı kontrolü
        success_count = sum(1 for result in source_results.values() if result['status'] == 'success')
        
        if (success_count >= len(source_results) // 2 and  # En az yarısı başarılı
            merge_result['status'] == 'success' and
            final_result['status'] == 'success'):
            logger.info("Kapsamlı veri toplama işlemi başarıyla tamamlandı!")
            return 0
        else:
            logger.error("Veri toplama işleminde kritik hatalar oluştu!")
            return 1
            
    except Exception as e:
        logger.error(f"Ana fonksiyon kritik hatası: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
