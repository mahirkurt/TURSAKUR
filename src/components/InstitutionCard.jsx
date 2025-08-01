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
    id, 
    isim_standart, 
    tip, 
    adres_yapilandirilmis, 
    iletisim, 
    meta_veri,
    kaynaklar 
  } = institution

  // Arama terimini vurgula
  const highlightText = (text, query) => {
    if (!query || !text) return text
    
    const regex = new RegExp(`(${query})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, index) => 
      regex.test(part) ? 
        <mark key={index} className="highlight">{part}</mark> : 
        part
    )
  }

  // Açık/kapalı durumu
  const getStatus = () => {
    const now = new Date();
    const currentHour = now.getHours();
    
    // 7/24 hizmet veren kurumlar
    if (tip?.toLowerCase().includes('acil') || tip?.toLowerCase().includes('hastane')) {
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
      navigate(`/kurum/${id}`);
    }
  };

  const handleDirectionsClick = (e) => {
    e.stopPropagation();
    if (meta_veri?.koordinatlar?.latitude && meta_veri?.koordinatlar?.longitude) {
      const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${meta_veri.koordinatlar.latitude},${meta_veri.koordinatlar.longitude}`;
      window.open(mapsUrl, '_blank');
    }
  };

  const handleCallClick = (e) => {
    e.stopPropagation();
    if (iletisim?.telefon?.[0]) {
      window.location.href = `tel:${iletisim.telefon[0]}`;
    }
  };

  const status = getStatus();
  const statusText = {
    open: 'Açık',
    closed: 'Kapalı',
    unknown: 'Bilinmiyor'
  };

  // Adres bilgisi
  const address = adres_yapilandirilmis;
  const fullAddress = [
    address?.sokak_no, 
    address?.mahalle, 
    address?.ilce, 
    address?.il
  ].filter(Boolean).join(', ');

  // Metadata items
  const metadataItems = [
    ...(fullAddress ? [{ icon: 'location_on', text: fullAddress }] : []),
    ...(iletisim?.telefon?.[0] ? [{ icon: 'phone', text: iletisim.telefon[0] }] : []),
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
        {tip || 'Sağlık Kuruluşu'}
      </CardBadge>

      <CardContent>
        <CardHeader
          title={highlightText(isim_standart, searchQuery)}
          subtitle={meta_veri?.bagli_oldugu_kurum}
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
        {kaynaklar && kaynaklar.length > 0 && (
          <div className="md-card__metadata">
            <div className="md-card__metadata-item">
              <span className="md-card__metadata-icon material-symbols-outlined">
                verified
              </span>
              <span>Kaynak: {kaynaklar[0]}</span>
            </div>
          </div>
        )}
      </CardContent>

      <CardActions alignment="between">
        <div style={{ display: 'flex', gap: 'var(--md-spacing-2)' }}>
          {iletisim?.telefon?.[0] && (
            <Button
              variant="text"
              size="small"
              icon="phone"
              onClick={handleCallClick}
            >
              Ara
            </Button>
          )}
          
          {meta_veri?.koordinatlar?.latitude && meta_veri?.koordinatlar?.longitude && (
            <Button
              variant="text"
              size="small"
              icon="directions"
              onClick={handleDirectionsClick}
            >
              Yol Tarifi
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
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    isim_standart: PropTypes.string.isRequired,
    tip: PropTypes.string,
    adres_yapilandirilmis: PropTypes.object,
    iletisim: PropTypes.object,
    meta_veri: PropTypes.object,
    kaynaklar: PropTypes.array
  }).isRequired,
  searchQuery: PropTypes.string,
  showDistance: PropTypes.bool,
  distance: PropTypes.string,
  className: PropTypes.string,
  onNavigate: PropTypes.func
};

export default InstitutionCard;
