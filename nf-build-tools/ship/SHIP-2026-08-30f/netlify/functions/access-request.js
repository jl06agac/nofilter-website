/* NoFilter — trade access, step 1: issue a code and email it.
   28 Aug (pass163). Replaces a code that was generated in the browser and printed
   on screen next to the button that accepted it.

   SET IN NETLIFY -> Project configuration -> Environment variables:

     ACCESS_SECRET    any long random string. The HMAC key the code is derived
                      from. If it is absent this falls back to RESEND_API_KEY so
                      the gate keeps working rather than failing shut on launch
                      day — but set it: reusing a provider key as a signing key
                      means rotating one forces the other.
     RESEND_API_KEY   re_...  sends both emails.
     QUOTE_FROM       verified Resend sender, e.g. "NoFilter <hello@nofilter.sg>".
     QUOTE_TO         where the lead notification goes. Defaults to hello@nofilter.sg.

   No npm dependencies — node:crypto and Node 18's global fetch, the same shape
   quote-confirm.js uses.

   ── WHY THE CODE IS NOT STORED ANYWHERE ──────────────────────────────────────
   There is no database and no blob store in this design, and that is deliberate
   rather than lazy. The code is a pure function of (email, 24-hour window,
   secret):

       HMAC-SHA256(secret, email + '|' + bucket)  ->  two words + three digits

   access-verify recomputes it from the same three inputs and compares. So the
   browser is never told the code, nothing has to be written down, nothing has to
   be cleaned up, and a cold start or a redeploy cannot lose a code someone is
   holding in their inbox. The trade-off is that the same address asking twice
   inside one window gets the same code back, which is a feature: a reader who
   loses the first email and asks again is not chasing two live codes.

   ── WHAT THIS GATE DOES AND DOES NOT STOP ───────────────────────────────────
   Stops: anyone who does not control the address they typed. The code exists
   only in that inbox and in this function.
   Does not stop: someone willing to script tens of thousands of guesses at
   access-verify. The keyspace is 16 x 10 x 1,000 = 160,000 (pass170) and verify
   sleeps 350ms on every answer, so a serial attack runs about fifteen hours and
   lights up the function log. That is proportionate to what is behind the door — wholesale
   per-kilo pricing — and it is honest to write down rather than imply otherwise. */

const crypto = require('crypto');

/* fauna of the four origins, then terrain. Kept identical to the words the
   browser used to generate, so the codes read the same as they always did. */
const W1 = ['ORANGUTAN', 'SIAMANG', 'HOOLOCK', 'GIBBON', 'TIGER', 'TAPIR', 'RHINO', 'SUNBEAR',
            'HORNBILL', 'PANGOLIN', 'SEROW', 'BINTURONG', 'MUNTJAC', 'CLOUDED', 'GAUR', 'ELEPHANT'];
const W2 = ['RIDGE', 'EDGE', 'BASIN', 'GROVE', 'TRAIL', 'RIVER', 'STAND', 'CREST', 'HOLLOW', 'SLOPE'];

/* mirrors the list in the page. The browser check is courtesy — fast feedback
   before a round trip — and this one is the check that counts, because anything
   the browser enforces can be edited by the person it is enforced against. */
const FREE = ('gmail.com googlemail.com yahoo.com yahoo.co.uk yahoo.com.sg ymail.com hotmail.com '
  + 'hotmail.co.uk outlook.com live.com msn.com icloud.com me.com mac.com aol.com proton.me '
  + 'protonmail.com pm.me gmx.com gmx.net mail.com yandex.com zoho.com fastmail.com hey.com '
  + 'tutanota.com qq.com 163.com 126.com naver.com daum.net hanmail.net rediffmail.com web.de '
  + 't-online.de orange.fr free.fr libero.it seznam.cz wp.pl o2.pl bigpond.com optusnet.com.au '
  + 'sky.com btinternet.com virginmedia.com comcast.net verizon.net att.net sbcglobal.net '
  + 'cox.net charter.net shaw.ca rogers.com telus.net singnet.com.sg pacific.net.sg starhub.net.sg '
  + 'emirates.net.ae eim.ae').split(' ');

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

function bucketOf(t) { return Math.floor(t / WINDOW_MS); }

/* 28 Aug (pass167) — ONE WORD, NO SPACES.
   Alex: "the spaces in between the words are confusing, when i type with a space
   it works, without a space also works, maybe passwords should just be all one
   word?"
   He is describing a code that looks like it has rules and does not: verify
   strips everything that is not a letter or a digit before comparing, so both
   forms always worked and the spaces only ever suggested a format that had to be
   got right. They are gone. The two words are still there — TAPIRBASIN7431 is
   the same keyspace as the spaced form and stays pronounceable — they simply
   stop pretending to be three separate things to type.
   (It was 1.6 million when this was written; pass170 cut the digits to three and
   the note below has the current figure.) */
function codeFor(secret, email, bucket) {
  const h = crypto.createHmac('sha256', secret).update(email + '|' + bucket).digest();
  const a = W1[h[0] % W1.length];
  const b = W2[h[1] % W2.length];
  /* 28 Aug (pass170): three digits, not four — Alex's call, and the cost is
     worth writing down rather than burying. The keyspace goes from 1.6 million
     to 160,000. Against the 350ms floor in access-verify that is about fifteen
     hours of uninterrupted scripted guessing rather than six days, and every one
     of those attempts is a logged function invocation. Still far beyond anyone
     idly curious about wholesale pricing, which is the threat this door is for.
     If the entropy is ever wanted back without adding a digit, the terrain list
     is the cheap lever: ten words to twenty doubles it. */
  const n = String(((h[2] << 8) | h[3]) % 1000).padStart(3, '0');
  return a + b + n;
}

const ESC = s => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/* 28 Aug (pass175) — Alex: "incredibly impersonal, can we change it and add our
   nofilter logo at least?"
   Fair. The first version was a code in a box from nobody, and a trade buyer's
   first direct contact with the company should not read like a password reset.
   What changed:
     · the real wordmark, hosted, at 440px for a 220px slot so it stays crisp on
       a retina screen. A PNG rather than the SVG on the CDN — Gmail strips SVG,
       which would have left an empty box exactly where the logo was supposed to
       be. Width and height are on the <img> because a mail client that blocks
       images by default should still lay the message out correctly.
     · the company they typed, said back to them. We asked for it; using it costs
       nothing and it is the difference between a broadcast and a reply.
     · what is actually behind the door, in one line. Nobody types a code to see
       a code.
     · a name at the bottom, and a reply that reaches it. reply_to is already set
       to the desk, so "just reply" is true rather than decorative.
   The dark code block stays. It is the one part that was working: unmissable,
   monospaced, and easy to select in one gesture. */
function html(code, company, first) {
  const hi = first ? `Hi ${ESC(first)},` : 'Hi there,';
  return `<!doctype html><html><body style="margin:0;background:#F4F2EE;padding:32px 16px;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;color:#1A1815">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;margin:0 auto">
      <tr><td style="padding-bottom:20px">
        <img src="https://nofilter-shared.netlify.app/nofilter-wordmark-email.png"
             width="220" height="44" alt="NoFilter"
             style="display:block;border:0;outline:none;text-decoration:none;width:220px;height:auto">
      </td></tr>
      <tr><td style="border-top:2px solid #EE4D17;padding-top:24px">
        <p style="margin:0 0 6px;font:600 11px/1 ui-monospace,monospace;letter-spacing:.2em;
           text-transform:uppercase;color:#EE4D17">Your access code</p>
        <h1 style="margin:0 0 16px;font-size:23px;line-height:1.25;font-weight:700">Your quote builder is ready.</h1>
        <p style="margin:0 0 14px;font-size:15px;line-height:1.65;color:#4A443E">${hi}</p>
        <p style="margin:0 0 22px;font-size:15px;line-height:1.65;color:#4A443E">
          Here&rsquo;s your code to open the NoFilter quote builder.</p>
        <p style="margin:0 0 18px;padding:18px 20px;background:#1A1815;border-radius:6px;
           font:700 24px/1.3 ui-monospace,monospace;letter-spacing:.14em;color:#F4EFE2;text-align:center">
          ${ESC(code)}</p>
        <p style="margin:0 0 22px;font-size:15px;line-height:1.65;color:#4A443E">
          Head back to the page you came from, click <b>Enter the code</b>, and type or paste this
          in. It&rsquo;ll keep working for the next 24 hours, so there&rsquo;s no rush.</p>
        <p style="margin:0 0 24px;font-size:15px;line-height:1.65;color:#4A443E">
          Once you&rsquo;re in, choose the coffees, machines and servicing that suit your space.
          You&rsquo;ll see your wholesale price, monthly cost and conservation contribution update live
          as you go. When you&rsquo;re happy with your setup, submit your choices and we&rsquo;ll come
          back to you to confirm everything.</p>
        <p style="margin:0 0 4px;font-size:15px;line-height:1.65;color:#4A443E">
          If you&rsquo;d rather talk anything through, just reply &mdash; it comes straight to me,
          and we can pen in a call or catch up in person.</p>
        <p style="margin:22px 0 0;font-size:15px;line-height:1.5;color:#1A1815"><b>Alex Clark</b><br>
          <span style="color:#8A837A">NoFilter &middot; Singapore &amp; UAE</span></p>
        <p style="margin:26px 0 0;padding-top:16px;border-top:1px solid #E0D8C6;
           font-size:12.5px;line-height:1.7;color:#8A837A">
          Didn't ask for this? Ignore it &mdash; nothing has been opened.</p>
      </td></tr>
    </table></body></html>`;
}

exports.handler = async function (event) {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'POST only' };

  const KEY = process.env.RESEND_API_KEY;
  const FROM = process.env.QUOTE_FROM;
  const SECRET = process.env.ACCESS_SECRET || KEY;
  if (!KEY || !FROM || !SECRET) return { statusCode: 503, body: 'access is not configured' };

  let p;
  try { p = JSON.parse(event.body || '{}'); } catch (e) { return { statusCode: 400, body: 'bad request' }; }

  const email = String(p.email || '').trim().toLowerCase();
  const company = String(p.company || '').trim().slice(0, 120);
  /* 28 Aug (pass176) — Alex: "email should say 'hi xyz'". The access form now
     asks. Only the first word is used for the greeting: people type "Alex Clark"
     and "Hi Alex" reads like a person wrote it, where "Hi Alex Clark" reads like
     a mail merge. Trimmed hard, because this goes into a subject-adjacent line
     and an unbounded string in an email template is somebody else's CVE. */
  const name = String(p.name || '').trim().slice(0, 80);
  const first = name.split(/\s+/)[0] || '';

  if (!email || email.length > 254 || !/^[^@\s]+@[^@\s.]+\.[^@\s]+$/.test(email)) {
    return { statusCode: 400, body: 'bad address' };
  }
  if (!company) return { statusCode: 400, body: 'company required' };
  if (FREE.indexOf(email.split('@')[1]) >= 0) {
    return { statusCode: 403, body: 'personal inbox' };
  }

  const code = codeFor(SECRET, email, bucketOf(Date.now()));

  const send = (payload) => fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  try {
    const r = await send({
      from: FROM, to: [email], reply_to: process.env.QUOTE_TO || 'hello@nofilter.sg',
      subject: 'Your NoFilter Access Code · ' + code,
      html: html(code, company, first),
      /* the plain-text part is not a formality — it is what a screen reader, a
         terminal client and Gmail's own preview line all read, so it says the
         same things in the same order rather than being a stripped stub */
      text: 'Your quote builder is ready.\n\n'
          + (first ? 'Hi ' + first + ',' : 'Hi there,') + '\n\n'
          + 'Here\'s your code to open the NoFilter quote builder.\n\n'
          + '    ' + code + '\n\n'
          + 'Head back to the page you came from, click "Enter the code", and type or\n'
          + "paste this in. It'll keep working for the next 24 hours, so there's no rush.\n\n"
          + "Once you're in, choose the coffees, machines and servicing that suit your\n"
          + "space. You'll see your wholesale price, monthly cost and conservation\n"
          + "contribution update live as you go. When you're happy with your setup,\n"
          + "submit your choices and we'll come back to you to confirm everything.\n\n"
          + "If you'd rather talk anything through, just reply — it comes straight to me,\n"
          + 'and we can pen in a call or catch up in person.\n\n'
          + 'Alex Clark\nNoFilter · Singapore & UAE\n\n'
          + "Didn't ask for this? Ignore it — nothing has been opened.",
    });
    if (!r.ok) return { statusCode: 502, body: 'send failed: ' + (await r.text()).slice(0, 200) };

    /* The lead notification is the half of this that was missing entirely — every
       trade enquiry until now stopped inside the browser and Alex never heard about
       it. Best-effort: it must never fail the reader's own email. */
    send({
      from: FROM, to: [process.env.QUOTE_TO || 'hello@nofilter.sg'], reply_to: email,
      subject: 'Trade Access · ' + (name ? name + ' · ' : '') + company,
      text: (name ? name : 'Someone') + ' asked for trade pricing.\n\n'
          + 'Name: ' + (name || '—') + '\n'
          + 'Company: ' + company + '\n'
          + 'Email: ' + email + '\n'
          + 'When: ' + new Date().toISOString() + '\n\n'
          + 'They have been sent a code and can open the builder themselves.',
    }).catch(() => {});

    return { statusCode: 200, body: 'sent' };
  } catch (e) {
    return { statusCode: 502, body: 'send error' };
  }
};
