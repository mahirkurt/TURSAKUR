# Türkiye Sağlık Kurumları Veritabanı

Bu proje, Türkiye'deki sağlık kuruluşlarının kapsamlı ve güncel bir veritabanını oluşturmayı amaçlar. Tüm hastaneler, sağlık ocakları, özel klinikler ve diğer sağlık tesislerinin adres, telefon ve diğer iletişim bilgilerini içerir.

## 🌐 Canlı Uygulama

**Web Arayüzü:** [https://turkiye-sakur.web.app](https://turkiye-sakur.web.app)

Firebase Hosting ile sunulan modern web arayüzü:
- 🔍 Gelişmiş arama ve filtreleme
- 📱 Mobil uyumlu responsive tasarım
- 🌙 6 farklı tema seçeneği (açık/koyu + erişilebilirlik)
- 📍 Harita entegrasyonu
- 📞 Direkt arama ve yönlendirme linkleri
- ⚡ Offline çalışma desteği (Service Worker)
- 🚀 Firebase CDN ile hızlı yükleme
- 🔒 Otomatik HTTPS

## 📊 Veri İstatistikleri

- **Toplam Kurum Sayısı:** 1,674
- **Devlet Hastaneleri:** 837
- **Özel Hastaneler:** 571
- **Diş Sağlığı Merkezleri:** 167
- **Eğitim ve Araştırma Hastaneleri:** 91
- **Üniversite Hastaneleri:** 8
- **Kapsanan İl Sayısı:** 106

## 🎯 Özellikler

### Web Arayüzü
- **Modern Tasarım:** Material Design 3 expressive tema sistemi
- **Arama ve Filtreleme:** İl, ilçe, kurum tipi ve metin bazlı arama
- **Responsive Design:** Tüm cihazlarda mükemmel görünüm
- **Tema Seçenekleri:**
  - Açık Tema (light.css)
  - Koyu Tema (dark.css)
  - Yüksek Kontrast Açık/Koyu (light-hc.css, dark-hc.css)
  - Orta Kontrast Açık/Koyu (light-mc.css, dark-mc.css)
- **Klavye Kısayolları:** Hızlı navigasyon
- **Offline Desteği:** Service Worker ile çevrimdışı çalışma

### Veri İşleme
- **Otomatik Güncellemeler:** GitHub Actions ile günlük veri kontrolü
- **Çoklu Kaynak Entegrasyonu:** 3 farklı veri kaynağından toplama
- **Veri Doğrulama:** Kapsamlı hata kontrolü ve temizleme
- **Geocoding:** Adres bazlı koordinat belirleme
- **Unicode Desteği:** Türkçe karakter sorunlarının çözümü

## 🚀 Teknolojiler

### Frontend
- **HTML5** - Semantic web yapısı
- **CSS3** - Modern styling ve animasyonlar
- **JavaScript (ES6+)** - Modüler uygulama mimarisi
- **Material Design 3** - Google'ın tasarım sistemi
- **Material Symbols** - İkon seti
- **Service Worker** - Offline desteği ve performans

### Backend & İşleme
- **Python 3.11+** - Veri işleme ve scraping
- **Requests** - HTTP istekleri
- **BeautifulSoup4** - Web scraping
- **Pandas** - Veri manipülasyonu
- **JSON** - Veri depolama formatı

### DevOps & Deployment
- **GitHub Actions** - CI/CD pipeline
- **GitHub Pages** - Static site hosting
- **Automated Testing** - Veri doğrulama testleri
- **Dependency Management** - Requirements.txt

## 📁 Proje Yapısı

```
├── .github/
│   ├── workflows/
│   │   └── deploy.yml           # GitHub Actions workflow
│   └── copilot-instructions.md  # Copilot talimatları
├── css/                         # Tema dosyaları
│   ├── light.css               # Açık tema
│   ├── dark.css                # Koyu tema
│   ├── light-hc.css            # Yüksek kontrast açık
│   ├── dark-hc.css             # Yüksek kontrast koyu
│   ├── light-mc.css            # Orta kontrast açık
│   └── dark-mc.css             # Orta kontrast koyu
├── data/
│   ├── turkiye_saglik_kuruluslari.json  # Ana veritabanı
│   └── raw/                     # Ham veri dosyaları
├── scripts/                     # Python betikleri
│   ├── process_data.py          # Ana veri işleme
│   ├── validate_data.py         # Veri doğrulama
│   ├── fetch_saglik_bakanligi_data.py
│   ├── fetch_ozel_hastaneler_data.py
│   └── fetch_universite_hastaneleri.py
├── web/                         # Web arayüzü
│   ├── index.html              # Ana sayfa
│   ├── styles/
│   │   └── main.css            # Ana CSS dosyası
│   ├── js/                     # JavaScript modülleri
│   │   ├── main.js             # Ana uygulama
│   │   ├── app.js              # Tema ve modal yönetimi
│   │   ├── data-loader.js      # Veri yükleme modülü
│   │   └── search-filter.js    # Arama ve filtreleme
│   └── sw.js                   # Service Worker
├── requirements.txt            # Python bağımlılıkları
└── README.md                   # Proje dokümantasyonu
```

## 🛠️ Kurulum

### Gereksinimler
- Python 3.11+
- Git
- Modern web tarayıcısı

### Yerel Geliştirme

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
```

2. **Python bağımlılıklarını yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Veri işleme betiğini çalıştırın:**
```bash
python scripts/process_data.py
```

4. **Web arayüzünü çalıştırın:**
```bash
# Basit HTTP sunucusu
cd web
python -m http.server 8000
```

5. **Tarayıcıda açın:**
```
http://localhost:8000
```

### GitHub Pages Deployment

1. **Repository'yi GitHub'a push edin**
2. **GitHub Pages'i etkinleştirin:**
   - Settings > Pages
   - Source: GitHub Actions
3. **Workflow otomatik olarak çalışacak**

## 📊 Veri Yapısı

Her sağlık kurumu için aşağıdaki alanlar bulunur:

```json
{
  "kurum_id": "TR-34-DEV-001",
  "kurum_adi": "İstanbul Üniversitesi İstanbul Tıp Fakültesi",
  "kurum_tipi": "Üniversite Hastanesi",
  "il_kodu": 34,
  "il_adi": "İstanbul",
  "ilce_adi": "Fatih",
  "adres": "Millet Cad. Çapa, 34093 Fatih/İstanbul",
  "telefon": "+902126351188",
  "koordinat_lat": 41.0178,
  "koordinat_lon": 28.9619,
  "web_sitesi": "https://www.itf.istanbul.edu.tr",
  "veri_kaynagi": "Üniversite Hastaneleri",
  "son_guncelleme": "2024-01-15"
}
```

## 🔧 API Kullanımı

### Veri Dosyasına Erişim
```javascript
// Tüm verileri al
fetch('/data/turkiye_saglik_kuruluslari.json')
  .then(response => response.json())
  .then(data => {
    console.log(`Toplam kurum: ${data.kurumlar.length}`);
  });
```

### Filtreleme Örnekleri
```javascript
// İstanbul'daki hastaneler
const istanbulHospitals = data.kurumlar.filter(k => k.il_adi === 'İstanbul');

// Üniversite hastaneleri
const universitySites = data.kurumlar.filter(k => k.kurum_tipi.includes('Üniversite'));

// Telefonu olan kurumlar
const withPhone = data.kurumlar.filter(k => k.telefon);
```

## 🤝 Katkıda Bulunma

1. **Fork** edin
2. **Feature branch** oluşturun (`git checkout -b feature/AmazingFeature`)
3. **Commit** edin (`git commit -m 'Add some AmazingFeature'`)
4. **Push** edin (`git push origin feature/AmazingFeature`)
5. **Pull Request** açın

### Kod Yazım Kuralları
- Python için PEP 8 standartları
- Type hints kullanın
- Docstring'leri dahil edin
- Kapsamlı hata yönetimi
- Logging için Python logging modülü

## 📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

- **GitHub Issues:** Bug raporları ve özellik istekleri
- **Email:** [YOUR_EMAIL]
- **Web:** [https://USERNAME.github.io/REPOSITORY](https://USERNAME.github.io/REPOSITORY)

## 🙏 Teşekkürler

- **Sağlık Bakanlığı** - Resmi sağlık tesisleri verileri
- **Özel Hastaneler** - Özel sağlık kurumları bilgileri  
- **Üniversiteler** - Üniversite hastaneleri verileri
- **Material Design Team** - Tasarım sistemi
- **GitHub** - Hosting ve CI/CD altyapısı

---

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**
