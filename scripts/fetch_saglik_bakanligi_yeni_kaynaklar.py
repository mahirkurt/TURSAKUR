#!/usr/bin/env python3
"""
Sağlık Bakanlığı Yeni Veri Kaynakları Keşif Scripti
=================================================

Yeni keşfedilen veri kaynakları:
1. KHGM Kamu Hastaneleri Listesi (khgmsaglikhizmetleridb.saglik.gov.tr)
2. Sağlık Turizmi Yetki Belgeli Tesisler (shgmturizmdb.saglik.gov.tr)
3. İl Sağlık Müdürlükleri (Özel hekim muayenehaneleri)
4. Kalite Akreditasyon (shgmkalitedb.saglik.gov.tr)
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

class SaglikBakanligiYeniKaynaklar:
    """Sağlık Bakanlığı'nın yeni keşfedilen veri kaynaklarını çeken sınıf."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Yeni keşfedilen kaynaklar
        self.veri_kaynaklari = {
            'khgm_kamu_hastaneleri': {
                'url': 'https://khgmsaglikhizmetleridb.saglik.gov.tr/TR-87343/kamu-hastaneleri-genel-mudurlugune-bagli-2-ve-3-basamak-kamu-saglik-tesisleri-guncel-listesi.html',
                'tip': 'html_table',
                'hedef': 'Kamu hastaneleri 2.-3. basamak'
            },
            'saglik_turizmi': {
                'url': 'https://shgmturizmdb.saglik.gov.tr/',
                'tip': 'file_download',
                'hedef': 'Sağlık turizmi yetki belgeli tesisler'
            },
            'khgm_site_haritasi': {
                'url': 'https://khgm.saglik.gov.tr/Siteagaci',
                'tip': 'link_crawler',
                'hedef': 'Şehir hastaneleri linkleri'
            },
            'ankara_il_saglik': {
                'url': 'https://ankaraism.saglik.gov.tr/TR-228957/dokumanlar.html',
                'tip': 'excel_download',
                'hedef': 'Özel hekim muayenehaneleri'
            },
            'kalite_akreditasyon': {
                'url': 'https://shgmkalitedb.saglik.gov.tr/TR-52461/guncel-standartlar-excel-versiyon.html',
                'tip': 'excel_download',
                'hedef': 'Akredite sağlık tesisleri'
            }
        }
        
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_khgm_kamu_hastaneleri(self) -> List[Dict]:
        """KHGM Kamu hastaneleri listesini çek"""
        hospitals = []
        url = self.veri_kaynaklari['khgm_kamu_hastaneleri']['url']
        
        try:
            logger.info("KHGM Kamu hastaneleri listesi çekiliyor...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Excel veya PDF linklerini bul
            links = soup.find_all('a', href=re.compile(r'\.(xlsx?|pdf)$', re.I))
            
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if 'liste' in text.lower() or 'excel' in text.lower():
                    if not href.startswith('http'):
                        href = 'https://khgmsaglikhizmetleridb.saglik.gov.tr' + href
                    
                    logger.info(f"✓ KHGM dosyası bulundu: {text} - {href}")
                    
                    # Bu Excel dosyasını indirip parse edebiliriz
                    if href.endswith(('.xlsx', '.xls')):
                        hospitals.extend(self._download_and_parse_excel(href, 'KHGM Kamu Hastaneleri'))
            
        except Exception as e:
            logger.error(f"KHGM kamu hastaneleri hatası: {e}")
        
        return hospitals
    
    def fetch_saglik_turizmi_tesisleri(self) -> List[Dict]:
        """Sağlık turizmi yetki belgeli tesisleri çek"""
        facilities = []
        base_url = 'https://shgmturizmdb.saglik.gov.tr'
        
        try:
            logger.info("Sağlık turizmi tesisleri çekiliyor...")
            response = self.session.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # PDF/Excel linklerini bul
            links = soup.find_all('a', href=re.compile(r'(yetki|liste|tesis)', re.I))
            
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if 'liste' in text.lower() or 'tesis' in text.lower():
                    if not href.startswith('http'):
                        href = base_url + href
                    
                    logger.info(f"✓ Sağlık turizmi dosyası: {text} - {href}")
                    
                    # PDF'den metin çıkarımı veya Excel parse
                    if href.endswith('.pdf'):
                        facilities.extend(self._parse_pdf_content(href, 'Sağlık Turizmi Tesisi'))
                    elif href.endswith(('.xlsx', '.xls')):
                        facilities.extend(self._download_and_parse_excel(href, 'Sağlık Turizmi Tesisi'))
            
        except Exception as e:
            logger.error(f"Sağlık turizmi tesisleri hatası: {e}")
        
        return facilities
    
    def fetch_il_saglik_mudurlukteri(self) -> List[Dict]:
        """81 İl Sağlık Müdürlüğü'nden özel hekim listelerini çek"""
        all_facilities = []
        
        # Büyük şehir il sağlık müdürlükleri
        il_domains = [
            'ankaraism.saglik.gov.tr',
            'istanbulism.saglik.gov.tr', 
            'izmirism.saglik.gov.tr',
            'bursaism.saglik.gov.tr',
            'antalyaism.saglik.gov.tr',
            'adanaism.saglik.gov.tr',
            'konyaism.saglik.gov.tr',
            'gaziantepism.saglik.gov.tr',
            'kayserism.saglik.gov.tr'
        ]
        
        for domain in il_domains:
            try:
                logger.info(f"İl Sağlık Müdürlüğü taranıyor: {domain}")
                
                # Dokuman sayfasını kontrol et
                urls_to_check = [
                    f'https://{domain}/TR-228957/dokumanlar.html',
                    f'https://{domain}/dokumanlar',
                    f'https://{domain}/ozel-hekim',
                    f'https://{domain}/listeler'
                ]
                
                for url in urls_to_check:
                    facilities = self._fetch_il_documents(url, domain.split('.')[0])
                    all_facilities.extend(facilities)
                    
            except Exception as e:
                logger.warning(f"İl Sağlık Müdürlüğü hatası {domain}: {e}")
                continue
        
        return all_facilities
    
    def _download_and_parse_excel(self, url: str, facility_type: str) -> List[Dict]:
        """Excel dosyasını indir ve parse et"""
        facilities = []
        
        try:
            logger.info(f"Excel indiriliyor: {url}")
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Geçici dosya olarak kaydet
            temp_file = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            # Pandas ile parse et
            try:
                import pandas as pd
                df = pd.read_excel(temp_file, sheet_name=0)
                
                for _, row in df.iterrows():
                    facility = {
                        'kurum_adi': str(row.iloc[0]) if len(row) > 0 else '',
                        'kurum_tipi': facility_type,
                        'veri_kaynagi': f'Sağlık Bakanlığı - {facility_type}',
                        'son_guncelleme': datetime.now().strftime('%Y-%m-%d'),
                        'excel_url': url
                    }
                    
                    # Diğer sütunları da ekle
                    if len(row) > 1:
                        facility['il_adi'] = str(row.iloc[1])
                    if len(row) > 2:
                        facility['ilce_adi'] = str(row.iloc[2])
                    if len(row) > 3:
                        facility['adres'] = str(row.iloc[3])
                    
                    facilities.append(facility)
                
                logger.info(f"✅ Excel parse edildi: {len(facilities)} kayıt")
                
            except Exception as parse_error:
                logger.error(f"Excel parse hatası: {parse_error}")
            
            # Geçici dosyayı sil
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            logger.error(f"Excel indirme hatası {url}: {e}")
        
        return facilities
    
    def _parse_pdf_content(self, url: str, facility_type: str) -> List[Dict]:
        """PDF içeriğini parse et (basit metin çıkarımı)"""
        facilities = []
        
        try:
            logger.info(f"PDF indiriliyor: {url}")
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # PDF parse için PyPDF2 veya pdfplumber kullanılabilir
            # Şimdilik basit text search yapalım
            
            temp_file = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            # PDF text extraction burada olacak
            logger.info(f"PDF kaydedildi: {temp_file} (manuel parse gerekli)")
            
            # Geçici dosyayı temizle
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            logger.error(f"PDF parse hatası {url}: {e}")
        
        return facilities
    
    def _fetch_il_documents(self, url: str, il_adi: str) -> List[Dict]:
        """İl Sağlık Müdürlüğü doküman sayfasını tara"""
        facilities = []
        
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Excel linklerini bul
            excel_links = soup.find_all('a', href=re.compile(r'\.(xlsx?|csv)$', re.I))
            
            for link in excel_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if any(keyword in text.lower() for keyword in ['hekim', 'muayene', 'liste', 'tesis']):
                    if not href.startswith('http'):
                        base_url = '/'.join(url.split('/')[:3])
                        href = base_url + href
                    
                    logger.info(f"✓ {il_adi} Excel bulundu: {text}")
                    facilities.extend(self._download_and_parse_excel(href, f'{il_adi} Özel Hekim'))
            
        except Exception as e:
            logger.warning(f"İl doküman sayfası hatası {url}: {e}")
        
        return facilities
    
    def fetch_all_new_sources(self) -> List[Dict]:
        """Tüm yeni veri kaynaklarını çek"""
        all_data = []
        
        logger.info("🚀 Sağlık Bakanlığı yeni veri kaynakları taranıyor...")
        
        # 1. KHGM Kamu Hastaneleri
        khgm_data = self.fetch_khgm_kamu_hastaneleri()
        all_data.extend(khgm_data)
        logger.info(f"✅ KHGM: {len(khgm_data)} kayıt")
        
        # 2. Sağlık Turizmi Tesisleri
        turizm_data = self.fetch_saglik_turizmi_tesisleri()
        all_data.extend(turizm_data)
        logger.info(f"✅ Sağlık Turizmi: {len(turizm_data)} kayıt")
        
        # 3. İl Sağlık Müdürlükleri
        il_data = self.fetch_il_saglik_mudurlukteri()
        all_data.extend(il_data)
        logger.info(f"✅ İl Sağlık Müd.: {len(il_data)} kayıt")
        
        logger.info(f"🎯 Toplam yeni veri: {len(all_data)} kayıt")
        return all_data
    
    def save_data(self, data: List[Dict]):
        """Verileri kaydet"""
        json_file = os.path.join(self.data_dir, 'saglik_bakanligi_yeni_kaynaklar.json')
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Veriler kaydedildi: {json_file}")

def main():
    """Ana fonksiyon"""
    logger.info("Sağlık Bakanlığı yeni veri kaynakları keşfi başlıyor...")
    
    fetcher = SaglikBakanligiYeniKaynaklar()
    
    try:
        all_data = fetcher.fetch_all_new_sources()
        
        if all_data:
            fetcher.save_data(all_data)
            logger.info("✅ Sağlık Bakanlığı yeni kaynaklar işlemi tamamlandı!")
        else:
            logger.warning("❌ Hiç yeni veri bulunamadı!")
            
    except Exception as e:
        logger.error(f"❌ İşlem başarısız: {e}")

if __name__ == "__main__":
    main()
