import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const [ROOTN, path] = [process.argv[2], process.argv[3]||'/shop/'];
const ROOT='/home/claude/ship/'+ROOTN;
const srv=http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8768);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1400,height:900}}); p.on('pageerror',e=>console.log('PAGEERROR',e.message));
const reqs=[]; await p.route('https://nofilter-shared.netlify.app/**', r=>{ reqs.push(r.request().url().split('/').pop()); r.fulfill({status:200, body:''}); });
await p.goto('http://localhost:8768'+path,{waitUntil:'load'}); await p.waitForTimeout(2500);
const mp4=reqs.filter(x=>x.endsWith('.mp4')), img=reqs.filter(x=>/\.(webp|jpg|png)$/.test(x));
console.log(ROOTN, path, '| mp4 requests:', mp4.length, [...new Set(mp4)].join(', '), '| images:', img.length, [...new Set(img)].join(', '));
// now navigate to origins and scroll: do the banners hydrate?
await p.evaluate(()=>{ location.hash='#origins'; }); await p.waitForTimeout(800);
await p.evaluate(()=>window.scrollTo(0, 1200)); await p.waitForTimeout(1200);
const mp4b=reqs.filter(x=>x.endsWith('.mp4'));
console.log('after opening origins + scroll: mp4 requests', mp4b.length, [...new Set(mp4b)].join(', '));
console.log('videos with src now:', await p.evaluate(()=>[...document.querySelectorAll('video')].filter(v=>v.getAttribute('src')||v.querySelector('source[src]')).map(v=>(v.closest('.route')||{}).id+':'+((v.getAttribute('src')||v.querySelector('source[src]').getAttribute('src')).split('/').pop())).join(', ')));
console.log('dead videos:', await p.evaluate(()=>document.querySelectorAll('video.dead').length));
await b.close(); srv.close();
