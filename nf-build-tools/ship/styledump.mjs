// dumps computed styles of every element per route/width so two builds can be diffed
import {chromium} from 'playwright';
import {writeFileSync} from 'node:fs';
const [,, port, out] = process.argv;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const res={};
for(const w of [1400, 820, 390]){
  const p=await b.newPage({viewport:{width:w,height:900}});
  await p.goto(`http://localhost:${port}/`,{waitUntil:'load'}); await p.waitForTimeout(1500);
  for(const r of ['home','origins','shop','work','quote']){
    await p.evaluate(r=>{ location.hash='#'+r; }, r); await p.waitForTimeout(700);
    if(r==='quote'){ await p.evaluate(()=>{ window.__nfGrantAccess && window.__nfGrantAccess(); }); await p.waitForTimeout(900); }
    if(r==='origins'){ await p.evaluate(()=>{ document.querySelector('.fbh-more[aria-controls="fbhd-gadis"]')?.click(); }); await p.waitForTimeout(700); }
    const dump=await p.evaluate(()=>{
      const PROPS=['display','position','color','background-color','background-image','font-family','font-size','font-weight','font-style','line-height','letter-spacing','text-transform','text-align','margin-top','margin-bottom','margin-left','margin-right','padding-top','padding-bottom','padding-left','padding-right','border-top-width','border-bottom-width','border-left-width','border-right-width','border-top-color','border-radius','gap','grid-template-columns','flex-direction','align-items','justify-content','overflow-x','overflow-y','z-index','max-width','min-height','box-shadow','outline-style','pointer-events','cursor','text-decoration-line','white-space','flex','order','aspect-ratio','object-fit','mix-blend-mode','backdrop-filter','border-style'];
      const out=[]; const els=document.querySelectorAll('body *');
      for(const el of els){ if(el.closest('script,style,svg')) continue; const cs=getComputedStyle(el); let s=''; for(const k of PROPS) s+=k+':'+cs.getPropertyValue(k)+';';
        const path=el.tagName+(el.id?'#'+el.id:'')+(el.className&&typeof el.className==='string'?'.'+el.className.trim().split(/\s+/).slice(0,3).join('.'):'');
        out.push([path, s]); }
      return out; });
    res[w+'/'+r]=dump;
  }
  await p.close();
}
await b.close();
writeFileSync(out, JSON.stringify(res));
console.log('dumped', Object.keys(res).length, 'states to', out);
