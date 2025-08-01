import React, { useState, useMemo } from 'react'
import Button from './ui/Button'
import './FilterPanel.css'

export function FilterPanel({ 
  provinces = [],
  selectedProvince = '',
  onProvinceChange,
  selectedDistrict = '',
  onDistrictChange,
  types = [],
  selectedTypes = [],
  onTypesChange,
  onClearFilters,
  hasActiveFilters = false,
  isLoading = false,
  className = "" 
}) {
  const [isExpanded, setIsExpanded] = useState(true);

  // İlçeleri seçili ile göre filtrele
  const districts = useMemo(() => {
    if (!selectedProvince || !provinces.length) return [];
    const province = provinces.find(p => p.il_adi === selectedProvince);
    return province?.ilceler || [];
  }, [selectedProvince, provinces]);

  const handleProvinceChange = (e) => {
    onProvinceChange(e.target.value);
    // İl değişince ilçeyi sıfırla
    if (onDistrictChange) {
      onDistrictChange('');
    }
  };

  const handleTypeToggle = (typeValue) => {
    const newTypes = selectedTypes.includes(typeValue)
      ? selectedTypes.filter(t => t !== typeValue)
      : [...selectedTypes, typeValue];
    onTypesChange(newTypes);
  };

  return (
    <div className={`filter-panel ${className}`}>
      <div className="filter-header">
        <h3 className="title-medium">Filtreler</h3>
        <button 
          className="toggle-button"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-label={isExpanded ? 'Filtreleri gizle' : 'Filtreleri göster'}
        >
          <span className="material-symbols-outlined">
            {isExpanded ? 'expand_less' : 'expand_more'}
          </span>
        </button>
      </div>

      {isExpanded && (
        <div className="filter-content">
          {/* İl Filtresi */}
          <div className="filter-group">
            <label htmlFor="province-select" className="label-medium">İl</label>
            <select 
              id="province-select"
              value={selectedProvince}
              onChange={handleProvinceChange}
              className="filter-select"
              disabled={isLoading}
            >
              <option value="">Tüm İller</option>
              {provinces.map(province => (
                <option key={province.il_adi} value={province.il_adi}>
                  {province.il_adi}
                </option>
              ))}
            </select>
          </div>

          {/* İlçe Filtresi */}
          {selectedProvince && districts.length > 0 && (
            <div className="filter-group">
              <label htmlFor="district-select" className="label-medium">İlçe</label>
              <select 
                id="district-select"
                value={selectedDistrict}
                onChange={(e) => onDistrictChange(e.target.value)}
                className="filter-select"
                disabled={isLoading}
              >
                <option value="">Tüm İlçeler</option>
                {districts.map(district => (
                  <option key={district} value={district}>
                    {district}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Kurum Tipi Filtresi */}
          <div className="filter-group">
            <label className="label-medium">Kurum Tipi</label>
            <div className="filter-checkboxes">
              {types.map(type => (
                <label key={type.value} className="checkbox-label">
                  <input 
                    type="checkbox"
                    checked={selectedTypes.includes(type.value)}
                    onChange={() => handleTypeToggle(type.value)}
                    className="filter-checkbox"
                  />
                  <span className="checkbox-text body-small">
                    {type.label} ({type.count})
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Filtreleri Temizle */}
          {hasActiveFilters && (
            <div className="filter-actions">
              <Button
                variant="outlined"
                size="small"
                icon="filter_list_off"
                onClick={onClearFilters}
                className="clear-filters-btn"
              >
                Filtreleri Temizle
              </Button>
            </div>
          )}
        </div>
      )}
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
