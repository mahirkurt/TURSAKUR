import React, { useState, useMemo } from 'react';
import { useInstitutions, useProvinces, useInstitutionTypes, useStatistics } from '../hooks/useInstitutions';
import { ThemeProvider } from '../contexts/ThemeContext';
import SearchBar from '../components/ui/SearchBar';
import FilterPanel from '../components/FilterPanel';
import InstitutionCard from '../components/InstitutionCard';
import StatsPanel from '../components/StatsPanel';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import TopAppBar from '../components/TopAppBar';
import Footer from '../components/Footer';
import Button from '../components/ui/Button';
import './HomePage.css';

function HomePage() {
  // Arama ve filtreleme state'i
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProvince, setSelectedProvince] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [sortBy, setSortBy] = useState('isim_standart');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Debounced search query (300ms gecikme)
  const [debouncedSearch, setDebouncedSearch] = useState('');
  
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [searchQuery]);

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
  }), [debouncedSearch, selectedProvince, selectedDistrict, selectedTypes, sortBy, sortOrder, currentPage]);

  // Data hooks
  const { data: institutionsData, isLoading: institutionsLoading, error: institutionsError } = useInstitutions(filters);
  const { data: provinces, isLoading: provincesLoading } = useProvinces();
  const { data: types, isLoading: typesLoading } = useInstitutionTypes();
  const { data: stats, isLoading: statsLoading } = useStatistics();

  // Derived data
  const institutions = institutionsData?.institutions || [];
  const totalCount = institutionsData?.totalCount || 0;

  // Event handlers
  const handleSearchChange = (value) => {
    setSearchQuery(value);
    setCurrentPage(1);
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handleSuggestionSelect = (suggestion) => {
    setSearchQuery(suggestion.title);
    setCurrentPage(1);
  };

  // Filtre temizleme
  const clearFilters = () => {
    setSearchQuery('');
    setSelectedProvince('');
    setSelectedDistrict('');
    setSelectedTypes([]);
    setCurrentPage(1);
  };

  const hasActiveFilters = searchQuery || selectedProvince || selectedDistrict || selectedTypes.length > 0;

  // Arama önerileri (mock data - gerçek uygulamada API'den gelecek)
  const searchSuggestions = useMemo(() => {
    if (!searchQuery || searchQuery.length < 2) return [];
    
    // Örnek öneriler
    return [
      { id: 1, title: 'Ankara Şehir Hastanesi', subtitle: 'Ankara', type: 'hospital' },
      { id: 2, title: 'İstanbul', subtitle: '2,847 sağlık kuruluşu', type: 'location' },
      { id: 3, title: 'Acil Servis', subtitle: '1,234 sonuç', type: 'suggestion' }
    ].filter(item => 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.subtitle.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [searchQuery]);

  // Render functions
  const renderLoadingState = () => (
    <LoadingSpinner message="Sağlık kuruluşları yükleniyor..." />
  );

  const renderErrorState = () => (
    <ErrorMessage 
      title="Veri yüklenirken hata oluştu"
      message={institutionsError.message}
      onRetry={() => window.location.reload()}
    />
  );

  const renderInstitutionsList = () => (
    <>
      {/* Kuruluş Kartları - Material Design 3 Grid */}
      <div className="institutions-grid">
        {institutions.map((institution) => (
          <InstitutionCard 
            key={institution.kurum_id}
            institution={institution}
            searchQuery={debouncedSearch}
            className="institution-card-item"
          />
        ))}
      </div>

      {/* Sayfalama - Material Design 3 */}
      {totalCount > pageSize && (
        <div className="pagination">
          <Button
            variant="outlined"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(p => p - 1)}
            icon="chevron_left"
          >
            Önceki
          </Button>
          
          <span className="pagination-info body-medium">
            Sayfa {currentPage} / {Math.ceil(totalCount / pageSize)}
          </span>
          
          <Button
            variant="outlined"
            disabled={currentPage >= Math.ceil(totalCount / pageSize)}
            onClick={() => setCurrentPage(p => p + 1)}
            icon="chevron_right"
            iconPosition="end"
          >
            Sonraki
          </Button>
        </div>
      )}
    </>
  );

  const renderEmptyStateFiltered = () => (
    <div className="empty-state" data-testid="no-results">
      <span className="empty-state-icon material-symbols-outlined">
        search_off
      </span>
      <h3 className="headline-small">Sonuç bulunamadı</h3>
      <p className="body-medium">
        Arama kriterlerinizi değiştirip tekrar deneyin.
      </p>
      <Button 
        variant="filled-tonal"
        onClick={clearFilters}
        icon="filter_list_off"
      >
        Filtreleri Temizle
      </Button>
    </div>
  );

  const renderEmptyStateWelcome = () => (
    <div className="empty-state">
      <span className="empty-state-icon material-symbols-outlined">
        local_hospital
      </span>
      <h3 className="headline-small">Hoş geldiniz</h3>
      <p className="body-medium">
        Arama yapmak için yukarıdaki arama çubuğunu kullanın veya filtreleri deneyin.
      </p>
    </div>
  );

  const renderResultsContent = () => {
    if (institutionsLoading) {
      return renderLoadingState();
    }
    
    if (institutionsError) {
      return renderErrorState();
    }
    
    if (institutions.length > 0) {
      return renderInstitutionsList();
    }
    
    if (hasActiveFilters) {
      return renderEmptyStateFiltered();
    }
    
    return renderEmptyStateWelcome();
  };

  return (
    <ThemeProvider>
      <div className="home-page">
        <TopAppBar />
        
        {/* Hero Section - Material Design 3 */}
        <section className="hero-section">
          <div className="hero-content">
            <h1 className="display-medium hero-title">
              Türkiye Sağlık Kuruluşları
            </h1>
            <p className="body-large hero-subtitle">
              Ülkemizdeki tüm sağlık kuruluşlarını keşfedin. Modern arama ve harita özellikleri ile aradığınız sağlık hizmetini kolayca bulun.
            </p>
            
            {/* Ana Arama Çubuğu - Material Design 3 */}
            <SearchBar
              value={searchQuery}
              onChange={handleSearchChange}
              onSearch={handleSearch}
              onSuggestionSelect={handleSuggestionSelect}
              suggestions={searchSuggestions}
              placeholder="Hastane, il, ilçe veya hizmet arayın..."
              loading={institutionsLoading}
              className="hero-search"
            />
          </div>
        </section>

        <div className="main-content">
          {/* Sidebar - Material Design 3 Layout */}
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
              provinces={provinces || []}
              selectedProvince={selectedProvince}
              onProvinceChange={setSelectedProvince}
              selectedDistrict={selectedDistrict}
              onDistrictChange={setSelectedDistrict}
              types={types || []}
              selectedTypes={selectedTypes}
              onTypesChange={setSelectedTypes}
              onClearFilters={clearFilters}
              hasActiveFilters={hasActiveFilters}
              isLoading={provincesLoading || typesLoading}
              className="filters-panel"
            />
          </aside>

          {/* Ana İçerik Alanı */}
          <main className="main-results">
            {/* Sonuç Başlığı ve Kontroller */}
            {institutionsData && (
              <div className="results-header">
                <div className="results-info">
                  <h2 className="headline-small">
                    {institutionsData.totalCount > 0 
                      ? `${institutionsData.totalCount.toLocaleString()} sonuç bulundu`
                      : 'Sonuç bulunamadı'
                    }
                  </h2>
                  {hasActiveFilters && (
                    <p className="body-medium results-filter-info">
                      Filtreler uygulandı
                    </p>
                  )}
                </div>

                {/* Sıralama Kontrolü */}
                {institutionsData.totalCount > 0 && (
                  <div className="sort-controls">
                    <label htmlFor="sort-select" className="label-medium">Sırala:</label>
                    <select 
                      id="sort-select"
                      value={`${sortBy}-${sortOrder}`}
                      onChange={(e) => {
                        const [newSortBy, newSortOrder] = e.target.value.split('-');
                        setSortBy(newSortBy);
                        setSortOrder(newSortOrder);
                        setCurrentPage(1);
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
            )}

            {/* Sonuç İçeriği */}
            <div className="results-content" data-testid="results-list">
              {renderResultsContent()}
            </div>
          </main>
        </div>

        <Footer />
      </div>
    </ThemeProvider>
  );
}

export default HomePage;
