import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const ROOT='/home/claude/ship/SHIP-2026-09-02k';
const srv=http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8798);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
for(const w of [1400,1000,390]){
  const p=await b.newPage({viewport:{width:w,height:900}}); p.on('pageerror',e=>console.log('PAGEERROR',e.message));
  const reqs=[]; await p.route('**/nofilter-shared.netlify.app/**', r=>{ reqs.push(r.request().url().split('/').pop()); r.fulfill({status:200,body:''}); });
  await p.goto('http://localhost:8798/',{waitUntil:'load'}); await p.waitForTimeout(2500);
  const v=await p.evaluate(()=>{ const v=document.querySelector('.plate-band video'); return {src:(v.getAttribute('src')||'').split('/').pop(), hd:v.getAttribute('data-src-hd'), ds:v.getAttribute('data-src')}; });
  console.log(w, JSON.stringify(v), 'requested:', reqs.filter(x=>x.startsWith('keeps')).join(','));
  console.log(w, 'partners row:', await p.evaluate(()=>[...document.querySelectorAll('#home .ro')].map(r=>r.textContent.trim()).find(t=>t.startsWith('Partners'))));
  await p.close();
}
await b.close(); srv.close();
