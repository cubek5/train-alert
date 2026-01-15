// カスタムService Worker - キャッシュ戦略の最適化
const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `train-alert-${CACHE_VERSION}`;

// キャッシュする重要なリソース
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/flutter_bootstrap.js',
  '/flutter.js',
  '/main.dart.js',
  '/manifest.json',
  '/favicon.png',
  '/icons/Icon-192.png',
  '/icons/Icon-512.png'
];

// CanvasKitは大きいので別管理
const CANVASKIT_CACHE = 'canvaskit-cache-v1';

// インストール時: 重要なリソースをプリキャッシュ
self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Precaching core resources');
      return cache.addAll(PRECACHE_URLS);
    }).then(() => self.skipWaiting())
  );
});

// アクティベート時: 古いキャッシュを削除
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== CANVASKIT_CACHE) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// フェッチ時: キャッシュ戦略を適用
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // CanvasKitリソース: Cache First（長期キャッシュ）
  if (url.pathname.includes('/canvaskit/')) {
    event.respondWith(
      caches.open(CANVASKIT_CACHE).then((cache) => {
        return cache.match(request).then((cached) => {
          if (cached) {
            console.log('[SW] CanvasKit from cache:', url.pathname);
            return cached;
          }
          return fetch(request).then((response) => {
            if (response.status === 200) {
              cache.put(request, response.clone());
            }
            return response;
          });
        });
      })
    );
    return;
  }

  // APIリクエスト: Network First（常に最新）
  if (url.hostname.includes('render.com') || url.pathname.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          return response;
        })
        .catch(() => {
          // オフライン時のフォールバック
          return new Response(
            JSON.stringify({
              status: 'error',
              message: 'オフラインです。インターネット接続を確認してください。'
            }),
            { headers: { 'Content-Type': 'application/json' } }
          );
        })
    );
    return;
  }

  // その他のリソース: Cache First with Network Fallback
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) {
        // バックグラウンドで更新をチェック
        fetch(request).then((response) => {
          if (response.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, response);
            });
          }
        }).catch(() => {});
        return cached;
      }
      return fetch(request).then((response) => {
        if (response.status === 200 && request.method === 'GET') {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      });
    })
  );
});

// メッセージハンドラ: キャッシュクリア等
self.addEventListener('message', (event) => {
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
  if (event.data.action === 'clearCache') {
    event.waitUntil(
      caches.keys().then((names) => {
        return Promise.all(names.map((name) => caches.delete(name)));
      })
    );
  }
});
