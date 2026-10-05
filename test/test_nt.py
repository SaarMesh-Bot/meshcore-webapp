import os
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__));sim=open(os.path.join(D,'sim.js')).read();errs=[]
LF=os.path.join(D,'node_modules/leaflet/dist/')
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900})
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.add_init_script(sim)
    pg.route('**/leaflet.min.js',lambda r:r.fulfill(path=LF+'leaflet.js',content_type='application/javascript'))
    pg.route('**/leaflet.min.css',lambda r:r.fulfill(path=LF+'leaflet.css',content_type='text/css'))
    pg.route('**/server.arcgisonline.com/**',lambda r:r.fulfill(status=200,body=b'',content_type='image/png'))
    pg.goto('file://'+os.path.join(D,'../'+os.environ.get('MCW_PAGE','index.html')))
    pg.click('#btnTcp');pg.fill('#tcpHost','192.168.1.5');pg.click('#tcpOk')
    pg.wait_for_function('typeof S!=="undefined" && S.connected && S.contacts.size>=5',timeout=10000)
    # Discovery
    pg.click('[data-tab=tools]');pg.click('#btnDisc2')
    pg.wait_for_function("document.querySelector('#ntDisc').textContent.includes('3 Repeater geantwortet')",timeout=25000)
    t=pg.text_content('#ntDisc');assert 'SaarRepeater Völklingen' in t and 'Repeater Saarlouis' in t and '9.50' in t,t
    pg.click('#ntDisc button[data-nt=addrep]');pg.wait_for_timeout(800)
    pg.click('#btnDisc2');pg.wait_for_timeout(300)  # Sperre 30 s
    assert pg.evaluate('__sim.discCount')==1
    pg.screenshot(path=os.path.join(D,'nt_disc.png'))
    # Trace über Kontakt Saarbrücken (Pfad über Völklingen)
    pg.click('[data-tab=contacts]');pg.wait_for_timeout(300)
    pg.locator('#ctable tr',has_text='Repeater Saarbrücken').locator('button[title=Trace-Route]').click()
    pg.wait_for_function("document.querySelector('#ntTrace').textContent.includes('schwächste')",timeout=15000)
    hops=pg.evaluate('__sim.lastTrace');print('hops',hops);assert len(hops)==3 and hops[0]==hops[2]
    t=pg.text_content('#ntTrace');assert '8.00 dB' in t and '6.50 dB' in t and '2.00 dB' in t,t
    pg.screenshot(path=os.path.join(D,'nt_trace.png'))
    pg.click('#ntTrace button[data-nt=tracemap]');pg.wait_for_timeout(1500);pg.screenshot(path=os.path.join(D,'nt_tracemap.png'))
    # Manueller Trace mit unbekanntem Hop → Fehler
    pg.click('[data-tab=tools]');pg.fill('#trPath','ff');pg.click('#btnTrace')
    pg.wait_for_function("document.querySelector('#ntTrace').textContent.includes('Keine Antwort')",timeout=20000)
    # Kontakt ohne Pfad
    pg.click('[data-tab=contacts]');pg.wait_for_timeout(300)
    n=pg.locator('#ctable tr',has_text='Repeater Merzig').locator('button[title=Trace-Route]').count();print('merzig trace btn',n)
    if n:pg.locator('#ctable tr',has_text='Repeater Merzig').locator('button[title=Trace-Route]').click();pg.wait_for_timeout(500)
    print('ERRORS',errs);b.close()
print('OK')
