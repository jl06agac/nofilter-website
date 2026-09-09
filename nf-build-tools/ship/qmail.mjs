import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const ROOT='/home/claude/ship/SHIP-2026-09-02h';
const srv=http.createServer((req,res)=>{ if(req.method==='POST'){res.writeHead(200);return res.end('ok');} let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8766);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1500,height:950}}); p.on('pageerror',e=>console.log('PAGEERROR',e.message));
const posts=[]; await p.route('**/*', r=>{ const q=r.request(); if(q.method()==='POST'){ posts.push([q.url().replace('http://localhost:8766',''), q.postData()]); return r.fulfill({status:200, body:'ok'}); } r.continue(); });
await p.goto('http://localhost:8766/',{waitUntil:'load'}); await p.waitForTimeout(1200);
await p.evaluate(()=>{ window.__nfGrantAccess && window.__nfGrantAccess(); }); await p.waitForTimeout(1200);
await p.evaluate(()=>{ document.querySelector('[data-deckmkt="UK"]')?.click(); }); await p.waitForTimeout(600);
// pick the first coffee tile and the first machine through the UI
await p.evaluate(()=>{ const t=document.querySelector('#nfConsoleWrap .cx-tile'); t&&t.click(); }); await p.waitForTimeout(400);
await p.evaluate(()=>{ const a=document.querySelector('#nfConsoleWrap .mach .mx-add, #nfConsoleWrap .mach button'); a&&a.click(); }); await p.waitForTimeout(600);
await p.evaluate(()=>{ document.querySelector('#fName').value='Alex Clark'; document.querySelector('#fCo').value='NoFilter'; document.querySelector('#fEmail').value='alex@nofilter.sg'; const f=document.querySelector('#fName').closest('form'); f.requestSubmit ? f.requestSubmit() : f.dispatchEvent(new Event('submit',{cancelable:true,bubbles:true})); });
await p.waitForTimeout(1500);
for(const [u,d] of posts){ console.log('POST', u); if(u.includes('quote-confirm')){ const j=JSON.parse(d); console.log(JSON.stringify({price:j.price,rate:j.rate,topUpKg:j.topUpKg,topUpMo:j.topUpMo,consPerKg:j.consPerKg,cupsY:j.cupsY,kg:j.kg,total:j.total,market:j.market,machines:j.machines,coffee:j.coffee})); } else { console.log(decodeURIComponent(d).split('&').filter(x=>/coffee_price_kg|topup_kg|conservation_kg|band_rate|monthly_total/.test(x)).join('  ')); } }
// footer screenshot
await p.evaluate(()=>document.querySelector('.foot-entities').scrollIntoView()); await p.waitForTimeout(500);
const bb=await (await p.$('.foot-entities')).boundingBox(); await p.screenshot({path:'ukfoot.png',clip:{x:0,y:bb.y-20,width:1500,height:bb.height+60}});
await b.close(); srv.close();
