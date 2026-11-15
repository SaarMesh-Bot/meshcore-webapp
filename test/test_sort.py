"""Kontakte: Sortierung per Spaltenkopf und Auswahlfeld, wird im Browser gemerkt."""
import os
from playwright.sync_api import sync_playwright
from h import setup, connect, D

errs = []
def names(pg):
    return pg.eval_on_selector_all('#ctable tr td:first-child a', 'a=>a.map(x=>x.textContent)')
def col(pg, js):
    return pg.evaluate(f"contactList().map({js})")

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900})
    setup(pg, errs); connect(pg)
    pg.evaluate("store.del('mcw.cSort')"); pg.reload(); connect(pg)
    pg.click('[data-tab=contacts]'); pg.wait_for_timeout(300)
    # Standard: zuletzt gehört, neueste zuerst
    seen = col(pg, 'n=>lastSeen(n)')
    assert seen == sorted(seen, reverse=True), seen
    assert pg.text_content('#cthead th[data-sort=seen]').endswith('↓')
    # Name aufsteigend per Spaltenkopf, nochmal klicken = absteigend
    pg.click('#cthead th[data-sort=name]'); pg.wait_for_timeout(100)
    n = names(pg); key = lambda s: s.lower()
    assert n == sorted(n, key=key), n
    assert pg.input_value('#cSort') == 'name'
    pg.click('#cthead th[data-sort=name]'); pg.wait_for_timeout(100)
    n2 = names(pg); assert n2 == sorted(n2, key=key, reverse=True), n2
    # SNR über Auswahlfeld: beste zuerst, leere Werte ans Ende
    pg.select_option('#cSort', 'snr'); pg.wait_for_timeout(100)
    snr = col(pg, 'n=>n.snr??null'); v = [x for x in snr if x is not None]
    assert v == sorted(v, reverse=True) and snr[:len(v)] == v, snr
    pg.click('#cSortDir'); pg.wait_for_timeout(100)
    snr = col(pg, 'n=>n.snr??null'); v = [x for x in snr if x is not None]
    assert v == sorted(v) and snr[:len(v)] == v, snr
    # Entfernung, nächste zuerst
    pg.select_option('#cSort', 'dist'); pg.wait_for_timeout(100)
    d = col(pg, 'n=>CSORT_VAL.dist(n)'); v = [x for x in d if x is not None]
    assert v == sorted(v) and d[:len(v)] == v, d
    # Pfad + Typ laufen fehlerfrei
    for k in ('path', 'type'):
        pg.select_option('#cSort', k); pg.wait_for_timeout(100)
    pg.screenshot(path=os.path.join(D, 'sort.png'))
    # Einstellung bleibt nach Neuladen erhalten
    pg.select_option('#cSort', 'name'); pg.reload(); connect(pg)
    pg.click('[data-tab=contacts]'); pg.wait_for_timeout(300)
    assert pg.input_value('#cSort') == 'name'
    n = names(pg); assert n == sorted(n, key=key), n
    b.close()
assert not errs, errs
print('OK sort')
