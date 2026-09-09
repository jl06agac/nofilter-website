import {chromium} from 'playwright';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:700,height:520}}); p.on('pageerror',e=>console.log('PAGEERROR',e.message));
await p.goto('file:///home/claude/ship/board-proto.html'); await p.waitForTimeout(500);
await p.screenshot({path:'bp1.png'});
await p.evaluate(()=>{ window.__board.paintField('#16a34a'); window.__board.flipTo(window.__board.toGrid(['','EACH CUP','GIVES','10 CENTS',''])); }); await p.waitForTimeout(500); await p.screenshot({path:'bp2.png'}); await p.waitForTimeout(1200); await p.screenshot({path:'bp3.png'});
await b.close();
