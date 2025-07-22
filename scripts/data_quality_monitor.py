#!/usr/bin/env python3
"""
Türkiye Sağlık Kuruluşları - Veri Kalitesi Monitoring
Veritabanındaki veri kalitesini analiz eder ve raporlar.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataQualityMonitor:
    """Veri kalitesi monitoring sınıfı."""
    
    def __init__(self, data_file: str = 'data/turkiye_saglik_kuruluslari.json'):
        self.data_file = data_file
        self.data = None
        self.kurumlar = []
        self.quality_report = {
            'timestamp': datetime.now().isoformat(),
            'total_records': 0,
            'quality_scores': {},
            'issues': [],
            'recommendations': []
        }
    
    def load_data(self) -> bool:
        """Veri dosyasını yükle."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            self.kurumlar = self.data.get('kurumlar', [])
            self.quality_report['total_records'] = len(self.kurumlar)
            
            logger.info(f"✅ Veri dosyası yüklendi: {len(self.kurumlar):,} kayıt")
            return True
            
        except FileNotFoundError:
            logger.error(f"❌ Veri dosyası bulunamadı: {self.data_file}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse hatası: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Veri yükleme hatası: {e}")
            return False
    
    def check_completeness(self):
        """Veri tamlığını kontrol et."""
        logger.info("📋 Veri tamlığı analizi...")
        
        required_fields = ['kurum_id', 'kurum_adi', 'kurum_tipi', 'il_adi']
        optional_fields = ['adres', 'telefon', 'koordinat_lat', 'koordinat_lon', 'web_sitesi']
        
        field_stats = defaultdict(int)
        missing_required = []
        
        for i, kurum in enumerate(self.kurumlar):
            # Zorunlu alanları kontrol et
            for field in required_fields:
                if field in kurum and kurum[field]:
                    field_stats[field] += 1
                else:
                    missing_required.append({
                        'index': i,
                        'kurum_adi': kurum.get('kurum_adi', 'Bilinmiyor'),
                        'missing_field': field
                    })
            
            # Opsiyonel alanları kontrol et
            for field in optional_fields:
                if field in kurum and kurum[field]:
                    field_stats[field] += 1
        
        # Tamamlık skorları
        total = len(self.kurumlar)
        completeness_scores = {}
        
        for field in required_fields + optional_fields:
            score = (field_stats[field] / total) * 100
            completeness_scores[field] = score
            
            if field in required_fields and score < 95:
                self.quality_report['issues'].append({
                    'type': 'completeness',
                    'severity': 'critical' if score < 80 else 'warning',
                    'field': field,
                    'message': f"Zorunlu alan eksik: {field} (%{score:.1f} tamamlık)",
                    'affected_records': total - field_stats[field]
                })
        
        self.quality_report['quality_scores']['completeness'] = completeness_scores
        
        logger.info("✅ Veri tamlığı analizi tamamlandı")
        
        # Top eksik alanları logla
        for field in ['telefon', 'koordinat_lat', 'web_sitesi']:
            score = completeness_scores.get(field, 0)
            logger.info(f"   {field}: %{score:.1f}")
    
    def check_data_consistency(self):
        """Veri tutarlılığını kontrol et."""
        logger.info("🔄 Veri tutarlılığı analizi...")
        
        consistency_issues = []
        
        # 1. Kurum ID formatı kontrolü
        id_pattern = re.compile(r'^TR-\d{2}-[A-Z]+-(00[1-9]|0[1-9]\d|[1-9]\d{2})$')
        invalid_ids = []
        
        for i, kurum in enumerate(self.kurumlar):
            kurum_id = kurum.get('kurum_id', '')
            if kurum_id and not id_pattern.match(kurum_id):
                invalid_ids.append({
                    'index': i,
                    'kurum_adi': kurum.get('kurum_adi', ''),
                    'invalid_id': kurum_id
                })
        
        if invalid_ids:
            self.quality_report['issues'].append({
                'type': 'consistency',
                'severity': 'warning',
                'message': f"Geçersiz kurum ID formatı: {len(invalid_ids)} kayıt",
                'affected_records': len(invalid_ids)
            })
        
        # 2. Telefon formatı kontrolü
        phone_pattern = re.compile(r'^\+90\d{10}$')
        invalid_phones = []
        
        for i, kurum in enumerate(self.kurumlar):
            telefon = kurum.get('telefon', '')
            if telefon and not phone_pattern.match(telefon):
                invalid_phones.append({
                    'kurum_adi': kurum.get('kurum_adi', ''),
                    'invalid_phone': telefon
                })
        
        if invalid_phones:
            self.quality_report['issues'].append({
                'type': 'consistency',
                'severity': 'warning',
                'message': f"Geçersiz telefon formatı: {len(invalid_phones)} kayıt",
                'affected_records': len(invalid_phones)
            })
        
        # 3. Koordinat değerleri kontrolü
        invalid_coords = []
        
        for i, kurum in enumerate(self.kurumlar):
            lat = kurum.get('koordinat_lat')
            lon = kurum.get('koordinat_lon')
            
            if lat is not None and lon is not None:
                # Türkiye koordinat aralıkları: lat: 35-42, lon: 25-45
                if not (35 <= lat <= 42) or not (25 <= lon <= 45):
                    invalid_coords.append({
                        'kurum_adi': kurum.get('kurum_adi', ''),
                        'lat': lat,
                        'lon': lon
                    })
        
        if invalid_coords:
            self.quality_report['issues'].append({
                'type': 'consistency',
                'severity': 'warning',
                'message': f"Türkiye dışı koordinatlar: {len(invalid_coords)} kayıt",
                'affected_records': len(invalid_coords)
            })
        
        logger.info("✅ Veri tutarlılığı analizi tamamlandı")
    
    def check_duplicates(self):
        """Duplicate kayıtları kontrol et."""
        logger.info("🔍 Duplicate kontrol analizi...")
        
        # Kurum adı + il kombinasyonu ile duplicate kontrol
        name_city_combinations = defaultdict(list)
        
        for i, kurum in enumerate(self.kurumlar):
            kurum_adi = kurum.get('kurum_adi', '').strip().lower()
            il_adi = kurum.get('il_adi', '').strip().lower()
            
            key = f"{kurum_adi}|{il_adi}"
            name_city_combinations[key].append({
                'index': i,
                'kurum_id': kurum.get('kurum_id'),
                'kurum_adi': kurum.get('kurum_adi'),
                'il_adi': kurum.get('il_adi'),
                'veri_kaynagi': kurum.get('veri_kaynagi')
            })
        
        # Duplicate olanları bul
        duplicates = []
        for key, records in name_city_combinations.items():
            if len(records) > 1:
                duplicates.append({
                    'key': key,
                    'count': len(records),
                    'records': records
                })
        
        if duplicates:
            total_duplicate_records = sum(d['count'] - 1 for d in duplicates)  # -1 çünkü biri orijinal
            
            self.quality_report['issues'].append({
                'type': 'duplicates',
                'severity': 'warning',
                'message': f"Duplicate kayıtlar: {len(duplicates)} grup, {total_duplicate_records} fazla kayıt",
                'affected_records': total_duplicate_records,
                'duplicate_groups': len(duplicates)
            })
        
        logger.info(f"✅ Duplicate kontrol tamamlandı - {len(duplicates)} grup bulundu")
    
    def check_data_freshness(self):
        """Veri güncelliğini kontrol et."""
        logger.info("📅 Veri güncelliği analizi...")
        
        if not self.data or 'meta' not in self.data:
            logger.warning("⚠️ Meta bilgiler bulunamadı")
            return
        
        last_updated_str = self.data['meta'].get('last_updated', '')
        if not last_updated_str:
            logger.warning("⚠️ Son güncelleme tarihi bulunamadı")
            return
        
        try:
            # ISO format parse et
            last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
            now = datetime.now(last_updated.tzinfo)
            age = now - last_updated
            
            age_days = age.days
            age_hours = age.seconds // 3600
            
            if age_days > 7:
                severity = 'critical'
            elif age_days > 3:
                severity = 'warning'
            else:
                severity = 'info'
            
            self.quality_report['quality_scores']['data_freshness'] = {
                'last_updated': last_updated_str,
                'age_days': age_days,
                'age_hours': age_hours,
                'severity': severity
            }
            
            if age_days > 1:
                self.quality_report['issues'].append({
                    'type': 'freshness',
                    'severity': severity,
                    'message': f"Veri yaşı: {age_days} gün, {age_hours} saat",
                    'recommendation': 'Veri güncelleme scriptlerini çalıştırın'
                })
            
            logger.info(f"✅ Veri yaşı: {age_days} gün, {age_hours} saat")
            
        except Exception as e:
            logger.warning(f"⚠️ Tarih parse hatası: {e}")
    
    def generate_recommendations(self):
        """Kalite iyileştirme önerileri üret."""
        logger.info("💡 Öneri oluşturma...")
        
        recommendations = []
        
        # Tamamlık bazlı öneriler
        completeness = self.quality_report['quality_scores'].get('completeness', {})
        
        if completeness.get('telefon', 0) < 50:
            recommendations.append({
                'category': 'data_enrichment',
                'priority': 'medium',
                'action': 'Telefon bilgilerini manuel araştırma ile tamamlayın',
                'impact': 'Kullanıcı deneyimi iyileştirmesi'
            })
        
        if completeness.get('koordinat_lat', 0) < 30:
            recommendations.append({
                'category': 'data_enrichment',
                'priority': 'high',
                'action': 'Geocoding API kullanarak eksik koordinatları tamamlayın',
                'impact': 'Harita özelliği kullanılabilirliği'
            })
        
        if completeness.get('web_sitesi', 0) < 20:
            recommendations.append({
                'category': 'data_enrichment',
                'priority': 'low',
                'action': 'Web sitesi bilgilerini Google araması ile tamamlayın',
                'impact': 'Kullanıcıların kurumları bulması'
            })
        
        # Issue bazlı öneriler
        issues = self.quality_report.get('issues', [])
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        
        if critical_issues:
            recommendations.append({
                'category': 'data_quality',
                'priority': 'critical',
                'action': f'{len(critical_issues)} kritik veri kalitesi sorunu çözülmelidir',
                'impact': 'Sistem güvenilirliği'
            })
        
        # Veri kaynağı bazlı öneriler
        source_stats = Counter([k.get('veri_kaynagi', 'Bilinmiyor') for k in self.kurumlar])
        total_records = len(self.kurumlar)
        
        for source, count in source_stats.items():
            if 'timeout' in source.lower() or 'hata' in source.lower():
                recommendations.append({
                    'category': 'data_collection',
                    'priority': 'medium',
                    'action': f'"{source}" kaynağındaki teknik sorunları çözün',
                    'impact': f'{count} kayıt etkilenmiş'
                })
        
        self.quality_report['recommendations'] = recommendations
        logger.info(f"✅ {len(recommendations)} öneri oluşturuldu")
    
    def calculate_overall_score(self):
        """Genel kalite skoru hesapla."""
        logger.info("📊 Genel kalite skoru hesaplama...")
        
        scores = []
        weights = {}
        
        # Tamamlık skorları (ağırlık: 40%)
        completeness = self.quality_report['quality_scores'].get('completeness', {})
        required_fields = ['kurum_id', 'kurum_adi', 'kurum_tipi', 'il_adi']
        
        if completeness:
            avg_completeness = sum(completeness.get(f, 0) for f in required_fields) / len(required_fields)
            scores.append(('completeness', avg_completeness, 0.4))
        
        # Consistency skoru (ağırlık: 30%)
        consistency_issues = [i for i in self.quality_report.get('issues', []) if i.get('type') == 'consistency']
        total_records = self.quality_report['total_records']
        
        if total_records > 0:
            affected_by_consistency = sum(i.get('affected_records', 0) for i in consistency_issues)
            consistency_score = max(0, 100 - (affected_by_consistency / total_records * 100))
            scores.append(('consistency', consistency_score, 0.3))
        
        # Duplicate skoru (ağırlık: 20%)
        duplicate_issues = [i for i in self.quality_report.get('issues', []) if i.get('type') == 'duplicates']
        if duplicate_issues and total_records > 0:
            duplicate_records = sum(i.get('affected_records', 0) for i in duplicate_issues)
            duplicate_score = max(0, 100 - (duplicate_records / total_records * 100))
        else:
            duplicate_score = 100  # Duplicate yoksa tam puan
        scores.append(('duplicates', duplicate_score, 0.2))
        
        # Freshness skoru (ağırlık: 10%)
        freshness = self.quality_report['quality_scores'].get('data_freshness', {})
        age_days = freshness.get('age_days', 0)
        
        if age_days <= 1:
            freshness_score = 100
        elif age_days <= 3:
            freshness_score = 80
        elif age_days <= 7:
            freshness_score = 60
        else:
            freshness_score = 40
        scores.append(('freshness', freshness_score, 0.1))
        
        # Ağırlıklı ortalama hesapla
        if scores:
            weighted_score = sum(score * weight for _, score, weight in scores)
            
            self.quality_report['overall_quality_score'] = {
                'score': round(weighted_score, 1),
                'grade': self._get_grade(weighted_score),
                'component_scores': {name: score for name, score, _ in scores}
            }
            
            logger.info(f"✅ Genel kalite skoru: {weighted_score:.1f}/100 ({self._get_grade(weighted_score)})")
        
    def _get_grade(self, score: float) -> str:
        """Skordan harf notu üret."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def save_report(self, output_file: str = 'data/quality_report.json'):
        """Kalite raporunu kaydet."""
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.quality_report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Kalite raporu kaydedildi: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rapor kaydetme hatası: {e}")
            return False
    
    def print_summary(self):
        """Özet raporu yazdır."""
        logger.info("📋 VERİ KALİTESİ RAPORU ÖZETİ")
        logger.info("=" * 40)
        
        # Genel bilgiler
        total = self.quality_report['total_records']
        logger.info(f"📊 Toplam kayıt: {total:,}")
        
        # Genel skor
        overall = self.quality_report.get('overall_quality_score', {})
        if overall:
            score = overall['score']
            grade = overall['grade']
            logger.info(f"🎯 Kalite skoru: {score}/100 (Not: {grade})")
        
        # Issue özeti
        issues = self.quality_report.get('issues', [])
        if issues:
            critical = len([i for i in issues if i.get('severity') == 'critical'])
            warning = len([i for i in issues if i.get('severity') == 'warning'])
            
            logger.info(f"⚠️ Sorunlar: {critical} kritik, {warning} uyarı")
        else:
            logger.info("✅ Hiç kalite sorunu yok!")
        
        # Öneri sayısı
        recommendations = self.quality_report.get('recommendations', [])
        logger.info(f"💡 Öneriler: {len(recommendations)} madde")
        
        logger.info("")
        logger.info("🔗 Detaylı rapor: data/quality_report.json")
    
    def run_full_analysis(self):
        """Tam kalite analizi yap."""
        logger.info("🔍 TÜRKİYE SAĞLIK KURULUŞLARI - VERİ KALİTESİ ANALİZİ")
        logger.info("=" * 65)
        
        if not self.load_data():
            return False
        
        # Analizleri sırayla çalıştır
        self.check_completeness()
        self.check_data_consistency()
        self.check_duplicates()
        self.check_data_freshness()
        self.generate_recommendations()
        self.calculate_overall_score()
        
        # Raporu kaydet ve özetle
        self.save_report()
        self.print_summary()
        
        return True

def main():
    """Ana fonksiyon."""
    monitor = DataQualityMonitor()
    success = monitor.run_full_analysis()
    
    if success:
        logger.info("✅ Veri kalitesi analizi tamamlandı!")
    else:
        logger.error("❌ Veri kalitesi analizi başarısız!")
        sys.exit(1)

if __name__ == "__main__":
    main()
