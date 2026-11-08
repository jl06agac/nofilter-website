/* One shop order, for the confirmation page the customer lands on after paying.
     GET  /.netlify/functions/order-summary?order=cs_...            the order (JSON)
     GET  /.netlify/functions/order-summary?order=cs_...&manage=1   opens Stripe's self-service page for
                                                                    this customer's subscription (redirect)
     POST /.netlify/functions/order-summary  {order, reportBack, news}  records the customer's choices
   The order id (Stripe's {CHECKOUT_SESSION_ID}) is long, random and only in the payer's browser; holding it
   is what lets the page show the order, as Stripe's own return-page guidance does. Only paid orders the shop
   created are answered.
   GET returns: the order number, what was bought (with each line's delivery frequency), what was paid, the
   email the confirmation went to, the delivery address, the card's brand and last four, the subscription
   (frequency, next charge), the contribution by origin and partner, and the running total this customer's
   paid shop orders and subscription deliveries have sent to conservation. Never returned: phone, full card
   details, billing address. */
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
const shipOf = s => (s.total_details || {}).amount_shipping || 0;

// Everything this customer's paid shop orders and subscription renewals have sent to conservation.
async function givenSoFar(customer, key) {
  if (!customer) return null;
  let total = 0, orders = 0;
  const sessions = await call(`checkout/sessions?customer=${customer}&limit=100`, key);
  for (const s of sessions.data || []) {
    if (s.payment_status !== 'paid' || (s.metadata || {}).source !== 'website-shop') continue;
    total += Math.round(((s.amount_total || 0) - shipOf(s)) * parseFloat((s.metadata || {}).contribution_rate || '0.10')); orders++;
  }
  const inv = await call(`invoices?customer=${customer}&status=paid&limit=100`, key);
  for (const i of inv.data || []) {
    if (i.billing_reason !== 'subscription_cycle') continue;
    const meta = (i.parent && i.parent.subscription_details && i.parent.subscription_details.metadata) || (i.subscription_details && i.subscription_details.metadata) || {};
    if (meta.source !== 'website-shop') continue;
    total += Math.round((i.amount_paid || 0) * parseFloat(meta.contribution_rate || '0.10')); orders++;
  }
  return { total, orders };
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
    const s = await call('checkout/sessions/' + id + '?expand[]=payment_intent.latest_charge&expand[]=subscription.default_payment_method', KEY);
    if (s.payment_status !== 'paid' || (s.metadata || {}).source !== 'website-shop') return reply(404, { error: 'no such order' });
    const customer = typeof s.customer === 'string' ? s.customer : (s.customer && s.customer.id) || null;
    const sub = s.subscription && typeof s.subscription === 'object' ? s.subscription : null;

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
      const p = await call('billing_portal/sessions', KEY, f);
      return { statusCode: 303, headers: { Location: p.url, 'Cache-Control': 'no-store' }, body: '' };
    }

    const rate = parseFloat((s.metadata || {}).contribution_rate || '0.10');
    const lines = await call(`checkout/sessions/${id}/line_items?limit=100&expand[]=data.price.product`, KEY);
    const by = {};
    for (const l of lines.data) {
      const m = (l.price && l.price.product && l.price.product.metadata) || {};
      const k = (m.origin || 'unknown') + '|' + (m.partner || '');
      if (!by[k]) by[k] = { origin: m.origin || 'unknown', name: String(l.description || '').split(' coffee')[0], partner: m.partner || '', bags: 0, sales: 0 };
      by[k].bags += l.quantity || 0; by[k].sales += l.amount_total || 0;
    }
    const byPartner = Object.values(by).map(v => ({ origin: v.origin, name: v.name, partner: v.partner, bags: v.bags, contribution: Math.round(v.sales * rate) }));
    const items = lines.data.map(l => { const [name, size] = String(l.description || '').split(' coffee, ');
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
      firstName: String((ship && ship.name) || cd.name || '').trim().split(/\s+/)[0] || null,
      address: ship ? [ship.name, a.line1, a.line2, [a.city || 'Singapore', a.postal_code].filter(Boolean).join(' ')].filter(Boolean) : [],
      items, subtotal: s.amount_subtotal || 0, discount: (s.total_details || {}).amount_discount || 0,
      delivery: shipOf(s), total: s.amount_total || 0,
      paidWith: card ? { brand: card.brand || '', last4: card.last4 || '', wallet: wallet || null } : ptype ? { brand: ptype } : null,
      placed: s.created || null };

    let subscription = null;
    if (sub) {
      const item = sub.items && sub.items.data && sub.items.data[0];
      const every = +((sub.metadata || {}).every_weeks) || (item && item.price && item.price.recurring && item.price.recurring.interval_count) || 0;
      subscription = { every, nextCharge: (item && item.current_period_end) || sub.current_period_end || null, status: sub.status, managed: !!customer };
      // the project chosen while paying carries on to every delivery (read by the NGO report)
      const choice = (s.metadata || {}).choice || '';
      if (choice && (sub.metadata || {}).choice !== choice) { const f = new URLSearchParams(); f.set('metadata[choice]', choice); call('subscriptions/' + sub.id, KEY, f).catch(() => {}); }
    }

    let given = null;
    try { given = await givenSoFar(customer, KEY); } catch (e) { given = null; }

    return reply(200, { order, subscription, given, currency: s.currency || 'sgd', bags: byPartner.reduce((n, v) => n + v.bags, 0),
      contribution: byPartner.reduce((n, v) => n + v.contribution, 0), byPartner, code: (s.metadata || {}).code || null,
      choice: (s.metadata || {}).choice || null });
  } catch (e) { return reply(502, { error: 'stripe error', detail: e.stripe ? String(e.stripe).replace(/\b(sk|pk|rk)_(test|live)_\S+/g, '$1_$2_…') : null }); }
};
