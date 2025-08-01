import React from 'react'
import './StatsPanel.css'

function StatsPanel({ stats, isLoading, className = "" }) {
  if (isLoading) {
    return (
      <div className={`stats-panel ${className}`}>
        <h3 className="title-medium">İstatistikler</h3>
        <p className="body-small">Yükleniyor...</p>
      </div>
    )
  }

  return (
    <div className={`stats-panel ${className}`}>
      <h3 className="title-medium">İstatistikler</h3>
      {stats && (
        <div className="stats-content">
          <div className="stat-item">
            <span className="stat-value headline-small">{stats.total?.toLocaleString('tr-TR')}</span>
            <span className="stat-label body-small">Toplam Kurum</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default StatsPanel
