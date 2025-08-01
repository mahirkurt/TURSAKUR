# TURSAKUR 2.0 🏥

**Türkiye Sağlık Kuruluşları Veritabanı** - Modern React Frontend ile Supabase Backend

[![React](https://img.shields.io/badge/React-19.1.0-blue.svg)](https://reactjs.org/)
[![Supabase](https://img.shields.io/badge/Supabase-2.53.0-green.svg)](https://supabase.com/)
[![Vite](https://img.shields.io/badge/Vite-Latest-purple.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## 🎯 Proje Özeti

TURSAKUR 2.0, Türkiye'deki tüm sağlık kuruluşlarının kapsamlı veritabanını sunan modern bir web uygulamasıdır. PostGIS tabanlı coğrafi sorgular, real-time arama, ve kullanıcı dostu arayüz ile sağlık kuruluşlarına kolay erişim sağlar.

## ✨ Özellikler

- 🗺️ **Interaktif Harita**: Leaflet.js ile coğrafi görselleştirme
- 🔍 **Gelişmiş Arama**: Real-time filtreleme ve coğrafi sorgular
- 📱 **Responsive Tasarım**: Mobile-first approach
- ⚡ **Hızlı Performans**: Vite build tool ve React Query
- 🗄️ **Supabase Backend**: PostgreSQL + PostGIS ile güçlü veri yönetimi
- 🔄 **Real-time Updates**: Anlık veri güncellemeleri
- 📊 **Data Visualization**: İstatistiksel görselleştirmeler

## 🏗️ Teknik Stack

### Frontend
- **React 19.1.0** - Modern UI library
- **Vite** - Next generation build tool
- **React Router** - SPA routing
- **Leaflet.js** - Interactive maps
- **React Query** - Server state management
- **Zustand** - Client state management

### Backend
- **Supabase** - Backend-as-a-Service
- **PostgreSQL** - Primary database
- **PostGIS** - Spatial database extension
- **Row Level Security** - Data security

### Development
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Python** - Data processing scripts - Modern Türkiye Sağlık Kuruluşları Haritası

Modern web teknolojileri ile geliştirilmiş, Türkiye'deki sağlık kuruluşlarını harita üzerinde gösteren kapsamlı web uygulaması.

## 🚀 Özellikler

### 🔍 Akıllı Arama ve Filtreleme
- **Gerçek zamanlı arama**: 300ms debounce ile optimize edilmiş
- **Gelişmiş filtreleme**: İl, ilçe, kuruluş tipi, mesafe bazlı filtreleme
- **Coğrafi sorgular**: Harita görünümü bazlı arama
- **Öneri sistemi**: Arama geçmişi ve akıllı öneriler

### 🗺️ İnteraktif Harita
- **Leaflet entegrasyonu**: Performanslı harita deneyimi
- **Kümeleme**: Binlerce kuruluşu optimize şekilde gösterme
- **Gerçek zamanlı filtreleme**: Harita üzerinde anlık filtreleme
- **Çoklu katman desteği**: Farklı kuruluş tiplerini ayrı katmanlarda

### 🎨 Modern Tasarım
- **Material Design 3**: Google'ın en güncel tasarım sistemi
- **Responsive**: Mobil, tablet ve masaüstü uyumlu
- **Dark/Light Mode**: Otomatik tema geçişi
- **Accessibility**: WCAG 2.1 AA standartlarına uygun

### 📊 Analitik ve İstatistikler
- **Gerçek zamanlı istatistikler**: Kuruluş sayıları, tip dağılımı
- **Coğrafi analiz**: İl ve bölge bazlı dağılım
- **Performans metrikleri**: Arama ve filtreleme hızları

## 🏗️ Teknoloji Stack

### Frontend
- **React 18** - Modern UI kütüphanesi
- **Vite** - Hızlı geliştirme ortamı
- **TanStack Query** - Server state yönetimi
- **React Router** - SPA routing
- **Leaflet & React-Leaflet** - Harita entegrasyonu
- **Material Design 3** - Tasarım sistemi

### Backend
- **Supabase** - Backend-as-a-Service
- **PostgreSQL** - İlişkisel veritabanı
- **PostGIS** - Coğrafi veri eklentisi
- **Row Level Security** - Güvenlik katmanı

### DevOps
- **GitHub Actions** - CI/CD pipeline
- **ESLint + Prettier** - Kod kalitesi
- **Lighthouse** - Performans testi
- **Docker** - Konteynerizasyon desteği

## 📋 Hızlı Başlangıç

### Gereksinimler
- Node.js 18+
- Python 3.11+
- Git

### Kurulum

1. **Repository'yi klonlayın**
```bash
git clone https://github.com/[username]/TURSAKUR.git
cd TURSAKUR/tursakur-2.0
```

2. **Bağımlılıkları yükleyin**
```bash
npm install
pip install -r requirements.txt
```

3. **Çevre değişkenlerini ayarlayın**
```bash
cp .env.example .env
# .env dosyasını Supabase bilgilerinizle güncelleyin
```

4. **Uygulamayı başlatın**
```bash
npm run dev
```

Uygulama http://localhost:5173 adresinde çalışacaktır.

## 🔧 Konfigürasyon

### Çevre Değişkenleri

```bash
# Supabase Konfigürasyonu
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key

# Uygulama Konfigürasyonu
VITE_APP_TITLE=TURSAKUR 2.0
VITE_DEFAULT_CENTER_LAT=39.9334
VITE_DEFAULT_CENTER_LNG=32.8597
VITE_DEFAULT_ZOOM=6
```

### Veritabanı Schema

Schema dosyası `database/schema.sql` içinde yer almaktadır. Supabase SQL Editor'da çalıştırın:

```sql
-- PostGIS eklentisini etkinleştir
CREATE EXTENSION IF NOT EXISTS postgis;

-- Diğer schema komutları...
```

## 📊 Veri Migrasyonu

Mevcut JSON verilerini Supabase'e aktarmak için:

```bash
python scripts/load_to_supabase.py
```

Bu script:
- Mevcut JSON dosyalarını okur
- Veri kalitesi kontrolü yapar
- Supabase veritabanına toplu olarak aktarır
- Migrasyon raporunu oluşturur

## 🚀 Deployment

### GitHub Actions ile Otomatik Deploy

1. Repository'nize aşağıdaki secrets'ları ekleyin:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

2. Main branch'e push yapın:
```bash
git push origin main
```

GitHub Actions otomatik olarak:
- Kodu test eder
- Build alır
- Production'a deploy eder
- Veri senkronizasyonu yapar

### Manuel Build

```bash
npm run build
```

Build dosyaları `dist/` klasöründe oluşturulur.

## 🧪 Testing

### Unit Testler
```bash
npm test
```

### E2E Testler
```bash
npm run test:e2e
```

### Performans Testleri
```bash
npm run lighthouse
```

## 📁 Proje Yapısı

```
tursakur-2.0/
├── src/
│   ├── components/          # Yeniden kullanılabilir bileşenler
│   │   ├── TopAppBar.jsx
│   │   ├── SearchBar.jsx
│   │   ├── MapView.jsx
│   │   └── ...
│   ├── pages/              # Sayfa bileşenleri
│   │   ├── HomePage.jsx
│   │   ├── MapPage.jsx
│   │   └── ...
│   ├── hooks/              # Custom React hooks
│   │   └── useInstitutions.js
│   ├── contexts/           # React context providers
│   │   └── ThemeContext.jsx
│   ├── lib/                # Utility kütüphaneleri
│   │   └── supabase.js
│   └── styles/             # Global stiller
│       ├── base.css
│       ├── light.css
│       └── dark.css
├── scripts/                # Python ETL scriptleri
│   ├── supabase_client.py
│   └── load_to_supabase.py
├── database/               # Veritabanı schema
│   └── schema.sql
├── .github/workflows/      # CI/CD konfigürasyonu
└── data/                   # Veri dosyaları
```

## 🎨 Tasarım Sistemi

### Renk Paleti
- **Primary**: #BB0012 (Türk Kırmızısı)
- **Secondary**: #00696D (Petrol Yeşili)
- **Tertiary**: #775700 (Altın Sarısı)

### Tipografi
- **Font**: Figtree (Google Fonts)
- **Scale**: Material Design 3 Type Scale

### Spacing
- **Base Unit**: 8dp
- **Responsive Breakpoints**: 600px, 900px, 1240px

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add some amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

### Kod Standartları
- ESLint konfigürasyonuna uyun
- Prettier ile formatlayın
- Testler yazın
- Commit message'ları konvansiyonel olsun

## 📜 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- **OpenStreetMap** - Harita verileri
- **Supabase** - Backend altyapısı
- **Material Design** - Tasarım sistemi
- **Leaflet** - Harita kütüphanesi

## 📞 İletişim

- **Project Link**: [https://github.com/[username]/TURSAKUR](https://github.com/[username]/TURSAKUR)
- **Documentation**: [Talimatnameler](/talimatnameler/)
- **Issues**: [GitHub Issues](https://github.com/[username]/TURSAKUR/issues)

---

<p align="center">
  <strong>TURSAKUR 2.0</strong> - Modern Türkiye Sağlık Kuruluşları Haritası
  <br>
  ❤️ ile Türkiye için geliştirilmiştir
</p>

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
