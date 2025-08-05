/**
 * TURSAKUR 2.0 - Search and Filter Logic
 * ========================================
 * 
 * Handles user input for searching and filtering health facilities.
 */

document.addEventListener('DOMContentLoaded', async () => {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const cityFilter = document.getElementById('city-filter');
    const typeFilter = document.getElementById('type-filter');
    const quickFilterContainer = document.querySelector('.quick-filters');
    const dataLoader = window.tursakurDataLoader;

    if (!dataLoader) {
        console.error('Tursakur Data Loader bulunamadı!');
        return;
    }

    // Veri yükleyicinin hazır olmasını bekle
    await dataLoader.initializeApp();

    const populateFilters = async () => {
        try {
            // İlleri yükle ve doldur
            const provinces = await dataLoader.loadProvinces();
            cityFilter.innerHTML = '<option value="all">Tüm İller</option>';
            provinces.forEach(province => {
                const option = document.createElement('option');
                option.value = province;
                option.textContent = province;
                cityFilter.appendChild(option);
            });

            // Kurum tiplerini yükle ve doldur
            const types = await dataLoader.loadFacilityTypes();
            typeFilter.innerHTML = '<option value="all">Tüm Tipler</option>';
            types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                typeFilter.appendChild(option);
            });

            // Hızlı filtreleri (chipleri) doldur
            if (quickFilterContainer) {
                const quickFilterTypes = types.slice(0, 4); // İlk 4 tipi gösterelim
                quickFilterContainer.innerHTML = '<legend class="sr-only">Hızlı Filtreler</legend>';
                quickFilterTypes.forEach(type => {
                    const chip = document.createElement('button');
                    chip.className = 'quick-filter-chip';
                    chip.dataset.filter = type;
                    chip.textContent = type;
                    chip.addEventListener('click', () => handleQuickFilter(chip));
                    quickFilterContainer.appendChild(chip);
                });
            }

        } catch (error) {
            console.error('Filtreler doldurulurken hata oluştu:', error);
        }
    };

    const applyFilters = async () => {
        const query = searchInput.value;
        const selectedCity = cityFilter.value;
        const selectedType = typeFilter.value;

        const filters = {
            province: selectedCity,
            type: selectedType
        };

        try {
            const results = await dataLoader.searchFacilities(query, filters);
            dataLoader.renderFacilities(results);
        } catch (error) {
            console.error('Filtreleme sırasında hata:', error);
        }
    };

    const handleQuickFilter = (clickedChip) => {
        const isActive = clickedChip.classList.contains('quick-filter-chip--selected');
        
        // Tüm chiplerden seçili durumunu kaldır
        document.querySelectorAll('.quick-filter-chip').forEach(chip => {
            chip.classList.remove('quick-filter-chip--selected');
        });

        if (isActive) {
            // Eğer zaten aktifse, seçimi kaldır ve ana filtreyi 'all' yap
            typeFilter.value = 'all';
        } else {
            // Değilse, bu çipi aktif yap ve ana filtreyi ayarla
            clickedChip.classList.add('quick-filter-chip--selected');
            typeFilter.value = clickedChip.dataset.filter;
        }

        applyFilters();
    };

    // Event Listeners
    searchButton.addEventListener('click', applyFilters);
    searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            applyFilters();
        }
    });
    cityFilter.addEventListener('change', applyFilters);
    typeFilter.addEventListener('change', () => {
        // Ana select değiştiğinde, ilgili çipi de güncelle
        const selectedType = typeFilter.value;
        document.querySelectorAll('.quick-filter-chip').forEach(chip => {
            if (chip.dataset.filter === selectedType) {
                chip.classList.add('quick-filter-chip--selected');
            } else {
                chip.classList.remove('quick-filter-chip--selected');
            }
        });
        applyFilters();
    });

    // Initial population
    populateFilters();
});
