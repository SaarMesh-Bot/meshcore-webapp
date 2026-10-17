# Favoriten in Repeater-Liste/Übersicht und Firmware-Update-Karte im Repeater-Admin
import os, json
from playwright.sync_api import sync_playwright
from h import setup, connect, D

V = '1.17.1'
def asset(n): return {"name": n, "size": 1400000, "browser_download_url": "https://github.com/meshcore-dev/MeshCore/releases/download/repeater-v%s/%s" % (V, n)}
ASSETS = {"tag_name": "repeater-v" + V, "assets": [asset(n) for n in [
    'Heltec_v3_repeater-v%s-abc1234-merged.bin' % V, 'Heltec_v3_repeater-v%s-abc1234.bin' % V,
    'heltec_v4_repeater-v%s-abc1234-merged.bin' % V, 'heltec_v4_repeater-v%s-abc1234.bin' % V,
    'RAK_4631_repeater-v%s-abc1234.uf2' % V, 'RAK_4631_repeater-v%s-abc1234.zip' % V,
    'Xiao_rp2040_repeater-v%s-abc1234.bin' % V, 'Xiao_rp2040_repeater-v%s-abc1234.uf2' % V]]}

errs, dialogs = [], []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 900})
    setup(pg, errs, dialogs)
    pg.route('**/api.github.com/**/releases/tags/**', lambda r: r.fulfill(status=200, body=json.dumps(ASSETS), content_type='application/json', headers={'access-control-allow-origin': '*'}))
    connect(pg)
    pg.click('[data-tab=admin]'); pg.wait_for_timeout(300)

    # --- Favoriten ---
    names = lambda: pg.eval_on_selector_all('#admList .citem .nm', 'e=>e.map(x=>x.textContent)')
    pg.locator('#admList .citem', has_text='Repeater Saarlouis').locator('[data-fav]').click()
    pg.wait_for_timeout(100)
    assert names()[1] == 'Repeater Saarlouis', names()
    assert pg.locator('#admList .favsep').count() == 2
    # Übersicht: Favorit oben, Stern klickbar ohne die Zeile zu öffnen
    first = pg.text_content('table.dash tbody tr:first-child td:first-child')
    assert 'Repeater Saarlouis' in first and '★' in first, first
    pg.locator('table.dash tbody tr', has_text='Repeater Merzig').locator('[data-fav]').click()
    pg.wait_for_timeout(100)
    assert pg.locator('table.dash').count() == 1, 'Stern hat die Zeile geöffnet'
    assert pg.evaluate("JSON.parse(localStorage.getItem('mcw.repfav')).length") == 2
    # Nur Favoriten
    pg.click('button[data-a=favonly]'); pg.wait_for_timeout(100)
    assert pg.locator('table.dash tbody tr').count() == 2
    assert 'Favoriten abfragen' in pg.text_content('button[data-a=dashrun]')
    assert len(names()) == 3, names()   # Übersicht + 2 Favoriten
    pg.click('#admFavOnly'); pg.wait_for_timeout(100)
    assert pg.locator('table.dash tbody tr').count() >= 4
    # nach Neuladen erhalten
    pg.reload(); pg.wait_for_timeout(500)
    assert pg.evaluate("FAV.size") == 2

    # --- Firmware-Update ---
    connect(pg)
    pg.click('[data-tab=admin]'); pg.wait_for_timeout(300)
    pg.locator('#admList .citem', has_text='SaarRepeater Völklingen').click()
    pg.fill('#admPw', 'geheim'); pg.click('button[data-a=login]')
    pg.wait_for_selector('text=angemeldet als Admin', timeout=8000)
    pg.wait_for_selector('#fwPick', timeout=8000)
    pg.click('button[data-a=fwcheck]')
    pg.wait_for_function("document.querySelector('#admMain').textContent.includes('Heltec V3')", timeout=15000)
    pg.wait_for_function("document.querySelector('#fwPick').value==='Heltec_v3'", timeout=5000)
    t = pg.text_content('#admMain')
    assert 'Update verfügbar' in t, 'kein Update-Hinweis'
    href = pg.get_attribute('a.btn[download]', 'href')
    assert href.endswith('Heltec_v3_repeater-v%s-abc1234.bin' % V), href
    assert 'MeshCore-OTA' in t and '192.168.4.1/update' in t
    # RAK manuell wählen → Bluetooth-Anleitung
    pg.select_option('#fwPick', 'RAK_4631'); pg.wait_for_timeout(200)
    assert 'nRF Device Firmware Update' in pg.text_content('#admMain')
    assert pg.get_attribute('a.btn[download]', 'href').endswith('.zip')
    # RP2040 → kein Funk-Update
    pg.select_option('#fwPick', 'Xiao_rp2040'); pg.wait_for_timeout(200)
    assert pg.locator('button[data-a=ota]').count() == 0
    assert 'kein Funk-Update' in pg.text_content('#admMain')
    pg.select_option('#fwPick', 'Heltec_v3'); pg.wait_for_timeout(200)
    pg.click('button[data-a=ota]')
    pg.wait_for_selector('.fwok', timeout=10000)
    t = pg.text_content('.fwok')
    assert 'OTA-Modus aktiv' in t and '192.168.4.1/update' in t, t
    assert any('OTA-Update-Modus' in d for d in dialogs), dialogs
    pg.screenshot(path=os.path.join(D, 'fw_ota.png'), full_page=True)
    errs = [e for e in errs if 'ERR_TUNNEL' not in e and 'ERR_' not in e]
    assert not errs, errs
    b.close()
print('OK')
