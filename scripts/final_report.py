#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TURSAKUR Final Report Generator
Türkiye Sağlık Kuruluşları Kapsamlı Analiz ve Rapor Sistemi
"""

import json
import logging
from datetime import datetime
from collections import Counter, defaultdict
import os

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_report.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TURSAKURFinalReport:
    """TURSAKUR Final Report Generator"""
    
    def __init__(self):
        self.data_dir = "data"
        self.raw_data_dir = "data/raw"
        
    def load_main_data(self):
        """Ana veri dosyasını yükle"""
        try:
            main_file = os.path.join(self.data_dir, "turkiye_saglik_kuruluslari.json")
            with open(main_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ana veri dosyası yüklenemedi: {e}")
            return None
    
    def analyze_data_sources(self):
        """Veri kaynaklarını analiz et"""
        sources_analysis = {}
        
        # Raw data dosyalarını kontrol et
        raw_files = [
            "saglik_bakanligi_tesisleri.json",
            "ozel_hastaneler.json", 
            "universite_hastaneleri.json",
            "trhastane_universite_hastaneleri.json"
        ]
        
        for file in raw_files:
            file_path = os.path.join(self.raw_data_dir, file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sources_analysis[file] = {
                            "kayit_sayisi": len(data),
                            "dosya_boyutu": f"{os.path.getsize(file_path) / 1024:.2f} KB",
                            "son_degisiklik": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                        }
                except Exception as e:
                    logger.warning(f"{file} analiz edilemedi: {e}")
                    sources_analysis[file] = {"hata": str(e)}
            else:
                sources_analysis[file] = {"durum": "Dosya bulunamadı"}
        
        return sources_analysis
    
    def generate_comprehensive_statistics(self, data):
        """Kapsamlı istatistikler oluştur"""
        if not data or 'kurumlar' not in data:
            return {}
        
        kurumlar = data['kurumlar']
        
        # Temel istatistikler
        stats = {
            "toplam_kurum": len(kurumlar),
            "metadata": data.get('metadata', {}),
        }
        
        # İl bazında analiz
        il_analizi = {}
        
        # Kurum tipi analizi
        kurum_tipi_analizi = {}
        
        # Veri kalitesi analizi
        kalite_analizi = {
            'koordinat_olan': 0,
            'telefon_olan': 0,
            'web_sitesi_olan': 0,
            'tam_veri_olan': 0
        }
        
        for kurum in kurumlar:
            il_adi = kurum.get('il_adi', 'Bilinmeyen')
            kurum_tipi = kurum.get('kurum_tipi', 'Bilinmeyen')
            
            # İl analizi - initialize if not exists
            if il_adi not in il_analizi:
                il_analizi[il_adi] = {
                    'toplam': 0,
                    'kurum_tipleri': {},
                    'koordinat_olan': 0,
                    'telefon_olan': 0,
                    'web_sitesi_olan': 0
                }
            
            # Kurum tipi analizi - initialize if not exists
            if kurum_tipi not in kurum_tipi_analizi:
                kurum_tipi_analizi[kurum_tipi] = {
                    'toplam': 0,
                    'koordinat_olan': 0,
                    'telefon_olan': 0,
                    'web_sitesi_olan': 0,
                    'iller': set()
                }
            
            # İl analizi
            il_analizi[il_adi]['toplam'] += 1
            if kurum_tipi not in il_analizi[il_adi]['kurum_tipleri']:
                il_analizi[il_adi]['kurum_tipleri'][kurum_tipi] = 0
            il_analizi[il_adi]['kurum_tipleri'][kurum_tipi] += 1
            
            # Kurum tipi analizi
            kurum_tipi_analizi[kurum_tipi]['toplam'] += 1
            kurum_tipi_analizi[kurum_tipi]['iller'].add(il_adi)
            
            # Veri kalitesi kontrolü
            has_coord = kurum.get('koordinat_lat') and kurum.get('koordinat_lon')
            has_phone = kurum.get('telefon') and kurum.get('telefon').strip()
            has_website = kurum.get('web_sitesi') and kurum.get('web_sitesi').strip()
            
            if has_coord:
                kalite_analizi['koordinat_olan'] += 1
                il_analizi[il_adi]['koordinat_olan'] += 1
                kurum_tipi_analizi[kurum_tipi]['koordinat_olan'] += 1
            
            if has_phone:
                kalite_analizi['telefon_olan'] += 1
                il_analizi[il_adi]['telefon_olan'] += 1
                kurum_tipi_analizi[kurum_tipi]['telefon_olan'] += 1
            
            if has_website:
                kalite_analizi['web_sitesi_olan'] += 1
                il_analizi[il_adi]['web_sitesi_olan'] += 1
                kurum_tipi_analizi[kurum_tipi]['web_sitesi_olan'] += 1
            
            if has_coord and has_phone and has_website:
                kalite_analizi['tam_veri_olan'] += 1
        
        # Set'leri listeye çevir (JSON serileştirme için)
        for tip in kurum_tipi_analizi:
            kurum_tipi_analizi[tip]['iller'] = list(kurum_tipi_analizi[tip]['iller'])
        
        stats.update({
            'il_bazinda_analiz': il_analizi,
            'kurum_tipi_analizi': kurum_tipi_analizi,
            'veri_kalitesi': kalite_analizi
        })
        
        return stats
    
    def generate_final_report(self):
        """Final raporu oluştur"""
        logger.info("🎯 TURSAKUR Final Report Generator başlatılıyor...")
        
        # Ana veriyi yükle
        main_data = self.load_main_data()
        if not main_data:
            logger.error("❌ Ana veri yüklenemedi, rapor oluşturulamıyor")
            return
        
        # Veri kaynaklarını analiz et
        sources_analysis = self.analyze_data_sources()
        
        # Kapsamlı istatistikler
        comprehensive_stats = self.generate_comprehensive_statistics(main_data)
        
        # Final rapor objesi
        final_report = {
            "rapor_tarihi": datetime.now().isoformat(),
            "tursakur_versiyonu": "2.0.0",
            "veri_kaynaklari_analizi": sources_analysis,
            "kapsamli_istatistikler": comprehensive_stats,
            "ozet": {
                "toplam_kurum": comprehensive_stats.get('toplam_kurum', 0),
                "toplam_il": len(comprehensive_stats.get('il_bazinda_analiz', {})),
                "kurum_tipi_cesitliligi": len(comprehensive_stats.get('kurum_tipi_analizi', {})),
                "veri_kalite_skoru": round((comprehensive_stats.get('veri_kalitesi', {}).get('koordinat_olan', 0) / max(comprehensive_stats.get('toplam_kurum', 1), 1)) * 100, 2)
            }
        }
        
        # Raporu kaydet
        report_file = "tursakur_final_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        # Konsol çıktısı
        self.print_console_report(final_report)
        
        logger.info(f"✅ Final rapor oluşturuldu: {report_file}")
        return final_report
    
    def print_console_report(self, report):
        """Konsol raporu yazdır"""
        print("\n" + "="*80)
        print("🏥 TURSAKUR - TÜRKİYE SAĞLIK KURULUŞLARI FİNAL RAPORU")
        print("="*80)
        
        ozet = report['ozet']
        print(f"📊 GENEL ÖZET:")
        print(f"   • Toplam Kurum: {ozet['toplam_kurum']:,}")
        print(f"   • Toplam İl: {ozet['toplam_il']}")
        print(f"   • Kurum Tipi Çeşitliliği: {ozet['kurum_tipi_cesitliligi']}")
        print(f"   • Veri Kalite Skoru: %{ozet['veri_kalite_skoru']}")
        
        print(f"\n📁 VERİ KAYNAKLARI:")
        for kaynak, bilgi in report['veri_kaynaklari_analizi'].items():
            if 'kayit_sayisi' in bilgi:
                print(f"   • {kaynak}: {bilgi['kayit_sayisi']} kayıt ({bilgi['dosya_boyutu']})")
            else:
                print(f"   • {kaynak}: {bilgi.get('durum', 'Hata')}")
        
        kurum_analizi = report['kapsamli_istatistikler']['kurum_tipi_analizi']
        print(f"\n🏥 KURUM TİPİ DAĞILIMI:")
        for tip, bilgi in sorted(kurum_analizi.items(), key=lambda x: x[1]['toplam'], reverse=True):
            print(f"   • {tip}: {bilgi['toplam']:,} kurum ({len(bilgi['iller'])} ilde)")
        
        kalite = report['kapsamli_istatistikler']['veri_kalitesi']
        print(f"\n📍 VERİ KALİTESİ:")
        print(f"   • Koordinat bilgisi olan: {kalite['koordinat_olan']:,}")
        print(f"   • Telefon bilgisi olan: {kalite['telefon_olan']:,}")
        print(f"   • Web sitesi olan: {kalite['web_sitesi_olan']:,}")
        print(f"   • Tam veri setine sahip: {kalite['tam_veri_olan']:,}")
        
        print(f"\n✅ TURSAKUR v2.0 başarıyla finalize edilmiştir!")
        print("="*80)

def main():
    """Ana fonksiyon"""
    reporter = TURSAKURFinalReport()
    reporter.generate_final_report()

if __name__ == "__main__":
    main()
