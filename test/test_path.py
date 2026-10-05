import os,sys
from playwright.sync_api import sync_playwright
from h import setup,connect,PAGE as HPAGE
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
errs,dl=[],[]
PAGE=HPAGE
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':800});setup(pg,errs,dl);connect(pg,'file://'+PAGE)
    MER=pg.evaluate("[...S.contacts.values()].find(c=>c.name.includes('Merzig')).key")
    VK=pg.evaluate("[...S.contacts.values()].find(c=>c.name.startsWith('SaarRepeater')).key")
    SL=pg.evaluate("[...S.contacts.values()].find(c=>c.name.includes('Saarlouis')).key")
    pg.evaluate(f"openAdmin('{MER}')");pg.wait_for_timeout(200)
    ok('unbekannt (Flood)' in pg.inner_text('.admpath'),'Pfadzeile im Admin')
    pg.click('button[data-a=path]');pg.wait_for_timeout(200)
    pg.select_option('#peAdd',VK);pg.wait_for_timeout(100)
    ok(pg.locator('#pathBody .hop:not(.me)').count()==1,'Hop per Liste')
    pg.screenshot(path='pe_modal.png')
    pg.click('[data-pe=map]');pg.wait_for_timeout(1500)
    ok(not pg.is_hidden('#pathBar'),'Kartenleiste sichtbar')
    # Klick auf Saarlouis-Marker
    pg.evaluate(f"markers.get('{SL}').fire('click')");pg.wait_for_timeout(300)
    ok(pg.evaluate("PE.hops.length")==2,'Hop per Karte: %s'%pg.evaluate("PE.hops"))
    pg.evaluate(f"markers.get('{MER}').fire('click')");pg.wait_for_timeout(200);ok(pg.evaluate("PE.hops.length")==2,'Ziel nicht als Hop')
    pg.screenshot(path='pe_map.png')
    pg.click('#pathBar [data-pp=done]');pg.wait_for_timeout(200);ok(not pg.is_hidden('#pathModal'),'zurück im Dialog')
    pg.click('#peSave');pg.wait_for_timeout(800)
    r=pg.evaluate(f"(()=>{{const c=S.contacts.get('{MER}');return [c.outPathLen,pathDesc(c.outPathLen,c.outPath).hops]}})()")
    ok(r[0]==2 and r[1]==[VK[:2],SL[:2]],'Pfad gespeichert '+str(r))
    ok('SaarRepeater' in pg.inner_text('.admpath'),'Admin zeigt neuen Pfad: '+pg.inner_text('.admpath'))
    # 2-Byte
    pg.click('button[data-a=path]');pg.select_option('#peHs','2');pg.wait_for_timeout(100);pg.click('#peSave');pg.wait_for_timeout(800)
    r=pg.evaluate(f"(()=>{{const c=S.contacts.get('{MER}');return [c.outPathLen,pathDesc(c.outPathLen,c.outPath).hops]}})()")
    ok(r[0]==(1<<6|2) and r[1]==[VK[:4],SL[:4]],'2-Byte-Pfad '+str(r))
    pg.click('button[data-a=path]');pg.click('#peFlood');pg.wait_for_timeout(800)
    ok(pg.evaluate(f"S.contacts.get('{MER}').outPathLen")==255,'Flood zurückgesetzt')
    # Advert-Weg
    pg.evaluate(f"(()=>{{const n=S.nodes.get('{MER}');n.path=['{SL[:2]}','{VK[:2]}'];openPathEditor('{MER}')}})()");pg.wait_for_timeout(200)
    pg.click('[data-pe=adv]');ok(pg.evaluate("PE.hops")==[VK[:2],SL[:2]],'Weg des letzten Adverts umgekehrt')
    pg.fill('#peHex','zz');pg.click('[data-pe=hex]');pg.fill('#peHex','6a 29');pg.click('[data-pe=hex]');ok(pg.evaluate("PE.hops.length")==4,'Hex-Eingabe')
    print('ERR',errs);b.close()
sys.exit(1 if F or errs else 0)
