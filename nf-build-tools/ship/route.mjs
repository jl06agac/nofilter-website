import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const ROOT='/home/claude/ship/'+process.argv[2];
const srv=http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8769);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
for(const path of ['/shop/','/origins/','/origins/gayo-lues/','/trade-pricing/','/ae/shop/']){
  const p=await b.newPage({viewport:{width:1400,height:900}}); await p.route('https://nofilter-shared.netlify.app/**', r=>r.fulfill({status:200, body:''}));
  await p.goto('http://localhost:8769'+path,{waitUntil:'load'}); await p.waitForTimeout(1500);
  console.log(path, '→ on:', await p.evaluate(()=>[...document.querySelectorAll('.route.on')].map(s=>s.id).join(',')), '| __nfRoute:', await p.evaluate(()=>window.__nfRoute), '| url:', await p.evaluate(()=>location.pathname+location.hash), '| mkt:', await p.evaluate(()=>window.__nfCur), '| drawer open:', await p.evaluate(()=>[...document.querySelectorAll('.fbh-drawer:not([hidden])')].map(d=>d.id).join(',')));
  await p.close();
}
await b.close(); srv.close();
