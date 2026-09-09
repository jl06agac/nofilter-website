import {chromium} from 'playwright';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage(); await p.route('**/*.{mp4,webp,jpg,png,woff2}', r=>r.fulfill({status:200,body:''}));
await p.goto('file:///home/claude/ship/SHIP-2026-09-02c/index.html',{waitUntil:'load'}); await p.waitForTimeout(500);
console.log((await p.evaluate(()=>[...document.querySelectorAll('video')].map(v=>{const r=v.closest('.route'); const s=v.getAttribute('src')||v.querySelector('source')?.getAttribute('src')||v.querySelector('source')?.getAttribute('data-src')||'-'; return (r?r.id:'NOROUTE')+' | '+(v.className||'')+' | preload='+v.getAttribute('preload')+' | '+s.split('/').pop()+' | data-o='+(v.closest('[data-o]')?.getAttribute('data-o')||'')}))).join("\n"));
await b.close();
