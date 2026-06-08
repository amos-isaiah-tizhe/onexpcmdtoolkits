/* OneXportal Toolkit — Service Worker
 * Strategy:
 *  - Precache the app shell (HTML, CSS, JS, data, icons) on install
 *  - NetworkFirst for HTML navigations (fresh when online, cache when offline)
 *  - CacheFirst for same-origin static assets (css/js/json/img/fonts)
 *  - Falls back to /offline.html if a navigation fails and isn't cached
 */
const VERSION = 'v1.0.0';
const STATIC_CACHE = `onexp-static-${VERSION}`;
const RUNTIME_CACHE = `onexp-runtime-${VERSION}`;

const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/termux-ops.html',
  '/git-termux.html',
  '/offline.html',
  '/manifest.webmanifest',
  '/assets/css/styles.css',
  '/assets/js/scripts.js',
  '/assets/data/commands-termux.json',
  '/assets/data/commands-git.json',
  '/img/favicon.png',
  '/img/logo.png',
  '/img/icon-192.png',
  '/img/icon-512.png',
  '/img/apple-touch-icon.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== STATIC_CACHE && k !== RUNTIME_CACHE)
            .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;

  // HTML navigations: network-first, fall back to cache, then offline page
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(RUNTIME_CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() =>
          caches.match(req).then((cached) => cached || caches.match('/offline.html'))
        )
    );
    return;
  }

  // Same-origin static assets: cache-first
  if (sameOrigin) {
    event.respondWith(
      caches.match(req).then((cached) => {
        return cached || fetch(req).then((res) => {
          const copy = res.clone();
          caches.open(RUNTIME_CACHE).then((c) => c.put(req, copy));
          return res;
        }).catch(() => cached);
      })
    );
    return;
  }

  // Cross-origin (fonts, font-awesome CDN): stale-while-revalidate
  event.respondWith(
    caches.match(req).then((cached) => {
      const network = fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(RUNTIME_CACHE).then((c) => c.put(req, copy));
        return res;
      }).catch(() => cached);
      return cached || network;
    })
  );
});
