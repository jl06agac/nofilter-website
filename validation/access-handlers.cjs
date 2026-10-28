// Executes generated handlers with outbound email intercepted. Prints no codes or rates.
const assert=require('node:assert/strict'),crypto=require('node:crypto'),path=require('node:path');
process.env.ACCESS_SECRET=crypto.randomBytes(32).toString('hex');process.env.RESEND_API_KEY='test-only';process.env.QUOTE_FROM='test@example.invalid';process.env.QUOTE_TO='test@example.invalid';
let code,deliveries=0;
global.fetch=async(url,options)=>{assert.equal(url,'https://api.resend.com/emails');const p=JSON.parse(options.body);deliveries++;if(p.subject.startsWith('Your NoFilter Access Code'))code=p.subject.split(' · ')[1];return {ok:true,text:async()=>''};};
const root=path.resolve('SHIP-2026-10-28a/netlify/functions');const request=require(root+'/access-request.js').handler,verify=require(root+'/access-verify.js').handler;
const event=p=>({httpMethod:'POST',body:JSON.stringify(p)});
(async()=>{const email='validation@example.invalid';let r=await request(event({email,company:'Local validation',name:'Test'}));assert.equal(r.statusCode,200);assert(code);assert.equal(deliveries,2);console.log('PASS request handler generated a code; both outbound emails intercepted');
r=await verify(event({email,code:'INVALID'}));assert.equal(r.statusCode,401);assert(!JSON.parse(r.body).rates);console.log('PASS invalid code denied with no rates');
r=await verify(event({email:'other@example.invalid',code}));assert.equal(r.statusCode,401);console.log('PASS code bound to requesting email');
r=await verify(event({email,code}));assert.equal(r.statusCode,200);const p=JSON.parse(r.body);assert(p.ok);assert.deepEqual(Object.keys(p.rates).sort(),['AE','SG','UK']);assert.equal(r.headers['Cache-Control'],'no-store');console.log('PASS valid code returns all three market payloads with no-store');
const now=Date.now;Date.now=()=>now()+3*24*60*60*1000;r=await verify(event({email,code}));Date.now=now;assert.equal(r.statusCode,401);console.log('PASS expired code denied');
console.log('LIMIT: handler integration only. Browser gate and live email delivery untested.');})().catch(e=>{console.error('FAIL',e.message);process.exitCode=1;});
