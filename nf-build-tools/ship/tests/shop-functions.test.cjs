// node --test nf-build-tools/ship/tests/shop-functions.test.cjs  (no network: Stripe is mocked)
const test=require('node:test'),assert=require('node:assert/strict'),path=require('path');
const F=path.join(__dirname,'..','SHIP-2026-08-30f','netlify','functions');
const checkout=require(path.join(F,'checkout.js')),report=require(path.join(F,'shop-ngo-report.js'));
const ev=(body,headers={origin:'https://nofilter.sg'})=>({httpMethod:'POST',headers,body:JSON.stringify(body)});
function mockStripe(handler){const calls=[];global.fetch=async(url,opt={})=>{calls.push({url,opt});const r=handler(url,opt);return {ok:r.ok!==false,json:async()=>r.body};};return calls;}

test('no key: 503, nothing sent',async()=>{delete process.env.STRIPE_SECRET_KEY;process.env.STRIPE_PUBLISHABLE_KEY='pk_test_x';assert.equal((await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}]}))).statusCode,503);});

test('only the four coffees in 250 g or 1 kg; quantities merged and capped',()=>{
 const c=checkout._test.cleanLines;
 assert.equal(c([{name:'Free coffee',size:'1kg',qty:1}]),null);
 assert.equal(c([{name:'Gayo Lues',size:'5kg',qty:1}]),null);
 assert.equal(c([{name:'Gayo Lues',size:'1kg',qty:0}]),null);
 assert.deepEqual(c([{name:'Gayo Lues',size:'1 KG',qty:15},{name:'Gayo Lues',size:'1kg',qty:9}]),[{name:'Gayo Lues',size:'1kg',qty:20,every:0}]);
 assert.equal(c([{name:'Gayo Lues',size:'1kg',qty:1,every:5}]),null,'every 1-4 weeks only');
});

test('prices are set here, every line carries its origin and partner, delivery in Singapore',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_PUBLISHABLE_KEY='pk_test_x';delete process.env.PRICE_BAG_1KG;delete process.env.PRICE_BAG_250G;
 const calls=mockStripe(u=>({body:{client_secret:'cs_test_1_secret_x',id:'cs_test_1'}}));
 const r=await checkout.handler(ev({lines:[{name:'Batang Gadis',size:'1kg',qty:2,price:0.01},{name:'Batang Toru',size:'250g',qty:1}]}));
 assert.equal(r.statusCode,200);const out=JSON.parse(r.body);assert.equal(out.clientSecret,'cs_test_1_secret_x');assert.equal(out.publishableKey,'pk_test_x');assert.equal(out.session,'cs_test_1');
 const f=new URLSearchParams(calls[0].opt.body);
 assert.equal(f.get('line_items[0][price_data][unit_amount]'),'8000','the page cannot set a price');
 assert.equal(f.get('line_items[1][price_data][unit_amount]'),'2400');
 assert.equal(f.get('line_items[0][price_data][product_data][metadata][origin]'),'gadis');
 assert.equal(f.get('line_items[0][price_data][product_data][metadata][partner]'),'SRI');
 assert.equal(f.get('line_items[1][price_data][product_data][metadata][partner]'),'PRCF Indonesia, OIC');
 assert.equal(f.get('metadata[contribution_rate]'),'0.10');assert.equal(f.get('metadata[source]'),'website-shop');
 assert.equal(f.get('shipping_address_collection[allowed_countries][0]'),'SG');
 assert.equal(f.get('allow_promotion_codes'),'true','customers can enter a code');
 assert.equal(f.get('ui_mode'),'embedded_page');assert.equal(f.get('return_url'),'https://nofilter.sg/shop/?paid=1&order={CHECKOUT_SESSION_ID}');
 assert.equal(f.get('line_items[0][price_data][product_data][images][0]'),'https://nofilter-shared.netlify.app/bag-batang-gadis-640.webp');
 assert.equal(f.get('metadata[choice]'),'','no choice yet means where it is needed most');
});

test('a known client code is applied; an unknown one leaves the code box open',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';
 let calls=mockStripe(u=>u.includes('promotion_codes')?{body:{data:[{id:'promo_123'}]}}:{body:{client_secret:'cs_test_2_secret',id:'cs_test_2'}});
 let r=await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],code:'sprinklr-10'}));
 assert.match(calls[0].url,/code=SPRINKLR10/);let f=new URLSearchParams(calls[1].opt.body);
 assert.equal(f.get('discounts[0][promotion_code]'),'promo_123');assert.equal(f.get('allow_promotion_codes'),null);assert.equal(JSON.parse(r.body).code,'SPRINKLR10');
 calls=mockStripe(u=>u.includes('promotion_codes')?{body:{data:[]}}:{body:{client_secret:'cs_test_3_secret',id:'cs_test_3'}});
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

test('order summary: only paid shop orders; order details for the confirmation page; no phone, billing address or card details beyond the last four',async()=>{
 const sum=require(path.join(F,'order-summary.js'));process.env.STRIPE_SECRET_KEY='sk_test_x';
 assert.equal((await sum.handler({queryStringParameters:{order:'../../etc'}})).statusCode,400);
 mockStripe(u=>u.includes('/line_items')?{body:{data:[{description:'Batang Gadis coffee, 1 kg',quantity:1,amount_total:8000,price:{product:{metadata:{origin:'gadis',partner:'SRI'}}}},{description:'Gayo Lues coffee, 250 g',quantity:2,amount_total:4800,price:{product:{metadata:{origin:'gayo',partner:'OIC'}}}}]}}
  :{body:{payment_status:'paid',currency:'sgd',created:1794100000,amount_subtotal:12800,amount_total:11520,total_details:{amount_discount:1280,amount_shipping:0},metadata:{source:'website-shop',contribution_rate:'0.10',code:'SPRINKLR10',order_ref:'NF-7K2Q9M'},customer_details:{email:'a@b.c',name:'Alex Clark',phone:'+6590000000',address:{line1:'BILLING ST'}},collected_information:{shipping_details:{name:'Alex Clark',address:{line1:'1 Raffles Place',line2:'#20-01',city:'Singapore',postal_code:'048616',country:'SG'}}},payment_intent:{latest_charge:{payment_method_details:{type:'card',card:{brand:'visa',last4:'4242',exp_month:12,exp_year:2030,fingerprint:'fp_secret',wallet:{type:'apple_pay'}}}}}}});
 const r=JSON.parse((await sum.handler({queryStringParameters:{order:'cs_test_abcdefghijklmnop'}})).body);
 assert.equal(r.bags,3);assert.equal(r.contribution,1280);assert.deepEqual(r.byPartner.map(x=>[x.name,x.partner,x.contribution]),[['Batang Gadis','SRI',800],['Gayo Lues','OIC',480]]);
 assert.equal(r.order.ref,'NF-7K2Q9M');assert.equal(r.order.email,'a@b.c');assert.equal(r.order.firstName,'Alex');
 assert.deepEqual(r.order.address,['Alex Clark','1 Raffles Place','#20-01','Singapore 048616']);
 assert.deepEqual(r.order.items[0],{name:'Batang Gadis',size:'1 kg',qty:1,amount:8000,every:0});
 assert.equal(r.order.total,11520);assert.equal(r.order.discount,1280);assert.deepEqual(r.order.paidWith,{brand:'visa',last4:'4242',wallet:'apple_pay'});
 const out=JSON.stringify(r);for(const x of ['+6590000000','BILLING','fp_secret','2030'])assert(!out.includes(x),'never returned: '+x);
 mockStripe(()=>({body:{payment_status:'unpaid',metadata:{source:'website-shop'}}}));
 assert.equal((await sum.handler({queryStringParameters:{order:'cs_test_abcdefghijklmnop'}})).statusCode,404);
});

test('the chosen project is recorded on the open order, and only one of the three',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_PUBLISHABLE_KEY='pk_test_x';
 let calls=mockStripe(u=>({body:{client_secret:'cs_test_9_secret',id:'cs_test_9'}}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],choice:'orangutans-in-danger'}));
 assert.equal(new URLSearchParams(calls[0].opt.body).get('metadata[choice]'),'orangutans-in-danger');
 calls=mockStripe(u=>({body:{client_secret:'x',id:'cs_test_9'}}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],choice:'buy-a-yacht'}));
 assert.equal(new URLSearchParams(calls[0].opt.body).get('metadata[choice]'),'');
 calls=mockStripe((u,o)=>o.method==='GET'?{body:{status:'open',metadata:{source:'website-shop'}}}:{body:{}});
 let r=await checkout.handler(ev({action:'choose',session:'cs_test_abcdefghijkl',choice:'coffee-with-forest'}));
 assert.equal(r.statusCode,200);assert.equal(new URLSearchParams(calls[1].opt.body).get('metadata[choice]'),'coffee-with-forest');
 assert.equal((await checkout.handler(ev({action:'choose',session:'cs_test_abcdefghijkl',choice:'nope'}))).statusCode,400);
 mockStripe((u,o)=>({body:{status:'complete',metadata:{source:'website-shop'}}}));
 assert.equal((await checkout.handler(ev({action:'choose',session:'cs_test_abcdefghijkl',choice:'protect-forests'}))).statusCode,409,'a paid order cannot be changed');
});

test('every order gets a quotable number, on the order and its payment',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_PUBLISHABLE_KEY='pk_test_x';
 const calls=mockStripe(()=>({body:{client_secret:'x',id:'cs_test_9'}}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}]}));
 const f=new URLSearchParams(calls[0].opt.body),ref=f.get('metadata[order_ref]');
 assert.match(ref,/^NF-[2-9A-HJKMNP-Z]{6}$/);
 assert.equal(f.get('payment_intent_data[metadata][order_ref]'),ref);assert.equal(f.get('payment_intent_data[description]'),'NoFilter order '+ref);
});

test('subscriptions: weekly-based recurring prices at 10% off; one frequency; one-offs ride along',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_PUBLISHABLE_KEY='pk_test_x';delete process.env.PRICE_BAG_1KG;delete process.env.PRICE_BAG_250G;
 const calls=mockStripe(()=>({body:{client_secret:'x',id:'cs_test_9'}}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:2,every:2},{name:'Batang Gadis',size:'1kg',qty:1,every:4},{name:'Batang Toru',size:'1kg',qty:1}]}));
 const f=new URLSearchParams(calls[0].opt.body);
 assert.equal(f.get('mode'),'subscription');
 assert.equal(f.get('line_items[0][price_data][unit_amount]'),'2160');assert.equal(f.get('line_items[0][price_data][recurring][interval]'),'week');assert.equal(f.get('line_items[0][price_data][recurring][interval_count]'),'2');
 assert.equal(f.get('line_items[1][price_data][recurring][interval_count]'),'2','the basket shares one frequency');
 assert.equal(f.get('line_items[2][price_data][unit_amount]'),'8000');assert.equal(f.get('line_items[2][price_data][recurring][interval]'),null,'one-off rides along');
 assert.equal(f.get('subscription_data[metadata][source]'),'website-shop');assert.equal(f.get('subscription_data[metadata][every_weeks]'),'2');
 assert.equal(f.get('shipping_options[0][shipping_rate_data][type]'),null);assert.equal(f.get('allow_promotion_codes'),null,'no code box on subscriptions');
 assert.match(f.get('custom_text[submit][message]'),/every 2 weeks.*until you cancel.*\/subscription-terms\//);
 const one=mockStripe(()=>({body:{client_secret:'x',id:'cs_test_9'}}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}]}));
 const g=new URLSearchParams(one[0].opt.body);assert.equal(g.get('mode'),'payment');assert.equal(g.get('customer_creation'),'always');
});

test('subscriptions with a client code: the better of the two, never both',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_PUBLISHABLE_KEY='pk_test_x';
 const promo=pct=>(u,o)=>u.includes('promotion_codes')?{body:{data:[{id:'promo_1',coupon:{percent_off:pct}}]}}:{body:{client_secret:'x',id:'cs_test_9'}};
 let calls=mockStripe(promo(10));
 let r=JSON.parse((await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1,every:1},{name:'Batang Toru',size:'250g',qty:1}],code:'SPRINKLR10'}))).body);
 let f=new URLSearchParams(calls[1].opt.body);
 assert.equal(f.get('line_items[0][price_data][unit_amount]'),'2160','10% sub vs 10% code: 10%');
 assert.equal(f.get('line_items[1][price_data][unit_amount]'),'2160','one-off gets the code');
 assert.equal(f.get('discounts[0][promotion_code]'),null,'not stacked by Stripe');assert.equal(r.code,'SPRINKLR10');
 calls=mockStripe(promo(15));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1,every:1}],code:'BIG15'}));
 assert.equal(new URLSearchParams(calls[1].opt.body).get('line_items[0][price_data][unit_amount]'),'2040','a bigger code wins');
 calls=mockStripe(promo(10));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],code:'SPRINKLR10'}));
 assert.equal(new URLSearchParams(calls[1].opt.body).get('discounts[0][promotion_code]'),'promo_1','one-off orders: Stripe applies the code');
});

test('order summary: subscription, running total, choices and the manage link',async()=>{
 const sum=require(path.join(F,'order-summary.js'));process.env.STRIPE_SECRET_KEY='sk_test_x';
 const session={payment_status:'paid',mode:'subscription',currency:'sgd',customer:'cus_1',amount_subtotal:2160,amount_total:2160,total_details:{amount_shipping:0},
  metadata:{source:'website-shop',contribution_rate:'0.10',order_ref:'NF-ABCDEF',choice:'protect-forests'},customer_details:{email:'a@b.c',name:'Alex Clark'},
  subscription:{id:'sub_1',status:'active',metadata:{every_weeks:'2'},items:{data:[{current_period_end:1795000000,price:{recurring:{interval:'week',interval_count:2}}}]},default_payment_method:{type:'card',card:{brand:'visa',last4:'4242'}}}};
 const calls=mockStripe((u,o)=>{
  if(u.includes('/line_items'))return {body:{data:[{description:'Gayo Lues coffee, 250 g',quantity:1,amount_total:2160,price:{recurring:{interval:'week',interval_count:2},product:{metadata:{origin:'gayo',partner:'OIC'}}}}]}};
  if(u.includes('checkout/sessions?customer='))return {body:{data:[{payment_status:'paid',amount_total:2160,total_details:{amount_shipping:0},metadata:{source:'website-shop',contribution_rate:'0.10'}},{payment_status:'paid',amount_total:8000,total_details:{amount_shipping:0},metadata:{source:'website-shop'}}]}};
  if(u.includes('invoices?'))return {body:{data:[{billing_reason:'subscription_cycle',amount_paid:2160,parent:{subscription_details:{metadata:{source:'website-shop',contribution_rate:'0.10'}}}},{billing_reason:'subscription_create',amount_paid:2160,parent:{subscription_details:{metadata:{source:'website-shop'}}}}]}};
  if(u.includes('billing_portal'))return {body:{url:'https://billing.stripe.com/p/session/x'}};
  if(u.includes('customers/')||u.includes('subscriptions/'))return {body:{}};
  return {body:session};});
 const r=JSON.parse((await sum.handler({queryStringParameters:{order:'cs_test_abcdefghijklmnop'}})).body);
 assert.deepEqual(r.subscription,{every:2,nextCharge:1795000000,status:'active',managed:true});
 assert.equal(r.order.items[0].every,2);assert.deepEqual(r.order.paidWith,{brand:'visa',last4:'4242',wallet:null});
 assert.deepEqual(r.given,{total:216+800+216,orders:3},'two paid orders plus one renewal; the first subscription invoice is the order itself');
 assert(calls.some(c=>c.url.endsWith('subscriptions/sub_1')&&new URLSearchParams(c.opt.body).get('metadata[choice]')==='protect-forests'),'choice carried to the subscription');
 const m=await sum.handler({queryStringParameters:{order:'cs_test_abcdefghijklmnop',manage:'1'},headers:{host:'nofilter.sg'}});
 assert.equal(m.statusCode,303);assert.equal(m.headers.Location,'https://billing.stripe.com/p/session/x');
 const p=await sum.handler({httpMethod:'POST',body:JSON.stringify({order:'cs_test_abcdefghijklmnop',reportBack:true,news:false})});
 assert.equal(p.statusCode,200);const pc=calls.filter(c=>c.url.endsWith('customers/cus_1')).pop();
 const pf=new URLSearchParams(pc.opt.body);assert.equal(pf.get('metadata[report_back]'),'yes');assert.equal(pf.get('metadata[news]'),'no');
});

test('report: subscription deliveries after the first are counted, by product origin and the subscription choice',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.REPORT_KEY='secret';
 mockStripe(u=>{
  if(u.startsWith('https://api.stripe.com/v1/checkout/sessions?'))return {body:{has_more:false,data:[]}};
  if(u.includes('products/prod_gayo'))return {body:{metadata:{origin:'gayo',partner:'OIC'}}};
  if(u.includes('invoices?'))return {body:{has_more:false,data:[
   {id:'in_1',billing_reason:'subscription_cycle',parent:{subscription_details:{metadata:{source:'website-shop',contribution_rate:'0.10',choice:'protect-forests'}}},lines:{data:[{amount:4320,quantity:2,pricing:{price_details:{product:'prod_gayo'}}}]}},
   {id:'in_2',billing_reason:'subscription_create',parent:{subscription_details:{metadata:{source:'website-shop'}}},lines:{data:[{amount:9999,quantity:1}]}},
   {id:'in_3',billing_reason:'subscription_cycle',parent:{subscription_details:{metadata:{source:'other'}}},lines:{data:[{amount:9999,quantity:1}]}}]}};
  return {body:{}};});
 const r=JSON.parse((await report.handler({headers:{'x-report-key':'secret'},queryStringParameters:{from:'2026-11-01',to:'2026-11-30'}})).body);
 assert.equal(r.renewals,1);assert.equal(r.contribution,432);
 assert.deepEqual(r.byPartner.map(x=>[x.origin,x.partner,x.bags,x.contribution]),[['gayo','OIC',2,432]]);
 assert.deepEqual(r.byChoice,[{choice:'protect-forests',origin:'gayo',partner:'OIC',contribution:432}]);
});
