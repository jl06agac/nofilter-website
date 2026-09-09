import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const ROOT='/home/claude/ship/SHIP-2026-09-02j';
const srv=http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} const ext=f.split('.').pop(); res.writeHead(200,{'Content-Type':{html:'text/html',js:'text/javascript',css:'text/css',woff2:'font/woff2'}[ext]||'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8765);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
async function run(url, live){
  const p=await b.newPage({viewport:{width:1500,height:950}});
  const calls=[]; p.on('pageerror',e=>console.log('PAGEERROR',e.message));
  await p.route('**/.netlify/functions/**', async route=>{ const r=route.request(); const body=JSON.parse(r.postData()||'{}'); calls.push([r.url().split('/').pop(), body]);
    if(r.url().endsWith('access-request')) return route.fulfill({status: body.email.endsWith('gmail.com')?403:200, body:'sent'});
    if(r.url().endsWith('access-verify')) return route.fulfill({status: body.code==='TAPIRBASIN743'?200:401, contentType:'application/json', body: JSON.stringify({ok: body.code==='TAPIRBASIN743'})}); });
  await p.goto(url,{waitUntil:'load'}); await p.waitForTimeout(1200);
  await p.evaluate(()=>{ document.querySelectorAll('.route').forEach(s=>s.classList.toggle('on', s.id==='quote')); location.hash='#quote'; });
  await p.waitForTimeout(600);
  console.log('LIVE flag:', await p.evaluate(()=>window.__nfAccessLive));
  await p.fill('#accName','Alex Clark'); await p.fill('#accEmail','alex@nofilter.sg'); await p.fill('#accCo','NoFilter Pte. Ltd.');
  await p.evaluate(()=>document.querySelector('#accForm').requestSubmit()); await p.waitForTimeout(800);
  const panel=await p.evaluate(()=>({hidden:document.querySelector('#accIssued').hidden, hd:document.querySelector('#accPanelHd').textContent, code:document.querySelector('#accCode').textContent, demoNote:!document.querySelector('#accNoteDemo').hidden, liveNote:!document.querySelector('#accNoteLive').hidden, dest:document.querySelector('#accDest').textContent, go:document.querySelector('#accForm .acc-go').textContent.trim(), err:document.querySelector('#accErr').hidden}));
  console.log('panel', JSON.stringify(panel)); console.log('calls', JSON.stringify(calls));
  await p.screenshot({path:`access-${live?'live':'demo'}.png`, clip:{x:0,y:0,width:1500,height:950}});
  // gate
  await p.evaluate(()=>document.querySelector('#accEnter').click()); await p.waitForTimeout(3500);
  const code = live ? 'WRONGCODE1' : panel.code;
  await p.keyboard.type(code, {delay:30}); await p.keyboard.press('Enter'); await p.waitForTimeout(1200); if(!live) await p.waitForTimeout(6000);
  let txt=await p.evaluate(()=>document.querySelector('#crtText').innerText.replace(/\s+/g,' '));
  console.log('after first attempt:', txt.slice(0,160));
  if(live){ await p.waitForTimeout(1200); await p.keyboard.type('tapir basin 743',{delay:30}); await p.keyboard.press('Enter'); await p.waitForTimeout(1500); console.log('after correct code:', await p.evaluate(()=>document.querySelector('#crtText').innerText.replace(/\s+/g,' ').slice(0,120))); await p.waitForTimeout(6000); }
  console.log('unlocked:', await p.evaluate(()=>document.documentElement.classList.contains('nf-unlocked')), '| calls:', JSON.stringify(calls.slice(1)));
  await p.close();
}
console.log('=== DEMO (file://)'); await run('file:///home/claude/nfw/Marketing/NoFilter-Website/NoFilter-Website-Master.html', false);
console.log('=== LIVE (http://)'); await run('http://localhost:8765/', true);
await b.close(); srv.close();
