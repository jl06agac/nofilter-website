import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const ROOT='/home/claude/ship/SHIP-2026-09-02h';
const srv=http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8790);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1400,height:900}}); p.on('pageerror',e=>console.log('PAGEERROR',e.message));
const ifr=[]; await p.route('**/*', r=>{ const u=r.request().url(); if(/nofilter-gis-map|nofilter-shared/.test(u)) { ifr.push([Math.round(performance.now()), u.split('/').slice(2).join('/').slice(0,50)]); return r.fulfill({status:200, body:''}); } r.continue(); });
const t0=Date.now(); await p.goto('http://localhost:8790/wholesale-coffee/',{waitUntil:'load'}); await p.waitForTimeout(2500);
console.log('iframe src set:', await p.evaluate(()=>{ const f=document.querySelector('iframe[data-counter-src]'); return f? (f.src||'(none)').slice(0,60) : 'no frame'; }));
console.log('work videos wet:', await p.evaluate(()=>[...document.querySelectorAll('#work video')].map(v=>!!(v.getAttribute('src')||v.querySelector('source[src]'))).join(' ')));
console.log('home videos wet (should be no):', await p.evaluate(()=>[...document.querySelectorAll('#home video')].map(v=>!!(v.getAttribute('src')||v.querySelector('source[src]'))).join(' ')));
// now navigate to home and check hero hydrates + nothing else
await p.evaluate(()=>location.hash='#home'); await p.waitForTimeout(1500);
console.log('after → home, home videos wet:', await p.evaluate(()=>[...document.querySelectorAll('#home video')].map(v=>!!(v.getAttribute('src')||v.querySelector('source[src]'))).join(' ')));
console.log('origins videos wet (should be no):', await p.evaluate(()=>[...document.querySelectorAll('#origins video')].map(v=>!!(v.getAttribute('src')||v.querySelector('source[src]'))).join(' ')));
await b.close(); srv.close();
