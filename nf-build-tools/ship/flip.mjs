import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const mk=(ROOT,port)=>http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(port);
const s1=mk('/home/claude/ship/SHIP-2026-09-02h',8791), s2=mk('/home/claude/ship/SHIP-2026-09-02i',8792);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
for(const [port,tag] of [[8791,'02h'],[8792,'02i']]){
  const p=await b.newPage({viewport:{width:1400,height:900}}); await p.route('**/nofilter-shared.netlify.app/**', r=>r.fulfill({status:200,body:''}));
  await p.goto(`http://localhost:${port}/wholesale-coffee/`,{waitUntil:'load'}); await p.waitForTimeout(2500);
  const flips=await p.evaluate(async()=>{ const host=document.querySelector('#work .nw-livewrap .nw-screen'); host.scrollIntoView(); await new Promise(r=>setTimeout(r,300)); let n=0; new MutationObserver(()=>n++).observe(host,{attributes:true,attributeFilter:['class']});
    // slow trackpad: 2px every 120ms for 3s
    for(let i=0;i<25;i++){ window.scrollBy(0,2); await new Promise(r=>setTimeout(r,120)); } await new Promise(r=>setTimeout(r,600)); return n; });
  console.log(tag,'class flips during a slow 3s scroll:',flips);
  await p.close();
}
await b.close(); s1.close(); s2.close();
