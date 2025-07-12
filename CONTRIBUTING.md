# Katkıda Bulunma Rehberi

Bu rehber, Türkiye Sağlık Kuruluşları Açık Veritabanı projesine nasıl katkıda bulunabileceğinizi açıklar.

## 🎯 Katkı Türleri

### 1. Veri Ekleme/Düzeltme
- Yeni sağlık kurumu bilgileri ekleme
- Mevcut verilerdeki hataları düzeltme
- Eksik bilgileri tamamlama

### 2. Kod Geliştirme
- Veri işleme betiklerini iyileştirme
- Yeni özellikler ekleme
- Hata düzeltmeleri

### 3. Dokümantasyon
- README dosyasını iyileştirme
- Kod dokümantasyonu ekleme
- Kullanım örnekleri oluşturma

## 📋 Veri Ekleme Kuralları

### Veri Formatı
Tüm veriler JSON formatında olmalıdır ve şu şemaya uygun olmalıdır:

```json
{
  "kurum_id": "TR-[il_kodu]-[tip_kodu]-[sira_no]",
  "kurum_adi": "Tam resmi kurum adı",
  "kurum_tipi": "Standart kategori (aşağıdaki listeden)",
  "il_kodu": 1-81,
  "il_adi": "İl adı",
  "ilce_adi": "İlçe adı",
  "adres": "Tam adres",
  "telefon": "+90XXXXXXXXXX",
  "koordinat_lat": 0.000000,
  "koordinat_lon": 0.000000,
  "web_sitesi": "https://example.com",
  "veri_kaynagi": "Kaynak açıklaması",
  "son_guncelleme": "YYYY-MM-DD"
}
```

### Kurum Tipleri (Standart Liste)
- Devlet Hastanesi
- Üniversite Hastanesi
- Eğitim ve Araştırma Hastanesi
- Özel Hastane
- Aile Sağlığı Merkezi
- Toplum Sağlığı Merkezi
- Ağız ve Diş Sağlığı Merkezi
- Özel Poliklinik
- Özel Tıp Merkezi
- Diyaliz Merkezi
- Fizik Tedavi ve Rehabilitasyon Merkezi
- Ambulans İstasyonu

### Veri Kaynakları
Güvenilir kaynakları kullanın:
- İl/İlçe Sağlık Müdürlükleri resmi siteleri
- Sağlık Bakanlığı resmi verileri
- Kurum resmi web siteleri
- Resmi telefon rehberleri

## 🔄 Katkı Süreci

### 1. Issue Oluşturma
Yeni bir katkı yapmadan önce bir issue oluşturun:
- Hangi veriyi eklediğinizi/değiştirdiğinizi açıklayın
- Kaynak bilgilerini belirtin
- Varsa ekran görüntüleri ekleyin

### 2. Fork ve Branch
```bash
# Projeyi fork edin
# Yeni bir branch oluşturun
git checkout -b veri-guncelleme-istanbul
```

### 3. Veri Ekleme/Düzeltme
- Ham verileri `data/raw/` klasörüne ekleyin
- Dosya adını anlaşılır yapın: `istanbul_devlet_hastaneleri.json`
- Veri formatına uygun olduğundan emin olun

### 4. Test Etme
```bash
# Veri doğrulama betiğini çalıştırın
python scripts/validate_data.py

# Temizleme ve birleştirme betiğini test edin
python scripts/process_data.py
```

### 5. Pull Request
- Açıklayıcı bir başlık yazın
- Değişiklikleri detaylı açıklayın
- Hangi kaynakları kullandığınızı belirtin
- Test sonuçlarını ekleyin

## ✅ PR Kontrolü

Pull request'iniz şu kriterleri karşılamalıdır:

### Veri Kalitesi
- [ ] Tüm zorunlu alanlar doldurulmuş
- [ ] Koordinat bilgileri doğru
- [ ] Telefon numaraları standart formatta
- [ ] Kurum tipi standart listeden seçilmiş

### Format Uyumu
- [ ] JSON formatı geçerli
- [ ] Şemaya uygun
- [ ] Encoding UTF-8

### Kaynak Güvenilirliği
- [ ] Güvenilir kaynak belirtilmiş
- [ ] Veri güncel (son 6 ay içinde)
- [ ] Doğrulanabilir

## 🛠️ Geliştirme Ortamı

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Geliştirme Araçları
- Python 3.8+
- Git
- VS Code (önerilen)

### Kod Standartları
- PEP 8 kod stili
- Type hints kullanımı
- Docstring'ler
- Unit testler

## 📞 İletişim

Sorularınız için:
- Issue açın
- GitHub Discussions kullanın
- E-posta: [proje_email@example.com]

## 🙏 Teşekkürler

Her türlü katkınız için şimdiden teşekkür ederiz! Birlikte Türkiye'nin en kapsamlı sağlık kuruluşları veritabanını oluşturalım.
