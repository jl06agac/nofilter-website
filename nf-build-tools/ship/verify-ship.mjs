import {chromium} from 'playwright';
import {readdirSync, statSync} from 'node:fs';
import {join} from 'node:path';
const ROOT='/home/claude/ship/'+(process.argv[2]||'SHIP-2026-09-02d');
const pages=[]; (function walk(d){ for(const e of readdirSync(d)){ const p=join(d,e); if(statSync(p).isDirectory()){ if(e!=='netlify'&&e!=='assets') walk(p);} else if(e.endsWith('.html')&&e!=='404.html') pages.push(p);} })(ROOT);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
let bad=0;
for(const f of pages){
  const p=await b.newPage({viewport:{width:1586,height:993}});
  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERROR '+e.message)); p.on('console',m=>{ if(m.type()==='error' && !/net::ERR|Failed to load resource|404/.test(m.text())) errs.push('CONSOLE '+m.text()); });
  await p.goto('file://'+f,{waitUntil:'load'}); await p.waitForTimeout(1200);
  const info=await p.evaluate(()=>({on:[...document.querySelectorAll('section.route.on')].map(s=>s.id).join(','), title:document.title, ship:document.querySelector('meta[name="nf-ship"]')?.content, canon:document.querySelector('link[rel=canonical]')?.href, mkt:document.querySelector('#mktSel [aria-pressed="true"]')?.dataset.mkt, hasDeck:!!document.querySelector('[data-deckmkt="UK"]')}));
  const rel=f.replace(ROOT+'/','');
  if(errs.length) bad++;
  console.log(rel.padEnd(42), JSON.stringify(info), errs.length?('\n   '+errs.slice(0,3).join('\n   ')):'');
  await p.close();
}
// deck flow on the trade-pricing page, UK
const p=await b.newPage({viewport:{width:1586,height:993}});
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+ROOT+'/trade-pricing/index.html',{waitUntil:'load'}); await p.waitForTimeout(1500);
await p.evaluate(()=>{document.documentElement.classList.add('nf-unlocked'); const c=document.getElementById('nfConsoleWrap');c.removeAttribute('aria-hidden'); document.body.appendChild(c);c.classList.add('nf-focus-sec');document.documentElement.classList.add('nf-focus-on'); [...document.querySelectorAll('.deck-screen')].forEach((el,i)=>el.classList.toggle('is-active',i===1)); window.dispatchEvent(new Event('resize'));});
await p.waitForTimeout(800);
for(const mk of ['UK','AE','SG']){ await p.evaluate(k=>document.querySelector('[data-deckmkt="'+k+'"]').click(),mk); await p.waitForTimeout(700);
  console.log(mk, await p.evaluate(()=>[...document.querySelectorAll('.q-eq-card')].map(c=>c.querySelector('.q-eq-name').textContent+' '+c.querySelector('.mx-add-main')?.textContent.replace(/\s+/g,' ').trim()).join(' | ')+' | '+document.querySelector('#specHd').textContent)); }
await p.evaluate(()=>{[...document.querySelectorAll('.deck-screen')].forEach((el,i)=>el.classList.toggle('is-active',i===2)); window.dispatchEvent(new Event('resize'));}); await p.waitForTimeout(900);
for(const ph of [0,1,2]){ await p.evaluate(n=>window.__nfGoPhase(n),ph); await p.waitForTimeout(600); console.log('ph'+ph, await p.evaluate(()=>document.getElementById('morphFigure').textContent.replace(/\s+/g,' ').trim()+' gutters:'+document.querySelectorAll('.mgut.is-on').length)); }
console.log('deck errors:', errs.length? errs : 'none');
await b.close();
console.log(bad? `${bad} pages with errors` : 'all pages clean');
