#!/usr/bin/env python3
# Test Supabase connection and table

import json
from supabase import create_client, Client

# Supabase config
url = 'https://moamwmxcpgjvyyawlygw.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vYW13bXhjcGdqdnl5YXdseWd3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwMzA1NzgsImV4cCI6MjA2OTYwNjU3OH0.w88NfzOopSYo8Q23ypWaknnaZcSXnV0WPtiE2-ePGfU'

supabase: Client = create_client(url, key)

# Test table exists
try:
    result = supabase.table('health_facilities').select('id,name,facility_type,province').limit(5).execute()
    print(f'✅ health_facilities tablosu mevcut - {len(result.data)} kayıt bulundu')
    print('İlk 3 kayıt:')
    for record in result.data[:3]:
        print(f'  - {record["name"]} ({record["facility_type"]}) - {record["province"]}')
except Exception as e:
    print(f'❌ health_facilities tablosu hatası: {e}')

# Test wrong table name (kuruluslar)
try:
    result2 = supabase.table('kuruluslar').select('*').limit(1).execute()
    print(f'✅ kuruluslar tablosu da mevcut - {len(result2.data)} kayıt')
except Exception as e:
    print(f'❌ kuruluslar tablosu bulunamadı: {e}')
