// node --test nf-build-tools/ship/tests/shop-functions.test.cjs  (no network: Stripe is mocked)
const test=require('node:test'),assert=require('node:assert/strict'),path=require('path');
const F=path.join(__dirname,'..','SHIP-2026-08-30f','netlify','functions');
const checkout=require(path.join(F,'checkout.js')),report=require(path.join(F,'shop-ngo-report.js'));
const ev=(body,headers={origin:'https://nofilter.sg'})=>({httpMethod:'POST',headers,body:JSON.stringify(body)});
function mockStripe(handler){const calls=[];global.fetch=async(url,opt={})=>{calls.push({url,opt});const r=handler(url,opt);return {ok:r.ok!==false,json:async()=>r.body};};return calls;}

test('no key: 503, nothing sent',async()=>{delete process.env.STRIPE_SECRET_KEY;assert.equal((await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}]}))).statusCode,503);});

test('only the four coffees in 250 g or 1 kg; quantities merged and capped',()=>{
 const c=checkout._test.cleanLines;
 assert.equal(c([{name:'Free coffee',size:'1kg',qty:1}]),null);
 assert.equal(c([{name:'Gayo Lues',size:'5kg',qty:1}]),null);
 assert.equal(c([{name:'Gayo Lues',size:'1kg',qty:0}]),null);
 assert.deepEqual(c([{name:'Gayo Lues',size:'1 KG',qty:15},{name:'Gayo Lues',size:'1kg',qty:9}]),[{name:'Gayo Lues',size:'1kg',qty:20}]);
});

test('prices are set here, every line carries its origin and partner, delivery in Singapore',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';delete process.env.PRICE_BAG_1KG;delete process.env.PRICE_BAG_250G;
 const calls=mockStripe(u=>({body:{url:'https://checkout.stripe.com/s/1'}}));
 const r=await checkout.handler(ev({lines:[{name:'Batang Gadis',size:'1kg',qty:2,price:0.01},{name:'Batang Toru',size:'250g',qty:1}]}));
 assert.equal(r.statusCode,200);assert.equal(JSON.parse(r.body).url,'https://checkout.stripe.com/s/1');
 const f=new URLSearchParams(calls[0].opt.body);
 assert.equal(f.get('line_items[0][price_data][unit_amount]'),'8000','the page cannot set a price');
 assert.equal(f.get('line_items[1][price_data][unit_amount]'),'2400');
 assert.equal(f.get('line_items[0][price_data][product_data][metadata][origin]'),'gadis');
 assert.equal(f.get('line_items[0][price_data][product_data][metadata][partner]'),'SRI');
 assert.equal(f.get('line_items[1][price_data][product_data][metadata][partner]'),'PRCF Indonesia, SRI');
 assert.equal(f.get('metadata[contribution_rate]'),'0.10');assert.equal(f.get('metadata[source]'),'website-shop');
 assert.equal(f.get('shipping_address_collection[allowed_countries][0]'),'SG');
 assert.equal(f.get('allow_promotion_codes'),'true','customers can enter a code');
 assert.equal(f.get('success_url'),'https://nofilter.sg/shop/?paid=1&order={CHECKOUT_SESSION_ID}');
});

test('a known client code is applied; an unknown one leaves the code box open',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';
 let calls=mockStripe(u=>u.includes('promotion_codes')?{body:{data:[{id:'promo_123'}]}}:{body:{url:'https://checkout.stripe.com/s/2'}});
 let r=await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],code:'sprinklr-10'}));
 assert.match(calls[0].url,/code=SPRINKLR10/);let f=new URLSearchParams(calls[1].opt.body);
 assert.equal(f.get('discounts[0][promotion_code]'),'promo_123');assert.equal(f.get('allow_promotion_codes'),null);assert.equal(JSON.parse(r.body).code,'SPRINKLR10');
 calls=mockStripe(u=>u.includes('promotion_codes')?{body:{data:[]}}:{body:{url:'https://checkout.stripe.com/s/3'}});
 r=await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],code:'NOPE'}));
 f=new URLSearchParams(calls[1].opt.body);assert.equal(f.get('discounts[0][promotion_code]'),null);assert.equal(f.get('allow_promotion_codes'),'true');assert.equal(f.get('metadata[code]'),'NOPE');
});

test('report: 10% of what was paid after discounts, by origin and partner',()=>{
 const lines=[{amount_total:7200,quantity:1,price:{product:{metadata:{origin:'gadis',partner:'SRI'}}}},{amount_total:4320,quantity:2,price:{product:{metadata:{origin:'gayo',partner:'OIC'}}}},{amount_total:2160,quantity:1,price:{product:{metadata:{origin:'gadis',partner:'SRI'}}}}];
 const c=report._test.contributions(lines,0.10);
 assert.equal(c['gadis|SRI'].sales,9360);assert.equal(c['gadis|SRI'].contribution,936);assert.equal(c['gadis|SRI'].bags,2);
 assert.equal(c['gayo|OIC'].contribution,432);
});

test('report: key required; totals across orders; other Stripe sessions ignored; refunds listed',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.REPORT_KEY='secret';
 const q={from:'2026-11-01',to:'2026-11-30'};
 assert.equal((await report.handler({headers:{'x-report-key':'wrong'},queryStringParameters:q})).statusCode,403);
 const line=(amt,o,p)=>({amount_total:amt,quantity:1,price:{product:{metadata:{origin:o,partner:p}}}});
 mockStripe(u=>{
  if(u.includes('/line_items'))return {body:{data:u.includes('cs_1')?[line(8000,'gadis','SRI')]:[line(2400,'gadis','SRI'),line(2400,'gayo','OIC')]}};
  return {body:{has_more:false,data:[
   {id:'cs_1',payment_status:'paid',metadata:{source:'website-shop',contribution_rate:'0.10'},payment_intent:{latest_charge:{refunded:false}}},
   {id:'cs_2',payment_status:'paid',metadata:{source:'website-shop',contribution_rate:'0.10'},payment_intent:{latest_charge:{refunded:true}}},
   {id:'cs_x',payment_status:'paid',metadata:{source:'something-else'}},
   {id:'cs_u',payment_status:'unpaid',metadata:{source:'website-shop'}}]}};});
 const r=JSON.parse((await report.handler({headers:{'x-report-key':'secret'},queryStringParameters:q})).body);
 assert.equal(r.orders,2);assert.deepEqual(r.refunded,['cs_2']);
 const gadis=r.byPartner.find(x=>x.origin==='gadis');assert.equal(gadis.sales,10400);assert.equal(gadis.contribution,1040);
 assert.equal(r.contribution,1040+240);
 assert.equal(report._test.sgDay('2026-11-01',false),Math.floor(Date.parse('2026-10-31T16:00:00Z')/1000),'Singapore dates');
});

test('order summary: only paid shop orders; contribution by partner; nothing personal',async()=>{
 const sum=require(path.join(F,'order-summary.js'));process.env.STRIPE_SECRET_KEY='sk_test_x';
 assert.equal((await sum.handler({queryStringParameters:{order:'../../etc'}})).statusCode,400);
 mockStripe(u=>u.includes('/line_items')?{body:{data:[{description:'Batang Gadis coffee, 1 kg',quantity:1,amount_total:8000,price:{product:{metadata:{origin:'gadis',partner:'SRI'}}}},{description:'Gayo Lues coffee, 250 g',quantity:2,amount_total:4800,price:{product:{metadata:{origin:'gayo',partner:'OIC'}}}}]}}
  :{body:{payment_status:'paid',currency:'sgd',metadata:{source:'website-shop',contribution_rate:'0.10',code:'SPRINKLR10'},customer_details:{email:'a@b.c',name:'X'}}});
 const r=JSON.parse((await sum.handler({queryStringParameters:{order:'cs_test_abcdefghijklmnop'}})).body);
 assert.equal(r.bags,3);assert.equal(r.contribution,1280);assert.deepEqual(r.byPartner.map(x=>[x.name,x.partner,x.contribution]),[['Batang Gadis','SRI',800],['Gayo Lues','OIC',480]]);
 assert(!JSON.stringify(r).includes('a@b.c'),'no personal details');
 mockStripe(()=>({body:{payment_status:'unpaid',metadata:{source:'website-shop'}}}));
 assert.equal((await sum.handler({queryStringParameters:{order:'cs_test_abcdefghijklmnop'}})).statusCode,404);
});
