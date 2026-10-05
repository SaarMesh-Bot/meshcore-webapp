import os,json
D=os.path.dirname(os.path.abspath(__file__))
SIM=open(os.path.join(D,'sim.js')).read()
LF=os.path.join(D,'node_modules/leaflet/dist/')
PAGE=os.path.normpath(os.path.join(D,'..',os.environ.get('MCW_PAGE','index.html')))
ROOT=os.path.dirname(PAGE)
REL=json.dumps([{"tag_name":"repeater-v1.17.1"},{"tag_name":"companion-v1.17.1"},{"tag_name":"room-server-v1.17.1"}])
def setup(pg,errs,dialogs=None,accept=True):
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m:m.type=='error' and 'Failed to load resource' not in m.text and errs.append('console: '+m.text))
    if dialogs is not None:
        def dlg(d):
            dialogs.append(d.message); d.accept() if accept else d.dismiss()
        pg.on('dialog',dlg)
    pg.add_init_script(SIM)
    pg.route('**/leaflet.min.js',lambda r:r.fulfill(path=LF+'leaflet.js',content_type='application/javascript'))
    pg.route('**/leaflet.min.css',lambda r:r.fulfill(path=LF+'leaflet.css',content_type='text/css'))
    pg.route('**/qrcode.min.js',lambda r:r.fulfill(path=os.path.join(D,'node_modules/qrcode-generator/qrcode.js'),content_type='application/javascript'))
    pg.route('**/jsQR.min.js',lambda r:r.fulfill(path=os.path.join(D,'node_modules/jsqr/dist/jsQR.js'),content_type='application/javascript'))
    pg.route('**/api.github.com/**',lambda r:r.fulfill(status=200,body=REL,content_type='application/json',headers={'access-control-allow-origin':'*'}))
    pg.route('**/raw.githubusercontent.com/**/catalog.json',lambda r:r.fulfill(path=os.path.join(D,'..','catalog.json'),content_type='application/json',headers={'access-control-allow-origin':'*'}))
    for host in ['server.arcgisonline.com','tile.openstreetmap.org','tile.opentopomap.org']:
        pg.route('**/'+host+'/**',lambda r:r.fulfill(status=200,body=b'',content_type='image/png'))
def connect(pg,url=None):
    pg.goto(url or 'file://'+PAGE)
    pg.click('#btnTcp');pg.fill('#tcpHost','1.2.3.4');pg.click('#tcpOk')
    pg.wait_for_function('typeof S!=="undefined" && S.connected && S.contacts.size>=5',timeout=10000);pg.wait_for_timeout(800)
