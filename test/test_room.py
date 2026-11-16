# Room-Server: Anmeldung im Chat, Senden nur nach Login, Nur-Lesen, Wiederanmeldung ohne Passwort
import os,sys
from playwright.sync_api import sync_playwright
from h import setup,connect
errs,dialogs=[],[]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900})
    pg.add_init_script('window.__SIM_ROOM=true')
    setup(pg,errs,dialogs);connect(pg)
    room="[...S.contacts.values()].find(c=>c.type===3)"
    pg.wait_for_function(room,timeout=5000)
    pg.click('[data-tab=chat]');pg.click('.citem:has-text("RGB-Spelunke")')
    pg.wait_for_selector('#roombar.need',timeout=3000)
    assert 'nur nach Anmeldung' in pg.text_content('#roombar')
    # Senden ohne Anmeldung wird blockiert, Text bleibt stehen
    pg.fill('#msgIn','Hallo');pg.click('#btnSend');pg.wait_for_timeout(300)
    assert pg.input_value('#msgIn')=='Hallo'
    assert not pg.evaluate('__sim.roomPosts'),'ohne Login gesendet'
    # falsches Passwort: Room antwortet nicht → Zeitüberschreitung mit Hinweis
    pg.fill('#roomPw','falsch');pg.click('#btnRoomJoin')
    pg.wait_for_function("document.querySelector('#roombar').textContent.includes('Passwort falsch')",timeout=20000)
    # richtiges Passwort, gemerkt
    pg.fill('#roomPw','hello');pg.click('#btnRoomJoin')
    pg.wait_for_function("document.querySelector('#roombar').textContent.includes('Angemeldet · Lesen/Schreiben')",timeout=10000)
    assert pg.evaluate("localStorage.getItem('mcw.admpw.'+%s.key.slice(0,12))"%room)=='"hello"'
    # nachgelieferter Beitrag: Autor ohne „@ Room“
    pg.wait_for_function("document.querySelector('#msgs').textContent.includes('Willkommen in der Spelunke')",timeout=8000)
    frm=pg.locator('#msgs .msg.in .from').first.text_content()
    assert frm=='Anna Handy',frm
    assert '🔓' in pg.text_content('#chatlist')
    # jetzt senden → ACK
    pg.click('#btnSend')
    pg.wait_for_function("document.querySelector('#msgs').textContent.includes('zugestellt')",timeout=8000)
    assert pg.evaluate('__sim.roomPosts')==['Hallo']
    # neu verbinden: automatische Wiederanmeldung mit gemerktem Passwort
    pg.click('#btnDisc') if pg.locator('#btnDisc').is_enabled() else None
    pg.wait_for_function('!S.connected',timeout=5000)
    n=pg.evaluate('__sim.roomLogins')
    pg.click('#btnTcp');pg.fill('#tcpHost','1.2.3.4');pg.click('#tcpOk')
    pg.wait_for_function('S.connected',timeout=10000)
    pg.click('[data-tab=chat]');pg.click('.citem:has-text("RGB-Spelunke")')
    pg.wait_for_function("document.querySelector('#roombar').textContent.includes('Angemeldet')",timeout=10000)
    assert pg.evaluate('__sim.roomLogins')==n+1,('Auto-Login',n,pg.evaluate('__sim.roomLogins'))
    assert pg.evaluate('__sim.roomPws')[-1]=='hello'
    # Nur-Lesen (allow.read.only): Senden blockiert
    pg.evaluate("__sim.roomRO=true;__sim.roomPerm=null")
    pg.fill('#roomPw','irgendwas') if pg.locator('#roomPw').count() else None
    pg.evaluate("roomLogin(%s.key,'irgendwas',false)"%room)
    pg.wait_for_selector('#roombar.ro',timeout=10000)
    pg.fill('#msgIn','Darf ich?');pg.click('#btnSend');pg.wait_for_timeout(300)
    assert pg.input_value('#msgIn')=='Darf ich?' and pg.evaluate('__sim.roomPosts')==['Hallo']
    # vergessen
    pg.click('#btnRoomForget');pg.wait_for_selector('#roombar.need',timeout=3000)
    assert pg.evaluate("localStorage.getItem('mcw.room.'+%s.key.slice(0,12))"%room) is None
    # Repeater-Admin ohne Room unverändert
    errs=[e for e in errs if 'ERR_TUNNEL' not in e and 'ERR_' not in e]
    print('dialogs',dialogs)
    if errs:print('ERRORS',errs);sys.exit(1)
    print('OK')
    b.close()
