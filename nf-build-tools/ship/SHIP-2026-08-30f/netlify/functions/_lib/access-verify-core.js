/* NoFilter — trade access, step 2: check a code the reader typed.
   28 Aug (pass163). Pair to access-request.js; read the long note at the top of
   that file for why nothing is stored.

   Recomputes the code from (secret, email, day bucket) and compares. Both the
   current bucket and the previous one are accepted, so a code issued at 23:59
   does not die sixty seconds later — without that, codes near a boundary would
   fail for no reason the reader could see.
   Practical validity is therefore between 24 and 48 hours (pass178).

   THREE THINGS THIS FILE DOES ON PURPOSE:

   1 · timingSafeEqual, not ===. A plain comparison returns faster the earlier it
       finds a difference, which leaks the code one character at a time to anyone
       patient enough to measure. The cost of doing it properly is one import.

   2 · a flat 350ms on EVERY answer, right or wrong. Two reasons. It puts the
       keyspace (160,000 since pass170) hours out of reach of a serial script,
       and — more
       subtly — an equal delay on success and failure means the response time
       tells an attacker nothing that the response body does not already say.

   3 · the same 'no' for every kind of failure. Wrong code, unknown address,
       expired window: all 401 'no'. Distinguishing them would confirm which
       addresses have asked for access, and that list is Alex's, not the
       internet's. */

const crypto = require('crypto');

const W1 = ['ORANGUTAN', 'SIAMANG', 'HOOLOCK', 'GIBBON', 'TIGER', 'TAPIR', 'RHINO', 'SUNBEAR',
            'HORNBILL', 'PANGOLIN', 'SEROW', 'BINTURONG', 'MUNTJAC', 'CLOUDED', 'GAUR', 'ELEPHANT'];
const W2 = ['RIDGE', 'EDGE', 'BASIN', 'GROVE', 'TRAIL', 'RIVER', 'STAND', 'CREST', 'HOLLOW', 'SLOPE'];

/* 28 Aug (pass178) — Alex: "30 mins is too short, let it be 24 hrs."
   The window is the BUCKET, and lengthening it is the safe way to do this. The
   tempting alternative — keep 30-minute buckets and accept the last 48 of them —
   would have put 48 live codes in a keyspace of 160,000 at once, which drops a
   scripted attack from about eight hours to under twenty minutes. Widening the
   bucket instead leaves exactly two codes live, as before, and the entropy
   untouched.
   The trade is that validity is now 24 to 48 hours rather than exactly 24:
   verify still accepts the previous bucket so a code issued at 23:59 does not die
   sixty seconds later. Erring long on an access code to a price list is the right
   side to err on. */
const WINDOW_MS = 24 * 60 * 60 * 1000;

/* 28 Aug (pass167): one word, no spaces — see the note in access-request.js.
   Nothing here needed to change for it. norm() already stripped everything that
   is not a letter or a digit from both sides, which is why a code typed with
   spaces and the same code typed without always compared equal. Kept identical
   to the issuing function on purpose: the two must agree exactly, and the
   cheapest way to guarantee that is for the code to be the same eight lines. */
function codeFor(secret, email, bucket) {
  const h = crypto.createHmac('sha256', secret).update(email + '|' + bucket).digest();
  const a = W1[h[0] % W1.length];
  const b = W2[h[1] % W2.length];
  /* pass170: three digits — see the note in access-request.js. These eight lines
     must stay byte-identical to the issuing function or every code fails, which
     is the entire reason they are duplicated rather than shared: two files that
     obviously match beat one import that quietly does not ship. */
  const n = String(((h[2] << 8) | h[3]) % 1000).padStart(3, '0');
  return a + b + n;
}

/* the reader types into a CRT that shows no spaces and does not care about case;
   both sides are flattened to letters and digits before anything is compared */
const norm = s => String(s == null ? '' : s).replace(/[^A-Za-z0-9]+/g, '').toUpperCase();

function same(a, b) {
  const x = Buffer.from(a), y = Buffer.from(b);
  if (x.length !== y.length) return false;
  return crypto.timingSafeEqual(x, y);
}

const wait = ms => new Promise(r => setTimeout(r, ms));

/* 7 Sep (block 114/115) — THE LADDER LIVES HERE, NOT IN THE PAGE.
   build-ship.mjs lifts RATES {SG,AE,UK: kg, bands, mach, cover, buyx} out of
   the master and writes the literal over the marker below, so the published
   HTML carries only the public reference figures and a valid code is the one
   way to receive the rest. A function's source is never sent to a browser.
   The marker is left null in the template on purpose: a build that fails to
   fill it is caught by build-ship, not by a customer with an empty builder. */
const RATES = /*NF_RATES*/null;

exports.handler = async function (event) {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'POST only' };

  const SECRET = process.env.ACCESS_SECRET || process.env.RESEND_API_KEY;
  if (!SECRET) return { statusCode: 503, body: 'access is not configured' };

  let p;
  try { p = JSON.parse(event.body || '{}'); } catch (e) { return { statusCode: 400, body: 'bad request' }; }

  const email = String(p.email || '').trim().toLowerCase();
  const typed = norm(p.code);

  await wait(350);

  const deny = { statusCode: 401, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ok: false }) };
  if (!email || !typed) return deny;

  const now = Date.now();
  const b = Math.floor(now / WINDOW_MS);
  for (const bucket of [b, b - 1]) {
    if (same(typed, norm(codeFor(SECRET, email, bucket)))) {
      return { statusCode: 200, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }, body: JSON.stringify({ ok: true, rates: RATES }) };
    }
  }
  return deny;
};
