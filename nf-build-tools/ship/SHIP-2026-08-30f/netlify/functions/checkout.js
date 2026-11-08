/* NoFilter checkout: turns the cart into a Stripe Checkout Session and returns its URL.
   PRICES AND PRODUCTS LIVE HERE, not in the page: the page sends only names, sizes and
   quantities, and anything not on the list below is refused.
   Netlify -> Site settings -> Environment:
     STRIPE_SECRET_KEY   sk_test_... to rehearse, sk_live_... to go live (without it: 503)
     PRICE_BAG_250G      unit amount in cents (default 2400 = SGD 24.00, MARKETS.SG.bag250)
     PRICE_BAG_1KG       unit amount in cents (default 8000 = SGD 80.00, MARKETS.SG.bag1kg)
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
  'Batang Toru': { origin: 'toru', partner: 'PRCF Indonesia, SRI' },
  'Batang Gadis': { origin: 'gadis', partner: 'SRI' },
  'Gayo Lues': { origin: 'gayo', partner: 'OIC' },
  'Arakan Mountains': { origin: 'arakan', partner: 'Fauna & Flora Myanmar, ACCA' }
};
const COFFEES = Object.keys(ORIGINS);
const CONTRIBUTION_RATE = '0.10';
const reply = (statusCode, body) => ({ statusCode, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }, body: JSON.stringify(body) });

async function stripe(path, key, form, method = 'POST') {
  const res = await fetch('https://api.stripe.com/v1/' + path, {
    method,
    headers: { Authorization: 'Bearer ' + key, ...(form ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}) },
    body: form ? form.toString() : undefined
  });
  return { ok: res.ok, data: await res.json() };
}

// One line per coffee and size; quantities merged, capped at 20 bags a line.
function cleanLines(lines) {
  if (!Array.isArray(lines) || !lines.length || lines.length > 20) return null;
  const merged = new Map();
  for (const l of lines) {
    const name = COFFEES.find(c => c === String(l && l.name || '').trim());
    const size = String(l && l.size || '').toLowerCase().replace(/\s+/g, '');
    const qty = parseInt(l && l.qty, 10);
    if (!name || !['250g', '1kg'].includes(size) || !Number.isInteger(qty) || qty < 1) return null;
    const k = name + '|' + size;
    merged.set(k, Math.min(20, (merged.get(k) || 0) + qty));
  }
  return [...merged].map(([k, qty]) => { const [name, size] = k.split('|'); return { name, size, qty }; });
}

exports.handler = async function (event) {
  if (event.httpMethod !== 'POST') return reply(405, { error: 'POST only' });
  const KEY = process.env.STRIPE_SECRET_KEY;
  if (!KEY) return reply(503, { error: 'payments not configured' });
  let body;
  try { body = JSON.parse(event.body || '{}'); } catch (e) { return reply(400, { error: 'bad request' }); }
  const lines = cleanLines(body.lines);
  if (!lines) return reply(400, { error: 'bad cart' });
  const code = String(body.code || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 24);

  const P250 = parseInt(process.env.PRICE_BAG_250G || '2400', 10);
  const P1KG = parseInt(process.env.PRICE_BAG_1KG || '8000', 10);
  const DELIVERY = parseInt(process.env.DELIVERY_CENTS || '0', 10);
  const host = event.headers && event.headers.host;
  const origin = (event.headers && event.headers.origin) || (host ? 'https://' + host : '');
  if (!/^https?:\/\//.test(origin)) return reply(400, { error: 'bad origin' });

  const form = new URLSearchParams();
  form.set('mode', 'payment');
  form.set('locale', 'en-GB');
  form.set('success_url', origin + '/shop/?paid=1&order={CHECKOUT_SESSION_ID}');
  form.set('cancel_url', origin + '/shop/');
  form.set('shipping_address_collection[allowed_countries][0]', 'SG');
  form.set('phone_number_collection[enabled]', 'true');
  form.set('shipping_options[0][shipping_rate_data][type]', 'fixed_amount');
  form.set('shipping_options[0][shipping_rate_data][display_name]', DELIVERY ? 'Delivery within Singapore' : 'Free delivery within Singapore');
  form.set('shipping_options[0][shipping_rate_data][fixed_amount][amount]', String(Math.max(0, DELIVERY)));
  form.set('shipping_options[0][shipping_rate_data][fixed_amount][currency]', 'sgd');
  form.set('metadata[source]', 'website-shop');
  form.set('metadata[contribution_rate]', CONTRIBUTION_RATE);
  lines.forEach((l, i) => {
    form.set(`line_items[${i}][quantity]`, String(l.qty));
    form.set(`line_items[${i}][price_data][currency]`, 'sgd');
    form.set(`line_items[${i}][price_data][unit_amount]`, String(l.size === '250g' ? P250 : P1KG));
    form.set(`line_items[${i}][price_data][product_data][name]`, `${l.name} coffee, ${l.size === '250g' ? '250 g' : '1 kg'}`);
    form.set(`line_items[${i}][price_data][product_data][metadata][origin]`, ORIGINS[l.name].origin);
    form.set(`line_items[${i}][price_data][product_data][metadata][partner]`, ORIGINS[l.name].partner);
  });

  // A client code is applied for them when Stripe knows it; otherwise they can type one in.
  let applied = false;
  if (code) {
    const found = await stripe('promotion_codes?active=true&limit=1&code=' + encodeURIComponent(code), KEY, null, 'GET');
    const promo = found.ok && found.data && Array.isArray(found.data.data) ? found.data.data[0] : null;
    if (promo && promo.id) { form.set('discounts[0][promotion_code]', promo.id); applied = true; }
    form.set('metadata[code]', code);
  }
  if (!applied) form.set('allow_promotion_codes', 'true');

  const { ok, data } = await stripe('checkout/sessions', KEY, form);
  if (!ok || !data.url) return reply(502, { error: 'stripe error' });
  return reply(200, { url: data.url, code: applied ? code : null });
};

exports._test = { cleanLines, COFFEES, ORIGINS };
