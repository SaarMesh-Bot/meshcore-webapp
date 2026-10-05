import os
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__));sim=open(os.path.join(D,'sim.js')).read();errs=[]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900})
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.add_init_script(sim)
    pg.goto('file://'+os.path.join(D,'../'+os.environ.get('MCW_PAGE','index.html')))
    pg.click('#btnTcp');pg.fill('#tcpHost','192.168.1.5');pg.click('#tcpOk')
    pg.wait_for_function('typeof S!=="undefined" && S.connected && S.contacts.size>=5',timeout=10000)
    # eigenes Gerät
    pg.click('[data-tab=device]');pg.click('#btnSelfTel')
    pg.wait_for_function("document.querySelector('#telBody').textContent.includes('Spannung')",timeout=8000)
    txt=pg.text_content('#telBody');assert '4,09 V' in txt and '23,8 °C' in txt and '1.013,2 hPa' in txt and '55,0 %' in txt,txt
    pg.click('#telBody button[data-tel=req]');pg.wait_for_function("document.querySelectorAll('#telBody .tspark').length>=3",timeout=8000)
    pg.screenshot(path=os.path.join(D,'tel_self.png'))
    pg.click('#telClose')
    # Freigabe ändern
    pg.select_option('#telBase','2');pg.wait_for_timeout(500);pg.select_option('#telLoc','1');pg.wait_for_timeout(500)
    assert pg.evaluate('__sim.telem')==(2|1<<2),pg.evaluate('__sim.telem')
    assert pg.evaluate('S.self.telem')==6
    # Companion-Kontakt
    pg.click('[data-tab=contacts]');pg.wait_for_timeout(300)
    pg.locator('#ctable tr',has_text='Anna Handy').locator('button[title=Telemetrie]').click()
    pg.click('#telBody button[data-tel=req]')
    pg.wait_for_function("document.querySelector('#telBody').textContent.includes('GPS')",timeout=8000)
    assert '49.3000, 6.9000' in pg.text_content('#telBody'),pg.text_content('#telBody')
    pg.click('#telClose')
    # Repeater im Admin
    pg.locator('#ctable tr',has_text='SaarRepeater').locator('button[title="Repeater-Admin"]').click()
    pg.fill('#admPw','geheim');pg.click('button[data-a=login]');pg.wait_for_selector('text=angemeldet als Admin',timeout=8000)
    pg.click('#admMain button[data-tel=req]');pg.wait_for_function("document.querySelector('#admMain .telbox').textContent.includes('Luftdruck')",timeout=8000)
    pg.select_option('#admMain select[data-tel=auto]','60')
    assert pg.evaluate("JSON.parse(localStorage.getItem('mcw.telAuto'))")
    pg.click('#admMain button[data-tel=req]');pg.wait_for_function("document.querySelectorAll('#admMain .tspark').length>=3",timeout=8000)
    pg.wait_for_timeout(300);pg.screenshot(path=os.path.join(D,'tel_admin.png'),full_page=True)
    hist=pg.evaluate("JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>k.startsWith('mcw.tel.')&&k!=='mcw.telAuto'))).length")
    print('hist',hist,'ERRORS',errs);b.close()
print('OK')
