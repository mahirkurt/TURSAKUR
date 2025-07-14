#!/usr/bin/env python3
"""
Türkiye Sağlık Kuruluşları - Coğrafi Eşleştirme Doğrulama
81 il standardına uygunluk ve coğrafi eşleştirme kalitesi kontrol sistemi
"""
import json
from collections import Counter

def analyze_geographic_mapping():
    """Coğrafi eşleştirme sisteminin kalitesini analiz et"""
    
    # Ana veri dosyasını oku
    with open('data/turkiye_saglik_kuruluslari.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Metadata kontrol et
    metadata = data.get('metadata', {})
    print("🏛️ TÜRKİYE SAĞLIK KURULUŞLARI - COĞRAFİ EŞLEŞTİRME ANALİZİ")
    print("=" * 65)
    print(f"🏥 Toplam sağlık kurumu: {metadata.get('total_kurumlar', 'N/A')}")
    print(f"🗺️ Toplam il sayısı: {metadata.get('total_iller', 'N/A')}")
    print(f"📅 Son güncelleme: {metadata.get('son_guncelleme', 'N/A')}")

    # Kurum listesini al
    kurumlar = data.get('kurumlar', [])

    # İl analizi
    il_dagılımı = Counter(k.get('il_adi') for k in kurumlar)
    total_il_sayisi = len(il_dagılımı)
    
    print(f"\n📊 COĞRAFİ DAĞILIM ANALİZİ")
    print(f"🗺️ Gerçek il sayısı: {total_il_sayisi}")
    print(f"✅ 81 il standardına uygun: {'EVET' if total_il_sayisi == 81 else 'HAYIR'}")
    
    if total_il_sayisi == 81:
        print("🏛️ Türkiye'nin resmi 81 il sistemi başarıyla uygulandı!")
    else:
        print(f"⚠️ Sorun: {total_il_sayisi} il bulundu, 81 olmalı")
    
    # En çok kuruma sahip iller
    print(f"\n🏆 EN ÇOK KURUMA SAHİP İLLER:")
    for il, sayi in il_dagılımı.most_common(10):
        print(f"  {sayi:3d} kurum - {il}")
    
    # Kurum tipi dağılımı
    kurum_tipi_dagılımı = Counter(k.get('kurum_tipi') for k in kurumlar)
    print(f"\n🏥 KURUM TİPİ DAĞILIMI:")
    for tip, sayi in kurum_tipi_dagılımı.most_common():
        print(f"  {sayi:3d} kurum - {tip}")
    
    # Veri kalitesi kontrolleri
    print(f"\n🔍 VERİ KALİTESİ KONTROLLERİ:")
    
    # Eksik il_kodu olan kurumlar
    eksik_il_kodu = [k for k in kurumlar if not k.get('il_kodu')]
    print(f"  📍 Eksik il kodu: {len(eksik_il_kodu)} kurum")
    
    # Eksik kurum_id olan kurumlar  
    eksik_kurum_id = [k for k in kurumlar if not k.get('kurum_id')]
    print(f"  🆔 Eksik kurum ID: {len(eksik_kurum_id)} kurum")
    
    # Koordinat bilgisi olan kurumlar
    koordinatli = [k for k in kurumlar if k.get('koordinat_lat') and k.get('koordinat_lon')]
    print(f"  🗺️ Koordinat bilgisi: {len(koordinatli)} kurum ({len(koordinatli)/len(kurumlar)*100:.1f}%)")
    
    # İl plaka kodu kontrolü
    print(f"\n🚘 İL PLAKA KODU KONTROLLERİ:")
    plaka_kodu_dagılımı = Counter(k.get('il_kodu') for k in kurumlar)
    
    # 1-81 arası plaka kodları kontrolü
    eksik_plaka_kodları = set(range(1, 82)) - set(plaka_kodu_dagılımı.keys())
    if eksik_plaka_kodları:
        print(f"  ⚠️ Eksik plaka kodları: {sorted(eksik_plaka_kodları)}")
    else:
        print(f"  ✅ Tüm plaka kodları (1-81) mevcut")
    
    # Geçersiz plaka kodları
    geçersiz_plaka = [kod for kod in plaka_kodu_dagılımı.keys() if kod and (kod < 1 or kod > 81)]
    if geçersiz_plaka:
        print(f"  ⚠️ Geçersiz plaka kodları: {geçersiz_plaka}")
    
    print(f"\n� COĞRAFİ EŞLEŞTİRME BAŞARI ORANI:")
    başarılı_eşleşme = len([k for k in kurumlar if k.get('il_kodu') and 1 <= k.get('il_kodu', 0) <= 81])
    başarı_oranı = başarılı_eşleşme / len(kurumlar) * 100 if kurumlar else 0
    print(f"  ✅ Başarılı eşleşme: {başarılı_eşleşme}/{len(kurumlar)} (%{başarı_oranı:.1f})")
    
    if başarı_oranı >= 95:
        print("  🌟 Mükemmel! Coğrafi eşleştirme sistemi çok başarılı.")
    elif başarı_oranı >= 90:
        print("  👍 İyi! Coğrafi eşleştirme sistemi başarılı.")
    else:
        print("  ⚠️ Geliştirilmeli! Coğrafi eşleştirme sisteminde iyileştirme gerekli.")

if __name__ == "__main__":
    analyze_geographic_mapping()
