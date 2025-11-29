/**
 * VitaCare Pro - Service Worker
 * Enables offline functionality and caching
 */

const CACHE_NAME = 'vitacare-pro-v1';
const STATIC_ASSETS = [
    '/',
    '/static/css/vitacare-pro-enhancements.css',
    '/static/js/toast-notifications.js',
    '/static/js/loading-overlay.js',
    '/static/js/risk-gauge.js',
    '/static/js/form-validation.js',
    '/static/js/table-utilities.js'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => name !== CACHE_NAME)
                        .map((name) => caches.delete(name))
                );
            })
            .then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const { request } = event;

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Cache-first strategy for static assets
    if (request.url.includes('/static/')) {
        event.respondWith(
            caches.match(request)
                .then((cachedResponse) => {
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    return fetch(request).then((response) => {
                        // Cache the new response
                        if (response.status === 200) {
                            const responseClone = response.clone();
                            caches.open(CACHE_NAME).then((cache) => {
                                cache.put(request, responseClone);
                            });
                        }
                        return response;
                    });
                })
                .catch(() => {
                    // Return offline page if available
                    return caches.match('/offline.html');
                })
        );
        return;
    }

    // Network-first strategy for API calls and pages
    event.respondWith(
        fetch(request)
            .then((response) => {
                // Cache successful responses
                if (response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // Fallback to cache
                return caches.match(request)
                    .then((cachedResponse) => {
                        return cachedResponse || caches.match('/offline.html');
                    });
            })
    );
});
