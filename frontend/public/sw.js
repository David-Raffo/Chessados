// Service worker mínimo para que la app sea instalable como PWA.
// Cachea el motor WASM (pesa varios MB) y deja que el resto vaya a la red.
const CACHE = "chessados-v1";

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(["/stockfish/stockfish.js", "/stockfish/stockfish.wasm"])));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith("/stockfish/")) {
    e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request)));
  }
});
