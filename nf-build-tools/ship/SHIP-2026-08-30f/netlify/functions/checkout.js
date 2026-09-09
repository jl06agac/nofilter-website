/* NoFilter checkout — creates a Stripe Checkout Session from the cart.
   PRICES LIVE HERE, not in the page. Set in Netlify -> Site settings -> Environment:
     STRIPE_SECRET_KEY   sk_test_... to rehearse, sk_live_... to go live
     PRICE_BAG_1KG       unit amount in CENTS  [PLACEHOLDER default until Alex confirms]
     PRICE_BAG_250G      unit amount in CENTS  [PLACEHOLDER default until Alex confirms]
   No npm dependencies — talks to Stripe's REST API directly (Node 18+ fetch). */
exports.handler = async function(event){
  if(event.httpMethod !== 'POST') return { statusCode: 405, body: 'POST only' };
  const KEY = process.env.STRIPE_SECRET_KEY;
  if(!KEY) return { statusCode: 503, body: 'payments not configured' };
  let lines;
  try { lines = JSON.parse(event.body).lines; } catch(e){ return { statusCode: 400, body: 'bad request' }; }
  if(!Array.isArray(lines) || !lines.length || lines.length > 20) return { statusCode: 400, body: 'bad cart' };

  const P1KG = parseInt(process.env.PRICE_BAG_1KG  || '7200', 10);
  const P250 = parseInt(process.env.PRICE_BAG_250G || '2400', 10);
  const origin = (event.headers && (event.headers.origin || ('https://' + event.headers.host))) || '';

  const form = new URLSearchParams();
  form.set('mode', 'payment');
  form.set('success_url', origin + '/?paid=1#shop');
  form.set('cancel_url',  origin + '/#shop');
  lines.forEach(function(l, i){
    const qty = Math.max(1, Math.min(99, parseInt(l.qty, 10) || 1));
    const is250 = String(l.size || '').indexOf('250') >= 0;
    const name = String(l.name || 'NoFilter Coffee').slice(0, 60) + ' - ' + (is250 ? '250g' : '1kg');
    form.set('line_items[' + i + '][quantity]', String(qty));
    form.set('line_items[' + i + '][price_data][currency]', 'sgd');
    form.set('line_items[' + i + '][price_data][unit_amount]', String(is250 ? P250 : P1KG));
    form.set('line_items[' + i + '][price_data][product_data][name]', name);
  });
  const res = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString()
  });
  const data = await res.json();
  if(!res.ok || !data.url) return { statusCode: 502, body: 'stripe error' };
  return { statusCode: 200, headers: {'Content-Type':'application/json'}, body: JSON.stringify({ url: data.url }) };
};
