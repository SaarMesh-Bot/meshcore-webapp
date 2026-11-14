# Reichweite laut CoreScope: Observations und max. Hops einer gesendeten Nachricht (fetch gemockt)
import sys,json
from playwright.sync_api import sync_playwright
from h import setup,connect,PAGE
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
errs,dl=[],[]
RESP={'packet':{},'observation_count':5,'observations':[
  {'observer_id':'A','path_json':'[]'},{'observer_id':'A','path_json':'["F9D7A6"]'},
  {'observer_id':'B','path_json':'["F9D7A6","5000E4"]'},{'observer_id':'C','path_json':'["1F869D"]'},
  {'observer_id':'C','path_json':'["F9D7A6","955B4F"]'}]}
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1100,'height':800});setup(pg,errs,dl);connect(pg,'file://'+PAGE)
    if pg.evaluate("typeof csObs==='undefined'"):print('SKIP: Seite hat noch keine CoreScope-Reichweite');b.close();sys.exit(0)
    pg.evaluate("""R=>{window.__csCalls=[];const of=window.fetch;window.fetch=(u,o)=>{if(String(u).includes('/api/packets/')){__csCalls.push(String(u));
      return Promise.resolve(new Response(JSON.stringify(R),{status:200,headers:{'Content-Type':'application/json'}}))}return of(u,o)}}""",RESP)
    pg.evaluate("S.active='ch:0';switchTab('chat')");pg.wait_for_timeout(200)
    pg.fill('#msgIn','Hallo CS-Test');pg.press('#msgIn','Enter');pg.wait_for_timeout(500)
    VK=pg.evaluate("[...S.contacts.values()].find(c=>c.name.startsWith('SaarRepeater')).key")
    pg.evaluate(f"""(()=>{{const m=S.msgs['ch:0'].slice(-1)[0];noteEcho({{ptype:5,route:1,hopCount:1,path:['{VK[:2]}'],snr:7,phash:'81c8a8367a5ffd68',dec:{{text:'Hallo CS-Test',from:S.self.name,ts:Math.floor(m.ts/1000),chSecret:S.channels[0].secret}}}})}})()""")
    pg.wait_for_timeout(800)
    m=pg.evaluate("S.msgs['ch:0'].slice(-1)[0]")
    ok(m.get('phash')=='81c8a8367a5ffd68','Paket-Hash aus Echo übernommen')
    ok(pg.evaluate("__csCalls.length")==1 and pg.evaluate("__csCalls[0]").endswith('/api/packets/81c8a8367a5ffd68'),'CoreScope abgefragt: '+str(pg.evaluate("__csCalls")))
    cs=m.get('cs') or {}
    ok(cs.get('obs')==5 and cs.get('observers')==3 and cs.get('maxHops')==2,'Auswertung: '+str(cs))
    t=pg.inner_text('#msgs .msg.out:last-child')
    ok('👁 5 · max. 2 Hops' in t,'Anzeige: '+t.replace('\n',' | '))
    pg.evaluate("renderAll()");pg.wait_for_timeout(300)
    ok(pg.evaluate("__csCalls.length")==1,'kein erneuter Abruf innerhalb von 30 s')
    pg.click('#msgs button.echo');pg.wait_for_timeout(200)
    ok('5 Observations von 3 Observern' in pg.inner_text('.echolist'),'Details in der Liste')
    pg.screenshot(path='csobs.png')
    print('ERR',errs);b.close()
sys.exit(1 if F or errs else 0)
