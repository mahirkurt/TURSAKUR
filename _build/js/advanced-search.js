/**
 * TURSAKUR Advanced Search Module
 * Provides intelligent search functionality for healthcare institutions
 */

class AdvancedSearch {
    constructor() {
        this.searchIndex = [];
        this.recentSearches = this.loadRecentSearches();
        this.searchSuggestions = [];
        this.init();
    }
    
    init() {
        this.setupSearchInterface();
        this.loadSearchIndex();
        this.bindEvents();
    }
    
    setupSearchInterface() {
        const searchContainer = document.querySelector('.search-container');
        if (!searchContainer) return;
        
        // Create advanced search overlay
        const advancedSearchHTML = `
            <div class="advanced-search-overlay" id="advanced-search-overlay">
                <div class="advanced-search-panel">
                    <div class="advanced-search-header">
                        <h3>Gelişmiş Arama</h3>
                        <button class="close-advanced-search" id="close-advanced-search">
                            <span class="material-symbols-outlined">close</span>
                        </button>
                    </div>
                    
                    <div class="advanced-search-content">
                        <!-- Quick Filters -->
                        <div class="search-section">
                            <h4>Hızlı Filtreler</h4>
                            <div class="quick-filters">
                                <button class="quick-filter-btn" data-query="acil">Acil Servis</button>
                                <button class="quick-filter-btn" data-query="özel">Özel Hastane</button>
                                <button class="quick-filter-btn" data-query="üniversite">Üniversite</button>
                                <button class="quick-filter-btn" data-query="kardiyoloji">Kardiyoloji</button>
                                <button class="quick-filter-btn" data-query="çocuk">Çocuk Hastanesi</button>
                                <button class="quick-filter-btn" data-query="göz">Göz Hastanesi</button>
                            </div>
                        </div>
                        
                        <!-- Recent Searches -->
                        <div class="search-section" id="recent-searches-section" style="display: none;">
                            <h4>Son Aramalar</h4>
                            <div class="recent-searches" id="recent-searches-list"></div>
                        </div>
                        
                        <!-- Search Tips -->
                        <div class="search-section">
                            <h4>Arama İpuçları</h4>
                            <div class="search-tips">
                                <div class="tip-item">
                                    <span class="material-symbols-outlined">lightbulb</span>
                                    <span>"İstanbul kardiyoloji" - Şehir + uzmanlık alanı</span>
                                </div>
                                <div class="tip-item">
                                    <span class="material-symbols-outlined">lightbulb</span>
                                    <span>"Acil servis" - Hizmet türü ile arama</span>
                                </div>
                                <div class="tip-item">
                                    <span class="material-symbols-outlined">lightbulb</span>
                                    <span>"Dr." - Doktor ismi ile arama</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Search Suggestions Dropdown -->
            <div class="search-suggestions-dropdown" id="search-suggestions">
                <div class="suggestions-list" id="suggestions-list"></div>
            </div>
        `;
        
        searchContainer.insertAdjacentHTML('afterend', advancedSearchHTML);
        
        // Add advanced search button to main search bar
        const searchBar = document.querySelector('.search-bar');
        const advancedBtn = document.createElement('button');
        advancedBtn.className = 'search-advanced-btn';
        advancedBtn.innerHTML = '<span class="material-symbols-outlined">tune</span>';
        advancedBtn.title = 'Gelişmiş Arama';
        searchBar.appendChild(advancedBtn);
    }
    
    async loadSearchIndex() {
        try {
            const response = await fetch('data/turkiye_saglik_kuruluslari.json');
            const data = await response.json();
            
            this.searchIndex = data.map(hospital => ({
                id: hospital.kurum_id,
                name: hospital.kurum_adi?.toLowerCase() || '',
                type: hospital.kurum_tipi?.toLowerCase() || '',
                province: hospital.il_adi?.toLowerCase() || '',
                district: hospital.ilce_adi?.toLowerCase() || '',
                address: hospital.adres?.toLowerCase() || '',
                searchText: [
                    hospital.kurum_adi,
                    hospital.kurum_tipi,
                    hospital.il_adi,
                    hospital.ilce_adi,
                    hospital.adres
                ].filter(Boolean).join(' ').toLowerCase()
            }));
            
            console.log('Search index loaded:', this.searchIndex.length, 'hospitals');
        } catch (error) {
            console.error('Error loading search index:', error);
        }
    }
    
    bindEvents() {
        const searchInput = document.getElementById('search-input');
        const advancedBtn = document.querySelector('.search-advanced-btn');
        const closeAdvancedBtn = document.getElementById('close-advanced-search');
        const overlay = document.getElementById('advanced-search-overlay');
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value);
            });
            
            searchInput.addEventListener('focus', () => {
                this.showSuggestions();
            });
            
            searchInput.addEventListener('keydown', (e) => {
                this.handleKeyboardNavigation(e);
            });
        }
        
        if (advancedBtn) {
            advancedBtn.addEventListener('click', () => {
                this.showAdvancedSearch();
            });
        }
        
        if (closeAdvancedBtn) {
            closeAdvancedBtn.addEventListener('click', () => {
                this.hideAdvancedSearch();
            });
        }
        
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.hideAdvancedSearch();
                }
            });
        }
        
        // Quick filter buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.quick-filter-btn')) {
                const query = e.target.dataset.query;
                this.executeSearch(query);
                this.hideAdvancedSearch();
            }
        });
        
        // Click outside to close suggestions
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-bar') && !e.target.closest('.search-suggestions-dropdown')) {
                this.hideSuggestions();
            }
        });
    }
    
    handleSearchInput(query) {
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }
        
        const suggestions = this.generateSuggestions(query);
        this.displaySuggestions(suggestions);
    }
    
    generateSuggestions(query) {
        const queryLower = query.toLowerCase();
        const suggestions = [];
        
        // Exact matches first
        const exactMatches = this.searchIndex.filter(item => 
            item.name.includes(queryLower)
        ).slice(0, 3);
        
        // Province matches
        const provinceMatches = this.searchIndex.filter(item => 
            item.province.includes(queryLower) && !exactMatches.find(em => em.id === item.id)
        ).slice(0, 2);
        
        // Type matches
        const typeMatches = this.searchIndex.filter(item => 
            item.type.includes(queryLower) && 
            !exactMatches.find(em => em.id === item.id) &&
            !provinceMatches.find(pm => pm.id === item.id)
        ).slice(0, 2);
        
        // Recent searches that match
        const recentMatches = this.recentSearches.filter(recent => 
            recent.toLowerCase().includes(queryLower)
        ).slice(0, 2);
        
        return {
            exact: exactMatches,
            province: provinceMatches,
            type: typeMatches,
            recent: recentMatches
        };
    }
    
    displaySuggestions(suggestions) {
        const suggestionsList = document.getElementById('suggestions-list');
        if (!suggestionsList) return;
        
        let html = '';
        
        // Recent searches
        if (suggestions.recent.length > 0) {
            html += '<div class="suggestion-group">';
            html += '<div class="suggestion-group-title">Son Aramalar</div>';
            suggestions.recent.forEach(query => {
                html += `
                    <div class="suggestion-item recent" data-query="${query}">
                        <span class="material-symbols-outlined">history</span>
                        <span>${query}</span>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        // Exact matches
        if (suggestions.exact.length > 0) {
            html += '<div class="suggestion-group">';
            html += '<div class="suggestion-group-title">Hastaneler</div>';
            suggestions.exact.forEach(item => {
                html += `
                    <div class="suggestion-item hospital" data-id="${item.id}">
                        <span class="material-symbols-outlined">local_hospital</span>
                        <div class="suggestion-content">
                            <div class="suggestion-name">${this.highlightMatch(item.name, document.getElementById('search-input').value)}</div>
                            <div class="suggestion-location">${item.district}, ${item.province}</div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        // Province matches
        if (suggestions.province.length > 0) {
            html += '<div class="suggestion-group">';
            html += '<div class="suggestion-group-title">Şehirler</div>';
            suggestions.province.forEach(item => {
                html += `
                    <div class="suggestion-item location" data-query="${item.province}">
                        <span class="material-symbols-outlined">location_city</span>
                        <span>${this.highlightMatch(item.province, document.getElementById('search-input').value)}</span>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        suggestionsList.innerHTML = html;
        this.showSuggestions();
        
        // Bind suggestion click events
        suggestionsList.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                if (item.dataset.id) {
                    this.selectHospital(item.dataset.id);
                } else if (item.dataset.query) {
                    this.executeSearch(item.dataset.query);
                }
            });
        });
    }
    
    highlightMatch(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    showSuggestions() {
        const dropdown = document.getElementById('search-suggestions');
        if (dropdown) {
            dropdown.style.display = 'block';
        }
    }
    
    hideSuggestions() {
        const dropdown = document.getElementById('search-suggestions');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }
    
    showAdvancedSearch() {
        const overlay = document.getElementById('advanced-search-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
            this.updateRecentSearches();
        }
    }
    
    hideAdvancedSearch() {
        const overlay = document.getElementById('advanced-search-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    updateRecentSearches() {
        const section = document.getElementById('recent-searches-section');
        const list = document.getElementById('recent-searches-list');
        
        if (this.recentSearches.length > 0) {
            section.style.display = 'block';
            list.innerHTML = this.recentSearches.map(query => `
                <div class="recent-search-item" data-query="${query}">
                    <span class="material-symbols-outlined">search</span>
                    <span>${query}</span>
                    <button class="remove-recent" data-query="${query}">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
            `).join('');
            
            // Bind events
            list.querySelectorAll('.recent-search-item').forEach(item => {
                item.addEventListener('click', () => {
                    this.executeSearch(item.dataset.query);
                    this.hideAdvancedSearch();
                });
            });
            
            list.querySelectorAll('.remove-recent').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.removeRecentSearch(btn.dataset.query);
                });
            });
        } else {
            section.style.display = 'none';
        }
    }
    
    executeSearch(query) {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.value = query;
            
            // Trigger search event
            const event = new Event('input', { bubbles: true });
            searchInput.dispatchEvent(event);
            
            // Add to recent searches
            this.addToRecentSearches(query);
            
            this.hideSuggestions();
        }
    }
    
    selectHospital(hospitalId) {
        // Scroll to and highlight specific hospital
        const hospitalCard = document.querySelector(`[data-id="${hospitalId}"]`);
        if (hospitalCard) {
            hospitalCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            hospitalCard.classList.add('highlight');
            setTimeout(() => {
                hospitalCard.classList.remove('highlight');
            }, 3000);
        }
        
        this.hideSuggestions();
    }
    
    handleKeyboardNavigation(e) {
        const suggestions = document.querySelectorAll('.suggestion-item');
        if (suggestions.length === 0) return;
        
        const current = document.querySelector('.suggestion-item.selected');
        let index = Array.from(suggestions).indexOf(current);
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (current) current.classList.remove('selected');
                index = (index + 1) % suggestions.length;
                suggestions[index].classList.add('selected');
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                if (current) current.classList.remove('selected');
                index = index <= 0 ? suggestions.length - 1 : index - 1;
                suggestions[index].classList.add('selected');
                break;
                
            case 'Enter':
                e.preventDefault();
                if (current) {
                    current.click();
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }
    
    addToRecentSearches(query) {
        if (!query || this.recentSearches.includes(query)) return;
        
        this.recentSearches.unshift(query);
        this.recentSearches = this.recentSearches.slice(0, 5); // Keep only 5 recent searches
        this.saveRecentSearches();
    }
    
    removeRecentSearch(query) {
        this.recentSearches = this.recentSearches.filter(q => q !== query);
        this.saveRecentSearches();
        this.updateRecentSearches();
    }
    
    loadRecentSearches() {
        try {
            return JSON.parse(localStorage.getItem('tursakur_recent_searches') || '[]');
        } catch {
            return [];
        }
    }
    
    saveRecentSearches() {
        localStorage.setItem('tursakur_recent_searches', JSON.stringify(this.recentSearches));
    }
}

// Initialize advanced search when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AdvancedSearch();
});
