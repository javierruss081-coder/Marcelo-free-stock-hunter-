const CACHE = "stock-hunter-v4-1";
const STATIC = ["./", "./index.html", "./manifest.json"];

self.addEventListener("install", event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(STATIC))
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    Promise.all([
      self.clients.claim(),
      caches.keys().then(keys =>
        Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
      )
    ])
  );
});

self.addEventListener("fetch", event => {
  const req = event.request;
  const url = new URL(req.url);

  // Only manage same-origin GET requests.
  if (req.method !== "GET" || url.origin !== self.location.origin) return;

  const isLiveData =
    url.pathname.endsWith("/offers.json") ||
    url.pathname.endsWith("/market_data.json");

  const isDocument = req.mode === "navigate" || url.pathname.endsWith("/index.html");

  // Network-first for the app shell and live data so GitHub updates appear quickly.
  if (isLiveData || isDocument) {
    event.respondWith(
      fetch(req, { cache: "no-store" })
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE).then(cache => cache.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // Cache-first for other same-origin static files.
  event.respondWith(
    caches.match(req).then(hit =>
      hit ||
      fetch(req).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(cache => cache.put(req, copy));
        return res;
      })
    )
  );
});
