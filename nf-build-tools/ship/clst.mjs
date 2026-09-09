import {chromium} from 'playwright';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:800,height:600}});
await p.goto('file:///home/claude/ship/clstest.html'); await p.waitForTimeout(3200);
console.log(JSON.stringify(await p.evaluate(()=>window.__ls)));
await b.close();
