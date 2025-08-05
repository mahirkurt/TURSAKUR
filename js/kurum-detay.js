/**
 * TURSAKUR 2.0 - Kurum Detay Sayfası Mantığı
 * ==========================================
 * 
 * URL'den kurum ID'sini alarak ilgili kurumun detaylarını
 * yükler ve ekranda gösterir.
 */

document.addEventListener('DOMContentLoaded', async () => {
    const dataLoader = window.tursakurDataLoader;
    const mainContent = document.getElementById('kurum-detay-main-content');
    const breadcrumb = document.getElementById('breadcrumb-kurum-adi');

    if (!dataLoader || !mainContent) {
        console.error('Gerekli bileşenler (dataLoader veya mainContent) bulunamadı.');
        mainContent.innerHTML = '<p class="error-message">Sayfa yüklenirken bir hata oluştu. Lütfen ana sayfaya dönüp tekrar deneyin.</p>';
        return;
    }

    const getKurumIdFromUrl = () => {
        const params = new URLSearchParams(window.location.search);
        return params.get('id');
    };

    const loadAndRenderKurumDetay = async () => {
        const kurumId = getKurumIdFromUrl();
        if (!kurumId) {
            mainContent.innerHTML = '<p class="error-message">Kurum ID\'si bulunamadı. Lütfen geçerli bir kurum seçin.</p>';
            return;
        }

        try {
            // Veri yükleyicinin hazır olduğundan emin ol
            await dataLoader.initializeApp();
            
            const kurum = await dataLoader.getFacilityById(kurumId);

            if (kurum) {
                renderKurumDetay(kurum);
                if (breadcrumb) {
                    breadcrumb.textContent = kurum.name;
                }
                document.title = `${kurum.name} - TURSAKUR Sağlık Kuruluşları Rehberi`;
            } else {
                mainContent.innerHTML = `<p class="error-message">ID'si ${kurumId} olan kurum bulunamadı.</p>`;
                if (breadcrumb) {
                    breadcrumb.textContent = "Kurum Bulunamadı";
                }
            }
        } catch (error) {
            console.error('Kurum detayı yüklenirken hata:', error);
            mainContent.innerHTML = '<p class="error-message">Kurum bilgileri yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.</p>';
        }
    };

    const renderKurumDetay = (kurum) => {
        if (!kurum) {
            mainContent.innerHTML = '<p>Aradığınız kurum bulunamadı veya bilgileri eksik. Lütfen ana sayfaya dönüp tekrar deneyin.</p>';
            document.title = 'Kurum Bulunamadı - TURSAKUR';
            return;
        }

        document.title = `${kurum.name} - TURSAKUR`;

        const iconLetter = kurum.name ? kurum.name.charAt(0).toUpperCase() : 'H';
        const location = kurum.district && kurum.province ? `${kurum.district}, ${kurum.province}` : kurum.province || 'Konum Belirtilmemiş';

        mainContent.innerHTML = `
            <header class="kurum-detay-header">
                <div class="kurum-detay-header-content">
                    <div class="kurum-detay-icon">${iconLetter}</div>
                    <div class="kurum-detay-info">
                        <h1 class="kurum-detay-title">${kurum.name}</h1>
                        <div class="kurum-detay-type">${kurum.facility_type}</div>
                        <div class="kurum-detay-location">
                            <span class="material-symbols-outlined">location_on</span>
                            <span>${location}</span>
                        </div>
                    </div>
                    <div class="kurum-detay-actions">
                        <button class="kurum-action-btn">
                            <span class="material-symbols-outlined">share</span> Paylaş
                        </button>
                        <button class="kurum-action-btn kurum-action-btn--outline">
                            <span class="material-symbols-outlined">bookmark_add</span> Kaydet
                        </button>
                    </div>
                </div>
            </header>

            <div class="kurum-detay-container">
                <main class="kurum-detay-main">
                    <section class="kurum-detay-card">
                        <h2 class="kurum-detay-card-title">
                            <span class="material-symbols-outlined kurum-detay-card-icon">info</span>
                            Genel Bilgiler
                        </h2>
                        <p>${kurum.description || 'Bu kurum için henüz bir açıklama eklenmemiştir.'}</p>
                    </section>

                    <section class="kurum-detay-card">
                        <h2 class="kurum-detay-card-title">
                            <span class="material-symbols-outlined kurum-detay-card-icon">medical_services</span>
                            Sunulan Hizmetler
                        </h2>
                        <div class="kurum-hizmetler">
                            ${renderHizmetler(kurum.services)}
                        </div>
                    </section>
                </main>

                <aside class="kurum-detay-sidebar">
                    <section class="kurum-detay-card">
                        <h2 class="kurum-detay-card-title">
                            <span class="material-symbols-outlined kurum-detay-card-icon">contacts</span>
                            İletişim Bilgileri
                        </h2>
                        <div class="kurum-iletisim-listesi">
                            ${renderIletisim("Telefon", kurum.phone, "call")}
                            ${renderIletisim("Web Sitesi", kurum.website, "language", true)}
                            ${renderIletisim("Adres", kurum.address, "location_on")}
                        </div>
                    </section>

                    <section class="kurum-detay-card">
                        <h2 class="kurum-detay-card-title">
                            <span class="material-symbols-outlined kurum-detay-card-icon">schedule</span>
                            Çalışma Saatleri
                        </h2>
                        <div class="calisma-saatleri">
                            ${renderCalismaSaatleri(kurum.hours)}
                        </div>
                    </section>
                </aside>
            </div>
        `;
    };

    const renderIletisim = (label, value, icon, isLink = false) => {
        if (!value) return '';

        const valueHtml = isLink ? `<a href="${value}" target="_blank" rel="noopener noreferrer">${value.replace(/^(https?:\/\/)?(www\.)?/, '')}</a>` : value;

        return `
            <div class="kurum-iletisim-item">
                <span class="material-symbols-outlined kurum-iletisim-icon" aria-hidden="true">${icon}</span>
                <div class="kurum-iletisim-content">
                    <div class="kurum-iletisim-label">${label}</div>
                    <div class="kurum-iletisim-value">${valueHtml}</div>
                </div>
            </div>
        `;
    };

    const renderHizmetler = (services) => {
        if (!services || services.length === 0) {
            return '<p>Belirtilen hizmet bulunmamaktadır.</p>';
        }
        return services.map(service => `<span class="hizmet-chip">${service}</span>`).join('');
    };

    const renderCalismaSaatleri = (hours) => {
        if (!hours) {
            return '<p>Çalışma saatleri belirtilmemiştir.</p>';
        }
        // Örnek bir yapı, gerçek veri modeline göre uyarlanmalı
        return `
            <div class="saat-item">
                <span>Hafta İçi</span>
                <span>${hours.weekday || 'Belirtilmemiş'}</span>
            </div>
            <div class="saat-item">
                <span>Hafta Sonu</span>
                <span>${hours.weekend || 'Belirtilmemiş'}</span>
            </div>
            <div class="saat-item">
                <span>Acil Servis</span>
                <span class="durum-aktif">${hours.emergency || '7/24'}</span>
            </div>
        `;
    };

    loadAndRenderKurumDetay();
});
