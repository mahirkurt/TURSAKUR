/**
 * Main Application Entry Point
 * Uygulamanın ana başlangıç noktası
 */

// Uygulama başlatma
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🏥 Türkiye Sağlık Kurumları Veritabanı başlatılıyor...');
    
    try {
        // 1. Tema yöneticisini başlat
        themeManager.init();
        console.log('✅ Tema yöneticisi başlatıldı');

        // 2. Arama ve filtreleme modülünü başlat
        searchFilter.init();
        console.log('✅ Arama ve filtreleme modülü başlatıldı');

        // 3. URL parametrelerini yükle
        searchFilter.loadFromURL();
        console.log('✅ URL parametreleri yüklendi');

        // 4. Verileri yükle
        await dataLoader.loadData();
        console.log('✅ Veriler yüklendi');

        // 5. Ek UI event listener'larını ayarla
        setupAdditionalEventListeners();
        console.log('✅ Event listener\'lar ayarlandı');

        // 6. Sayfa yüklendiğinde filtreleri uygula
        searchFilter.applyFilters();
        console.log('✅ İlk filtreler uygulandı');

        console.log('🎉 Uygulama başarıyla başlatıldı!');

    } catch (error) {
        console.error('❌ Uygulama başlatılırken hata oluştu:', error);
        showApplicationError();
    }
});

/**
 * Ek UI event listener'larını ayarla
 */
function setupAdditionalEventListeners() {
    // Sayfa scroll olayları
    setupScrollEvents();
    
    // Klavye kısayolları
    setupKeyboardShortcuts();
    
    // Resize olayları
    setupResizeEvents();
    
    // Print olayları
    setupPrintEvents();
}

/**
 * Scroll olaylarını ayarla
 */
function setupScrollEvents() {
    let isScrolling = false;
    
    window.addEventListener('scroll', () => {
        if (!isScrolling) {
            window.requestAnimationFrame(() => {
                handleScroll();
                isScrolling = false;
            });
            isScrolling = true;
        }
    });
}

/**
 * Scroll işlemlerini ele al
 */
function handleScroll() {
    const scrollY = window.scrollY;
    const header = document.querySelector('.app-header');
    
    if (header) {
        // Header'ı scroll'da gizle/göster
        if (scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }
    
    // "Yukarı çık" butonunu göster/gizle
    const backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        if (scrollY > 300) {
            backToTopButton.style.display = 'flex';
        } else {
            backToTopButton.style.display = 'none';
        }
    }
}

/**
 * Klavye kısayollarını ayarla
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K: Arama kutusuna odaklan
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Ctrl/Cmd + /: Klavye kısayolları modalını göster
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            showKeyboardShortcuts();
        }
        
        // T: Tema değiştir
        if (e.key === 't' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            // Input alanında değilse
            if (!['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
                e.preventDefault();
                themeManager.toggleTheme();
            }
        }
    });
}

/**
 * Resize olaylarını ayarla
 */
function setupResizeEvents() {
    let resizeTimeout;
    
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            handleResize();
        }, 250);
    });
}

/**
 * Resize işlemlerini ele al
 */
function handleResize() {
    // Mobil/desktop görünüm değişikliklerini ele al
    const isMobile = window.innerWidth <= 768;
    document.body.classList.toggle('mobile', isMobile);
    
    // Grid layout'u yeniden hesapla
    const resultsGrid = document.getElementById('results-grid');
    if (resultsGrid) {
        // CSS Grid zaten responsive, ek işlem gerekmiyor
    }
}

/**
 * Print olaylarını ayarla
 */
function setupPrintEvents() {
    window.addEventListener('beforeprint', () => {
        // Print öncesi temizlik
        document.body.classList.add('printing');
    });
    
    window.addEventListener('afterprint', () => {
        // Print sonrası temizlik
        document.body.classList.remove('printing');
    });
}

/**
 * Klavye kısayolları modalını göster
 */
function showKeyboardShortcuts() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content keyboard-shortcuts-modal">
            <div class="modal-header">
                <h2>Klavye Kısayolları</h2>
                <button class="icon-button modal-close">
                    <span class="material-symbols-outlined">close</span>
                </button>
            </div>
            <div class="modal-body">
                <div class="shortcuts-grid">
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>K</kbd>
                        <span>Arama kutusuna odaklan</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>T</kbd>
                        <span>Tema değiştir</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Esc</kbd>
                        <span>Modalı kapat</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>/</kbd>
                        <span>Bu pencereyi göster</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.classList.add('show');
    
    // Event listeners
    const closeButton = modal.querySelector('.modal-close');
    closeButton.addEventListener('click', () => {
        modal.remove();
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

/**
 * Uygulama hatası göster
 */
function showApplicationError() {
    const appContainer = document.getElementById('app');
    if (appContainer) {
        appContainer.innerHTML = `
            <div class="error-page">
                <div class="error-content">
                    <span class="material-symbols-outlined error-icon">error</span>
                    <h1>Bir Hata Oluştu</h1>
                    <p>Uygulama başlatılırken beklenmeyen bir hata oluştu.</p>
                    <button class="primary-button" onclick="window.location.reload()">
                        <span class="material-symbols-outlined">refresh</span>
                        Sayfayı Yenile
                    </button>
                </div>
            </div>
        `;
    }
}

/**
 * Yukarı çık butonunu oluştur
 */
function createBackToTopButton() {
    const button = document.createElement('button');
    button.id = 'back-to-top';
    button.className = 'back-to-top-button';
    button.title = 'Sayfa başına dön';
    button.innerHTML = `
        <span class="material-symbols-outlined">keyboard_arrow_up</span>
    `;
    
    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.body.appendChild(button);
}

/**
 * Sayfa yüklendikten sonra ek özellikler
 */
window.addEventListener('load', () => {
    // Yukarı çık butonunu oluştur
    createBackToTopButton();
    
    // Service Worker'ı kaydet (eğer destekleniyorsa)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(() => console.log('✅ Service Worker kaydedildi'))
            .catch(() => console.log('ℹ️ Service Worker kaydedilemedi'));
    }
    
    // Analytics (eğer varsa)
    initializeAnalytics();
});

/**
 * Analytics başlat
 */
function initializeAnalytics() {
    // Google Analytics veya başka analytics servisi
    // Şimdilik boş, ileride eklenebilir
}

/**
 * Hata yakalama
 */
window.addEventListener('error', (e) => {
    console.error('Global hata:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Yakalanmamış promise hatası:', e.reason);
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        dataLoader,
        searchFilter,
        themeManager,
        institutionModal
    };
}
