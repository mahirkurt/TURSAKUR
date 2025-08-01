import React from 'react'
import './ErrorMessage.css'

function ErrorMessage({ title = "Bir hata oluştu", message, onRetry, className = "" }) {
  return (
    <div className={`error-message ${className}`}>
      <div className="error-content">
        <div className="error-icon">⚠️</div>
        <h3 className="error-title headline-small">{title}</h3>
        {message && (
          <p className="error-description body-medium">{message}</p>
        )}
        {onRetry && (
          <button onClick={onRetry} className="retry-button">
            Tekrar Dene
          </button>
        )}
      </div>
    </div>
  )
}

export default ErrorMessage
