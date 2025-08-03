import React, { useState } from 'react';
import { 
  runFullSKRSIntegration, 
  fetchSKRSInstitutions,
  fetchSKRSProvinces,
  fetchSKRSSpecialties 
} from '../services/skrsService';

/**
 * SKRS Entegrasyon Yönetici Paneli
 * Sağlık Bakanlığı SKRS verilerini çekme ve entegre etme
 */
function SKRSAdminPanel() {
  const [status, setStatus] = useState('ready');
  const [progress, setProgress] = useState({});
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }]);
  };

  const handleTestConnection = async () => {
    setStatus('testing');
    setError(null);
    addLog('🔍 SKRS servislerine bağlantı test ediliyor...', 'info');

    try {
      // Test: Sadece 1 kurum çek
      addLog('📡 SKRSKurumveKurulus servisi test ediliyor...', 'info');
      const institutions = await fetchSKRSInstitutions();
      addLog(`✅ ${institutions.length} kurum bulundu`, 'success');

      // Test: İlleri çek
      addLog('📍 SKRSIl servisi test ediliyor...', 'info');
      const provinces = await fetchSKRSProvinces();
      addLog(`✅ ${provinces.length} il bulundu`, 'success');

      // Test: Branşları çek
      addLog('🩺 SKRSKlinikKodlari servisi test ediliyor...', 'info');
      const specialties = await fetchSKRSSpecialties();
      addLog(`✅ ${specialties.length} branş bulundu`, 'success');

      setProgress({
        institutions: institutions.length,
        provinces: provinces.length,
        specialties: specialties.length
      });

      addLog('🎉 Tüm SKRS servisleri başarıyla test edildi!', 'success');
      setStatus('tested');

    } catch (err) {
      console.error('SKRS Test Hatası:', err);
      setError(err.message);
      addLog(`❌ Test başarısız: ${err.message}`, 'error');
      setStatus('error');
    }
  };

  const handleFullIntegration = async () => {
    setStatus('integrating');
    setError(null);
    addLog('🚀 SKRS tam entegrasyonu başlatılıyor...', 'info');

    try {
      const result = await runFullSKRSIntegration();
      
      setProgress(result);
      addLog(`🎉 Entegrasyon tamamlandı!`, 'success');
      addLog(`📊 ${result.totalInserted} kurum başarıyla kaydedildi`, 'success');
      
      if (result.totalErrors > 0) {
        addLog(`⚠️ ${result.totalErrors} kayıtta hata oluştu`, 'warning');
      }

      setStatus('completed');

    } catch (err) {
      console.error('SKRS Entegrasyon Hatası:', err);
      setError(err.message);
      addLog(`❌ Entegrasyon başarısız: ${err.message}`, 'error');
      setStatus('error');
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'testing':
      case 'integrating':
        return '#ff9800';
      case 'tested':
      case 'completed':
        return '#4caf50';
      case 'error':
        return '#f44336';
      default:
        return '#2196f3';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'testing':
        return 'Bağlantı test ediliyor...';
      case 'integrating':
        return 'Entegrasyon çalışıyor...';
      case 'tested':
        return 'Test başarılı - Entegrasyona hazır';
      case 'completed':
        return 'Entegrasyon tamamlandı';
      case 'error':
        return 'Hata oluştu';
      default:
        return 'SKRS Entegrasyona hazır';
    }
  };

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '20px auto', 
      padding: '20px',
      backgroundColor: '#f5f5f5',
      borderRadius: '8px'
    }}>
      <h2 style={{ 
        color: '#1976d2', 
        marginBottom: '20px',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        🏥 SKRS (Sağlık Kodlama Referans Servisi) Entegrasyonu
      </h2>

      {/* Durum Kartı */}
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px',
        border: `3px solid ${getStatusColor()}`
      }}>
        <h3 style={{ color: getStatusColor(), margin: '0 0 10px 0' }}>
          Durum: {getStatusText()}
        </h3>
        
        {progress.institutions && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px', marginTop: '15px' }}>
            <div style={{ textAlign: 'center', padding: '10px', backgroundColor: '#e3f2fd', borderRadius: '5px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
                {progress.institutions || progress.totalInserted || 0}
              </div>
              <div style={{ color: '#666' }}>Sağlık Kurumu</div>
            </div>
            <div style={{ textAlign: 'center', padding: '10px', backgroundColor: '#e8f5e8', borderRadius: '5px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4caf50' }}>
                {progress.provinces || 81}
              </div>
              <div style={{ color: '#666' }}>İl</div>
            </div>
            <div style={{ textAlign: 'center', padding: '10px', backgroundColor: '#fff3e0', borderRadius: '5px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff9800' }}>
                {progress.specialties || 0}
              </div>
              <div style={{ color: '#666' }}>Tıp Branşı</div>
            </div>
          </div>
        )}

        {error && (
          <div style={{
            backgroundColor: '#ffebee',
            color: '#d32f2f',
            padding: '10px',
            borderRadius: '5px',
            marginTop: '15px',
            border: '1px solid #ffcdd2'
          }}>
            <strong>❌ Hata:</strong> {error}
          </div>
        )}
      </div>

      {/* Kontrol Butonları */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
        <button
          onClick={handleTestConnection}
          disabled={status === 'testing' || status === 'integrating'}
          style={{
            padding: '12px 24px',
            backgroundColor: '#2196f3',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: status === 'testing' || status === 'integrating' ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            opacity: status === 'testing' || status === 'integrating' ? 0.6 : 1
          }}
        >
          🔍 Bağlantıyı Test Et
        </button>

        <button
          onClick={handleFullIntegration}
          disabled={status === 'testing' || status === 'integrating' || status !== 'tested'}
          style={{
            padding: '12px 24px',
            backgroundColor: '#4caf50',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: (status === 'testing' || status === 'integrating' || status !== 'tested') ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            opacity: (status === 'testing' || status === 'integrating' || status !== 'tested') ? 0.6 : 1
          }}
        >
          🚀 Tam Entegrasyonu Başlat
        </button>
      </div>

      {/* SKRS Bilgi Kartı */}
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h3 style={{ color: '#1976d2', marginBottom: '15px' }}>
          📋 SKRS Hakkında
        </h3>
        <div style={{ lineHeight: '1.6', color: '#666' }}>
          <p><strong>SKRS (Sağlık Kodlama Referans Servisi)</strong>, T.C. Sağlık Bakanlığı'nın resmi veri servisidir.</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px', marginTop: '15px' }}>
            <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '5px' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#1976d2' }}>🏥 SKRSKurumveKurulus</h4>
              <p style={{ margin: 0, fontSize: '14px' }}>
                Türkiye'deki tüm sağlık kurum ve kuruluşlarının güncel listesi
              </p>
            </div>
            <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '5px' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#1976d2' }}>📍 SKRSIl</h4>
              <p style={{ margin: 0, fontSize: '14px' }}>
                81 ilin standart kodları ve isimleri
              </p>
            </div>
            <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '5px' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#1976d2' }}>🩺 SKRSKlinikKodlari</h4>
              <p style={{ margin: 0, fontSize: '14px' }}>
                Tıp alanındaki tüm branşların standart kodları
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Log Konsolu */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <h3 style={{ 
          backgroundColor: '#37474f', 
          color: 'white', 
          margin: 0, 
          padding: '15px',
          fontSize: '16px' 
        }}>
          📋 İşlem Logları
        </h3>
        <div style={{
          maxHeight: '300px',
          overflowY: 'auto',
          padding: '15px',
          backgroundColor: '#fafafa'
        }}>
          {logs.length === 0 ? (
            <div style={{ color: '#999', fontStyle: 'italic' }}>
              Henüz işlem yapılmadı. Test butonuna tıklayarak başlayın.
            </div>
          ) : (
            logs.map((log, index) => (
              <div key={index} style={{
                marginBottom: '8px',
                padding: '8px',
                borderRadius: '4px',
                backgroundColor: log.type === 'error' ? '#ffebee' : 
                               log.type === 'success' ? '#e8f5e8' : 
                               log.type === 'warning' ? '#fff3e0' : 'white',
                borderLeft: `4px solid ${log.type === 'error' ? '#f44336' : 
                                        log.type === 'success' ? '#4caf50' : 
                                        log.type === 'warning' ? '#ff9800' : '#2196f3'}`
              }}>
                <span style={{ 
                  color: '#666', 
                  fontSize: '12px',
                  marginRight: '10px'
                }}>
                  {log.timestamp}
                </span>
                <span>{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default SKRSAdminPanel;
