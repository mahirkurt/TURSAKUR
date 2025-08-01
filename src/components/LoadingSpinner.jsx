import React from 'react'
import './LoadingSpinner.css'

function LoadingSpinner({ message = "Yükleniyor...", size = "medium", className = "" }) {
  return (
    <div className={`loading-spinner ${size} ${className}`} data-testid="loading">
      <div className="spinner">
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
      </div>
      {message && (
        <p className="loading-message body-medium">{message}</p>
      )}
    </div>
  )
}

export default LoadingSpinner
