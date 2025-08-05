/**
 * TURSAKUR 2.0 - UI Components
 * ============================
 * 
 * Arayüz bileşenlerini (kartlar, listeler vb.) oluşturan ve yöneten modül.
 */

class UIComponents {
    constructor(containerSelector) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            console.error(`UI Temsilcisi: '${containerSelector}' selektörüne sahip konteyner bulunamadı.`);
        }
        console.log('🎨 UI Temsilcisi başlatıldı.');
    }

    /**
     * Verilen sağlık kuruluşları listesini arayüzde render eder.
     * @param {Array<Object>} facilities - Görüntülenecek sağlık kuruluşları dizisi.
     */
    renderFacilities(facilities) {
        if (!this.container) {
            console.error('Render edilecek konteyner yok.');
            return;
        }

        this.container.innerHTML = ''; // Konteyneri temizle

        if (!facilities || facilities.length === 0) {
            this.container.innerHTML = '<p class="info-message">Gösterilecek sağlık kuruluşu bulunamadı.</p>';
            return;
        }

        const fragment = document.createDocumentFragment();
        facilities.forEach(facility => {
            const card = this.createFacilityCard(facility);
            fragment.appendChild(card);
        });

        this.container.appendChild(fragment);
    }

    /**
     * Tek bir sağlık kuruluşu için bir kart elementi oluşturur.
     * @param {Object} facility - Sağlık kuruluşu veri objesi.
     * @returns {HTMLElement} - Oluşturulan kart elementi.
     */
    createFacilityCard(facility) {
        const card = document.createElement('article');
        card.className = 'kurum-card';
        card.dataset.id = facility.id || 'id-yok';
        card.setAttribute('role', 'link');
        card.setAttribute('tabindex', '0');

        const name = facility.name || 'İsimsiz Kurum';
        const type = facility.facility_type || 'Tip Belirtilmemiş';
        const province = facility.province || 'Konum';
        const district = facility.district || 'Belirtilmemiş';
        const location = `${province} / ${district}`;
        const iconChar = name.charAt(0).toUpperCase();

        card.innerHTML = `
            <div class="kurum-header">
                <div class="kurum-icon" aria-hidden="true">${iconChar}</div>
                <div class="kurum-content">
                    <h3 class="kurum-title">${name}</h3>
                    <div class="kurum-type">${type}</div>
                </div>
            </div>
            <div class="kurum-location">
                <span class="material-symbols-outlined">location_on</span>
                <span>${location}</span>
            </div>
            <div class="kurum-details">
                ${facility.phone ? `<div class="detail-item"><span class="material-symbols-outlined">call</span><span>${facility.phone}</span></div>` : ''}
            </div>
            <div class="kurum-actions">
                <button class="kurum-action-btn">Detayları Gör</button>
            </div>
        `;
        
        card.addEventListener('click', () => {
            window.location.href = `kurum-detay.html?id=${facility.id}`;
        });

        return card;
    }
}
