import {chromium} from 'playwright';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1350,height:900}});
await p.goto('http://localhost:9010/trade-pricing',{waitUntil:'load'}); await p.waitForTimeout(3000);
const r=await p.evaluate(()=>{const f=document.querySelector('#quote .qplate'); const b=f.getBoundingClientRect(); const col=f.parentElement.getBoundingClientRect(); return {plate:[b.x,b.y,b.width,b.height], col:[col.x,col.y,col.width,col.height], colClass:f.parentElement.className, sib:[...f.parentElement.children].map(e=>e.tagName+'.'+e.className+(e.hidden?'[hidden]':'')+' h='+Math.round(e.getBoundingClientRect().height))};});
console.log(JSON.stringify(r,null,1));
await p.screenshot({path:'q-1350.png'});
await b.close();
