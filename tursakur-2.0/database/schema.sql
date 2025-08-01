-- TURSAKUR 2.0 - Supabase Veritabanı Şeması
-- Talimatnameler/mimari.md'ye göre hazırlanmıştır

-- PostGIS eklentisini etkinleştir
CREATE EXTENSION IF NOT EXISTS postgis;

-- Sağlık kuruluşları için ana tablo
CREATE TABLE public.kuruluslar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Temel Bilgiler
    isim_standart TEXT NOT NULL,
    tip TEXT, -- 'Devlet Hastanesi', 'Özel Hastane', 'Üniversite Hastanesi', 'ASM' vb.
    alt_tip TEXT,
    
    -- Adres Bilgileri (Yapılandırılmış)
    adres_yapilandirilmis JSONB,
    
    -- İletişim Bilgileri
    iletisim JSONB,
    
    -- Coğrafi Veri (En Önemli Kısım)
    konum GEOMETRY(Point, 4326), -- 4326: GPS koordinat sistemi (WGS 84)
    
    -- Veri Kaynağı ve İzlenebilirlik
    kaynaklar JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    -- Meta Veri
    meta_veri JSONB DEFAULT '{}'::jsonb,
    
    -- Durum
    aktif BOOLEAN DEFAULT true
);

-- Coğrafi sorguları hızlandırmak için bir GIST indeksi oluşturulur.
CREATE INDEX idx_kuruluslar_konum ON public.kuruluslar USING gist (konum);

-- Arama performansını artırmak için metin alanlarına indeksler
CREATE INDEX idx_kuruluslar_isim ON public.kuruluslar USING gin (to_tsvector('turkish', isim_standart));

-- JSON alanlarında arama için indeksler
CREATE INDEX idx_kuruluslar_il ON public.kuruluslar USING gin ((adres_yapilandirilmis->'il'));
CREATE INDEX idx_kuruluslar_ilce ON public.kuruluslar USING gin ((adres_yapilandirilmis->'ilce'));
CREATE INDEX idx_kuruluslar_tip ON public.kuruluslar USING gin (to_tsvector('turkish', tip));

-- Updated_at trigger for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_kuruluslar_updated_at BEFORE UPDATE
    ON public.kuruluslar FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Row Level Security (RLS) politikaları
ALTER TABLE public.kuruluslar ENABLE ROW LEVEL SECURITY;

-- Herkese okuma izni ver (public read access)
CREATE POLICY "Kuruluslar okuma erişimi" ON public.kuruluslar
    FOR SELECT USING (true);

-- Sadece authenticated kullanıcılar yazabilir (future-proofing için)
CREATE POLICY "Kuruluslar yazma erişimi" ON public.kuruluslar
    FOR ALL USING (auth.role() = 'authenticated');

-- Örnek veri yapısı yorumu
COMMENT ON TABLE public.kuruluslar IS 'TURSAKUR 2.0 - Türkiye Sağlık Kuruluşları Ana Tablosu';
COMMENT ON COLUMN public.kuruluslar.isim_standart IS 'Standartlaştırılmış kurum ismi';
COMMENT ON COLUMN public.kuruluslar.adres_yapilandirilmis IS 'JSON: {tam_adres, il, ilce, mahalle, posta_kodu, aciklama}';
COMMENT ON COLUMN public.kuruluslar.iletisim IS 'JSON: {telefon_1, telefon_2, faks, email, website}';
COMMENT ON COLUMN public.kuruluslar.konum IS 'PostGIS Point geometry - GPS koordinatları';
COMMENT ON COLUMN public.kuruluslar.kaynaklar IS 'JSON Array: Veri kaynaklarının izlenebilirlik bilgileri';
COMMENT ON COLUMN public.kuruluslar.meta_veri IS 'JSON: {yatak_kapasitesi, sgk_anlasmasi, bolumler, logo_url}';
