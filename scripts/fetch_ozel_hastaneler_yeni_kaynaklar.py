#!/usr/bin/env python3
"""
Özel Hastaneler Yeni Veri Kaynakları Keşif Scripti
================================================

Yeni keşfedilen özel hastane veri kaynakları:
1. 81 İl Sağlık Müdürlüğü özel hastane birimleri
2. Hakem hastane listeleri (MEB PDF)
3. Sağlıkta Kalite Değerlendirme listeleri
4. Özel Hastaneler Birimi dokümanları
5. İl bazlı özel hastane nöbet listeleri
"""

import requests
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OzelHastanelerYeniKaynaklar:
    """Özel hastaneler için yeni veri kaynaklarını çeken sınıf."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 81 İl Sağlık Müdürlüğü domain listesi
        self.il_saglik_mudurlukleri = [
            'adanaism.saglik.gov.tr', 'adiyamanisme.saglik.gov.tr', 'afyonism.saglik.gov.tr',
            'agriism.saglik.gov.tr', 'amasyaism.saglik.gov.tr', 'ankaraism.saglik.gov.tr',
            'antalyaism.saglik.gov.tr', 'artvinism.saglik.gov.tr', 'aydinism.saglik.gov.tr',
            'balikesirism.saglik.gov.tr', 'bilecikism.saglik.gov.tr', 'bingolism.saglik.gov.tr',
            'bitlisism.saglik.gov.tr', 'boluism.saglik.gov.tr', 'burdurism.saglik.gov.tr',
            'bursaism.saglik.gov.tr', 'canakkaleism.saglik.gov.tr', 'cankiriism.saglik.gov.tr',
            'corumism.saglik.gov.tr', 'denizliism.saglik.gov.tr', 'diyarbakirism.saglik.gov.tr',
            'edirneism.saglik.gov.tr', 'elazigism.saglik.gov.tr', 'erzincanisme.saglik.gov.tr',
            'erzurumism.saglik.gov.tr', 'eskisehirism.saglik.gov.tr', 'gaziantepism.saglik.gov.tr',
            'giresunism.saglik.gov.tr', 'gumushaneism.saglik.gov.tr', 'hakkariism.saglik.gov.tr',
            'hatayism.saglik.gov.tr', 'ispartaism.saglik.gov.tr', 'mersinism.saglik.gov.tr',
            'istanbulism.saglik.gov.tr', 'izmirism.saglik.gov.tr', 'karsism.saglik.gov.tr',
            'kastamonuism.saglik.gov.tr', 'kayserism.saglik.gov.tr', 'kirklareliism.saglik.gov.tr',
            'kirsehirism.saglik.gov.tr', 'kocaeliism.saglik.gov.tr', 'konyaism.saglik.gov.tr',
            'kutahyaism.saglik.gov.tr', 'malatyaism.saglik.gov.tr', 'manisaism.saglik.gov.tr',
            'kahramanmarasism.saglik.gov.tr', 'mardinism.saglik.gov.tr', 'muglaism.saglik.gov.tr',
            'musism.saglik.gov.tr', 'nevsehirism.saglik.gov.tr', 'nigdeism.saglik.gov.tr',
            'orduism.saglik.gov.tr', 'rizeism.saglik.gov.tr', 'sakaryaism.saglik.gov.tr',
            'samsunism.saglik.gov.tr', 'siirtism.saglik.gov.tr', 'sinopism.saglik.gov.tr',
            'sivasism.saglik.gov.tr', 'tekirdagism.saglik.gov.tr', 'tokatism.saglik.gov.tr',
            'trabzonism.saglik.gov.tr', 'tunceliism.saglik.gov.tr', 'sanliurfaism.saglik.gov.tr',
            'usakism.saglik.gov.tr', 'vanisme.saglik.gov.tr', 'yozgatism.saglik.gov.tr',
            'zonguldakism.saglik.gov.tr', 'aksarayism.saglik.gov.tr', 'bayburtism.saglik.gov.tr',
            'karamanism.saglik.gov.tr', 'kirikkaleism.saglik.gov.tr', 'batmanism.saglik.gov.tr',
            'sirnakism.saglik.gov.tr', 'bartinism.saglik.gov.tr', 'ardahanism.saglik.gov.tr',
            'igdirism.saglik.gov.tr', 'yalovaism.saglik.gov.tr', 'karabukism.saglik.gov.tr',
            'kilisism.saglik.gov.tr', 'osmaniyeism.saglik.gov.tr', 'duzceism.saglik.gov.tr'
        ]
        
        # Öncelikli büyük şehirler
        self.priority_cities = [
            'istanbulism.saglik.gov.tr', 'ankaraism.saglik.gov.tr', 'izmirism.saglik.gov.tr',
            'bursaism.saglik.gov.tr', 'antalyaism.saglik.gov.tr', 'adanaism.saglik.gov.tr',
            'konyaism.saglik.gov.tr', 'gaziantepism.saglik.gov.tr', 'kayserism.saglik.gov.tr',
            'eskisehirism.saglik.gov.tr', 'mersinism.saglik.gov.tr', 'kocaeliism.saglik.gov.tr'
        ]
        
        # Alternatif veri kaynakları
        self.alternatif_kaynaklar = {
            'kalite_degerlendirme': 'https://shgmkalitedb.saglik.gov.tr',
            'hakem_hastaneler': 'https://nallihan.meb.gov.tr/meb_iys_dosyalar/2020_01/31092458_Ek-12_Hakem_Hastane_Listesi_Ylk_Ytiraz_Hastaneleri.pdf',
            'ozel_hastaneler_db': 'https://shgmozelhasdb.saglik.gov.tr'
        }
        
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_il_ozel_hastaneler(self, domain: str) -> List[Dict]:
        """Bir İl Sağlık Müdürlüğü'nden özel hastane listesini çek"""
        hospitals = []
        
        try:
            il_adi = domain.split('ism.')[0].title()
            logger.info(f"İl taranıyor: {il_adi}")
            
            # Farklı sayfa yapılarını dene
            urls_to_check = [
                f'https://{domain}',  # Ana sayfa
                f'https://{domain}/TR-11541/ozel-hastaneler.html',  # Mersin formatı
                f'https://{domain}/baskanlik/ozel-hastaneler-birimi-detay/900901',  # Antalya formatı
                f'https://{domain}/ozel-hastaneler',
                f'https://{domain}/hastaneler',
                f'https://{domain}/saglik-tesisleri'
            ]
            
            for url in urls_to_check:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Ana sayfada özel hastane isimlerini ara
                        page_text = soup.get_text().lower()
                        
                        # Özel hastane pattern'lerini bul
                        hospital_patterns = [
                            r'özel\s+[\w\s]+hastane[^\.]*',
                            r'[\w\s]+medical[\w\s]*hastane[^\.]*',
                            r'[\w\s]+hospital[^\.]*',
                            r'özel\s+[\w\s]+tıp\s+merkezi[^\.]*'
                        ]
                        
                        for pattern in hospital_patterns:
                            matches = re.findall(pattern, page_text, re.IGNORECASE)
                            for match in matches:
                                hospital_name = self._clean_hospital_name(match)
                                if hospital_name and len(hospital_name) > 5:
                                    hospital = {
                                        'kurum_adi': hospital_name,
                                        'kurum_tipi': 'Özel Hastane',
                                        'il_adi': il_adi,
                                        'veri_kaynagi': f'İl Sağlık Müdürlüğü - {il_adi}',
                                        'kaynak_url': url,
                                        'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
                                    }
                                    hospitals.append(hospital)
                        
                        # Eğer veri bulunduysa diğer URL'leri deneme
                        if hospitals:
                            break
                            
                except Exception as url_error:
                    continue
            
            if hospitals:
                logger.info(f"✅ {il_adi}: {len(hospitals)} özel hastane bulundu")
            
        except Exception as e:
            logger.warning(f"İl sağlık müdürlüğü hatası {domain}: {e}")
        
        return hospitals
    
    def _clean_hospital_name(self, raw_name: str) -> str:
        """Hastane adını temizle"""
        # Gereksiz kelimeleri temizle
        clean_name = raw_name.strip()
        clean_name = re.sub(r'\s+', ' ', clean_name)  # Çoklu boşlukları tek boşluk yap
        clean_name = re.sub(r'[^\w\s-]', '', clean_name)  # Özel karakterleri temizle
        
        # Çok kısa veya geçersiz isimleri filtrele
        if len(clean_name) < 5 or any(word in clean_name.lower() for word in ['duyuru', 'haber', 'sayfa', 'site']):
            return ''
        
        return clean_name.title()
    
    def fetch_hakem_hastane_listesi(self) -> List[Dict]:
        """MEB Hakem Hastane PDF listesini çek"""
        hospitals = []
        
        try:
            pdf_url = self.alternatif_kaynaklar['hakem_hastaneler']
            logger.info("Hakem hastane PDF listesi indiriliyor...")
            
            response = self.session.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            # PDF'i geçici dosya olarak kaydet
            temp_pdf = f"temp_hakem_hastaneler_{datetime.now().strftime('%Y%m%d')}.pdf"
            with open(temp_pdf, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ PDF indirildi: {temp_pdf}")
            
            # Not: PDF parse için PyPDF2 veya pdfplumber kütüphanesi gerekli
            # Şimdilik dosyayı kaydet, manuel parse için
            
            # Geçici dosyayı temizle
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
                
        except Exception as e:
            logger.error(f"Hakem hastane PDF hatası: {e}")
        
        return hospitals
    
    def fetch_kalite_degerlendirme_listesi(self) -> List[Dict]:
        """Sağlıkta Kalite Değerlendirme listesini çek"""
        hospitals = []
        
        try:
            base_url = self.alternatif_kaynaklar['kalite_degerlendirme']
            logger.info("Kalite değerlendirme listeleri taranıyor...")
            
            response = self.session.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Excel/PDF linklerini bul
            doc_links = soup.find_all('a', href=re.compile(r'\.(xlsx?|pdf)$', re.I))
            
            for link in doc_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if any(keyword in text.lower() for keyword in ['liste', 'kurum', 'hastane', 'kalite']):
                    if not href.startswith('http'):
                        href = base_url + href
                    
                    logger.info(f"✓ Kalite değerlendirme dosyası: {text} - {href}")
                    
                    # Bu dosyaları parse edebiliriz
                    if href.endswith(('.xlsx', '.xls')):
                        hospitals.extend(self._parse_excel_file(href, 'Kalite Değerlendirmesi'))
            
        except Exception as e:
            logger.error(f"Kalite değerlendirme hatası: {e}")
        
        return hospitals
    
    def _parse_excel_file(self, url: str, source_type: str) -> List[Dict]:
        """Excel dosyasını parse et"""
        hospitals = []
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            temp_file = f"temp_excel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            try:
                import pandas as pd
                df = pd.read_excel(temp_file)
                
                for _, row in df.iterrows():
                    if len(row) > 0:
                        hospital = {
                            'kurum_adi': str(row.iloc[0]),
                            'kurum_tipi': 'Özel Hastane',
                            'veri_kaynagi': source_type,
                            'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
                            'excel_url': url
                        }
                        
                        if len(row) > 1:
                            hospital['il_adi'] = str(row.iloc[1])
                        if len(row) > 2:
                            hospital['ilce_adi'] = str(row.iloc[2])
                            
                        hospitals.append(hospital)
                
                logger.info(f"✅ Excel parse edildi: {len(hospitals)} hastane")
                
            except Exception as parse_error:
                logger.error(f"Excel parse hatası: {parse_error}")
            
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            logger.error(f"Excel indirme hatası {url}: {e}")
        
        return hospitals
    
    def fetch_all_ozel_hastane_sources(self) -> List[Dict]:
        """Tüm özel hastane veri kaynaklarını çek"""
        all_hospitals = []
        
        logger.info("🏥 Özel hastaneler yeni veri kaynakları taranıyor...")
        
        # 1. Öncelikli büyük şehir İl Sağlık Müdürlükleri
        for domain in self.priority_cities:
            hospitals = self.fetch_il_ozel_hastaneler(domain)
            all_hospitals.extend(hospitals)
        
        logger.info(f"✅ Büyük şehir İSM'ler: {len(all_hospitals)} hastane")
        
        # 2. Hakem Hastane Listesi
        hakem_hospitals = self.fetch_hakem_hastane_listesi()
        all_hospitals.extend(hakem_hospitals)
        logger.info(f"✅ Hakem hastaneler: {len(hakem_hospitals)} hastane")
        
        # 3. Kalite Değerlendirme Listesi
        kalite_hospitals = self.fetch_kalite_degerlendirme_listesi()
        all_hospitals.extend(kalite_hospitals)
        logger.info(f"✅ Kalite değerlendirme: {len(kalite_hospitals)} hastane")
        
        # Duplikatları temizle
        unique_hospitals = []
        seen_names = set()
        
        for hospital in all_hospitals:
            name_key = hospital['kurum_adi'].lower().strip()
            if name_key not in seen_names and len(name_key) > 5:
                seen_names.add(name_key)
                unique_hospitals.append(hospital)
        
        logger.info(f"🎯 Toplam benzersiz özel hastane: {len(unique_hospitals)}")
        return unique_hospitals
    
    def save_data(self, hospitals: List[Dict]):
        """Verileri kaydet"""
        json_file = os.path.join(self.data_dir, 'ozel_hastaneler_yeni_kaynaklar.json')
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(hospitals, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Özel hastane verileri kaydedildi: {json_file}")

def main():
    """Ana fonksiyon"""
    logger.info("Özel hastaneler yeni veri kaynakları keşfi başlıyor...")
    
    fetcher = OzelHastanelerYeniKaynaklar()
    
    try:
        hospitals = fetcher.fetch_all_ozel_hastane_sources()
        
        if hospitals:
            fetcher.save_data(hospitals)
            
            # İstatistikler
            cities = {}
            for hospital in hospitals:
                city = hospital.get('il_adi', 'Bilinmiyor')
                cities[city] = cities.get(city, 0) + 1
            
            logger.info("🏙️ İl bazlı dağılım:")
            for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
                logger.info(f"   - {city}: {count}")
                
            logger.info("✅ Özel hastaneler yeni kaynaklar işlemi tamamlandı!")
        else:
            logger.warning("❌ Hiç özel hastane bulunamadı!")
            
    except Exception as e:
        logger.error(f"❌ İşlem başarısız: {e}")

if __name__ == "__main__":
    main()
