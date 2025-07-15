#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mükerrer Sağlık Kurumu Kayıtlarını Birleştirme Modülü

Bu modül, farklı kaynaklardan gelen sağlık kurumu verilerindeki mükerrer kayıtları
tespit eder ve en kapsamlı veriyi koruyarak birleştirir.

Author: TURSAKUR Team
Version: 1.0.0
Date: 2025-01-14
"""

import json
import logging
import hashlib
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from difflib import SequenceMatcher
from geopy.distance import geodesic
import unicodedata

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/merge_duplicates.log', encoding='utf-8'),
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
    koordinat_lat: Optional[float]
    koordinat_lon: Optional[float]
    web_sitesi: Optional[str]
    veri_kaynagi: str
    son_guncelleme: str
    kaynak_url: Optional[str] = None  # Özel hastaneler için ek alan

class DuplicateMerger:
    """Mükerrer kayıt birleştirme sınıfı"""
    
    def __init__(self):
        self.similarity_threshold = 0.85  # Benzerlik eşiği
        self.coordinate_threshold = 1.0   # Koordinat mesafe eşiği (km)
        self.merged_count = 0
        self.duplicate_count = 0
        
    def normalize_text(self, text: str) -> str:
        """Metni normalize et"""
        if not text:
            return ""
        
        # Unicode normalizasyonu
        text = unicodedata.normalize('NFKD', text)
        
        # Küçük harfe çevir
        text = text.lower()
        
        # Özel karakterleri kaldır
        text = re.sub(r'[^\w\s]', '', text)
        
        # Fazla boşlukları kaldır
        text = re.sub(r'\s+', ' ', text)
        
        # Yaygın kısaltmaları genişlet
        replacements = {
            'hast': 'hastane',
            'üniv': 'üniversite',
            'eğt': 'eğitim',
            'arş': 'araştırma',
            'dev': 'devlet',
            'mrk': 'merkez',
            'asm': 'aile sağlığı merkezi',
            'tsm': 'toplum sağlığı merkezi',
            'adsm': 'ağız diş sağlığı merkezi'
        }
        
        for abbrev, full in replacements.items():
            text = text.replace(abbrev, full)
        
        return text.strip()
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """İki kurum adı arasındaki benzerliği hesapla"""
        norm1 = self.normalize_text(name1)
        norm2 = self.normalize_text(name2)
        
        # Sequence matcher ile benzerlik
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Anahtar kelimeler benzerliği
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if words1 and words2:
            word_similarity = len(words1 & words2) / len(words1 | words2)
            # Kelime benzerliğini daha ağırlıklı yap
            similarity = (similarity * 0.6) + (word_similarity * 0.4)
        
        return similarity
    
    def calculate_address_similarity(self, addr1: str, addr2: str) -> float:
        """İki adres arasındaki benzerliği hesapla"""
        if not addr1 or not addr2:
            return 0.0
        
        norm1 = self.normalize_text(addr1)
        norm2 = self.normalize_text(addr2)
        
        # Sequence matcher ile benzerlik
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Adres bileşenleri benzerliği
        addr_components1 = set(norm1.split())
        addr_components2 = set(norm2.split())
        
        if addr_components1 and addr_components2:
            component_similarity = len(addr_components1 & addr_components2) / len(addr_components1 | addr_components2)
            similarity = (similarity * 0.7) + (component_similarity * 0.3)
        
        return similarity
    
    def calculate_coordinate_distance(self, inst1: HealthInstitution, inst2: HealthInstitution) -> Optional[float]:
        """İki kurum arasındaki koordinat mesafesini hesapla (km)"""
        if (inst1.koordinat_lat is None or inst1.koordinat_lon is None or
            inst2.koordinat_lat is None or inst2.koordinat_lon is None):
            return None
        
        try:
            coord1 = (inst1.koordinat_lat, inst1.koordinat_lon)
            coord2 = (inst2.koordinat_lat, inst2.koordinat_lon)
            return geodesic(coord1, coord2).kilometers
        except Exception:
            return None
    
    def normalize_phone(self, phone: str) -> str:
        """Telefon numarasını normalize et"""
        if not phone:
            return ""
        
        # Sadece rakamları al
        digits = re.sub(r'\D', '', phone)
        
        # Türkiye formatına çevir
        if len(digits) == 10:
            return f"+90{digits}"
        elif len(digits) == 11 and digits.startswith('0'):
            return f"+90{digits[1:]}"
        elif len(digits) == 12 and digits.startswith('90'):
            return f"+{digits}"
        
        return phone
    
    def is_duplicate(self, inst1: HealthInstitution, inst2: HealthInstitution) -> Tuple[bool, float]:
        """İki kurumun mükerrer olup olmadığını kontrol et"""
        
        # Aynı kayıt kontrolü
        if inst1.kurum_id == inst2.kurum_id:
            return True, 1.0
        
        # İl kontrolü - farklı illerde olamaz
        if inst1.il_kodu != inst2.il_kodu:
            return False, 0.0
        
        # İsim benzerliği
        name_similarity = self.calculate_name_similarity(inst1.kurum_adi, inst2.kurum_adi)
        
        # Adres benzerliği
        address_similarity = self.calculate_address_similarity(inst1.adres, inst2.adres)
        
        # Koordinat mesafesi
        coord_distance = self.calculate_coordinate_distance(inst1, inst2)
        
        # Telefon benzerliği
        phone_similarity = 0.0
        norm_phone1 = self.normalize_phone(inst1.telefon)
        norm_phone2 = self.normalize_phone(inst2.telefon)
        if norm_phone1 and norm_phone2 and norm_phone1 == norm_phone2:
            phone_similarity = 1.0
        
        # Kurum tipi benzerliği
        type_similarity = 1.0 if inst1.kurum_tipi == inst2.kurum_tipi else 0.0
        
        # Genel benzerlik skoru
        similarity_score = (
            name_similarity * 0.4 +
            address_similarity * 0.2 +
            type_similarity * 0.2 +
            phone_similarity * 0.2
        )
        
        # Koordinat mesafesi varsa bonus
        if coord_distance is not None:
            if coord_distance <= self.coordinate_threshold:
                similarity_score += 0.1
            else:
                similarity_score -= 0.1
        
        similarity_score = max(0.0, min(1.0, similarity_score))
        
        # Eşik kontrolü
        is_dup = similarity_score >= self.similarity_threshold
        
        if is_dup:
            logger.debug(f"Mükerrer bulundu: {inst1.kurum_adi} ↔ {inst2.kurum_adi} (Skor: {similarity_score:.3f})")
        
        return is_dup, similarity_score
    
    def merge_institutions(self, institutions: List[HealthInstitution]) -> HealthInstitution:
        """Birden fazla kurumu birleştir"""
        if len(institutions) == 1:
            return institutions[0]
        
        # En kapsamlı veriyi bul
        primary = self._find_most_comprehensive(institutions)
        
        # Diğer verilerden eksik bilgileri tamamla
        for inst in institutions:
            if inst.kurum_id == primary.kurum_id:
                continue
            
            # Boş alanları doldur
            if not primary.adres and inst.adres:
                primary.adres = inst.adres
            
            if not primary.telefon and inst.telefon:
                primary.telefon = inst.telefon
            
            if primary.koordinat_lat is None and inst.koordinat_lat is not None:
                primary.koordinat_lat = inst.koordinat_lat
                primary.koordinat_lon = inst.koordinat_lon
            
            if not primary.web_sitesi and inst.web_sitesi:
                primary.web_sitesi = inst.web_sitesi
            
            # Daha uzun/detaylı metinleri tercih et
            if len(inst.adres) > len(primary.adres):
                primary.adres = inst.adres
            
            # Veri kaynaklarını birleştir
            if inst.veri_kaynagi not in primary.veri_kaynagi:
                primary.veri_kaynagi = f"{primary.veri_kaynagi}, {inst.veri_kaynagi}"
        
        # Güncelleme tarihini en son yap
        primary.son_guncelleme = datetime.now().strftime('%Y-%m-%d')
        
        return primary
    
    def _find_most_comprehensive(self, institutions: List[HealthInstitution]) -> HealthInstitution:
        """En kapsamlı veriyi bul"""
        scores = []
        
        for inst in institutions:
            score = 0
            
            # Veri completeness skoru
            if inst.adres:
                score += len(inst.adres) * 0.1
            if inst.telefon:
                score += 10
            if inst.koordinat_lat is not None:
                score += 15
            if inst.web_sitesi:
                score += 5
            
            # Güvenilir kaynaklar bonus
            reliable_sources = ['sağlık bakanlığı', 'üniversite', 'resmi']
            if any(source in inst.veri_kaynagi.lower() for source in reliable_sources):
                score += 20
            
            scores.append((score, inst))
        
        # En yüksek skoru döndür
        return max(scores, key=lambda x: x[0])[1]
    
    def find_duplicates(self, institutions: List[HealthInstitution]) -> Dict[str, List[HealthInstitution]]:
        """Mükerrer kayıtları bul ve grupla"""
        duplicate_groups = {}
        processed = set()
        
        for i, inst1 in enumerate(institutions):
            if inst1.kurum_id in processed:
                continue
            
            group = [inst1]
            processed.add(inst1.kurum_id)
            
            for j, inst2 in enumerate(institutions[i+1:], i+1):
                if inst2.kurum_id in processed:
                    continue
                
                is_dup, similarity = self.is_duplicate(inst1, inst2)
                
                if is_dup:
                    group.append(inst2)
                    processed.add(inst2.kurum_id)
                    logger.info(f"Mükerrer tespit edildi: {inst1.kurum_adi} ↔ {inst2.kurum_adi} (Benzerlik: {similarity:.3f})")
            
            if len(group) > 1:
                self.duplicate_count += len(group) - 1
                group_id = f"duplicate_group_{len(duplicate_groups) + 1}"
                duplicate_groups[group_id] = group
            else:
                # Tekil kayıt
                duplicate_groups[inst1.kurum_id] = group
        
        return duplicate_groups
    
    def merge_all_duplicates(self, institutions: List[HealthInstitution]) -> List[HealthInstitution]:
        """Tüm mükerrer kayıtları birleştir"""
        logger.info(f"Toplam {len(institutions)} kurum için mükerrer analizi başlatılıyor...")
        
        duplicate_groups = self.find_duplicates(institutions)
        merged_institutions = []
        
        for group_id, group in duplicate_groups.items():
            if len(group) > 1:
                merged = self.merge_institutions(group)
                merged_institutions.append(merged)
                self.merged_count += 1
                logger.info(f"Grup birleştirildi: {[inst.kurum_adi for inst in group]} → {merged.kurum_adi}")
            else:
                merged_institutions.append(group[0])
        
        logger.info(f"Birleştirme tamamlandı: {self.duplicate_count} mükerrer kayıt, {self.merged_count} birleştirme")
        return merged_institutions
    
    def generate_merge_report(self, original_count: int, final_count: int) -> str:
        """Birleştirme raporu oluştur"""
        report = f"""
=== MÜKERRER KAYIT BİRLEŞTİRME RAPORU ===

Başlangıç kurum sayısı: {original_count}
Final kurum sayısı: {final_count}
Tespit edilen mükerrer kayıt: {self.duplicate_count}
Yapılan birleştirme: {self.merged_count}
Azalma oranı: {((original_count - final_count) / original_count * 100):.1f}%

Benzerlik eşiği: {self.similarity_threshold}
Koordinat mesafe eşiği: {self.coordinate_threshold} km

Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report

def load_institutions_from_files(file_paths: List[str]) -> List[HealthInstitution]:
    """Birden fazla dosyadan kurumları yükle"""
    all_institutions = []
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                # Veri formatını normalize et
                normalized_item = {}
                
                # Gerekli alanları kontrol et ve default değerler ver
                normalized_item['kurum_id'] = item.get('kurum_id', '')
                normalized_item['kurum_adi'] = item.get('kurum_adi', '')
                normalized_item['kurum_tipi'] = item.get('kurum_tipi', '')
                normalized_item['il_kodu'] = item.get('il_kodu', 0)
                normalized_item['il_adi'] = item.get('il_adi', '')
                normalized_item['ilce_adi'] = item.get('ilce_adi', '')
                normalized_item['adres'] = item.get('adres', '')
                normalized_item['telefon'] = item.get('telefon', '')
                normalized_item['koordinat_lat'] = item.get('koordinat_lat')
                normalized_item['koordinat_lon'] = item.get('koordinat_lon')
                normalized_item['web_sitesi'] = item.get('web_sitesi', '')
                normalized_item['veri_kaynagi'] = item.get('veri_kaynagi', '')
                normalized_item['son_guncelleme'] = item.get('son_guncelleme', '')
                normalized_item['kaynak_url'] = item.get('kaynak_url')
                
                institution = HealthInstitution(**normalized_item)
                all_institutions.append(institution)
            
            logger.info(f"{file_path} dosyasından {len(data)} kurum yüklendi")
            
        except Exception as e:
            logger.error(f"{file_path} dosyası yüklenemedi: {e}")
    
    return all_institutions

def save_institutions_to_file(institutions: List[HealthInstitution], file_path: str):
    """Kurumları dosyaya kaydet"""
    try:
        data = [asdict(institution) for institution in institutions]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"{len(institutions)} kurum {file_path} dosyasına kaydedildi")
        
    except Exception as e:
        logger.error(f"Dosya kaydetme hatası: {e}")

def main():
    """Ana fonksiyon"""
    try:
        # Log dizinini oluştur
        import os
        os.makedirs('logs', exist_ok=True)
        
        logger.info("Mükerrer kayıt birleştirme işlemi başlatılıyor...")
        
        # Veri dosyalarını belirle
        data_files = [
            'data/raw/saglik_bakanligi_tesisleri.json',
            'data/raw/ozel_hastaneler.json',
            'data/raw/universite_hastaneleri.json',
            'data/raw/trhastane_universite_hastaneleri.json',
            'data/raw/kapsamli_universite_hastane_iliskileri.json',
            'data/raw/il_saglik_test.json'  # Test dosyası
        ]
        
        # Mevcut dosyaları kontrol et
        existing_files = []
        for file_path in data_files:
            if os.path.exists(file_path):
                existing_files.append(file_path)
            else:
                logger.warning(f"Dosya bulunamadı: {file_path}")
        
        if not existing_files:
            logger.error("Hiçbir veri dosyası bulunamadı!")
            return 1
        
        # Kurumları yükle
        institutions = load_institutions_from_files(existing_files)
        original_count = len(institutions)
        
        if not institutions:
            logger.error("Hiçbir kurum verisi yüklenemedi!")
            return 1
        
        # Mükerrer kayıtları birleştir
        merger = DuplicateMerger()
        merged_institutions = merger.merge_all_duplicates(institutions)
        final_count = len(merged_institutions)
        
        # Sonuçları kaydet
        output_file = 'data/turkiye_saglik_kuruluslari_merged.json'
        save_institutions_to_file(merged_institutions, output_file)
        
        # Rapor oluştur
        report = merger.generate_merge_report(original_count, final_count)
        print(report)
        
        # Raporu dosyaya kaydet
        with open('logs/merge_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("Mükerrer kayıt birleştirme işlemi başarıyla tamamlandı")
        
    except Exception as e:
        logger.error(f"Ana fonksiyon hatası: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
