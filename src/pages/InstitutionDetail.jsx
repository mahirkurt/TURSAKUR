import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useInstitutions } from '../hooks/useInstitutions';
import { ThemeProvider } from '../contexts/ThemeContext';
import TopAppBar from '../components/TopAppBar';
import Footer from '../components/Footer';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import './InstitutionDetail.css';

/**
 * Institution Detail Page
 * Sağlık kuruluşu detay sayfası
 */
function InstitutionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // Tek kurum verisi getir
  const { data: institutionsData, isLoading, error } = useInstitutions({
    kurum_id: id,
    pageSize: 1
  });

  const institution = institutionsData?.institutions?.[0];

  // Eğer ID yoksa veya geçersizse ana sayfaya yönlendir
  useEffect(() => {
    if (!id || id === 'undefined' || id === 'null') {
      navigate('/', { replace: true });
    }
  }, [id, navigate]);

  const handleBack = () => {
    navigate(-1);
  };

  const handleCall = (phone) => {
    if (phone) {
      window.location.href = `tel:${phone}`;
    }
  };

  const handleDirections = (lat, lon, address) => {
    if (lat && lon) {
      // Google Maps ile yol tarifi
      const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`;
      window.open(url, '_blank');
    } else if (address) {
      // Adres ile arama
      const encodedAddress = encodeURIComponent(address);
      const url = `https://www.google.com/maps/search/?api=1&query=${encodedAddress}`;
      window.open(url, '_blank');
    }
  };

  if (isLoading) {
    return (
      <ThemeProvider>
        <div className="app">
          <TopAppBar />
          <main className="institution-detail-page">
            <LoadingSpinner message="Kurum bilgileri yükleniyor..." />
          </main>
          <Footer />
        </div>
      </ThemeProvider>
    );
  }

  if (error || !institution) {
    return (
      <ThemeProvider>
        <div className="app">
          <TopAppBar />
          <main className="institution-detail-page">
            <div className="container">
              <ErrorMessage 
                title="Kurum bulunamadı"
                message="Aradığınız sağlık kuruluşu bulunamadı veya bir hata oluştu."
                onRetry={() => navigate('/', { replace: true })}
                retryText="Ana Sayfaya Dön"
              />
            </div>
          </main>
          <Footer />
        </div>
      </ThemeProvider>
    );
  }

  const {
    id: institutionId,
    isim_standart,
    tip,
    adres_yapilandirilmis: adresYapilandirilmis,
    iletisim,
    koordinatlar,
    kaynaklar,
    // Backward compatibility için eski alanlar
    kurum_adi = isim_standart,
    kurum_tipi = tip,
    il_adi = adresYapilandirilmis?.il,
    ilce_adi = adresYapilandirilmis?.ilce,
    adres = adresYapilandirilmis?.tam_adres,
    telefon = iletisim?.telefon?.[0],
    koordinat_lat = koordinatlar?.latitude,
    koordinat_lon,
    veri_kaynagi,
    adres_yapilandirilmis
  } = institution;

  return (
    <ThemeProvider>
      <div className="app">
        <TopAppBar />
        
        <main className="institution-detail-page">
          <div className="container">
            {/* Navigasyon */}
            <div className="detail-navigation">
              <Button
                variant="text"
                icon="arrow_back"
                onClick={handleBack}
              >
                Geri
              </Button>
            </div>

            {/* Başlık Kartı */}
            <div className="md-card md-card--elevated detail-header-card">
              <div className="md-card__content">
                <div className="detail-header">
                  <div className="detail-title-section">
                    <span className="md-card__badge detail-type-badge">
                      {kurum_tipi}
                    </span>
                    <h1 className="display-small detail-title">
                      {kurum_adi}
                    </h1>
                    <p className="title-medium detail-location">
                      <span className="material-symbols-outlined">location_on</span>
                      {ilce_adi}, {il_adi}
                    </p>
                  </div>

                  <div className="detail-actions">
                    {telefon && (
                      <Button
                        variant="filled"
                        icon="phone"
                        onClick={() => handleCall(telefon)}
                      >
                        Ara
                      </Button>
                    )}
                    <Button
                      variant="filled-tonal"
                      icon="directions"
                      onClick={() => handleDirections(koordinat_lat, koordinat_lon, adres)}
                    >
                      Yol Tarifi
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* Detay Bilgileri */}
            <div className="detail-content">
              <div className="detail-grid">
                {/* İletişim Bilgileri */}
                <div className="md-card md-card--elevated detail-card">
                  <div className="md-card__content">
                    <h2 className="headline-small detail-card-title">
                      <span className="material-symbols-outlined">contact_phone</span>
                      İletişim Bilgileri
                    </h2>
                    
                    <div className="detail-info-list">
                      {telefon && (
                        <div className="detail-info-item">
                          <span className="detail-info-label">Telefon:</span>
                          <a href={`tel:${telefon}`} className="detail-info-value detail-link">
                            {telefon}
                          </a>
                        </div>
                      )}
                      
                      <div className="detail-info-item">
                        <span className="detail-info-label">Adres:</span>
                        <span className="detail-info-value">
                          {adres || adres_yapilandirilmis || `${ilce_adi}, ${il_adi}`}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Konum Bilgileri */}
                <div className="md-card md-card--elevated detail-card">
                  <div className="md-card__content">
                    <h2 className="headline-small detail-card-title">
                      <span className="material-symbols-outlined">location_on</span>
                      Konum Bilgileri
                    </h2>
                    
                    <div className="detail-info-list">
                      <div className="detail-info-item">
                        <span className="detail-info-label">İl:</span>
                        <span className="detail-info-value">{il_adi}</span>
                      </div>
                      
                      <div className="detail-info-item">
                        <span className="detail-info-label">İlçe:</span>
                        <span className="detail-info-value">{ilce_adi}</span>
                      </div>

                      {koordinat_lat && koordinat_lon && (
                        <div className="detail-info-item">
                          <span className="detail-info-label">Koordinatlar:</span>
                          <span className="detail-info-value">
                            {koordinat_lat}, {koordinat_lon}
                          </span>
                        </div>
                      )}
                    </div>

                    {koordinat_lat && koordinat_lon && (
                      <div className="detail-map-section">
                        <Button
                          variant="outlined"
                          icon="map"
                          onClick={() => handleDirections(koordinat_lat, koordinat_lon, adres)}
                          className="map-button"
                        >
                          Haritada Göster
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Kurum Bilgileri */}
                <div className="md-card md-card--elevated detail-card">
                  <div className="md-card__content">
                    <h2 className="headline-small detail-card-title">
                      <span className="material-symbols-outlined">business</span>
                      Kurum Bilgileri
                    </h2>
                    
                    <div className="detail-info-list">
                      <div className="detail-info-item">
                        <span className="detail-info-label">Kurum Tipi:</span>
                        <span className="detail-info-value">{kurum_tipi}</span>
                      </div>

                      {veri_kaynagi && (
                        <div className="detail-info-item">
                          <span className="detail-info-label">Veri Kaynağı:</span>
                          <span className="detail-info-value">{veri_kaynagi}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </ThemeProvider>
  );
}

export default InstitutionDetail;
