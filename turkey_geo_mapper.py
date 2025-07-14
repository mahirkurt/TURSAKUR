#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Türkiye Resmi İl ve İlçe Veritabanı
T.C. İçişleri Bakanlığı resmi verilerine dayalı coğrafi eşleme sistemi
"""

import json
import unicodedata
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class TurkeyGeoMapper:
    """Türkiye coğrafi veri eşleyici sınıfı"""
    
    def __init__(self):
        self.provinces = self._load_official_provinces()
        self.districts = self._load_official_districts()
        self.province_aliases = self._create_province_aliases()
        self.district_aliases = self._create_district_aliases()
    
    def _load_official_provinces(self) -> Dict[int, Dict]:
        """T.C. resmi 81 il verisi"""
        return {
            1: {"name": "Adana", "region": "Akdeniz", "plate": "01"},
            2: {"name": "Adıyaman", "region": "Güneydoğu Anadolu", "plate": "02"},
            3: {"name": "Afyonkarahisar", "region": "Ege", "plate": "03"},
            4: {"name": "Ağrı", "region": "Doğu Anadolu", "plate": "04"},
            5: {"name": "Amasya", "region": "Karadeniz", "plate": "05"},
            6: {"name": "Ankara", "region": "İç Anadolu", "plate": "06"},
            7: {"name": "Antalya", "region": "Akdeniz", "plate": "07"},
            8: {"name": "Artvin", "region": "Karadeniz", "plate": "08"},
            9: {"name": "Aydın", "region": "Ege", "plate": "09"},
            10: {"name": "Balıkesir", "region": "Marmara", "plate": "10"},
            11: {"name": "Bilecik", "region": "Marmara", "plate": "11"},
            12: {"name": "Bingöl", "region": "Doğu Anadolu", "plate": "12"},
            13: {"name": "Bitlis", "region": "Doğu Anadolu", "plate": "13"},
            14: {"name": "Bolu", "region": "Karadeniz", "plate": "14"},
            15: {"name": "Burdur", "region": "Akdeniz", "plate": "15"},
            16: {"name": "Bursa", "region": "Marmara", "plate": "16"},
            17: {"name": "Çanakkale", "region": "Marmara", "plate": "17"},
            18: {"name": "Çankırı", "region": "İç Anadolu", "plate": "18"},
            19: {"name": "Çorum", "region": "Karadeniz", "plate": "19"},
            20: {"name": "Denizli", "region": "Ege", "plate": "20"},
            21: {"name": "Diyarbakır", "region": "Güneydoğu Anadolu", "plate": "21"},
            22: {"name": "Edirne", "region": "Marmara", "plate": "22"},
            23: {"name": "Elazığ", "region": "Doğu Anadolu", "plate": "23"},
            24: {"name": "Erzincan", "region": "Doğu Anadolu", "plate": "24"},
            25: {"name": "Erzurum", "region": "Doğu Anadolu", "plate": "25"},
            26: {"name": "Eskişehir", "region": "İç Anadolu", "plate": "26"},
            27: {"name": "Gaziantep", "region": "Güneydoğu Anadolu", "plate": "27"},
            28: {"name": "Giresun", "region": "Karadeniz", "plate": "28"},
            29: {"name": "Gümüşhane", "region": "Karadeniz", "plate": "29"},
            30: {"name": "Hakkâri", "region": "Doğu Anadolu", "plate": "30"},
            31: {"name": "Hatay", "region": "Akdeniz", "plate": "31"},
            32: {"name": "Isparta", "region": "Akdeniz", "plate": "32"},
            33: {"name": "Mersin", "region": "Akdeniz", "plate": "33"},
            34: {"name": "İstanbul", "region": "Marmara", "plate": "34"},
            35: {"name": "İzmir", "region": "Ege", "plate": "35"},
            36: {"name": "Kars", "region": "Doğu Anadolu", "plate": "36"},
            37: {"name": "Kastamonu", "region": "Karadeniz", "plate": "37"},
            38: {"name": "Kayseri", "region": "İç Anadolu", "plate": "38"},
            39: {"name": "Kırklareli", "region": "Marmara", "plate": "39"},
            40: {"name": "Kırşehir", "region": "İç Anadolu", "plate": "40"},
            41: {"name": "Kocaeli", "region": "Marmara", "plate": "41"},
            42: {"name": "Konya", "region": "İç Anadolu", "plate": "42"},
            43: {"name": "Kütahya", "region": "Ege", "plate": "43"},
            44: {"name": "Malatya", "region": "Doğu Anadolu", "plate": "44"},
            45: {"name": "Manisa", "region": "Ege", "plate": "45"},
            46: {"name": "Kahramanmaraş", "region": "Akdeniz", "plate": "46"},
            47: {"name": "Mardin", "region": "Güneydoğu Anadolu", "plate": "47"},
            48: {"name": "Muğla", "region": "Ege", "plate": "48"},
            49: {"name": "Muş", "region": "Doğu Anadolu", "plate": "49"},
            50: {"name": "Nevşehir", "region": "İç Anadolu", "plate": "50"},
            51: {"name": "Niğde", "region": "İç Anadolu", "plate": "51"},
            52: {"name": "Ordu", "region": "Karadeniz", "plate": "52"},
            53: {"name": "Rize", "region": "Karadeniz", "plate": "53"},
            54: {"name": "Sakarya", "region": "Marmara", "plate": "54"},
            55: {"name": "Samsun", "region": "Karadeniz", "plate": "55"},
            56: {"name": "Siirt", "region": "Güneydoğu Anadolu", "plate": "56"},
            57: {"name": "Sinop", "region": "Karadeniz", "plate": "57"},
            58: {"name": "Sivas", "region": "İç Anadolu", "plate": "58"},
            59: {"name": "Tekirdağ", "region": "Marmara", "plate": "59"},
            60: {"name": "Tokat", "region": "Karadeniz", "plate": "60"},
            61: {"name": "Trabzon", "region": "Karadeniz", "plate": "61"},
            62: {"name": "Tunceli", "region": "Doğu Anadolu", "plate": "62"},
            63: {"name": "Şanlıurfa", "region": "Güneydoğu Anadolu", "plate": "63"},
            64: {"name": "Uşak", "region": "Ege", "plate": "64"},
            65: {"name": "Van", "region": "Doğu Anadolu", "plate": "65"},
            66: {"name": "Yozgat", "region": "İç Anadolu", "plate": "66"},
            67: {"name": "Zonguldak", "region": "Karadeniz", "plate": "67"},
            68: {"name": "Aksaray", "region": "İç Anadolu", "plate": "68"},
            69: {"name": "Bayburt", "region": "Karadeniz", "plate": "69"},
            70: {"name": "Karaman", "region": "İç Anadolu", "plate": "70"},
            71: {"name": "Kırıkkale", "region": "İç Anadolu", "plate": "71"},
            72: {"name": "Batman", "region": "Güneydoğu Anadolu", "plate": "72"},
            73: {"name": "Şırnak", "region": "Güneydoğu Anadolu", "plate": "73"},
            74: {"name": "Bartın", "region": "Karadeniz", "plate": "74"},
            75: {"name": "Ardahan", "region": "Doğu Anadolu", "plate": "75"},
            76: {"name": "Iğdır", "region": "Doğu Anadolu", "plate": "76"},
            77: {"name": "Yalova", "region": "Marmara", "plate": "77"},
            78: {"name": "Karabük", "region": "Karadeniz", "plate": "78"},
            79: {"name": "Kilis", "region": "Güneydoğu Anadolu", "plate": "79"},
            80: {"name": "Osmaniye", "region": "Akdeniz", "plate": "80"},
            81: {"name": "Düzce", "region": "Karadeniz", "plate": "81"}
        }
    
    def _load_official_districts(self) -> Dict[int, List[str]]:
        """İl koduna göre resmi ilçe listesi"""
        return {
            # Adana (01)
            1: ["Seyhan", "Yüreğir", "Çukurova", "Sarıçam", "Aladağ", "Ceyhan", "Feke", 
                "İmamoğlu", "Karaisalı", "Karataş", "Kozan", "Pozantı", "Saimbeyli", 
                "Tufanbeyli", "Yumurtalık"],
            
            # Adıyaman (02)
            2: ["Merkez", "Besni", "Çelikhan", "Gerger", "Gölbaşı", "Kâhta", "Samsat", 
                "Sincik", "Tut"],
            
            # Afyonkarahisar (03)
            3: ["Merkez", "Bolvadin", "Çay", "Dazkırı", "Dinar", "Emirdağ", "Hocalar", 
                "İhsaniye", "İscehisar", "Kızılören", "Sandıklı", "Sinanpaşa", "Sultandağı", 
                "Şuhut", "Başmakçı", "Bayat", "Çobanlar", "Evciler"],
            
            # Ağrı (04)
            4: ["Merkez", "Diyadin", "Doğubayazıt", "Eleşkirt", "Hamur", "Patnos", 
                "Taşlıçay", "Tutak"],
            
            # Amasya (05)
            5: ["Merkez", "Göynücek", "Gümüşhacıköy", "Hamamözü", "Merzifon", "Suluova", 
                "Taşova"],
            
            # Ankara (06)
            6: ["Altındağ", "Ayaş", "Bala", "Beypazarı", "Çamlıdere", "Çankaya", "Çubuk", 
                "Elmadağ", "Etimesgut", "Evren", "Gölbaşı", "Güdül", "Haymana", "Kalecik", 
                "Kızılcahamam", "Mamak", "Nallıhan", "Polatlı", "Pursaklar", "Sincan", 
                "Şereflikoçhisar", "Yenimahalle", "Keçiören", "Kahramankazan", "Akyurt"],
            
            # Antalya (07)
            7: ["Akdeniz", "Döşemealtı", "Kepez", "Konyaaltı", "Muratpaşa", "Akseki", 
                "Alanya", "Demre", "Elmalı", "Finike", "Gazipaşa", "Gündoğmuş", "İbradı", 
                "Kaş", "Kemer", "Korkuteli", "Kumluca", "Manavgat", "Serik"],
            
            # Artvin (08)
            8: ["Merkez", "Ardanuç", "Arhavi", "Borçka", "Hopa", "Murgul", "Şavşat", 
                "Yusufeli"],
            
            # Aydın (09)
            9: ["Efeler", "Bozdoğan", "Buharkent", "Çine", "Didim", "Germencik", "İncirliova", 
                "Karacasu", "Karpuzlu", "Koçarlı", "Köşk", "Kuşadası", "Kuyucak", "Nazilli", 
                "Söke", "Sultanhisar", "Yenipazar"],
            
            # Balıkesir (10)
            10: ["Altıeylül", "Karesi", "Ayvalık", "Balya", "Bandırma", "Bigadiç", "Burhaniye", 
                 "Dursunbey", "Edremit", "Erdek", "Gömeç", "Gönen", "Havran", "İvrindi", 
                 "Kepsut", "Manyas", "Marmara", "Savaştepe", "Sındırgı", "Susurluk"],
            
            # Bilecik (11)
            11: ["Merkez", "Bozüyük", "Gölpazarı", "İnhisar", "Osmaneli", "Pazaryeri", 
                 "Söğüt", "Yenipazar"],
            
            # Bingöl (12)
            12: ["Merkez", "Adaklı", "Genç", "Karlıova", "Kiğı", "Solhan", "Yayladere", 
                 "Yedisu"],
            
            # Bitlis (13)
            13: ["Merkez", "Adilcevaz", "Ahlat", "Güroymak", "Hizan", "Mutki", "Tatvan"],
            
            # Bolu (14)
            14: ["Merkez", "Dörtdivan", "Gerede", "Göynük", "Kıbrıscık", "Mengen", 
                 "Mudurnu", "Seben", "Yeniçağa"],
            
            # Burdur (15)
            15: ["Merkez", "Ağlasun", "Altınyayla", "Bucak", "Çavdır", "Çeltikçi", 
                 "Gölhisar", "Karamanlı", "Kemer", "Tefenni", "Yeşilova"],
            
            # Bursa (16)
            16: ["Osmangazi", "Yıldırım", "Nilüfer", "Büyükorhan", "Gemlik", "Gürsu", 
                 "Harmancık", "İnegöl", "İznik", "Karacabey", "Keles", "Kestel", "Mudanya", 
                 "Mustafakemalpaşa", "Orhaneli", "Orhangazi", "Yenişehir"],
            
            # Çanakkale (17)
            17: ["Merkez", "Ayvacık", "Bayramiç", "Biga", "Bozcaada", "Çan", "Eceabat", 
                 "Ezine", "Gelibolu", "Gökçeada", "Lapseki", "Yenice"],
            
            # Çankırı (18)
            18: ["Merkez", "Atkaracalar", "Bayramören", "Çerkeş", "Eldivan", "Ilgaz", 
                 "Kızılırmak", "Korgun", "Kurşunlu", "Orta", "Şabanözü", "Yapraklı"],
            
            # Çorum (19)
            19: ["Merkez", "Alaca", "Bayat", "Boğazkale", "Dodurga", "İskilip", "Kargı", 
                 "Laçin", "Mecitözü", "Oğuzlar", "Ortaköy", "Osmancık", "Sungurlu", "Uğurludağ"],
            
            # Denizli (20)
            20: ["Pamukkale", "Merkezefendi", "Acıpayam", "Babadağ", "Baklan", "Bekilli", 
                 "Beyağaç", "Bozkurt", "Buldan", "Çal", "Çameli", "Çardak", "Çivril", 
                 "Güney", "Honaz", "Kale", "Sarayköy", "Serinhisar", "Tavas"],
            
            # Diyarbakır (21)
            21: ["Bağlar", "Kayapınar", "Sur", "Yenişehir", "Bismil", "Çermik", "Çınar", 
                 "Çüngüş", "Dicle", "Eğil", "Ergani", "Hani", "Hazro", "Kulp", "Kocaköy", 
                 "Lice", "Silvan"],
            
            # Edirne (22)
            22: ["Merkez", "Enez", "Havsa", "İpsala", "Keşan", "Lalapaşa", "Meriç", 
                 "Süloğlu", "Uzunköprü"],
            
            # Elazığ (23)
            23: ["Merkez", "Ağın", "Alacakaya", "Arıcak", "Baskil", "Karakoçan", "Keban", 
                 "Kovancılar", "Maden", "Palu", "Sivrice"],
            
            # Erzincan (24)
            24: ["Merkez", "Çayırlı", "İliç", "Kemah", "Kemaliye", "Otlukbeli", "Refahiye", 
                 "Tercan", "Üzümlü"],
            
            # Erzurum (25)
            25: ["Aziziye", "Palandöken", "Yakutiye", "Aşkale", "Çat", "Hınıs", "Horasan", 
                 "İspir", "Karaçoban", "Karayazı", "Köprüköy", "Narman", "Oltu", "Olur", 
                 "Pasinler", "Şenkaya", "Tekman", "Tortum", "Uzundere"],
            
            # Eskişehir (26)
            26: ["Odunpazarı", "Tepebaşı", "Alpu", "Beylikova", "Çifteler", "Günyüzü", 
                 "Han", "İnönü", "Mahmudiye", "Mihalıççık", "Sarıcakaya", "Seyitgazi", 
                 "Sivrihisar"],
            
            # Gaziantep (27)
            27: ["Şahinbey", "Şehitkamil", "Oğuzeli", "Araban", "İslahiye", "Karkamış", 
                 "Nizip", "Nurdağı", "Yavuzeli"],
            
            # Giresun (28)
            28: ["Merkez", "Alucra", "Bulancak", "Çamoluk", "Çanakçı", "Dereli", "Doğankent", 
                 "Espiye", "Eynesil", "Görele", "Güce", "Keşap", "Piraziz", "Şebinkarahisar", 
                 "Tirebolu", "Yağlıdere"],
            
            # Gümüşhane (29)
            29: ["Merkez", "Kelkit", "Köse", "Kürtün", "Şiran", "Torul"],
            
            # Hakkâri (30)
            30: ["Merkez", "Çukurca", "Derecik", "Şemdinli", "Yüksekova"],
            
            # Hatay (31)
            31: ["Antakya", "Defne", "Arsuz", "Belen", "Dörtyol", "Erzin", "Hassa", 
                 "İskenderun", "Kırıkhan", "Kumlu", "Payas", "Reyhanlı", "Samandağ", 
                 "Yayladağı", "Altınözü"],
            
            # Isparta (32)
            32: ["Merkez", "Aksu", "Atabey", "Eğirdir", "Gelendost", "Gönen", "Keçiborlu", 
                 "Senirkent", "Sütçüler", "Şarkikaraağaç", "Uluborlu", "Yalvaç", "Yenişarbademli"],
            
            # Mersin (33)
            33: ["Akdeniz", "Mezitli", "Toroslar", "Yenişehir", "Anamur", "Aydıncık", 
                 "Bozyazı", "Çamlıyayla", "Erdemli", "Gülnar", "Mut", "Silifke", "Tarsus"],
            
            # İstanbul (34)
            34: ["Adalar", "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler", 
                 "Bakırköy", "Başakşehir", "Bayrampaşa", "Beşiktaş", "Beykoz", "Beylikdüzü", 
                 "Beyoğlu", "Büyükçekmece", "Çatalca", "Çekmeköy", "Esenler", "Esenyurt", 
                 "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Kadıköy", "Kâğıthane", 
                 "Kartal", "Küçükçekmece", "Maltepe", "Pendik", "Sancaktepe", "Sarıyer", 
                 "Silivri", "Sultangazi", "Sultanbeyli", "Şile", "Şişli", "Tuzla", "Ümraniye", 
                 "Üsküdar", "Zeytinburnu"],
            
            # İzmir (35)
            35: ["Aliağa", "Balçova", "Bayındır", "Bayraklı", "Bergama", "Beydağ", "Bornova", 
                 "Buca", "Çeşme", "Çiğli", "Dikili", "Foça", "Gaziemir", "Güzelbahçe", 
                 "Karabağlar", "Karaburun", "Karşıyaka", "Kemalpaşa", "Kınık", "Kiraz", 
                 "Konak", "Menderes", "Menemen", "Narlıdere", "Ödemiş", "Seferihisar", 
                 "Selçuk", "Tire", "Torbalı", "Urla"],
            
            # Kars (36)
            36: ["Merkez", "Akyaka", "Arpaçay", "Digor", "Kağızman", "Sarıkamış", "Selim", 
                 "Susuz"],
            
            # Kastamonu (37)
            37: ["Merkez", "Abana", "Ağlı", "Araç", "Azdavay", "Bozkurt", "Cide", "Çatalzeytin", 
                 "Daday", "Devrekani", "Doğanyurt", "Hanönü", "İhsangazi", "İnebolu", "Küre", 
                 "Pınarbaşı", "Seydiler", "Şenpazar", "Taşköprü", "Tosya"],
            
            # Kayseri (38)
            38: ["Kocasinan", "Melikgazi", "Talas", "Hacılar", "Akkışla", "Bünyan", "Develi", 
                 "Felahiye", "İncesu", "Özvatan", "Pınarbaşı", "Sarıoğlan", "Sarız", "Tomarza", 
                 "Yahyalı", "Yeşilhisar"],
            
            # Kırklareli (39)
            39: ["Merkez", "Babaeski", "Demirköy", "Kofçaz", "Lüleburgaz", "Pehlivanköy", 
                 "Pınarhisar", "Vize"],
            
            # Kırşehir (40)
            40: ["Merkez", "Akçakent", "Akpınar", "Boztepe", "Çiçekdağı", "Kaman", "Mucur"],
            
            # Kocaeli (41)
            41: ["İzmit", "Başiskele", "Çayırova", "Darıca", "Derince", "Dilovası", "Gebze", 
                 "Gölcük", "Kandıra", "Karamürsel", "Körfez", "Kartepe"],
            
            # Konya (42)
            42: ["Karatay", "Meram", "Selçuklu", "Ahırlı", "Akören", "Akşehir", "Altınekin", 
                 "Beyşehir", "Bozkır", "Cihanbeyli", "Çeltik", "Çumra", "Derbent", "Derebucak", 
                 "Doğanhisar", "Emirgazi", "Ereğli", "Güneysınır", "Hadim", "Halkapınar", 
                 "Hüyük", "Ilgın", "Kadınhanı", "Karapınar", "Kulu", "Sarayönü", "Seydişehir", 
                 "Taşkent", "Tuzlukçu", "Yalıhüyük", "Yunak"],
            
            # Kütahya (43)
            43: ["Merkez", "Altıntaş", "Aslanapa", "Çavdarhisar", "Domaniç", "Dumlupınar", 
                 "Emet", "Gediz", "Hisarcık", "Pazarlar", "Simav", "Şaphane", "Tavşanlı"],
            
            # Malatya (44)
            44: ["Battalgazi", "Yeşilyurt", "Akçadağ", "Arapgir", "Arguvan", "Darende", 
                 "Doğanşehir", "Doğanyol", "Hekimhan", "Kale", "Kuluncak", "Pütürge", "Yazıhan"],
            
            # Manisa (45)
            45: ["Şehzadeler", "Yunusemre", "Ahmetli", "Akhisar", "Alaşehir", "Demirci", 
                 "Gölmarmara", "Gördes", "Kırkağaç", "Köprübaşı", "Kula", "Salihli", "Sarıgöl", 
                 "Saruhanlı", "Selendi", "Soma", "Turgutlu"],
            
            # Kahramanmaraş (46)
            46: ["Dulkadiroğlu", "Onikişubat", "Afşin", "Andırın", "Çağlayancerit", "Ekinözü", 
                 "Elbistan", "Göksun", "Nurhak", "Pazarcık", "Türkoğlu"],
            
            # Mardin (47)
            47: ["Artuklu", "Dargeçit", "Derik", "Kızıltepe", "Mazıdağı", "Midyat", "Nusaybin", 
                 "Ömerli", "Savur", "Yeşilli"],
            
            # Muğla (48)
            48: ["Menteşe", "Bodrum", "Dalaman", "Datça", "Fethiye", "Kavaklıdere", "Köyceğiz", 
                 "Marmaris", "Milas", "Ortaca", "Seydikemer", "Ula", "Yatağan"],
            
            # Muş (49)
            49: ["Merkez", "Bulanık", "Hasköy", "Korkut", "Malazgirt", "Varto"],
            
            # Nevşehir (50)
            50: ["Merkez", "Acıgöl", "Avanos", "Derinkuyu", "Gülşehir", "Hacıbektaş", 
                 "Kozaklı", "Ürgüp"],
            
            # Niğde (51)
            51: ["Merkez", "Altunhisar", "Bor", "Çamardı", "Çiftlik", "Ulukışla"],
            
            # Ordu (52)
            52: ["Altınordu", "Akkuş", "Aybastı", "Çamaş", "Çatalpınar", "Çaybaşı", "Fatsa", 
                 "Gölköy", "Gülyalı", "Gürgentepe", "İkizce", "Kabadüz", "Kabataş", "Korgan", 
                 "Kumru", "Mesudiye", "Perşembe", "Ulubey", "Ünye"],
            
            # Rize (53)
            53: ["Merkez", "Ardeşen", "Çamlıhemşin", "Çayeli", "Derepazarı", "Fındıklı", 
                 "Güneysu", "Hemşin", "İkizdere", "İyidere", "Kalkandere", "Pazar"],
            
            # Sakarya (54)
            54: ["Adapazarı", "Serdivan", "Akyazı", "Arifiye", "Erenler", "Ferizli", "Geyve", 
                 "Hendek", "Karapürçek", "Karasu", "Kaynarca", "Kocaali", "Pamukova", "Sapanca", 
                 "Söğütlü", "Taraklı"],
            
            # Samsun (55)
            55: ["İlkadım", "Atakum", "Canik", "Tekkeköy", "Alaçam", "Asarcık", "Ayvacık", 
                 "Bafra", "Çarşamba", "Havza", "Kavak", "Ladik", "Ondokuzmayıs", "Salıpazarı", 
                 "Terme", "Vezirköprü", "Yakakent"],
            
            # Siirt (56)
            56: ["Merkez", "Baykan", "Eruh", "Kurtalan", "Pervari", "Şirvan", "Tillo"],
            
            # Sinop (57)
            57: ["Merkez", "Ayancık", "Boyabat", "Dikmen", "Durağan", "Erfelek", "Gerze", 
                 "Saraydüzü", "Türkeli"],
            
            # Sivas (58)
            58: ["Merkez", "Akıncılar", "Altınyayla", "Divriği", "Doğanşar", "Gemerek", 
                 "Gölova", "Gürün", "Hafik", "İmranlı", "Kangal", "Koyulhisar", "Şarkışla", 
                 "Suşehri", "Ulaş", "Yıldızeli", "Zara"],
            
            # Tekirdağ (59)
            59: ["Süleymanpaşa", "Çerkezköy", "Çorlu", "Ergene", "Hayrabolu", "Malkara", 
                 "Marmaraereğlisi", "Muratlı", "Saray", "Şarköy"],
            
            # Tokat (60)
            60: ["Merkez", "Almus", "Artova", "Başçiftlik", "Erbaa", "Niksar", "Pazar", 
                 "Reşadiye", "Sulusaray", "Turhal", "Yeşilyurt", "Zile"],
            
            # Trabzon (61)
            61: ["Ortahisar", "Akçaabat", "Araklı", "Arsin", "Beşikdüzü", "Çarşıbaşı", 
                 "Çaykara", "Dernekpazarı", "Düzköy", "Hayrat", "Köprübaşı", "Maçka", 
                 "Of", "Sürmene", "Şalpazarı", "Tonya", "Vakfıkebir", "Yomra"],
            
            # Tunceli (62)
            62: ["Merkez", "Çemişgezek", "Hozat", "Mazgirt", "Nazımiye", "Ovacık", "Pertek", 
                 "Pülümür"],
            
            # Şanlıurfa (63)
            63: ["Eyyübiye", "Haliliye", "Karaköprü", "Akçakale", "Birecik", "Bozova", 
                 "Ceylanpınar", "Harran", "Hilvan", "Siverek", "Suruç", "Viranşehir"],
            
            # Uşak (64)
            64: ["Merkez", "Banaz", "Eşme", "Karahallı", "Sivaslı", "Ulubey"],
            
            # Van (65)
            65: ["İpekyolu", "Tuşba", "Bahçesaray", "Başkale", "Çaldıran", "Çatak", "Edremit", 
                 "Erciş", "Gevaş", "Gürpınar", "Muradiye", "Özalp", "Saray"],
            
            # Yozgat (66)
            66: ["Merkez", "Akdağmadeni", "Aydıncık", "Boğazlıyan", "Çandır", "Çayıralan", 
                 "Çekerek", "Kadışehri", "Saraykent", "Sarıkaya", "Sorgun", "Şefaatli", 
                 "Yenifakılı", "Yerköy"],
            
            # Zonguldak (67)
            67: ["Merkez", "Alaplı", "Çaycuma", "Devrek", "Gökçebey", "Kilimli", "Kozlu"],
            
            # Aksaray (68)
            68: ["Merkez", "Ağaçören", "Eskil", "Gülağaç", "Güzelyurt", "Ortaköy", "Sarıyahşi"],
            
            # Bayburt (69)
            69: ["Merkez", "Aydıntepe", "Demirözü"],
            
            # Karaman (70)
            70: ["Merkez", "Ayrancı", "Başyayla", "Ermenek", "Kazımkarabekir", "Sarıveliler"],
            
            # Kırıkkale (71)
            71: ["Merkez", "Bahşılı", "Balışeyh", "Çelebi", "Delice", "Karakeçili", "Keskin", 
                 "Sulakyurt", "Yahşihan"],
            
            # Batman (72)
            72: ["Merkez", "Beşiri", "Gercüş", "Hasankeyf", "Kozluk", "Sason"],
            
            # Şırnak (73)
            73: ["Merkez", "Beytüşşebap", "Cizre", "Güçlükonak", "İdil", "Silopi", "Uludere"],
            
            # Bartın (74)
            74: ["Merkez", "Amasra", "Kurucaşile", "Ulus"],
            
            # Ardahan (75)
            75: ["Merkez", "Çıldır", "Damal", "Göle", "Hanak", "Posof"],
            
            # Iğdır (76)
            76: ["Merkez", "Aralık", "Karakoyunlu", "Tuzluca"],
            
            # Yalova (77)
            77: ["Merkez", "Altınova", "Armutlu", "Çınarcık", "Çiftlikköy", "Termal"],
            
            # Karabük (78)
            78: ["Merkez", "Eflani", "Eskipazar", "Ovacık", "Safranbolu", "Yenice"],
            
            # Kilis (79)
            79: ["Merkez", "Elbeyli", "Musabeyli", "Polateli"],
            
            # Osmaniye (80)
            80: ["Merkez", "Bahçe", "Düziçi", "Hasanbeyli", "Kadirli", "Sumbas", "Toprakkale"],
            
            # Düzce (81)
            81: ["Merkez", "Akçakoca", "Cumayeri", "Çilimli", "Gölyaka", "Gümüşova", "Kaynaşlı", "Yığılca"]
        }
    
    def _create_province_aliases(self) -> Dict[str, int]:
        """İl adı varyasyonları ve eşlemeleri"""
        aliases = {}
        
        for code, data in self.provinces.items():
            name = data["name"]
            # Ana isim
            aliases[name.upper()] = code
            
            # Unicode normalizasyonu
            normalized = self._normalize_text(name)
            aliases[normalized.upper()] = code
            
        # Özel durumlar
        special_cases = {
            "AFYONKARAHİSAR": 3, "AFYON": 3,
            "KAHRAMANMARAŞ": 46, "MARAŞ": 46, "KAHRAMANMARAş": 46,
            "ŞANLIURFA": 63, "URFA": 63, "ŞANLıURFA": 63,
            "HAKKÂRİ": 30, "HAKKARI": 30,
            "ŞIRNAK": 73, "ŞıRNAK": 73,
            "İSTANBUL": 34, "ISTANBUL": 34,
            "İZMİR": 35, "IZMIR": 35,
            "ÇANKIRI": 18, "ÇANKıRı": 18
        }
        
        aliases.update(special_cases)
        return aliases
    
    def _create_district_aliases(self) -> Dict[str, Tuple[int, str]]:
        """İlçe adı varyasyonları ve (il_kodu, ilçe_adı) eşlemeleri"""
        aliases = {}
        
        for province_code, districts in self.districts.items():
            for district in districts:
                # Ana isim
                key = district.upper()
                aliases[key] = (province_code, district)
                
                # Unicode normalizasyonu
                normalized = self._normalize_text(district)
                aliases[normalized.upper()] = (province_code, district)
        
        return aliases
    
    def _normalize_text(self, text: str) -> str:
        """Türkçe karakterleri normalize et"""
        if not text:
            return ""
        
        # Unicode normalize - NFKC kullan (compatible decomposition + canonical composition)
        text = unicodedata.normalize('NFKC', text)
        
        # Türkçe karakter dönüşümleri - özel karakterler dahil
        replacements = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'C', 'Ğ': 'G', 'I': 'I', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U',
            # Özel Unicode karakterler 
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i', 'ḿ': 'm', 'ń': 'n',
            'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I', 'Ḿ': 'M', 'Ń': 'N',
            # Diğer aksan işaretleri
            'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a',
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o',
            'ù': 'u', 'ú': 'u', 'û': 'u'
        }
        
        for tr_char, en_char in replacements.items():
            text = text.replace(tr_char, en_char)
        
        return text
    
    def map_province(self, province_name: str) -> Optional[Tuple[int, str]]:
        """İl adını resmi il koduna ve adına eşle"""
        if not province_name:
            return None
        
        # Temizle ve normalize et
        clean_name = re.sub(r'[^\w\s]', '', province_name).strip().upper()
        
        # Direkt eşleme dene
        if clean_name in self.province_aliases:
            code = self.province_aliases[clean_name]
            return (code, self.provinces[code]["name"])
        
        # Fuzzy matching
        for alias, code in self.province_aliases.items():
            if alias in clean_name or clean_name in alias:
                return (code, self.provinces[code]["name"])
        
        return None
    
    def map_district(self, district_name: str, province_code: Optional[int] = None) -> Optional[Tuple[int, str]]:
        """İlçe adını resmi il koduna ve ilçe adına eşle"""
        if not district_name:
            return None
        
        clean_name = re.sub(r'[^\w\s]', '', district_name).strip().upper()
        
        # Eğer il kodu biliniyorsa, sadece o ilde ara
        if province_code and province_code in self.districts:
            for district in self.districts[province_code]:
                if (clean_name == district.upper() or 
                    clean_name == self._normalize_text(district).upper()):
                    return (province_code, district)
        
        # Tüm ilçelerde ara
        if clean_name in self.district_aliases:
            return self.district_aliases[clean_name]
        
        # Fuzzy matching
        for alias, (code, name) in self.district_aliases.items():
            if alias in clean_name or clean_name in alias:
                return (code, name)
        
        return None
    
    def validate_geography(self, province_name: str, district_name: Optional[str] = None) -> Dict:
        """Coğrafi bilgileri doğrula ve standartlaştır"""
        result = {
            "valid": False,
            "province_code": None,
            "province_name": None,
            "district_name": None,
            "region": None,
            "corrections": []
        }
        
        # İl eşleme
        province_mapping = self.map_province(province_name)
        if province_mapping:
            code, name = province_mapping
            result["valid"] = True
            result["province_code"] = code
            result["province_name"] = name
            result["region"] = self.provinces[code]["region"]
            
            if name != province_name:
                result["corrections"].append(f"İl adı düzeltildi: {province_name} → {name}")
        else:
            result["corrections"].append(f"Geçersiz il adı: {province_name}")
            return result
        
        # İlçe eşleme
        if district_name:
            district_mapping = self.map_district(district_name, result["province_code"])
            if district_mapping:
                _, district = district_mapping
                result["district_name"] = district
                
                if district != district_name:
                    result["corrections"].append(f"İlçe adı düzeltildi: {district_name} → {district}")
            else:
                # Varsayılan olarak Merkez
                result["district_name"] = "Merkez"
                result["corrections"].append(f"Geçersiz ilçe adı, Merkez olarak atandı: {district_name}")
        else:
            result["district_name"] = "Merkez"
        
        return result
    
    def export_geo_data(self, filepath: str):
        """Coğrafi veriyi JSON olarak dışa aktar"""
        geo_data = {
            "metadata": {
                "total_provinces": 81,
                "total_districts": sum(len(districts) for districts in self.districts.values()),
                "generated_at": datetime.now().isoformat(),
                "source": "T.C. İçişleri Bakanlığı Resmi Verisi"
            },
            "provinces": self.provinces,
            "districts": self.districts,
            "regions": {}
        }
        
        # Bölge bazında grupla
        for code, data in self.provinces.items():
            region = data["region"]
            if region not in geo_data["regions"]:
                geo_data["regions"][region] = []
            geo_data["regions"][region].append({
                "code": code,
                "name": data["name"],
                "plate": data["plate"]
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(geo_data, f, ensure_ascii=False, indent=2)

def main():
    """Test fonksiyonu"""
    mapper = TurkeyGeoMapper()
    
    # Test verileri
    test_cases = [
        ("Çankırı", "Merkez"),
        ("ISTANBUL", "Kadikoy"),
        ("İzmir", "Karşıyaka"),
        ("Afyon", "Merkez"),
        ("Kahramanmaras", "Merkez"),
        ("Hatalı İl", "Hatalı İlçe")
    ]
    
    print("🗺️ TÜRKİYE COĞRAFİ EŞLEME TESTİ")
    print("=" * 50)
    
    for province, district in test_cases:
        result = mapper.validate_geography(province, district)
        
        print(f"\n📍 Test: {province} / {district}")
        print(f"   Geçerli: {'✅' if result['valid'] else '❌'}")
        
        if result["valid"]:
            print(f"   İl: {result['province_name']} ({result['province_code']:02d})")
            print(f"   İlçe: {result['district_name']}")
            print(f"   Bölge: {result['region']}")
        
        if result["corrections"]:
            for correction in result["corrections"]:
                print(f"   🔧 {correction}")
    
    # Geo veriyi dışa aktar
    mapper.export_geo_data('data/turkey_geo_data.json')
    print(f"\n💾 Coğrafi veri kaydedildi: data/turkey_geo_data.json")

if __name__ == "__main__":
    main()
