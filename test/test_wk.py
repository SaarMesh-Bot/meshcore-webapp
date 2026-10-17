import os,json,sys
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__));sim=open(os.path.join(D,'sim.js')).read()
ST={"generated":"2026-10-17T14:06:28Z","netz":{"repeater":328,"observer":19},"spam":{"health":"healthy","active_incidents":1,"active_traffic":0,"active_radio":0,"packets_15m":137,"typical_15m":76.0},
    "relevanz":{"region":388,"kritisch":5,"wichtig":15},"positionen":{"count":16},"statistik":{"error":"x"},
    "tropo":{"class":"normal","name":"Normal","peak_class":"leicht","peak_name":"Leicht erhöht","peak_at":"2026-10-19T13:00:00Z"}}
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    calls=[]
    def st(r):calls.append(r.request.url);r.fulfill(status=200,body=json.dumps(ST),content_type='application/json',headers={'Access-Control-Allow-Origin':'*'})
    pg.route('**/werkzeuge/status.json*',st)
    pg.add_init_script(sim);pg.goto('file://'+os.path.join(D,'../'+os.environ.get('MCW_PAGE','index.html')))
    pg.click('#tabs button[data-tab="tools"]');pg.wait_for_timeout(800)
    t=pg.inner_text('#wkList')
    ok(pg.locator('#wkList a').count()==6,'6 Werkzeuge ohne Verbindung')
    ok('328 Repeater aktiv' in t and '1 aktive Auffälligkeit' in t and '5 kritisch' in t and '16 auffällige Positionen' in t,'Status-Texte')
    ok('Status gerade nicht verfügbar' in t and 'Leicht erhöht ab' in t,'Fehler- und Tropo-Status')
    ok(pg.get_attribute('#wkList a[data-wk="spam"]','href')=='https://live.saarmesh.de/spam/','Link Spam-Monitor')
    ok(pg.get_attribute('#wkList a[data-wk="tropo"]','target')=='_blank','öffnet in neuem Tab')
    ok('Status von' in pg.inner_text('#wkUpd'),'Zeitstempel')
    pg.click('#tabs button[data-tab="live"]');pg.click('#tabs button[data-tab="tools"]');pg.wait_for_timeout(300)
    ok(len(calls)==1,'kein erneuter Abruf innerhalb 5 min (%d)'%len(calls))
    pg.screenshot(path='wk.png')
    pg.unroute('**/werkzeuge/status.json*');pg.route('**/werkzeuge/status.json*',lambda r:r.abort())
    pg.evaluate("WK.d=null;loadWk(true)");pg.wait_for_timeout(500)
    ok(pg.inner_text('#wkList').count('Status gerade nicht verfügbar')==6,'offline: Links bleiben, Status nicht verfügbar')
    ok(not errs,'keine JS-Fehler '+str(errs))
    b.close()
sys.exit(1 if F else 0)
