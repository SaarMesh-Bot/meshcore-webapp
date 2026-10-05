// Service Worker der Meshcore Webapp: Offline-Start, Bibliotheken und angesehene Kartenkacheln zwischenspeichern
const BETA=self.registration.scope.includes('/beta/');
const APP=(BETA?'mcw-beta-app-':'mcw-app-')+'v1',LIB='mcw-lib-v1',TILE='mcw-tiles-v1',DATA=(BETA?'mcw-beta-data-':'mcw-data-')+'v1';
const CORE=['./','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
const TILE_HOST=/(^|\.)(arcgisonline\.com|tile\.openstreetmap\.org|tile\.opentopomap\.org)$/;
const LIB_HOST=/^(cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net)$/;
const MAX_TILES=4000;
self.addEventListener('install',e=>{e.waitUntil(caches.open(APP).then(c=>c.addAll(CORE)).catch(()=>{}).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil((async()=>{
  const own=BETA?['mcw-beta-app-','mcw-beta-data-']:['mcw-app-','mcw-data-'];
  for(const k of await caches.keys())if(own.some(p=>k.startsWith(p))&&k!==APP&&k!==DATA)await caches.delete(k);
  await self.clients.claim()})())});
async function netFirst(req,cache,fallback){
  try{const r=await fetch(req);if(r&&r.ok){const c=await caches.open(cache);c.put(req,r.clone())}return r}
  catch(e){const m=await caches.match(req,{ignoreSearch:true})||(fallback&&await caches.match(fallback));if(m)return m;throw e}
}
async function cacheFirst(req,cache){const m=await caches.match(req);if(m)return m;const r=await fetch(req);if(r&&r.ok){const c=await caches.open(cache);c.put(req,r.clone())}return r}
let putCount=0;
async function tile(req){
  const c=await caches.open(TILE),m=await c.match(req);if(m)return m;
  const r=await fetch(req);
  if(r&&r.ok&&r.type!=='opaque'){c.put(req,r.clone());if(++putCount%200===0)trimTiles(c)}
  return r;
}
async function trimTiles(c){const ks=await c.keys();if(ks.length>MAX_TILES)for(const k of ks.slice(0,ks.length-MAX_TILES))await c.delete(k)}
self.addEventListener('fetch',e=>{
  const req=e.request;if(req.method!=='GET')return;const u=new URL(req.url);
  if(u.origin===location.origin){
    if(req.mode==='navigate')return e.respondWith(netFirst(req,APP,'./'));
    if(/\.json$/.test(u.pathname))return e.respondWith(netFirst(req,DATA));
    return e.respondWith(netFirst(req,APP));
  }
  if(LIB_HOST.test(u.hostname))return e.respondWith(cacheFirst(req,LIB));
  if(TILE_HOST.test(u.hostname))return e.respondWith(tile(req));
});
self.addEventListener('notificationclick',e=>{
  e.notification.close();const conv=e.notification.data&&e.notification.data.conv;
  e.waitUntil((async()=>{const cs=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    const c=cs.find(x=>x.url.startsWith(self.registration.scope));
    if(c){await c.focus();c.postMessage({type:'open',conv});return}
    await self.clients.openWindow('./'+(conv?'?open='+encodeURIComponent(conv):''))})());
});
