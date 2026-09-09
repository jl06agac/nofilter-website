import {chromium} from 'playwright'; import {PNG} from 'pngjs'; import pixelmatch from 'pixelmatch'; import {readFileSync, writeFileSync} from 'node:fs';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
async function shots(port, tag){
  for(const [w,h] of [[1350,940],[390,844]]){
    const p=await b.newPage({viewport:{width:w,height:h}, reducedMotion:'reduce'});
    await p.goto(`http://localhost:${port}/`,{waitUntil:'load'}); await p.waitForTimeout(6500);
    for(const r of ['home','origins','shop','work']){ await p.evaluate(r=>{location.hash='#'+r;},r); await p.waitForTimeout(1200); await p.evaluate(()=>{ document.querySelectorAll('video').forEach(v=>{try{v.pause()}catch(e){}}); }); await p.screenshot({path:`shot-${tag}-${w}-${r}.png`, fullPage:true}); }
    await p.close();
  }
}
await shots(9000,'d'); await shots(9003,'e');
for(const w of [1350,390]) for(const r of ['home','origins','shop','work']){
  const A=PNG.sync.read(readFileSync(`shot-d-${w}-${r}.png`)), B=PNG.sync.read(readFileSync(`shot-e-${w}-${r}.png`));
  if(A.width!==B.width||A.height!==B.height){ console.log(w,r,'SIZE DIFF',A.width,A.height,'vs',B.width,B.height); continue; }
  const diff=new PNG({width:A.width,height:A.height}); const n=pixelmatch(A.data,B.data,diff.data,A.width,A.height,{threshold:0.15}); writeFileSync(`diff-${w}-${r}.png`,PNG.sync.write(diff));
  console.log(w,r,'px differing:',n,'of',A.width*A.height,(100*n/(A.width*A.height)).toFixed(2)+'%');
}
await b.close();
