import sys,json
from playwright.sync_api import sync_playwright
from h import setup,connect,PAGE
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
errs,dl=[],[]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1100,'height':800});setup(pg,errs,dl);connect(pg,'file://'+PAGE)
    if pg.evaluate("typeof noteEcho==='undefined'"):print('SKIP: Seite hat noch keine Repeater-Echos');b.close();sys.exit(0)
    VK=pg.evaluate("[...S.contacts.values()].find(c=>c.name.startsWith('SaarRepeater')).key")
    SL=pg.evaluate("[...S.contacts.values()].find(c=>c.name.includes('Saarlouis')).key")
    pg.evaluate("S.active='ch:0';switchTab('chat')");pg.wait_for_timeout(200)
    pg.fill('#msgIn','Hallo Echo-Test');pg.press('#msgIn','Enter');pg.wait_for_timeout(500)
    ok(pg.evaluate("__sim.chanSent&&__sim.chanSent.includes('Hallo Echo-Test')"),'Kanalnachricht gesendet')
    pk=lambda path,snr,text='Hallo Echo-Test',frm=None: f"""(()=>{{const m=S.msgs['ch:0'].slice(-1)[0];noteEcho({{ptype:5,route:1,hopCount:{len(path)},path:{json.dumps(path)},snr:{snr},dec:{{text:'{text}',from:{frm or 'S.self.name'},ts:Math.floor(m.ts/1000),chSecret:S.channels[0].secret}}}})}})()"""
    pg.evaluate(pk([VK[:2]],7.5))
    pg.evaluate(pk([VK[:2],SL[:2]],-3.25))
    pg.evaluate(pk([VK[:2]],8))  # gleiches Echo nochmal
    pg.evaluate(pk([SL[:2]],2,'anderer Text'))  # passt nicht
    pg.evaluate(pk([SL[:2]],2,frm="'Fremder'"))  # anderer Absender
    pg.wait_for_timeout(400)
    e=pg.evaluate("S.msgs['ch:0'].slice(-1)[0].echo")
    ok(len(e)==2 and [x for x in e if x['h']==VK[:2]][0]['n']==2,'2 Repeater, Duplikat gezählt: '+str(e))
    t=pg.inner_text('#msgs .msg.out:last-child')
    ok('✓✓ 2 Repeater' in t,'Anzeige: '+t.replace('\n',' | '))
    pg.click('#msgs button.echo');pg.wait_for_timeout(200)
    ok('SaarRepeater' in pg.inner_text('.echolist') and 'Saarlouis' in pg.inner_text('.echolist'),'Liste aufklappbar')
    pg.screenshot(path='echo.png')
    # Direktnachricht (Flood): Quell-Hash = eigener Schlüssel, Ziel-Hash = Kontakt
    A=pg.evaluate("[...S.contacts.values()].find(c=>c.name==='Anna Handy').key")
    pg.evaluate(f"openChat('{A}')");pg.wait_for_timeout(200);pg.fill('#msgIn','DM Test');pg.press('#msgIn','Enter');pg.wait_for_timeout(600)
    pg.evaluate(f"noteEcho({{ptype:2,route:1,hopCount:1,path:['{VK[:2]}'],snr:4,dec:{{src:S.self.key.slice(0,2),dst:'{A[:2]}'}}}})");pg.wait_for_timeout(300)
    ok(len(pg.evaluate(f"S.msgs['c:{A[:12]}'].slice(-1)[0].echo||[]"))==1,'Echo für Direktnachricht')
    print('ERR',errs);b.close()
sys.exit(1 if F or errs else 0)
