#!/usr/bin/env python3
"""
SGK Sağlık Hizmet Sunucuları Veri Çekme Scripti
================================================

Bu script SGK'nın SHS (Sağlık Hizmet Sunucuları) sorgulama sayfasından
anlaşmalı sağlık kurumlarını çeker.

Kaynak: https://sgk.gov.tr/Uygulamalar/SHS_SORGU
Kapsam: Hastane, tıp merkezi, dal merkezi, diyaliz merkezi, eczane vb.
"""

import requests
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import time

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SGKSHSDataFetcher:
    """SGK Sağlık Hizmet Sunucuları verilerini çeken sınıf."""
    
    def __init__(self):
        self.base_url = "https://sgk.gov.tr"
        self.shs_url = "https://sgk.gov.tr/Uygulamalar/SHS_SORGU"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
        })
        
        # İl kodları (81 il)
        self.il_kodlari = {
            'Adana': '01', 'Adıyaman': '02', 'Afyonkarahisar': '03', 'Ağrı': '04',
            'Amasya': '05', 'Ankara': '06', 'Antalya': '07', 'Artvin': '08',
            'Aydın': '09', 'Balıkesir': '10', 'Bilecik': '11', 'Bingöl': '12',
            'Bitlis': '13', 'Bolu': '14', 'Burdur': '15', 'Bursa': '16',
            'Çanakkale': '17', 'Çankırı': '18', 'Çorum': '19', 'Denizli': '20',
            'Diyarbakır': '21', 'Edirne': '22', 'Elazığ': '23', 'Erzincan': '24',
            'Erzurum': '25', 'Eskişehir': '26', 'Gaziantep': '27', 'Giresun': '28',
            'Gümüşhane': '29', 'Hakkâri': '30', 'Hatay': '31', 'Isparta': '32',
            'Mersin': '33', 'İstanbul': '34', 'İzmir': '35', 'Kars': '36',
            'Kastamonu': '37', 'Kayseri': '38', 'Kırklareli': '39', 'Kırşehir': '40',
            'Kocaeli': '41', 'Konya': '42', 'Kütahya': '43', 'Malatya': '44',
            'Manisa': '45', 'Kahramanmaraş': '46', 'Mardin': '47', 'Muğla': '48',
            'Muş': '49', 'Nevşehir': '50', 'Niğde': '51', 'Ordu': '52',
            'Rize': '53', 'Sakarya': '54', 'Samsun': '55', 'Siirt': '56',
            'Sinop': '57', 'Sivas': '58', 'Tekirdağ': '59', 'Tokat': '60',
            'Trabzon': '61', 'Tunceli': '62', 'Şanlıurfa': '63', 'Uşak': '64',
            'Van': '65', 'Yozgat': '66', 'Zonguldak': '67', 'Aksaray': '68',
            'Bayburt': '69', 'Karaman': '70', 'Kırıkkale': '71', 'Batman': '72',
            'Şırnak': '73', 'Bartın': '74', 'Ardahan': '75', 'Iğdır': '76',
            'Yalova': '77', 'Karabük': '78', 'Kilis': '79', 'Osmaniye': '80',
            'Düzce': '81'
        }
        
        # Kurum türleri
        self.kurum_turleri = {
            'HASTANE': 'Hastane',
            'TIP_MERKEZI': 'Tıp Merkezi', 
            'DAL_MERKEZI': 'Dal Merkezi',
            'DIYALIZ': 'Diyaliz Merkezi',
            'ECZANE': 'Eczane',
            'LABORATUVAR': 'Laboratuvar',
            'GORUNTULEME': 'Görüntüleme Merkezi'
        }
        
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_form_data(self) -> Optional[Dict]:
        """Form verilerini ve CSRF token'ı al"""
        try:
            response = self.session.get(self.shs_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # CSRF token ve diğer hidden alanları bul
            form_data = {}
            hidden_inputs = soup.find_all('input', type='hidden')
            for inp in hidden_inputs:
                name = inp.get('name')
                value = inp.get('value', '')
                if name:
                    form_data[name] = value
            
            return form_data
            
        except Exception as e:
            logger.error(f"Form verileri alınamadı: {e}")
            return None
    
    def search_shs_by_city(self, il_kodu: str, il_adi: str) -> List[Dict]:
        """Belirli bir il için SHS listesini çek"""
        facilities = []
        
        try:
            # Form verilerini al
            form_data = self.get_form_data()
            if not form_data:
                return facilities
            
            # Arama parametrelerini ekle
            search_data = form_data.copy()
            search_data.update({
                'il': il_kodu,
                'kurum_tur': '',  # Tüm türler
                'kurum_adi': '',  # Tüm kurumlar
                'btnSearch': 'Ara'
            })
            
            logger.info(f"SGK SHS araması: {il_adi} ({il_kodu})")
            
            response = self.session.post(
                self.shs_url,
                data=search_data,
                timeout=30,
                headers={'Referer': self.shs_url}
            )
            response.raise_for_status()
            
            # Sonuçları parse et
            soup = BeautifulSoup(response.text, 'html.parser')
            results_table = soup.find('table')
            
            if results_table:
                rows = results_table.find_all('tr')[1:]  # Başlık satırını atla
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        facility = {
                            'kurum_adi': cells[0].get_text(strip=True),
                            'kurum_tipi': cells[1].get_text(strip=True),
                            'adres': cells[2].get_text(strip=True),
                            'telefon': self._clean_phone(cells[3].get_text(strip=True)),
                            'il_adi': il_adi,
                            'il_kodu': int(il_kodu),
                            'veri_kaynagi': 'SGK Sağlık Hizmet Sunucuları',
                            'son_guncelleme': datetime.now().strftime('%Y-%m-%d')
                        }
                        
                        # İlçe bilgisini adresten çıkarmaya çalış
                        if '/' in facility['adres']:
                            adres_parts = facility['adres'].split('/')
                            if len(adres_parts) >= 2:
                                facility['ilce_adi'] = adres_parts[0].strip()
                        
                        facilities.append(facility)
                
                logger.info(f"✓ {il_adi}: {len(facilities)} kurum bulundu")
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            logger.error(f"SGK SHS sorgusu hatası {il_adi}: {e}")
        
        return facilities
    
    def _clean_phone(self, phone: str) -> str:
        """Telefon numarasını temizle"""
        if not phone:
            return ''
        
        # Sadece rakamları al
        phone = ''.join(filter(str.isdigit, phone))
        
        # Türkiye formatına çevir
        if phone.startswith('90'):
            phone = phone[2:]
        elif phone.startswith('0'):
            phone = phone[1:]
        
        if len(phone) == 10:
            return f"+90{phone}"
        
        return phone
    
    def fetch_all_data(self) -> List[Dict]:
        """Tüm illerden SHS verilerini çek"""
        all_facilities = []
        
        # Öncelikli iller (büyük şehirler)
        priority_cities = [
            'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya',
            'Adana', 'Konya', 'Gaziantep', 'Kayseri', 'Eskişehir'
        ]
        
        # Önce büyük şehirleri çek
        for il_adi in priority_cities:
            if il_adi in self.il_kodlari:
                il_kodu = self.il_kodlari[il_adi]
                facilities = self.search_shs_by_city(il_kodu, il_adi)
                all_facilities.extend(facilities)
        
        # Sonra diğer illeri çek
        remaining_cities = [il for il in self.il_kodlari.keys() if il not in priority_cities]
        
        for il_adi in remaining_cities[:10]:  # İlk 10 il daha (rate limiting için)
            il_kodu = self.il_kodlari[il_adi]
            facilities = self.search_shs_by_city(il_kodu, il_adi)
            all_facilities.extend(facilities)
        
        logger.info(f"Toplam SGK SHS verisi: {len(all_facilities)} kurum")
        return all_facilities
    
    def save_data(self, facilities: List[Dict]):
        """Verileri kaydet"""
        # JSON kaydet
        json_file = os.path.join(self.data_dir, 'sgk_shs_data.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(facilities, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ SGK SHS verileri kaydedildi: {json_file}")
        logger.info(f"📊 Toplam kurum sayısı: {len(facilities)}")

def main():
    """Ana fonksiyon"""
    logger.info("SGK SHS veri çekme işlemi başlıyor...")
    
    fetcher = SGKSHSDataFetcher()
    
    try:
        facilities = fetcher.fetch_all_data()
        
        if facilities:
            fetcher.save_data(facilities)
            logger.info("✅ SGK SHS veri çekme işlemi tamamlandı!")
        else:
            logger.warning("❌ Hiç veri çekilemedi!")
            
    except Exception as e:
        logger.error(f"❌ İşlem başarısız: {e}")

if __name__ == "__main__":
    main()
