import React, { useState, useMemo } from 'react'
import { useInstitutions, useProvinces, useInstitutionTypes, useStatistics } from '../hooks/useInstitutions'
import SearchBar from '../components/SearchBar'
import FilterPanel from '../components/FilterPanel'
import InstitutionCard from '../components/InstitutionCard'
import StatsPanel from '../components/StatsPanel'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import TopAppBar from '../components/TopAppBar'
import './HomePage.css'

function HomePage() {
  // Arama ve filtreleme state'i
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedProvince, setSelectedProvince] = useState('')
  const [selectedDistrict, setSelectedDistrict] = useState('')
  const [selectedTypes, setSelectedTypes] = useState([])
  const [sortBy, setSortBy] = useState('isim_standart')
  const [sortOrder, setSortOrder] = useState('asc')
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 20

  // Debounced search query (300ms gecikme)
  const [debouncedSearch, setDebouncedSearch] = useState('')
  
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery)
    }, 300)
    
    return () => clearTimeout(timer)
  }, [searchQuery])

  // Filtre objesi oluştur
  const filters = useMemo(() => ({
    search: debouncedSearch,
    il: selectedProvince,
    ilce: selectedDistrict,
    tip: selectedTypes,
    sortBy,
    sortOrder,
    page: currentPage,
    pageSize
  }), [debouncedSearch, selectedProvince, selectedDistrict, selectedTypes, sortBy, sortOrder, currentPage])

  // Data hooks
  const { data: institutionsData, isLoading: institutionsLoading, error: institutionsError } = useInstitutions(filters)
  const { data: provinces, isLoading: provincesLoading } = useProvinces()
  const { data: types, isLoading: typesLoading } = useInstitutionTypes()
  const { data: stats, isLoading: statsLoading } = useStatistics()

  const institutions = institutionsData?.institutions || []
  const totalCount = institutionsData?.total || 0

  // Loading state
  const isLoading = institutionsLoading || provincesLoading || typesLoading || statsLoading

  // Error handling
  if (institutionsError) {
    return (
      <div className="home-page">
        <TopAppBar />
        <ErrorMessage 
          title="Veri Yükleme Hatası"
          message={institutionsError.message}
          onRetry={() => window.location.reload()}
        />
      </div>
    )
  }

  // Filter handlers
  const handleSearchChange = (query) => {
    setSearchQuery(query)
    setCurrentPage(1) // Reset sayfa
  }

  const handleProvinceChange = (province) => {
    setSelectedProvince(province)
    setSelectedDistrict('') // İlçe resetle
    setCurrentPage(1)
  }

  const handleDistrictChange = (district) => {
    setSelectedDistrict(district)
    setCurrentPage(1)
  }

  const handleTypeToggle = (type) => {
    setSelectedTypes(prev => 
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    )
    setCurrentPage(1)
  }

  const clearFilters = () => {
    setSearchQuery('')
    setSelectedProvince('')
    setSelectedDistrict('')
    setSelectedTypes([])
    setCurrentPage(1)
  }

  const hasActiveFilters = searchQuery || selectedProvince || selectedDistrict || selectedTypes.length > 0

  return (
    <div className="home-page">
      <TopAppBar />
      
      {/* Hero Bölümü */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="display-small hero-title">
            Türkiye Sağlık Kuruluşları
          </h1>
          <p className="body-large hero-subtitle">
            Ülkemizdeki tüm sağlık kuruluşlarını keşfedin. Modern arama ve harita özellikleri ile aradığınız sağlık hizmetini kolayca bulun.
          </p>
          
          {/* Ana Arama Çubuğu */}
          <SearchBar
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Hastane, il, ilçe veya hizmet arayın..."
            className="hero-search"
          />
        </div>
      </section>

      <div className="main-content">
        {/* Sidebar - Filtreler ve İstatistikler */}
        <aside className="sidebar">
          {/* İstatistikler Paneli */}
          {stats && (
            <StatsPanel 
              stats={stats}
              isLoading={statsLoading}
              className="stats-panel"
            />
          )}

          {/* Filtreler Paneli */}
          <FilterPanel
            // Province filter
            provinces={provinces || []}
            selectedProvince={selectedProvince}
            onProvinceChange={handleProvinceChange}
            
            // District filter
            selectedDistrict={selectedDistrict}
            onDistrictChange={handleDistrictChange}
            
            // Type filter
            types={types || []}
            selectedTypes={selectedTypes}
            onTypeToggle={handleTypeToggle}
            
            // Actions
            onClearFilters={clearFilters}
            hasActiveFilters={hasActiveFilters}
            
            isLoading={provincesLoading || typesLoading}
            className="filter-panel"
          />
        </aside>

        {/* Ana İçerik */}
        <main className="content">
          {/* Sonuç Başlığı ve Sıralama */}
          <div className="results-header">
            <div className="results-info">
              <h2 className="headline-small">
                {totalCount > 0 ? (
                  `${totalCount.toLocaleString('tr-TR')} kurum bulundu`
                ) : hasActiveFilters ? (
                  'Arama kriterlerinize uygun kurum bulunamadı'
                ) : (
                  'Tüm sağlık kuruluşları'
                )}
              </h2>
              
              {hasActiveFilters && (
                <p className="body-medium results-filters">
                  {searchQuery && <span>"{searchQuery}" için </span>}
                  {selectedProvince && <span>{selectedProvince} ili </span>}
                  {selectedDistrict && <span>{selectedDistrict} ilçesi </span>}
                  {selectedTypes.length > 0 && (
                    <span>{selectedTypes.join(', ')} tipinde </span>
                  )}
                  arama sonuçları
                </p>
              )}
            </div>

            {totalCount > 0 && (
              <div className="sort-controls">
                <label className="label-medium">Sırala:</label>
                <select 
                  value={`${sortBy}-${sortOrder}`}
                  onChange={(e) => {
                    const [newSortBy, newSortOrder] = e.target.value.split('-')
                    setSortBy(newSortBy)
                    setSortOrder(newSortOrder)
                    setCurrentPage(1)
                  }}
                  className="sort-select"
                >
                  <option value="isim_standart-asc">Ad (A-Z)</option>
                  <option value="isim_standart-desc">Ad (Z-A)</option>
                  <option value="tip-asc">Tip (A-Z)</option>
                  <option value="updated_at-desc">Son Güncellenen</option>
                </select>
              </div>
            )}
          </div>

          {/* Sonuç Listesi */}
          <div className="results-content">
            {isLoading ? (
              <LoadingSpinner message="Sağlık kuruluşları yükleniyor..." />
            ) : institutions.length > 0 ? (
              <>
                <div className="institutions-grid">
                  {institutions.map((institution) => (
                    <InstitutionCard 
                      key={institution.id}
                      institution={institution}
                      searchQuery={debouncedSearch}
                    />
                  ))}
                </div>

                {/* Sayfalama */}
                {totalCount > pageSize && (
                  <div className="pagination">
                    <button
                      disabled={currentPage === 1}
                      onClick={() => setCurrentPage(p => p - 1)}
                      className="pagination-button"
                    >
                      Önceki
                    </button>
                    
                    <span className="pagination-info">
                      Sayfa {currentPage} / {Math.ceil(totalCount / pageSize)}
                    </span>
                    
                    <button
                      disabled={currentPage >= Math.ceil(totalCount / pageSize)}
                      onClick={() => setCurrentPage(p => p + 1)}
                      className="pagination-button"
                    >
                      Sonraki
                    </button>
                  </div>
                )}
              </>
            ) : hasActiveFilters ? (
              <div className="empty-state">
                <div className="empty-state-icon">🔍</div>
                <h3 className="headline-small">Sonuç bulunamadı</h3>
                <p className="body-medium">
                  Arama kriterlerinizi değiştirip tekrar deneyin.
                </p>
                <button onClick={clearFilters} className="clear-filters-button">
                  Filtreleri Temizle
                </button>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">🏥</div>
                <h3 className="headline-small">Hoş geldiniz</h3>
                <p className="body-medium">
                  Arama yapmak için yukarıdaki arama çubuğunu kullanın veya filtreleri deneyin.
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default HomePage
