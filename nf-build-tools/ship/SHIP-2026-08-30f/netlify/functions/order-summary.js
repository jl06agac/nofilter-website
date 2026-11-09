/* One shop order, for the confirmation page the customer lands on after paying.
     GET  /.netlify/functions/order-summary?order=cs_...            the order (JSON)
     GET  /.netlify/functions/order-summary?order=cs_...&manage=1   opens Stripe's self-service page for
                                                                    this customer's subscription (redirect)
     POST /.netlify/functions/order-summary  {order, reportBack, news}  records the customer's choices
     POST ... {order, action:'swap', items:[{id, name, size, qty}]}   change coffee, size or quantity (qty 0
                                                                       removes a coffee; one must remain)
     POST ... {order, action:'every', every:1-4}                       change how often; takes effect after
                                                                       the delivery already paid for
     POST ... {order, action:'skip'} / {action:'unskip'}               skip the next delivery, or undo it
   Changes never charge on the spot: swaps apply from the next delivery, a new frequency starts when the
   current period ends.
   The order id (Stripe's {CHECKOUT_SESSION_ID}) is long, random and only in the payer's browser; holding it
   is what lets the page show the order, as Stripe's own return-page guidance does. Only paid orders the shop
   created are answered.
   GET returns: the order number, what was bought (with each line's delivery frequency), what was paid, the
   email the confirmation went to, the delivery address, the card's brand and last four, the subscription
   (frequency, next charge), the contribution by origin and partner, and the running total this customer's
   paid shop orders and subscription deliveries have sent to conservation. Never returned: phone, full card
   details, billing address. */
const { ensureCatalogue, ensurePortal, lookupKey, deliveryKey } = require('./_lib/catalogue.js');
const { ORIGINS, SUB_OFF, BAG } = require('./checkout.js')._test;
const reply = (statusCode, body, extra) => ({ statusCode, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...(extra || {}) }, body: JSON.stringify(body) });

async function call(path, key, form) {
  const res = await fetch('https://api.stripe.com/v1/' + path, {
    method: form ? 'POST' : 'GET',
    headers: { Authorization: 'Bearer ' + key, ...(form ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}) },
    body: form ? form.toString() : undefined
  });
  const data = await res.json();
  if (!res.ok) { const e = Error('stripe error'); e.stripe = data && data.error && data.error.message; throw e; }
  return data;
}
const subPeriodEnd = sub => { const it = sub.items && sub.items.data && sub.items.data[0]; return (it && it.current_period_end) || sub.current_period_end || sub.trial_end || 0; };
const isDelivery = it => { const pr = it.price || {}, prod = pr.product && typeof pr.product === 'object' ? pr.product : {};
  return (prod.metadata || {}).kind === 'delivery' || /^delivery$/i.test(prod.name || '') || /delivery/i.test(it.description || ''); };
const shipOf = s => (s.total_details || {}).amount_shipping || 0;

// Everything this customer's paid shop orders and subscription renewals have sent to conservation.
async function givenSoFar(customer, key) {
  if (!customer) return null;
  let total = 0, orders = 0;
  const sessions = await call(`checkout/sessions?customer=${customer}&limit=100`, key);
  for (const s of sessions.data || []) {
    if (s.payment_status !== 'paid' || (s.metadata || {}).source !== 'website-shop') continue;
    total += Math.round(Math.max(0, (s.amount_total || 0) - shipOf(s) - (+(s.metadata || {}).delivery_cents || 0)) * parseFloat((s.metadata || {}).contribution_rate || '0.10')); orders++;
  }
  const inv = await call(`invoices?customer=${customer}&status=paid&limit=100`, key);
  for (const i of inv.data || []) {
    if (i.billing_reason !== 'subscription_cycle') continue;
    const meta = (i.parent && i.parent.subscription_details && i.parent.subscription_details.metadata) || (i.subscription_details && i.subscription_details.metadata) || {};
    if (meta.source !== 'website-shop') continue;
    const del = ((i.lines && i.lines.data) || []).filter(l => /delivery/i.test(l.description || '')).reduce((n, l) => n + (l.amount || 0), 0);
    total += Math.round(Math.max(0, (i.amount_paid || 0) - del) * parseFloat(meta.contribution_rate || '0.10')); orders++;
  }
  return { total, orders };
}

function paidAtOf(s, ch) {
  const inv = s.invoice && typeof s.invoice === 'object' ? s.invoice : null;
  if (inv) return (inv.status === 'paid' && inv.status_transitions && inv.status_transitions.paid_at) || null;
  if (s.mode === 'subscription') return null;
  return (s.payment_status === 'paid' && ch && ch.status === 'succeeded' && ch.created) || null;
}

exports.handler = async function (event) {
  const KEY = process.env.STRIPE_SECRET_KEY;
  if (!KEY) return reply(503, { error: 'payments not configured' });
  const post = event.httpMethod === 'POST';
  let body = {};
  if (post) { try { body = JSON.parse(event.body || '{}'); } catch (e) { return reply(400, { error: 'bad request' }); } }
  const q = event.queryStringParameters || {};
  const id = String((post ? body.order : q.order) || '');
  if (!/^cs_(test|live)_[A-Za-z0-9]{10,200}$/.test(id)) return reply(400, { error: 'bad order' });
  try {
    // Stripe expands at most 4 levels, so the subscription's items and products come in their own call
    const s = await call('checkout/sessions/' + id + '?expand[]=payment_intent.latest_charge&expand[]=invoice', KEY);
    if (s.payment_status !== 'paid' || (s.metadata || {}).source !== 'website-shop') return reply(404, { error: 'no such order' });
    const customer = typeof s.customer === 'string' ? s.customer : (s.customer && s.customer.id) || null;
    const subId = typeof s.subscription === 'string' ? s.subscription : (s.subscription && s.subscription.id) || null;
    const sub = subId ? await call('subscriptions/' + subId + '?expand[]=default_payment_method&expand[]=items.data.price.product', KEY) : null;

    // Subscription changes
    if (post && body.action) {
      if (!sub || !['active', 'trialing', 'past_due'].includes(sub.status)) return reply(409, { error: 'no active subscription' });
      const periodEnd = subPeriodEnd(sub);
      if (body.action === 'skip' || body.action === 'unskip') {
        const f = new URLSearchParams();
        if (body.action === 'skip') { f.set('pause_collection[behavior]', 'void'); f.set('pause_collection[resumes_at]', String(periodEnd + 3600)); }
        else f.set('pause_collection', '');
        await call('subscriptions/' + sub.id, KEY, f);
        return reply(200, { skipped: body.action === 'skip' });
      }
      const DEL = parseInt(process.env.DELIVERY_CENTS || '400', 10), FREE_FROM = parseInt(process.env.FREE_FROM_CENTS || '5000', 10);
      const P = { '250g': BAG['250g'], '1kg': BAG['1kg'], delivery: DEL };
      const off = Math.max(SUB_OFF, (+((sub.metadata || {}).off_pct) || Math.round(SUB_OFF * 100)) / 100);
      const cat = await ensureCatalogue(KEY, ORIGINS, P, off);
      const all = (sub.items && sub.items.data) || [];
      const items = all.filter(it => !isDelivery(it)), delItem = all.find(isDelivery);
      const curEvery = +((sub.metadata || {}).every_weeks) || (items[0] && items[0].price.recurring.interval_count) || 2;
      const priceFor = (name, size, every) => { const o = ORIGINS[name]; const c = o && cat[lookupKey(o.origin, size, every, off)]; return c && c.price; };
      const unitOf = size => Math.round(P[size] * (1 - off));
      const sizeOf = it => (/1\s*kg/i.test((it.price.product && it.price.product.name) || it.price.nickname || '') ? '1kg' : '250g');
      const nameOf = it => Object.keys(ORIGINS).find(n => ((it.price.product && it.price.product.metadata) || {}).origin === ORIGINS[n].origin);
      const f = new URLSearchParams();
      f.set('proration_behavior', 'none');
      if (body.action === 'swap') {
        const want = Array.isArray(body.items) ? body.items : [];
        // The request must describe the whole subscription: every coffee once, nothing else. Otherwise Stripe
        // keeps the items left out and the delivery threshold would be judged on part of the basket.
        const ids = want.map(w => w && w.id);
        if (ids.length !== items.length || new Set(ids).size !== ids.length || !items.every(it => ids.includes(it.id)))
          return reply(409, { error: 'subscription changed; reload the page' });
        let kept = 0;
        want.forEach((w, i) => {
          if (!items.find(it => it.id === w.id)) return;
          const qty = Math.max(0, Math.min(20, parseInt(w.qty, 10) || 0));
          f.set(`items[${i}][id]`, w.id);
          if (!qty) { f.set(`items[${i}][deleted]`, 'true'); return; }
          const pr = priceFor(w.name, String(w.size).toLowerCase().replace(/\s+/g, ''), curEvery);
          if (!pr) throw Object.assign(Error('bad item'), { bad: true });
          f.set(`items[${i}][price]`, pr); f.set(`items[${i}][quantity]`, String(qty)); kept++;
        });
        if (!kept) return reply(400, { error: 'keep at least one coffee, or cancel instead' });
        var perDelivery = want.reduce((n, w) => { const q = Math.max(0, Math.min(20, parseInt(w.qty, 10) || 0)); return n + (q && items.find(it => it.id === w.id) ? unitOf(String(w.size).toLowerCase().replace(/\s+/g, '')) * q : 0); }, 0), nextI = want.length, newEvery = curEvery;
      } else if (body.action === 'every') {
        const n = parseInt(body.every, 10);
        if (![1, 2, 3, 4].includes(n)) return reply(400, { error: 'every 1-4 weeks' });
        items.forEach((it, i) => { const pr = priceFor(nameOf(it), sizeOf(it), n); if (!pr) throw Object.assign(Error('bad item'), { bad: true });
          f.set(`items[${i}][id]`, it.id); f.set(`items[${i}][price]`, pr); f.set(`items[${i}][quantity]`, String(it.quantity)); });
        var perDelivery = items.reduce((m, it) => m + unitOf(sizeOf(it)) * (it.quantity || 1), 0), nextI = items.length, newEvery = n;
        // a new interval would otherwise restart the billing period (and charge) today: hold it to the end of
        // the period already paid for
        f.set('trial_end', String(periodEnd));
        f.set('metadata[every_weeks]', String(n));
      } else return reply(400, { error: 'unknown action' });
      // delivery: charged per delivery under the threshold, dropped above it
      const needDel = perDelivery < FREE_FROM && DEL > 0;
      if (needDel) { const dp = cat[deliveryKey(newEvery)].price; if (delItem) { f.set(`items[${nextI}][id]`, delItem.id); } f.set(`items[${nextI}][price]`, dp); f.set(`items[${nextI}][quantity]`, '1'); }
      else if (delItem) { f.set(`items[${nextI}][id]`, delItem.id); f.set(`items[${nextI}][deleted]`, 'true'); }
      await call('subscriptions/' + sub.id + '?expand[]=items.data.price.product', KEY, f);
      return reply(200, { ok: true });
    }

    // The customer's choices: email when the partners report back, and news and offers.
    if (post) {
      if (!customer) return reply(409, { error: 'no customer' });
      const f = new URLSearchParams();
      f.set('metadata[report_back]', body.reportBack ? 'yes' : 'no');
      f.set('metadata[news]', body.news ? 'yes' : 'no');
      f.set('metadata[prefs_at]', new Date().toISOString());
      await call('customers/' + customer, KEY, f);
      return reply(200, { reportBack: !!body.reportBack, news: !!body.news });
    }

    // Manage: Stripe's self-service page for this customer (skip, pause, change, cancel).
    if (q.manage) {
      if (!customer) return reply(409, { error: 'no customer' });
      const host = event.headers && event.headers.host;
      const f = new URLSearchParams(); f.set('customer', customer); f.set('return_url', 'https://' + host + '/shop/');
      try { f.set('configuration', await ensurePortal(KEY)); } catch (e) { /* the account's default portal */ }
      const p = await call('billing_portal/sessions', KEY, f);
      return { statusCode: 303, headers: { Location: p.url, 'Cache-Control': 'no-store' }, body: '' };
    }

    const rate = parseFloat((s.metadata || {}).contribution_rate || '0.10');
    const lines = await call(`checkout/sessions/${id}/line_items?limit=100&expand[]=data.price.product`, KEY);
    const by = {};
    const delLines = lines.data.filter(l => ((l.price && l.price.product && l.price.product.metadata) || {}).kind === 'delivery');
    for (const l of lines.data) {
      const m = (l.price && l.price.product && l.price.product.metadata) || {};
      if (m.kind === 'delivery' || !m.origin) continue;
      const k = (m.origin || 'unknown') + '|' + (m.partner || '');
      if (!by[k]) by[k] = { origin: m.origin || 'unknown', name: String(l.description || '').split(' coffee')[0], partner: m.partner || '', bags: 0, sales: 0 };
      by[k].bags += l.quantity || 0; by[k].sales += l.amount_total || 0;
    }
    const byPartner = Object.values(by).map(v => ({ origin: v.origin, name: v.name, partner: v.partner, bags: v.bags, contribution: Math.round(v.sales * rate) }));
    const items = lines.data.filter(l => !delLines.includes(l)).map(l => { const [name, size] = String(l.description || '').split(' coffee, ');
      const r = l.price && l.price.recurring;
      return { name, size: size || '', qty: l.quantity || 0, amount: l.amount_total || 0, every: r && r.interval === 'week' ? r.interval_count : 0 }; });
    const ship = (s.collected_information && s.collected_information.shipping_details) || s.shipping_details || null;
    const a = (ship && ship.address) || {};
    const ch = s.payment_intent && s.payment_intent.latest_charge;
    const pm = sub && sub.default_payment_method && typeof sub.default_payment_method === 'object' ? sub.default_payment_method : null;
    const card = (ch && ch.payment_method_details && ch.payment_method_details.card) || (pm && pm.card) || null;
    const wallet = card && card.wallet && card.wallet.type;
    const ptype = (ch && ch.payment_method_details && ch.payment_method_details.type) || (pm && pm.type) || null;
    const cd = s.customer_details || {};
    const order = { ref: (s.metadata || {}).order_ref || null, email: cd.email || null,
      firstName: (n => n ? n.charAt(0).toUpperCase() + n.slice(1) : null)(String((ship && ship.name) || cd.name || '').trim().split(/\s+/)[0]),   /* "alex" typed at Stripe reads "Alex" */
      address: ship ? [ship.name, a.line1, a.line2, [a.city || 'Singapore', a.postal_code].filter(Boolean).join(' ')].filter(Boolean) : [],
      items, subtotal: s.amount_subtotal || 0, discount: (s.total_details || {}).amount_discount || 0,
      delivery: shipOf(s) + delLines.reduce((n, l) => n + (l.amount_total || 0), 0), total: s.amount_total || 0,
      paidWith: card ? { brand: card.brand || '', last4: card.last4 || '', wallet: wallet || null } : ptype ? { brand: ptype } : null,
      placed: s.created || null,
      // 182/184 (Codex): the moment the order counts for the Monday 12:00 cut-off, shared by the confirmation
      // page and the order email so both name the same roast. Subscriptions: when the first invoice (the
      // session's) was paid. One-off orders: the charge's time, once it has succeeded (checkout offers only
      // methods that settle at checkout). Not paid yet: null, and no roast date is stated.
      paidAt: paidAtOf(s, ch) };

    let subscription = null;
    if (sub) {
      const item = sub.items && sub.items.data && sub.items.data[0];
      const every = +((sub.metadata || {}).every_weeks) || (item && item.price && item.price.recurring && item.price.recurring.interval_count) || 0;
      const pc = sub.pause_collection && sub.pause_collection.behavior === 'void' ? sub.pause_collection : null;
      subscription = { every, nextCharge: subPeriodEnd(sub) || null, status: sub.status, managed: !!customer,
        skipping: pc ? { until: pc.resumes_at || null } : null, cancelling: !!sub.cancel_at_period_end,
        off: +((sub.metadata || {}).off_pct) || Math.round(SUB_OFF * 100),
        delivery: ((sub.items && sub.items.data) || []).filter(isDelivery).reduce((n, it) => n + ((it.price || {}).unit_amount || 0), 0),
        items: ((sub.items && sub.items.data) || []).filter(it => !isDelivery(it)).map(it => { const pr = it.price || {}, prod = pr.product && typeof pr.product === 'object' ? pr.product : {};
          const [name, size] = String(prod.name || '').split(' coffee, ');
          return { id: it.id, name: name || null, size: size || '', qty: it.quantity || 1, amount: (pr.unit_amount || 0) * (it.quantity || 1) }; }) };
      // the project chosen while paying carries on to every delivery (read by the NGO report)
      const choice = (s.metadata || {}).choice || '';
      if (choice && (sub.metadata || {}).choice !== choice) { const f = new URLSearchParams(); f.set('metadata[choice]', choice); call('subscriptions/' + sub.id, KEY, f).catch(() => {}); }
    }

    let given = null;
    try { given = await givenSoFar(customer, KEY); } catch (e) { given = null; }

    return reply(200, { order, subscription, given, currency: s.currency || 'sgd', bags: byPartner.reduce((n, v) => n + v.bags, 0),
      contribution: byPartner.reduce((n, v) => n + v.contribution, 0), byPartner, code: (s.metadata || {}).code || null,
      choice: (s.metadata || {}).choice || null });
  } catch (e) { if (e.bad) return reply(400, { error: 'that coffee or size is not in the range' }); return reply(502, { error: 'stripe error', detail: e.stripe ? String(e.stripe).replace(/\b(sk|pk|rk)_(test|live)_\S+/g, '$1_$2_…') : null }); }
};
