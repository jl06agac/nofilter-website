import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const ROOT='/home/claude/ship/SHIP-2026-09-02j';
const srv=http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8795);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
for(const w of [1400, 390]){
  const p=await b.newPage({viewport:{width:w,height:900}}); p.on('pageerror',e=>console.log('PAGEERROR',e.message));
  await p.route('**/nofilter-shared.netlify.app/**', r=>r.fulfill({status:200,body:''}));
  await p.goto('http://localhost:8795/wholesale-coffee/',{waitUntil:'load'}); await p.waitForTimeout(1000);
  const el=await p.$('#nfBoard'); await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(600);
  const frame=await p.$('#nfBoard'); const box=await (await p.$('.nw-livewrap')).boundingBox();
  await p.waitForTimeout(3000); await p.screenshot({path:`board-${w}-a.png`, clip:{x:Math.max(0,box.x-20),y:Math.max(0,box.y-20),width:Math.min(w,box.width+40),height:box.height+40}});
  await p.waitForTimeout(9000); await p.screenshot({path:`board-${w}-b.png`, clip:{x:Math.max(0,box.x-20),y:Math.max(0,box.y-20),width:Math.min(w,box.width+40),height:box.height+40}});
  console.log(w, 'board text now:', await p.evaluate(()=>{ const cs=[...document.querySelectorAll('#nfBoard .nfb-c .t span')].map(s=>s.textContent||' '); let out=[]; for(let r=0;r<5;r++) out.push(cs.slice(r*22,r*22+22).join('').trim()); return out.filter(Boolean).join(' / '); }));
  // scroll test with flips running
  const st=await p.evaluate(async()=>{ const run=(dist,dur)=>new Promise(res=>{const d=[];let last=performance.now(),t0=last,y0=scrollY;(function step(){const n=performance.now();d.push(n-last);last=n;const t=(n-t0)/dur;if(t<1){scrollTo(0,y0+dist*(t<.5?t*2:2-t*2));requestAnimationFrame(step)}else res(d)})()}); const d=await run(1500,4000); const s=[...d].sort((a,b)=>a-b); return {frames:d.length, p99:+s[Math.floor(.99*(s.length-1))].toFixed(1), over32:d.filter(x=>x>32).length}; });
  console.log(w, 'scroll while board live:', JSON.stringify(st));
  await p.close();
}
await b.close(); srv.close();
