/**
 * TURSAKUR 2.0 - Ana Sayfa JavaScript
 * ===================================
 * 
 * Uygulamanın ana giriş noktası. Gerekli modülleri başlatır ve
 * olayları yönetir.
 */

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 TURSAKUR 2.0 ana sayfa başlatılıyor...');

    const dataLoader = window.tursakurDataLoader;
    const ui = new UIComponents('#kurumlar-container');

    if (!dataLoader) {
        console.error('❌ Ana başlatma hatası: Data Loader bulunamadı. data-loader.js yüklendiğinden emin olun.');
        return;
    }

    try {
        // Uygulamanın veri altyapısını başlat
        await dataLoader.initializeApp();

        // Başlangıçta tüm kurumları yükle ve render et
        const initialFacilities = await dataLoader.loadHealthFacilities();
        ui.renderFacilities(initialFacilities);

        console.log('✅ TURSAKUR 2.0 ana sayfa başarıyla yüklendi ve ilk veriler gösterildi.');

    } catch (error) {
        console.error('❌ Ana sayfa başlatılırken bir hata oluştu:', error);
        const container = document.getElementById('kurumlar-container');
        if (container) {
            container.innerHTML = '<p class="error-message">Sağlık kurumları yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.</p>';
        }
    }

    // Arama ve filtreleme mantığı `search-filter.js` içinde yönetiliyor.
    // O dosya da DOMContentLoaded olayını dinleyerek kendi kendini başlatır.
});
