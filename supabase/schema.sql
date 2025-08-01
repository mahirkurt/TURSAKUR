-- TURSAKUR 2.0 - Supabase Database Schema
-- Sağlık kuruluşları için PostgreSQL tabloları

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Health facilities table
CREATE TABLE IF NOT EXISTS health_facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    facility_type TEXT,
    province TEXT NOT NULL,
    district TEXT,
    address TEXT,
    phone TEXT,
    website TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    sources TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_health_facilities_province ON health_facilities(province);
CREATE INDEX IF NOT EXISTS idx_health_facilities_type ON health_facilities(facility_type);
CREATE INDEX IF NOT EXISTS idx_health_facilities_location ON health_facilities(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_health_facilities_active ON health_facilities(is_active);
CREATE INDEX IF NOT EXISTS idx_health_facilities_name ON health_facilities USING gin(to_tsvector('turkish', name));
CREATE INDEX IF NOT EXISTS idx_health_facilities_address ON health_facilities USING gin(to_tsvector('turkish', address));

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_health_facilities_updated_at 
    BEFORE UPDATE ON health_facilities 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) policies
ALTER TABLE health_facilities ENABLE ROW LEVEL SECURITY;

-- Allow anonymous read access
CREATE POLICY "Allow anonymous read access" ON health_facilities
    FOR SELECT USING (true);

-- Only authenticated users can insert/update/delete
CREATE POLICY "Allow authenticated users to insert" ON health_facilities
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to update" ON health_facilities
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to delete" ON health_facilities
    FOR DELETE USING (auth.role() = 'authenticated');

-- Statistics view for easy querying
CREATE OR REPLACE VIEW health_facilities_stats AS
SELECT 
    COUNT(*) as total_facilities,
    COUNT(*) FILTER (WHERE latitude IS NOT NULL AND longitude IS NOT NULL) as with_coordinates,
    COUNT(*) FILTER (WHERE phone IS NOT NULL) as with_phone,
    COUNT(*) FILTER (WHERE website IS NOT NULL) as with_website,
    COUNT(DISTINCT province) as total_provinces,
    COUNT(DISTINCT facility_type) as total_types
FROM health_facilities 
WHERE is_active = true;

-- Province summary view
CREATE OR REPLACE VIEW facilities_by_province AS
SELECT 
    province,
    COUNT(*) as facility_count,
    COUNT(DISTINCT facility_type) as type_count,
    COUNT(*) FILTER (WHERE latitude IS NOT NULL AND longitude IS NOT NULL) as with_coordinates
FROM health_facilities 
WHERE is_active = true
GROUP BY province
ORDER BY facility_count DESC;

-- Facility type summary view
CREATE OR REPLACE VIEW facilities_by_type AS
SELECT 
    facility_type,
    COUNT(*) as facility_count,
    COUNT(DISTINCT province) as province_count,
    COUNT(*) FILTER (WHERE latitude IS NOT NULL AND longitude IS NOT NULL) as with_coordinates
FROM health_facilities 
WHERE is_active = true
GROUP BY facility_type
ORDER BY facility_count DESC;
