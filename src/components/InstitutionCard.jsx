import React from 'react';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';
import Card, { CardContent, CardHeader, CardActions, CardMetadata, CardBadge } from './ui/Card';
import Button from './ui/Button';
import './InstitutionCard.css'

/**
 * Institution Card Component
 * Sağlık kuruluşları için Material Design 3 standardında özelleştirilmiş kart bileşeni
 */
function InstitutionCard({ 
  institution, 
  searchQuery = "", 
  showDistance = false, 
  distance = null, 
  className = "", 
  onNavigate 
}) {
  const navigate = useNavigate();
  
  const { 
    kurum_id, 
    kurum_adi, 
    kurum_tipi, 
    il_adi,
    ilce_adi,
    adres,
    telefon,
    koordinat_lat,
    koordinat_lon,
    veri_kaynagi,
    adres_yapilandirilmis 
  } = institution

  // Arama terimini vurgula
  const highlightText = (text, query) => {
    if (!query || !text) return text
    
    const regex = new RegExp(`(${query})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, index) => 
      regex.test(part) ? 
        <mark key={`highlight-${index}-${part}`} className="highlight">{part}</mark> : 
        part
    )
  }

  // Açık/kapalı durumu
  const getStatus = () => {
    const now = new Date();
    const currentHour = now.getHours();
    
    // 7/24 hizmet veren kurumlar
    if (kurum_tipi?.toLowerCase().includes('acil') || 
        kurum_tipi?.toLowerCase().includes('hastane')) {
      return 'open';
    } else if (currentHour >= 8 && currentHour < 17) {
      return 'open';
    } else {
      return 'closed';
    }
  };

  const handleCardClick = () => {
    if (onNavigate) {
      onNavigate(institution);
    } else {
      navigate(`/kurum/${kurum_id}`);
    }
  };

  const handleMapClick = (e) => {
    e.stopPropagation();
    if (koordinat_lat && koordinat_lon) {
      const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${koordinat_lat},${koordinat_lon}`;
      window.open(mapsUrl, '_blank');
    }
  };

  const handleCallClick = (e) => {
    e.stopPropagation();
    if (telefon) {
      window.location.href = `tel:${telefon}`;
    }
  };

  const status = getStatus();
  const statusText = {
    open: 'Açık',
    closed: 'Kapalı',
    unknown: 'Bilinmiyor'
  };

  // Adres bilgisi - önce yapılandırılmış adresi dene, yoksa ham adresi kullan
  let fullAddress = '';
  if (adres_yapilandirilmis) {
    fullAddress = [
      adres_yapilandirilmis.sokak_no || adres_yapilandirilmis.sokak, 
      adres_yapilandirilmis.mahalle, 
      adres_yapilandirilmis.ilce || ilce_adi, 
      adres_yapilandirilmis.il || il_adi
    ].filter(Boolean).join(', ');
  } else {
    fullAddress = [adres, ilce_adi, il_adi].filter(Boolean).join(', ');
  }

  // Metadata items
  const metadataItems = [
    ...(fullAddress ? [{ icon: 'location_on', text: fullAddress }] : []),
    ...(telefon ? [{ icon: 'phone', text: telefon }] : []),
    ...(showDistance && distance ? [{ icon: 'near_me', text: `${distance} km`, className: 'institution-card__distance' }] : [])
  ];

  return (
    <Card
      variant="elevated"
      interactive
      onClick={handleCardClick}
      className={`institution-card ${className}`}
    >
      {/* Kurum tipi badge'i */}
      <CardBadge className="institution-card__type">
        {kurum_tipi || 'Sağlık Kuruluşu'}
      </CardBadge>

      <CardContent>
        <CardHeader
          title={highlightText(kurum_adi, searchQuery)}
          subtitle={`${ilce_adi}, ${il_adi}`}
        />

        {/* Açık/Kapalı durumu */}
        <div className={`institution-card__status institution-card__status--${status}`}>
          {statusText[status]}
        </div>

        {/* Metadata */}
        {metadataItems.length > 0 && (
          <CardMetadata items={metadataItems} />
        )}

        {/* Kaynak bilgisi */}
        {veri_kaynagi && (
          <div className="md-card__metadata">
            <div className="md-card__metadata-item">
              <span className="md-card__metadata-icon material-symbols-outlined">
                verified
              </span>
              <span>Kaynak: {veri_kaynagi}</span>
            </div>
          </div>
        )}
      </CardContent>

      <CardActions alignment="between">
        <div style={{ display: 'flex', gap: 'var(--md-spacing-2)' }}>
          {telefon && (
            <Button
              variant="text"
              size="small"
              icon="phone"
              onClick={handleCallClick}
            >
              Ara
            </Button>
          )}
          
          {koordinat_lat && koordinat_lon && (
            <Button
              variant="text"
              size="small"
              icon="map"
              onClick={handleMapClick}
            >
              Haritada Göster
            </Button>
          )}
        </div>

        <Button
          variant="filled-tonal"
          size="small"
          icon="info"
        >
          Detaylar
        </Button>
      </CardActions>
    </Card>
  );
}

InstitutionCard.propTypes = {
  institution: PropTypes.shape({
    kurum_id: PropTypes.string.isRequired,
    kurum_adi: PropTypes.string.isRequired,
    kurum_tipi: PropTypes.string,
    il_adi: PropTypes.string,
    ilce_adi: PropTypes.string,
    adres: PropTypes.string,
    telefon: PropTypes.string,
    koordinat_lat: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    koordinat_lon: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    web_sitesi: PropTypes.string,
    veri_kaynagi: PropTypes.string,
    adres_yapilandirilmis: PropTypes.object
  }).isRequired,
  searchQuery: PropTypes.string,
  showDistance: PropTypes.bool,
  distance: PropTypes.string,
  className: PropTypes.string,
  onNavigate: PropTypes.func
};

export default InstitutionCard;
