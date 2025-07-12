/**
 * Service Worker
 * Offline çalışma ve önbellekleme için
 */

const CACHE_NAME = 'turkiye-saglik-v1.0.0';
const STATIC_CACHE = 'static-v1.0.0';
const DATA_CACHE = 'data-v1.0.0';

// Önbelleğe alınacak statik dosyalar
const STATIC_FILES = [
    '/',
    '/index.html',
    '/css/light.css',
    '/css/dark.css',
    '/css/light-hc.css',
    '/css/dark-hc.css',
    '/css/light-mc.css',
    '/css/dark-mc.css',
    '/styles/main.css',
    '/js/main.js',
    '/js/app.js',
    '/js/data-loader.js',
    '/js/search-filter.js',
    'https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap',
    'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200'
];

// Önbelleğe alınacak veri dosyaları
const DATA_FILES = [
    '/data/turkiye_saglik_kuruluslari.json'
];

// Service Worker kurulumu
self.addEventListener('install', (event) => {
    console.log('Service Worker kurulumu başlıyor...');
    
    event.waitUntil(
        Promise.all([
            // Statik dosyaları önbelleğe al
            caches.open(STATIC_CACHE).then((cache) => {
                console.log('Statik dosyalar önbelleğe alınıyor...');
                return cache.addAll(STATIC_FILES);
            }),
            // Veri dosyalarını önbelleğe al
            caches.open(DATA_CACHE).then((cache) => {
                console.log('Veri dosyaları önbelleğe alınıyor...');
                return cache.addAll(DATA_FILES);
            })
        ]).then(() => {
            console.log('✅ Service Worker kurulumu tamamlandı');
            // Yeni service worker'ı hemen aktif et
            return self.skipWaiting();
        }).catch((error) => {
            console.error('❌ Service Worker kurulum hatası:', error);
        })
    );
});

// Service Worker aktivasyonu
self.addEventListener('activate', (event) => {
    console.log('Service Worker aktivasyonu başlıyor...');
    
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    // Eski önbellekleri temizle
                    if (cacheName !== STATIC_CACHE && cacheName !== DATA_CACHE) {
                        console.log('Eski önbellek temizleniyor:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('✅ Service Worker aktivasyonu tamamlandı');
            // Tüm istemcileri kontrol et
            return self.clients.claim();
        }).catch((error) => {
            console.error('❌ Service Worker aktivasyon hatası:', error);
        })
    );
});

// Fetch olaylarını yakala
self.addEventListener('fetch', (event) => {
    const requestUrl = new URL(event.request.url);
    
    // Sadece GET isteklerini yakala
    if (event.request.method !== 'GET') return;
    
    // Farklı dosya türleri için farklı stratejiler
    if (isDataRequest(requestUrl)) {
        // Veri dosyaları için: Network First stratejisi
        event.respondWith(networkFirstStrategy(event.request, DATA_CACHE));
    } else if (isStaticRequest(requestUrl)) {
        // Statik dosyalar için: Cache First stratejisi
        event.respondWith(cacheFirstStrategy(event.request, STATIC_CACHE));
    } else {
        // Diğer istekler için: Network First stratejisi
        event.respondWith(networkFirstStrategy(event.request, STATIC_CACHE));
    }
});

/**
 * Veri isteği kontrolü
 */
function isDataRequest(url) {
    return url.pathname.includes('/data/') || 
           url.pathname.endsWith('.json');
}

/**
 * Statik dosya isteği kontrolü
 */
function isStaticRequest(url) {
    return url.pathname.includes('/css/') ||
           url.pathname.includes('/js/') ||
           url.pathname.includes('/styles/') ||
           url.pathname.endsWith('.css') ||
           url.pathname.endsWith('.js') ||
           url.hostname === 'fonts.googleapis.com' ||
           url.hostname === 'fonts.gstatic.com';
}

/**
 * Cache First stratejisi
 * Önce önbellekte ara, bulamazsan network'ten al
 */
async function cacheFirstStrategy(request, cacheName) {
    try {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            // Önbellekte bulundu
            return cachedResponse;
        }
        
        // Önbellekte bulunamadı, network'ten al
        const networkResponse = await fetch(request);
        
        // Başarılı response'u önbelleğe al
        if (networkResponse && networkResponse.status === 200) {
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.error('Cache First stratejisi hatası:', error);
        
        // Offline fallback
        if (request.destination === 'document') {
            return caches.match('/index.html');
        }
        
        throw error;
    }
}

/**
 * Network First stratejisi
 * Önce network'ten al, başarısızsa önbellekte ara
 */
async function networkFirstStrategy(request, cacheName) {
    try {
        // Önce network'ten dene
        const networkResponse = await fetch(request);
        
        // Başarılı response'u önbelleğe al
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.warn('Network isteği başarısız, önbellekte aranıyor:', error);
        
        // Network başarısız, önbellekte ara
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Hem network hem önbellek başarısız
        if (request.destination === 'document') {
            // HTML sayfası için fallback
            const fallbackResponse = await cache.match('/index.html');
            if (fallbackResponse) {
                return fallbackResponse;
            }
        }
        
        throw error;
    }
}

// Mesaj olaylarını dinle
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME });
    }
    
    if (event.data && event.data.type === 'CLEAR_CACHE') {
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => caches.delete(cacheName))
            );
        }).then(() => {
            event.ports[0].postMessage({ success: true });
        });
    }
});

// Sync olaylarını dinle (background sync için)
self.addEventListener('sync', (event) => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

/**
 * Arka plan senkronizasyonu
 */
async function doBackgroundSync() {
    try {
        // Veri dosyasını güncelle
        const cache = await caches.open(DATA_CACHE);
        const response = await fetch('/data/turkiye_saglik_kuruluslari.json');
        
        if (response && response.status === 200) {
            await cache.put('/data/turkiye_saglik_kuruluslari.json', response.clone());
            console.log('✅ Arka plan senkronizasyonu tamamlandı');
        }
    } catch (error) {
        console.error('❌ Arka plan senkronizasyonu hatası:', error);
    }
}
