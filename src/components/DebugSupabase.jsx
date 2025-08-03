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
        
        // 1. Connection Test
        const { data: testData, error: testError, count: totalCount } = await supabase
          .from('turkiye_saglik_kuruluslari')
          .select('id, isim_standart, tip, adres_yapilandirilmis', { count: 'exact' })
          .eq('aktif', true)
          .limit(5);
        
        if (testError) {
          console.error('❌ Supabase Error:', testError);
          setError(testError.message);
          setStatus('error');
          return;
        }
        
        console.log('✅ Supabase Success:', { data: testData, count: totalCount });
        setData(testData);
        setCount(totalCount);
        setStatus('success');
        
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
