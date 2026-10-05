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
