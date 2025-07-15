/**
 * TURSAKUR Interactive Map Module
 * Provides interactive mapping functionality for healthcare institutions
 */

class TURSAKURMap {
    constructor() {
        this.map = null;
        this.markersLayer = null;
        this.hospitalData = [];
        this.currentFilter = 'all';
        this.userLocation = null;
        
        // Icon configurations
        this.hospitalIcons = {
            DEVLET_HASTANESI: L.divIcon({
                className: 'custom-hospital-icon devlet',
                html: '<span class="material-symbols-outlined">local_hospital</span>',
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32]
            }),
            OZEL_HASTANE: L.divIcon({
                className: 'custom-hospital-icon ozel',
                html: '<span class="material-symbols-outlined">business</span>',
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32]
            }),
            UNIVERSITE_HASTANESI: L.divIcon({
                className: 'custom-hospital-icon universite',
                html: '<span class="material-symbols-outlined">school</span>',
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32]
            }),
            EGITIM_ARASTIRMA_HASTANESI: L.divIcon({
                className: 'custom-hospital-icon egitim',
                html: '<span class="material-symbols-outlined">science</span>',
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32]
            }),
            DIS_SAGLIGI: L.divIcon({
                className: 'custom-hospital-icon dis',
                html: '<span class="material-symbols-outlined">dentistry</span>',
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32]
            })
        };
        
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.initMap();
        this.addEventListeners();
        this.displayMarkers();
        this.updateStats();
    }
    
    async loadData() {
        try {
            const response = await fetch('data/turkiye_saglik_kuruluslari.json');
            this.hospitalData = await response.json();
            console.log('Loaded hospitals:', this.hospitalData.length);
        } catch (error) {
            console.error('Error loading hospital data:', error);
        }
    }
    
    initMap() {
        // Initialize map centered on Turkey
        this.map = L.map('map', {
            center: [39.9334, 32.8597], // Ankara coordinates
            zoom: 6,
            zoomControl: false
        });
        
        // Add custom zoom control
        L.control.zoom({
            position: 'bottomleft'
        }).addTo(this.map);
        
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);
        
        // Initialize markers layer
        this.markersLayer = L.layerGroup().addTo(this.map);
        
        // Add scale control
        L.control.scale({
            position: 'bottomleft',
            metric: true,
            imperial: false
        }).addTo(this.map);
    }
    
    displayMarkers() {
        // Clear existing markers
        this.markersLayer.clearLayers();
        
        const filteredData = this.getFilteredData();
        
        filteredData.forEach(hospital => {
            if (hospital.koordinat_lat && hospital.koordinat_lon) {
                const marker = this.createMarker(hospital);
                this.markersLayer.addLayer(marker);
            }
        });
        
        this.updateStats();
    }
    
    createMarker(hospital) {
        const icon = this.hospitalIcons[hospital.kurum_tipi] || this.hospitalIcons.DEVLET_HASTANESI;
        
        const marker = L.marker([hospital.koordinat_lat, hospital.koordinat_lon], {
            icon: icon
        });
        
        const popupContent = this.createPopupContent(hospital);
        marker.bindPopup(popupContent, {
            maxWidth: 300,
            className: 'hospital-popup'
        });
        
        return marker;
    }
    
    createPopupContent(hospital) {
        const typeLabels = {
            'DEVLET_HASTANESI': 'Devlet Hastanesi',
            'OZEL_HASTANE': 'Özel Hastane',
            'UNIVERSITE_HASTANESI': 'Üniversite Hastanesi',
            'EGITIM_ARASTIRMA_HASTANESI': 'Eğitim Araştırma Hastanesi',
            'DIS_SAGLIGI': 'Diş Sağlığı Merkezi'
        };
        
        return `
            <div class="hospital-popup">
                <div class="popup-header">${hospital.kurum_adi}</div>
                <div class="popup-type">${typeLabels[hospital.kurum_tipi] || hospital.kurum_tipi}</div>
                <div class="popup-location">
                    <span class="material-symbols-outlined" style="font-size: 16px; vertical-align: middle;">location_on</span>
                    ${hospital.ilce_adi}, ${hospital.il_adi}
                </div>
                ${hospital.telefon ? `
                    <div style="color: var(--md-sys-color-on-surface-variant); font-size: 14px; margin-bottom: 8px;">
                        <span class="material-symbols-outlined" style="font-size: 16px; vertical-align: middle;">phone</span>
                        ${hospital.telefon}
                    </div>
                ` : ''}
                <div class="popup-actions">
                    <button class="popup-btn primary" onclick="mapInstance.showDirections(${hospital.koordinat_lat}, ${hospital.koordinat_lon})">
                        <span class="material-symbols-outlined" style="font-size: 14px;">directions</span>
                        Yol Tarifi
                    </button>
                    <button class="popup-btn secondary" onclick="mapInstance.showDetails('${hospital.kurum_id}')">
                        <span class="material-symbols-outlined" style="font-size: 14px;">info</span>
                        Detaylar
                    </button>
                </div>
            </div>
        `;
    }
    
    getFilteredData() {
        if (this.currentFilter === 'all') {
            return this.hospitalData;
        }
        return this.hospitalData.filter(hospital => hospital.kurum_tipi === this.currentFilter);
    }
    
    updateStats() {
        const filteredData = this.getFilteredData();
        
        const stats = {
            total: filteredData.length,
            devlet: filteredData.filter(h => h.kurum_tipi === 'DEVLET_HASTANESI').length,
            ozel: filteredData.filter(h => h.kurum_tipi === 'OZEL_HASTANE').length,
            universite: filteredData.filter(h => h.kurum_tipi === 'UNIVERSITE_HASTANESI').length
        };
        
        document.getElementById('total-visible').textContent = stats.total;
        document.getElementById('devlet-count').textContent = stats.devlet;
        document.getElementById('ozel-count').textContent = stats.ozel;
        document.getElementById('universite-count').textContent = stats.universite;
    }
    
    setFilter(filter) {
        this.currentFilter = filter;
        this.displayMarkers();
        
        // Update active button
        document.querySelectorAll('.map-control-btn[data-filter]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
    }
    
    locateUser() {
        if (navigator.geolocation) {
            const locateBtn = document.getElementById('locate-btn');
            locateBtn.innerHTML = '<span class="material-symbols-outlined">hourglass_empty</span> Konumunuz bulunuyor...';
            locateBtn.disabled = true;
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    this.userLocation = [lat, lon];
                    
                    // Add user location marker
                    if (this.userMarker) {
                        this.map.removeLayer(this.userMarker);
                    }
                    
                    this.userMarker = L.marker([lat, lon], {
                        icon: L.divIcon({
                            className: 'user-location-icon',
                            html: '<span class="material-symbols-outlined">person_pin_circle</span>',
                            iconSize: [40, 40],
                            iconAnchor: [20, 40]
                        })
                    }).addTo(this.map);
                    
                    // Center map on user location
                    this.map.setView([lat, lon], 12);
                    
                    // Find nearby hospitals
                    this.findNearbyHospitals(lat, lon);
                    
                    locateBtn.innerHTML = '<span class="material-symbols-outlined">my_location</span> Konumum';
                    locateBtn.disabled = false;
                },
                (error) => {
                    console.error('Geolocation error:', error);
                    alert('Konum alınamadı. Lütfen konum izinlerini kontrol edin.');
                    locateBtn.innerHTML = '<span class="material-symbols-outlined">my_location</span> Konumum';
                    locateBtn.disabled = false;
                }
            );
        } else {
            alert('Tarayıcınız konum hizmetlerini desteklemiyor.');
        }
    }
    
    findNearbyHospitals(userLat, userLon) {
        const nearbyHospitals = this.hospitalData
            .filter(hospital => hospital.koordinat_lat && hospital.koordinat_lon)
            .map(hospital => ({
                ...hospital,
                distance: this.calculateDistance(
                    userLat, userLon,
                    hospital.koordinat_lat, hospital.koordinat_lon
                )
            }))
            .sort((a, b) => a.distance - b.distance)
            .slice(0, 5);
        
        // Show nearby hospitals popup
        const nearbyList = nearbyHospitals
            .map(hospital => `
                <div style="margin-bottom: 8px; padding: 8px; background: var(--md-sys-color-surface-variant); border-radius: 6px;">
                    <strong>${hospital.kurum_adi}</strong><br>
                    <small>${hospital.ilce_adi}, ${hospital.il_adi} • ${hospital.distance.toFixed(1)} km</small>
                </div>
            `)
            .join('');
        
        const popup = L.popup()
            .setLatLng([userLat, userLon])
            .setContent(`
                <div style="max-width: 250px;">
                    <h4>En Yakın Hastaneler</h4>
                    ${nearbyList}
                </div>
            `)
            .openOn(this.map);
    }
    
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    showDirections(lat, lon) {
        if (this.userLocation) {
            const url = `https://www.google.com/maps/dir/${this.userLocation[0]},${this.userLocation[1]}/${lat},${lon}`;
            window.open(url, '_blank');
        } else {
            const url = `https://www.google.com/maps/search/${lat},${lon}`;
            window.open(url, '_blank');
        }
    }
    
    showDetails(kurumId) {
        const hospital = this.hospitalData.find(h => h.kurum_id === kurumId);
        if (hospital) {
            // Create detailed info modal (simplified for now)
            alert(`Detaylar:\n${hospital.kurum_adi}\n${hospital.adres || 'Adres bilgisi mevcut değil'}`);
        }
    }
    
    addEventListeners() {
        // Filter buttons
        document.querySelectorAll('.map-control-btn[data-filter]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filter = e.target.closest('.map-control-btn').dataset.filter;
                this.setFilter(filter);
            });
        });
        
        // Locate button
        document.getElementById('locate-btn').addEventListener('click', () => {
            this.locateUser();
        });
    }
}

// CSS for custom markers
const style = document.createElement('style');
style.textContent = `
    .custom-hospital-icon {
        border-radius: 50%;
        display: flex !important;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        border: 2px solid white;
    }
    
    .custom-hospital-icon.devlet {
        background: #1976d2;
    }
    
    .custom-hospital-icon.ozel {
        background: #388e3c;
    }
    
    .custom-hospital-icon.universite {
        background: #f57c00;
    }
    
    .custom-hospital-icon.egitim {
        background: #7b1fa2;
    }
    
    .custom-hospital-icon.dis {
        background: #d32f2f;
    }
    
    .user-location-icon {
        color: #2196f3;
        font-size: 40px !important;
        text-shadow: 0 0 10px rgba(33, 150, 243, 0.8);
    }
    
    .leaflet-popup-content-wrapper {
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .leaflet-popup-tip {
        border-radius: 2px;
    }
`;
document.head.appendChild(style);

// Initialize map when DOM is loaded
let mapInstance;
document.addEventListener('DOMContentLoaded', () => {
    mapInstance = new TURSAKURMap();
});
