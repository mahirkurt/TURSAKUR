<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Türkiye Sağlık Kuruluşları Projesi - Copilot Talimatları

Bu proje, Türkiye'deki sağlık kuruluşlarının açık kaynaklı veritabanını oluşturmayı amaçlar.

## Proje Özellikleri
- JSON formatında veri depolama
- Python tabanlı veri işleme betikleri
- Web scraping ve geocoding
- GitHub Actions ile CI/CD
- Leaflet.js ile interaktif harita
- DataTables.js ile aranabilir veri tablosu

## Kod Yazım Kuralları
- Python için PEP 8 standartlarını kullan
- Type hints ekle
- Docstring'leri dahil et
- Hata yönetimi (try-except) kullan
- Logging için Python logging modülünü kullan

## Veri Yapısı
Her sağlık kurumu için şu alanları kullan:
- kurum_id (string): TR-[il_kodu]-[tip_kodu]-[sira_no]
- kurum_adi (string): Resmi kurum adı
- kurum_tipi (enum): Standart kategori listesi
- il_kodu, il_adi, ilce_adi (string/int)
- adres (string): Tam adres
- telefon (string): +90XXXXXXXXXX formatında
- koordinat_lat, koordinat_lon (float): Enlem/boylam
- web_sitesi (string): URL formatında
- veri_kaynagi (string): Kaynak açıklaması
- son_guncelleme (date): YYYY-MM-DD formatında

## Güvenlik
- API anahtarlarını environment variable olarak kullan
- Hassas bilgileri kod içine yazma
- Rate limiting uygula (web scraping için)

## Test
- Unit testler yaz
- Veri doğrulama testleri ekle
- CI/CD pipeline'da testleri çalıştır
