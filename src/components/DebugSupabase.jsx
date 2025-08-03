import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

/**
 * Supabase Debug Component
 * Anlık veritabanı bağlantısını test eder
 */
function DebugSupabase() {
  const [status, setStatus] = useState('testing');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [count, setCount] = useState(0);

  useEffect(() => {
    async function testSupabase() {
      try {
        console.log('🔍 Supabase Debug Testi Başlatılıyor...');
        
        // 1. Önce tüm tabloları listele
        const { data: tables } = await supabase.rpc('get_tables');
        console.log('📊 Mevcut tablolar:', tables);
        
        // 2. Information schema'dan tablo adlarını al
        const { data: schemaData } = await supabase
          .from('information_schema.tables')
          .select('table_name')
          .eq('table_schema', 'public');
        
        console.log('🗃️ Schema bilgisi:', schemaData);
        
        // 3. Farklı tablo adlarını dene
        const possibleTableNames = [
          'kuruluslar',
          'turkiye_saglik_kuruluslari', 
          'saglik_kuruluslari',
          'institutions',
          'health_institutions',
          'tursakur',
          'health_data'
        ];
        
        let foundTable = null;
        
        for (const tableName of possibleTableNames) {
          try {
            const { data: testData, error: testError, count: totalCount } = await supabase
              .from(tableName)
              .select('*', { count: 'exact' })
              .limit(1);
            
            if (!testError) {
              console.log(`✅ Tablo bulundu: ${tableName}, Kayıt sayısı: ${totalCount}`);
              foundTable = { name: tableName, count: totalCount, sample: testData };
              break;
            } else {
              console.log(`❌ ${tableName} bulunamadı:`, testError.message);
            }
          } catch (err) {
            console.log(`⚠️ ${tableName} test hatası:`, err.message);
          }
        }
        
        if (foundTable) {
          setData(foundTable.sample);
          setCount(foundTable.count);
          setStatus('success');
          setError(`Doğru tablo adı: ${foundTable.name}`);
        } else {
          setStatus('error');
          setError('Hiçbir tablo bulunamadı!');
        }
        
      } catch (err) {
        console.error('❌ Exception:', err);
        setError(err.message);
        setStatus('error');
      }
    }
    
    testSupabase();
  }, []);
  
  if (status === 'testing') {
    return (
      <div style={{ 
        position: 'fixed', 
        top: 10, 
        right: 10, 
        background: '#yellow', 
        padding: '10px', 
        borderRadius: '5px',
        zIndex: 9999,
        fontSize: '12px'
      }}>
        🔍 Supabase Test Ediliyor...
      </div>
    );
  }
  
  if (status === 'error') {
    return (
      <div style={{ 
        position: 'fixed', 
        top: 10, 
        right: 10, 
        background: '#ffcdd2', 
        padding: '10px', 
        borderRadius: '5px',
        zIndex: 9999,
        fontSize: '12px',
        maxWidth: '300px'
      }}>
        ❌ Supabase Hatası: {error}
      </div>
    );
  }
  
  return (
    <div style={{ 
      position: 'fixed', 
      top: 10, 
      right: 10, 
      background: '#c8e6c9', 
      padding: '10px', 
      borderRadius: '5px',
      zIndex: 9999,
      fontSize: '12px'
    }}>
      ✅ Supabase OK: {count} toplam kurum, {data?.length} test verisi
    </div>
  );
}

export default DebugSupabase;
