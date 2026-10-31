const CACHE_NAME = "marcelo-markets-v9-1-security-20261030";
const SHELL = ["./", "./index.html", "./manifest.json", "./logo.png", "./icon-192.png", "./icon-512.png"];
self.addEventListener("install", event => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL)));
});
self.addEventListener("activate", event => {
  event.waitUntil(Promise.all([
    self.clients.claim(),
    caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith("marcelo-") && k !== CACHE_NAME)
      .map(k => caches.delete(k))))
  ]));
});
self.addEventListener("fetch", event => {
  const req=event.request;
  if(req.method!=="GET") return;
  const url=new URL(req.url);
  // Never intercept any Supabase, Google-login, or other third-party requests.
  if(url.origin!==self.location.origin) return;
  const isDynamic = req.mode==="navigate" || /\/(index\.html|config\.js|manifest\.json|market_data\.json|offers\.json|service-worker\.js)$/.test(url.pathname);
  if(isDynamic){
    event.respondWith(fetch(req,{cache:"no-store"}).then(res=>{
      if(res.ok) {const copy=res.clone();caches.open(CACHE_NAME).then(c=>c.put(req,copy));}
      return res;
    }).catch(async()=> (await caches.match(req)) || Response.error()));
    return;
  }
  event.respondWith(caches.match(req).then(hit=>hit || fetch(req).then(res=>{
    if(res.ok) {const copy=res.clone();caches.open(CACHE_NAME).then(c=>c.put(req,copy));}
    return res;
  })));
});
