import os,json,sys
from playwright.sync_api import sync_playwright
from h import D,setup,connect
errs,dl=[],[]
def ok(c,msg):
    print(('OK  ' if c else 'FAIL'),msg)
    if not c: FAILS.append(msg)
FAILS=[]
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':1280,'height':820},accept_downloads=True);pg=ctx.new_page()
    setup(pg,errs,dl);connect(pg)
    REP=pg.evaluate("[...S.contacts.values()].find(c=>c.name.startsWith('SaarRepeater')).key")
    MER=pg.evaluate("[...S.contacts.values()].find(c=>c.name.includes('Merzig')).key")
    # ---- QR ----
    pg.evaluate("qrChannel('ch:0')");pg.wait_for_selector('#qrBox svg',timeout=5000)
    ok('meshcore://channel/add?name=Public&secret=8b3387e9c5cdea6ac9e5edbaa115cd72' in pg.inner_text('#qrUrl') or 'secret=000000' in pg.inner_text('#qrUrl'),'Kanal-QR-URL: '+pg.inner_text('#qrUrl'))
    pg.screenshot(path='f_qr.png');pg.click('#qrClose')
    pg.evaluate("qrSelf()");pg.wait_for_selector('#qrBox svg');u=pg.inner_text('#qrUrl');ok(u.startswith('meshcore://contact/add?name=Mathias%20Test&public_key=') and u.endswith('&type=1'),'Eigener QR: '+u);pg.click('#qrClose')
    # decode own QR with jsQR from SVG -> canvas
    dec=pg.evaluate("""async()=>{await loadLib(LIBS.qr);const q=qrcode(0,'M');q.addData('meshcore://channel/add?name=%23qrtest&secret=0123456789abcdef0123456789abcdef&region_scope=saarland');q.make();
      const c=document.createElement('canvas');const n=q.getModuleCount(),sz=8,m=4;c.width=c.height=(n+2*m)*sz;const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,c.width,c.height);g.fillStyle='#000';
      for(let r=0;r<n;r++)for(let k=0;k<n;k++)if(q.isDark(r,k))g.fillRect((k+m)*sz,(r+m)*sz,sz,sz);SCAN.noBD=true;return await detectQr(c)}""")
    ok(dec and dec.endswith('region_scope=saarland'),'QR dekodiert (jsQR): '+str(dec))
    # ---- Links importieren ----
    pg.evaluate("handleMeshLink('meshcore://channel/add?name=%23qrtest&secret=0123456789abcdef0123456789abcdef&region_scope=saarland')");pg.wait_for_timeout(1500)
    r=pg.evaluate("(()=>{const c=S.channels.find(c=>c.secret==='0123456789abcdef0123456789abcdef');return c?[c.name,chanRegion(c),S.active,curTab]:null})()")
    ok(r and r[0]=='#qrtest' and r[1]=='saarland' and r[3]=='chat','Kanal per Link hinzugefügt: '+str(r))
    newkey='ab'*32
    pg.evaluate(f"handleMeshLink('meshcore://contact/add?name=Neuer+Repeater&public_key={newkey}&type=2')");pg.wait_for_timeout(1200)
    r=pg.evaluate(f"(()=>{{const c=S.contacts.get('{newkey}');return c?[c.name,c.type,c.saved,c.outPathLen]:null}})()")
    ok(r and r[0]=='Neuer Repeater' and r[1]==2 and r[2] and r[3]==255,'Kontakt per Link: '+str(r))
    ok(not pg.is_hidden('#nodeModal'),'Knotendetails nach Import offen');pg.click('#nodeClose')
    try:
        pg.evaluate("handleMeshLink('https://example.org')");ok(False,'kein Fehler bei falschem Link')
    except Exception as e: ok('Kein MeshCore' in str(e),'falscher Link abgelehnt')
    pg.evaluate("handleMeshLink('meshcore://'+'11'.repeat(110))");pg.wait_for_timeout(500);ok(pg.evaluate("__sim.imported&&__sim.imported.length===220"),'Advert-Visitenkarte importiert')
    # scanner UI paste
    pg.evaluate("openScanner()");pg.wait_for_timeout(500);pg.screenshot(path='f_scan.png')
    pg.fill('#scanPaste','meshcore://channel/add?name=%23qrtest&secret=0123456789abcdef0123456789abcdef');pg.click('#scanOk');pg.wait_for_timeout(500)
    ok(pg.is_hidden('#scanModal'),'Scanner nach Einfügen geschlossen')
    # ---- Benachrichtigungen / Erwähnung ----
    r=pg.evaluate("""(()=>{NOTIF.mode='mention';const m1={dir:'in',from:'Anna',text:'Hallo @[Mathias Test] wie gehts?'},m2={dir:'in',from:'Anna',text:'Hallo zusammen'};m1.mention=isMention(m1);m2.mention=isMention(m2);
      const a=[shouldNotify('ch:0',m1),shouldNotify('ch:0',m2),shouldNotify('c:abc',m2)];NOTIF.conv['ch:0']='mute';a.push(shouldNotify('ch:0',m1));delete NOTIF.conv['ch:0'];
      a.push(isMention({dir:'in',text:'@mathias test ok'}),isMention({dir:'in',text:'@Mathias Tester'}));return a})()""")
    ok(r==[True,False,True,False,True,False],'Benachrichtigungslogik '+str(r))
    pg.evaluate("NOTIF.mode='off'")
    # ---- Suche ----
    pg.evaluate("""S.msgs['ch:0']=(S.msgs['ch:0']||[]).concat([{id:'m1',dir:'in',from:'Bot',text:'Treffen am Schaumberg heute Abend',ts:Date.now()-60000,rx:Date.now()-60000},{id:'m2',dir:'in',from:'Anna',text:'@[Mathias Test] kommst du?',ts:Date.now(),rx:Date.now(),mention:true}].concat(Array.from({length:60},(_,i)=>({id:'f'+i,dir:'in',from:'X',text:'Füller '+i,ts:Date.now()+i,rx:Date.now()+i}))));S.active=null;switchTab('chat')""")
    pg.fill('#chatSearch','schaumberg');pg.wait_for_timeout(300)
    ok(pg.locator('.sres').count()==1 and 'Schaumberg' in pg.inner_text('.sres mark'),'Suchtreffer')
    pg.screenshot(path='f_search.png');pg.click('.sres');pg.wait_for_timeout(400)
    ok(pg.evaluate("S.active")=='ch:0' and pg.locator('.msg.flash').count()==1,'Sprung zum Treffer')
    ok(pg.locator('.msg.mention').count()>=1,'Erwähnung hervorgehoben')
    pg.select_option('#convNotify','mute');pg.wait_for_timeout(200);ok(pg.evaluate("NOTIF.conv['ch:0']")=='mute','Kanal stumm');pg.fill('#chatSearch','')
    pg.evaluate("S.unread['ch:0']=3;S.active=null;renderChat()");ok(pg.inner_text('#unreadBadge')=='' or pg.is_hidden('#unreadBadge'),'stummer Kanal zählt nicht im Badge')
    pg.select_option('#chatlist ~ x',[]) if False else None
    pg.evaluate("setConvMode('ch:0','std')")
    # ---- Knotendetails ----
    pg.evaluate(f"""(()=>{{const n=S.nodes.get('{REP}');n.first=Date.now()-86400000;n.heard=Date.now()-60000;for(let i=0;i<12;i++)nhAdd('{REP}',[Date.now()-3600000*(12-i),6+Math.sin(i)*3,-80-i,i%3?1:0,i%3?'{MER[:2]}':null]);openNode('{REP}')}})()""")
    pg.wait_for_timeout(200);t=pg.inner_text('#nodeBody')
    ok('Ø SNR' in t and 'Letzte Adverts' in t and pg.locator('#nodeBody svg.tspark').count()==1,'Knotendetails mit Verlauf')
    ok(pg.locator('#nodeBody a[href*="live.saarmesh.de/#/nodes/'+REP+'"]').count()==1,'CoreScope-Link')
    pg.screenshot(path='f_node.png');pg.click('#nodeClose')
    # ---- Kontakte: neue Knoten + Export ----
    pg.evaluate("""(()=>{const k='cd'.repeat(32);const nb=new Uint8Array(32);nb.set(enc.encode('Neuling'));const f=bytes(0x8A,unhex(k),1,0,0xFF,new Uint8Array(64),nb,u32(now()),i32(49300000),i32(7000000),u32(now()));handlePush(f)})()""")
    pg.click('[data-tab=contacts]');pg.wait_for_timeout(300)
    ok(not pg.is_hidden('#cNewBar') and '1' in pg.inner_text('#cNewBar'),'Banner neue Knoten: '+pg.inner_text('#cNewBar'))
    pg.screenshot(path='f_contacts.png')
    with pg.expect_download() as d: pg.click('#btnCExpGpx')
    gpx=open(d.value.path()).read();ok('<wpt lat="49.25"' in gpx and 'SaarRepeater' in gpx,'GPX-Export')
    with pg.expect_download() as d: pg.click('#btnCExpCsv')
    csv=open(d.value.path(),encoding='utf-8-sig').read();ok(csv.startswith('name;typ;') and 'Neuling' in csv,'CSV-Export')
    n9=pg.evaluate("__sim.calls.filter(c=>c===9).length");pg.click('#cNewBar button[data-cn=all]');pg.wait_for_timeout(600)
    ok(pg.evaluate("__sim.calls.filter(c=>c===9).length")==n9+1 and pg.is_hidden('#cNewBar'),'Neue Knoten gespeichert')
    pg.click('#ctable a.nlink >> nth=0');pg.wait_for_timeout(200);ok(not pg.is_hidden('#nodeModal'),'Name öffnet Details');pg.click('#nodeClose')
    # ---- Sicherung ----
    pg.click('[data-tab=device]');pg.wait_for_timeout(300)
    with pg.expect_download() as d: pg.click('#btnBackup')
    bk=json.load(open(d.value.path()));ok(bk['app']=='meshcore-webapp' and len(bk['contacts'])>=5 and any(c['name']=='#qrtest' for c in bk['channels']),'Sicherung exportiert (%d Kontakte, %d Kanäle)'%(len(bk['contacts']),len(bk['channels'])))
    bk['contacts'].append({'key':'ef'*32,'name':'Aus Sicherung','type':1,'raw':pg.evaluate("(()=>{const nb=new Uint8Array(32);nb.set(enc.encode('Aus Sicherung'));return hex(bytes(3,unhex('ef'.repeat(32)),1,0,0xFF,new Uint8Array(64),nb,u32(0),i32(0),i32(0)))})()")})
    bk['channels'].append({'name':'#backupkanal','secret':'fe'*16,'region':'lux'})
    open('bk.json','w').write(json.dumps(bk))
    n9=pg.evaluate("__sim.calls.filter(c=>c===9).length")
    pg.set_input_files('#restoreFile','bk.json');pg.wait_for_timeout(2500)
    r=pg.evaluate("[__sim.calls.filter(c=>c===9).length,S.channels.map(c=>c.name),(()=>{const c=S.channels.find(c=>c.name==='#backupkanal');return c&&chanRegion(c)})()]")
    ok(r[0]==n9+1 and '#backupkanal' in r[1] and r[2]=='lux','Sicherung eingespielt '+str(r))
    # ---- Auto-Add ----
    ok(pg.locator('#aaBox input[data-aa]').count()==5,'Auto-Add-Optionen')
    pg.uncheck('#aaBox input[data-aa="4"]');pg.wait_for_timeout(300);ok(pg.evaluate("__sim.aa")==0x1a,'Auto-Add gesetzt: %s'%pg.evaluate("__sim.aa"))
    ok('⬆ v1.17.1' in pg.inner_text('#kvInfo'),'Firmware-Hinweis Companion')
    pg.screenshot(path='f_device.png',full_page=True)
    # ---- Assistent ----
    pg.click('#btnWizard');pg.wait_for_timeout(200);pg.screenshot(path='f_wiz0.png')
    pg.click('#wizNext');pg.fill('#wzName','Mathias SB');pg.click('#wizNext');pg.wait_for_timeout(800)
    ok(pg.evaluate("S.self.name")=='Mathias SB','Name per Assistent')
    pg.fill('#wzLat','49.31');pg.fill('#wzLon','6.99');pg.click('#wizNext');pg.wait_for_timeout(800);pg.screenshot(path='f_wiz3.png')
    ok('Passt zum Profil' in pg.inner_text('#wizBody'),'Funkprofil erkannt')
    pg.evaluate("__sim.radio=[868000,250000,11,5]");pg.evaluate("reloadSelf().then(renderWizard)");pg.wait_for_timeout(500)
    pg.click('#wzRadio');pg.wait_for_timeout(800);ok(pg.evaluate("__sim.radio")==[869618,62500,8,8],'Funkprofil gesetzt')
    pg.click('#wizNext');pg.wait_for_timeout(300);pg.screenshot(path='f_wiz4.png')
    cnt=pg.locator('#wizBody input[data-wch]').count();ok(cnt>0,'Kanalvorschläge %d'%cnt)
    pg.fill('#wzCh','#wizkanal');pg.click('#wizNext');pg.wait_for_timeout(1500)
    ok('#wizkanal' in pg.evaluate("S.channels.map(c=>c.name)"),'Kanal per Assistent')
    pg.click('#wizNext');pg.wait_for_timeout(300);ok('Fertig' in pg.inner_text('#wizBody'),'Letzter Schritt');pg.click('#wizNext');ok(pg.is_hidden('#wizModal'),'Assistent geschlossen')
    # ---- Repeater-Übersicht ----
    pg.evaluate(f"store.set('mcw.admpw.{REP[:12]}','geheim')")
    pg.click('[data-tab=admin]');pg.wait_for_timeout(300)
    ok('Repeater-Übersicht' in pg.inner_text('#admMain'),'Übersicht als Startseite')
    pg.click('button[data-a=dashrun]');pg.wait_for_function("!DASH.busy",timeout=30000);pg.wait_for_timeout(300)
    r=pg.evaluate(f"RD['{REP}']");ok(r and r.get('batt')==4012 and r.get('ver')=='v1.13.0','Übersicht abgefragt '+str({k:r.get(k) for k in ['batt','ver','up']} if r else r))
    ok('⬆ v1.17.1' in pg.inner_text('table.dash'),'Firmware-Hinweis Repeater')
    pg.screenshot(path='f_dash.png')
    # ---- Anonym ----
    pg.evaluate(f"openAdmin('{MER}')");pg.wait_for_timeout(200);pg.click('button[data-a=anon]');pg.wait_for_timeout(5000)
    ok(pg.evaluate(f"!admS('{MER}').anon"),'Merzig (Flood) antwortet nicht anonym')
    pg.evaluate(f"admLogout&&0;ADM.key='{pg.evaluate('[...S.contacts.values()].find(c=>c.name===\"Repeater Saarbrücken\").key')}';renderAdmin()");pg.wait_for_timeout(200)
    pg.click('button[data-a=anon]');pg.wait_for_function("admCur().anon&&admCur().anon.regions",timeout=15000);pg.wait_for_timeout(300)
    t=pg.inner_text('#admMain');ok('SaarMesh' in t and '#saarland' in t and 'an' in t,'Anonyme Infos angezeigt')
    an=pg.evaluate("__sim.anon.slice(-3)");ok(an[0][1:4]==[2,1,pg.evaluate("[...S.contacts.values()].find(c=>c.name===\"Repeater Saarbrücken\").outPath[0]")] ,'Anon-Anfrage mit Rückpfad '+str(an))
    pg.screenshot(path='f_anon.png')
    # ---- Regionen ----
    pg.evaluate(f"ADM.key='{REP}';renderAdmin()");pg.wait_for_timeout(200)
    pg.click('button[data-a=regload]');pg.wait_for_function("admCur().regions",timeout=10000);pg.wait_for_timeout(200)
    ok(pg.locator('.regt tbody tr').count()==4,'4 Regionen geladen')
    pg.fill('#regNew','#Testreg');pg.select_option('#regParent','saarland');pg.click('button[data-a=regadd]');pg.wait_for_function("admCur().regions&&admCur().regions.list.length===5",timeout=10000)
    r=pg.evaluate("admCur().regions.list.find(r=>r.name==='testreg')");ok(r and r['parent']=='saarland' and r['ind']==3 and not r['flood'],'Region angelegt '+str(r))
    pg.click('button[data-reg=allowf][data-n=testreg]');pg.wait_for_function("admCur().regions.list.find(r=>r.name==='testreg').flood",timeout=10000)
    ok(True,'Flood erlaubt');pg.screenshot(path='f_regions.png',full_page=True)
    pg.click('button[data-a=regsave]');pg.wait_for_timeout(1500);ok(pg.evaluate("__sim.regSaved===true&&!admCur().regDirty"),'region save')
    # ---- Karte: eigener Empfang ----
    pg.click('[data-tab=map]');pg.wait_for_timeout(500);pg.check('#mRx');pg.wait_for_timeout(500)
    ok(pg.evaluate("rxLayer.getLayers().length")>=2,'Empfangsebene: %d'%pg.evaluate("rxLayer.getLayers().length"))
    pg.screenshot(path='f_map.png')
    print('ERR',errs);print('FAILS',FAILS);b.close()
    sys.exit(1 if FAILS or errs else 0)
