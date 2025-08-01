# 🚀 TURSAKUR 2.0 Supabase Entegrasyon Testi

Bu dokümanda Supabase entegrasyonlarını test etmek için gereken adımları bulacaksınız.

## 📋 Ön Gereksinimler

✅ React uygulaması çalışıyor (http://localhost:5173)  
✅ Environment variables (.env) yapılandırıldı  
✅ Python ve Node.js bağımlılıkları yüklendi  
❓ **Supabase veritabanı schema'sı oluşturulacak**

## 🗄️ 1. Adım: Supabase Schema Oluşturma

### A. Supabase Dashboard'a Erişim
1. [https://supabase.com/dashboard](https://supabase.com/dashboard) adresine gidin
2. Giriş yapın ve projenizi seçin
3. Proje ID'niz: `moamwmxcpgjvyyawlygw`

### B. SQL Editor'da Schema Çalıştırma
1. Sol menüden **"SQL Editor"** seçin
2. **"New Query"** butonuna basın
3. Aşağıdaki komutu çalıştırarak dosya içeriğini görüntüleyin:

```bash
# Terminal'de şu komutu çalıştırın:
cat database/schema.sql
```

4. `database/schema.sql` dosyasının **TÜM İÇERİĞİNİ** kopyalayın
5. SQL Editor'a yapıştırın
6. **"RUN"** (Çalıştır) butonuna basın
7. Başarılı mesajını bekleyin ✅

### C. Schema Doğrulama
```sql
-- Bu sorguyu SQL Editor'da çalıştırarak kontrol edin:
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'kuruluslar';
```

Sonuç: `kuruluslar` tablosu görünmelidir.

## 🧪 2. Adım: Python Backend Test

Schema oluşturduktan sonra Python entegrasyonunu test edin:

```bash
# 1. Bağlantı testi
python scripts/supabase_client.py

# 2. Schema testi ve örnek veri ekleme
python scripts/test_schema.py

# 3. Başarılıysa çıktı şu şekilde olacak:
# ✅ Veritabanı bağlantısı başarılı!
# ✅ 3/3 örnek kuruluş eklendi
# ✅ Toplam kayıt: 3
```

## 🌐 3. Adım: Frontend React Test

### A. Browser Console Test
1. http://localhost:5173 adresini açın
2. Developer Tools → Console (F12)
3. Şu komutu yazın:

```javascript
// Supabase client test
fetch('/test-supabase.js')
  .then(r => r.text())
  .then(eval);

// Sonra test fonksiyonunu çalıştırın:
testSupabaseConnection();
```

### B. React Hooks Test
Ana sayfada aşağıdaki fonksiyonları test edin:

- ✅ **Arama çubuğu**: Kuruluş ismi arayın
- ✅ **Filtreleme**: İl/ilçe/tip filtreleyin  
- ✅ **Harita görünümü**: /map sayfasına gidin
- ✅ **İstatistikler**: Ana sayfada sayıları kontrol edin

## 📊 4. Adım: Gerçek Veri Yükleme

Test verileri başarılıysa gerçek verileri yükleyin:

```bash
# Mevcut JSON verilerini Supabase'e yükle
python scripts/load_to_supabase.py

# Bu işlem şunları yapacak:
# - data/ klasöründeki JSON dosyalarını okur
# - Veri kalitesi kontrolü yapar
# - Duplikat kontrolü yapar
# - Toplu olarak Supabase'e aktarır
# - Migrasyon raporu oluşturur
```

## 🗺️ 5. Adım: Coğrafi Özellikler Test

### PostGIS Fonksiyon Testi
```sql
-- SQL Editor'da bu sorguyu çalıştırın:
SELECT 
  isim_standart,
  ST_AsText(konum) as koordinatlar,
  adres_yapilandirilmis->>'il' as il
FROM kuruluslar 
WHERE konum IS NOT NULL 
LIMIT 5;
```

### Mesafe Hesaplama Testi
```sql
-- Ankara'ya en yakın 10 kuruluş
SELECT 
  isim_standart,
  adres_yapilandirilmis->>'il' as il,
  ST_Distance(
    konum, 
    ST_SetSRID(ST_Point(32.8597, 39.9334), 4326)
  ) as mesafe_metre
FROM kuruluslar 
WHERE konum IS NOT NULL
ORDER BY mesafe_metre
LIMIT 10;
```

## 🔍 6. Adım: Performans Test

### A. Arama Performansı
```bash
# Terminal'de curl ile API test
curl "http://localhost:5173/api/institutions?search=hastane&limit=100"
```

### B. Harita Performansı
1. http://localhost:5173/map sayfasını açın
2. Developer Tools → Network sekmesi
3. Haritayı hareket ettirin ve API çağrılarını gözlemleyin
4. Response sürelerini kontrol edin (< 500ms ideal)

## ✅ Başarı Kriterleri

Test başarılı sayılır eğer:

- [ ] Supabase bağlantısı çalışıyor
- [ ] Schema doğru oluşturuldu (kuruluslar tablosu var)
- [ ] Python scripts hatasız çalışıyor
- [ ] React uygulaması veri çekiyor
- [ ] Arama ve filtreleme fonksiyon ediyor
- [ ] Harita doğru konumları gösteriyor
- [ ] Coğrafi sorgular çalışıyor

## 🚨 Hata Çözümleri

### Hata: "relation public.kuruluslar does not exist"
**Çözüm**: Schema henüz oluşturulmamış. Adım 1'i tekrarlayın.

### Hata: "Invalid API key"
**Çözüm**: `.env` dosyasındaki SUPABASE_KEY'i kontrol edin.

### Hata: "PostGIS extension not found"
**Çözüm**: Supabase'de PostGIS eklentisi etkinleştirin:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Hata: React uygulaması veri göstermiyor
**Çözüm**: 
1. Browser console'da hata mesajlarını kontrol edin
2. Network sekmesinde API çağrılarını inceleyin
3. Environment variables'ların doğru yüklendiğini kontrol edin

## 📞 Test Sonrası

Test tamamlandıktan sonra:

1. **Başarılıysa**: Production deploy için hazır
2. **Başarısızsa**: Hata mesajlarını paylaşın

Test sonuçlarını şu formatta rapor edin:
```
✅/❌ Supabase Bağlantı
✅/❌ Schema Oluşturma  
✅/❌ Python Backend
✅/❌ React Frontend
✅/❌ Coğrafi Özellikler
✅/❌ Performans
```
