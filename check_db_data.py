#!/usr/bin/env python3
"""Veritabanı veri kontrolü"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    supabase = create_client(
        'https://moamwmxcpgjvyyawlygw.supabase.co',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vYW13bXhjcGdqdnl5YXdseWd3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwMzA1NzgsImV4cCI6MjA2OTYwNjU3OH0.w88NfzOopSYo8Q23ypWaknnaZcSXnV0WPtiE2-ePGfU'
    )
    
    try:
        # Count query  
        result = supabase.table('kuruluslar').select('*', count='exact').limit(3).execute()
        print(f'✅ Toplam kuruluş: {result.count}')
        
        if result.data:
            print(f"📝 {len(result.data)} örnek kayıt:")
            for i, record in enumerate(result.data):
                print(f"   {i+1}. {record['isim_standart']} - {record['adres_yapilandirilmis']['il']}")
                
        # Test new format query
        adres_result = supabase.table('kuruluslar').select('adres_yapilandirilmis').limit(1).execute()
        if adres_result.data:
            print(f"📍 Adres yapısı: {adres_result.data[0]['adres_yapilandirilmis']}")
                
    except Exception as e:
        print(f'❌ Hata: {e}')

if __name__ == "__main__":
    main()
