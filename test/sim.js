// Simulierte MeshCore-Companion hinter einem Fake-WebSocket (ersetzt die TCP-Bridge)
(()=>{
const enc=new TextEncoder(),dec=new TextDecoder();
const W=()=>{const a=[];const o={u8:v=>{a.push(v&255);return o},i8:v=>o.u8(v),u16:v=>{a.push(v&255,(v>>8)&255);return o},be16:v=>{a.push((v>>8)&255,v&255);return o},
  u32:v=>{v>>>=0;a.push(v&255,(v>>>8)&255,(v>>>16)&255,(v>>>24)&255);return o},i32:v=>o.u32(v|0),
  b:x=>{a.push(...x);return o},s:(t,n)=>{const e=enc.encode(t);if(n==null){a.push(...e)}else{for(let i=0;i<n;i++)a.push(i<e.length?e[i]:0)}return o},out:()=>new Uint8Array(a)};return o};
const key=s=>{let h=2166136261;for(const ch of s){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)>>>0}const k=new Uint8Array(32);for(let i=0;i<32;i++){h^=i*131;h=Math.imul(h,16777619)>>>0;k[i]=h>>>24}return k};
const hex=b=>[...b].map(x=>x.toString(16).padStart(2,'0')).join('');
const SELF=key('selfnode');
const NODES=[
  {name:'SaarRepeater Völklingen',type:2,k:key('rep-voelklingen'),lat:49.25,lon:6.85},
  {name:'Repeater Saarbrücken',type:2,k:key('rep-saarbruecken'),lat:49.23,lon:6.99},
  {name:'Repeater Saarlouis',type:2,k:key('rep-saarlouis'),lat:49.31,lon:6.75},
  {name:'Repeater Merzig',type:2,k:key('rep-merzig'),lat:49.44,lon:6.63},
  {name:'Anna Handy',type:1,k:key('anna-phone'),lat:0,lon:0},
];
const REP=NODES[0];
const st={logged:{},queue:[],now:()=>Math.floor(Date.now()/1000),settings:{name:'SaarRepeater Völklingen',lat:'49.25',lon:'6.85','owner.info':'SaarMesh|mathias','tx':'22',repeat:'on','advert.interval':'120','flood.advert.interval':'12','flood.max':'64','guest.password':'gast',radio:'869.6179809,62.5,8,8'},
  calls:[],telem:0,telemCount:0,aa:0x1e,aah:0,radio:[869618,62500,8,8],name:'Mathias Test',
  regions:[{name:'*',parent:null,flood:true},{name:'saarlorlux',parent:'*',flood:true},{name:'saarland',parent:'saarlorlux',flood:true,home:true},{name:'lux',parent:'saarlorlux',flood:false}]};
function regTree(){const out=[];const pr=(r,ind)=>{out.push(' '.repeat(ind)+r.name+(r.home?'^':'')+(r.flood?' F':''));st.regions.filter(x=>x.parent===r.name).forEach(x=>pr(x,ind+1))};pr(st.regions[0],0);return out.join('\n')}
window.__sim=st;
function contactFrame(n,code=3){const op=new Uint8Array(64);let opl=0xFF;if(n===REP)opl=0;else if(n===NODES[1]){opl=1;op[0]=REP.k[0]}
  const ov=(st.paths||{})[hex(n.k)];if(ov){opl=ov[0];op.set(ov[1])}
  return W().u8(code).b(n.k).u8(n.type).u8(0).u8(opl).b(op).s(n.name,32).u32(st.now()-600)
  .i32(Math.round(n.lat*1e6)).i32(Math.round(n.lon*1e6)).u32(st.now()).out()}
const byPrefix=p=>NODES.find(n=>hex(n.k).startsWith(hex(p)));
class FakeWS{
  constructor(url){this.url=url;this.readyState=0;this.binaryType='arraybuffer';this.buf=new Uint8Array(0);
    setTimeout(()=>{this.readyState=1;this.onmessage&&this.onmessage({data:JSON.stringify({type:'connected',version:'sim'})})},50)}
  close(){this.readyState=3}
  emit(p,delay=5){setTimeout(()=>{if(this.readyState!==1)return;const f=new Uint8Array(p.length+3);f[0]=0x3E;f[1]=p.length&255;f[2]=p.length>>8;f.set(p,3);this.onmessage&&this.onmessage({data:f.buffer})},delay)}
  send(data){const d=new Uint8Array(data);let o=0;while(o+3<=d.length){const len=d[o+1]|(d[o+2]<<8);this.cmd(d.slice(o+3,o+3+len));o+=3+len}}
  sent(tag,est=1500){return W().u8(6).u8(0).u32(tag).u32(est).out()}
  cmd(f){const c=f[0];st.calls.push(c);const ok=W().u8(0).out();
    const tagOf=()=>(Math.random()*0xffffffff)>>>0;
    switch(c){
      case 22:return this.emit(W().u8(13).u8(8).u8(50).u8(8).u32(0).s('01-Jan-2026',12).s('Heltec V3',40).s('v1.13.0',20).u8(1).u8(0).out());
      case 1:return this.emit(W().u8(5).u8(1).i8(22).u8(22).b(SELF).i32(49250000).i32(6870000).u8(0).u8(1).u8(st.telem).u8(0).u32(st.radio[0]).u32(st.radio[1]).u8(st.radio[2]).u8(st.radio[3]).s(st.name).out());
      case 38:st.telem=f[2];return this.emit(ok);
      case 39:{
        const lpp=(i)=>{st.telemCount++;const v=4.10-0.01*st.telemCount;const w=W().u8(1).u8(116).be16(Math.round(v*100)).u8(1).u8(103).be16(235+st.telemCount*3).u8(2).u8(104).u8(110).u8(2).u8(115).be16(10132);
          if(i==='gps'){const g=W().u8(3).u8(136);const e3=x=>{x=Math.round(x);g.u8((x>>16)&255).u8((x>>8)&255).u8(x&255)};e3(49.3*1e4);e3(6.9*1e4);e3(250*100);w.b(g.out())}return w.out()};
        if(f.length===4)return this.emit(W().u8(0x8B).u8(0).b(SELF.slice(0,6)).b(lpp()).out(),30);
        const p=f.slice(4,36),n=NODES.find(n=>hex(n.k)===hex(p));this.emit(this.sent(st.now()));
        if(n.type===2&&!st.logged[hex(p)])return; // Repeater ohne Login: keine Antwort
        this.emit(W().u8(0x8B).u8(0).b(p.slice(0,6)).b(lpp(n.type===1?'gps':'')).out(),600);return}
      case 36:{const tag=f[1]|(f[2]<<8)|(f[3]<<16)|(f[4]<<24),fl=f[9],sz=1<<(fl&3),path=f.slice(10);this.emit(this.sent(tag>>>0,800));
        const hops=[];for(let i=0;i<path.length;i+=sz)hops.push(hex(path.slice(i,i+sz)));
        if(!hops.every(h=>NODES.some(n=>n.type===2&&hex(n.k).startsWith(h))))return; // unbekannter Hop → keine Antwort
        st.lastTrace=hops;const w=W().u8(0x89).u8(0).u8(path.length).u8(fl).u32(tag).u32(0).b(path);hops.forEach((h,i)=>w.i8(Math.round((8-i*3)*4)));w.i8(Math.round(6.5*4));
        this.emit(w.out(),900);return}
      case 55:{this.emit(ok);const tag=f.slice(3,7);st.discCount=(st.discCount||0)+1;
        [[NODES[0],9.5,7.25,-62],[NODES[2],-3.5,-6,-104],[{k:key('fremder-repeater'),type:2},2,1.5,-90]].forEach(([n,so,sb,rs],i)=>
          this.emit(W().u8(0x8E).i8(Math.round(sb*4)).i8(rs).u8(0).u8(0x90|2).i8(Math.round(so*4)).b(tag).b(n.k).out(),400+i*700));return}
      case 9:{(st.paths||(st.paths={}))[hex(f.slice(1,33))]=[f[35],f.slice(36,100)];return this.emit(ok)}
      case 13:{if(st.paths)delete st.paths[hex(f.slice(1,33))];return this.emit(ok)}
      case 6:case 29:case 63:return this.emit(ok);
      case 14:return this.emit(W().u8(0).out());
      case 8:st.name=dec.decode(f.slice(1));return this.emit(ok);
      case 11:{const dv=new DataView(f.buffer,f.byteOffset);st.radio=[dv.getUint32(1,true),dv.getUint32(5,true),f[9],f[10]];return this.emit(ok)}
      case 17:return this.emit(W().u8(11).u8(0x11).b(f.length>=33?f.slice(1,33):SELF).u32(st.now()).b(new Uint8Array(64)).u8(0x81).s(f.length>=33?'X':st.name).out());
      case 18:st.imported=hex(f.slice(1));return this.emit(ok);
      case 59:return this.emit(W().u8(25).u8(st.aa).u8(st.aah).out());
      case 58:st.aa=f[1];if(f.length>2)st.aah=f[2];return this.emit(ok);
      case 57:{const p=f.slice(1,33),d=f.slice(33),n=NODES.find(n=>hex(n.k)===hex(p)),tag=tagOf();st.anon=(st.anon||[]).concat([[hex(p).slice(0,8),...d]]);
        const flood=!n||(n!==REP&&n!==NODES[1]);this.emit(W().u8(6).u8(flood?1:0).u32(tag).u32(1500).out());if(flood)return;
        let rep;if(d[0]===2)rep=W().s(n.name+'\nSaarMesh|anon').out();else if(d[0]===3)rep=W().u8(0).out();else rep=W().s(st.regions.filter(r=>r.flood).map(r=>r.name).join(',')).out();
        this.emit(W().u8(0x8C).u8(0).u32(tag).u32(st.now()+5).b(rep).out(),500);return}
      case 4:{this.emit(W().u8(2).u32(NODES.length).out());NODES.forEach((n,i)=>this.emit(contactFrame(n),10+i*5));return this.emit(W().u8(4).u32(st.now()).out(),60)}
      case 30:{const n=NODES.find(n=>hex(n.k)===hex(f.slice(1,33)));return this.emit(n?contactFrame(n):W().u8(1).u8(2).out())}
      case 31:{const c=(st.chans||(st.chans={0:['Public',new Uint8Array(16)]}))[f[1]];return this.emit(c?W().u8(18).u8(f[1]).s(c[0],32).b(c[1]).out():W().u8(1).u8(2).out())}
      case 32:{(st.chans||(st.chans={0:['Public',new Uint8Array(16)]}))[f[1]]=[dec.decode(f.slice(2,34)).replace(/\0.*$/,''),f.slice(34,50)];return this.emit(W().u8(0).out())}
      case 64:return this.emit(W().u8(28).out());
      case 20:return this.emit(W().u8(12).u16(4100).u32(10).u32(100).out());
      case 56:{const t=f[1];if(t===0)return this.emit(W().u8(24).u8(0).u16(4100).u32(3600).u16(0).u8(0).out());
        if(t===1)return this.emit(W().u8(24).u8(1).u16(-110&0xffff).i8(-80).i8(20).u32(10).u32(20).out());
        return this.emit(W().u8(24).u8(2).u32(100).u32(50).u32(10).u32(10).u32(10).u32(10).u32(0).out())}
      case 10:{const m=st.queue.shift();return this.emit(m||W().u8(10).out())}
      case 26:{ // Login
        const p=f.slice(1,33),pw=dec.decode(f.slice(33));const tag=st.now();this.emit(this.sent(tag));
        const pre=p.slice(0,6);
        if(pw==='geheim'){st.logged[hex(p)]='admin';this.emit(W().u8(0x85).u8(1).b(pre).u32(st.now()+400).u8(3).u8(2).out(),500)}
        else if(pw==='gast'||pw===''){st.logged[hex(p)]='guest';this.emit(W().u8(0x85).u8(0).b(pre).u32(st.now()).u8(0).u8(2).out(),500)}
        else this.emit(W().u8(0x86).u8(0).b(pre).out(),500);return}
      case 27:{const p=f.slice(1,33);this.emit(this.sent(st.now()));
        this.emit(W().u8(0x87).u8(0).b(p.slice(0,6)).u16(4012).u16(0).u16(-112&0xffff).u16(-71&0xffff).u32(15432).u32(8210).u32(5400).u32(3*86400+7200)
          .u32(5000).u32(3210).u32(9000).u32(6432).u16(0).u16(7*4).u16(120).u16(2300).u32(9100).u32(42).out(),600);return}
      case 50:{const p=f.slice(1,33),d=f.slice(33),tag=tagOf();this.emit(this.sent(tag));
        let rep;
        if(d[0]===6){const cnt=d[2],off=d[3]|(d[4]<<8),pl=d[6];const nb=[[NODES[1],7.5,120],[NODES[2],-2.25,600],[NODES[3],-9,3600],[{k:key('unknown-xyz')},1,90]];
          const part=nb.slice(off,off+cnt);const w=W().u16(nb.length).u16(part.length);part.forEach(([n,snr,ago])=>w.b(n.k.slice(0,pl)).u32(ago).i8(Math.round(snr*4)));rep=w.out()}
        else if(d[0]===5){if(st.logged[hex(p)]!=='admin')return;rep=W().b(SELF.slice(0,6)).u8(3).b(NODES[4].k.slice(0,6)).u8(0).out()}
        else if(d[0]===7)rep=W().s('v1.13.0\nSaarRepeater Völklingen\nSaarMesh|mathias').out();
        this.emit(W().u8(0x8C).u8(0).u32(tag).b(rep).out(),700);return}
      case 2:{ // Textnachricht / CLI
        const tt=f[1],pre=f.slice(7,13),text=dec.decode(f.slice(13));this.emit(this.sent(0,1200));
        if(tt!==1)return;
        let r='Unknown command';const s=st.settings;
        if(st.logged[hex(byPrefix(pre).k)]!=='admin')return; // nicht angemeldet → keine Antwort
        let m;
        if(m=text.match(/^get (\S+)$/))r=s[m[1]]!=null?'> '+s[m[1]]:'??: '+m[1];
        else if(m=text.match(/^set (\S+) (.*)$/)){if(m[1] in s){s[m[1]]=m[2];r=m[1]==='repeat'?'OK - repeat is now '+m[2].toUpperCase():'OK'}else r='unknown config: '+m[1]}
        else if(text==='ver')r='v1.13.0 (Build: 01-Jan-2026)';
        else if(text==='clock sync')r='OK - clock set: 12:00 - 4/10/2026 UTC';
        else if(text==='advert')r='OK - Advert sent';else if(text==='advert.zerohop')r='OK - zerohop advert sent';
        else if(text==='clear stats')r='(OK - stats reset)';
        else if(text==='clock')r='20:31 - 4/10/2026 UTC';
        else if(text==='region')r=regTree();
        else if(m=text.match(/^region put (\S+)(?: (\S+))?$/)){if(st.regions.some(x=>x.name===m[1]))r='Err - exists';else{st.regions.push({name:m[1],parent:m[2]||'*',flood:false});r='OK'}}
        else if(m=text.match(/^region (allowf|denyf|home|remove) (\S+)$/)){const g=st.regions.find(x=>x.name===m[2]);if(!g)r='Err - unknown region';else{if(m[1]==='allowf')g.flood=true;else if(m[1]==='denyf')g.flood=false;else if(m[1]==='home'){st.regions.forEach(x=>x.home=false);g.home=true}else st.regions=st.regions.filter(x=>x!==g&&x.parent!==g.name);r='OK'}}
        else if(text==='region save'){st.regSaved=true;r='OK'}
        else if(text==='neighbors')r=[NODES[1],NODES[2]].map((n,i)=>hex(n.k.slice(0,4)).toUpperCase()+':'+(120+i*500)+':'+(i?-47:54)).join('\n');
        const msg=W().u8(16).i8(24).u8(0).u8(0).b(pre).u8(1).u8(1).u32(st.now()).s(r).out();
        setTimeout(()=>{st.queue.push(msg);this.emit(W().u8(0x83).out())},800);return}
      default:return this.emit(W().u8(1).u8(1).out());
    }
  }
}
window.WebSocket=FakeWS;
})();
