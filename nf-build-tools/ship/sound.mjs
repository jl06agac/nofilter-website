import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const ROOT='/home/claude/ship/'+(process.argv[2]||'SHIP-2026-09-02k');
const srv=http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8796);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage({viewport:{width:1400,height:900}}); p.on('pageerror',e=>console.log('PAGEERROR',e.message));
let callReq=0; await p.route('**/nofilter-shared.netlify.app/**', r=>{ if(r.request().url().includes('nf-board-call')) callReq++; r.fulfill({status:200,body:''}); });
await p.goto('http://localhost:8796/wholesale-coffee/',{waitUntil:'load'}); await p.waitForTimeout(800);
await (await p.$('#nfBoard')).scrollIntoViewIfNeeded(); await p.waitForTimeout(700);
// instrument: count buffer sources started
await p.evaluate(()=>{ window.__starts=0; const P=AudioBufferSourceNode.prototype, o=P.start; P.start=function(){ window.__starts++; return o.apply(this,arguments); }; });
const btn=await p.$('#nfBoardSound'); const box=await btn.boundingBox(); console.log('button', JSON.stringify(box), await btn.getAttribute('aria-pressed'), await p.evaluate(()=>document.querySelector('.nfb-snd-t').textContent));
console.log('call requests before tap:', callReq);
await btn.click(); await p.waitForTimeout(400);
console.log('after tap:', await btn.getAttribute('aria-pressed'), await p.evaluate(()=>document.querySelector('.nfb-snd-t').textContent), 'stored=', await p.evaluate(()=>localStorage.getItem('nf-board-sound')), 'callReq=', callReq);
await p.screenshot({path:'sound-on.png', clip:{x:box.x-260,y:box.y-60,width:300,height:90}});
await p.waitForTimeout(6000);
console.log('buffer sources started in 6s of story:', await p.evaluate(()=>window.__starts));
// gate: scrolled away → no clicks
await p.evaluate(()=>scrollTo(0,0)); await p.waitForTimeout(600); const s0=await p.evaluate(()=>window.__starts); await p.waitForTimeout(3000);
console.log('clicks while scrolled away:', await p.evaluate(()=>window.__starts)-s0);
await (await p.$('#nfBoard')).scrollIntoViewIfNeeded(); await p.waitForTimeout(600);
await btn.click(); await p.waitForTimeout(600); const s1=await p.evaluate(()=>window.__starts); await p.waitForTimeout(3000);
console.log('after switching off:', await btn.getAttribute('aria-pressed'), 'clicks:', await p.evaluate(()=>window.__starts)-s1, 'stored=', await p.evaluate(()=>localStorage.getItem('nf-board-sound')));
// remembered on: reload with '1'
await p.evaluate(()=>localStorage.setItem('nf-board-sound','1')); await p.reload({waitUntil:'load'}); await p.waitForTimeout(800);
console.log('remembered:', await p.getAttribute('#nfBoardSound','aria-pressed'), 'ctx before gesture:', await p.evaluate(()=>window.__nfBoard.sound.isOn()));
await p.mouse.click(200,200); await p.waitForTimeout(300);
await (await p.$('#nfBoard')).scrollIntoViewIfNeeded(); await p.evaluate(()=>{ window.__starts=0; const P=AudioBufferSourceNode.prototype, o=P.start; P.start=function(){ window.__starts++; return o.apply(this,arguments); }; }); await p.waitForTimeout(6000);
console.log('remembered-on clicks in 6s:', await p.evaluate(()=>window.__starts));
// direct call: does call() fetch + play (mocked)?
await p.evaluate(()=>window.__nfBoard.sound.call()); await p.waitForTimeout(500); console.log('call requests after call():', callReq);
await p.close(); await b.close(); srv.close();
