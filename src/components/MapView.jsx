import React, { useState, useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './MapView.css'

// Fix for default markers with fallback
try {
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  })
} catch (error) {
  console.warn('Leaflet icon setup failed:', error)
}

// Custom icon creators
const createCustomIcon = (type, color) => {
  const iconHtml = `
    <div class="custom-marker ${type}" style="background-color: ${color}">
      ${getIconForType(type)}
    </div>
  `
  return L.divIcon({
    html: iconHtml,
    className: 'custom-marker-wrapper',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15]
  })
}

const getIconForType = (type) => {
  const icons = {
    'hastane': '🏥',
    'saglik-ocagi': '🏥',
    'eczane': '💊',
    'universite-hastanesi': '🎓',
    'default': '📍'
  }
  return icons[type] || icons.default
}

// Map control components
function MapControls({ onZoomIn, onZoomOut, onResetView, onToggleFilters, showFilters }) {
  return (
    <div className="map-controls">
      <button 
        className="map-control-button" 
        onClick={onZoomIn}
        title="Yakınlaştır"
        aria-label="Yakınlaştır"
      >
        ➕
      </button>
      <button 
        className="map-control-button" 
        onClick={onZoomOut}
        title="Uzaklaştır"
        aria-label="Uzaklaştır"
      >
        ➖
      </button>
      <button 
        className="map-control-button" 
        onClick={onResetView}
        title="Türkiye görünümüne dön"
        aria-label="Türkiye görünümüne dön"
      >
        🌍
      </button>
      <button 
        className={`map-control-button ${showFilters ? 'active' : ''}`}
        onClick={onToggleFilters}
        title="Filtreleri göster/gizle"
        aria-label="Filtreleri göster/gizle"
      >
        🔧
      </button>
    </div>
  )
}

function MapFilters({ visibleTypes, onTypeToggle, showFilters }) {
  const institutionTypes = [
    { key: 'hastane', label: 'Hastaneler', color: '#BB0012' },
    { key: 'saglik-ocagi', label: 'Sağlık Ocakları', color: '#00696D' },
    { key: 'eczane', label: 'Eczaneler', color: '#775700' },
    { key: 'universite-hastanesi', label: 'Üniversite Hastaneleri', color: '#B3261E' }
  ]

  if (!showFilters) return null

  return (
    <div className="map-filters">
      <h3 className="map-filters-title">Harita Filtreleri</h3>
      <div className="map-filter-group">
        <label className="map-filter-label">Kuruluş Türleri</label>
        <div className="map-filter-checkboxes">
          {institutionTypes.map(type => (
            <label key={type.key} className="map-filter-checkbox">
              <input
                type="checkbox"
                className="map-filter-input"
                checked={visibleTypes.includes(type.key)}
                onChange={() => onTypeToggle(type.key)}
              />
              <span className="map-filter-text">{type.label}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}

function MapInfo({ institutions, bounds }) {
  const visibleCount = institutions?.length || 0
  const typeStats = institutions?.reduce((acc, inst) => {
    const type = inst.tip || 'Diğer'
    acc[type] = (acc[type] || 0) + 1
    return acc
  }, {}) || {}

  return (
    <div className="map-info">
      <h3 className="map-info-title">Harita Bilgileri</h3>
      <div className="map-info-content">
        <p>Görünümde {visibleCount} kuruluş bulunuyor</p>
        <div className="map-info-stats">
          {Object.entries(typeStats).map(([type, count]) => (
            <div key={type} className="map-info-stat">
              <div className="map-info-stat-value">{count}</div>
              <div className="map-info-stat-label">{type}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Map component that handles bounds and markers
function MapContent({ institutions, onBoundsChange, visibleTypes }) {
  const map = useMap()
  
  useEffect(() => {
    const handleMoveEnd = () => {
      const bounds = map.getBounds()
      if (onBoundsChange) {
        onBoundsChange({
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest()
        })
      }
    }

    map.on('moveend', handleMoveEnd)
    return () => {
      map.off('moveend', handleMoveEnd)
    }
  }, [map, onBoundsChange])

  // Filter institutions based on visible types
  const filteredInstitutions = institutions?.filter(inst => {
    const type = inst.tip?.toLowerCase().replace(/\s+/g, '-') || 'default'
    return visibleTypes.length === 0 || visibleTypes.includes(type)
  }) || []

  return (
    <>
      {filteredInstitutions.map(institution => {
        if (!institution.konum?.coordinates) return null
        
        const [lng, lat] = institution.konum.coordinates
        const type = institution.tip?.toLowerCase().replace(/\s+/g, '-') || 'default'
        const icon = createCustomIcon(type, '#BB0012')

        return (
          <Marker
            key={institution.id}
            position={[lat, lng]}
            icon={icon}
          >
            <Popup>
              <div className="map-popup">
                <h4 className="popup-title">{institution.isim_standart}</h4>
                <p className="popup-type">{institution.tip}</p>
                <p className="popup-address">
                  {institution.adres_yapilandirilmis?.il}, {institution.adres_yapilandirilmis?.ilce}
                </p>
                {institution.iletisim?.telefon && (
                  <p className="popup-phone">📞 {institution.iletisim.telefon}</p>
                )}
                {institution.iletisim?.website && (
                  <p className="popup-website">
                    <a href={institution.iletisim.website} target="_blank" rel="noopener noreferrer">
                      🌐 Web Sitesi
                    </a>
                  </p>
                )}
              </div>
            </Popup>
          </Marker>
        )
      })}
    </>
  )
}

function MapView({ 
  institutions = [], 
  loading = false, 
  error = null,
  center = [39.9334, 32.8597], // Ankara coordinates
  zoom = 6,
  onBoundsChange,
  className = ""
}) {
  const [showFilters, setShowFilters] = useState(false)
  const [visibleTypes, setVisibleTypes] = useState(['hastane', 'saglik-ocagi', 'eczane', 'universite-hastanesi'])
  const mapRef = useRef()

  const handleZoomIn = () => {
    if (mapRef.current) {
      mapRef.current.zoomIn()
    }
  }

  const handleZoomOut = () => {
    if (mapRef.current) {
      mapRef.current.zoomOut()
    }
  }

  const handleResetView = () => {
    if (mapRef.current) {
      mapRef.current.setView(center, zoom)
    }
  }

  const handleTypeToggle = (type) => {
    setVisibleTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    )
  }

  if (error) {
    return (
      <div className={`map-view ${className}`}>
        <div className="map-error">
          <div className="map-error-icon">🗺️</div>
          <h3 className="map-error-title">Harita yüklenemedi</h3>
          <p className="map-error-message">{error.message || 'Bilinmeyen hata'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`map-view ${className}`}>
      {loading && (
        <div className="map-loading">
          <div className="loading-spinner">
            <div className="spinner-ring"></div>
          </div>
        </div>
      )}
      
      <MapContainer
        center={center}
        zoom={zoom}
        className="map-container"
        ref={mapRef}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapContent 
          institutions={institutions}
          onBoundsChange={onBoundsChange}
          visibleTypes={visibleTypes}
        />
      </MapContainer>

      <MapControls
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onResetView={handleResetView}
        onToggleFilters={() => setShowFilters(!showFilters)}
        showFilters={showFilters}
      />

      <MapFilters
        visibleTypes={visibleTypes}
        onTypeToggle={handleTypeToggle}
        showFilters={showFilters}
      />

      <MapInfo 
        institutions={institutions?.filter(inst => {
          const type = inst.tip?.toLowerCase().replace(/\s+/g, '-') || 'default'
          return visibleTypes.length === 0 || visibleTypes.includes(type)
        })}
      />
    </div>
  )
}

export default MapView
