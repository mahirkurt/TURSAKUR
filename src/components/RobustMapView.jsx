import React, { useState, useEffect, Suspense } from 'react'
import LoadingSpinner from './LoadingSpinner'
import './MapView.css'

// Lazy load map components
const LazyMapContainer = React.lazy(() => 
  import('react-leaflet').then(module => ({ default: module.MapContainer }))
)
const LazyTileLayer = React.lazy(() => 
  import('react-leaflet').then(module => ({ default: module.TileLayer }))
)
const LazyMarker = React.lazy(() => 
  import('react-leaflet').then(module => ({ default: module.Marker }))
)
const LazyPopup = React.lazy(() => 
  import('react-leaflet').then(module => ({ default: module.Popup }))
)

// Map loading fallback
const MapLoadingFallback = () => (
  <div className="map-loading-fallback" id="map">
    <LoadingSpinner message="Harita yükleniyor..." />
  </div>
)

// Map error fallback
const MapErrorFallback = ({ onRetry }) => (
  <div className="map-error-fallback" id="map">
    <div className="error-content">
      <h3>🗺️ Harita Yüklenemedi</h3>
      <p>Harita görüntülenirken bir sorun oluştu.</p>
      <button onClick={onRetry} className="retry-button">
        Tekrar Dene
      </button>
    </div>
  </div>
)

function RobustMapView({ 
  institutions = [], 
  loading = false, 
  error = null,
  center = [39.9334, 32.8597], // Ankara coordinates
  zoom = 6,
  onBoundsChange,
  className = ""
}) {
  const [mapError, setMapError] = useState(null)
  const [isMapReady, setIsMapReady] = useState(false)
  const [retryCount, setRetryCount] = useState(0)

  // Reset error when component mounts or retry
  useEffect(() => {
    setMapError(null)
    
    // Dynamically load Leaflet CSS
    const leafletCSS = document.createElement('link')
    leafletCSS.rel = 'stylesheet'
    leafletCSS.href = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css'
    leafletCSS.integrity = 'sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=='
    leafletCSS.crossOrigin = ''
    
    if (!document.querySelector('link[href*="leaflet.css"]')) {
      document.head.appendChild(leafletCSS)
    }

    // Check if Leaflet is available
    const checkLeaflet = () => {
      if (typeof window !== 'undefined' && window.L) {
        setIsMapReady(true)
      } else {
        // Load Leaflet script
        const leafletScript = document.createElement('script')
        leafletScript.src = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js'
        leafletScript.integrity = 'sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA=='
        leafletScript.crossOrigin = ''
        leafletScript.onload = () => {
          setTimeout(() => setIsMapReady(true), 100)
        }
        leafletScript.onerror = () => {
          setMapError(new Error('Leaflet kütüphanesi yüklenemedi'))
        }
        document.head.appendChild(leafletScript)
      }
    }

    const timer = setTimeout(checkLeaflet, 100)
    return () => clearTimeout(timer)
  }, [retryCount])

  const handleRetry = () => {
    setRetryCount(prev => prev + 1)
    setMapError(null)
    setIsMapReady(false)
  }

  // Show error fallback if map failed to load
  if (mapError || error) {
    return <MapErrorFallback onRetry={handleRetry} />
  }

  // Show loading while map is initializing
  if (!isMapReady || loading) {
    return <MapLoadingFallback />
  }

  return (
    <div className={`map-view ${className}`}>
      <Suspense fallback={<MapLoadingFallback />}>
        <div className="map-container-wrapper">
          <div id="map" style={{ height: '100%', width: '100%' }}>
            {/* Basit harita iframe fallback */}
            <iframe
              src="https://www.openstreetmap.org/export/embed.html?bbox=26.043%2C35.815%2C44.818%2C42.107&amp;layer=mapnik&amp;marker=39.9334%2C32.8597"
              width="100%"
              height="400"
              style={{ border: 'none', borderRadius: '8px' }}
              title="Türkiye Haritası"
            />
          </div>
        </div>
      </Suspense>
    </div>
  )
}

export default RobustMapView
