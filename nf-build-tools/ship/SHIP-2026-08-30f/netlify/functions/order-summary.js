/* What one shop order put towards conservation, for the thank-you panel the customer lands on.
     GET /.netlify/functions/order-summary?order=cs_...   (Stripe's {CHECKOUT_SESSION_ID})
   Returns only bags and contribution by origin and partner: no name, address, email or card.
   Only paid orders the shop created are answered. When the shop later offers a list of items to
   fund, the customer's choice can be written to this order's metadata from here. */
const reply = (statusCode, body) => ({ statusCode, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }, body: JSON.stringify(body) });

async function get(path, key) {
  const res = await fetch('https://api.stripe.com/v1/' + path, { headers: { Authorization: 'Bearer ' + key } });
  const data = await res.json();
  if (!res.ok) throw Error('stripe error');
  return data;
}

exports.handler = async function (event) {
  const KEY = process.env.STRIPE_SECRET_KEY;
  if (!KEY) return reply(503, { error: 'payments not configured' });
  const id = String((event.queryStringParameters || {}).order || '');
  if (!/^cs_(test|live)_[A-Za-z0-9]{10,200}$/.test(id)) return reply(400, { error: 'bad order' });
  try {
    const s = await get('checkout/sessions/' + id, KEY);
    if (s.payment_status !== 'paid' || (s.metadata || {}).source !== 'website-shop') return reply(404, { error: 'no such order' });
    const rate = parseFloat((s.metadata || {}).contribution_rate || '0.10');
    const lines = await get(`checkout/sessions/${id}/line_items?limit=100&expand[]=data.price.product`, KEY);
    const by = {};
    for (const l of lines.data) {
      const m = (l.price && l.price.product && l.price.product.metadata) || {};
      const k = (m.origin || 'unknown') + '|' + (m.partner || '');
      if (!by[k]) by[k] = { origin: m.origin || 'unknown', name: String(l.description || '').split(' coffee')[0], partner: m.partner || '', bags: 0, sales: 0 };
      by[k].bags += l.quantity || 0; by[k].sales += l.amount_total || 0;
    }
    const byPartner = Object.values(by).map(v => ({ origin: v.origin, name: v.name, partner: v.partner, bags: v.bags, contribution: Math.round(v.sales * rate) }));
    return reply(200, { currency: s.currency || 'sgd', bags: byPartner.reduce((n, v) => n + v.bags, 0),
      contribution: byPartner.reduce((n, v) => n + v.contribution, 0), byPartner, code: (s.metadata || {}).code || null });
  } catch (e) { return reply(502, { error: 'stripe error' }); }
};
