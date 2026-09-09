import {readFileSync} from 'node:fs';
const r=JSON.parse(readFileSync(process.argv[2],'utf8')); const a=r.audits;
console.log('PERF', Math.round(r.categories.performance.score*100), '|', ['first-contentful-paint','largest-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index'].map(k=>k.split('-').map(w=>w[0]).join('').toUpperCase()+' '+a[k].displayValue).join(' | '));
const items=Object.values(a).filter(x=>x.score!==null && x.score<0.9 && x.scoreDisplayMode!=='informative').sort((x,y)=>(x.score-y.score));
for(const x of items){ console.log(' -', x.id, '| score', x.score, '|', x.displayValue||'', '|', (x.title||'').slice(0,60)); }
const lcp=a['largest-contentful-paint-element']; if(lcp&&lcp.details&&lcp.details.items) console.log('LCP element:', JSON.stringify(lcp.details.items[0]).slice(0,300));
const cls=a['layout-shifts']||a['layout-shift-elements']; if(cls&&cls.details) console.log('CLS items:', JSON.stringify(cls.details.items.slice(0,3)).slice(0,600));
const bt=a['bootup-time']; if(bt&&bt.details) console.log('bootup:', bt.displayValue, JSON.stringify(bt.details.items.slice(0,4).map(i=>[i.url.split('/').slice(-2).join('/'),Math.round(i.total),Math.round(i.scripting)])));
const mt=a['mainthread-work-breakdown']; if(mt&&mt.details) console.log('main thread:', mt.displayValue, JSON.stringify(mt.details.items.map(i=>[i.groupLabel,Math.round(i.duration)])));
const rb=a['render-blocking-resources']; if(rb&&rb.details) console.log('render blocking:', JSON.stringify(rb.details.items.map(i=>[i.url.split('/').pop(), i.totalBytes, i.wastedMs])));
const uc=a['unused-css-rules']; if(uc&&uc.details) console.log('unused css:', uc.displayValue, JSON.stringify(uc.details.items.map(i=>[i.url.split('/').pop().slice(0,40), i.totalBytes, i.wastedBytes])));
const uj=a['unused-javascript']; if(uj&&uj.details) console.log('unused js:', uj.displayValue, JSON.stringify(uj.details.items.map(i=>[i.url.split('/').pop().slice(0,40), i.totalBytes, i.wastedBytes])));
const dom=a['dom-size']; if(dom) console.log('dom size:', dom.displayValue);
const lcpb=a['lcp-lazy-loaded']; const fd=a['font-display']; if(fd&&fd.details) console.log('font-display:', JSON.stringify(fd.details.items.map(i=>i.url.split('/').pop())));
const ld=a['lcp-breakdown']||a['largest-contentful-paint-element']; 
const net=a['network-requests']; if(net&&net.details){ const it=net.details.items; console.log('requests:', it.length, 'bytes', Math.round(it.reduce((s,i)=>s+(i.transferSize||0),0)/1024)+'KB'); console.log(it.slice(0,40).map(i=>[i.url.split('/').pop().slice(0,32), i.resourceType, Math.round((i.transferSize||0)/1024)+'K', Math.round(i.networkEndTime-i.networkRequestTime)+'ms'].join(' ')).join('\n')); }
const ttfb=a['server-response-time']; if(ttfb) console.log('TTFB', ttfb.displayValue);
const ins=a['prioritize-lcp-image']; if(ins) console.log('prioritize-lcp-image', ins.displayValue, ins.score);
const lt=a['long-tasks']; if(lt&&lt.details) console.log('long tasks:', JSON.stringify(lt.details.items.slice(0,6).map(i=>[i.url.split('/').pop().slice(0,30), Math.round(i.duration), Math.round(i.startTime)])));
