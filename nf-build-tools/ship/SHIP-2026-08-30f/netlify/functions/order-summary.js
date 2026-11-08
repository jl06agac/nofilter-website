/* One shop order, for the confirmation page the customer lands on after paying.
     GET /.netlify/functions/order-summary?order=cs_...   (Stripe's {CHECKOUT_SESSION_ID})
   Returns the order number, what was bought and paid, the email the confirmation went to, the
   delivery address, the card's brand and last four, and the contribution by origin and partner.
   As Stripe's own return-page guidance does: the session id is long, random and only in the payer's
   browser. Never returned: phone, full card details, billing address.
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
    const s = await get('checkout/sessions/' + id + '?expand[]=payment_intent.latest_charge', KEY);
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
    const items = lines.data.map(l => { const [name, size] = String(l.description || '').split(' coffee, ');
      return { name, size: size || '', qty: l.quantity || 0, amount: l.amount_total || 0 }; });
    const ship = (s.collected_information && s.collected_information.shipping_details) || s.shipping_details || null;
    const a = (ship && ship.address) || {};
    const ch = s.payment_intent && s.payment_intent.latest_charge;
    const card = ch && ch.payment_method_details && ch.payment_method_details.card;
    const wallet = card && card.wallet && card.wallet.type;
    const cd = s.customer_details || {};
    const order = { ref: (s.metadata || {}).order_ref || null, email: cd.email || null,
      firstName: String((ship && ship.name) || cd.name || '').trim().split(/\s+/)[0] || null,
      address: ship ? [ship.name, a.line1, a.line2, [a.city || 'Singapore', a.postal_code].filter(Boolean).join(' ')].filter(Boolean) : [],
      items, subtotal: s.amount_subtotal || 0, discount: (s.total_details || {}).amount_discount || 0,
      delivery: (s.total_details || {}).amount_shipping || 0, total: s.amount_total || 0,
      paidWith: card ? { brand: card.brand || '', last4: card.last4 || '', wallet: wallet || null }
        : (ch && ch.payment_method_details && ch.payment_method_details.type) ? { brand: ch.payment_method_details.type } : null,
      placed: s.created || null };
    return reply(200, { order, currency: s.currency || 'sgd', bags: byPartner.reduce((n, v) => n + v.bags, 0),
      contribution: byPartner.reduce((n, v) => n + v.contribution, 0), byPartner, code: (s.metadata || {}).code || null,
      choice: (s.metadata || {}).choice || null });
  } catch (e) { return reply(502, { error: 'stripe error' }); }
};
