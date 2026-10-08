import sys
from playwright.sync_api import sync_playwright
from h import setup,connect,PAGE
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':800});setup(pg,errs);connect(pg,'file://'+PAGE)
    VK=pg.evaluate("[...S.contacts.values()].find(c=>c.name.startsWith('SaarRepeater')).key")
    SL=pg.evaluate("[...S.contacts.values()].find(c=>c.name.includes('Saarlouis')).key")
    js="""([a,b])=>{const ch=S.channels[0];
      const mk=(path,snr)=>{const raw=new Uint8Array([0x15,path.length,...path.map(h=>parseInt(h,16)),parseInt(ch.hash,16),1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]);onRawPacket(raw,snr,-90)};
      mk([a.slice(0,2),b.slice(0,2)],8);mk(['ee'],3.25);
      const t=new TextEncoder().encode('Tester: Hallo Pfad');const f=new Uint8Array(12+t.length);f.set([17,32,0,0,ch.idx,2,0,1,2,3,4],0);f.set(t,11);
      handleMsgFrame(f.slice(0,11+t.length));
      S.active='ch:'+ch.idx;switchTab('chat');return S.msgs[S.active].at(-1).path}"""
    path=pg.evaluate(js,[VK,SL]);pg.wait_for_timeout(300)
    ok(path==[VK[:2],SL[:2]],'Pfad an Nachricht: %s'%path)
    pg.click('a.hoplink');pg.wait_for_timeout(200)
    t=pg.inner_text('.mpath');print(t)
    ok('SaarRepeater' in t and 'Saarlouis' in t and 'ich' in t,'Pfadkette mit Namen')
    ok('Auch gehört über' in t and 'ee' in t,'Alternativer Weg (Echo)')
    pg.screenshot(path='msgpath.png')
    pg.click('.mpath [data-ppkt]');pg.wait_for_timeout(300);ok(pg.evaluate("curTab")=='live' and pg.evaluate("S.selPkt")>0,'Sprung ins Paket')
    pg.evaluate("switchTab('chat')");pg.wait_for_timeout(200)
    pg.click('.mpath .acts [data-pmap]');pg.wait_for_timeout(1500);ok(pg.evaluate("curTab")=='map','Karte geöffnet')
    pg.evaluate("switchTab('chat')");pg.wait_for_timeout(200);pg.click('a.hoplink');pg.wait_for_timeout(200);ok(pg.locator('.mpath').count()==0,'zuklappen')
    print('ERR',errs);b.close()
sys.exit(1 if F or errs else 0)
