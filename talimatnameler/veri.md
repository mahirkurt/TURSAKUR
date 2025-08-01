# TURSAKUR 2.0 - Veri Toplama ve Otomasyon Rehberi

**Doküman Versiyonu:** 1.2 (Master)
**Tarih:** 1 Ağustos 2025
**Hazırlayan:** Gemini

## 1. Temel Felsefe ve İlkeler

Bu doküman, TURSAKUR veritabanının temelini oluşturan veri toplama, işleme ve yükleme (ETL - Extract, Transform, Load) süreçlerinin teknik manifestosudur. Amacımız, Türkiye'deki tüm sağlık kuruluşlarını kapsayan, güvenilir, kapsamlı ve **sürekli güncel** bir ulusal veri varlığı yaratmaktır.

Bu hedefe ulaşmak için tüm süreçler aşağıdaki ilkelere dayanmalıdır:

* **Katmanlı Güven (Tiered Trust):** Her veri kaynağına eşit güvenilmez. Resmi devlet kaynakları (Tier 1) her zaman en yüksek önceliğe sahiptir. Diğer kaynaklar (Tier 2, Tier 3) bu veriyi zenginleştirmek ve doğrulamak için kullanılır.
* **Tam Otomasyon (Full Automation):** Tüm veri toplama ve işleme adımları, insan müdahalesi gerektirmeyecek şekilde, periyodik olarak otomatik çalışmalıdır.
* **Dayanıklılık (Resilience):** Veri kazıyıcılar (scrapers), kaynak web sitelerindeki küçük HTML veya API değişikliklerine karşı dayanıklı olmalı, hata durumunda süreci durdurmak yerine bilgilendirme yapıp devam etmelidir.
* **İzlenebilirlik (Traceability):** Veritabanındaki her bir kayıt, hangi kaynaktan, ne zaman alındığı bilgisine sahip olmalıdır. Bu, veri kalitesini ve güvenilirliğini artırır.
* **Etik Veri Toplama (Ethical Scraping):** Kaynak sitelerin `robots.txt` kurallarına her zaman uyulmalı, sunuculara aşırı yük bindirecek agresif isteklerden kaçınılmalı ve yalnızca kamunun erişimine açık veriler sorumlu bir şekilde kullanılmalıdır.

---

## 2. Veri Hattı Mimarisi (ETL Pipeline)

Veri hattımız, `scripts` klasörü altında yer alan Python script'leri ile yönetilir ve GitHub Actions üzerinde periyodik olarak çalıştırılır.

1.  **Extract (Veri Çıkarma):** `fetch_*.py` script'leri, belirlenen kaynaklardan ham veriyi çeker ve `data/raw/{kaynak_adi}_{tarih}.json` formatında kaydeder.
2.  **Transform (Veri Dönüştürme):** Tek bir ana script (`process_data.py`), tüm ham verileri okur, temizler, standartlaştırır, coğrafi kodlar, tekilleştirir ve birleştirir.
3.  **Load (Veri Yükleme):** `load_to_supabase.py` script'i, işlenmiş nihai veriyi Supabase veritabanına aktarır.

---

## 3. Veri Kaynakları ve Çıkarma Stratejileri

Veri kaynaklarımız, güvenilirlik seviyelerine göre üç katmana ayrılmıştır.

### Tier 1: Resmi Devlet Kaynakları (En Yüksek Öncelik)

Bu kaynaklar, veritabanımızın temelini oluşturur ve en güvenilir bilgiyi sağlar.

* **T.C. Sağlık Bakanlığı Portalları:**
    * **Hedef:** Şehir Hastaneleri, Devlet Hastaneleri, Ağız ve Diş Sağlığı Merkezleri (ADSM), Aile Sağlığı Merkezleri (ASM), Toplum Sağlığı Merkezleri (TSM).
    * **Potansiyel Giriş Noktaları:**
        * **Kamu Hastaneleri Genel Müdürlüğü (KHGM):** `https://khgm.saglik.gov.tr` - Özellikle Şehir Hastaneleri ve bağlı Devlet Hastaneleri için duyurular ve listeler bulunur.
        * **Sağlık Bilgi Sistemleri Genel Müdürlüğü (SBSGM):** `https://sbsgm.saglik.gov.tr` - Sağlık tesisleri ile ilgili standartları ve potansiyel listeleri barındırabilir.
        * **Yönetim Hizmetleri Genel Müdürlüğü:** `https://yhgm.saglik.gov.tr` - İl Sağlık Müdürlükleri'nin listesine buradan ulaşılabilir.
    * **Strateji:**
        1.  **API Önceliği:** `sbn.saglik.gov.tr`, `e-nabiz.gov.tr` gibi portalların ve mobil uygulamaların ağ trafiği (network traffic) incelenerek gizli (undocumented) API'ler aranmalıdır. Tarayıcının "Geliştirici Araçları" (F12) -> "Ağ (Network)" sekmesi, sayfa yüklenirken yapılan `fetch/XHR` isteklerini izlemek için kullanılır. Bu API'ler, veriyi en temiz ve yapısal haliyle sağlar.
        2.  **HTML Parsing (Yedek Plan):** Doğrudan API bulunamazsa, KHGM gibi sitelerdeki hastane listelerinin bulunduğu sayfalar `requests` ve `BeautifulSoup4` ile kazınır. Script, il ve ilçe bazında arama yaparak tüm kurumları listelemelidir. JavaScript ile render edilen dinamik içerikler için `Selenium` veya `Playwright` kullanımı gerekebilir.

* **İl Sağlık Müdürlükleri (81 adet):**
    * **Hedef:** Özellikle ilçe ve köy düzeyindeki küçük birimler (ASM'ler, 112 istasyonları, Sağlık Evleri). Bu birimler genellikle merkezi listelerde yer almaz.
    * **Potansiyel Giriş Noktaları:**
        * **Ana Liste:** `https://yhgm.saglik.gov.tr/TR-6420/il-saglik-mudurlukleri.html` - Tüm il müdürlüklerinin linklerini içeren merkezi bir sayfa.
        * **URL Yapısı:** Genellikle `{il_adi}ism.saglik.gov.tr` (örn: `istanbulism.saglik.gov.tr`) formatını takip ederler.
    * **Strateji:**
        1.  **Master Scraper Geliştirme:** Ana listeden 81 ilin web sitesi URL'si alınır. Bu sitelerin çoğu benzer bir yapıya ("Kurumlarımız", "Sağlık Tesisleri" menüleri) sahip olduğundan, ortak bir kazıma mantığı geliştiren bir "master scraper" yazılır.
        2.  **İstisna Yönetimi:** Farklı bir yapıya sahip olan iller için (örn: İstanbul, Ankara, İzmir gibi büyükşehirler) bu master scraper içinde özel istisna (`try-except` blokları ve farklı CSS seçicileri) tanımlanır.

* **Yükseköğretim Kurulu (YÖK) ve Üniversiteler:**
    * **Hedef:** Üniversite ve Tıp Fakültesi Hastaneleri, Diş Hekimliği Fakülteleri, Sağlık Bilimleri Fakülteleri.
    * **Potansiyel Giriş Noktaları:**
        * **YÖK Atlas:** `https://yokatlas.yok.gov.tr` - Tıp, Diş Hekimliği gibi programları olan tüm üniversitelerin listesine ulaşmak için en güvenilir kaynaktır.
        * **Üniversite Web Siteleri:** `*.edu.tr` uzantılı siteler.
    * **Strateji:**
        1.  YÖK Atlas'tan "Tıp" programını seçerek tüm tıp fakültesi olan üniversitelerin listesi alınır.
        2.  Her üniversitenin kendi web sitesindeki "hastanelerimiz", "sağlık kampüsü", "araştırma ve uygulama merkezi" gibi bölümler hedeflenerek detaylı bilgi (adres, telefon, anabilim dalları, yönetici bilgileri) toplanır.

* **Sosyal Güvenlik Kurumu (SGK):**
    * **Hedef:** SGK ile anlaşmalı tüm özel, vakıf ve kamu sağlık hizmeti sunucuları (hastaneler, tıp merkezleri, diyaliz merkezleri, kaplıcalar vb.).
    * **Potansiyel Giriş Noktaları:**
        * **SGK Sağlık Hizmet Sunucuları Portalı:** `https://gss.sgk.gov.tr/SaglikHizmetSunuculari/pages/shsAnlasmaliKurumSorgu.faces`
    * **Strateji:**
        1.  Bu sayfa, form gönderimi ile çalışan bir yapıya sahiptir. `requests` kütüphanesi ile bu form gönderimleri simüle edilmelidir.
        2.  Tüm iller ve tüm kurum türleri (`Hastane`, `Tıp Merkezi`, `Diyaliz` vb.) için döngüsel olarak form gönderilir.
        3.  Her sorgu sonucunda dönen HTML tablosu `BeautifulSoup4` veya `pandas.read_html` ile ayrıştırılarak veriler toplanır.
        4.  İndirilebilir Excel veya PDF dosyaları varsa, bunlar öncelikli olarak kullanılır çünkü daha yapısal veri sunarlar.

### Tier 2: Kurumsal ve Sektörel Kaynaklar (Doğrulama ve Zenginleştirme)

Bu kaynaklar, Tier 1 verisini doğrulamak ve eksik bilgileri (web sitesi, logo, özel hizmetler, bölüm listeleri) tamamlamak için kullanılır.

* **Özel Hastane Zincirleri:**
    * **Hedef:** Zincire ait tüm şubelerin eksiksiz listesi, sundukları özel hizmetler, doktor listeleri ve web adresleri.
    * **Strateji:** Her bir zincirin kurumsal web sitesindeki "Hastanelerimiz", "Tıbbi Birimlerimiz" veya "İletişim" sayfaları hedeflenir. Bu siteler genellikle yapısal veri (JSON-LD, Microdata) içerir, bu da kazıma işlemini kolaylaştırır.
    * **Örnek Giriş Noktaları:**
        * **Acıbadem Sağlık Grubu:** `https://www.acibadem.com.tr/hastaneler/`
        * **Medical Park Hastaneler Grubu:** `https://www.medicalpark.com.tr/hastanelerimiz`
        * **Memorial Sağlık Grubu:** `https://www.memorial.com.tr/hastaneler`
        * **Medicana Sağlık Grubu:** `https://www.medicana.com.tr/hastanelerimiz`
        * **Dünyagöz Hastaneler Grubu:** `https://www.dunyagoz.com/subelerimiz`

* **Meslek Odaları ve Birlikler:**
    * **Hedef:** Özellikle özel muayenehaneler, poliklinikler, laboratuvarlar ve eczaneler gibi daha küçük ölçekli, Tier 1'de bulunması zor olan kurumlar.
    * **Strateji:** Bu kurumların "üye arama", "eczane bul" veya "yetkili laboratuvarlar" gibi herkese açık arama motorları kazınır. Bu sayfalar genellikle form tabanlıdır ve `requests` ile simüle edilmeleri gerekir.
    * **Örnek Giriş Noktaları:**
        * **Türk Tabipleri Birliği (TTB):** `https://www.ttb.org.tr/` (Özel Hekim Arama bölümleri hedeflenir)
        * **Türk Dişhekimleri Birliği (TDB):** `https://www.tdb.org.tr/` (Bölgesel odaların listeleri üzerinden gidilir)
        * **Tüm Eczacı İşverenler Sendikası (TEİS):** `https://www.teis.org.tr/eczane-bul` (Nöbetçi ve tüm eczaneler için)
        * **Türkiye Eczacılar Birliği (TEB):** `https://www.teb.org.tr/` (Bölgesel Eczacı Odaları listeleri üzerinden)

### Tier 3: Halka Açık Agregatörler (Keşif ve Çapraz Referans)

Bu kaynaklar, diğer katmanlarda bulunmayan yeni kurumları keşfetmek ve adres/telefon gibi bilgileri çapraz kontrol etmek için kullanılır. Verileri her zaman şüpheyle karşılanmalı ve Tier 1/2 kaynaklarla doğrulanmalıdır.

* **Wikipedia:**
    * **Strateji:** Python `wikipedia` kütüphanesi veya `BeautifulSoup` ile hedeflenir.
    * **Örnek Giriş Noktaları:**
        * `https://tr.wikipedia.org/wiki/Türkiye'deki_hastaneler_listesi`
        * İl bazlı listeler (örn: `https://tr.wikipedia.org/wiki/Kategori:İstanbul'daki_hastaneler`)

* **Online Hastane/Doktor Rehberleri:**
    * **Strateji:** Bu siteler, özellikle kullanıcı yorumları, fotoğraflar ve popüler hizmetler gibi zenginleştirici veriler için değerlidir.
    * **Örnek Giriş Noktaları:**
        * **DoktorTakvimi:** `https://www.doktortakvimi.com/hastaneler`
        * **En İyi Hekim:** `https://www.eniyihekim.com/` (İl bazlı hastane arama)
        * **TRHastane:** `https://www.trhastane.com/`

* **Harita Servisleri ve İşletme Dizinleri:**
    * **Strateji:** "hastane", "poliklinik", "eczane" gibi anahtar kelimelerle belirli coğrafi alanlarda arama yapmak için API'leri kullanılır. Bu, özellikle yeni açılan veya hiçbir yerde listelenmeyen kurumları keşfetmek için güçlü bir yöntemdir.
    * **Örnek Giriş Noktaları:**
        * **Google Maps/Places API:** En kapsamlı ve güncel POI (Point of Interest) veritabanını sunar.
        * **OpenStreetMap (OSM):** `https://www.openstreetmap.org` - Gönüllü tabanlı, tamamen açık kaynaklı bir alternatiftir. Overpass API (`https://overpass-turbo.eu/`) ile çok detaylı sorgular yapılabilir.
        * **Foursquare / Swarm:** `https://foursquare.com/` - Sosyal ve popüler mekan verileri için kullanılabilir.

---

## 4. Veri İşleme ve Standardizasyon Süreci (Transform)

Bu süreç, ham veriyi tutarlı, güvenilir ve kullanılabilir bir formata dönüştürür.

### 4.1. Standart Kurum Profili (Veri Modeli)

İşleme hattından geçen her kurum, aşağıdaki standart JSON yapısına dönüştürülmelidir. Bu yapı, Supabase'deki tablo şemasıyla doğrudan uyumludur.

```json
{
  "id": "UUID",
  "isim_standart": "Acıbadem Maslak Hastanesi",
  "tip": "Özel Hastane",
  "alt_tip": "Genel Hastane",
  "adres_yapilandirilmis": {
    "tam_adres": "Büyükdere Cad. No:40 Maslak, Sarıyer, İstanbul",
    "il": "İstanbul",
    "ilce": "Sarıyer",
    "mahalle": "Maslak",
    "posta_kodu": "34457",
    "aciklama": "Büyükdere Cad. No:40"
  },
  "iletisim": {
    "telefon_1": "+902123044444",
    "telefon_2": null,
    "faks": "+902123044445",
    "email": "info.maslak@acibadem.com",
    "website": "[https://www.acibadem.com.tr/hastane/maslak-hastanesi/](https://www.acibadem.com.tr/hastane/maslak-hastanesi/)"
  },
  "konum": {
    "type": "Point",
    "coordinates": [29.0234, 41.0987]
  },
  "kaynaklar": [
    {
      "kaynak_id": "acibadem_web",
      "kaynaktaki_isim": "Acıbadem Maslak Hastanesi",
      "url": "[https://www.acibadem.com.tr/hastaneler/acibadem-maslak-hastanesi/](https://www.acibadem.com.tr/hastaneler/acibadem-maslak-hastanesi/)",
      "son_gorulme_tarihi": "2025-08-01T03:15:00Z"
    },
    {
      "kaynak_id": "sgk_anlasmali",
      "kaynaktaki_isim": "ÖZEL ACIBADEM MASLAK HASTANESİ",
      "url": "[https://gss.sgk.gov.tr/](https://gss.sgk.gov.tr/)...",
      "son_gorulme_tarihi": "2025-08-01T03:05:00Z"
    }
  ],
  "meta_veri": {
    "yatak_kapasitesi": 220,
    "sgk_anlasmasi": true,
    "bolumler": ["Kardiyoloji", "Onkoloji", "Nöroloji"],
    "logo_url": "https://..."
  },
  "aktif": true,
  "updated_at": "2025-08-01T04:30:00Z"
}
```

### 4.2. Akıllı Tekilleştirme ve Birleştirme Mantığı (Deduplication & Merging)

Bu, veri hattının en karmaşık adımıdır ve aynı kuruma ait farklı kayıtları tek bir "altın kayıt" (golden record) haline getirmeyi amaçlar.

1.  **Ön İşleme ve Anahtar Oluşturma:**
    * Gelen her yeni kaydın `isim` ve `adres` alanları standartlaştırılır (her kelimenin baş harfi büyük olacak şekilde düzenleme, noktalama işaretlerini kaldırma, "HASTANESİ" -> "HST" gibi standart kısaltmalar kullanma).
    * Her kayıt için bir **birincil anahtar** oluşturulur: `(standart_isim, il, ilce)` üçlüsünün bir hash'i.

2.  **Eşleştirme Stratejisi (Sıralı):**
    * **Adım 1: Anahtar Eşleşmesi:** Yeni kaydın birincil anahtarı, veritabanındaki mevcut anahtarlarla karşılaştırılır. Eşleşme varsa, kayıtlar birleştirilmek üzere işaretlenir.
    * **Adım 2: Coğrafi Eşleşme:** Anahtar eşleşmesi yoksa, yeni kaydın koordinatları alınır. Veritabanında bu koordinatların **50 metrelik** yarıçapı içinde başka bir kurum olup olmadığı PostGIS'in `ST_DWithin` fonksiyonu ile sorgulanır. Eşleşme varsa, isim benzerliği kontrol edilir.
    * **Adım 3: Bulanık Metin Eşleşmesi (Fuzzy Matching):** Yukarıdaki adımlar başarısız olursa, yeni kaydın standart ismi, aynı il ve ilçedeki tüm mevcut kayıtların standart isimleriyle `fuzzywuzzy` kütüphanesi kullanılarak karşılaştırılır. `token_set_ratio` skoru **90'ın üzerindeyse** ve adres metinleri de benzerse, kayıtlar birleştirilmek üzere işaretlenir.

3.  **Birleştirme Kuralları (Alan Bazlı Güven Hiyerarşisi):**
    * İki kayıt birleştirilirken, her bir alan için hangi kaynağın verisinin kullanılacağına karar verilir.
    * **`isim_standart`:** Tier 1 (Sağlık Bak.) > Tier 1 (Üniversite) > Tier 2 (Kurumsal Web) > Tier 3
    * **`telefon` / `faks`:** Tier 2 (Kurumsal Web - genellikle en güncel) > Tier 1 (SGK) > Tier 3
    * **`website` / `email`:** Her zaman Tier 2 (Kurumsal Web) önceliklidir.
    * **`adres_yapilandirilmis`:** Tier 1 (Sağlık Bak.) verisi temel alınır, Tier 3 (Google Maps) verisi ile posta kodu gibi eksikler tamamlanır.
    * **`konum` (Koordinatlar):** Tier 3 (Google Maps API) > Tier 3 (OSM) > Diğer kaynaklardan Geocoding ile elde edilen.
    * **`meta_veri`:** Tüm kaynaklardan gelen veriler birleştirilir. Örneğin, bir kaynaktan yatak kapasitesi, diğerinden bölümler geliyorsa, ikisi de nihai kayda eklenir.

4.  **Kaynak Takibi:** Birleştirme işlemi sonucunda, nihai "altın kaydın" `kaynaklar` dizisine, bu kaydı oluşturan **tüm** kaynaklardan gelen bilgiler eklenir. Bu, veri kökenini takip etmek ve gelecekteki güncellemeleri yönetmek için hayati önem taşır.

---

## 5. Veri Yükleme Süreci (Load)

* **`load_to_supabase.py`:** İşlenmiş, temiz ve tekilleştirilmiş veri, Supabase Python istemcisi kullanılarak veritabanına aktarılır.
* **`upsert` Metodu:** `upsert=True` parametresi ile, kayıtların var olup olmadığı kontrol edilir. Varsa güncellenir, yoksa yeni kayıt olarak eklenir.

---

## 6. Otomasyon (GitHub Actions)

Tüm bu süreç, `.github/workflows/data_pipeline.yml` dosyası ile her gece otomatik olarak çalıştırılır.
