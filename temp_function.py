def get_il_kodu_from_il_adi(il_adi: str) -> int:
    """İl adından il kodunu bul"""
    if not il_adi:
        return 0
    
    # İl isimleri haritası
    il_kodlari = {
        'ADANA': 1, 'ADIYAMAN': 2, 'AFYONKARAHİSAR': 3, 'AĞRI': 4, 'AMASYA': 5,
        'ANKARA': 6, 'ANTALYA': 7, 'ARTVİN': 8, 'AYDIN': 9, 'BALIKESİR': 10,
        'BİLECİK': 11, 'BİNGÖL': 12, 'BİTLİS': 13, 'BOLU': 14, 'BURDUR': 15,
        'BURSA': 16, 'ÇANAKKALE': 17, 'ÇANKIRI': 18, 'ÇORUM': 19, 'DENİZLİ': 20,
        'DİYARBAKIR': 21, 'EDİRNE': 22, 'ELAZIĞ': 23, 'ERZİNCAN': 24, 'ERZURUM': 25,
        'ESKİŞEHİR': 26, 'GAZİANTEP': 27, 'GİRESUN': 28, 'GÜMÜŞHANE': 29, 'HAKKARİ': 30,
        'HATAY': 31, 'ISPARTA': 32, 'MERSİN': 33, 'İSTANBUL': 34, 'İZMİR': 35,
        'KARS': 36, 'KASTAMONU': 37, 'KAYSERİ': 38, 'KIRKLARELİ': 39, 'KIRŞEHİR': 40,
        'KOCAELİ': 41, 'KONYA': 42, 'KÜTAHYA': 43, 'MALATYA': 44, 'MANİSA': 45,
        'KAHRAMANMARAŞ': 46, 'MARDİN': 47, 'MUĞLA': 48, 'MUŞ': 49, 'NEVŞEHİR': 50,
        'NİĞDE': 51, 'ORDU': 52, 'RİZE': 53, 'SAKARYA': 54, 'SAMSUN': 55,
        'SİİRT': 56, 'SİNOP': 57, 'SİVAS': 58, 'TEKİRDAĞ': 59, 'TOKAT': 60,
        'TRABZON': 61, 'TUNCELİ': 62, 'ŞANLIURFA': 63, 'UŞAK': 64, 'VAN': 65,
        'YOZGAT': 66, 'ZONGULDAK': 67, 'AKSARAY': 68, 'BAYBURT': 69, 'KARAMAN': 70,
        'KIRIKKALE': 71, 'BATMAN': 72, 'ŞIRNAK': 73, 'BARTIN': 74, 'ARDAHAN': 75,
        'IĞDIR': 76, 'YALOVA': 77, 'KARABÜK': 78, 'KİLİS': 79, 'OSMANİYE': 80,
        'DÜZCE': 81
    }
    
    # İl adını normalize et
    il_original = il_adi.upper().strip()
    
    # Unicode combining characters temizle (örn: ̇ karakter kodu 775)
    il_normalized = unicodedata.normalize('NFD', il_original)
    il_normalized = ''.join(c for c in il_normalized if unicodedata.category(c) != 'Mn')
    il_normalized = unicodedata.normalize('NFC', il_normalized)
    
    # Önce Türkçe karakterli versiyonu dene
    if il_normalized in il_kodlari:
        return il_kodlari[il_normalized]
    
    # Türkçe karakterleri ASCII'ye çevir
    il_ascii = il_normalized.replace('İ', 'I').replace('Ş', 'S').replace('Ğ', 'G')
    il_ascii = il_ascii.replace('Ü', 'U').replace('Ö', 'O').replace('Ç', 'C')
    
    # Alternatif isimler
    alternatifler = {
        'AFYON': 'AFYONKARAHİSAR',
        'K.MARAŞ': 'KAHRAMANMARAŞ',
        'MARAŞ': 'KAHRAMANMARAŞ',
        'KAHRAMANMARAS': 'KAHRAMANMARAŞ',
        'ŞURFA': 'ŞANLIURFA',
        'URFA': 'ŞANLIURFA',
        'SANLIURFA': 'ŞANLIURFA'
    }
    
    if il_ascii in alternatifler:
        il_ascii = alternatifler[il_ascii]
    
    return il_kodlari.get(il_ascii, 0)
