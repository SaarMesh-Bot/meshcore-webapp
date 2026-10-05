import os
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__));sim=open(os.path.join(D,'sim.js')).read()
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':700});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    dl=[];pg.on('dialog',lambda d:(dl.append(d.message),d.accept()))
    pg.add_init_script(sim);pg.goto('file://'+os.path.join(D,'../'+os.environ.get('MCW_PAGE','index.html')))
    pg.click('#btnTcp');pg.fill('#tcpHost','1.2.3.4');pg.click('#tcpOk');pg.wait_for_function('typeof S!=="undefined" && S.connected',timeout=10000);pg.wait_for_timeout(1500)
    t=pg.evaluate("""[
      linkify('🗺️ Region-Scope? Für das #Saarland gilt: saarlorlux. Infos: https://saarmesh.de/regions/'),
      linkify('Siehe (https://example.org/a_(b)) und www.saarmesh.de, ok?'),
      linkify('kein#hash, aber #Public und <b>x</b> & 50% #a'),
    ]""")
    for x in t:print(x)
    assert 'href="https://saarmesh.de/regions/"' in t[0] and 'data-ch="#saarland"' in t[0]
    assert 'href="https://www.saarmesh.de"' in t[1] and 'example.org/a_(b)"' in t[1]
    assert 'kein#hash' in t[2] and 'data-ch="#public"' in t[2] and '&lt;b&gt;' in t[2] and 'data-ch="#a"' not in t[2]
    pg.evaluate("S.msgs['ch:0']=[{dir:'in',from:'SaarMesh-Bot',text:'Region-Scope? Für das #Saarland gilt: saarlorlux. Infos: https://saarmesh.de/regions/ und #public',ts:Date.now(),rx:Date.now(),snr:11.5,hops:0}];S.active='ch:0';switchTab('chat')")
    pg.wait_for_timeout(300);pg.screenshot(path='link.png')
    pg.click('a.chlink[data-ch="#saarland"]');pg.wait_for_timeout(1500)
    print('dialog',dl);print('channels',pg.evaluate("S.channels.map(c=>c.name)"),'active',pg.evaluate('S.active'))
    pg.evaluate("S.active='ch:0';renderChat()");pg.wait_for_timeout(200)
    pg.click('a.chlink[data-ch="#public"]');pg.wait_for_timeout(300);print('active after #public',pg.evaluate('S.active'))
    print('ERR',errs);b.close()
