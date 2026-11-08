/* NoFilter checkout: turns the cart into a Stripe Checkout Session on Stripe's hosted page (156; it was
   embedded in our panel before). The panel takes the customer's project choice first and sends it here;
   this returns the hosted page's URL, and Stripe returns the customer to /shop/?paid=1&order=….
   PRICES AND PRODUCTS LIVE HERE, not in the page: the page sends only names, sizes and
   quantities, and anything not on the list below is refused.
   Netlify -> Site settings -> Environment:
     STRIPE_SECRET_KEY        sk_test_... to rehearse, sk_live_... to go live (without it: 503)
     (STRIPE_PUBLISHABLE_KEY is no longer needed: the hosted page needs no key on our side)
     (bag prices are BAG below, not Netlify settings: 168, after a leftover PRICE_BAG_1KG=8000 in Netlify
      charged SGD 80 while the page showed 75. A test keeps BAG equal to MARKETS.SG in the master.)
     DELIVERY_CENTS      delivery charge per order in cents (default 0: retail prices include delivery)
   Payment methods (cards, Apple Pay, Google Pay, PayNow) are switched on in the Stripe
   dashboard; this function does not name them, so the dashboard decides.
   A client code (e.g. SPRINKLR10, from the impact counter's shop QR) arrives as `code`;
   if it matches an active Stripe promotion code it is applied, otherwise the customer can
   still enter one at checkout. No npm dependencies: Stripe's REST API via fetch (Node 18+). */
// Each coffee's landscape and partner, as the site names them (ORIGINS in the master). Every
// order line carries these, so what each partner is owed can be totalled from Stripe
// (see shop-ngo-report.js). Retail bags carry a flat 10% of what the customer paid.
const ORIGINS = {
  'Batang Toru': { origin: 'toru', partner: 'PRCF Indonesia, OIC' },
  'Batang Gadis': { origin: 'gadis', partner: 'SRI' },
  'Gayo Lues': { origin: 'gayo', partner: 'OIC' },
  'Arakan Mountains': { origin: 'arakan', partner: 'Fauna & Flora Myanmar, ACCA' }
};
const COFFEES = Object.keys(ORIGINS);
const CONTRIBUTION_RATE = '0.10';
const BAGS = { 'Batang Toru': 'bag-batang-toru-640.webp', 'Batang Gadis': 'bag-batang-gadis-640.webp', 'Gayo Lues': 'bag-gayo-lues-640.webp', 'Arakan Mountains': 'bag-arakan-640.webp' };
const CDN = 'https://nofilter-shared.netlify.app/';
// The three things a customer can point their 10% at, as on the impact counter. No choice means
// where the partner needs it most. Recorded on the order (metadata.choice) and totalled in the report.
const CHOICES = { 'protect-forests': 'Protect wild forests', 'orangutans-in-danger': 'Help orangutans in danger', 'coffee-with-forest': 'Grow coffee with the forest' };
// A short order number the customer can quote (NF-7K2Q9M): on the order, its payment, and the confirmation page.
const crypto = require('crypto');
const { ensureCatalogue, lookupKey, deliveryKey } = require('./_lib/catalogue.js');
const orderRef = () => 'NF-' + Array.from(crypto.randomBytes(6), b => '23456789ABCDEFGHJKMNPQRSTUVWXYZ'[b % 31]).join('');
const reply = (statusCode, body) => ({ statusCode, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }, body: JSON.stringify(body) });

async function stripe(path, key, form, method = 'POST') {
  const res = await fetch('https://api.stripe.com/v1/' + path, {
    method,
    headers: { Authorization: 'Bearer ' + key, ...(form ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}) },
    body: form ? form.toString() : undefined
  });
  return { ok: res.ok, data: await res.json() };
}

// Subscriptions: a line with `every` 1-4 is delivered every that many weeks at SUB_OFF off. Stripe allows
// one frequency per subscription, so the basket's subscription lines share one (the page enforces it;
// here the first one wins). One-off lines in the same basket are charged once, on the first payment.
const SUB_OFF = 0.05;
// Retail bag prices in cents: the one place the server takes them from. Must equal MARKETS.SG.bag250 / bag1kg
// in NoFilter-Website-Master.html (a unit test checks).
const BAG = { '250g': 2400, '1kg': 7500 };
// Delivery: DELIVERY_CENTS (default SGD 4) on orders under FREE_FROM_CENTS (default SGD 50); free from there.
// For a subscription the test is each delivery's coffee; it is never part of the conservation share.
// One line per coffee, size and plan; quantities merged. At most MAX_BAGS bags in the whole order.
const MAX_BAGS = 20;
function cleanLines(lines) {
  if (!Array.isArray(lines) || !lines.length || lines.length > 20) return null;
  const merged = new Map();
  for (const l of lines) {
    const name = COFFEES.find(c => c === String(l && l.name || '').trim());
    const size = String(l && l.size || '').toLowerCase().replace(/\s+/g, '');
    const qty = parseInt(l && l.qty, 10);
    const every = parseInt(l && l.every, 10) || 0;
    if (!name || !['250g', '1kg'].includes(size) || !Number.isInteger(qty) || qty < 1 || every < 0 || every > 4) return null;
    const k = name + '|' + size + '|' + every;
    merged.set(k, (merged.get(k) || 0) + qty);
  }
  let total = 0; for (const q of merged.values()) total += q;
  if (total > MAX_BAGS) return null;
  const out = [...merged].map(([k, qty]) => { const [name, size, every] = k.split('|'); return { name, size, qty, every: +every }; });
  const first = (out.find(l => l.every) || {}).every || 0;
  return out.map(l => (l.every ? { ...l, every: first } : l));
}

// A code is built into a subscription's prices, so it lasts for every delivery. Only a code made for that
// is honoured there: a percentage, duration 'forever', valid, not tied to one customer, no first-order or
// minimum-spend rule, not expired, not limited to certain products, and no redemption cap at all (a use built
// into prices is never counted by Stripe, so a cap could not hold). Anything else is left out of a
// subscription order; in a one-off order Stripe applies the code and enforces its own rules.
// c is the coupon, fetched with applies_to expanded.
function subscriptionCodeOk(promo, c) {
  c = c || {};
  const r = promo.restrictions || {};
  const now = Math.floor(Date.now() / 1000);
  if (!promo.active || c.valid === false || !c.percent_off || c.duration !== 'forever') return false;
  if (promo.customer || r.first_time_transaction || r.minimum_amount) return false;
  if (promo.expires_at && promo.expires_at <= now) return false;
  if (c.redeem_by && c.redeem_by <= now) return false;
  if (promo.max_redemptions || c.max_redemptions) return false;
  if (c.applies_to && Array.isArray(c.applies_to.products) && c.applies_to.products.length) return false;
  return true;
}

// A client code: its promotion id, percentage, and whether it may be built into subscription prices.
// No expand on the list: Stripe's current API holds the coupon as an ID under promotion.coupon (older
// versions put it at coupon), and an expand path the account's version doesn't have fails the whole call.
async function lookupCode(code, KEY) {
  const found = await stripe('promotion_codes?active=true&limit=1&code=' + encodeURIComponent(code), KEY, null, 'GET');
  const promo = found.ok && found.data && Array.isArray(found.data.data) ? found.data.data[0] : null;
  if (!promo || !promo.id) return null;
  const ref = promo.coupon || (promo.promotion && promo.promotion.coupon);
  const cid = typeof ref === 'string' ? ref : ref && ref.id;
  const cr = cid ? await stripe('coupons/' + encodeURIComponent(cid) + '?expand[]=applies_to', KEY, null, 'GET') : null;
  const coupon = cr && cr.ok ? cr.data : null;
  // oneOffOk: the basket may show the discount on one-off bags only when Stripe can't refuse or narrow it for
  // this basket (no customer, first-order, minimum-spend or product rule, not expired or used up); otherwise
  // the page leaves the price to Stripe's payment page (171, Codex)
  const r = promo.restrictions || {}, now = Math.floor(Date.now() / 1000);
  const oneOffOk = !!(coupon && coupon.percent_off && coupon.valid !== false && !promo.customer && !r.first_time_transaction && !r.minimum_amount
    && !(coupon.applies_to && Array.isArray(coupon.applies_to.products) && coupon.applies_to.products.length)
    && !(promo.expires_at && promo.expires_at <= now) && !(promo.max_redemptions && promo.times_redeemed >= promo.max_redemptions)
    && !(coupon.max_redemptions && coupon.times_redeemed >= coupon.max_redemptions));
  return { promoId: promo.id, pct: coupon && coupon.percent_off ? coupon.percent_off / 100 : 0, subOk: !!(coupon && subscriptionCodeOk(promo, coupon)), oneOffOk };
}

exports.handler = async function (event) {
  const KEY = process.env.STRIPE_SECRET_KEY;
  // 166: the basket asks what a client code is worth, so it can show the price that will be charged.
  // Answers only the percentage and whether it applies to subscriptions; nothing about the customer.
  if (event.httpMethod === 'GET') {
    if (!KEY) return reply(503, { error: 'payments not configured' });
    const code = String((event.queryStringParameters || {}).code || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 24);
    if (!code) return reply(400, { error: 'no code' });
    const c = await lookupCode(code, KEY);
    return reply(c && c.pct ? 200 : 404, c && c.pct ? { code, pct: c.pct, subscriptions: c.subOk, oneOff: c.oneOffOk } : { error: 'unknown code' });
  }
  if (event.httpMethod !== 'POST') return reply(405, { error: 'POST only' });
  if (!KEY) return reply(503, { error: 'payments not configured' });
  let body;
  try { body = JSON.parse(event.body || '{}'); } catch (e) { return reply(400, { error: 'bad request' }); }

  // The customer changes their project while paying: written to the open order they are paying for.
  if (body.action === 'choose') {
    const id = String(body.session || '');
    if (!/^cs_(test|live)_[A-Za-z0-9]{10,200}$/.test(id) || !(body.choice in CHOICES || body.choice === '')) return reply(400, { error: 'bad choice' });
    const s = await stripe('checkout/sessions/' + id, KEY, null, 'GET');
    if (!s.ok || s.data.status !== 'open' || (s.data.metadata || {}).source !== 'website-shop') return reply(409, { error: 'order not open' });
    const f = new URLSearchParams(); f.set('metadata[choice]', body.choice);
    const u = await stripe('checkout/sessions/' + id, KEY, f);
    return u.ok ? reply(200, { choice: body.choice || null }) : reply(502, { error: 'stripe error' });
  }
  const lines = cleanLines(body.lines);
  if (!lines) return reply(400, { error: 'bad cart' });
  const code = String(body.code || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 24);

  const P250 = BAG['250g'], P1KG = BAG['1kg'];
  const DELIVERY = parseInt(process.env.DELIVERY_CENTS || '400', 10);
  const FREE_FROM = parseInt(process.env.FREE_FROM_CENTS || '5000', 10);
  const host = event.headers && event.headers.host;
  const origin = (event.headers && event.headers.origin) || (host ? 'https://' + host : '');
  if (!/^https?:\/\//.test(origin)) return reply(400, { error: 'bad origin' });

  const every = (lines.find(l => l.every) || {}).every || 0;
  const form = new URLSearchParams();
  form.set('mode', every ? 'subscription' : 'payment');
  form.set('locale', 'en-GB');
  // Stripe's hosted checkout (156): the customer goes to checkout.stripe.com and comes back here
  form.set('success_url', origin + '/shop/?paid=1&order={CHECKOUT_SESSION_ID}');
  form.set('cancel_url', origin + '/shop/');
  form.set('shipping_address_collection[allowed_countries][0]', 'SG');
  form.set('phone_number_collection[enabled]', 'true');
  if (!every) {
  form.set('customer_creation', 'always'); // so a customer's orders can be totalled on the confirmation page
  form.set('shipping_options[0][shipping_rate_data][type]', 'fixed_amount');
  // The roast-day promise, shown on the delivery line before they pay (as on the confirmation page).
  const oneOffSub = lines.reduce((n, l) => n + (l.size === '250g' ? P250 : P1KG) * l.qty, 0);
  const charge = oneOffSub < FREE_FROM ? Math.max(0, DELIVERY) : 0;
  form.set('shipping_options[0][shipping_rate_data][display_name]', (charge ? 'Delivery' : 'Free delivery') + ' within Singapore \u00b7 roasted Wednesday, dispatched shortly after');
  form.set('shipping_options[0][shipping_rate_data][fixed_amount][amount]', String(charge));
  form.set('shipping_options[0][shipping_rate_data][fixed_amount][currency]', 'sgd');
  }
  const ref = orderRef();
  form.set('metadata[source]', 'website-shop');
  form.set('metadata[order_ref]', ref);
  if (every) {
    form.set('subscription_data[description]', 'NoFilter coffee every ' + (every === 1 ? 'week' : every + ' weeks') + ' (' + ref + ')');
    form.set('subscription_data[metadata][source]', 'website-shop');
    form.set('subscription_data[metadata][contribution_rate]', CONTRIBUTION_RATE);
    form.set('subscription_data[metadata][order_ref]', ref);
    form.set('subscription_data[metadata][every_weeks]', String(every));
    form.set('custom_text[submit][message]', 'Delivered every ' + (every === 1 ? 'week' : every + ' weeks') + ' from that Wednesday\u2019s roast, charged each time until you cancel. Swap coffees, skip a delivery or cancel any time from your order page. [Subscription terms](' + origin + '/subscription-terms/)');
  } else {
    form.set('payment_intent_data[description]', 'NoFilter order ' + ref);
    form.set('payment_intent_data[metadata][order_ref]', ref);
  }
  form.set('metadata[contribution_rate]', CONTRIBUTION_RATE);
  form.set('metadata[choice]', body.choice in CHOICES ? body.choice : '');
  // A client code: in a one-off order Stripe applies it. In a subscription order the customer gets the
  // better of the two, never both: subscription lines take max(SUB_OFF, code), one-off lines take the code;
  // applied to the prices here, since a Stripe code would apply to every future delivery too.
  let codePct = 0, promoId = null;
  if (code) {
    const c = await lookupCode(code, KEY);
    if (c) { promoId = c.promoId; if (every && c.subOk) codePct = c.pct; }
    form.set('metadata[code]', code);
  }
  const unit = l => { const base = l.size === '250g' ? P250 : P1KG;
    const off = every ? (l.every ? Math.max(SUB_OFF, codePct) : codePct) : 0; return Math.round(base * (1 - off)); };
  // Subscription lines use the range's real Stripe prices (so they can be swapped later), unless a client
  // code beats the subscription discount, in which case that line is priced here as before.
  let cat = null;
  const subOff = Math.max(SUB_OFF, codePct);
  if (every) cat = await ensureCatalogue(KEY, ORIGINS, { '250g': P250, '1kg': P1KG, delivery: Math.max(0, DELIVERY) }, subOff);
  lines.forEach((l, i) => {
    form.set(`line_items[${i}][quantity]`, String(l.qty));
    if (l.every && cat) { form.set(`line_items[${i}][price]`, cat[lookupKey(ORIGINS[l.name].origin, l.size, l.every, subOff)].price); return; }
    form.set(`line_items[${i}][price_data][currency]`, 'sgd');
    form.set(`line_items[${i}][price_data][unit_amount]`, String(unit(l)));
    if (l.every) { form.set(`line_items[${i}][price_data][recurring][interval]`, 'week'); form.set(`line_items[${i}][price_data][recurring][interval_count]`, String(l.every)); }
    form.set(`line_items[${i}][price_data][product_data][name]`, `${l.name} coffee, ${l.size === '250g' ? '250 g' : '1 kg'}`);
    form.set(`line_items[${i}][price_data][product_data][metadata][origin]`, ORIGINS[l.name].origin);
    form.set(`line_items[${i}][price_data][product_data][metadata][partner]`, ORIGINS[l.name].partner);
    form.set(`line_items[${i}][price_data][product_data][images][0]`, CDN + BAGS[l.name]);
  });

  // Subscription delivery: a recurring delivery line when each delivery's coffee comes to less than the threshold
  if (every) {
    const perDelivery = lines.filter(l => l.every).reduce((n, l) => n + unit(l) * l.qty, 0);
    form.set('subscription_data[metadata][off_pct]', String(Math.round(subOff * 100)));
    if (perDelivery < FREE_FROM && DELIVERY > 0) { const i = lines.length; form.set(`line_items[${i}][price]`, cat[deliveryKey(every)].price); form.set(`line_items[${i}][quantity]`, '1'); form.set('metadata[delivery_cents]', String(DELIVERY)); }
  }
  // One-off order: a known client code is applied by Stripe; otherwise they can type one in.
  // Subscription order: the code is already in the prices above, so no code box (it would stack).
  let applied = false;
  if (!every) { if (promoId) { form.set('discounts[0][promotion_code]', promoId); applied = true; } else form.set('allow_promotion_codes', 'true'); }
  else applied = codePct > 0;

  const { ok, data } = await stripe('checkout/sessions', KEY, form);
  // Stripe's own message (a sentence about a parameter, never a key or customer detail) so a refusal can be diagnosed.
  if (!ok || !data.url) return reply(502, { error: 'stripe error', detail: String((data && data.error && data.error.message) || '').replace(/\b(sk|pk|rk)_(test|live)_\S+/g, '$1_$2_…') || null });
  return reply(200, { url: data.url, session: data.id, code: applied ? code : null });
};

exports._test = { cleanLines, subscriptionCodeOk, COFFEES, ORIGINS, CHOICES, SUB_OFF, MAX_BAGS, BAG };
