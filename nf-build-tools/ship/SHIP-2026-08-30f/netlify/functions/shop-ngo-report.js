/* What the retail shop owes each conservation partner, for a period, worked out from paid
   Stripe orders. Stripe is the record; nothing is stored here.
     GET /.netlify/functions/shop-ngo-report?from=2026-07-01&to=2026-12-31
     header x-report-key: <REPORT_KEY>       (Netlify environment variable; without it: 503)
   For every paid order the shop created (metadata.source = website-shop), each line's
   amount after discounts is grouped by the coffee's origin and partner (stamped on the line
   by checkout.js), and the contribution is that amount times the order's contribution_rate.
   byChoice splits the same amounts by the project the customer chose (where-needed if none).
   Delivery charges are not coffee and carry no contribution. Refunds are not netted off:
   a refunded order is listed under `refunded` so it can be excluded by hand.
   Dates are Singapore dates, inclusive. Amounts are in cents (SGD). */
const crypto = require('crypto');
const reply = (statusCode, body) => ({ statusCode, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }, body: JSON.stringify(body) });
const sgDay = (d, endOfDay) => Math.floor(Date.parse(d + (endOfDay ? 'T23:59:59.999+08:00' : 'T00:00:00+08:00')) / 1000);

function sameKey(given, expected) {
  const a = Buffer.from(String(given || '')), b = Buffer.from(String(expected || ''));
  return a.length === b.length && a.length > 0 && crypto.timingSafeEqual(a, b);
}

async function get(path, key) {
  const res = await fetch('https://api.stripe.com/v1/' + path, { headers: { Authorization: 'Bearer ' + key } });
  const data = await res.json();
  if (!res.ok) throw Error((data && data.error && data.error.message) || 'stripe error');
  return data;
}

// Groups one order's lines by origin; pure, so it can be tested without Stripe.
function contributions(lines, rate) {
  const out = {};
  for (const l of lines) {
    const meta = (l.price && l.price.product && l.price.product.metadata) || {};
    const origin = meta.origin || 'unknown', partner = meta.partner || 'unknown';
    const k = origin + '|' + partner;
    if (!out[k]) out[k] = { origin, partner, sales: 0, contribution: 0, bags: 0 };
    out[k].sales += l.amount_total || 0;
    out[k].bags += l.quantity || 0;
  }
  for (const v of Object.values(out)) v.contribution = Math.round(v.sales * rate);
  return out;
}

exports.handler = async function (event) {
  const KEY = process.env.STRIPE_SECRET_KEY, REPORT = process.env.REPORT_KEY;
  if (!KEY || !REPORT) return reply(503, { error: 'report not configured' });
  if (!sameKey(event.headers && event.headers['x-report-key'], REPORT)) return reply(403, { error: 'not authorised' });
  const q = event.queryStringParameters || {};
  if (!/^\d{4}-\d{2}-\d{2}$/.test(q.from || '') || !/^\d{4}-\d{2}-\d{2}$/.test(q.to || '')) return reply(400, { error: 'from and to are YYYY-MM-DD' });
  const gte = sgDay(q.from, false), lte = sgDay(q.to, true);
  if (!(gte <= lte)) return reply(400, { error: 'from is after to' });

  const totals = {}, refunded = [], byChoice = {};
  let orders = 0, after = '';
  try {
    for (;;) {
      const page = await get(`checkout/sessions?status=complete&limit=100&created[gte]=${gte}&created[lte]=${lte}&expand[]=data.payment_intent.latest_charge${after ? '&starting_after=' + after : ''}`, KEY);
      for (const s of page.data) {
        if (s.payment_status !== 'paid' || (s.metadata || {}).source !== 'website-shop') continue;
        const rate = parseFloat((s.metadata || {}).contribution_rate || '0.10');
        const lines = await get(`checkout/sessions/${s.id}/line_items?limit=100&expand[]=data.price.product`, KEY);
        const pi = s.payment_intent && typeof s.payment_intent === 'object' ? s.payment_intent : null;
        if (pi && pi.latest_charge && typeof pi.latest_charge === 'object' && pi.latest_charge.refunded) refunded.push(s.id);
        orders++;
        const choice = (s.metadata || {}).choice || 'where-needed';
        for (const [k, v] of Object.entries(contributions(lines.data, rate))) {
          if (!totals[k]) totals[k] = { origin: v.origin, partner: v.partner, sales: 0, contribution: 0, bags: 0 };
          totals[k].sales += v.sales; totals[k].contribution += v.contribution; totals[k].bags += v.bags;
          const ck = choice + '|' + k;
          if (!byChoice[ck]) byChoice[ck] = { choice, origin: v.origin, partner: v.partner, contribution: 0 };
          byChoice[ck].contribution += v.contribution;
        }
      }
      if (!page.has_more || !page.data.length) break;
      after = page.data[page.data.length - 1].id;
    }
  } catch (e) { return reply(502, { error: e.message }); }

  const byPartner = Object.values(totals).sort((a, b) => b.contribution - a.contribution);
  return reply(200, { from: q.from, to: q.to, currency: 'sgd', orders, byPartner, byChoice: Object.values(byChoice),
    contribution: byPartner.reduce((n, v) => n + v.contribution, 0), refunded });
};

exports._test = { contributions, sgDay };
