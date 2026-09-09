import {chromium} from 'playwright';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1350,height:940}});
const t0=Date.now(); const log=[]; p.on('request',r=>{ const u=r.url(); if(/\.mp4|hero-poster/.test(u)) log.push([Date.now()-t0, u.split('/').pop()]); });
await p.goto('http://localhost:9005/',{waitUntil:'load'}); const tl=Date.now()-t0; await p.waitForTimeout(6500);
console.log('load at', tl,'ms'); console.log(log.map(x=>x.join(' ')).join('\n'));
console.log(await p.evaluate(()=>[...document.querySelectorAll('.cover-video-stack video')].map(v=>v.className+': src='+(v.querySelector('source').getAttribute('src')?'yes':'no')+' playing='+(!v.paused)+' t='+v.currentTime.toFixed(1))));
await b.close();
