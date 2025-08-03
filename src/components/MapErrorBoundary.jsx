import React from 'react'
import './MapErrorBoundary.css'

class MapErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Map error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="map-error-fallback" id="map">
          <div className="error-content">
            <h3>🗺️ Harita Yüklenemedi</h3>
            <p>Harita görüntülenirken bir sorun oluştu.</p>
            <button 
              onClick={() => window.location.reload()}
              className="retry-button"
            >
              Tekrar Dene
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default MapErrorBoundary
