# Firebase Deployment Talimatları

Bu dosya Firebase Hosting üzerinde deploy etmek için gerekli adımları içerir.

## 1. Ön Gereksinimler

### Node.js yükleyin
```bash
# https://nodejs.org/ adresinden indirin
```

### Firebase CLI yükleyin
```bash
npm install -g firebase-tools
```

### Firebase'e giriş yapın
```bash
firebase login
```

## 2. Manuel Deployment

### Veriyi güncelleyin
```bash
python scripts/process_data.py
```

### Public klasörünü hazırlayın
```powershell
# Windows PowerShell
Copy-Item index.html public/
Copy-Item -Recurse js public/
Copy-Item -Recurse css public/
Copy-Item -Recurse styles public/
Copy-Item -Recurse data public/
Copy-Item sw.js public/
```

### Firebase'e deploy edin
```bash
firebase deploy
```

## 3. GitHub Actions ile Otomatik Deployment

### GitHub Secrets Ekleme

1. Firebase CI token oluşturun:
   ```bash
   firebase login:ci
   ```

2. GitHub repository > Settings > Secrets and variables > Actions:
   - `FIREBASE_TOKEN`: Yukarıdaki komuttan aldığınız token

### Tetikleme Yöntemleri

- **Otomatik**: `main` branch'e push yapıldığında
- **Manuel**: GitHub Actions sekmesinden "Run workflow"
- **Zamanlanmış**: Her gün saat 02:00'da veri güncellemesi

## 4. Firebase Proje URL'leri

- **Hosting URL**: https://turkiye-sakur.web.app
- **Firebase Console**: https://console.firebase.google.com/project/turkiye-sakur

## 5. Özellikler

### Web Uygulaması Özellikleri:
- ✅ 1,674+ sağlık kurumu veritabanı
- ✅ Material Design 3 tema sistemi (6 farklı tema)
- ✅ Gelişmiş arama ve filtreleme
- ✅ İnteraktif kurum detay sayfaları
- ✅ Responsive tasarım (mobil uyumlu)
- ✅ Offline çalışma desteği (Service Worker)
- ✅ Karanlık/Aydınlık tema geçişi
- ✅ Erişilebilirlik desteği
- ✅ Firebase Hosting ile hızlı CDN
- ✅ Otomatik HTTPS
- ✅ Global deployment

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
