#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Google Maps/Places API Veri Çıkarıcısı
===================================================

Tier 3 - Keşif ve Çapraz Referans Kaynak
Hedef: Google Maps Places API ile sağlık kuruluşları

Çıkarılan Veriler:
- Hastaneler
- Poliklinikler  
- Eczaneler
- Laboratuvarlar
- Özel muayenehaneler
- Koordinat bilgileri
"""

import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import os
from urllib.parse import urlencode

class GooglePlacesScraper:
    """Google Places API ile sağlık kuruluşlarını çıkarır"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            raise ValueError("Google Places API key gerekli. GOOGLE_PLACES_API_KEY environment variable set edin.")
        
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
        # Rate limiting - Google Places API limits
        self.request_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
        
        # Data storage
        self.data_dir = Path(__file__).parent.parent / "data" / "raw"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Turkish major cities with coordinates for search
        self.search_locations = [
            {"name": "İstanbul", "lat": 41.0082, "lng": 28.9784, "radius": 50000},
            {"name": "Ankara", "lat": 39.9334, "lng": 32.8597, "radius": 30000},
            {"name": "İzmir", "lat": 38.4237, "lng": 27.1428, "radius": 30000},
            {"name": "Bursa", "lat": 40.1826, "lng": 29.0665, "radius": 25000},
            {"name": "Antalya", "lat": 36.8969, "lng": 30.7133, "radius": 25000},
            {"name": "Gaziantep", "lat": 37.0662, "lng": 37.3833, "radius": 20000},
            {"name": "Konya", "lat": 37.8746, "lng": 32.4932, "radius": 20000},
            {"name": "Adana", "lat": 37.0000, "lng": 35.3213, "radius": 20000},
            {"name": "Kayseri", "lat": 38.7312, "lng": 35.4787, "radius": 20000},
            {"name": "Mersin", "lat": 36.8000, "lng": 34.6333, "radius": 20000},
            {"name": "Trabzon", "lat": 41.0015, "lng": 39.7178, "radius": 15000},
            {"name": "Samsun", "lat": 41.2867, "lng": 36.3300, "radius": 15000},
        ]
        
        # Search types for health facilities
        self.search_types = [
            {
                "keyword": "hastane hospital",
                "type": "hospital",
                "category": "Hastane"
            },
            {
                "keyword": "poliklinik tıp merkezi medical center",
                "type": "doctor",
                "category": "Poliklinik"
            },
            {
                "keyword": "eczane pharmacy",
                "type": "pharmacy",
                "category": "Eczane"
            },
            {
                "keyword": "laboratuvar laboratory lab",
                "type": "doctor",
                "category": "Laboratuvar"
            },
            {
                "keyword": "muayenehane clinic",
                "type": "doctor",
                "category": "Muayenehane"
            },
            {
                "keyword": "diş hekimi dentist",
                "type": "dentist",
                "category": "Diş Hekimi"
            },
            {
                "keyword": "fizik tedavi rehabilitation",
                "type": "physiotherapist",
                "category": "Fizik Tedavi"
            }
        ]
        
        self.results = []
        self.seen_place_ids = set()

    def _rate_limit(self):
        """Rate limiting implementation"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()

    def _make_request(self, url: str, params: Dict) -> Optional[Dict]:
        """Rate-limited API request with error handling"""
        self._rate_limit()
        
        params['key'] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"API request failed for {url}: {e}")
            return None

    def nearby_search(self, location: Dict, search_config: Dict) -> List[Dict]:
        """Nearby search API'yi kullanarak arama yapar"""
        self.logger.info(f"Arama yapılıyor: {location['name']} - {search_config['category']}")
        
        url = f"{self.base_url}/nearbysearch/json"
        
        params = {
            'location': f"{location['lat']},{location['lng']}",
            'radius': location['radius'],
            'keyword': search_config['keyword'],
            'type': search_config['type'],
            'language': 'tr'
        }
        
        all_results = []
        next_page_token = None
        
        while True:
            if next_page_token:
                params['pagetoken'] = next_page_token
            
            response_data = self._make_request(url, params)
            
            if not response_data:
                break
            
            if response_data.get('status') != 'OK' and response_data.get('status') != 'ZERO_RESULTS':
                self.logger.warning(f"API response status: {response_data.get('status')}")
                break
            
            results = response_data.get('results', [])
            
            for place in results:
                if place.get('place_id') not in self.seen_place_ids:
                    self.seen_place_ids.add(place['place_id'])
                    processed_place = self._process_place_data(place, location, search_config)
                    if processed_place:
                        all_results.append(processed_place)
            
            next_page_token = response_data.get('next_page_token')
            if not next_page_token:
                break
            
            # Wait for next page token to become valid
            time.sleep(2)
        
        self.logger.info(f"Bulunan yer sayısı: {len(all_results)}")
        return all_results

    def text_search(self, location: Dict, search_config: Dict) -> List[Dict]:
        """Text search API'yi kullanarak arama yapar"""
        url = f"{self.base_url}/textsearch/json"
        
        query = f"{search_config['keyword']} in {location['name']} Turkey"
        
        params = {
            'query': query,
            'location': f"{location['lat']},{location['lng']}",
            'radius': location['radius'],
            'language': 'tr'
        }
        
        all_results = []
        next_page_token = None
        
        while True:
            if next_page_token:
                params['pagetoken'] = next_page_token
            
            response_data = self._make_request(url, params)
            
            if not response_data:
                break
            
            if response_data.get('status') != 'OK' and response_data.get('status') != 'ZERO_RESULTS':
                break
            
            results = response_data.get('results', [])
            
            for place in results:
                if place.get('place_id') not in self.seen_place_ids:
                    self.seen_place_ids.add(place['place_id'])
                    processed_place = self._process_place_data(place, location, search_config)
                    if processed_place:
                        all_results.append(processed_place)
            
            next_page_token = response_data.get('next_page_token')
            if not next_page_token:
                break
            
            time.sleep(2)
        
        return all_results

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Place Details API ile detaylı bilgi alır"""
        url = f"{self.base_url}/details/json"
        
        params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,international_phone_number,website,rating,user_ratings_total,types,opening_hours,photos',
            'language': 'tr'
        }
        
        response_data = self._make_request(url, params)
        
        if response_data and response_data.get('status') == 'OK':
            return response_data.get('result')
        
        return None

    def _process_place_data(self, place: Dict, location: Dict, search_config: Dict) -> Optional[Dict]:
        """Google Places API verisini standardize eder"""
        try:
            # Basic information
            place_data = {
                'isim': place.get('name', ''),
                'google_place_id': place.get('place_id'),
                'tip': search_config['category'],
                'rating': place.get('rating'),
                'rating_count': place.get('user_ratings_total'),
                'arama_sehri': location['name'],
                'kaynak': 'Google Places API',
                'kaynak_url': f"https://maps.google.com/maps?cid={place.get('place_id')}",
                'tarih': datetime.now(timezone.utc).isoformat()
            }
            
            # Address
            if place.get('vicinity'):
                place_data['adres'] = place['vicinity']
            elif place.get('formatted_address'):
                place_data['adres'] = place['formatted_address']
            
            # Coordinates
            if place.get('geometry', {}).get('location'):
                location_data = place['geometry']['location']
                place_data['konum'] = {
                    'type': 'Point',
                    'coordinates': [location_data['lng'], location_data['lat']]
                }
            
            # Business status
            if place.get('business_status'):
                place_data['durum'] = place['business_status']
            
            # Types
            if place.get('types'):
                place_data['google_types'] = place['types']
            
            # Get detailed information
            if place.get('place_id'):
                details = self.get_place_details(place['place_id'])
                if details:
                    # Phone number
                    if details.get('international_phone_number'):
                        place_data['telefon'] = details['international_phone_number']
                    
                    # Website
                    if details.get('website'):
                        place_data['website'] = details['website']
                    
                    # Opening hours
                    if details.get('opening_hours', {}).get('weekday_text'):
                        place_data['calisma_saatleri'] = details['opening_hours']['weekday_text']
                    
                    # Photos
                    if details.get('photos'):
                        # Get photo references
                        place_data['foto_referanslari'] = [photo.get('photo_reference') 
                                                        for photo in details['photos'][:3]]
            
            return place_data
            
        except Exception as e:
            self.logger.warning(f"Place data işlenirken hata: {e}")
            return None

    def filter_results(self):
        """Sonuçları filtreler ve temizler"""
        filtered_results = []
        
        for place in self.results:
            # Basic validation
            if not place.get('isim') or len(place['isim']) < 3:
                continue
            
            # Filter out non-health related places based on name
            name_lower = place['isim'].lower()
            health_keywords = [
                'hastane', 'hospital', 'poliklinik', 'clinic', 'eczane', 'pharmacy',
                'laboratuvar', 'laboratory', 'muayenehane', 'tıp', 'medical',
                'sağlık', 'health', 'doktor', 'doctor', 'hekim', 'diş', 'dental'
            ]
            
            if not any(keyword in name_lower for keyword in health_keywords):
                # Check Google types as well
                google_types = place.get('google_types', [])
                health_types = ['hospital', 'pharmacy', 'doctor', 'dentist', 'physiotherapist', 'health']
                
                if not any(any(ht in gt for ht in health_types) for gt in google_types):
                    continue
            
            # Add to filtered results
            filtered_results.append(place)
        
        removed_count = len(self.results) - len(filtered_results)
        self.results = filtered_results
        
        if removed_count > 0:
            self.logger.info(f"{removed_count} alakasız kayıt filtrelendi")

    def save_data(self):
        """Çekilen veriyi JSON dosyasına kaydeder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"google_places_saglik_{timestamp}.json"
        filepath = self.data_dir / filename
        
        output_data = {
            'kaynak': 'Google Places API',
            'tier': 3,
            'cekme_tarihi': datetime.now(timezone.utc).isoformat(),
            'toplam_kayit': len(self.results),
            'veriler': self.results,
            'meta': {
                'api_version': 'v1',
                'search_locations': [loc['name'] for loc in self.search_locations],
                'search_categories': [st['category'] for st in self.search_types],
                'scraper_version': '2.0',
                'veri_tipi': 'google_places_saglik'
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Veri kaydedildi: {filepath}")
        return filepath

    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.logger.info("Google Places API veri çekme işlemi başlatılıyor...")
        
        if not self.api_key:
            self.logger.error("Google Places API key bulunamadı")
            return False
        
        try:
            total_searches = len(self.search_locations) * len(self.search_types)
            current_search = 0
            
            for location in self.search_locations:
                for search_config in self.search_types:
                    current_search += 1
                    self.logger.info(f"İlerleme: {current_search}/{total_searches}")
                    
                    # Try nearby search first
                    nearby_results = self.nearby_search(location, search_config)
                    self.results.extend(nearby_results)
                    
                    # Also try text search for better coverage
                    text_results = self.text_search(location, search_config)
                    self.results.extend(text_results)
                    
                    # Rate limiting between search types
                    time.sleep(1)
            
            # Filter and clean results
            self.filter_results()
            
            # Save data
            self.save_data()
            
            self.logger.info(f"Google Places API veri çekme işlemi tamamlandı. Toplam: {len(self.results)} yer")
            return True
            
        except Exception as e:
            self.logger.error(f"Google Places API veri çekme sırasında hata: {e}")
            return False

def main():
    """Ana fonksiyon"""
    # API key'i environment variable'dan al
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    
    if not api_key:
        print("GOOGLE_PLACES_API_KEY environment variable ayarlanmalı")
        print("Kullanım: export GOOGLE_PLACES_API_KEY='your_api_key_here'")
        return 1
    
    scraper = GooglePlacesScraper(api_key)
    success = scraper.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
