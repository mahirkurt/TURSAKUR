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
    '/styles/main.css',
    '/js/main.js',
    '/js/app.js',
    '/js/data-loader.js',
    '/js/search-filter.js'
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
                    if (cacheName !== STATIC_CACHE && cacheName !== DATA_CACHE) {
                        console.log('Eski önbellek temizleniyor:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('✅ Service Worker aktivasyonu tamamlandı');
            return self.clients.claim();
        })
    );
});

// Fetch olaylarını yakala
self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;
    
    const requestUrl = new URL(event.request.url);
    
    // Veri dosyaları için Network First stratejisi
    if (requestUrl.pathname.includes('/data/')) {
        event.respondWith(networkFirstStrategy(event.request, DATA_CACHE));
    } else {
        // Statik dosyalar için Cache First stratejisi
        event.respondWith(cacheFirstStrategy(event.request, STATIC_CACHE));
    }
});

// Cache First stratejisi
async function cacheFirstStrategy(request, cacheName) {
    try {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        cache.put(request, networkResponse.clone());
        return networkResponse;
    } catch (error) {
        console.log('Cache/Network hatası:', error);
        return new Response('Offline - İçerik kullanılamıyor', { status: 503 });
    }
}

// Network First stratejisi
async function networkFirstStrategy(request, cacheName) {
    try {
        const networkResponse = await fetch(request);
        const cache = await caches.open(cacheName);
        cache.put(request, networkResponse.clone());
        return networkResponse;
    } catch (error) {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        return new Response('Offline - Veri kullanılamıyor', { status: 503 });
    }
}
