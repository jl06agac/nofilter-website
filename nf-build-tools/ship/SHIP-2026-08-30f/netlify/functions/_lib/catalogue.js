/* The shop's subscription range in Stripe, created on first use and found again by lookup key after that.
   One Product per coffee and size (carrying its origin and partner, as the NGO report reads them) and four
   weekly Prices on each (every 1, 2, 3 or 4 weeks) at the subscription discount. Real products, rather than
   one-off price data, are what let a customer swap coffee, size or frequency in Stripe's customer portal.
   If the bag price changes (PRICE_BAG_* in Netlify), the next call creates the new Price and moves the
   lookup key to it; existing subscriptions keep their price until changed. Also sets up the portal
   configuration for card, address, invoices and cancelling.
   Not a function: Netlify only deploys .js files at the top of netlify/functions. */
const API = 'https://api.stripe.com/v1/';
async function call(path, key, form) {
  const res = await fetch(API + path, { method: form ? 'POST' : 'GET',
    headers: { Authorization: 'Bearer ' + key, ...(form ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}) },
    body: form ? form.toString() : undefined });
  const data = await res.json();
  if (!res.ok) { const e = Error('stripe error'); e.stripe = data && data.error && data.error.message; throw e; }
  return data;
}
const SIZES = { '250g': '250 g', '1kg': '1 kg' };
const EVERY = [1, 2, 3, 4];
const lookupKey = (origin, size, every) => `nf-sub-${origin}-${size}-w${every}`;

let cache = null; // per warm instance

// origins: { 'Batang Toru': { origin, partner }, ... }; prices: { '250g': cents, '1kg': cents }; off: 0.10
async function ensureCatalogue(key, origins, prices, off) {
  const want = {};
  for (const [name, o] of Object.entries(origins)) for (const size of Object.keys(SIZES)) for (const every of EVERY)
    want[lookupKey(o.origin, size, every)] = { name, size, every, origin: o.origin, partner: o.partner, amount: Math.round(prices[size] * (1 - off)) };
  const sig = JSON.stringify(want);
  if (cache && cache.sig === sig) return cache.map;
  const keys = Object.keys(want), found = {};
  for (let i = 0; i < keys.length; i += 10) {
    const q = keys.slice(i, i + 10).map(k => 'lookup_keys[]=' + encodeURIComponent(k)).join('&');
    const r = await call('prices?active=true&limit=100&' + q, key);
    for (const p of r.data) found[p.lookup_key] = p;
  }
  const products = {}; // origin|size -> product id
  for (const p of Object.values(found)) { const w = want[p.lookup_key]; if (w) products[w.origin + '|' + w.size] = p.product; }
  const map = {};
  for (const [lk, w] of Object.entries(want)) {
    let p = found[lk];
    if (!p || p.unit_amount !== w.amount || p.currency !== 'sgd') {
      const pk = w.origin + '|' + w.size;
      if (!products[pk]) {
        const f = new URLSearchParams();
        f.set('name', `${w.name} coffee, ${SIZES[w.size]}`);
        f.set('metadata[origin]', w.origin); f.set('metadata[partner]', w.partner); f.set('metadata[nf_key]', `${w.origin}-${w.size}`);
        products[pk] = (await call('products', key, f)).id;
      }
      const f = new URLSearchParams();
      f.set('product', products[pk]); f.set('currency', 'sgd'); f.set('unit_amount', String(w.amount));
      f.set('recurring[interval]', 'week'); f.set('recurring[interval_count]', String(w.every));
      f.set('lookup_key', lk); f.set('transfer_lookup_key', 'true');
      f.set('nickname', `Every ${w.every === 1 ? 'week' : w.every + ' weeks'}`);
      p = await call('prices', key, f);
    }
    map[lk] = { price: p.id, product: typeof p.product === 'string' ? p.product : p.product.id };
  }
  cache = { sig, map };
  return map;
}

// The portal configuration for the shop: card, delivery address, email, invoices, and cancel at the end of
// the period. Swapping coffee, size and frequency happens on the shop's own order page instead, because the
// portal can only update subscriptions with a single item and a shop subscription can hold several coffees.
async function ensurePortal(key) {
  const list = await call('billing_portal/configurations?active=true&limit=20', key);
  const have = (list.data || []).find(c => (c.metadata || {}).nf === 'shop-v1');
  if (have) return have.id;
  const f = new URLSearchParams();
  f.set('business_profile[headline]', 'NoFilter coffee: your subscription, card and delivery address.');
  f.set('features[subscription_cancel][enabled]', 'true');
  f.set('features[subscription_cancel][mode]', 'at_period_end');
  f.set('features[payment_method_update][enabled]', 'true');
  f.set('features[invoice_history][enabled]', 'true');
  f.set('features[customer_update][enabled]', 'true');
  f.set('features[customer_update][allowed_updates][0]', 'shipping');
  f.set('features[customer_update][allowed_updates][1]', 'email');
  f.set('metadata[nf]', 'shop-v1');
  return (await call('billing_portal/configurations', key, f)).id;
}
function hash(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return (h >>> 0).toString(36); }

module.exports = { ensureCatalogue, ensurePortal, lookupKey, call };
