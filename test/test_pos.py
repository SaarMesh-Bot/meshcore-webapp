import os,sys
from playwright.sync_api import sync_playwright
from h import setup,connect,PAGE
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
errs,dl=[],[]
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':1280,'height':900},geolocation={'latitude':49.3170,'longitude':6.7510,'accuracy':12},permissions=['geolocation'])
    pg=ctx.new_page();setup(pg,errs,dl);connect(pg,'file://'+PAGE)
    if pg.evaluate("typeof initPosition==='undefined'"):print('SKIP: Seite hat noch keine Standort-Quelle');b.close();sys.exit(0)
    pg.click('[data-tab=device]');pg.wait_for_timeout(400)
    ok(pg.evaluate("hasGps()&&!gpsOn()"),'GPS-Modul erkannt, aus')
    ok('Fest eingestellt' in pg.inner_text('#kvPos'),'Quelle fest')
    pg.select_option('#posMode','gps');pg.wait_for_timeout(600)
    ok(pg.evaluate("__sim.vars.gps")=='1' and 'gps_interval:60' in pg.evaluate("__sim.varLog"),'GPS eingeschaltet + Intervall')
    pg.select_option('#gpsInt','300');pg.wait_for_timeout(400);ok('gps_interval:300' in pg.evaluate("__sim.varLog"),'Intervall geändert')
    pg.select_option('#posMode','phone');pg.wait_for_timeout(2500)
    ok(pg.evaluate("__sim.vars.gps")=='0','GPS beim Wechsel aufs Handy aus (Nachfrage bestätigt)')
    r=pg.evaluate("[S.self.lat,S.self.lon]");ok(abs(r[0]-49.317)<1e-4 and abs(r[1]-6.751)<1e-4,'Handy-Position übernommen '+str(r))
    pg.screenshot(path='pos_phone.png',full_page=True)
    # Bewegung < 100 m → keine Übernahme
    ctx.set_geolocation({'latitude':49.3172,'longitude':6.7510,'accuracy':10});pg.wait_for_timeout(1500)
    ok(abs(pg.evaluate("S.self.lat")-49.317)<1e-5,'kleine Bewegung ignoriert')
    # ungefähr → gerundet
    pg.uncheck('#posExact');pg.evaluate("GPS.lastSentT=0");pg.click('[data-pos=now]');pg.wait_for_timeout(1500)
    ok(pg.evaluate("S.self.lat")==49.32 and pg.evaluate("S.self.lon")==6.75,'gerundet: '+str(pg.evaluate("[S.self.lat,S.self.lon]")))
    # feste Position setzen → Quelle zurück auf fest
    pg.select_option('#posMode','manual');pg.wait_for_timeout(400)
    pg.fill('#setLat','49.2');pg.fill('#setLon','7.0');pg.click('#btnSetPos');pg.wait_for_timeout(800)
    ok(pg.evaluate("[S.self.lat,S.self.lon,GPS.mode]")==[49.2,7.0,'manual'],'feste Position')
    pg.uncheck('#setLocAdv');pg.wait_for_timeout(500);ok(pg.evaluate("__sim.locp")==0 and 'nicht mitgesendet' in pg.inner_text('#kvPos'),'Standort in Adverts aus')
    pg.evaluate("__sim.vars=null");pg.evaluate("initPosition()");pg.wait_for_timeout(400)
    ok(pg.locator('#posMode option[value=gps][disabled]').count()==1,'ohne GPS-Modul deaktiviert')
    print('ERR',errs);b.close()
sys.exit(1 if F or errs else 0)
