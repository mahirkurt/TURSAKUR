// Supabase Client Test Script
// Browser console'da çalıştırılabilir

async function testSupabaseConnection() {
  console.log('🧪 TURSAKUR 2.0 Frontend Supabase Testi');
  console.log('='.repeat(50));
  
  try {
    // Import from window if available, or show manual test instructions
    if (typeof window !== 'undefined' && window.supabase) {
      const { supabase } = window;
      
      console.log('1️⃣ Supabase client test...');
      
      // Test basic connection
      const { data, error } = await supabase
        .from('kuruluslar')
        .select('count', { count: 'exact' })
        .limit(1);
      
      if (error) {
        console.error('❌ Bağlantı hatası:', error.message);
        
        if (error.code === '42P01') {
          console.log('📋 Schema henüz oluşturulmamış. Lütfen şu adımları takip edin:');
          console.log('1. https://supabase.com/dashboard adresine gidin');
          console.log('2. Projenizi seçin');
          console.log('3. SQL Editor → New Query');
          console.log('4. database/schema.sql içeriğini yapıştırın');
          console.log('5. Run butonuna basın');
        }
        return false;
      }
      
      console.log('✅ Supabase bağlantısı başarılı!');
      console.log(`📊 Toplam kayıt sayısı: ${data?.[0]?.count || 0}`);
      
      // Test environment variables
      console.log('2️⃣ Environment variables test...');
      const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
      const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
      
      console.log('✅ VITE_SUPABASE_URL:', supabaseUrl ? 'Loaded' : 'Missing');
      console.log('✅ VITE_SUPABASE_ANON_KEY:', supabaseKey ? 'Loaded' : 'Missing');
      
      return true;
    } else {
      console.log('ℹ️ Supabase client bulunamadı. Manual test için:');
      console.log('1. React uygulamasını açın (http://localhost:5173)');
      console.log('2. Developer Tools → Console');
      console.log('3. Bu script\'i çalıştırın');
    }
  } catch (error) {
    console.error('❌ Test hatası:', error);
    return false;
  }
}

// Test manual query example
const testQueries = {
  async testBasicQuery() {
    const response = await fetch('/api/institutions?limit=5');
    return response.json();
  },
  
  async testSearch() {
    const response = await fetch('/api/institutions?search=hastane&limit=10');
    return response.json();
  },
  
  async testGeographicQuery() {
    const response = await fetch('/api/institutions?province=Ankara&limit=20');
    return response.json();
  }
};

console.log('🚀 Frontend Supabase Test Script yüklendi');
console.log('Çalıştırmak için: testSupabaseConnection()');

export { testSupabaseConnection, testQueries };
