import {chromium} from 'playwright';
import http from 'node:http'; import {readFileSync, existsSync, statSync} from 'node:fs'; import {join} from 'node:path';
const ROOT='/home/claude/ship/SHIP-2026-09-02k';
const srv=http.createServer((req,res)=>{ let p=decodeURIComponent(req.url.split('?')[0]); let f=join(ROOT,p); if(existsSync(f)&&statSync(f).isDirectory()) f=join(f,'index.html'); if(!existsSync(f)){res.writeHead(404);return res.end();} res.writeHead(200,{'Content-Type':f.endsWith('.html')?'text/html':'application/octet-stream'}); res.end(readFileSync(f)); }).listen(8797);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
for(const w of [1400,390]){
const p=await b.newPage({viewport:{width:w,height:900}});
await p.route('**/nofilter-shared.netlify.app/**', r=>r.fulfill({status:200,body:''}));
await p.goto('http://localhost:8797/wholesale-coffee/',{waitUntil:'load'}); await p.waitForTimeout(800);
await (await p.$('#nfBoard')).scrollIntoViewIfNeeded(); await p.waitForTimeout(2500);
const box=await (await p.$('.nw-livewrap')).boundingBox();
await p.screenshot({path:`snd-${w}-off.png`, clip:{x:Math.max(0,box.x-10),y:Math.max(0,box.y-10),width:Math.min(w,box.width+20),height:box.height+20}});
await (await p.$('#nfBoardSound')).click(); await p.waitForTimeout(300);
await p.screenshot({path:`snd-${w}-on.png`, clip:{x:Math.max(0,box.x-10),y:Math.max(0,box.y-10),width:Math.min(w,box.width+20),height:box.height+20}});
await p.close(); }
await b.close(); srv.close();
