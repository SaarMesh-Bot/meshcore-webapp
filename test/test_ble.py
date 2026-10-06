import os
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__))
FAKE="""
window.__att=0;
navigator.bluetooth={requestDevice:async()=>({name:'MeshCore-Mathias',addEventListener(){},gatt:{connect:async()=>{window.__att++;throw new DOMException('Connection Error: Connection attempt failed.','NetworkError')},disconnect(){}}})};
"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(FAKE);pg.goto('file://'+os.path.join(D,'../'+os.environ.get('MCW_PAGE','index.html')));pg.click('#btnBle')
    pg.wait_for_selector('#bleModal:not([hidden])',timeout=15000)
    print('attempts',pg.evaluate('__att'));pg.screenshot(path='ble_modal.png')
    pg.click('#bleRetry');pg.wait_for_timeout(6000);print('attempts after retry',pg.evaluate('__att'),'modal',pg.locator('#bleModal').is_visible())
    print('ERR',errs);b.close()

# Android-Koppeln: erster Dienstabruf scheitert, weil die PIN-Eingabe die Verbindung trennt
FAKE2="""
window.__c=0;window.__svc=0;
const ch={addEventListener(){},removeEventListener(){},startNotifications:async()=>{},writeValue:async()=>{}};
const gatt={connected:false,connect:async()=>{window.__c++;gatt.connected=true;return gatt},disconnect(){gatt.connected=false},
  getPrimaryService:async()=>{window.__svc++;if(window.__svc===1){gatt.connected=false;throw new DOMException('GATT Server is disconnected. Cannot retrieve services. (Re)connect first with `device.gatt.connect`.','NetworkError')}return {getCharacteristic:async()=>ch}}};
navigator.bluetooth={requestDevice:async()=>({name:'MeshCore-T1',addEventListener(){},gatt})};
"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(FAKE2);pg.goto('file://'+os.path.join(D,'../'+os.environ.get('MCW_PAGE','index.html')))
    r=pg.evaluate("(async()=>{const t=new BleTransport();t.onFrame=()=>{};try{await t.open();return ['ok',__c,__svc,t.ready||null]}catch(e){return ['err',e.message,e.detail||'',__c,__svc]}})()")
    print('pairing',r)
    if pg.evaluate("typeof BleTransport.prototype.open==='function'&&BleTransport.toString().includes('PIN-Eingabe')"):
        assert r[0]=='ok' and r[1]==2 and r[2]==2,r
    print('ERR',errs);b.close()
