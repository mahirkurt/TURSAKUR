# TURSAKUR 2.0 - İleri Düzey Material 3 Tasarım ve Uygulama Rehberi

**Doküman Versiyonu:** 3.1 (Master)
**Tarih:** 1 Ağustos 2025
**Hazırlayan:** Gemini

## Temel Felsefe

Projemiz, kullanıcı deneyimini zenginleştirmek ve marka kimliğimizi yansıtmak amacıyla Google'ın en güncel tasarım dili olan **Material Design 3 (M3)**'ü temel alır. Temel hedeflerimiz, markamızın kimliğine uygun, **"ifadeci" (expressive)**, dinamik, güvenilir ve tüm kullanıcılar için **erişilebilir** bir arayüz oluşturmaktır. Bu rehber, projedeki tüm geliştiricilerin uyması gereken standartları belirler ve sıradan bir uygulamadan çok, yaşayan ve akılda kalıcı bir dijital deneyim yaratmanın manifestosudur.

---

## 1. Temalaştırma (Theming): Kimliğin Dijital DNA'sı

Projemizin renk, tipografi ve şekil temaları için tek bir doğruluk kaynağı (single source of truth) vardır: **Material Theme Builder**. Tema, programatik olarak kod içinde üretilmez; bu araçtan dışa aktarılan CSS dosyaları ile yönetilir.

**Ana Tema Klasörü:** `src/styles/`

Bu klasör, tüm tema dosyalarını barındırır. Yapı, farklı renk şemaları (açık/koyu) ve kontrast seviyeleri arasında dinamik geçişi destekleyecek şekilde modüler olarak tasarlanmıştır.

* `theme/light.css`: Standart açık tema renk değişkenleri.
* `theme/light-mc.css`: Orta kontrastlı açık tema.
* `theme/light-hc.css`: Yüksek kontrastlı açık tema.
* `theme/dark.css`: Standart koyu tema renk değişkenleri.
* `theme/dark-mc.css`: Orta kontrastlı koyu tema.
* `theme/dark-hc.css`: Yüksek kontrastlı koyu tema.
* `base.css`: Tüm temalar tarafından paylaşılan temel stiller (tipografi, şekil, reset stilleri, `body` için temel renkler vb.).

### 1.1. Renk (Color): Duygu ve Hiyerarşi

Renk paletimiz, TURSAKUR marka kimliğini yansıtan tohum renkler üzerine kurulmuştur.

* **Birincil Renk (Primary):** `#BB0012` (Canlı Kırmızı).
* **İkincil Renk (Secondary):** `#00696D` (Turkuaz/Deniz Mavisi).
* **Üçüncül Renk (Tertiary):** `#775700` (Altın Sarısı/Okra).

#### **İleri Seviye Renk Kullanımı: Tonal Paletler**

Geliştiriciler, sadece ana renklerle sınırlı kalmamalıdır. Material Theme Builder, her tohum renkten 13 tonluk bir **tonal palet** üretir. Bu paletler, arayüze derinlik ve ifade katmak için kullanılmalıdır:

* **`Primary Container` / `Secondary Container`:** Vurgulanması gereken bileşenlerin (seçili bir filtre çipi, bir bilgi kartının başlığı) arka planı için kullanılır.
* **`Surface` Renkleri (`Surface`, `Surface Dim`, `Surface Bright`):** Uygulamanın genel arka plan katmanlarını oluşturur. `Surface Dim` gibi daha koyu tonlar, arayüze derinlik katmak için kullanılabilir.
* **`Surface Container` Renkleri:** `Surface` üzerinde yer alan bileşenlerin (kartlar, dialoglar) arka planları için kullanılır. `Surface Container High` veya `Highest` gibi tonlar, bir bileşeni diğerlerinden daha fazla öne çıkarmak için kullanılır.

### 1.2. Tipografi (Typography): Ses ve Okunabilirlik

* **Font Ailesi:** **Figtree**.
* **Entegrasyon:** Figtree, Google Fonts üzerinden projeye dahil edilir.
* **Stil ve Ölçek:** Geliştirme sırasında M3'ün tipografi ölçeğini tanımlayan CSS değişkenleri (`--md-sys-typescale-display-large` vb.) kullanılmalıdır. **Metin stillerini asla manuel olarak (örn: `font-size: 16px;`) tanımlamayın.**

### 1.3. Şekil (Shape): Dokunsallık ve Marka

* **Ölçek:** `None`, `Extra Small`, `Small`, `Medium`, `Large`, `Extra Large`, `Full`.
* **Uygulama:**
    * **Kartlar, Dialoglar:** Medium (`12dp`)
    * **Butonlar, Çipler:** Full (Tam yuvarlak)
    * **Görseller, Medya:** Large (`16dp`)

### 1.4. Tema Uygulama ve Değiştirme (React)

Tema dosyaları, `main.jsx` içinde import edilir. Tema değişimi, React Context API kullanılarak uygulama genelinde yönetilir.

1.  **CSS Dosyalarını Import Etme (`main.jsx`):**
    ```jsx
    import React from 'react';
    import ReactDOM from 'react-dom/client';
    import App from './App';

    // Temel stilleri ve tüm tema varyasyonlarını import et
    import './styles/base.css';
    import './styles/theme/light.css';
    import './styles/theme/dark.css';
    // Gerekirse diğer kontrast dosyaları da burada import edilebilir.

    ReactDOM.createRoot(document.getElementById('root')).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
    ```

2.  **Tema Yönetim Context'i (`src/contexts/ThemeContext.jsx`):**
    ```jsx
    import React, { createContext, useState, useLayoutEffect, useContext } from 'react';

    const ThemeContext = createContext();

    export const ThemeProvider = ({ children }) => {
      // 'light' veya 'dark'
      const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

      useLayoutEffect(() => {
        // `<html>` etiketine tema sınıfını uygula
        document.documentElement.className = ''; // Önceki sınıfları temizle
        document.documentElement.classList.add(theme);
        localStorage.setItem('theme', theme);
      }, [theme]);

      const toggleTheme = () => {
        setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
      };

      return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
          {children}
        </ThemeContext.Provider>
      );
    };

    export const useTheme = () => useContext(ThemeContext);
    ```
    *Not: Bu örnekte `light.css` ve `dark.css` dosyalarının sırasıyla `.light` ve `.dark` sınıflarını tanımladığı varsayılmıştır. Material Theme Builder çıktısı doğrudan sınıf ismi olmadan değişkenleri tanımlıyorsa, CSS dosyalarının başına ilgili sınıf ismi eklenmelidir.*

---

## 2. Hareket ve Animasyon (Motion & Animation): Canlı ve Sezgisel Arayüz

Animasyon, sadece bir süsleme değil, kullanıcıya geri bildirim sağlayan, hiyerarşiyi güçlendiren ve deneyimi keyifli hale getiren temel bir unsurdur.

### 2.1. Easing ve Süre (Easing & Duration)

* **Easing Curves:** `Emphasized`, `Standard`, `Linear`.
* **Süre:** `Kısa (100-200ms)`, `Orta (200-500ms)`, `Uzun (500ms+)`.

### 2.2. Sayfa Geçişleri (Page Transitions)

* **Shared Axis (Paylaşılan Eksen):** Hiyerarşik olarak aynı seviyedeki sayfalar arasında kullanılır.
* **Fade Through (Solma ile Geçiş):** Birbirleriyle ilişkisi olmayan sayfalar arasında kullanılır.

### 2.3. Durum Katmanları (State Layers)

Kullanıcı etkileşimleri, bileşenin üzerine binen yarı saydam bir renk katmanıyla görselleştirilir.

* **Hover:** `on-surface` renginin `%8` opaklığı.
* **Focus:** `on-surface` renginin `%12` opaklığı.
* **Pressed:** `on-surface` renginin `%12` opaklığı.
* **Dragged:** `on-surface` renginin `%16` opaklığı.

### 2.4. İleri Seviye: Animasyon Koreografisi ve Mikro-etkileşimler

* **Koreografi:** Birden fazla elementin ekrana giriş veya çıkışı, bir bütün olarak anlamlı bir hareket oluşturmalıdır.
    * **Staggering (Sendeletme):** Bir listedeki öğeler ekrana girerken, hepsi aynı anda değil, aralarında 20-30ms gibi küçük gecikmelerle girmelidir.
    * **Sıralı Animasyon:** Bir kart genişlediğinde, önce kartın boyutu büyür, ardından içindeki metin ve ikonlar `fade-in` olur.
* **Mikro-etkileşimler:** Kullanıcıya anında ve keyifli geri bildirimler veren küçük animasyonlardır.

---

## 3. Layout ve Boşluk Sistemi (Layout & Spacing)

### 3.1. 8dp Grid Sistemi

Tüm bileşenlerin boyutları ve boşlukları **8dp'nin katları** olmalıdır.

### 3.2. İleri Seviye: Kanonik Layout'lar ve Uyarlanabilir Bileşenler

* **Supporting Pane:** Masaüstü ve tabletlerde, ana içeriğin yanında ek bilgiler sunan bir panel.
* **Uyarlanabilir Bileşenler:** CSS Container Queries (`@container`) ile bileşenlerin kendi boyutlarına göre stil değiştirmesi sağlanır.

---

## 4. Bileşen, İkon ve Logo Yönetimi

* **Bileşen Kütüphanesi:** Google'ın resmi **Material Web Components** (`@material/web`).
* **İkonlar:** **Material Symbols**.
* **Logo Kullanımı:** `TURSAKUR-Light.png` (koyu zemin), `TURSAKUR-Color.png` (açık zemin), `TURSAKUR-Dark.png` (monokrom).

---

## 5. Duyarlı Tasarım ve Cihaza Özel Deneyim

### 5.1. Telefon (Genişlik < 600dp)

* **Navigasyon:** **Bottom Navigation Bar** ve **Modal Navigation Drawer**.
* **Layout:** Tek sütunlu, dikey taranabilir düzen.

### 5.2. Tablet (600dp - 1239dp arası)

* **Navigasyon:** Dikey, ikon tabanlı ve sabit **Navigation Rail**.
* **Layout:** **List-Detail arayüzü** ve çok sütunlu kart düzenleri.

### 5.3. Masaüstü (Genişlik > 1240dp)

* **Navigasyon:** Her zaman açık, ikon ve metin içeren **Permanent Navigation Drawer**.
* **Layout ve Etkileşim:** **Hover** etkileşimleri zorunludur. **Yoğun veri tabloları** ve **Klavye kısayolları** ile deneyim zenginleştirilir.

---

## 6. Geliştirme Standartları ve En İyi Pratikler

### 6.1. Kod Kalitesi

* **Linter & Formatter:** **ESLint** ve **Prettier** kullanımı zorunludur.
* **Otomatik Kontrol:** `husky` ve `lint-staged` ile her `commit` öncesi otomatik kontrol.
* **Commit Mesajları:** **Conventional Commits** standardına uyulmalıdır.

### 6.2. Performans Optimizasyonu

* **Tembel Yükleme (Lazy Loading):** `React.lazy` ve `Suspense` ile sayfa ve bileşen bazlı kod ayırma standarttır.
* **Bundle Analizi:** `vite-plugin-visualizer` ile periyodik paket analizi yapılmalıdır.
* **Algısal Yük Yönetimi:** `Intersection Observer API` kullanılarak kullanıcı aşağı kaydırdıkça içerik yüklenir.

### 6.3. İleri Düzey Erişilebilirlik (a11y)

* **Semantik HTML ve ARIA Rolleri:** Temel gerekliliklerdir.
* **Hareket Azaltma Tercihi:** Kullanıcının işletim sisteminde "hareketi azalt" ayarı aktifse, animasyonlar devre dışı bırakılmalıdır.
* **Canlı Bölgeler (Live Regions):** Dinamik olarak güncellenen içerikler için `aria-live` attribute'u kullanılmalıdır.

### 6.4. State Management Felsefesi

* **Yerel State Önceliği:** `useState` ile bileşen içinde tutulmalıdır.
* **Global State (`Zustand`):** Sadece zorunlu global durumlar (kullanıcı, tema) için kullanılır. Store'lar konuya özel olarak ayrılır.

---

## 7. Marka İfadesi (Brand Expression): TURSAKUR Kimliğini Yaratmak

* **İmza Anları:** Uygulamanın en önemli anlarında markaya özgü, koreografisi yapılmış animasyonlar kullanılır.
* **Dokunsal Geri Bildirim (Haptic Feedback):** Destekleyen mobil cihazlarda, önemli eylemler tamamlandığında hafif bir titreşim geri bildirimi verilebilir.
* **Boş Durumlar (Empty States):** Sonuç bulunamadığında, sadece metin yerine yardımcı bir illüstrasyon ve eylem butonu gösterilmelidir.
