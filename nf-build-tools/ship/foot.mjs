import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const ROOT='/home/claude/ship/SHIP-2026-09-02c';
const srv=http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8767);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
for(const [w,name] of [[1500,'wide'],[760,'narrow']]){
  const p=await b.newPage({viewport:{width:w,height:900}});
  await p.goto('http://localhost:8767/',{waitUntil:'load'}); await p.waitForTimeout(1000);
  await p.evaluate(()=>{ document.querySelector('[data-mkt="UK"]')?.click(); }); await p.waitForTimeout(500);
  const el=await p.$('.foot-entities'); await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(400);
  await el.screenshot({path:`ukfoot-${name}.png`});
  console.log(name, await p.evaluate(()=>[...document.querySelectorAll('.foot-ent')].map(e=>e.innerText.replace(/\n/g,' / '))));
  await p.close();
}
await b.close(); srv.close();
