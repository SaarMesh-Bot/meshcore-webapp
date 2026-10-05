import os, sys
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
sim = open(os.path.join(D, 'sim.js')).read()
errs, dialogs = [], []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 900})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: m.type == 'error' and errs.append('console: ' + m.text))
    def dlg(d):
        dialogs.append(d.message); d.accept()
    pg.on('dialog', dlg)
    pg.add_init_script(sim)
    LF=os.path.join(D,'node_modules/leaflet/dist/')
    pg.route('**/leaflet.min.js',lambda r:r.fulfill(path=LF+'leaflet.js',content_type='application/javascript'))
    pg.route('**/leaflet.min.css',lambda r:r.fulfill(path=LF+'leaflet.css',content_type='text/css'))
    pg.route('**/server.arcgisonline.com/**',lambda r:r.fulfill(status=200,body=b'',content_type='image/png'))
    pg.goto('file://' + os.path.join(D, '../'+os.environ.get('MCW_PAGE','index.html')))
    pg.click('#btnTcp'); pg.fill('#tcpHost', '192.168.1.5'); pg.click('#tcpOk')
    pg.wait_for_function('typeof S!=="undefined" && S.connected && S.contacts.size>=5', timeout=10000)
    # über die Kontakttabelle öffnen
    pg.click('[data-tab=contacts]'); pg.wait_for_timeout(300)
    pg.locator('#ctable tr', has_text='SaarRepeater Völklingen').locator('button[title="Repeater-Admin"]').click()
    pg.wait_for_timeout(300)
    assert pg.locator('#sec-admin.active').count() == 1
    # falsches Passwort
    pg.fill('#admPw', 'falsch'); pg.click('button[data-a=login]')
    pg.wait_for_function("document.querySelector('#admLog').textContent.includes('abgelehnt')", timeout=8000)
    # richtiges Passwort, merken
    pg.fill('#admPw', 'geheim'); pg.check('#admRemember'); pg.click('button[data-a=login]')
    pg.wait_for_selector('text=angemeldet als Admin', timeout=8000)
    pg.wait_for_function("document.querySelector('#admMain').textContent.includes('Laufzeit')", timeout=8000)
    pg.click('button[data-a=neigh]')
    pg.wait_for_function("document.querySelector('#admMain').textContent.includes('Repeater Merzig')", timeout=8000)
    pg.click('button[data-a=acl]')
    pg.wait_for_function("document.querySelector('#admMain').textContent.includes('Anna Handy')", timeout=8000)
    pg.click('button[data-a=info]')
    pg.wait_for_function("document.querySelector('#admMain').textContent.includes('v1.13.0')", timeout=8000)
    pg.click('button[data-a=loadset]')
    pg.wait_for_selector('#adm_flood_max', timeout=60000)
    assert pg.input_value('#adm_name') == 'SaarRepeater Völklingen', pg.input_value('#adm_name')
    assert pg.input_value('#adm_radio') == '869.618,62.5,8,8', pg.input_value('#adm_radio')
    pg.fill('#adm_name', 'SaarRepeater VK'); pg.select_option('#adm_repeat', 'off'); pg.fill('#adm_flood_max', '8')
    # Neuzeichnen darf Eingaben nicht verwerfen
    pg.click('button[data-a=status]'); pg.wait_for_timeout(1500)
    assert pg.input_value('#adm_name') == 'SaarRepeater VK', 'Eingabe verloren'
    pg.click('button[data-a=saveset]')
    pg.wait_for_function("__sim.settings['flood.max']==='8' && __sim.settings.repeat==='off' && __sim.settings.name==='SaarRepeater VK'", timeout=20000)
    # Terminal
    log = pg.text_content('#admLog'); assert '< >' not in log and '> SaarRepeater' not in log, log[-400:]
    pg.click('button[data-cli="neighbors"]')
    pg.wait_for_function("document.querySelector('#admLog').textContent.includes('13.5 dB')", timeout=8000)
    assert 'Repeater Saarbrücken' in pg.text_content('#admLog')
    pg.fill('#admCmd', 'ver'); pg.press('#admCmd', 'Enter')
    pg.wait_for_function("document.querySelector('#admLog').textContent.includes('Build')", timeout=8000)
    pg.click('button[data-cli="get radio"]')
    pg.wait_for_function("document.querySelector('#admLog').textContent.includes('869.6179809')", timeout=8000)
    pg.click('button[data-a=clock]'); pg.wait_for_function("document.querySelector('#admLog').textContent.includes('clock set')", timeout=8000)
    # CLI-Antworten dürfen nicht im Chat landen
    cli_in_chat = pg.evaluate("Object.values(S.msgs).flat().filter(m=>/Build|clock set/.test(m.text)).length")
    assert cli_in_chat == 0, cli_in_chat
    pg.wait_for_timeout(500)
    pg.screenshot(path=os.path.join(D, 'adm_full.png'), full_page=True)
    # Nachbarn auf der Karte
    pg.click('button[data-a=neighmap]'); pg.wait_for_timeout(1500)
    pg.screenshot(path=os.path.join(D, 'adm_map.png'))
    # Passwort gemerkt + Gast-Login bei anderem Repeater
    pg.click('[data-tab=admin]'); pg.wait_for_timeout(300)
    pg.locator('#admList .citem', has_text='Repeater Saarbrücken').click()
    assert pg.input_value('#admPw') == ''
    pg.fill('#admPw', 'gast'); pg.click('button[data-a=login]')
    pg.wait_for_selector('text=angemeldet als Gast', timeout=8000)
    assert pg.locator('button[data-a=loadset]').count() == 0
    pg.screenshot(path=os.path.join(D, 'adm_guest.png'))
    pg.locator('#admList .citem', has_text='SaarRepeater').click()
    stored = pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('mcw.admpw')).length")
    print('stored pw entries', stored, 'dialogs', len(dialogs))
    print('ERRORS', errs)
    b.close()
print('OK')
