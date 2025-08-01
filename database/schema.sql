-- TURSAKUR Database Schema for Supabase PostgreSQL with PostGIS
-- Bu schema Türkiye sağlık kuruluşları veritabanı için tasarlanmıştır

-- Enable PostGIS extension for geographic data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create kuruluslar (health institutions) table
CREATE TABLE IF NOT EXISTS public.kuruluslar (
    kurum_id VARCHAR(50) PRIMARY KEY,
    kurum_adi VARCHAR(500) NOT NULL,
    kurum_tipi VARCHAR(100) NOT NULL,
    il_kodu INTEGER,
    il_adi VARCHAR(100),
    ilce_adi VARCHAR(100),
    adres TEXT,
    telefon VARCHAR(20),
    koordinat_lat DECIMAL(10,8),
    koordinat_lon DECIMAL(11,8),
    web_sitesi VARCHAR(500),
    veri_kaynagi VARCHAR(200),
    son_guncelleme DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- PostGIS geometry column for spatial queries
    location GEOMETRY(POINT, 4326)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_kuruluslar_kurum_tipi ON public.kuruluslar(kurum_tipi);
CREATE INDEX IF NOT EXISTS idx_kuruluslar_il_adi ON public.kuruluslar(il_adi);
CREATE INDEX IF NOT EXISTS idx_kuruluslar_ilce_adi ON public.kuruluslar(ilce_adi);
CREATE INDEX IF NOT EXISTS idx_kuruluslar_kurum_adi ON public.kuruluslar(kurum_adi);

-- Create spatial index for geography-based queries
CREATE INDEX IF NOT EXISTS idx_kuruluslar_location ON public.kuruluslar USING GIST (location);

-- Function to automatically update location geometry from lat/lon
CREATE OR REPLACE FUNCTION update_location_geometry()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.koordinat_lat IS NOT NULL AND NEW.koordinat_lon IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.koordinat_lon, NEW.koordinat_lat), 4326);
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update location when coordinates change
DROP TRIGGER IF EXISTS trigger_update_location ON public.kuruluslar;
CREATE TRIGGER trigger_update_location
    BEFORE INSERT OR UPDATE ON public.kuruluslar
    FOR EACH ROW
    EXECUTE FUNCTION update_location_geometry();

-- Enable Row Level Security (RLS) for public access
ALTER TABLE public.kuruluslar ENABLE ROW LEVEL SECURITY;

-- Create policy for public read access (anonymous users can read data)
CREATE POLICY "Public read access" ON public.kuruluslar
    FOR SELECT USING (true);

-- Create policy for authenticated users to insert/update (if needed later)
CREATE POLICY "Authenticated users can insert" ON public.kuruluslar
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can update" ON public.kuruluslar
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Create a view for easy querying with distance calculations
CREATE OR REPLACE VIEW public.kuruluslar_with_distance AS
SELECT 
    *,
    -- Add helper columns for geographic queries
    ST_X(location) as lon,
    ST_Y(location) as lat
FROM public.kuruluslar;

-- Grant permissions for anonymous access (public read)
GRANT SELECT ON public.kuruluslar TO anon;
GRANT SELECT ON public.kuruluslar_with_distance TO anon;

-- Grant full access to authenticated users
GRANT ALL ON public.kuruluslar TO authenticated;
GRANT ALL ON public.kuruluslar_with_distance TO authenticated;

-- Function for geographic search within radius (in meters)
CREATE OR REPLACE FUNCTION public.search_within_radius(
    center_lat DECIMAL,
    center_lon DECIMAL,
    radius_meters INTEGER DEFAULT 10000
)
RETURNS TABLE(
    kurum_id VARCHAR(50),
    kurum_adi VARCHAR(500),
    kurum_tipi VARCHAR(100),
    il_adi VARCHAR(100),
    ilce_adi VARCHAR(100),
    adres TEXT,
    telefon VARCHAR(20),
    koordinat_lat DECIMAL(10,8),
    koordinat_lon DECIMAL(11,8),
    web_sitesi VARCHAR(500),
    distance_meters DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        k.kurum_id,
        k.kurum_adi,
        k.kurum_tipi,
        k.il_adi,
        k.ilce_adi,
        k.adres,
        k.telefon,
        k.koordinat_lat,
        k.koordinat_lon,
        k.web_sitesi,
        ROUND(ST_Distance(
            k.location,
            ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography
        )::DECIMAL, 2) as distance_meters
    FROM public.kuruluslar k
    WHERE k.location IS NOT NULL
    AND ST_DWithin(
        k.location::geography,
        ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography,
        radius_meters
    )
    ORDER BY distance_meters;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION public.search_within_radius TO anon;
GRANT EXECUTE ON FUNCTION public.search_within_radius TO authenticated;

-- Add some sample data for testing (optional, will be replaced with real data)
INSERT INTO public.kuruluslar (
    kurum_id, kurum_adi, kurum_tipi, il_kodu, il_adi, ilce_adi, 
    adres, telefon, koordinat_lat, koordinat_lon, web_sitesi, 
    veri_kaynagi, son_guncelleme
) VALUES (
    'TR-06-DEV-001',
    'Test Hastanesi',
    'Devlet Hastanesi',
    06,
    'Ankara',
    'Çankaya',
    'Test Mahallesi, Test Caddesi No:1, Çankaya/Ankara',
    '+905551234567',
    39.9334,
    32.8597,
    'https://test-hastanesi.gov.tr',
    'Test Data',
    CURRENT_DATE
) ON CONFLICT (kurum_id) DO NOTHING;

-- Create indexes after data insertion for better performance
ANALYZE public.kuruluslar;

-- Display schema creation results
SELECT 
    'Schema başarıyla oluşturuldu!' as status,
    COUNT(*) as test_record_count
FROM public.kuruluslar;
