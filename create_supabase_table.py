"""
TURSAKUR 2.0 - Supabase Table Creator
Creates the health_facilities table in Supabase PostgreSQL
"""
import os
from supabase import create_client
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_table():
    """Create health_facilities table in Supabase"""
    # Load environment
    load_dotenv()
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Use service role for DDL
    
    if not url or not key:
        logger.error("Missing Supabase credentials")
        return False
    
    supabase = create_client(url, key)
    
    # SQL to create table
    create_table_sql = """
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_health_facilities_province ON health_facilities(province);
CREATE INDEX IF NOT EXISTS idx_health_facilities_type ON health_facilities(facility_type);
CREATE INDEX IF NOT EXISTS idx_health_facilities_active ON health_facilities(is_active);

-- RLS Policies
ALTER TABLE health_facilities ENABLE ROW LEVEL SECURITY;

-- Allow public read access
DROP POLICY IF EXISTS "Allow public read access" ON health_facilities;
CREATE POLICY "Allow public read access" ON health_facilities
    FOR SELECT USING (true);
"""
    
    try:
        # Execute the SQL using rpc call
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        logger.info("✅ Table created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create table: {e}")
        # Try alternative method
        try:
            # Split into individual statements
            statements = [
                "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"",
                """CREATE TABLE IF NOT EXISTS health_facilities (
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
                )""",
                "CREATE INDEX IF NOT EXISTS idx_health_facilities_province ON health_facilities(province)",
                "CREATE INDEX IF NOT EXISTS idx_health_facilities_type ON health_facilities(facility_type)",
                "CREATE INDEX IF NOT EXISTS idx_health_facilities_active ON health_facilities(is_active)",
                "ALTER TABLE health_facilities ENABLE ROW LEVEL SECURITY",
                "DROP POLICY IF EXISTS \"Allow public read access\" ON health_facilities",
                "CREATE POLICY \"Allow public read access\" ON health_facilities FOR SELECT USING (true)"
            ]
            
            for stmt in statements:
                try:
                    result = supabase.rpc('exec_sql', {'sql': stmt}).execute()
                    logger.info(f"✅ Executed: {stmt[:50]}...")
                except Exception as stmt_error:
                    logger.warning(f"⚠️ Statement failed: {stmt_error}")
            
            return True
        except Exception as e2:
            logger.error(f"❌ Alternative method failed: {e2}")
            return False

if __name__ == "__main__":
    create_table()
