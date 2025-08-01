import React from 'react'
import './FilterPanel.css'

// Placeholder bileşenler - gerçek uygulamada tam implement edilecek

export function FilterPanel({ className = "" }) {
  return (
    <div className={`filter-panel ${className}`}>
      <h3 className="title-medium">Filtreler</h3>
      <p className="body-small">Filtreleme özellikleri yakında eklenecek...</p>
    </div>
  )
}

export function StatsPanel({ stats, isLoading, className = "" }) {
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

export default FilterPanel
