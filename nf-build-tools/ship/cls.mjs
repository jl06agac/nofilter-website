import {chromium} from 'playwright';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1350,height:940}});
await p.addInitScript(()=>{ window.__ls=[]; new PerformanceObserver(l=>{ for(const e of l.getEntries()){ if(e.hadRecentInput) continue; window.__ls.push({t:Math.round(e.startTime), v:+e.value.toFixed(4), src:(e.sources||[]).map(s=>{const n=s.node; if(!n) return '?'; const id=n.id?'#'+n.id:''; const cls=n.className&&typeof n.className==='string'?'.'+n.className.trim().split(/\s+/).slice(0,3).join('.'):''; return (n.tagName||'')+id+cls+' ['+Math.round(s.previousRect.top)+'→'+Math.round(s.currentRect.top)+', h'+Math.round(s.previousRect.height)+'→'+Math.round(s.currentRect.height)+']';})}); } }).observe({type:'layout-shift', buffered:true}); });
await p.goto('http://localhost:9005/',{waitUntil:'load'}); await p.waitForTimeout(9000);
const ls=await p.evaluate(()=>window.__ls); let tot=0; for(const e of ls){ tot+=e.v; console.log(e.t+'ms', e.v, e.src.join(' | ')); } console.log('CLS total', tot.toFixed(4));
await b.close();
