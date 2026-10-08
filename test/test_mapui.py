import sys,random
from playwright.sync_api import sync_playwright
from h import setup,connect,PAGE
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
errs,dl=[],[]
random.seed(1)
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1300,'height':800});setup(pg,errs,dl);connect(pg,'file://'+PAGE)
    if pg.evaluate("typeof declutter==='undefined'"):print('SKIP: Seite hat noch keine kompakte Karte');b.close();sys.exit(0)
    # viele Knoten auf engem Raum
    js="const now=Date.now();"+"".join(f"S.nodes.set('{i:064x}',{{key:'{i:064x}',name:'Testknoten Nummer {i}',type:{random.choice([1,2,2,3])},lat:{49.3+random.gauss(0,.15)},lon:{6.9+random.gauss(0,.2)},heard:now-{random.randint(0,90000000)}}});" for i in range(1,201))
    pg.evaluate(js)
    pg.click('[data-tab=map]');pg.wait_for_timeout(400);pg.evaluate("renderMap();map.setView([49.3,6.9],9)");pg.wait_for_timeout(700)
    vis=lambda:pg.evaluate("$$('.leaflet-tooltip.lbl:not(.hid)').length");tot=lambda:pg.evaluate("$$('.leaflet-tooltip.lbl').length")
    v9,t9=vis(),tot()
    ok(t9>150 and 0<v9<t9,'Überlappende Namen ausgeblendet: %d von %d sichtbar'%(v9,t9))
    def overlaps():
        return pg.evaluate("""(()=>{const r=$$('.leaflet-tooltip.lbl:not(.hid)').map(e=>e.getBoundingClientRect());let n=0;
          for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){const a=r[i],b=r[j];if(a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top)n++}return n})()""")
    ok(overlaps()==0,'Sichtbare Namen überlappen nicht')
    pg.evaluate("map.setView([49.3,6.9],12)");pg.wait_for_timeout(700)
    ok(pg.evaluate("$('#map').classList.contains('zhi')"),'Große Marker ab Zoom 11')
    ok(overlaps()==0,'Auch nach Zoom keine Überlappung')
    pg.evaluate("map.setView([49.3,6.9],9)");pg.wait_for_timeout(700)
    # Typ-Chip per Klick
    n0=pg.evaluate("markers.size");pg.click('.chip:has(input[data-t="2"])');pg.wait_for_timeout(400)
    n1=pg.evaluate("markers.size");ok(n1<n0 and not pg.is_checked('input.mf[data-t="2"]'),'Chip blendet Repeater aus: %d → %d'%(n0,n1))
    pg.click('.chip:has(input[data-t="2"])');pg.wait_for_timeout(400);ok(pg.evaluate("markers.size")==n0,'Chip wieder an')
    # Namen aus/an
    pg.click('.chip:has(#mLabels)');pg.wait_for_timeout(300);ok(tot()==0,'Namen aus')
    pg.click('.chip:has(#mLabels)');pg.wait_for_timeout(500);ok(tot()>0,'Namen wieder an')
    # Panel einklappen + merken
    pg.click('#btnMpColl');pg.wait_for_timeout(100);ok(not pg.is_visible('#mapPanel .mpb') and pg.is_visible('#mapInfo'),'Panel eingeklappt, Info bleibt')
    ok(pg.evaluate("store.get('mcw.mapPanelColl',false)")==True,'Einklapp-Zustand gespeichert')
    pg.click('#btnMpColl');pg.wait_for_timeout(100);ok(pg.is_visible('#mapPanel .mpb'),'Panel wieder offen')
    pg.screenshot(path='mapui.png')
    print('ERR',errs);b.close()
sys.exit(1 if F or errs else 0)
