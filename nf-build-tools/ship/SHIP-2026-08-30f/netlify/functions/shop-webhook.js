/* 166 · Stripe tells the site an order is paid; the site emails the customer NoFilter's own confirmation and
   emails NoFilter the order to fulfil.
     POST /.netlify/functions/shop-webhook   (Stripe webhook, event checkout.session.completed)
   Set up once in Stripe (Developers, Webhooks): endpoint https://nofilter.sg/.netlify/functions/shop-webhook,
   event checkout.session.completed. Stripe shows a signing secret (whsec_...); it goes in Netlify as
   STRIPE_WEBHOOK_SECRET. Without it this function answers 503 and sends nothing.
   Every request is checked against Stripe's signature (HMAC-SHA256 of "timestamp.body", five minutes'
   tolerance), so nobody else can make the site send mail. The order details come from order-summary.js, the
   same code and the same privacy limits as the confirmation page (no phone, no full card). Resend's
   Idempotency-Key is the Stripe session id, so a retried webhook never sends a second email.
   Uses RESEND_API_KEY and QUOTE_FROM (as the quote emails do); the NoFilter copy goes to ORDERS_TO, or
   QUOTE_TO, or hello@nofilter.sg. */
const crypto = require('crypto');
const summary = require('./order-summary.js');

const ESC = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const money = c => 'SGD ' + (Math.round(c) / 100).toFixed(2);
const EVERY = { 1: 'every week', 2: 'every 2 weeks', 3: 'every 3 weeks', 4: 'every 4 weeks' };
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const sgDay = (ms) => { const d = new Date(ms + 8 * 36e5); return { dow: d.getUTCDay(), date: d.getUTCDate(), month: MONTHS[d.getUTCMonth()] }; };
// the Wednesday roast after a moment (the confirmation page's nextRoast, in Singapore time)
function roastAfter(ms) { const d = sgDay(ms); const add = ((3 - d.dow + 7) % 7) || 7; const w = sgDay(ms + add * 864e5); return `Wednesday ${w.date} ${w.month}`; }
const dateOf = sec => { const d = sgDay(sec * 1000); return `${d.date} ${d.month}`; };

function verify(raw, header, secret, now = Date.now()) {
  const parts = Object.fromEntries(String(header || '').split(',').map(kv => kv.split('=')).filter(p => p.length === 2).map(([k, v]) => [k.trim(), v.trim()]));
  const sigs = String(header || '').split(',').filter(kv => kv.trim().startsWith('v1=')).map(kv => kv.trim().slice(3));
  const t = parseInt(parts.t, 10);
  if (!t || !sigs.length || Math.abs(now / 1000 - t) > 300) return false;
  const want = crypto.createHmac('sha256', secret).update(t + '.' + raw).digest('hex');
  return sigs.some(s => s.length === want.length && crypto.timingSafeEqual(Buffer.from(s), Buffer.from(want)));
}

function customerEmail(d, origin, sessionId) {
  const o = d.order || {}, sb = d.subscription, first = o.firstName ? ', ' + ESC(o.firstName) : '';
  const manage = sb && sb.every ? `${origin}/shop/?paid=1&order=${encodeURIComponent(sessionId)}&manage=page` : '';
  const per = sb && sb.every ? (sb.items || []).reduce((n, it) => n + (it.amount || 0), 0) + (sb.delivery || 0) : 0;
  const row = (l, r, bold) => `<tr><td style="padding:4px 0;font-size:14px;color:${bold ? '#1A1815' : '#6B645C'};${bold ? 'font-weight:700;' : ''}">${l}</td><td align="right" style="padding:4px 0;font-size:14px;color:#1A1815;${bold ? 'font-weight:700;' : ''}white-space:nowrap">${r}</td></tr>`;
  const items = (o.items || []).map(it => `<tr><td style="padding:8px 0;border-bottom:1px solid #E7E1D6;font-size:14px;color:#1A1815"><b>${ESC(it.name)}</b><br><span style="color:#6B645C;font-size:13px">${ESC(it.size)} &times; ${it.qty}${it.every ? ' &middot; ' + EVERY[it.every] : ''}</span></td><td align="right" style="padding:8px 0;border-bottom:1px solid #E7E1D6;font-size:14px;white-space:nowrap">${money(it.amount)}</td></tr>`).join('');
  const sums = (o.discount ? row('Discount' + (d.code ? ' (' + ESC(d.code) + ')' : ''), '&minus;' + money(o.discount)) : '') + row('Delivery', o.delivery ? money(o.delivery) : 'Free') + row('Total paid', money(o.total), true);
  const partners = (d.byPartner || []).map(p => (p.partner ? ESC(p.partner) + ' in ' : '') + ESC(p.name)).join('; ');
  const pw = o.paidWith ? ({ apple_pay: 'Apple Pay, ', google_pay: 'Google Pay, ' }[o.paidWith.wallet] || '') + ESC(String(o.paidWith.brand || '').replace(/^./, c => c.toUpperCase())) + (o.paidWith.last4 ? ' &bull;&bull;&bull;&bull; ' + ESC(o.paidWith.last4) : '') : '';
  const html = `<!doctype html><html><body style="margin:0;background:#F4F2EE;padding:32px 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;color:#1A1815">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;margin:0 auto">
<tr><td style="padding-bottom:20px"><img src="https://nofilter-shared.netlify.app/nofilter-wordmark-email.png" width="200" height="40" alt="NoFilter" style="display:block;border:0;width:200px;height:auto"></td></tr>
<tr><td style="border-top:2px solid #EE4D17;padding-top:22px">
<p style="margin:0 0 6px;font:600 11px/1 ui-monospace,monospace;letter-spacing:.18em;text-transform:uppercase;color:#6B645C">Order ${ESC(o.ref || '')} &middot; confirmed</p>
<h1 style="margin:0 0 10px;font-size:24px;line-height:1.2;font-weight:800">Thanks${first}.</h1>
<p style="margin:0 0 20px;font-size:15px;line-height:1.6;color:#4A443E">We roast every Wednesday. Yours is roasted <b style="color:#1A1815">${roastAfter(Date.now())}</b> and dispatched shortly after, fresh from that roast.</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">${items}</table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px">${sums}</table>
${per ? `<p style="margin:14px 0 0;font-size:14px;color:#4A443E">Then <b style="color:#1A1815">${money(per)} ${EVERY[sb.every]}</b>${sb.nextCharge ? ', next charged on ' + dateOf(sb.nextCharge) : ''}. Swap coffees, change how often, skip a delivery or cancel whenever you like.</p>
<p style="margin:16px 0 0"><a href="${manage}" style="display:inline-block;background:#1A1815;color:#F4F2EE;text-decoration:none;font-weight:600;font-size:14px;padding:12px 20px;border-radius:999px">Manage your subscription</a></p>` : ''}
${d.contribution ? `<p style="margin:20px 0 0;padding-top:14px;border-top:1px solid #E7E1D6;font-size:14px;line-height:1.55;color:#4A443E"><b style="color:#C2410C">${money(d.contribution)} to conservation</b>${partners ? ', through ' + partners : ''}.</p>` : ''}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:18px"><tr>
${o.address && o.address.length ? `<td valign="top" style="padding-right:12px;font-size:13px;line-height:1.55;color:#4A443E"><span style="font:600 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;color:#6B645C">Delivering to</span><br>${o.address.map(ESC).join('<br>')}</td>` : ''}
${pw ? `<td valign="top" style="font-size:13px;line-height:1.55;color:#4A443E"><span style="font:600 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;color:#6B645C">Paid with</span><br>${pw}</td>` : ''}
</tr></table>
<p style="margin:24px 0 0;font-size:13px;line-height:1.6;color:#6B645C">Questions? Reply to this email, quoting ${ESC(o.ref || 'your order number')}.${per ? ` <a href="${origin}/subscription-terms/" style="color:#6B645C">Subscription terms</a>.` : ''}</p>
<p style="margin:18px 0 0;font-size:12px;color:#8A837A">NoFilter Pte. Ltd., Singapore</p>
</td></tr></table></body></html>`;
  const text = [`Order ${o.ref} confirmed. Thanks${o.firstName ? ', ' + o.firstName : ''}.`, `Roasted ${roastAfter(Date.now())}, dispatched shortly after.`, '',
    ...(o.items || []).map(it => `${it.name}, ${it.size} x ${it.qty}${it.every ? ', ' + EVERY[it.every] : ''}: ${money(it.amount)}`),
    o.discount ? `Discount: -${money(o.discount)}` : null, `Delivery: ${o.delivery ? money(o.delivery) : 'Free'}`, `Total paid: ${money(o.total)}`,
    per ? `\nThen ${money(per)} ${EVERY[sb.every]}. Manage your subscription: ${manage}` : null,
    d.contribution ? `\n${money(d.contribution)} to conservation${partners ? ', through ' + (d.byPartner || []).map(p => (p.partner ? p.partner + ' in ' : '') + p.name).join('; ') : ''}.` : null,
    '', `Questions? Reply to this email, quoting ${o.ref}.`].filter(x => x !== null).join('\n');
  return { subject: `Your NoFilter order ${o.ref || ''}`.trim(), html, text };
}

function deskEmail(d, sessionId) {
  const o = d.order || {}, sb = d.subscription;
  const lines = [`New shop order ${o.ref}${sb && sb.every ? ' (subscription, ' + EVERY[sb.every] + ')' : ''}`, `Roast: ${roastAfter(Date.now())}`, '',
    ...(o.items || []).map(it => `${it.qty} x ${it.name}, ${it.size}${it.every ? ' (' + EVERY[it.every] + ')' : ''}`), '',
    `Total paid: ${money(o.total)} (delivery ${o.delivery ? money(o.delivery) : 'free'}${o.discount ? ', discount ' + money(o.discount) + (d.code ? ' ' + d.code : '') : ''})`,
    d.contribution ? `To conservation: ${money(d.contribution)} (${(d.byPartner || []).map(p => p.partner + ' ' + money(p.contribution)).join(', ')})` : null, '',
    'Deliver to:', ...(o.address || []), '', `Customer: ${o.firstName || ''} <${o.email || ''}>`, `Stripe: ${sessionId}`].filter(x => x !== null);
  return { subject: `Shop order ${o.ref}${sb && sb.every ? ' · subscription' : ''} · ${money(o.total)}`, text: lines.join('\n') };
}

exports.handler = async function (event) {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'POST only' };
  const SECRET = process.env.STRIPE_WEBHOOK_SECRET, KEY = process.env.RESEND_API_KEY, FROM = process.env.QUOTE_FROM;
  if (!SECRET || !KEY || !FROM) return { statusCode: 503, body: 'not configured' };
  const raw = event.isBase64Encoded ? Buffer.from(event.body || '', 'base64').toString('utf8') : (event.body || '');
  const h = event.headers || {};
  if (!verify(raw, h['stripe-signature'] || h['Stripe-Signature'], SECRET)) return { statusCode: 400, body: 'bad signature' };
  let ev; try { ev = JSON.parse(raw); } catch (e) { return { statusCode: 400, body: 'bad body' }; }
  const s = ev && ev.data && ev.data.object;
  if (ev.type !== 'checkout.session.completed' || !s || (s.metadata || {}).source !== 'website-shop' || s.payment_status !== 'paid') return { statusCode: 200, body: 'ignored' };

  const r = await summary.handler({ httpMethod: 'GET', queryStringParameters: { order: s.id } });
  if (r.statusCode !== 200) return { statusCode: 500, body: 'order not readable' };   // Stripe retries
  const d = JSON.parse(r.body);
  let origin = 'https://nofilter.sg';
  try { origin = new URL(s.success_url).origin; } catch (e) {}
  const send = (payload, key) => fetch('https://api.resend.com/emails', { method: 'POST',
    headers: { Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json', 'Idempotency-Key': key }, body: JSON.stringify(payload) });
  const desk = process.env.ORDERS_TO || process.env.QUOTE_TO || 'hello@nofilter.sg';
  const results = [];
  if (d.order && d.order.email) {
    const m = customerEmail(d, origin, s.id);
    results.push(await send({ from: FROM, to: [d.order.email], reply_to: desk, subject: m.subject, html: m.html, text: m.text }, 'shop-customer-' + s.id));
  }
  const k = deskEmail(d, s.id);
  results.push(await send({ from: FROM, to: [desk], reply_to: (d.order && d.order.email) || desk, subject: k.subject, text: k.text }, 'shop-desk-' + s.id));
  const bad = results.filter(x => !x.ok);
  if (bad.length) { console.error('shop-webhook: email not sent for', (d.order || {}).ref, bad.map(x => x.status).join(',')); return { statusCode: 500, body: 'email failed' }; }
  return { statusCode: 200, body: 'sent' };
};

exports._test = { verify, customerEmail, deskEmail, roastAfter };
