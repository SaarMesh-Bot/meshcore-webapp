import os,json,sys
from playwright.sync_api import sync_playwright
# Verzeichnis mit Vermerk "stale" (Quelle gesperrt): Hinweis unter Gerät → Öffentliches Verzeichnis
D=os.path.dirname(os.path.abspath(__file__));sim=open(os.path.join(D,'sim.js')).read()
CAT={"v":1,"updated":"2026-10-16T08:13:30Z","source":"https://meshcore-analyzer.eu",
     "channels":[{"n":"#test","m":5},{"n":"#saarland","r":["de-sl"],"m":3}],"regions":["de-sl"]}
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
def run(pg,cat):
    pg.route('**/catalog.json*',lambda r:r.fulfill(status=200,body=json.dumps(cat),content_type='application/json',headers={'Access-Control-Allow-Origin':'*'}))
    pg.goto('file://'+os.path.join(D,'../'+os.environ.get('MCW_PAGE','index.html')))
    pg.click('#tabs button[data-tab="device"]');pg.wait_for_timeout(600)
    return pg.inner_text('#dirInfo')
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    pg=b.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.add_init_script(sim)
    t=run(pg,CAT)
    ok('2 Kanäle' in t and 'nicht erreichbar' not in t,'ohne Vermerk kein Hinweis')
    pg.close()
    pg=b.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.add_init_script(sim)
    t=run(pg,dict(CAT,stale={"since":"2026-10-22T18:19:52Z","reason":"HTTP 403"}))
    ok('Quelle seit 22.10.2026 nicht erreichbar (HTTP 403)' in t,'Hinweis bei gesperrter Quelle')
    ok('2 Kanäle' in t,'Kanäle bleiben nutzbar')
    ok(not errs,'keine JS-Fehler '+str(errs))
    b.close()
sys.exit(1 if F else 0)
