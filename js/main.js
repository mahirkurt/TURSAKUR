/**
 * Main.js - Uygulama başlatıcısı
 * Tüm modülleri başlatır ve koordine eder
 */

// Sayfa yüklendiğinde çalıştır
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Türkiye Sağlık Kurumları uygulaması başlatılıyor...');
    
    // Uygulamayı başlat
    app.init();
    
    // Veri yükleyiciyi başlat
    dataLoader.loadData().then(() => {
        // Veri yüklendikten sonra arama ve filtreleri başlat
        searchFilter.init();
        console.log('✅ Uygulama başarıyla başlatıldı');
    }).catch(error => {
        console.error('❌ Uygulama başlatma hatası:', error);
        app.showToast('Uygulama başlatılırken bir hata oluştu', 'error');
    });
});

// Global fonksiyonlar
window.showInstitutionDetail = function(kurumId) {
    const kurum = dataLoader.getInstitutionById(kurumId);
    if (!kurum) {
        app.showToast('Kurum bilgisi bulunamadı', 'error');
        return;
    }

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
                                    <a href="${kurum.web_sitesi}" target="_blank" rel="noopener noreferrer">${kurum.web_sitesi}</a>
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
};

// Error handling
window.addEventListener('error', function(e) {
    console.error('❌ JavaScript hatası:', e.error);
    if (window.app) {
        app.showToast('Bir hata oluştu. Sayfayı yenilemeyi deneyin.', 'error');
    }
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('❌ Promise hatası:', e.reason);
    if (window.app) {
        app.showToast('Bir hata oluştu. Sayfayı yenilemeyi deneyin.', 'error');
    }
});
