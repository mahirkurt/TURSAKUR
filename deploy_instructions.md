# GitHub Pages Deploy Talimatları

Bu dosya https://mahirkurt.github.io/Turkiye-Saglik-Kurumlari/ sayfasına deploy etmek için gerekli adımları içerir.

## 1. GitHub Repository Oluşturma

1. https://github.com/new adresine gidin
2. Repository name: `Turkiye-Saglik-Kurumlari`
3. Description: "Türkiye Sağlık Kurumları - Açık Kaynak Veritabanı ve İnteraktif Web Uygulaması"
4. Public seçeneğini işaretleyin
5. "Create repository" butonuna tıklayın

## 2. Local Repository'yi GitHub ile Bağlama

Aşağıdaki komutları PowerShell'de çalıştırın:

```powershell
# GitHub repository'sini remote olarak ekleyin
git remote add origin https://github.com/mahirkurt/Turkiye-Saglik-Kurumlari.git

# Kodu GitHub'a push edin
git push -u origin main
```

## 3. GitHub Pages Ayarları

1. GitHub repository sayfasında "Settings" sekmesine gidin
2. Sol menüden "Pages" seçeneğini bulun
3. Source olarak "GitHub Actions" seçin
4. Workflow otomatik olarak çalışacak ve sayfanız deploy edilecek

## 4. Deploy Durumunu Kontrol Etme

1. Repository'nin "Actions" sekmesine gidin
2. "Deploy to GitHub Pages" workflow'unu kontrol edin
3. Yeşil ✅ işareti deploy'un başarılı olduğunu gösterir
4. Site URL'si: https://mahirkurt.github.io/Turkiye-Saglik-Kurumlari/

## 5. Özellikler

### Web Uygulaması Özellikleri:
- ✅ 1,674 sağlık kurumu veritabanı
- ✅ Material Design 3 tema sistemi (6 farklı tema)
- ✅ Gelişmiş arama ve filtreleme
- ✅ İnteraktif kurum detay sayfaları
- ✅ Responsive tasarım (mobil uyumlu)
- ✅ Offline çalışma desteği (Service Worker)
- ✅ Karanlık/Aydınlık tema geçişi
- ✅ Erişilebilirlik desteği

### Otomatik Güncellemeler:
- ✅ Günlük veri güncelleme kontrolü
- ✅ GitHub Actions ile CI/CD
- ✅ Veri doğrulama ve test sistemi

## 6. Sorun Giderme

Eğer deploy işlemi başarısız olursa:

1. GitHub Actions loglarını kontrol edin
2. Repository'nin public olduğundan emin olun
3. GitHub Pages özelliğinin aktif olduğunu kontrol edin

## 7. Geliştirme

Local olarak geliştirme yapmak için:

```powershell
# Veri işleme scriptini çalıştır
python scripts/process_data.py

# Web sunucusu başlat (geliştirme için)
python -m http.server 8000 --directory web

# Tarayıcıda açın: http://localhost:8000
```
