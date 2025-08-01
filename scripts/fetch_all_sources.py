#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Ana Veri Toplama Orchestrator
==========================================

Tüm veri kaynaklarını koordine eden ana script.
Veri.md'de belirtilen ETL pipeline'ını çalıştırır.

Çalışma Sırası:
1. Tier 1 kaynakları (en yüksek öncelik)
2. Tier 2 kaynakları (doğrulama ve zenginleştirme)  
3. Tier 3 kaynakları (keşif ve çapraz referans)
4. Veri işleme ve birleştirme
5. Supabase'e yükleme
"""

import sys
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import time

class DataPipelineOrchestrator:
    """TURSAKUR veri toplama pipeline'ını yönetir"""
    
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.data_dir = self.scripts_dir.parent / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        
        # Create directories
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging setup
        log_file = self.data_dir / "pipeline.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Veri kaynaklarının yapılandırması
        self.data_sources = {
            'tier1': [
                {
                    'name': 'Sağlık Bakanlığı',
                    'script': 'fetch_saglik_bakanligi_data.py',
                    'description': 'KHGM, SBSGM, YHGM ve İl Sağlık Müdürlükleri',
                    'critical': True
                },
                {
                    'name': 'SGK Anlaşmalı Kurumlar',
                    'script': 'fetch_sgk_anlasmali_kurumlar.py',
                    'description': 'SGK ile anlaşmalı tüm sağlık hizmeti sunucuları',
                    'critical': True
                },
                {
                    'name': 'Üniversite Hastaneleri',
                    'script': 'fetch_universite_hastaneleri.py',
                    'description': 'YÖK ve üniversite web sitelerinden',
                    'critical': False
                }
            ],
            'tier2': [
                {
                    'name': 'Özel Hastane Zincirleri',
                    'script': 'fetch_ozel_hastane_zincirleri.py',
                    'description': 'Acıbadem, Medical Park, Memorial vb.',
                    'critical': False
                }
            ],
            'tier3': [
                {
                    'name': 'Google Places API',
                    'script': 'fetch_google_places.py',
                    'description': 'Google Maps POI verileri',
                    'critical': False
                }
            ]
        }
        
        self.execution_results = {
            'started_at': None,
            'completed_at': None,
            'tier1_results': {},
            'tier2_results': {},
            'tier3_results': {},
            'processing_result': None,
            'loading_result': None,
            'total_records': 0,
            'errors': []
        }

    def run_script(self, script_name: str) -> Dict:
        """Belirtilen script'i çalıştırır ve sonucu döner"""
        script_path = self.scripts_dir / script_name
        
        if not script_path.exists():
            error_msg = f"Script bulunamadı: {script_path}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'duration': 0,
                'records': 0
            }
        
        self.logger.info(f"Çalıştırılıyor: {script_name}")
        start_time = time.time()
        
        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                # Try to find and count records from output files
                records_count = self._count_records_from_latest_file(script_name)
                
                self.logger.info(f"✅ {script_name} başarıyla tamamlandı ({duration:.1f}s, {records_count} kayıt)")
                return {
                    'success': True,
                    'duration': duration,
                    'records': records_count,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                error_msg = f"Script başarısız: {script_name} (exit code: {result.returncode})"
                self.logger.error(f"❌ {error_msg}")
                self.logger.error(f"STDERR: {result.stderr}")
                
                return {
                    'success': False,
                    'error': error_msg,
                    'duration': duration,
                    'records': 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            error_msg = f"Script timeout: {script_name} ({duration:.1f}s)"
            self.logger.error(f"⏰ {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'duration': duration,
                'records': 0
            }
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Script çalıştırma hatası: {script_name} - {str(e)}"
            self.logger.error(f"💥 {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'duration': duration,
                'records': 0
            }

    def _count_records_from_latest_file(self, script_name: str) -> int:
        """En son oluşturulan veri dosyasından kayıt sayısını okur"""
        try:
            # Find the most recent file that matches the script
            script_prefix = script_name.replace('fetch_', '').replace('.py', '')
            
            matching_files = list(self.raw_data_dir.glob(f"{script_prefix}*.json"))
            if not matching_files:
                return 0
            
            # Get the most recent file
            latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('toplam_kayit', 0)
                
        except Exception as e:
            self.logger.warning(f"Kayıt sayısı okunamadı {script_name}: {e}")
            return 0

    def run_tier(self, tier_name: str, sources: List[Dict]) -> Dict:
        """Belirtilen tier'daki tüm kaynakları çalıştırır"""
        self.logger.info(f"\n🚀 {tier_name.upper()} KAYNAKLARI BAŞLATILIYOR...")
        
        tier_results = {}
        total_records = 0
        errors = []
        
        for source in sources:
            result = self.run_script(source['script'])
            tier_results[source['name']] = result
            
            if result['success']:
                total_records += result['records']
            else:
                errors.append(f"{source['name']}: {result.get('error', 'Bilinmeyen hata')}")
                
                # Critical source failure için durumu kontrol et
                if source.get('critical', False):
                    self.logger.warning(f"⚠️  Kritik kaynak başarısız: {source['name']}")
        
        success_count = sum(1 for r in tier_results.values() if r['success'])
        total_count = len(sources)
        
        self.logger.info(f"📊 {tier_name.upper()} SONUÇLARI: {success_count}/{total_count} başarılı, {total_records} toplam kayıt")
        
        return {
            'success_count': success_count,
            'total_count': total_count,
            'total_records': total_records,
            'results': tier_results,
            'errors': errors
        }

    def run_data_processing(self) -> Dict:
        """Veri işleme script'ini çalıştırır"""
        self.logger.info("\n🔄 VERİ İŞLEME BAŞLATILIYOR...")
        
        process_script = 'process_data.py'
        result = self.run_script(process_script)
        
        if result['success']:
            self.logger.info("✅ Veri işleme tamamlandı")
        else:
            self.logger.error("❌ Veri işleme başarısız")
        
        return result

    def run_data_loading(self) -> Dict:
        """Supabase veri yükleme script'ini çalıştırır"""
        self.logger.info("\n📤 SUPABASE YÜKLEME BAŞLATILIYOR...")
        
        load_script = 'load_to_supabase.py'
        result = self.run_script(load_script)
        
        if result['success']:
            self.logger.info("✅ Supabase yükleme tamamlandı")
        else:
            self.logger.error("❌ Supabase yükleme başarısız")
        
        return result

    def generate_report(self) -> str:
        """Pipeline çalışma raporu oluşturur"""
        report_lines = [
            "# TURSAKUR 2.0 Veri Pipeline Raporu",
            f"**Çalışma Tarihi:** {self.execution_results['started_at']}",
            f"**Tamamlanma Tarihi:** {self.execution_results['completed_at']}",
            ""
        ]
        
        # Tier summaries
        for tier_name in ['tier1', 'tier2', 'tier3']:
            tier_key = f"{tier_name}_results"
            if tier_key in self.execution_results and self.execution_results[tier_key]:
                tier_data = self.execution_results[tier_key]
                report_lines.extend([
                    f"## {tier_name.upper()} Sonuçları",
                    f"- **Başarılı:** {tier_data['success_count']}/{tier_data['total_count']}",
                    f"- **Toplam Kayıt:** {tier_data['total_records']:,}",
                    ""
                ])
                
                # Individual source results
                for source_name, result in tier_data['results'].items():
                    status = "✅" if result['success'] else "❌"
                    duration = result.get('duration', 0)
                    records = result.get('records', 0)
                    report_lines.append(f"  - {status} **{source_name}**: {records:,} kayıt ({duration:.1f}s)")
                
                report_lines.append("")
        
        # Processing and Loading
        if self.execution_results.get('processing_result'):
            result = self.execution_results['processing_result']
            status = "✅" if result['success'] else "❌"
            report_lines.extend([
                "## Veri İşleme",
                f"{status} Durum: {'Başarılı' if result['success'] else 'Başarısız'}",
                f"Süre: {result.get('duration', 0):.1f} saniye",
                ""
            ])
        
        if self.execution_results.get('loading_result'):
            result = self.execution_results['loading_result']
            status = "✅" if result['success'] else "❌"
            report_lines.extend([
                "## Supabase Yükleme",
                f"{status} Durum: {'Başarılı' if result['success'] else 'Başarısız'}",
                f"Süre: {result.get('duration', 0):.1f} saniye",
                ""
            ])
        
        # Summary
        total_records = sum(
            self.execution_results.get(f"{tier}_results", {}).get('total_records', 0)
            for tier in ['tier1', 'tier2', 'tier3']
        )
        
        report_lines.extend([
            "## Özet",
            f"- **Toplam Kayıt:** {total_records:,}",
            f"- **Çalışma Süresi:** {self._calculate_total_duration():.1f} saniye",
            ""
        ])
        
        # Errors
        all_errors = []
        for tier in ['tier1', 'tier2', 'tier3']:
            tier_data = self.execution_results.get(f"{tier}_results", {})
            all_errors.extend(tier_data.get('errors', []))
        
        if all_errors:
            report_lines.extend([
                "## Hatalar",
                *[f"- {error}" for error in all_errors],
                ""
            ])
        
        return "\n".join(report_lines)

    def _calculate_total_duration(self) -> float:
        """Toplam çalışma süresini hesaplar"""
        if self.execution_results['started_at'] and self.execution_results['completed_at']:
            start = datetime.fromisoformat(self.execution_results['started_at'])
            end = datetime.fromisoformat(self.execution_results['completed_at'])
            return (end - start).total_seconds()
        return 0.0

    def save_report(self, report_content: str):
        """Raporu dosyaya kaydeder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.data_dir / f"pipeline_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"📄 Rapor kaydedildi: {report_file}")

    def run(self, run_tier1=True, run_tier2=True, run_tier3=True, run_processing=True, run_loading=True):
        """Ana pipeline'ı çalıştırır"""
        self.execution_results['started_at'] = datetime.now(timezone.utc).isoformat()
        
        self.logger.info("🎯 TURSAKUR 2.0 VERİ PIPELINE BAŞLATILIYOR...")
        self.logger.info("=" * 60)
        
        try:
            # Tier 1 - En Yüksek Öncelik
            if run_tier1:
                self.execution_results['tier1_results'] = self.run_tier('tier1', self.data_sources['tier1'])
            
            # Tier 2 - Doğrulama ve Zenginleştirme
            if run_tier2:
                self.execution_results['tier2_results'] = self.run_tier('tier2', self.data_sources['tier2'])
            
            # Tier 3 - Keşif ve Çapraz Referans
            if run_tier3:
                self.execution_results['tier3_results'] = self.run_tier('tier3', self.data_sources['tier3'])
            
            # Data Processing
            if run_processing:
                self.execution_results['processing_result'] = self.run_data_processing()
            
            # Data Loading
            if run_loading and self.execution_results.get('processing_result', {}).get('success', False):
                self.execution_results['loading_result'] = self.run_data_loading()
            
            self.execution_results['completed_at'] = datetime.now(timezone.utc).isoformat()
            
            # Generate and save report
            report = self.generate_report()
            self.save_report(report)
            
            self.logger.info("=" * 60)
            self.logger.info("🎉 TURSAKUR 2.0 VERİ PIPELINE TAMAMLANDI!")
            
            return True
            
        except Exception as e:
            self.execution_results['completed_at'] = datetime.now(timezone.utc).isoformat()
            self.logger.error(f"💥 Pipeline genel hatası: {e}")
            return False

def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TURSAKUR 2.0 Veri Pipeline')
    parser.add_argument('--skip-tier1', action='store_true', help='Tier 1 kaynaklarını atla')
    parser.add_argument('--skip-tier2', action='store_true', help='Tier 2 kaynaklarını atla')
    parser.add_argument('--skip-tier3', action='store_true', help='Tier 3 kaynaklarını atla')
    parser.add_argument('--skip-processing', action='store_true', help='Veri işlemeyi atla')
    parser.add_argument('--skip-loading', action='store_true', help='Supabase yüklemeyi atla')
    
    args = parser.parse_args()
    
    orchestrator = DataPipelineOrchestrator()
    success = orchestrator.run(
        run_tier1=not args.skip_tier1,
        run_tier2=not args.skip_tier2,
        run_tier3=not args.skip_tier3,
        run_processing=not args.skip_processing,
        run_loading=not args.skip_loading
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
