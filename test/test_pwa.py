import subprocess,time,os,sys
from playwright.sync_api import sync_playwright
from h import D,SIM,LF,ROOT
srv=subprocess.Popen([sys.executable,'-m','http.server','8123','--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
errs=[];F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
try:
  with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context();ctx.add_init_script(SIM)
    ctx.route('**/leaflet.min.js',lambda r:r.fulfill(path=LF+'leaflet.js',content_type='application/javascript'))
    ctx.route('**/leaflet.min.css',lambda r:r.fulfill(path=LF+'leaflet.css',content_type='text/css'))
    ctx.route('**/api.github.com/**',lambda r:r.fulfill(status=200,body='[]',content_type='application/json'))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://127.0.0.1:8123/');pg.wait_for_function("navigator.serviceWorker.controller!==null||new Promise(r=>navigator.serviceWorker.ready.then(()=>r(true)))",timeout=10000)
    pg.wait_for_timeout(1500)
    ok(pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!r&&r.active&&r.active.state)") in ('activated','activating'),'Service Worker aktiv')
    pg.reload();pg.wait_for_timeout(1000)
    ok(pg.evaluate("!!navigator.serviceWorker.controller"),'Seite wird vom SW gesteuert')
    man=pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json())");ok(man['display']=='standalone' and len(man['icons'])==3,'Manifest')
    keys=pg.evaluate("caches.keys()");ok(any(k.endswith('app-v1') for k in keys),'Caches '+str(keys))
    ctx.set_offline(True);pg.reload();pg.wait_for_timeout(1000)
    ok('Meshcore' in pg.title() and pg.locator('#btnTcp').count()==1,'Offline-Start funktioniert')
    ctx.set_offline(False)
    print('ERR',errs);b.close()
finally: srv.terminate()
sys.exit(1 if F else 0)
