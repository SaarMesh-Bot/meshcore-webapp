# Übersetzung: eingehende (🌐 an der Nachricht, automatisch) und ausgehende Nachrichten (🌐 neben „Senden“).
# Chromes Translator-/LanguageDetector-API wird gemockt – im Test-Chromium fehlen die Sprachmodelle.
import sys
from playwright.sync_api import sync_playwright
from h import setup,connect,PAGE
F=[]
def ok(c,m):print('OK  ' if c else 'FAIL',m);c or F.append(m)
MOCK="""(()=>{window.__trCalls=[];window.__trCreate=[];
  window.LanguageDetector={create:async()=>({detect:async t=>[{detectedLanguage:/\\b(je|tu|pas|bonjour)\\b/i.test(t)?'fr':/\\b(the|you|hello)\\b/i.test(t)?'en':'de',confidence:0.9}]})};
  window.Translator={availability:async o=>o.sourceLanguage==='xx'?'unavailable':'available',
    create:async o=>{__trCreate.push(o.sourceLanguage+'>'+o.targetLanguage);return {translate:async t=>{__trCalls.push(t);return '['+o.targetLanguage.toUpperCase()+'] '+t}}}}})()"""
def addIn(pg,text,frm='Seb FR Metz 57'):
    pg.evaluate("([t,f])=>addMsg('ch:0',{dir:'in',from:f,text:t,ts:Date.now(),rx:Date.now(),snr:12,hops:5})",[text,frm])
    pg.wait_for_timeout(400)
def last(pg):return pg.locator('#msgs .msg').last
errs,dl=[],[]
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---- mit API ----
    pg=b.new_page(viewport={'width':1100,'height':800},locale='de-DE');pg.add_init_script(MOCK);setup(pg,errs,dl);connect(pg,'file://'+PAGE)
    if pg.evaluate("typeof trMsg==='undefined'"):print('SKIP: Seite hat noch keine Übersetzung');b.close();sys.exit(0)
    pg.evaluate("S.active='ch:0';switchTab('chat')");pg.wait_for_timeout(200)
    ok(pg.is_visible('#btnTr'),'🌐-Button neben Senden sichtbar')
    addIn(pg,'@[Blackblade-home] Cool je ne savais pas si tu me recevais 🤩')
    ok(last(pg).locator('button[data-tr]').count()==1,'🌐 an französischer Nachricht')
    m=pg.evaluate("S.msgs['ch:0'].slice(-1)[0]");ok(m.get('lang')=='fr','Sprache erkannt: '+str(m.get('lang')))
    addIn(pg,'Guten Abend zusammen, wie geht es euch?','Christian71')
    ok(last(pg).locator('button[data-tr]').count()==0,'kein 🌐 an deutscher Nachricht')
    addIn(pg,'nqbend','Saarmesh.de L2 Pro')
    ok(last(pg).locator('button[data-tr]').count()==0 and pg.evaluate("S.msgs['ch:0'].slice(-1)[0].lang")=='','kurze Nachricht: keine Erkennung')
    fr=pg.locator('#msgs .msg',has_text='Cool je ne savais').last
    fr.locator('button[data-tr]').click();pg.wait_for_timeout(300)
    t=fr.locator('.trx').inner_text()
    ok('[DE] Cool je ne savais pas si tu me recevais' in t and '@[Blackblade-home]' in t,'Übersetzung angezeigt: '+t)
    ok(not any('@[' in c for c in pg.evaluate("__trCalls")),'Erwähnung nicht mitübersetzt: '+str(pg.evaluate("__trCalls")))
    ok('🇫🇷→🇩🇪' in t,'Sprachen angezeigt')
    ok('Cool je ne savais' in fr.locator('.txt').inner_text(),'Original bleibt sichtbar')
    fr.locator('button[data-tr]').click();pg.wait_for_timeout(200)
    ok(fr.locator('.trx').count()==0,'erneuter Klick blendet aus')
    pg.evaluate("renderAll()");pg.wait_for_timeout(200)
    ok(pg.evaluate("S.msgs['ch:0'].find(m=>m.text.includes('Cool je')).tr.text").startswith('@[Blackblade-home] [DE]'),'Übersetzung bleibt gespeichert')
    # automatisch
    pg.evaluate("switchTab('device')");pg.check('#trAuto');pg.evaluate("switchTab('chat')")
    addIn(pg,'Bonjour à tous, je suis à Metz ce soir');pg.wait_for_timeout(300)
    ok('[DE] Bonjour' in last(pg).inner_text(),'automatisch übersetzt: '+last(pg).inner_text().replace('\n',' | '))
    # Zielsprache umstellen: Englisch-Leser sieht 🌐 an deutscher Nachricht
    pg.evaluate("switchTab('device')");pg.uncheck('#trAuto');pg.select_option('#trTo','en');pg.evaluate("switchTab('chat')");pg.wait_for_timeout(300)
    ok(pg.locator('#msgs .msg',has_text='Guten Abend zusammen').locator('button[data-tr]').count()==1,'Zielsprache Englisch: 🌐 an deutscher Nachricht')
    pg.evaluate("TR.set('to','de')")
    # ---- ausgehend ----
    pg.fill('#msgIn','@[Seb FR Metz 57] Hallo, ich empfange dich gut hier in Saarbrücken')
    pg.click('#btnTr');ok(pg.is_visible('#trBox') and 'Französisch' in pg.inner_text('#trBox'),'Sprachmenü offen')
    pg.locator('#trBox .mi[data-trto="fr"]').dispatch_event('mousedown');pg.wait_for_timeout(400)
    v=pg.input_value('#msgIn')
    ok(v=='@[Seb FR Metz 57] [FR] Hallo, ich empfange dich gut hier in Saarbrücken','Eingabe übersetzt: '+v)
    ok(pg.is_hidden('#trBox'),'Menü geschlossen')
    ok(pg.inner_text('#msgLen').startswith(str(len(v.encode()))),'Zeichenzähler aktualisiert: '+pg.inner_text('#msgLen'))
    pg.click('#btnTr');ok(pg.locator('#trBox [data-trundo]').count()==1,'Original wiederherstellen angeboten')
    pg.locator('#trBox [data-trundo]').dispatch_event('mousedown');pg.wait_for_timeout(200)
    ok(pg.input_value('#msgIn').startswith('@[Seb FR Metz 57] Hallo, ich'),'Original wiederhergestellt')
    pg.click('#btnTr');pg.locator('#trBox .mi[data-trto="de"]').dispatch_event('mousedown');pg.wait_for_timeout(300)
    ok(pg.input_value('#msgIn').startswith('@[Seb FR Metz 57] Hallo'),'gleiche Sprache: nichts geändert')
    pg.click('#btnTr');pg.locator('#trBox .mi[data-trto="fr"]').dispatch_event('mousedown');pg.wait_for_timeout(300)
    pg.press('#msgIn','Enter');pg.wait_for_timeout(500)
    ok(pg.evaluate("S.msgs['ch:0'].slice(-1)[0].text").startswith('@[Seb FR Metz 57] [FR]'),'übersetzte Nachricht gesendet')
    ok(pg.evaluate("TR.cfg().tx")=='fr','zuletzt gewählte Sprache gemerkt')
    pg.screenshot(path='tr.png')
    # ---- ohne API (ältere Chrome-Versionen, Android) ----
    pg2=b.new_page(viewport={'width':1100,'height':800},locale='de-DE');pg2.add_init_script('delete window.Translator;delete window.LanguageDetector');setup(pg2,errs,dl);connect(pg2,'file://'+PAGE)
    pg2.evaluate("S.active='ch:0';switchTab('chat')")
    addIn(pg2,'Cool je ne savais pas si tu me recevais')
    ok(pg2.is_hidden('#btnTr'),'ohne API: kein 🌐 neben Senden')
    ok(pg2.locator('#msgs button[data-tr]').count()==0,'ohne API: kein 🌐 an Nachrichten')
    ok('nicht verfügbar' in pg2.inner_text('#trInfo'),'ohne API: Hinweis in den Einstellungen')
    print('ERR',errs);b.close()
sys.exit(1 if F or errs else 0)
