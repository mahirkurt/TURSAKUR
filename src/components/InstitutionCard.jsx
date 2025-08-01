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

  // Kurum tipi renk belirleme
  const getInstitutionTypeColor = (type) => {
    if (!type) return 'default';
    
    const typeLower = type.toLowerCase();
    
    if (typeLower.includes('hastane')) return 'red';
    if (typeLower.includes('sağlık ocağı') || typeLower.includes('aile sağlığı')) return 'blue';
    if (typeLower.includes('poliklinik') || typeLower.includes('muayenehane')) return 'green';
    if (typeLower.includes('eczane')) return 'purple';
    if (typeLower.includes('diş')) return 'orange';
    if (typeLower.includes('özel')) return 'teal';
    if (typeLower.includes('devlet')) return 'indigo';
    
    return 'gray';
  };

  // Açık/kapalı durumu hesaplaması KALDIRILDI

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

  const handleDetailsClick = (e) => {
    e.stopPropagation();
    if (onNavigate) {
      onNavigate(institution);
    } else {
      navigate(`/kurum/${kurum_id}`);
    }
  };

  const institutionTypeColor = getInstitutionTypeColor(kurum_tipi);

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
      data-testid="facility-item"
      data-has-coords={!!(koordinat_lat && koordinat_lon)}
    >
      {/* Kurum tipi badge'i - Renkli */}
      <CardBadge className={`institution-card__type institution-card__type--${institutionTypeColor} facility-type`}>
        {kurum_tipi || 'Sağlık Kuruluşu'}
      </CardBadge>

      <CardContent>
        <CardHeader
          title={<span className="facility-name">{highlightText(kurum_adi, searchQuery)}</span>}
          subtitle={<span className="facility-location">{`${ilce_adi}, ${il_adi}`}</span>}
        />

        {/* Açık/Kapalı durumu KALDIRILDI */}

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
          onClick={handleDetailsClick}
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
