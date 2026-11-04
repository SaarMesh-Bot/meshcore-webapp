import os,sys
from playwright.sync_api import sync_playwright
from h import setup,connect,PAGE
# Uhr des Companions im Gerät-Tab: Abweichung, Datum/Uhrzeit, Hinweis wenn sie vorgeht
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});setup(pg,errs);connect(pg,'file://'+PAGE)
    if pg.evaluate("typeof readClock==='undefined'"):print('SKIP: Seite hat noch keine Uhranzeige');b.close();sys.exit(0)
    pg.click('[data-tab=device]');pg.wait_for_timeout(400)
    t=pg.inner_text('#kvInfo');ok('Uhr' in t and 'stimmt' in t,'Uhr stimmt nach dem Verbinden')
    ok('UTC' in t,'Uhrzeit wird angezeigt')
    pg.evaluate("__sim.clockOff=7200");pg.click('#btnStats');pg.wait_for_timeout(800)
    t=pg.inner_text('#kvInfo');ok('+2 h' in t and 'geht vor' in t,'Abweichung +2 h erkannt')
    ok('nicht zurückstellen' in t,'Hinweis bei vorgehender Uhr')
    pg.click('#btnTime');pg.wait_for_timeout(800)
    ok('+2 h' in pg.inner_text('#kvInfo'),'Zurückstellen klappt nicht (wie die Firmware)')
    pg.evaluate("__sim.clockOff=-600");pg.click('#btnTime');pg.wait_for_timeout(800)
    t=pg.inner_text('#kvInfo');ok('stimmt' in t and 'nicht zurückstellen' not in t,'nachgehende Uhr wird gestellt')
    ok(not errs,'keine JS-Fehler '+str(errs))
    b.close()
sys.exit(1 if F else 0)
