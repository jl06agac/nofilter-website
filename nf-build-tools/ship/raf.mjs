import {chromium} from 'playwright';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1350,height:940}});
await p.addInitScript(()=>{ const o=window.requestAnimationFrame; window.__rafN=0; window.__rafBy=new Map(); window.requestAnimationFrame=function(cb){ return o.call(window,function(t){ window.__rafN++; const k=(cb.toString().slice(0,90)).replace(/\s+/g,' '); window.__rafBy.set(k,(window.__rafBy.get(k)||0)+1); return cb(t); }); }; const oi=window.setInterval; window.__ivs=[]; window.setInterval=function(f,ms){ window.__ivs.push([ms,f.toString().slice(0,80).replace(/\s+/g,' ')]); return oi.apply(window,arguments); }; });
await p.goto('http://localhost:9003/',{waitUntil:'load'}); await p.waitForTimeout(7000);
await p.evaluate(()=>{ window.__rafN=0; window.__rafBy.clear(); }); await p.waitForTimeout(3000);
const r=await p.evaluate(()=>({n:window.__rafN, by:[...window.__rafBy.entries()].sort((a,b)=>b[1]-a[1]).slice(0,12), ivs:window.__ivs.filter(x=>x[0]<2000)}));
console.log('rAF callbacks in 3s idle:', r.n); for(const [k,v] of r.by) console.log(String(v).padStart(5), k); console.log('short intervals:', JSON.stringify(r.ivs));
await b.close();
