import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 104 · THE READER'S OWN RECORD ══════════════════════════════════════════
# Alex, 3 Sep, on the two emails a customer gets and the screen between them.
# The confirmation stops being a thank-you with a reference on it and becomes
# the record of what they chose — so the screen's promise ("we've emailed you
# a copy for your records") is true.
# What the record does NOT carry is volume. Alex: the cups adjustment "is just
# that a rough estimate primarily so they can see their possible NGO
# contribution at the price selected... it's only through discussion and
# actual experience that we determine their needs", and quoting it back "may
# unwittingly" put someone off a setup whose only fault was their own guess at
# a cup count. So the kilos, the coffee subtotal and the all-in monthly go;
# what stays is what is actually contracted — the price per kilo, the share,
# the top-up, the machines, and the servicing, plus the machine money, which
# is real and does not depend on how much coffee anyone drinks.
#   · servicing becomes its own field. It was never a discrete choice: on a
#     rental it is included, on a purchase it is the plan (svcYrs), year one
#     alone (svc1), or declined. One line per machine, in those words.
#   · machMonthly rides along, so the email can state the machine cost as a
#     fact rather than as a share of an estimate.

# ── servicing, per machine, in the reader's words ─────────────────────────
fix("""  var machMonthly = 0, capex = 0, units = 0, machLines = [], rentEquiv = 0, buyGaps = 0;
  MACHINES.forEach(function(m){
    var s = Q.m[m.k]; if(!s.q) return;
    units += s.q;
    if(s.mode === 'rental'){""",
    """  var machMonthly = 0, capex = 0, units = 0, machLines = [], rentEquiv = 0, buyGaps = 0;
  var svcLines = [];                                             /* block 104 */
  MACHINES.forEach(function(m){
    var s = Q.m[m.k]; if(!s.q) return;
    units += s.q;
    /* block 104 — servicing is not a control, it is the consequence of the
       mode and the options: stated here once, in the words the reader gets */
    svcLines.push(m.name + ' · ' + (s.mode === 'rental'
      ? 'included with the rental'
      : (s.svc ? (s.svcYrs || 1) + ' year' + ((s.svcYrs || 1) > 1 ? 's' : '') + ' of cover \\u00b7 parts, labour and breakdown'
               : (s.svc1 ? 'year one only' : 'not included'))));
    if(s.mode === 'rental'){""")

fix("""  return { kgTotal:kgTotal, coffee:coffee, band:band, contrib:contrib,
           bandPerKg:bandPerKg, topCents:topCents, topPerKg:topPerKg,
           machMonthly:machMonthly, capex:capex, units:units,""",
    """  return { kgTotal:kgTotal, coffee:coffee, band:band, contrib:contrib,
           bandPerKg:bandPerKg, topCents:topCents, topPerKg:topPerKg,
           machMonthly:machMonthly, capex:capex, units:units, svcLines:svcLines,   /* block 104 */""")

# ── the payload carries them ──────────────────────────────────────────────
fix("""          consPerKg: (c && c.bandPerKg != null) ? c.bandPerKg + (c.topPerKg || 0) : null,""",
    """          consPerKg: (c && c.bandPerKg != null) ? c.bandPerKg + (c.topPerKg || 0) : null,
          /* block 104 — servicing in its own right, and the machine money,
             which is a fact rather than a function of an estimated volume */
          servicing:  (c && c.svcLines) ? c.svcLines : [],
          machMonthly:(c && c.machMonthly != null) ? c.machMonthly : null,""")

# ── the screen ────────────────────────────────────────────────────────────
# Alex's copy. The offer block goes: the tasting choices are checkboxes on the
# form they just sent, so offering again is asking twice. The reference is on
# screen as well as in the email, so it can be quoted without opening an inbox.
fix("""      th.innerHTML = '<div class="q-thanks-mark">\\u2713</div>'
        + '<div class="q-thanks-title">Selections received.</div>'""",
    """      th.innerHTML = '<div class="q-thanks-mark">\\u2713</div>'
        + '<div class="q-thanks-kick">04 \\u00b7 Submission received</div>'   /* block 104 */
        + '<div class="q-thanks-title">Thank you.</div>'""")

lines = src.split("\n")
i = next(i for i, l in enumerate(lines) if "'<p class=\"q-thanks-body\">Thanks for taking the time to build out your setup. '" in l)
j = next(j for j in range(i, len(lines)) if "q-thanks-offer" in lines[j])
k = next(k for k in range(j, len(lines)) if lines[k].strip().startswith("+   '</div>'") or lines[k].strip() == "+ '</div>';")
body = """        /* block 104 — Alex's copy, 3 Sep. The email carries the same promise and
           the record itself; this states it and gets out of the way. */
        + '<p class="q-thanks-body">We\\u2019ve got your selections, and we\\u2019ve emailed you a copy '
        + 'for your records.</p>'
        + '<p class="q-thanks-body">We\\u2019ll review everything and come back to you with anything '
        + 'that needs confirming \\u2014 coffee to taste, a machine demo, or a few details about your '
        + 'space.</p>'
        + '<p class="q-thanks-body">For now, you\\u2019re done. We\\u2019ll take it from here.</p>'
        + '<div class="q-thanks-ref" id="qThanksRef" hidden></div>'"""
tail = lines[k].split("'</div>'", 1)[1]
lines[i:k+1] = [body + (";" if tail.strip().startswith(";") else "")]
src = "\n".join(lines)

CSS = r'''
/* ══ 104 · THE CONFIRMATION ═══════════════════════════════════════════════ */
.q-thanks-kick{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--signal);margin-bottom:10px}
.q-thanks-body + .q-thanks-body{margin-top:12px}
/* Alex, 3 Sep: "records should not be on a line by itself" — the browser
   balances the paragraph's last line rather than leaving one word on it */
.q-thanks-body{text-wrap:pretty}
/* and the reference reads: cream on the card, the number brighter */
.q-thanks-ref{margin-top:22px;padding:12px 16px;display:inline-block;color:rgba(244,239,226,.72);
  background:rgba(244,239,226,.07);border:1px solid rgba(244,239,226,.16);border-radius:6px;
  font-family:var(--mono);font-size:11.5px;letter-spacing:.14em;text-transform:uppercase}
.q-thanks-ref b{color:#F4EFE2;font-weight:600}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

# the reference is filled at reveal, not at construction: QREF lives in the
# console's own scope and the deck is built in another, so `typeof QREF` was
# false where the card is assembled and the line never printed. Here it is in
# scope, and the number is the one already on the sheet.
fix("""    settle.classList.add('q-sent');
    settle.appendChild(thanks);
    thanks.hidden = false;""",
    """    settle.classList.add('q-sent');
    /* block 104 */
    var tref = document.getElementById('qThanksRef');
    if(tref && typeof QREF === 'string' && QREF){
      tref.innerHTML = 'Your reference \\u00b7 <b>' + QREF + '</b>'; tref.hidden = false;
    }
    settle.appendChild(thanks);
    thanks.hidden = false;""")

# the tasting-offer block is gone (block 104), so the pass151 IIFE that removed
# it when a tasting had been ticked has nothing to act on. It self-guards, so
# it was harmless — but dead code that looks live is a trap for the next
# reader, and its reasoning is preserved in the patch history.
fix("""  /* answer what was actually ticked rather than re-pitching the offer */
  (function(){
    var offer = thanks && thanks.querySelector('.q-thanks-offer');
    if(!offer) return;""",
    """  /* block 104 — the offer panel itself is gone: the tasting choices are
     checkboxes on the form they just sent, so offering again asked twice.
     This block removed it when a tasting HAD been ticked; with no panel to
     remove it now returns on its first line, every time. */
  (function(){
    var offer = thanks && thanks.querySelector('.q-thanks-offer');
    if(!offer) return;""")

io.open(F, "w", encoding="utf-8").write(src)
print("the reader gets a record")
