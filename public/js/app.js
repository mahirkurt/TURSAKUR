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
                // En yakın .view-btn elementini bul (icon'a tıklandığında)
                const button = e.target.closest('.view-btn');
                const view = button ? button.dataset.view : null;
                if (view) {
                    this.changeView(view);
                }
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

        // DataLoader ile görünümü değiştir
        if (window.dataLoader && typeof window.dataLoader.setViewMode === 'function') {
            window.dataLoader.setViewMode(view);
            window.dataLoader.renderResults();
        }

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

/**
 * Hukuki sayfa göster
 */
function showLegalPage(pageType) {
    const modal = document.createElement('div');
    modal.className = 'legal-modal';
    modal.innerHTML = getLegalContent(pageType);
    
    document.body.appendChild(modal);
    
    // Modal kapatma fonksiyonu
    modal.addEventListener('click', (e) => {
        if (e.target === modal || e.target.classList.contains('close-modal')) {
            document.body.removeChild(modal);
        }
    });
    
    // ESC tuşu ile kapatma
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            document.body.removeChild(modal);
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
}

/**
 * Hukuki içerik al
 */
function getLegalContent(pageType) {
    const contents = {
        privacy: {
            title: 'Gizlilik Politikası',
            content: `
                <h3>Veri Toplama ve Kullanım</h3>
                <p>TURSAKUR projesi, halka açık sağlık kuruluşu bilgilerini toplar ve sunar. Kişisel veri toplanmaz.</p>
                
                <h3>Çerezler</h3>
                <p>Bu site, kullanıcı deneyimini iyileştirmek için minimal çerez kullanır.</p>
                
                <h3>Veri Güvenliği</h3>
                <p>Tüm veriler güvenli bir şekilde saklanır ve işlenir.</p>
            `
        },
        terms: {
            title: 'Kullanım Koşulları',
            content: `
                <h3>Kabul Edilen Kullanım</h3>
                <p>Bu hizmet, sağlık kuruluşları hakkında bilgi edinmek için kullanılabilir.</p>
                
                <h3>Yasaklanan Kullanım</h3>
                <p>Otomatik veri çekme, spam veya zararlı aktiviteler yasaktır.</p>
                
                <h3>Sorumluluk</h3>
                <p>Veriler "olduğu gibi" sunulur. Doğruluk garantisi verilmez.</p>
            `
        },
        kvkk: {
            title: 'KVKK Bildirimi',
            content: `
                <h3>Veri Sorumlusu</h3>
                <p>TURSAKUR projesi, 6698 sayılı KVKK kapsamında veri sorumlusudur.</p>
                
                <h3>İşlenen Veriler</h3>
                <p>Sadece halka açık sağlık kuruluşu verileri işlenir.</p>
                
                <h3>Hakların Kullanımı</h3>
                <p>KVKK kapsamındaki haklarınız için iletişime geçebilirsiniz.</p>
            `
        },
        about: {
            title: 'Hakkımızda',
            content: `
                <h3>Proje Amacı</h3>
                <p>TURSAKUR, Türkiye'deki sağlık kuruluşlarının açık ve erişilebilir bir veritabanını oluşturmayı amaçlar.</p>
                
                <h3>Açık Kaynak</h3>
                <p>Bu proje açık kaynak kodludur ve herkesin katkısına açıktır.</p>
                
                <h3>Veri Kaynakları</h3>
                <p>Veriler Sağlık Bakanlığı ve diğer resmi kaynaklardan toplanır.</p>
            `
        },
        api: {
            title: 'API Dokümantasyonu',
            content: `
                <h3>JSON API</h3>
                <p>Veriler JSON formatında <code>/data/turkiye_saglik_kuruluslari.json</code> adresinden erişilebilir.</p>
                
                <h3>Veri Yapısı</h3>
                <p>Her kurum için: kurum_id, kurum_adi, kurum_tipi, adres, telefon, koordinatlar vb. bilgiler bulunur.</p>
                
                <h3>Kullanım Sınırları</h3>
                <p>Makul kullanım politikası geçerlidir. Aşırı trafik engellenir.</p>
            `
        },
        contribute: {
            title: 'Katkıda Bulun',
            content: `
                <h3>GitHub Projesi</h3>
                <p>Projeye <a href="https://github.com/mahirkurt/TURSAKUR" target="_blank">GitHub</a> üzerinden katkıda bulunabilirsiniz.</p>
                
                <h3>Veri Güncellemeleri</h3>
                <p>Hatalı veya eksik verileri bildirerek projeye destek olabilirsiniz.</p>
                
                <h3>Kod Katkıları</h3>
                <p>Yeni özellikler, hata düzeltmeleri ve iyileştirmeler için pull request açabilirsiniz.</p>
            `
        },
        contact: {
            title: 'İletişim',
            content: `
                <h3>GitHub Issues</h3>
                <p>Teknik sorunlar için <a href="https://github.com/mahirkurt/TURSAKUR/issues" target="_blank">GitHub Issues</a> kullanın.</p>
                
                <h3>E-posta</h3>
                <p>Genel sorularınız için projenin GitHub sayfasından iletişim bilgilerine ulaşabilirsiniz.</p>
                
                <h3>Topluluk</h3>
                <p>Açık kaynak topluluğu aracılığıyla destek alabilirsiniz.</p>
            `
        },
        sources: {
            title: 'Veri Kaynakları',
            content: `
                <h3>Resmi Kaynaklar</h3>
                <ul>
                    <li>T.C. Sağlık Bakanlığı - SHGM</li>
                    <li>Üniversite Hastaneleri</li>
                    <li>Özel Hastaneler Birliği</li>
                </ul>
                
                <h3>Veri Toplama</h3>
                <p>Veriler halka açık web sitelerinden otomatik olarak toplanır.</p>
                
                <h3>Güncelleme Sıklığı</h3>
                <p>Veriler düzenli olarak güncellenir ve versiyonlanır.</p>
            `
        }
    };
    
    const content = contents[pageType] || { title: 'Sayfa Bulunamadı', content: '<p>İstenen sayfa bulunamadı.</p>' };
    
    return `
        <div class="legal-modal-backdrop">
            <div class="legal-modal-content">
                <div class="legal-modal-header">
                    <h2>${content.title}</h2>
                    <button class="close-modal icon-button">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
                <div class="legal-modal-body">
                    ${content.content}
                </div>
                <div class="legal-modal-footer">
                    <button class="md-button-filled close-modal">Kapat</button>
                </div>
            </div>
        </div>
    `;
}
