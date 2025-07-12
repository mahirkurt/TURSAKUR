/**
 * App.js - Ana uygulama modülü
 * Tema yönetimi ve genel UI işlevleri
 */

class App {
    constructor() {
        this.currentTheme = 'light';
        this.themes = ['light', 'dark', 'light-hc', 'dark-hc', 'light-mc', 'dark-mc'];
        this.themeIndex = 0;
    }

    /**
     * Uygulamayı başlat
     */
    init() {
        this.loadTheme();
        this.bindEvents();
        this.initServiceWorker();
    }

    /**
     * Event listener'ları bağla
     */
    bindEvents() {
        // Tema değiştirme butonu
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Hakkında butonu
        const infoButton = document.getElementById('info-button');
        if (infoButton) {
            infoButton.addEventListener('click', () => {
                this.showAboutModal();
            });
        }

        // Modal kapatma
        const closeModal = document.getElementById('close-modal');
        if (closeModal) {
            closeModal.addEventListener('click', () => {
                this.closeModal('detail-modal');
            });
        }

        const closeAbout = document.getElementById('close-about');
        if (closeAbout) {
            closeAbout.addEventListener('click', () => {
                this.closeModal('about-modal');
            });
        }

        // Modal overlay tıklama
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.closeModal(overlay.id);
                }
            });
        });

        // Görünüm değiştirme butonları
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.changeView(e.target.dataset.view);
            });
        });
    }

    /**
     * Tema yükle
     */
    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.currentTheme = savedTheme;
        this.themeIndex = this.themes.indexOf(savedTheme);
        this.applyTheme();
    }

    /**
     * Tema değiştir
     */
    toggleTheme() {
        this.themeIndex = (this.themeIndex + 1) % this.themes.length;
        this.currentTheme = this.themes[this.themeIndex];
        this.applyTheme();
        localStorage.setItem('theme', this.currentTheme);
    }

    /**
     * Temayı uygula
     */
    applyTheme() {
        // Tüm tema dosyalarını deaktive et
        this.themes.forEach(theme => {
            const link = document.getElementById(`theme-${theme}`);
            if (link) {
                link.disabled = true;
            }
        });

        // Aktif temayı etkinleştir
        const activeTheme = document.getElementById(`theme-${this.currentTheme}`);
        if (activeTheme) {
            activeTheme.disabled = false;
        }

        // Tema butonunu güncelle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('.material-symbols-outlined');
            if (icon) {
                icon.textContent = this.currentTheme.includes('dark') ? 'light_mode' : 'dark_mode';
            }
        }

        // Body'ye tema class'ı ekle
        document.body.className = `theme-${this.currentTheme}`;
    }

    /**
     * Hakkında modal'ını göster
     */
    showAboutModal() {
        const modal = document.getElementById('about-modal');
        if (modal) {
            modal.style.display = 'flex';
            document.body.classList.add('modal-open');
        }
    }

    /**
     * Modal kapat
     */
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    }

    /**
     * Görünüm değiştir
     */
    changeView(view) {
        // Aktif butonu güncelle
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-view="${view}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }

        // Görünüm logic'i burada implement edilecek
        console.log(`Görünüm değiştirildi: ${view}`);
    }

    /**
     * Service Worker'ı başlat
     */
    async initServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/sw.js');
                console.log('✅ Service Worker kayıt edildi');
            } catch (error) {
                console.log('❌ Service Worker kayıt hatası:', error);
            }
        }
    }

    /**
     * Toast bildirimi göster
     */
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-message">${message}</span>
            <button class="toast-close">
                <span class="material-symbols-outlined">close</span>
            </button>
        `;

        // Kapatma butonu
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });

        toastContainer.appendChild(toast);

        // Otomatik kapat
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
}

// Global instance
const app = new App();

/**
 * Kurum detayını göster
 */
function showInstitutionDetail(kurumId) {
    const kurum = dataLoader.getInstitutionById(kurumId);
    if (!kurum) return;

    const modal = document.getElementById('detail-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');

    if (!modal || !modalTitle || !modalBody) return;

    modalTitle.textContent = kurum.kurum_adi;
    
    modalBody.innerHTML = `
        <div class="institution-detail">
            <div class="detail-section">
                <h4>Genel Bilgiler</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">Kurum Tipi:</span>
                        <span class="detail-value">${kurum.kurum_tipi}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Kurum ID:</span>
                        <span class="detail-value">${kurum.kurum_id}</span>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h4>Konum Bilgileri</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">İl:</span>
                        <span class="detail-value">${kurum.il_adi}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">İlçe:</span>
                        <span class="detail-value">${kurum.ilce_adi}</span>
                    </div>
                    ${kurum.adres ? `
                        <div class="detail-item full-width">
                            <span class="detail-label">Adres:</span>
                            <span class="detail-value">${kurum.adres}</span>
                        </div>
                    ` : ''}
                </div>
            </div>

            ${kurum.telefon || kurum.web_sitesi ? `
                <div class="detail-section">
                    <h4>İletişim</h4>
                    <div class="detail-grid">
                        ${kurum.telefon ? `
                            <div class="detail-item">
                                <span class="detail-label">Telefon:</span>
                                <span class="detail-value">
                                    <a href="tel:${kurum.telefon}">${kurum.telefon}</a>
                                </span>
                            </div>
                        ` : ''}
                        ${kurum.web_sitesi ? `
                            <div class="detail-item">
                                <span class="detail-label">Web Sitesi:</span>
                                <span class="detail-value">
                                    <a href="${kurum.web_sitesi}" target="_blank">${kurum.web_sitesi}</a>
                                </span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}

            <div class="detail-section">
                <h4>Veri Bilgileri</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">Veri Kaynağı:</span>
                        <span class="detail-value">${kurum.veri_kaynagi || 'Bilinmiyor'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Son Güncelleme:</span>
                        <span class="detail-value">${kurum.son_guncelleme || 'Bilinmiyor'}</span>
                    </div>
                </div>
            </div>

            ${kurum.koordinat_lat && kurum.koordinat_lon ? `
                <div class="detail-actions">
                    <button class="action-button primary" onclick="window.open('https://maps.google.com/?q=${kurum.koordinat_lat},${kurum.koordinat_lon}', '_blank')">
                        <span class="material-symbols-outlined">directions</span>
                        Google Maps'te Aç
                    </button>
                </div>
            ` : ''}
        </div>
    `;

    modal.style.display = 'flex';
    document.body.classList.add('modal-open');
}
