# TURSAKUR 2.0: Kapsamlı Teknik Mimari ve Geliştirme Referansı

**Doküman Versiyonu:** 1.2
**Tarih:** 1 Ağustos 2025
**Hazırlayan:** Gemini

## 1. Vizyon ve Stratejik Hedefler

**TURSAKUR 1.0**, Türkiye'deki sağlık kuruluşları verisini farklı kaynaklardan toplayıp tek bir merkezde birleştirerek kamuya değerli bir hizmet sunmuştur. Bu sürecin başarısı, projenin veri odaklı yaklaşımının ve otomasyon yeteneklerinin bir kanıtıdır.

**TURSAKUR 2.0**, bu sağlam temel üzerine inşa edilecek yeni nesil bir platformdur. Stratejik hedef, statik bir veri deposu olmaktan çıkıp, **yaşayan, dinamik, gerçek zamanlıya yakın güncellenen ve kullanıcı etkileşimine açık** bir sağlık bilgi ekosistemi haline gelmektir. Bu yeni vizyon, en güncel teknolojilerle desteklenerek daha üstün bir kullanıcı deneyimi, daha kolay bakım ve gelecekteki geliştirmeler için maksimum esneklik sunmayı amaçlamaktadır.

## 2. Temel Teknolojiler ve Gerekçeleri

Projenin başarısı için seçilen teknoloji yığını, modern, ölçeklenebilir ve geliştirici dostu olma kriterlerine göre belirlenmiştir.

| Katman | Teknoloji | Gerekçe |
| :--- | :--- | :--- |
| **Frontend** | **React (Vite ile)** | **Hız ve Ekosistem:** Vite, inanılmaz hızlı bir geliştirme sunucusu ve optimize edilmiş build süreçleri sunar. React'in devasa ekosistemi, bileşen tabanlı mimarisi ve güçlü topluluk desteği, karmaşık arayüzlerin yönetimini kolaylaştırır. |
| **UI/UX** | **Material Design 3 (Material Theme Builder ile)** | **Saf ve Tutarlı Tasarım:** Projenin görsel dili, Google'ın en güncel tasarım sistemi olan MD3 ile birebir uyumlu olacaktır. Bu, Material Theme Builder aracından üretilen ve CSS değişkenlerini temel alan tema dosyalarıyla sağlanarak tasarım tutarlılığı garanti altına alınır. |
| **Backend & Veritabanı** | **Supabase** | **Hızlandırılmış Backend Geliştirme:** PostgreSQL veritabanı, otomatik API, kimlik doğrulama ve gerçek zamanlı yetenekleri tek bir platformda sunarak backend geliştirme ihtiyacını minimize eder. **PostGIS eklentisi**, gelişmiş coğrafi sorgular için kritik öneme sahiptir. |
| **Veri İşleme** | **Python** | **Mevcut Uzmanlıktan Faydalanma:** Projenin 1.0 versiyonundaki veri toplama ve işleme script'leri, minimum değişiklikle yeni mimariye entegre edilebilir. Python'un veri işleme kütüphaneleri bu görev için endüstri standardıdır. |
| **DevOps** | **GitHub & GitHub Actions** | **Entegre Geliştirme ve Dağıtım:** Kod yönetimi, versiyonlama, iş takibi (issues) ve CI/CD süreçlerinin tek bir platformdan yönetilmesi, geliştirme döngüsünü basitleştirir ve otomatikleştirir. |
| **Hosting** | **Vercel / Netlify** | **Modern Frontend Barındırma:** Bu platformlar, Vite ile oluşturulmuş uygulamalar için optimize edilmiştir. GitHub entegrasyonları sayesinde `git push` komutu ile otomatik dağıtım (deployment) imkanı sunarlar. |

## 3. Sistem Mimarisi (Genel Bakış)

TURSAKUR 2.0, birbirinden bağımsız ama entegre çalışan üç ana katmandan oluşur. Bu "ayrık mimari" (decoupled architecture), her bir parçanın bağımsız olarak geliştirilip ölçeklendirilmesine olanak tanır.

## 4. Katman 1: Veri İşleme ve Senkronizasyon (Backend)

Bu katman, projenin veri motorudur. Mevcut Python script'leri bu katmanın temelini oluşturacaktır.

* **Orkestrasyon:** Veri toplama işlemleri, periyodik olarak (örn. her gece) **GitHub Actions** üzerinde çalışan bir "cron job" ile tetiklenir.
* **İşleyiş:** Python ETL script'leri çalışır ve temiz veriyi Supabase PostgreSQL veritabanına yazar.

### 4.1. Supabase Veritabanı Şeması

Veritabanında `kuruluslar` adında merkezi bir tablo bulunacaktır. PostGIS eklentisinin aktif edilmesi kritiktir.

```sql
-- PostGIS eklentisini etkinleştir
CREATE EXTENSION IF NOT EXISTS postgis;

-- Sağlık kuruluşları için ana tablo
CREATE TABLE public.kuruluslar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Temel Bilgiler
    isim TEXT NOT NULL,
    tip TEXT, -- 'Devlet Hastanesi', 'Özel Hastane', 'Üniversite Hastanesi', 'ASM' vb.
    alt_tip TEXT,
    
    -- İletişim ve Adres
    adres TEXT,
    il TEXT,
    ilce TEXT,
    telefon TEXT,
    website TEXT,
    email TEXT,
    
    -- Coğrafi Veri (En Önemli Kısım)
    konum GEOMETRY(Point, 4326), -- 4326: GPS koordinat sistemi (WGS 84)
    
    -- Ekstra Meta Veri
    veri_kaynagi TEXT[], -- Bu kaydın hangi kaynaklardan geldiği (örn: ['sb.gov.tr', 'wikipedia'])
    aktif BOOLEAN DEFAULT true,
    ozellikler JSONB -- Poliklinikler, yatak sayısı gibi esnek veriler için
);

-- Coğrafi sorguları hızlandırmak için bir GIST indeksi oluşturulur.
CREATE INDEX idx_kuruluslar_konum ON public.kuruluslar USING gist (konum);

-- Arama performansını artırmak için metin alanlarına indeksler
CREATE INDEX idx_kuruluslar_isim ON public.kuruluslar USING gin (to_tsvector('turkish', isim));
CREATE INDEX idx_kuruluslar_il_ilce ON public.kuruluslar (il, ilce);
```

## 5. Katman 2: Veri ve API Platformu (Supabase)

Bu katman, geliştirme sürecini en çok hızlandıran kısımdır ve otomatik API, kimlik doğrulama ve gerçek zamanlı yetenekler sunar.

## 6. Katman 3: İstemci Uygulaması (Frontend)

Kullanıcının gördüğü ve etkileşimde bulunduğu modern web uygulamasıdır.

### 6.1. Proje Yapısı (React + Vite)

Standart ve ölçeklenebilir bir klasör yapısı benimsenmelidir (`/src` altında `components`, `pages`, `services`, `styles` vb.).

### 6.2. UI/UX ve Tasarım Sistemi (Material Design 3 & Material Theme Builder)

Projenin görsel dili, Material Theme Builder'dan üretilen CSS değişkenleri ve Google'ın resmi Material Web Components (`@material/web`) kütüphanesi ile MD3'e tam uyumlu olacaktır.

### 6.3. Durum Yönetimi (State Management)

`useState`, `useContext` ve özellikle asenkron veri yönetimi için **TanStack Query (React Query)** kullanılacaktır.

### 6.4. Kullanıcı Deneyimi (UX) ve Arayüz Özellikleri

Bu bölüm, TURSAKUR 2.0'ın temel kullanıcı etkileşimlerini ve arayüz bileşenlerini detaylandırmaktadır. Amaç, kullanıcıya akıcı, hızlı ve güçlü bir bilgiye erişim deneyimi sunmaktır.

#### **A. Akıllı Arama Çubuğu (`<SearchBar />`)**

Uygulamanın merkezinde yer alan bu bileşen, basit bir metin giriş alanından çok daha fazlası olacaktır.

* **Anında Sonuçlar:** Kullanıcı yazmaya başladığı anda, Supabase'in metin arama (`to_tsvector`) yetenekleri kullanılarak sonuçlar anında arama çubuğunun altında belirir.
* **Gecikmeli Sorgu (Debouncing):** Kullanıcının her tuş vuruşunda API'ye istek gönderilmesini önlemek için bir `useDebounce` hook'u kullanılacaktır. Bu, kullanıcı yazmayı bıraktıktan ~300ms sonra sorgunun gönderilmesini sağlayarak performansı artırır.
* **Kategorize Edilmiş Öneriler:** Arama sonuçları "Kuruluşlar", "İller" ve "İlçeler" gibi başlıklar altında gruplandırılarak sunulur. Bu, kullanıcının aradığını daha hızlı bulmasını sağlar.
* **Klavye Navigasyonu:** Kullanıcı, klavyenin ok tuşları ile arama sonuçları arasında gezinebilir ve Enter tuşu ile seçtiği sonuca gidebilir.

#### **B. Gelişmiş Filtreleme Paneli (`<FilterPanel />`)**

Arama sonuçlarını daraltmak için kullanıcıya güçlü araçlar sunar.

* **Bağımlı Filtreler:** "İl" filtresinde bir seçim yapıldığında, "İlçe" filtresinin seçenekleri otomatik olarak sadece o ile ait ilçelerle doldurulur. Bu, Supabase'e yapılacak dinamik bir sorgu ile sağlanır.
* **Çoklu Seçim:** Kullanıcı, "Kurum Tipi" gibi filtrelerde birden fazla seçenek (örn: hem 'Devlet Hastanesi' hem de 'Üniversite Hastanesi') seçebilir. Supabase sorgusu, bu seçimleri `in` operatörü ile işleyecektir.
* **Anlık Güncelleme:** Filtrelerde yapılan her değişiklik, sayfanın yeniden yüklenmesine gerek kalmadan sonuç listesini ve haritayı anında günceller. Bu, TanStack Query'nin sorgu anahtarlarını dinamik olarak yönetmesiyle sağlanır.
* **Filtreleri Temizle:** Tek bir tuşla uygulanan tüm filtreleri temizleme seçeneği sunulur.

#### **C. Etkileşimli Harita Görünümü (`<MapView />`)**

Verinin coğrafi olarak keşfedilmesini sağlayan temel bileşendir.

* **Performans için Kümeleme (Clustering):** Harita üzerinde birbirine yakın çok sayıda nokta olduğunda (örn: İstanbul'daki tüm Aile Sağlığı Merkezleri), bu noktalar tek bir küme ikonu altında gruplanır. Kullanıcı haritaya yaklaştıkça bu kümeler açılarak noktalar görünür hale gelir. `react-leaflet-markercluster` gibi kütüphaneler bu iş için kullanılabilir.
* **Harita-Liste Senkronizasyonu:**
    * Kullanıcı, sonuç listesindeki bir kurum kartının üzerine geldiğinde, haritadaki ilgili pin vurgulanır (örn: rengi değişir veya boyutu büyür).
    * Kullanıcı, haritadaki bir pine tıkladığında, sonuç listesi otomatik olarak o kurumun olduğu yere kaydırılır ve ilgili kart vurgulanır.
* **"Bu Alanda Ara":** Kullanıcı haritayı kaydırdığında veya yakınlaştırdığında, "Bu Alanda Ara" butonu belirir. Tıklandığında, sadece haritanın mevcut görünümündeki sınırlar içinde kalan kurumları listeleyecek yeni bir sorgu gönderilir. Bu, Supabase'in PostGIS `ST_MakeEnvelope` ve `ST_Intersects` fonksiyonları ile gerçekleştirilir.

#### **D. Kurum Bilgi Kartı (`<InstitutionCard />`)**

Arama sonuçları listesindeki her bir kurumu temsil eden, zengin içerikli bileşendir.

* **Hiyerarşik Bilgi Sunumu:** Kurumun adı, tipi, adresi gibi temel bilgiler net bir şekilde sunulur.
* **Hızlı Eylem Butonları:** Kart üzerinde "Yol Tarifi Al" (Google Maps'e yönlendirir), "Telefon Et" (`tel:` linki ile) ve "Web Sitesini Ziyaret Et" gibi ikon tabanlı butonlar bulunur.
* **Genişletilebilir Detaylar:** Kart üzerinde bir "Daha Fazla Bilgi" butonu ile, kurumun poliklinikleri, yatak sayısı gibi `ozellikler` JSONB alanında tutulan detaylı veriler gösterilebilir.
* **Ulaşım Mesafesi:** Eğer kullanıcı konum izni verdiyse, her kartta kuruma olan yaklaşık kuş uçuşu mesafe bilgisi gösterilebilir. Bu, PostGIS'in `ST_Distance` fonksiyonu ile hesaplanır.

## 7. Geliştirme ve Dağıtım Süreçleri (DevOps)

**Git**, **GitHub Actions** ve **Vercel/Netlify** kullanılarak tam otomatik bir CI/CD süreci kurulacaktır.

## 8. Yol Haritası ve Gelecek Potansiyeli

Bu mimari, gelecekte **kullanıcı katkısı**, **gelişmiş arama** ve **PWA** gibi özelliklerin kolayca eklenmesine olanak tanır.
