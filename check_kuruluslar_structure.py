#!/usr/bin/env python3
# Check kuruluslar table structure

import json
from supabase import create_client, Client

# Supabase config
url = 'https://moamwmxcpgjvyyawlygw.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vYW13bXhjcGdqdnl5YXdseWd3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwMzA1NzgsImV4cCI6MjA2OTYwNjU3OH0.w88NfzOopSYo8Q23ypWaknnaZcSXnV0WPtiE2-ePGfU'

supabase: Client = create_client(url, key)

# Check table structure and data
try:
    result = supabase.table('kuruluslar').select('*').limit(3).execute()
    print(f'✅ kuruluslar tablosu - {len(result.data)} kayıt bulundu')
    
    if result.data:
        print('\n📋 Tablo Yapısı:')
        first_record = result.data[0]
        for key, value in first_record.items():
            print(f'  {key}: {type(value).__name__} = {value}')
        
        print('\n🔍 İlk 3 Kayıt:')
        for i, record in enumerate(result.data, 1):
            print(f'{i}. {record.get("name", record.get("kurum_adi", "Unknown"))} - {record.get("province", record.get("il", "Unknown"))}')
            
except Exception as e:
    print(f'❌ Hata: {e}')
