/**
 * Theme Manager Module
 * Tema değiştirme ve yönetimi
 */

class ThemeManager {
    constructor() {
        this.currentTheme = 'light';
        this.themes = {
            'light': 'Açık Tema',
            'dark': 'Koyu Tema',
            'light-hc': 'Açık Yüksek Kontrast',
            'dark-hc': 'Koyu Yüksek Kontrast',
            'light-mc': 'Açık Orta Kontrast',
            'dark-mc': 'Koyu Orta Kontrast'
        };
        this.prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    }

    /**
     * Tema yöneticisini başlat
     */
    init() {
        this.loadSavedTheme();
        this.setupThemeToggle();
        this.setupSystemThemeDetection();
        this.createThemeSelector();
    }

    /**
     * Kaydedilmiş temayı yükle
     */
    loadSavedTheme() {
        const savedTheme = localStorage.getItem('health-db-theme');
        
        if (savedTheme && this.themes[savedTheme]) {
            this.currentTheme = savedTheme;
        } else {
            // Sistem temasını kontrol et
            this.currentTheme = this.prefersDark.matches ? 'dark' : 'light';
        }
        
        this.applyTheme(this.currentTheme);
    }

    /**
     * Temayı uygula
     */
    applyTheme(themeName) {
        if (!this.themes[themeName]) return;

        // Mevcut tema linkini kaldır
        const existingThemeLink = document.getElementById('theme-css');
        if (existingThemeLink) {
            existingThemeLink.remove();
        }

        // Yeni tema linkini ekle
        const themeLink = document.createElement('link');
        themeLink.id = 'theme-css';
        themeLink.rel = 'stylesheet';
        themeLink.href = `../css/${themeName}.css`;
        
        // Main CSS'den sonra ekle
        const mainCSS = document.querySelector('link[href*="main.css"]');
        if (mainCSS) {
            mainCSS.insertAdjacentElement('afterend', themeLink);
        } else {
            document.head.appendChild(themeLink);
        }

        this.currentTheme = themeName;
        localStorage.setItem('health-db-theme', themeName);
        
        // UI'ı güncelle
        this.updateThemeUI();
        
        console.log(`🎨 Tema değiştirildi: ${this.themes[themeName]}`);
    }

    /**
     * Tema UI'ını güncelle
     */
    updateThemeUI() {
        // Tema toggle butonunu güncelle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('.material-symbols-outlined');
            if (icon) {
                icon.textContent = this.currentTheme.includes('dark') ? 'light_mode' : 'dark_mode';
            }
            
            themeToggle.title = this.currentTheme.includes('dark') ? 
                'Açık temaya geç' : 'Koyu temaya geç';
        }

        // Tema seçiciyi güncelle
        const themeSelector = document.getElementById('theme-selector');
        if (themeSelector) {
            themeSelector.value = this.currentTheme;
        }

        // Body class'ını güncelle
        document.body.className = `theme-${this.currentTheme}`;
    }

    /**
     * Tema toggle butonunu ayarla
     */
    setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    }

    /**
     * Tema değiştir (açık/koyu arasında)
     */
    toggleTheme() {
        let newTheme;
        
        if (this.currentTheme.includes('dark')) {
            // Koyu temadan açık temaya geç
            newTheme = this.currentTheme.replace('dark', 'light');
        } else {
            // Açık temadan koyu temaya geç
            newTheme = this.currentTheme.replace('light', 'dark');
        }

        this.applyTheme(newTheme);
    }

    /**
     * Sistem tema algılamasını ayarla
     */
    setupSystemThemeDetection() {
        this.prefersDark.addEventListener('change', (e) => {
            // Eğer kullanıcı özel tema seçmemişse sistem temasını takip et
            const hasCustomTheme = localStorage.getItem('health-db-theme');
            if (!hasCustomTheme) {
                const systemTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(systemTheme);
            }
        });
    }

    /**
     * Tema seçiciyi oluştur
     */
    createThemeSelector() {
        const themeButton = document.getElementById('theme-selector-button');
        if (!themeButton) return;

        // Dropdown menüyü oluştur
        const dropdown = document.createElement('div');
        dropdown.id = 'theme-dropdown';
        dropdown.className = 'theme-dropdown';
        dropdown.innerHTML = `
            <div class="theme-dropdown-content">
                ${Object.entries(this.themes).map(([key, label]) => `
                    <button class="theme-option ${key === this.currentTheme ? 'active' : ''}" 
                            data-theme="${key}">
                        <span class="theme-preview" data-theme="${key}"></span>
                        <span class="theme-label">${label}</span>
                        ${key === this.currentTheme ? '<span class="material-symbols-outlined">check</span>' : ''}
                    </button>
                `).join('')}
            </div>
        `;

        // Butonu tıklama olayı
        themeButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleThemeDropdown();
        });

        // Tema seçeneklerine tıklama olayları
        dropdown.addEventListener('click', (e) => {
            const themeOption = e.target.closest('.theme-option');
            if (themeOption) {
                const selectedTheme = themeOption.getAttribute('data-theme');
                this.applyTheme(selectedTheme);
                this.hideThemeDropdown();
            }
        });

        // Dropdown'ı sayfaya ekle
        themeButton.parentNode.insertBefore(dropdown, themeButton.nextSibling);

        // Dışarıya tıklama ile kapat
        document.addEventListener('click', (e) => {
            if (!themeButton.contains(e.target) && !dropdown.contains(e.target)) {
                this.hideThemeDropdown();
            }
        });
    }

    /**
     * Tema dropdown'ını aç/kapat
     */
    toggleThemeDropdown() {
        const dropdown = document.getElementById('theme-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    }

    /**
     * Tema dropdown'ını gizle
     */
    hideThemeDropdown() {
        const dropdown = document.getElementById('theme-dropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
    }

    /**
     * Mevcut temayı al
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Tema listesini al
     */
    getAvailableThemes() {
        return this.themes;
    }
}

/**
 * Institution Detail Modal
 * Kurum detay modalını yönetir
 */
class InstitutionModal {
    constructor() {
        this.modal = null;
        this.currentInstitution = null;
    }

    /**
     * Modal HTML'ini oluştur
     */
    createModal() {
        if (this.modal) return;

        this.modal = document.createElement('div');
        this.modal.id = 'institution-modal';
        this.modal.className = 'modal-overlay';
        this.modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="modal-title">Kurum Detayı</h2>
                    <button class="icon-button" id="modal-close">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
                <div class="modal-body" id="modal-body">
                    <!-- İçerik buraya yüklenecek -->
                </div>
            </div>
        `;

        document.body.appendChild(this.modal);

        // Event listener'ları ekle
        this.setupModalEvents();
    }

    /**
     * Modal event listener'larını ayarla
     */
    setupModalEvents() {
        // Kapat butonu
        const closeButton = this.modal.querySelector('#modal-close');
        closeButton.addEventListener('click', () => this.hide());

        // Overlay'e tıklama ile kapat
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
            }
        });

        // ESC tuşu ile kapat
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                this.hide();
            }
        });
    }

    /**
     * Kurum detayını göster
     */
    show(institutionId) {
        const institution = dataLoader.getInstitutionById(institutionId);
        if (!institution) return;

        this.currentInstitution = institution;
        
        if (!this.modal) {
            this.createModal();
        }

        this.renderInstitutionDetail(institution);
        this.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Modalı gizle
     */
    hide() {
        if (this.modal) {
            this.modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    /**
     * Kurum detayını render et
     */
    renderInstitutionDetail(institution) {
        const modalTitle = this.modal.querySelector('#modal-title');
        const modalBody = this.modal.querySelector('#modal-body');

        modalTitle.textContent = institution.kurum_adi;

        const hasCoordinates = institution.koordinat_lat && institution.koordinat_lon;
        const hasPhone = institution.telefon && institution.telefon.trim();
        const hasWebsite = institution.web_sitesi && institution.web_sitesi.trim();

        modalBody.innerHTML = `
            <div class="institution-detail">
                <div class="detail-section">
                    <h3>Genel Bilgiler</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">Kurum Türü</span>
                            <span class="detail-value">${institution.kurum_tipi}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Kurum ID</span>
                            <span class="detail-value">${institution.kurum_id}</span>
                        </div>
                    </div>
                </div>

                <div class="detail-section">
                    <h3>Konum Bilgileri</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">İl</span>
                            <span class="detail-value">${institution.il_adi}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">İlçe</span>
                            <span class="detail-value">${institution.ilce_adi}</span>
                        </div>
                        ${institution.adres ? `
                            <div class="detail-item full-width">
                                <span class="detail-label">Adres</span>
                                <span class="detail-value">${institution.adres}</span>
                            </div>
                        ` : ''}
                        ${hasCoordinates ? `
                            <div class="detail-item">
                                <span class="detail-label">Enlem</span>
                                <span class="detail-value">${institution.koordinat_lat}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Boylam</span>
                                <span class="detail-value">${institution.koordinat_lon}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>

                <div class="detail-section">
                    <h3>İletişim</h3>
                    <div class="detail-grid">
                        ${hasPhone ? `
                            <div class="detail-item">
                                <span class="detail-label">Telefon</span>
                                <span class="detail-value">
                                    <a href="tel:${institution.telefon}">${institution.telefon}</a>
                                </span>
                            </div>
                        ` : ''}
                        ${hasWebsite ? `
                            <div class="detail-item full-width">
                                <span class="detail-label">Web Sitesi</span>
                                <span class="detail-value">
                                    <a href="${institution.web_sitesi}" target="_blank" rel="noopener">
                                        ${institution.web_sitesi}
                                        <span class="material-symbols-outlined">open_in_new</span>
                                    </a>
                                </span>
                            </div>
                        ` : ''}
                    </div>
                </div>

                <div class="detail-section">
                    <h3>Veri Bilgileri</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">Veri Kaynağı</span>
                            <span class="detail-value">${institution.veri_kaynagi || 'Belirtilmemiş'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Son Güncelleme</span>
                            <span class="detail-value">${institution.son_guncelleme || 'Belirtilmemiş'}</span>
                        </div>
                    </div>
                </div>

                <div class="detail-actions">
                    ${hasPhone ? `
                        <button class="primary-button" onclick="window.open('tel:${institution.telefon}')">
                            <span class="material-symbols-outlined">call</span>
                            <span>Ara</span>
                        </button>
                    ` : ''}
                    ${hasWebsite ? `
                        <button class="secondary-button" onclick="window.open('${institution.web_sitesi}', '_blank')">
                            <span class="material-symbols-outlined">language</span>
                            <span>Web Sitesi</span>
                        </button>
                    ` : ''}
                    ${hasCoordinates ? `
                        <button class="secondary-button" onclick="window.open('https://maps.google.com/?q=${institution.koordinat_lat},${institution.koordinat_lon}', '_blank')">
                            <span class="material-symbols-outlined">directions</span>
                            <span>Haritada Göster</span>
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }
}

// Global instances
const themeManager = new ThemeManager();
const institutionModal = new InstitutionModal();

// Global functions
function showInstitutionDetail(institutionId) {
    institutionModal.show(institutionId);
}
