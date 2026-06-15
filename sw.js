/* Remember: minimal offline shell cache */
const CACHE = 'remember-v6';
const SHARE_CACHE = 'rm-share';
const SHELL = ['./', './index.html', './manifest.json?v=5', './icon-192.png?v=5', './icon-512.png?v=5', './icon-192-maskable.png?v=5', './icon-512-maskable.png?v=5', './apple-touch-icon.png?v=5', './icon.svg?v=5'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()).catch(() => {}));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE && k !== SHARE_CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);
  // Share-target: a screenshot shared into Remember (POST). Stash the files, redirect into the app.
  if (req.method === 'POST' && url.searchParams.has('share-target')) {
    e.respondWith((async () => {
      try {
        const form = await req.formData();
        const files = form.getAll('files').filter(Boolean);
        const cache = await caches.open(SHARE_CACHE);
        await cache.put('/__shared_count__', new Response(String(files.length)));
        for (let i = 0; i < files.length; i++) {
          await cache.put('/__shared__' + i, new Response(files[i], { headers: { 'content-type': files[i].type || 'application/octet-stream' } }));
        }
      } catch (err) {}
      return Response.redirect('./?shared=1', 303);
    })());
    return;
  }
  if (req.method !== 'GET') return;
  // network-first for same-origin navigation/docs, cache-first for everything else (incl. fonts)
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then((res) => { caches.open(CACHE).then((c) => c.put('./index.html', res.clone())); return res; }).catch(() => caches.match('./index.html')));
    return;
  }
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res && res.status === 200 && (url.origin === self.location.origin || /fonts\.(googleapis|gstatic)\.com/.test(url.host))) {
        const cp = res.clone(); caches.open(CACHE).then((c) => c.put(req, cp));
      }
      return res;
    }).catch(() => hit))
  );
});
