import {chromium} from 'playwright';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const ctx=await b.newContext({viewport:{width:1350,height:940}}); const p=await ctx.newPage();
const c=await ctx.newCDPSession(p); await c.send('Profiler.enable'); await c.send('Profiler.setSamplingInterval',{interval:200}); await c.send('Profiler.start');
await p.goto(process.argv[2]||'http://localhost:9000/',{waitUntil:'load'}); await p.waitForTimeout(4000);
const {profile}=await c.send('Profiler.stop');
// self time per node
const dt=profile.timeDeltas; const samples=profile.samples; const byId=new Map(profile.nodes.map(n=>[n.id,n]));
const self=new Map(); for(let i=0;i<samples.length;i++){ const n=byId.get(samples[i]); const k=n.callFrame.functionName+' @'+(n.callFrame.url.split('/').pop()||'')+':'+n.callFrame.lineNumber; self.set(k,(self.get(k)||0)+(dt[i]||0)); }
const tot=[...self.values()].reduce((a,b)=>a+b,0);
console.log('total sampled ms', Math.round(tot/1000));
[...self.entries()].sort((a,b)=>b[1]-a[1]).slice(0,25).forEach(([k,v])=>console.log(String(Math.round(v/1000)).padStart(5),'ms', k));
// inclusive time for top-level script blocks: attribute by walking parents to the root's children
const parent=new Map(); for(const n of profile.nodes) for(const ch of (n.children||[])) parent.set(ch,n.id);
const incl=new Map(); for(let i=0;i<samples.length;i++){ let id=samples[i]; const seen=new Set(); while(id!=null){ const n=byId.get(id); const k=n.callFrame.functionName+' @'+n.callFrame.lineNumber+':'+n.callFrame.columnNumber; if(!seen.has(k)){ seen.add(k); incl.set(k,(incl.get(k)||0)+(dt[i]||0)); } id=parent.get(id); } }
console.log('--- inclusive (anonymous top-level IIFEs by line:col)');
[...incl.entries()].filter(([k])=>/^ @|^\(anonymous\)|^__nf|^init|^boot|^apply|^build|^render/.test(k)).sort((a,b)=>b[1]-a[1]).slice(0,20).forEach(([k,v])=>console.log(String(Math.round(v/1000)).padStart(5),'ms', k));
await b.close();
