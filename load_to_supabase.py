#!/usr/bin/env python3
"""
TURSAKUR 2.0 - Supabase Data Loader
Loads processed health facility data to Supabase PostgreSQL database.
"""
import json
import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials in environment variables")
    
    return supabase_url, supabase_key

def initialize_supabase():
    """Initialize Supabase client"""
    try:
        url, key = load_environment()
        supabase: Client = create_client(url, key)
        logger.info(f"✅ Supabase client initialized: {url}")
        return supabase
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase: {e}")
        raise

def create_table_if_not_exists(supabase):
    """Create health_facilities table if it doesn't exist"""
    schema_sql = """
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
    """
    
    try:
        result = supabase.rpc('exec_sql', {'sql': schema_sql}).execute()
        logger.info("✅ Database schema created/verified")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Schema creation failed (might already exist): {e}")
        return False

def load_processed_data():
    """Load processed health facility data"""
    data_file = Path('data/turkiye_saglik_kuruluslari_merged.json')
    
    if not data_file.exists():
        logger.warning("❌ Processed data file not found. Running data processing first...")
        os.system('python process_data.py')
        
        if not data_file.exists():
            raise FileNotFoundError("Could not find or create processed data file")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"📄 Loaded {len(data)} health facilities from processed data")
    return data

def transform_for_supabase(facility):
    """Transform facility data for Supabase insertion"""
    # Clean the data
    transformed = {
        'name': facility.get('name', '').strip(),
        'facility_type': facility.get('facility_type', 'Unknown'),
        'province': facility.get('province', '').strip(),
        'district': facility.get('district', '').strip() if facility.get('district') else None,
        'address': facility.get('address', '').strip() if facility.get('address') else None,
        'phone': facility.get('phone', '').strip() if facility.get('phone') else None,
        'website': facility.get('website', '').strip() if facility.get('website') else None,
        'latitude': float(facility['latitude']) if facility.get('latitude') else None,
        'longitude': float(facility['longitude']) if facility.get('longitude') else None,
        'sources': facility.get('sources', []),
        'is_active': True
    }
    
    # Remove empty strings
    for key, value in list(transformed.items()):
        if value == '':
            transformed[key] = None
    
    return transformed

def upload_data_batch(supabase, batch_data):
    """Upload a batch of data to Supabase"""
    try:
        result = supabase.table('health_facilities').insert(batch_data).execute()
        return len(result.data) if result.data else 0
    except Exception as e:
        logger.error(f"❌ Batch upload failed: {e}")
        return 0

def upload_to_supabase(supabase, facilities):
    """Upload all facilities to Supabase with batch processing"""
    batch_size = 100
    total_uploaded = 0
    total_facilities = len(facilities)
    
    logger.info(f"🚀 Starting upload of {total_facilities} facilities...")
    
    # Clear existing data
    try:
        result = supabase.table('health_facilities').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        logger.info("🗑️ Cleared existing data")
    except Exception as e:
        logger.warning(f"⚠️ Could not clear existing data: {e}")
    
    for i in range(0, total_facilities, batch_size):
        batch = facilities[i:i + batch_size]
        batch_data = [transform_for_supabase(facility) for facility in batch]
        
        uploaded = upload_data_batch(supabase, batch_data)
        total_uploaded += uploaded
        
        progress = ((i + len(batch)) / total_facilities) * 100
        logger.info(f"📊 Progress: {progress:.1f}% ({total_uploaded}/{total_facilities} facilities uploaded)")
    
    return total_uploaded

def verify_upload(supabase):
    """Verify the uploaded data"""
    try:
        # Count total facilities
        count_result = supabase.table('health_facilities').select('*', count='exact').execute()
        total_count = count_result.count
        
        # Get sample facilities
        sample_result = supabase.table('health_facilities').select('*').limit(5).execute()
        sample_facilities = sample_result.data
        
        # Get statistics by province
        stats_result = supabase.table('health_facilities').select('province').execute()
        provinces = {}
        for facility in stats_result.data:
            province = facility['province']
            provinces[province] = provinces.get(province, 0) + 1
        
        logger.info(f"✅ Upload verification:")
        logger.info(f"   Total facilities: {total_count}")
        logger.info(f"   Provinces covered: {len(provinces)}")
        logger.info(f"   Top provinces: {sorted(provinces.items(), key=lambda x: x[1], reverse=True)[:5]}")
        
        if sample_facilities:
            logger.info(f"   Sample facility: {sample_facilities[0]['name']} in {sample_facilities[0]['province']}")
        
        return total_count
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return 0

def main():
    """Main execution function"""
    try:
        logger.info("🚀 TURSAKUR 2.0 - Starting Supabase data upload")
        
        # Initialize Supabase
        supabase = initialize_supabase()
        
        # Create table schema
        create_table_if_not_exists(supabase)
        
        # Load processed data
        facilities = load_processed_data()
        
        # Upload to Supabase
        uploaded_count = upload_to_supabase(supabase, facilities)
        
        # Verify upload
        verified_count = verify_upload(supabase)
        
        if verified_count > 0:
            logger.info(f"🎉 SUCCESS! {verified_count} health facilities uploaded to Supabase")
            logger.info(f"🌐 Your TURSAKUR app is now connected to live data!")
        else:
            logger.error("❌ Upload verification failed")
            
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise

if __name__ == "__main__":
    main()
