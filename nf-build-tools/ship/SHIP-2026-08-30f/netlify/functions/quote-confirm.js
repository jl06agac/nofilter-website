/* NoFilter — quote confirmation email.
   Sends the reader the same message the page shows them, and copies the desk.

   SET THESE IN NETLIFY -> Site settings -> Environment variables.
   Alex sets them; they are never held anywhere in this repo.

     RESEND_API_KEY   re_...   from resend.com. Without it this function replies
                               503 and the page carries on as if nothing happened —
                               the reader still sees their confirmation.
     QUOTE_FROM       e.g. "NoFilter <hello@nofilter.sg>". MUST be a sender on a
                      domain verified in Resend, or the API rejects it.
     QUOTE_TO         optional. Internal copy of every enquiry.
                      Defaults to hello@nofilter.sg.

   No npm dependencies — Resend's REST API over Node 18's built-in fetch, the same
   shape checkout.js uses for Stripe. Swapping provider means changing one URL and
   one body; nothing else in the file is Resend-specific.

   WHY A FUNCTION AND NOT A NETLIFY FORM: Netlify's form notifications email a
   fixed address when a submission arrives. They do not reply to the person who
   submitted, which is the whole of what was asked for here. */

const ESC = s => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/* 3 Sep — this was a thank-you with a reference number on it, which made the
   screen's promise ("we've emailed you a copy for your records") untrue: there
   was no copy in it. It is now the record. Alex set what belongs in one and
   what does not: the price per kilo, the share, the top-up, the machines and
   the servicing are what is actually contracted, and they stay; the kilos, the
   coffee subtotal and the all-in monthly go, because volume here is a rough
   estimate the reader made to see a plausible contribution — "it's only
   through discussion and actual experience that we determine their needs" —
   and quoting it back can put someone off a setup whose only fault was their
   own guess at a cup count. The machine money survives that cut: it is a fact
   and it does not move with how much coffee anyone drinks. */
const HEAD = "Here's what you chose.";
const OPEN = "Thanks for putting your setup together. We've got everything you submitted " +
             "below and will review it from here.";
const CLOSE1 = "If there's anything we need to confirm — coffee to taste, a machine demo, " +
               "or a few details about your space — we'll come back to you directly.";
const CLOSE2 = "For now, there's nothing else you need to do.";
const CLOSE3 = "Any questions in the meantime, just reply to this email — it comes straight to me.";

/* the figures, formatted once for both bodies. A row with no value never
   prints: a purchase has no rental term, a setup with no top-up should not be
   told "none", and a rental has no capital line. */
function rowsOf(p) {
  const mk = (v) => `${p.market || ''} ${Number(v).toLocaleString(undefined,
                      { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`.trim();
  const whole = (v) => `${p.market || ''} ${Math.round(Number(v)).toLocaleString()}`.trim();
  const pct = (r) => String(+(Number(r) * 100).toFixed(2));
  /* the per-origin kilos come off the names — picking an origin opens it at
     5 kg/mo, so an untouched default would read back as though it were asked
     for (pass168, and the same reasoning that takes volume out entirely) */
  const origins = (a) => (Array.isArray(a) && a.length
    ? a.map(x => String(x).replace(/\s*·\s*\d+(\.\d+)?\s*kg\s*$/i, '').trim())
    : []);
  return [
    ['Coffee', origins(p.coffee)],
    ['Machines', Array.isArray(p.machines) ? p.machines.filter(x => !/^[+·]|DECLINED|baseline|callout/i.test(String(x))) : []],
    ['Servicing', Array.isArray(p.servicing) ? p.servicing : []],
    ['Coffee price', p.price != null ? [mk(p.price) + ' / kg'] : []],
    ['Conservation share', (p.rate != null && p.price != null)
      ? [pct(p.rate) + '% of the price · ' + mk(p.price * p.rate) + ' / kg'] : []],
    ['Optional top-up', Number(p.topUpKg)
      ? [mk(p.topUpKg) + ' / kg (100% to the NGO partners)'] : []],
    ['Machines & servicing', Number(p.machMonthly)
      ? [whole(p.machMonthly) + ' / month'] : []],
    ['One-time capital', Number(p.capex) ? [whole(p.capex)] : []],
  ].filter(([, v]) => v.length);
}

/* 28 Aug (pass175, moved here by pass185): the real wordmark, matching the
   access-code email. These two are the only messages a customer ever gets from
   us and they were set differently — one letterspaced type, one nothing. A PNG,
   not the CDN's SVG: Gmail strips SVG and would leave a hole exactly where the
   logo belongs. width/height are on the <img> so a client with images switched
   off still lays the message out correctly.

   This note used to sit inside the template as an HTML comment, which meant it
   was mailed to every customer along with their confirmation. Nothing strips
   comments out here — that only happens to index.html, in the build. Anything
   written inside these template literals is something a stranger reads. */
function html(p, ref) {
  const first = String(p.name || '').trim().split(/\s+/)[0] || '';
  const hi = /^[A-Za-z][A-Za-z'\u2019-]+$/.test(first) ? `Hi ${ESC(first)},` : 'Hi there,';
  const rows = rowsOf(p).map(([k, vals]) => `
        <tr>
          <td style="padding:9px 14px 9px 0;vertical-align:top;white-space:nowrap;
              font:600 11px/1.5 ui-monospace,monospace;letter-spacing:.12em;
              text-transform:uppercase;color:#8A837A">${ESC(k)}</td>
          <td style="padding:9px 0;vertical-align:top;font-size:15px;line-height:1.55;color:#1A1815">
            ${vals.map(v => ESC(v)).join('<br>')}</td>
        </tr>`).join('');
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
           text-transform:uppercase;color:#EE4D17">Your setup</p>
        <h1 style="margin:0 0 16px;font-size:23px;line-height:1.25;font-weight:700">${ESC(HEAD)}</h1>
        <p style="margin:0 0 14px;font-size:15px;line-height:1.65;color:#4A443E">${hi}</p>
        <p style="margin:0 0 22px;font-size:15px;line-height:1.65;color:#4A443E">${ESC(OPEN)}</p>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
               style="margin:0 0 22px;border-top:1px solid #E0D8C6;border-bottom:1px solid #E0D8C6">${rows}
        </table>
        ${ref ? `<p style="margin:0 0 22px;padding:12px 16px;background:#EDE7DA;border-radius:6px;
          font:12px/1.6 ui-monospace,monospace;letter-spacing:.1em;color:#4A443E">
          YOUR REFERENCE &middot; <b>${ESC(ref)}</b></p>` : ''}
        <p style="margin:0 0 14px;font-size:15px;line-height:1.65;color:#4A443E">${ESC(CLOSE1)}</p>
        <p style="margin:0 0 14px;font-size:15px;line-height:1.65;color:#4A443E">${ESC(CLOSE2)}</p>
        <p style="margin:0 0 4px;font-size:15px;line-height:1.65;color:#4A443E">${ESC(CLOSE3)}</p>
        <p style="margin:22px 0 0;font-size:15px;line-height:1.5;color:#1A1815"><b>Alex Clark</b><br>
          <span style="color:#8A837A">NoFilter &middot; Singapore &amp; UAE</span></p>
      </td></tr>
    </table></body></html>`;
}

function text(p, ref) {
  /* pass175: kept in step with the HTML above, and signed the same way. This is
     what a screen reader and Gmail's preview line actually read. */
  const first = String(p.name || '').trim().split(/\s+/)[0] || '';
  const hi = /^[A-Za-z][A-Za-z'\u2019-]+$/.test(first) ? 'Hi ' + first + ',' : 'Hi there,';
  const rows = rowsOf(p).map(([k, vals]) => k + ':\n  ' + vals.join('\n  ')).join('\n\n');
  return HEAD + '\n\n' + hi + '\n\n' + OPEN + '\n\n' + rows +
         (ref ? '\n\nYour reference: ' + ref : '') +
         '\n\n' + CLOSE1 + '\n\n' + CLOSE2 + '\n\n' + CLOSE3 +
         '\n\nAlex Clark\nNoFilter · Singapore & UAE';
}

exports.handler = async function (event) {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'POST only' };

  const KEY  = process.env.RESEND_API_KEY;
  const FROM = process.env.QUOTE_FROM;
  /* 503 rather than 500: nothing is broken, it is simply not configured yet. The
     page treats any non-200 as "carry on" — the reader still gets their
     confirmation on screen, they just do not get the email. */
  if (!KEY || !FROM) return { statusCode: 503, body: 'email not configured' };

  let p;
  try { p = JSON.parse(event.body || '{}'); } catch (e) { return { statusCode: 400, body: 'bad request' }; }

  const to = String(p.email || '').trim();
  /* deliberately permissive: this is a confirmation, not an auth flow, and a
     regex strict enough to be worth anything rejects valid addresses */
  if (!to || to.length > 254 || !/^[^@\s]+@[^@\s.]+\.[^@\s]+$/.test(to)) {
    return { statusCode: 400, body: 'bad address' };
  }
  const ref = String(p.ref || '').slice(0, 40);

  const send = (payload) => fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  try {
    const r = await send({
      from: FROM, to: [to], reply_to: process.env.QUOTE_TO || 'hello@nofilter.sg',
      subject: ref ? `Your NoFilter Setup · ${ref}` : 'Your NoFilter Setup',
      html: html(p, ref), text: text(p, ref),
    });
    if (!r.ok) return { statusCode: 502, body: 'send failed: ' + (await r.text()).slice(0, 200) };

    /* the internal copy is best-effort and must never fail the reader's email */
    const desk = process.env.QUOTE_TO || 'hello@nofilter.sg';
    /* 28 Aug (pass157) — the order first, the contact second. This listed only
       who they were, which tells you a lead exists and nothing about how to
       answer it. The money and the selections decide how fast it gets picked up,
       so they go at the top where they are read. */
    /* a zero is not a fact worth a line. capex is 0 on most quotes — no capital
       outlay — and "One-time capital: SGD 0" is noise in an email someone scans
       in ten seconds. Falsy numbers drop the row entirely via the filter below. */
    const money = (v) => (!Number(v) ? '' : `${p.market || ''} ${Number(v).toLocaleString()}`.trim());
    /* pass263 — money() drops the pence: "SGD 229.5" went out in a real enquiry.
       Anything stated per kilo, and any conservation figure, gets two decimals. */
    const n2  = (v) => Number(v).toLocaleString(undefined,
                        { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const cur = (v) => `${p.market || ''} ${n2(v)}`.trim();
    const perKg = (v) => (v == null || !isFinite(Number(v)) ? '' : `${cur(v)} / kg`);
    /* 5, 7.5 and 10 stay clean; a ramped rate lands on a quarter point (pass258) */
    const pct = (r) => String(+(Number(r) * 100).toFixed(2));
    const list  = (a) => (Array.isArray(a) && a.length ? a.join('\n  ') : '');
    /* 28 Aug (pass168) — the per-origin kilos come out of the email.
       Alex: "Coffee: Gayo Lues · 5 kg — a particular quantity which shouldnt be
       allowed." He is right, and the reason is that 5 kg is OURS: picking an
       origin opens it at 5 kg/mo and the stepper tunes it from there, so a reader
       who picks Gayo Lues and never touches the stepper gets our default quoted
       back at them as though they had asked for it. Origins are listed by name;
       total volume stays, once, and says what it is.
       On screen the per-origin figure is untouched — there it is a live control
       being operated, which is not the same thing as a number in a message. */
    const origins = (a) => (Array.isArray(a) && a.length
      ? a.map(x => String(x).replace(/\s*·\s*\d+(\.\d+)?\s*kg\s*$/i, '').trim()).join('\n  ')
      : '');
    const rows = [
      ['Coffee',            origins(p.coffee)],
      ['Machines',          list(p.machines)],
      /* pass263 — the chosen figures first, the derived ones after. Alex, on a
         live enquiry: "i need to know what per kg coffee price they chose and
         what top up per kg they chose, one all in figure isnt great." Price and
         top-up are what the reader set and what goes on the contract; the
         monthly total is those two multiplied by a volume this email itself
         labels an estimate. */
      ['Coffee price',      perKg(p.price)],
      ['Contribution',      (p.rate != null && p.price != null)
        ? pct(p.rate) + '% of the price  ·  ' + perKg(p.price * p.rate) : ''],
      ['Optional top-up',   Number(p.topUpKg)
        ? perKg(p.topUpKg) + '  (100% to the NGO partners)' : 'none'],
      ['To conservation',   Number(p.consPerKg)
        ? perKg(p.consPerKg) + (Number(p.contrib)
            ? '  ·  ' + cur(Number(p.contrib) + (Number(p.topUpMo) || 0)) + ' / mo' : '')
        : money(p.contrib)],
      ['Monthly total',     money(p.total)],
      ['One-time capital',  money(p.capex)],
      /* 28 Aug (pass171) — the figure AND its basis, on one line.
         pass168 marked this "(indicative)", which was honest and useless: it told
         the reader not to trust the number without telling them how to check it.
         The chain is short enough to print, so it gets printed. */
      /* 28 Aug (pass201) — the basis is cups a year now, not headcount. The
         quote builder's headcount slider is gone: it asked for the same
         quantity as the ledger's cups slider and the two never agreed, so the
         reader states cups and the kilos follow from the one figure. */
      /* block 109 (3 Sep): this is the cups-a-year slider the reader set on 3C,
         with the kilos derived from it — not the nominal 5 kg a pick used to
         carry. Labelled as theirs, because that is what it is: a rough figure
         to see a contribution against, not a commitment. */
      ['Coffee volume · their estimate', p.kg
        ? Math.round(p.kg) + ' kg / mo'
          + (p.cupsY ? '  (' + Number(p.cupsY).toLocaleString() + ' cups a year at 18 g a cup)' : '')
        : ''],
      /* pass168 — their own words, above the contact block. A note asking about a
         conference or a staffed cart decides how the enquiry gets answered, so it
         is not going underneath the headcount. */
      ['Their note',        p.notes ? String(p.notes).slice(0, 1200) : ''],
      ['—', '—'],
      ['Name', p.name], ['Company', p.company], ['Email', to], ['Phone', p.phone],
      /* pass201: the Headcount row is gone. It carried who.size, which is now
         cups a year — and the Coffee volume line above already states that
         figure with its basis, so the row was the same number twice. */
      ['Market', p.market], ['Reference', ref],
      ['Tasting · showroom', p.tasteShow ? 'yes' : ''], ['Tasting · on site', p.tasteSite ? 'yes' : ''],
    ].filter(([, v]) => v).map(([k, v]) => (k === '—' ? '' : `${k}: ${v}`)).join('\n');
    await send({
      from: FROM, to: [desk], reply_to: to,
      /* 28 Aug (pass157): was `${p.company || p.name || to}` — an OR, so it showed
         the company or the person but never both. Alex asked for both, and in a
         notification list the pair is what makes a subject scannable: you know
         who it is and which account before opening anything. */
      subject: [
        'Quote Enquiry',
        p.company || null,
        p.name || null,
        (!p.company && !p.name) ? to : null,
        ref || null,
      ].filter(Boolean).join(' · '),
      text: rows,
    }).catch(() => {});

    return { statusCode: 200, body: 'sent' };
  } catch (e) {
    return { statusCode: 502, body: 'send error' };
  }
};
