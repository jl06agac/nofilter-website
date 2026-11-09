// node --test nf-build-tools/ship/tests/shop-functions.test.cjs  (no network: Stripe is mocked)
const test=require('node:test'),assert=require('node:assert/strict'),path=require('path');
const F=path.join(__dirname,'..','SHIP-2026-08-30f','netlify','functions');
const checkout=require(path.join(F,'checkout.js')),report=require(path.join(F,'shop-ngo-report.js'));
const ev=(body,headers={origin:'https://nofilter.sg'})=>({httpMethod:'POST',headers,body:JSON.stringify(body)});
// Stripe refuses an expand deeper than 4 levels (found live on 8 Nov, when the mocks had let one through).
function tooDeep(url){const m=String(url).match(/expand(?:%5B%5D|\[\])=([^&]+)/g)||[];return m.map(x=>decodeURIComponent(x.split('=')[1])).find(p=>p.split('.').length>4);}
function mockStripe(handler){const calls=[];global.fetch=async(url,opt={})=>{calls.push({url,opt});const deep=String(url).includes('api.stripe.com')&&tooDeep(url);
 if(deep)return {ok:false,status:400,json:async()=>({error:{message:'You cannot expand more than 4 levels of a property. Property: '+deep}})};
 const r=handler(url,opt);return {ok:r.ok!==false,status:r.status||(r.ok===false?400:200),json:async()=>r.body};};return calls;}


// A fake Stripe that also answers the catalogue calls (prices by lookup key, products, prices).
function stripeWithCatalogue(rest){let n=0;return (u,o)=>{
 if(u.includes('/v1/prices?active'))return {body:{data:[]}};
 if(u.endsWith('/v1/products'))return {body:{id:'prod_'+(++n)}};
 if(u.endsWith('/v1/prices')){const f=new URLSearchParams(o.body);return {body:{id:'price_'+f.get('lookup_key'),product:f.get('product'),unit_amount:+f.get('unit_amount'),currency:'sgd',lookup_key:f.get('lookup_key')}};}
 return rest(u,o);};}
const sessionCall=calls=>new URLSearchParams(calls.find(c=>c.url.endsWith('/v1/checkout/sessions')).opt.body);

test('no key: 503, nothing sent',async()=>{delete process.env.STRIPE_SECRET_KEY;assert.equal((await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}]}))).statusCode,503);});

test('only the four coffees in 250 g or 1 kg; quantities merged; 20 bags an order',()=>{
 const c=checkout._test.cleanLines;
 assert.equal(c([{name:'Free coffee',size:'1kg',qty:1}]),null);
 assert.equal(c([{name:'Gayo Lues',size:'5kg',qty:1}]),null);
 assert.equal(c([{name:'Gayo Lues',size:'1kg',qty:0}]),null);
 assert.deepEqual(c([{name:'Gayo Lues',size:'1 KG',qty:12},{name:'Gayo Lues',size:'1kg',qty:8}]),[{name:'Gayo Lues',size:'1kg',qty:20,every:0}]);
 assert.equal(c([{name:'Gayo Lues',size:'1kg',qty:15},{name:'Gayo Lues',size:'1kg',qty:9}]),null,'merged past 20');
 assert.equal(c([{name:'Gayo Lues',size:'1kg',qty:20},{name:'Batang Toru',size:'250g',qty:1}]),null,'20 across the whole order, not per line');
 assert.equal(c([{name:'Gayo Lues',size:'1kg',qty:1,every:5}]),null,'every 1-4 weeks only');
});

test('prices are set here, every line carries its origin and partner, delivery in Singapore',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_PUBLISHABLE_KEY='pk_test_x';delete process.env.PRICE_BAG_1KG;delete process.env.PRICE_BAG_250G;
 const calls=mockStripe(u=>({body:{client_secret:'cs_test_1_secret_x',url:'https://checkout.stripe.com/c/pay/cs_test_1_secret_x',id:'cs_test_1'}}));
 const r=await checkout.handler(ev({lines:[{name:'Batang Gadis',size:'1kg',qty:2,price:0.01},{name:'Batang Toru',size:'250g',qty:1}]}));
 assert.equal(r.statusCode,200);const out=JSON.parse(r.body);assert.equal(out.url,'https://checkout.stripe.com/c/pay/cs_test_1_secret_x');assert.equal(out.session,'cs_test_1');
 const f=new URLSearchParams(calls[0].opt.body);
 assert.equal(f.get('line_items[0][price_data][unit_amount]'),'7500','the page cannot set a price');
 assert.equal(f.get('line_items[1][price_data][unit_amount]'),'2400');
 assert.equal(f.get('line_items[0][price_data][product_data][metadata][origin]'),'gadis');
 assert.equal(f.get('line_items[0][price_data][product_data][metadata][partner]'),'SRI');
 assert.equal(f.get('line_items[1][price_data][product_data][metadata][partner]'),'PRCF Indonesia, OIC');
 assert.equal(f.get('metadata[contribution_rate]'),'0.10');assert.equal(f.get('metadata[source]'),'website-shop');
 assert.equal(f.get('shipping_address_collection[allowed_countries][0]'),'SG');
 assert.equal(f.get('allow_promotion_codes'),'true','customers can enter a code');
 assert.equal(f.get('ui_mode'),null,'hosted page');assert.equal(f.get('success_url'),'https://nofilter.sg/shop/?paid=1&order={CHECKOUT_SESSION_ID}');assert.equal(f.get('cancel_url'),'https://nofilter.sg/shop/');
 assert.equal(f.get('line_items[0][price_data][product_data][images][0]'),'https://nofilter-shared.netlify.app/bag-batang-gadis-640.webp');
 assert.equal(f.get('metadata[choice]'),'','no choice yet means where it is needed most');
});

test('a known client code is applied; an unknown one leaves the code box open',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';
 let calls=mockStripe(u=>u.includes('promotion_codes')?{body:{data:[{id:'promo_123'}]}}:{body:{client_secret:'cs_test_2_secret',url:'https://checkout.stripe.com/c/pay/cs_test_2_secret',id:'cs_test_2'}});
 let r=await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],code:'sprinklr-10'}));
 assert.match(calls[0].url,/code=SPRINKLR10/);let f=new URLSearchParams(calls[1].opt.body);
 assert.equal(f.get('discounts[0][promotion_code]'),'promo_123');assert.equal(f.get('allow_promotion_codes'),null);assert.equal(JSON.parse(r.body).code,'SPRINKLR10');
 calls=mockStripe(u=>u.includes('promotion_codes')?{body:{data:[]}}:{body:{client_secret:'cs_test_3_secret',url:'https://checkout.stripe.com/c/pay/cs_test_3_secret',id:'cs_test_3'}});
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
 let calls=mockStripe(u=>({body:{client_secret:'cs_test_9_secret',url:'https://checkout.stripe.com/c/pay/cs_test_9_secret',id:'cs_test_9'}}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],choice:'orangutans-in-danger'}));
 assert.equal(new URLSearchParams(calls[0].opt.body).get('metadata[choice]'),'orangutans-in-danger');
 calls=mockStripe(u=>({body:{client_secret:'x',url:'https://checkout.stripe.com/c/pay/x',id:'cs_test_9'}}));
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
 const calls=mockStripe(()=>({body:{client_secret:'x',url:'https://checkout.stripe.com/c/pay/x',id:'cs_test_9'}}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}]}));
 const f=new URLSearchParams(calls[0].opt.body),ref=f.get('metadata[order_ref]');
 assert.match(ref,/^NF-[2-9A-HJKMNP-Z]{6}$/);
 assert.equal(f.get('payment_intent_data[metadata][order_ref]'),ref);assert.equal(f.get('payment_intent_data[description]'),'NoFilter order '+ref);
});

test('subscriptions: the range at 5% off; one frequency; one-offs ride along; delivery under SGD 50',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_PUBLISHABLE_KEY='pk_test_x';delete process.env.PRICE_BAG_1KG;delete process.env.PRICE_BAG_250G;
 const calls=mockStripe(stripeWithCatalogue(()=>({body:{client_secret:'x',url:'https://checkout.stripe.com/c/pay/x',id:'cs_test_9'}})));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:2,every:2},{name:'Batang Gadis',size:'1kg',qty:1,every:4},{name:'Batang Toru',size:'1kg',qty:1}]}));
 const f=sessionCall(calls);
 assert.equal(f.get('mode'),'subscription');
 assert.equal(f.get('line_items[0][price]'),'price_nf-sub-gayo-250g-w2-p5','a real price from the range, so it can be swapped later');
 assert.equal(f.get('line_items[1][price]'),'price_nf-sub-gadis-1kg-w2-p5','the basket shares one frequency');
 assert.equal(f.get('line_items[3][price]'),null,'2 x 22.80 + 76 per delivery is over SGD 50: no delivery line');
 const made=calls.filter(c=>c.url.endsWith('/v1/prices')).map(c=>new URLSearchParams(c.opt.body));
 assert.equal(made.length,36,'4 coffees x 2 sizes x 4 frequencies, plus delivery x 4');assert.equal(made.find(m=>m.get('lookup_key')==='nf-sub-gayo-250g-w2-p5').get('unit_amount'),'2280');
 assert.equal(made.find(m=>m.get('lookup_key')==='nf-del-w2').get('unit_amount'),'400');
 assert.equal(calls.filter(c=>c.url.endsWith('/v1/products')).length,9);
 const small=mockStripe(stripeWithCatalogue(()=>({body:{client_secret:'x',url:'https://checkout.stripe.com/c/pay/x',id:'cs_test_9'}})));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1,every:2}]}));
 const sf=sessionCall(small);assert.equal(sf.get('line_items[1][price]'),'price_nf-del-w2','one 250 g bag a delivery pays SGD 4 delivery');assert.equal(sf.get('metadata[delivery_cents]'),'400');
 assert.equal(f.get('line_items[2][price_data][unit_amount]'),'7500');assert.equal(f.get('line_items[2][price_data][recurring][interval]'),null,'one-off rides along');
 assert.equal(f.get('subscription_data[metadata][source]'),'website-shop');assert.equal(f.get('subscription_data[metadata][every_weeks]'),'2');
 assert.equal(f.get('shipping_options[0][shipping_rate_data][type]'),null);assert.equal(f.get('allow_promotion_codes'),null,'no code box on subscriptions');
 assert.match(f.get('custom_text[submit][message]'),/every 2 weeks.*until you cancel.*\[Subscription terms\]\(https:\/\/nofilter.sg\/subscription-terms\/\)/);
 const one=mockStripe(()=>({body:{client_secret:'x',url:'https://checkout.stripe.com/c/pay/x',id:'cs_test_9'}}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}]}));
 const g=sessionCall(one);assert.equal(g.get('mode'),'payment');assert.equal(g.get('customer_creation'),'always');
 assert.equal(g.get('shipping_options[0][shipping_rate_data][fixed_amount][amount]'),'400','one-off under SGD 50: SGD 4');
 const big=mockStripe(()=>({body:{client_secret:'x',url:'https://checkout.stripe.com/c/pay/x',id:'cs_test_9'}}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'1kg',qty:1}]}));
 assert.equal(sessionCall(big).get('shipping_options[0][shipping_rate_data][fixed_amount][amount]'),'0','SGD 50 and over: free');
});

test('subscriptions with a client code: the better of the two, never both',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_PUBLISHABLE_KEY='pk_test_x';
 const promo=pct=>stripeWithCatalogue((u,o)=>u.includes('promotion_codes')?{body:{data:[{id:'promo_1',active:true,promotion:{type:'coupon',coupon:'co_1'}}]}}:u.includes('/v1/coupons/co_1')?{body:{id:'co_1',percent_off:pct,duration:'forever',valid:true}}:{body:{client_secret:'x',url:'https://checkout.stripe.com/c/pay/x',id:'cs_test_9'}});
 let calls=mockStripe(promo(10));
 let r=JSON.parse((await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1,every:1},{name:'Batang Toru',size:'250g',qty:1}],code:'SPRINKLR10'}))).body);
 let f=sessionCall(calls);
 assert.equal(f.get('line_items[0][price]'),'price_nf-sub-gayo-250g-w1-p10','5% sub vs 10% code: the 10% price set, still swappable');
 assert.equal(f.get('line_items[1][price_data][unit_amount]'),'2160','one-off gets the code');assert.equal(f.get('subscription_data[metadata][off_pct]'),'10');
 assert.equal(f.get('discounts[0][promotion_code]'),null,'not stacked by Stripe');assert.equal(r.code,'SPRINKLR10');
 calls=mockStripe(promo(15));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1,every:1}],code:'BIG15'}));
 assert.equal(sessionCall(calls).get('line_items[0][price]'),'price_nf-sub-gayo-250g-w1-p15','a bigger code wins');
 calls=mockStripe(promo(10));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],code:'SPRINKLR10'}));
 assert.equal(sessionCall(calls).get('discounts[0][promotion_code]'),'promo_1','one-off orders: Stripe applies the code');
});

test('order summary: subscription, running total, choices and the manage link',async()=>{
 const sum=require(path.join(F,'order-summary.js'));process.env.STRIPE_SECRET_KEY='sk_test_x';
 const session={payment_status:'paid',mode:'subscription',currency:'sgd',customer:'cus_1',amount_subtotal:2160,amount_total:2160,total_details:{amount_shipping:0},
  metadata:{source:'website-shop',contribution_rate:'0.10',order_ref:'NF-ABCDEF',choice:'protect-forests'},customer_details:{email:'a@b.c',name:'Alex Clark'},
  subscription:{id:'sub_1',status:'active',metadata:{every_weeks:'2'},items:{data:[{current_period_end:1795000000,price:{recurring:{interval:'week',interval_count:2}}}]},default_payment_method:{type:'card',card:{brand:'visa',last4:'4242'}}}};
 const calls=mockStripe((u,o)=>{
  if(u.includes('/line_items'))return {body:{data:[{description:'Gayo Lues coffee, 250 g',quantity:1,amount_total:2160,price:{recurring:{interval:'week',interval_count:2},product:{metadata:{origin:'gayo',partner:'OIC'}}}}]}};
  if(u.includes('checkout/sessions?customer='))return {body:{data:[{payment_status:'paid',amount_total:2160,total_details:{amount_shipping:0},metadata:{source:'website-shop',contribution_rate:'0.10'}},{payment_status:'paid',amount_total:8000,total_details:{amount_shipping:0},metadata:{source:'website-shop'}}]}};
  if(u.includes('/v1/subscriptions/sub_1'))return {body:session.subscription};
  if(u.includes('invoices?'))return {body:{data:[{billing_reason:'subscription_cycle',amount_paid:2160,parent:{subscription_details:{metadata:{source:'website-shop',contribution_rate:'0.10'}}}},{billing_reason:'subscription_create',amount_paid:2160,parent:{subscription_details:{metadata:{source:'website-shop'}}}}]}};
  if(u.includes('billing_portal/configurations'))return {body:{data:[{id:'bpc_1',metadata:{nf:'shop-v1'}}]}};
  if(u.includes('billing_portal'))return {body:{url:'https://billing.stripe.com/p/session/x'}};
  if(u.includes('customers/')||u.includes('subscriptions/'))return {body:{}};
  return {body:session};});
 const r=JSON.parse((await sum.handler({queryStringParameters:{order:'cs_test_abcdefghijklmnop'}})).body);
 assert.equal(r.subscription.every,2);assert.equal(r.subscription.nextCharge,1795000000);assert.equal(r.subscription.managed,true);assert.equal(r.subscription.skipping,null);
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

test('subscription changes: swap coffee or size, change frequency without a charge today, skip the next delivery',async()=>{
 const sum=require(path.join(F,'order-summary.js'));process.env.STRIPE_SECRET_KEY='sk_test_x';
 const item=(id,origin,name,every)=>({id,quantity:1,current_period_end:1795000000,price:{unit_amount:2160,recurring:{interval:'week',interval_count:every},product:{name,metadata:{origin}}}});
 const session={payment_status:'paid',mode:'subscription',customer:'cus_1',metadata:{source:'website-shop'},
  subscription:{id:'sub_1',status:'active',metadata:{every_weeks:'2',off_pct:'5'},items:{data:[item('si_1','gayo','Gayo Lues coffee, 250 g',2),item('si_2','toru','Batang Toru coffee, 1 kg',2)]}}};
 let calls=mockStripe(stripeWithCatalogue((u,o)=>({body:u.includes('/v1/subscriptions/')?((o&&o.method==='POST')?{}:session.subscription):session})));
 const post=b=>sum.handler({httpMethod:'POST',body:JSON.stringify({order:'cs_test_abcdefghijklmnop',...b})});
 let r=await post({action:'swap',items:[{id:'si_1',name:'Batang Gadis',size:'1 kg',qty:2},{id:'si_2',name:'Batang Toru',size:'1kg',qty:0}]});
 assert.equal(r.statusCode,200);let f=new URLSearchParams(calls.filter(c=>c.url.includes('/v1/subscriptions/sub_1')).pop().opt.body);
 assert.equal(f.get('items[0][price]'),'price_nf-sub-gadis-1kg-w2-p5');assert.equal(f.get('items[0][quantity]'),'2');assert.equal(f.get('items[1][deleted]'),'true');assert.equal(f.get('proration_behavior'),'none');
 assert.equal(f.get('items[2][price]'),null,'2 x 1 kg is over SGD 50: no delivery');
 r=await post({action:'swap',items:[{id:'si_1',name:'Gayo Lues',size:'250g',qty:1},{id:'si_2',qty:0}]});
 f=new URLSearchParams(calls.filter(c=>c.url.includes('/v1/subscriptions/sub_1')).pop().opt.body);
 assert.equal(f.get('items[2][price]'),'price_nf-del-w2','down to one 250 g bag: delivery added');
 assert.equal((await post({action:'swap',items:[{id:'si_1',qty:0},{id:'si_2',qty:0}]})).statusCode,400,'one coffee must remain');
 assert.equal((await post({action:'swap',items:[{id:'si_1',name:'Free coffee',size:'1kg',qty:1},{id:'si_2',name:'Batang Toru',size:'1kg',qty:1}]})).statusCode,400);
 assert.equal((await post({action:'swap',items:[{id:'si_1',name:'Gayo Lues',size:'250g',qty:1}]})).statusCode,409,'part of the subscription only: refused, so delivery is never judged on half a basket');
 assert.equal((await post({action:'swap',items:[{id:'si_1',name:'Gayo Lues',size:'250g',qty:1},{id:'si_1',name:'Gayo Lues',size:'250g',qty:1}]})).statusCode,409,'the same coffee twice: refused');
 r=await post({action:'every',every:4});assert.equal(r.statusCode,200);
 f=new URLSearchParams(calls.filter(c=>c.url.includes('/v1/subscriptions/sub_1')).pop().opt.body);
 assert.equal(f.get('items[0][price]'),'price_nf-sub-gayo-250g-w4-p5');assert.equal(f.get('items[1][price]'),'price_nf-sub-toru-1kg-w4-p5');
 assert.equal(f.get('trial_end'),'1795000000','no charge until the paid period ends');assert.equal(f.get('metadata[every_weeks]'),'4');
 r=await post({action:'skip'});f=new URLSearchParams(calls.filter(c=>c.url.includes('/v1/subscriptions/sub_1')).pop().opt.body);
 assert.equal(f.get('pause_collection[behavior]'),'void');assert.equal(f.get('pause_collection[resumes_at]'),String(1795000000+3600));
 r=await post({action:'unskip'});f=new URLSearchParams(calls.filter(c=>c.url.includes('/v1/subscriptions/sub_1')).pop().opt.body);
 assert.equal(f.get('pause_collection'),'');
});

test('subscriptions: only a code made to last is built into the prices; once-only or limited codes are not',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';
 const ok=checkout._test.subscriptionCodeOk, base={id:'promo_1',active:true,promotion:{type:'coupon',coupon:'co_1'}}, cp={id:'co_1',percent_off:10,duration:'forever',valid:true};
 assert.equal(ok(base,cp),true);
 assert.equal(ok(base,{...cp,applies_to:{products:[]}}),true,'applies_to present but empty');
 assert.equal(ok(base,{...cp,duration:'once'}),false,'once');
 assert.equal(ok(base,{...cp,duration:'repeating',duration_in_months:3}),false,'repeating');
 assert.equal(ok({...base,restrictions:{first_time_transaction:true}},cp),false,'first order only');
 assert.equal(ok({...base,restrictions:{minimum_amount:5000,minimum_amount_currency:'sgd'}},cp),false,'minimum spend');
 assert.equal(ok({...base,customer:'cus_9'},cp),false,'one customer');
 assert.equal(ok({...base,max_redemptions:50,times_redeemed:1},cp),false,'a redemption cap, even unused (Codex)');
 assert.equal(ok(base,{...cp,max_redemptions:50,times_redeemed:0}),false,'a cap on the coupon');
 assert.equal(ok(base,{...cp,applies_to:{products:['prod_gayo']}}),false,'limited to one product (Codex)');
 assert.equal(ok({...base,expires_at:1},cp),false,'expired');
 assert.equal(ok(base,{...cp,valid:false}),false,'coupon no longer valid');
 const promo=(p,c)=>stripeWithCatalogue((u,o)=>u.includes('promotion_codes')?{body:{data:[p]}}:u.includes('/v1/coupons/')?{body:c}:{body:{url:'https://checkout.stripe.com/c/pay/x',id:'cs_test_9'}});
 let calls=mockStripe(promo(base,{...cp,duration:'once'}));
 let r=JSON.parse((await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1,every:1}],code:'WELCOME10'}))).body);
 assert.equal(sessionCall(calls).get('line_items[0][price]'),'price_nf-sub-gayo-250g-w1-p5','a once-only code leaves the subscription at 5%');
 assert.equal(r.code,null);
 assert.ok(calls.some(c=>c.url.includes('/v1/coupons/co_1?expand[]=applies_to')),'coupon fetched with its product limits');
 assert.ok(!calls.some(c=>/promotion_codes.*expand/.test(c.url)),'no version-specific expand on the code lookup');
 calls=mockStripe(promo(base,{...cp,duration:'once'}));
 await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'250g',qty:1}],code:'WELCOME10'}));
 assert.equal(sessionCall(calls).get('discounts[0][promotion_code]'),'promo_1','a one-off order still gets it, with Stripe enforcing its rules');
});

test('checkout refuses more than 20 bags in one order',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';mockStripe(()=>({body:{}}));
 const r=await checkout.handler(ev({lines:[{name:'Gayo Lues',size:'1kg',qty:20},{name:'Batang Toru',size:'1kg',qty:20},{name:'Batang Gadis',size:'250g',qty:5,every:2}]}));
 assert.equal(r.statusCode,400);
});

test('report: renewals counted after discounts, and every line of a long invoice',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.REPORT_KEY='secret';
 const meta={parent:{subscription_details:{metadata:{source:'website-shop',contribution_rate:'0.10'}}}};
 const ln=(amt,prod,disc)=>({id:'il_'+prod+amt,amount:amt,quantity:1,discount_amounts:disc?[{amount:disc}]:[],pricing:{price_details:{product:prod}}});
 const seen=[];
 mockStripe(u=>{
  if(u.startsWith('https://api.stripe.com/v1/checkout/sessions?'))return {body:{has_more:false,data:[]}};
  if(u.includes('products/prod_gayo'))return {body:{metadata:{origin:'gayo',partner:'OIC'}}};
  if(u.includes('products/prod_toru'))return {body:{metadata:{origin:'toru',partner:'PRCF Indonesia, OIC'}}};
  if(u.includes('/invoices/in_long/lines')){seen.push(u);return u.includes('starting_after')?{body:{has_more:false,data:[ln(7000,'prod_toru')]}}:{body:{has_more:true,data:[ln(2000,'prod_gayo')]}};}
  if(u.includes('invoices?'))return {body:{has_more:false,data:[
   {id:'in_disc',billing_reason:'subscription_cycle',...meta,lines:{has_more:false,data:[ln(8000,'prod_gayo',2000)]}},
   {id:'in_long',billing_reason:'subscription_cycle',...meta,lines:{has_more:true,data:[ln(2000,'prod_gayo')]}}]}};
  return {body:{}};});
 const r=JSON.parse((await report.handler({headers:{'x-report-key':'secret'},queryStringParameters:{from:'2026-11-01',to:'2026-11-30'}})).body);
 const by=Object.fromEntries(r.byPartner.map(x=>[x.origin,x.contribution]));
 assert.equal(by.gayo,600+200,'8000 less a 2000 discount = 6000, 10% = 600; plus 200 from the long invoice');
 assert.equal(by.toru,700,'the line past the first page is counted');
 assert.equal(seen.length,2,'invoice lines paged through');
});

test('quote enquiry: a failed internal copy is retried once and logged, never silent',async()=>{
 const q=require(path.join(F,'quote-confirm.js'));process.env.RESEND_API_KEY='re_x';process.env.QUOTE_FROM='NoFilter <hello@nofilter.sg>';process.env.QUOTE_TO='hello@nofilter.sg';
 const errs=[],orig=console.error;console.error=(...a)=>errs.push(a.join(' '));
 try{
  let calls=mockStripe((u,o)=>{const b=JSON.parse(o.body);return b.to[0]==='hello@nofilter.sg'?{ok:false,body:{}}:{body:{id:'em_1'}};});
  calls.forEach(()=>{});
  global.fetch=(f=>async(u,o)=>{const r=await f(u,o);r.status=r.ok?200:500;r.text=async()=>'down';return r;})(global.fetch);
  const ev2={httpMethod:'POST',body:JSON.stringify({email:'pat@example.com',name:'Pat',company:'Acme',ref:'Q-123',market:'SGD'})};
  let r=await q.handler(ev2);
  assert.equal(r.statusCode,200,'the customer still gets their copy');assert.equal(r.body,'sent; desk copy failed');
  assert.equal(calls.filter(c=>JSON.parse(c.opt.body).to[0]==='hello@nofilter.sg').length,2,'one retry');
  assert.ok(errs.some(e=>/DESK COPY NOT SENT/.test(e)&&/Q-123/.test(e)),'logged with the enquiry reference');
  calls=mockStripe(()=>({body:{id:'em_2'}}));
  r=await q.handler(ev2);assert.equal(r.body,'sent');assert.equal(calls.length,2,'customer and desk, no retry');
 }finally{console.error=orig;}
});

test('trade access: the rate-limited wrappers pass requests through unchanged',async()=>{
 process.env.ACCESS_SECRET='s3cret';process.env.RESEND_API_KEY='re_x';process.env.QUOTE_FROM='NoFilter <hello@nofilter.sg>';
 const v=await import(path.join(F,'access-verify.mjs')),q=await import(path.join(F,'access-request.mjs'));
 assert.equal(v.config.path,'/api/access-verify');assert.equal(q.config.path,'/api/access-request');
 assert.ok(v.config.rateLimit.windowLimit<=10&&q.config.rateLimit.windowLimit<=5);
 const post=(m,b)=>m.default(new Request('https://nofilter.sg'+m.config.path,{method:'POST',body:JSON.stringify(b)}));
 assert.equal((await v.default(new Request('https://nofilter.sg/api/access-verify'))).status,405,'GET refused as before');
 const no=await post(v,{email:'pat@acme.com',code:'TAPIRBASIN000'});assert.equal(no.status,401);assert.deepEqual(await no.json(),{ok:false});
 assert.equal((await post(q,{email:'pat@gmail.com',company:'Acme'})).status,403,'personal inbox refused as before');
 const sent=[];global.fetch=async(u,o)=>{sent.push(JSON.parse(o.body));return {ok:true,status:200,json:async()=>({id:'em'}),text:async()=>''};};
 const ok=await post(q,{email:'pat@acme.com',company:'Acme',name:'Pat Lee'});assert.equal(ok.status,200);
 const mine=sent.find(m=>m.to&&m.to[0]==='pat@acme.com')||{};const code=(mine.html||'').match(/\b[A-Z]{4,}[A-Z]{4,}\d{3}\b/);assert.ok(code,'a code went out');
 const yes=await post(v,{email:'pat@acme.com',code:code[0]});assert.equal(yes.status,200,'the emailed code opens the rates');
});

test('order emails: signed Stripe events only; the customer gets the receipt with a manage link, NoFilter gets the order',async()=>{
 const wh=require(path.join(F,'shop-webhook.js')),crypto=require('crypto');
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_WEBHOOK_SECRET='whsec_test';process.env.RESEND_API_KEY='re_x';process.env.QUOTE_FROM='NoFilter <hello@nofilter.sg>';process.env.QUOTE_TO='hello@nofilter.sg';
 const sess={id:'cs_test_abcdefghijklmnop',object:'checkout.session',payment_status:'paid',mode:'subscription',currency:'sgd',customer:'cus_1',subscription:'sub_1',success_url:'https://nofilter.sg/shop/?paid=1&order={CHECKOUT_SESSION_ID}',
  amount_subtotal:2160,amount_total:2560,total_details:{amount_shipping:0},metadata:{source:'website-shop',contribution_rate:'0.10',order_ref:'NF-SRSP2T',delivery_cents:'400'},
  customer_details:{email:'pat@example.com',name:'Pat Lee',address:{line1:'1 Raffles Place',postal_code:'048616',country:'SG'}},shipping_details:{name:'Pat Lee',address:{line1:'1 Raffles Place',postal_code:'048616',country:'SG'}}};
 const sub={id:'sub_1',status:'active',metadata:{every_weeks:'1',off_pct:'10'},items:{data:[
  {id:'si_1',quantity:1,current_period_end:1795000000,price:{unit_amount:2160,recurring:{interval:'week',interval_count:1},product:{name:'Arakan Mountains coffee, 250 g',metadata:{origin:'arakan',partner:'Fauna & Flora Myanmar, ACCA'}}}},
  {id:'si_d',quantity:1,current_period_end:1795000000,price:{unit_amount:400,recurring:{interval:'week',interval_count:1},product:{name:'Delivery',metadata:{kind:'delivery'}}}}]}};
 const mails=[];
 mockStripe((u,o)=>{
  if(u.startsWith('https://api.resend.com')){mails.push({body:JSON.parse(o.body),key:o.headers['Idempotency-Key']});return {body:{id:'em'}};}
  if(u.includes('/line_items'))return {body:{data:[{description:'Arakan Mountains coffee, 250 g',quantity:1,amount_total:2160,price:{recurring:{interval:'week',interval_count:1},product:{metadata:{origin:'arakan',partner:'Fauna & Flora Myanmar, ACCA'}}}},{description:'Delivery',quantity:1,amount_total:400,price:{recurring:{interval:'week',interval_count:1},product:{name:'Delivery',metadata:{kind:'delivery'}}}}]}};
  if(u.includes('/v1/subscriptions/sub_1'))return {body:sub};
  if(u.includes('checkout/sessions?customer='))return {body:{data:[]}};
  if(u.includes('invoices?'))return {body:{data:[]}};
  if(u.includes('/v1/checkout/sessions/'))return {body:sess};
  return {body:{}};});
 const raw=JSON.stringify({type:'checkout.session.completed',data:{object:sess}});
 const sign=(body,t=Math.floor(Date.now()/1000),sec='whsec_test')=>'t='+t+',v1='+crypto.createHmac('sha256',sec).update(t+'.'+body).digest('hex');
 const call=(body,sig)=>wh.handler({httpMethod:'POST',headers:{'stripe-signature':sig},body});
 assert.equal((await call(raw,sign(raw,undefined,'whsec_wrong'))).statusCode,400,'wrong secret');
 assert.equal((await call(raw,sign(raw,Math.floor(Date.now()/1000)-900))).statusCode,400,'stale');
 assert.equal((await call(raw.replace('NF-SRSP2T','NF-HACKED'),sign(raw))).statusCode,400,'body altered after signing');
 assert.equal(mails.length,0,'nothing sent on a bad signature');
 const other=JSON.stringify({type:'checkout.session.completed',data:{object:{...sess,metadata:{source:'other'}}}});
 assert.equal((await call(other,sign(other))).body,'ignored');
 const r=await call(raw,sign(raw));assert.equal(r.statusCode,200);assert.equal(mails.length,2);
 const cust=mails.find(m=>m.body.to[0]==='pat@example.com'),desk=mails.find(m=>m.body.to[0]==='hello@nofilter.sg');
 assert.ok(cust&&desk);assert.equal(cust.key,'shop-customer-cs_test_abcdefghijklmnop','a retried webhook cannot send twice');
 assert.match(cust.body.subject,/NF-SRSP2T/);assert.match(cust.body.html,/Thanks, Pat\./);
 assert.match(cust.body.html,/https:\/\/nofilter\.sg\/shop\/\?paid=1&order=cs_test_abcdefghijklmnop&manage=page/,'manage link opens the subscription controls');
 assert.match(cust.body.html,/SGD 2\.16 to conservation/,'10% of the coffee, not the delivery');
 assert.match(cust.body.html,/SGD 25\.60 every week/);
 assert.doesNotMatch(cust.body.html,/8123|phone/i);
 assert.match(desk.body.text,/1 x Arakan Mountains, 250 g/);assert.match(desk.body.text,/1 Raffles Place/);
});

test('code check for the basket: percentage and whether it applies to subscriptions, nothing else',async()=>{
 process.env.STRIPE_SECRET_KEY='sk_test_x';
 const promo={id:'promo_1',active:true,promotion:{type:'coupon',coupon:'co_1'}};
 const run=async(c,code='TEST10')=>{mockStripe(u=>u.includes('promotion_codes')?{body:{data:c?[promo]:[]}}:u.includes('/v1/coupons/')?{body:c}:{body:{}});
  const r=await checkout.handler({httpMethod:'GET',queryStringParameters:{code}});return {s:r.statusCode,b:JSON.parse(r.body)};};
 let r=await run({id:'co_1',percent_off:10,duration:'forever',valid:true});assert.equal(r.s,200);assert.deepEqual(r.b,{code:'TEST10',pct:0.1,subscriptions:true,oneOff:true});
 r=await run({id:'co_1',percent_off:10,duration:'once',valid:true});assert.deepEqual(r.b,{code:'TEST10',pct:0.1,subscriptions:false,oneOff:true},'once-only: fine on a one-off order');
 promo.restrictions={first_time_transaction:true};r=await run({id:'co_1',percent_off:10,duration:'forever',valid:true});assert.deepEqual(r.b,{code:'TEST10',pct:0.1,subscriptions:false,oneOff:false},'first order only: left to Stripe');delete promo.restrictions;
 r=await run(null);assert.equal(r.s,404);
 r=await run({id:'co_1',amount_off:500,valid:true});assert.equal(r.s,404,'a fixed-amount code is left to Stripe');
 r=await run(null,'');assert.equal(r.s,400);
});

test('the server charges the prices the shop page shows (BAG equals MARKETS.SG in the master)',()=>{
 const html=require('fs').readFileSync(path.join(__dirname,'..','..','..','NoFilter-Website-Master.html'),'utf8');
 const m=html.match(/bag250:\s*([\d.]+),\s*bag1kg:\s*([\d.]+)/);assert.ok(m,'MARKETS.SG bag prices found');
 assert.deepEqual(checkout._test.BAG,{'250g':Math.round(+m[1]*100),'1kg':Math.round(+m[2]*100)});
 process.env.PRICE_BAG_1KG='8000';assert.equal(checkout._test.BAG['1kg'],7500,'a Netlify setting no longer overrides it');delete process.env.PRICE_BAG_1KG;
});

test('order emails: delayed payments, a retry never sends twice, and Stripe sees only an error category',async()=>{
 const wh=require(path.join(F,'shop-webhook.js')),crypto=require('crypto');
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_WEBHOOK_SECRET='whsec_test';process.env.RESEND_API_KEY='re_x';process.env.QUOTE_FROM='NoFilter <hello@nofilter.sg>';process.env.QUOTE_TO='hello@nofilter.sg';
 const sess={id:'cs_test_zzzzzzzzzzzzzzzz',payment_status:'paid',mode:'payment',currency:'sgd',customer:'cus_1',payment_intent:'pi_1',created:1794151811,success_url:'https://nofilter.sg/shop/?paid=1',
  amount_subtotal:7500,amount_total:7500,total_details:{amount_shipping:0},metadata:{source:'website-shop',contribution_rate:'0.10',order_ref:'NF-AAAAAA'},customer_details:{email:'pat@example.com',name:'pat lee'}};
 let meta={},mails=[],failDesk=0;
 mockStripe((u,o)=>{
  if(u.startsWith('https://api.resend.com')){const b=JSON.parse(o.body);mails.push(b);if(b.to[0]==='hello@nofilter.sg'&&failDesk){failDesk--;return {ok:false,status:422,body:{message:'Invalid `to` field: pat@example.com is not allowed'}};}return {body:{id:'em'}};}
  if(u.includes('/v1/payment_intents/pi_1')){if(o&&o.method==='POST'){for(const [k,v] of new URLSearchParams(o.body))meta[k.slice(9,-1)]=v;}return {body:{id:'pi_1',metadata:meta,latest_charge:null}};}
  if(u.includes('/line_items'))return {body:{data:[{description:'Gayo Lues coffee, 1 kg',quantity:1,amount_total:7500,price:{product:{metadata:{origin:'gayo',partner:'OIC'}}}}]}};
  if(u.includes('checkout/sessions?customer='))return {body:{data:[]}};
  if(u.includes('invoices?'))return {body:{data:[]}};
  if(u.includes('/v1/checkout/sessions/'))return {body:sess};
  return {body:{}};});
 const sign=(b)=>{const t=Math.floor(Date.now()/1000);return 't='+t+',v1='+crypto.createHmac('sha256','whsec_test').update(t+'.'+b).digest('hex');};
 const fire=async(type,obj=sess)=>{const b=JSON.stringify({type,data:{object:obj}});return wh.handler({httpMethod:'POST',headers:{'stripe-signature':sign(b)},body:b});};
 assert.equal((await fire('checkout.session.completed',{...sess,payment_status:'unpaid'})).body,'waiting for payment');assert.equal(mails.length,0);
 // the desk copy fails once: the customer email is recorded, Stripe's log shows a category only
 failDesk=1;let r=await fire('checkout.session.async_payment_succeeded');
 assert.equal(r.statusCode,500);assert.equal(r.body,'email failed: desk 422 rejected');assert.doesNotMatch(r.body,/pat@/);
 assert.equal(meta.nf_mail_customer,'sent');assert.equal(meta.nf_mail_desk,undefined);
 // Stripe retries: only the desk copy goes, the customer isn't emailed again
 const before=mails.filter(m=>m.to[0]==='pat@example.com').length;
 r=await fire('checkout.session.async_payment_succeeded');assert.equal(r.body,'sent');
 assert.equal(mails.filter(m=>m.to[0]==='pat@example.com').length,before,'no second receipt');assert.equal(meta.nf_mail_desk,'sent');
 // days later, past Resend's 24 hours: nothing sent at all
 const n=mails.length;assert.equal((await fire('checkout.session.completed')).body,'already sent');assert.equal(mails.length,n);
 assert.equal(wh._test.category(401,'x'),'key');assert.equal(wh._test.category(403,'The domain is not verified'),'key');assert.equal(wh._test.category(422,'from address domain'),'sender');
});

test('order emails: a 409 is not a send, and an unrecorded send is not acknowledged',async()=>{
 const wh=require(path.join(F,'shop-webhook.js')),crypto=require('crypto');
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_WEBHOOK_SECRET='whsec_test';process.env.RESEND_API_KEY='re_x';process.env.QUOTE_FROM='NoFilter <hello@nofilter.sg>';process.env.QUOTE_TO='hello@nofilter.sg';
 const sess={id:'cs_test_yyyyyyyyyyyyyyyy',payment_status:'paid',mode:'payment',currency:'sgd',customer:'cus_1',payment_intent:'pi_2',created:1794151811,success_url:'https://nofilter.sg/shop/?paid=1',
  amount_subtotal:7500,amount_total:7500,total_details:{amount_shipping:0},metadata:{source:'website-shop',contribution_rate:'0.10',order_ref:'NF-BBBBBB'},customer_details:{email:'pat@example.com',name:'Pat'}};
 let meta={},resendStatus=200,metaFail=false,mails=0;
 mockStripe((u,o)=>{
  if(u.startsWith('https://api.resend.com')){mails++;return resendStatus===200?{body:{id:'em'}}:{ok:false,status:resendStatus,body:{name:'concurrent_idempotent_requests'}};}
  if(u.includes('/v1/payment_intents/pi_2')){if(o&&o.method==='POST'){if(metaFail)return {ok:false,status:500,body:{}};for(const [k,v] of new URLSearchParams(o.body))meta[k.slice(9,-1)]=v;}return {body:{id:'pi_2',metadata:meta}};}
  if(u.includes('/line_items'))return {body:{data:[{description:'Gayo Lues coffee, 1 kg',quantity:1,amount_total:7500,price:{product:{metadata:{origin:'gayo',partner:'OIC'}}}}]}};
  if(u.includes('checkout/sessions?customer='))return {body:{data:[]}};
  if(u.includes('invoices?'))return {body:{data:[]}};
  if(u.includes('/v1/checkout/sessions/'))return {body:sess};
  return {body:{}};});
 const sign=b=>{const t=Math.floor(Date.now()/1000);return 't='+t+',v1='+crypto.createHmac('sha256','whsec_test').update(t+'.'+b).digest('hex');};
 const fire=async(obj=sess)=>{const b=JSON.stringify({type:'checkout.session.completed',data:{object:obj}});return wh.handler({httpMethod:'POST',headers:{'stripe-signature':sign(b)},body:b});};
 resendStatus=409;let r=await fire();
 assert.equal(r.statusCode,500,'a 409 is retried');assert.deepEqual(meta,{},'and not recorded as sent');
 resendStatus=200;metaFail=true;r=await fire();
 assert.equal(r.statusCode,500,'sent but not recorded: not acknowledged');assert.match(r.body,/not recorded/);assert.deepEqual(meta,{});
 metaFail=false;r=await fire();assert.equal(r.body,'sent');assert.equal(meta.nf_mail_customer,'sent');assert.equal(meta.nf_mail_desk,'sent');
 const n=mails;r=await fire({...sess,id:'cs_test_xxxxxxxxxxxxxxxx',payment_intent:null});
 assert.equal(r.statusCode,500,'nothing to record on: nothing sent');assert.equal(mails,n);
});

test('order emails: a retry after the customer changes the subscription carries the same email',async()=>{
 const wh=require(path.join(F,'shop-webhook.js')),crypto=require('crypto');
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_WEBHOOK_SECRET='whsec_test';process.env.RESEND_API_KEY='re_x';process.env.QUOTE_FROM='NoFilter <hello@nofilter.sg>';process.env.QUOTE_TO='hello@nofilter.sg';
 const sess={id:'cs_test_wwwwwwwwwwwwwwww',payment_status:'paid',mode:'subscription',currency:'sgd',customer:'cus_1',subscription:'sub_9',created:1794151811,success_url:'https://nofilter.sg/shop/?paid=1',
  amount_subtotal:2160,amount_total:2560,total_details:{amount_shipping:0},metadata:{source:'website-shop',contribution_rate:'0.10',order_ref:'NF-CCCCCC',delivery_cents:'400'},customer_details:{email:'pat@example.com',name:'Pat'}};
 const item=(id,name,origin,amt,every)=>({id,quantity:1,current_period_end:1795000000,price:{unit_amount:amt,recurring:{interval:'week',interval_count:every},product:{name,metadata:{origin,partner:'OIC'}}}});
 let sub={id:'sub_9',status:'active',metadata:{every_weeks:'1',off_pct:'10'},default_payment_method:{type:'card',card:{brand:'visa',last4:'4242'}},items:{data:[item('si_1','Gayo Lues coffee, 250 g','gayo',2160,1),{...item('si_d','Delivery','delivery',400,1),price:{unit_amount:400,recurring:{interval:'week',interval_count:1},product:{name:'Delivery',metadata:{kind:'delivery'}}}}]}};
 let metaFail=true;const cust=[];
 mockStripe((u,o)=>{
  if(u.startsWith('https://api.resend.com')){const b=JSON.parse(o.body);if(b.to[0]==='pat@example.com')cust.push({key:o.headers['Idempotency-Key'],body:o.body});return {body:{id:'em'}};}
  if(u.includes('/v1/subscriptions/sub_9')){if(o&&o.method==='POST'){if(metaFail)return {ok:false,status:500,body:{}};for(const [k,v] of new URLSearchParams(o.body))sub.metadata[k.slice(9,-1)]=v;}return {body:sub};}
  if(u.includes('/line_items'))return {body:{data:[{description:'Gayo Lues coffee, 250 g',quantity:1,amount_total:2160,price:{recurring:{interval:'week',interval_count:1},product:{metadata:{origin:'gayo',partner:'OIC'}}}},{description:'Delivery',quantity:1,amount_total:400,price:{recurring:{interval:'week',interval_count:1},product:{name:'Delivery',metadata:{kind:'delivery'}}}}]}};
  if(u.includes('checkout/sessions?customer='))return {body:{data:[]}};
  if(u.includes('invoices?'))return {body:{data:[]}};
  if(u.includes('/v1/checkout/sessions/'))return {body:sess};
  return {body:{}};});
 const sign=b=>{const t=Math.floor(Date.now()/1000);return 't='+t+',v1='+crypto.createHmac('sha256','whsec_test').update(t+'.'+b).digest('hex');};
 const fire=async()=>{const b=JSON.stringify({type:'checkout.session.completed',data:{object:sess}});return wh.handler({httpMethod:'POST',headers:{'stripe-signature':sign(b)},body:b});};
 assert.equal((await fire()).statusCode,500,'sent, marker not saved');
 // the customer swaps to 1 kg every 4 weeks, and changes card, before Stripe retries
 sub.items.data=[item('si_1','Batang Toru coffee, 1 kg','toru',6750,4)];sub.default_payment_method={type:'card',card:{brand:'mastercard',last4:'1111'}};sub.items.data[0].current_period_end=1797000000;
 metaFail=false;assert.equal((await fire()).body,'sent');
 assert.equal(cust.length,2);assert.equal(cust[0].key,cust[1].key);assert.equal(cust[0].body,cust[1].body,'identical content under the same key');
 assert.match(cust[0].body,/SGD 25\.60 every week/);assert.doesNotMatch(cust[0].body,/1111|4242/,'no card line on a subscription email');
 assert.equal(sub.metadata.nf_mail_customer,'sent');
});

test('order emails: past 23 hours the customer gets nothing more and NoFilter gets an Action needed alert',async()=>{
 const wh=require(path.join(F,'shop-webhook.js')),crypto=require('crypto');
 process.env.STRIPE_SECRET_KEY='sk_test_x';process.env.STRIPE_WEBHOOK_SECRET='whsec_test';process.env.RESEND_API_KEY='re_x';process.env.QUOTE_FROM='NoFilter <hello@nofilter.sg>';process.env.QUOTE_TO='hello@nofilter.sg';
 const sess={id:'cs_test_vvvvvvvvvvvvvvvv',payment_status:'paid',mode:'payment',payment_intent:'pi_3',created:1794151811,success_url:'https://nofilter.sg/shop/?paid=1',
  amount_subtotal:7500,amount_total:7500,total_details:{amount_shipping:0},metadata:{source:'website-shop',contribution_rate:'0.10',order_ref:'NF-DDDDDD'},customer_details:{email:'pat@example.com',name:'Pat'}};
 let meta={nf_mail_desk:'sent'},mails=[],down=true;
 mockStripe((u,o)=>{
  if(u.startsWith('https://api.resend.com')){const b=JSON.parse(o.body);mails.push({b,key:o.headers['Idempotency-Key']});return down?{ok:false,status:503,body:{}}:{body:{id:'em'}};}
  if(u.includes('/v1/payment_intents/pi_3')){if(o&&o.method==='POST'){for(const [k,v] of new URLSearchParams(o.body))meta[k.slice(9,-1)]=v;}return {body:{id:'pi_3',metadata:meta}};}
  if(u.includes('/line_items'))return {body:{data:[{description:'Gayo Lues coffee, 1 kg',quantity:1,amount_total:7500,price:{product:{metadata:{origin:'gayo',partner:'OIC'}}}}]}};
  if(u.includes('checkout/sessions?customer='))return {body:{data:[]}};
  if(u.includes('invoices?'))return {body:{data:[]}};
  if(u.includes('/v1/checkout/sessions/'))return {body:sess};
  return {body:{}};});
 const orig=console.error;console.error=()=>{};
 const fire=async()=>{const b=JSON.stringify({type:'checkout.session.completed',created:Math.floor(Date.now()/1000)-24*3600,data:{object:sess}});const t=Math.floor(Date.now()/1000);
  return wh.handler({httpMethod:'POST',headers:{'stripe-signature':'t='+t+',v1='+crypto.createHmac('sha256','whsec_test').update(t+'.'+b).digest('hex')},body:b});};
 try{
  let r=await fire();assert.equal(r.statusCode,500,'alert could not be sent: Stripe keeps retrying');assert.match(r.body,/escalation failed: 503/);
  down=false;r=await fire();assert.equal(r.body,'escalated');
  assert.ok(mails.every(m=>m.b.to[0]==='hello@nofilter.sg'),'the customer is never emailed past the window');
  const last=mails[mails.length-1];assert.match(last.b.subject,/^Action needed: Shop order NF-DDDDDD/);assert.match(last.b.text,/receipt could not be confirmed as sent/);assert.match(last.b.text,/Check Resend .* before sending anything/);assert.equal(last.key,'shop-late-cs_test_vvvvvvvvvvvvvvvv');
  assert.equal(meta.nf_mail_late,'sent');const n=mails.length;assert.equal((await fire()).body,'already escalated');assert.equal(mails.length,n);
 }finally{console.error=orig;}
});
