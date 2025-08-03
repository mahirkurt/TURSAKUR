import React, { useState, useCallback } from 'react'
import TopAppBar from '../components/TopAppBar'
import MapView from '../components/MapView'
import RobustMapView from '../components/RobustMapView'
import MapErrorBoundary from '../components/MapErrorBoundary'
import SearchBar from '../components/SearchBar'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { useInstitutions } from '../hooks/useInstitutions'
import './MapPage.css'

function MapPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [mapBounds, setMapBounds] = useState(null)
  
  // Use bounds-based query for map
  const { 
    data: institutions, 
    isLoading, 
    error 
  } = useInstitutions({
    search: searchQuery,
    bounds: mapBounds,
    limit: 1000 // More generous limit for map view
  })

  const handleBoundsChange = useCallback((bounds) => {
    setMapBounds(bounds)
  }, [])

  const handleSearchChange = useCallback((value) => {
    setSearchQuery(value)
  }, [])

  return (
    <div className="map-page">
      <TopAppBar />
      
      <main className="map-main">
        <div className="map-header">
          <div className="map-search-container">
            <SearchBar
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Haritada arama yapın..."
              className="map-search"
            />
          </div>
        </div>

        <div className="map-content">
          {error ? (
            <ErrorMessage
              title="Harita verileri yüklenemedi"
              message={error.message}
              className="map-error"
            />
          ) : (
            <MapErrorBoundary>
              <RobustMapView
                institutions={institutions}
                loading={isLoading}
                onBoundsChange={handleBoundsChange}
                className="main-map"
              />
            </MapErrorBoundary>
          )}
        </div>

        <div className="map-footer">
          <div className="map-info-bar">
            <span className="institution-count">
              {institutions?.length || 0} kuruluş görüntüleniyor
            </span>
            {isLoading && (
              <span className="loading-indicator">
                <LoadingSpinner size="small" className="inline" />
                Yükleniyor...
              </span>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default MapPage
