import os,hashlib
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__));sim=open(os.path.join(D,'sim.js')).read()
payload=bytes([0x11])+b'\x22'*20   # GRP_TXT: Kanal-Hash + Daten
def pkt(path,ptype=5,route=1):
    return bytes([(ptype<<2)|route,len(path)])+bytes(path)+payload
exp=hashlib.sha256(bytes([5])+payload).hexdigest()[:16]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(sim);pg.goto('file://'+os.path.join(D,'../'+os.environ.get('MCW_PAGE','index.html')))
    pg.click('#btnTcp');pg.fill('#tcpHost','1.2.3.4');pg.click('#tcpOk');pg.wait_for_function('typeof S!=="undefined" && S.connected',timeout=10000);pg.wait_for_timeout(1500)
    for path,snr in [([0x68],4.5),([0x29,0x68],-2.0),([0x7b],9.25),([0x68],6.0)]:
        pg.evaluate(f"onRawPacket(new Uint8Array({list(pkt(path))}),{snr},-90)")
    pg.evaluate(f"onRawPacket(new Uint8Array({list(bytes([(3<<2)|2,0])+b'ABCD')}),3,-80)")  # ACK
    pg.wait_for_timeout(300)
    h=pg.evaluate("S.packets[0].phash");print('hash',h,'expected',exp);assert h==exp
    rows=pg.locator('#pkts tr').count();print('rows ungrouped',rows);assert rows==5
    pg.click('#btnGroup');pg.wait_for_timeout(300)
    rows=pg.locator('#pkts tr').count();print('rows grouped',rows);assert rows==2
    t=pg.locator('#pkts tr').nth(1).text_content();print(t);assert '×4' in t and '9.3' in t and '+2 Wege' in t
    pg.evaluate(f"onRawPacket(new Uint8Array({list(pkt([0x72]))}),1,-99)");pg.wait_for_timeout(500)
    assert '×5' in pg.locator('#pkts tr').nth(1).text_content()
    pg.locator('#pkts tr').nth(1).click();pg.wait_for_timeout(300)
    d=pg.text_content('#detail');assert '5× empfangen' in d and exp in d,d
    pg.locator('#detail tr[data-obs]').nth(2).click();pg.wait_for_timeout(200)
    pg.screenshot(path='grp.png')
    assert pg.evaluate("localStorage.getItem('mcw.groupHash')")=='true'
    print('ERR',errs);b.close()
print('OK')
