import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the one-year rung is gone; cover starts at two ─────────────────────
subs.append((
"""        buyx:{ cooler:800, install:300, svcPlan:{1:1250,2:3000,3:4300},""",
"""        buyx:{ cooler:800, install:300, svcPlan:{2:3000,3:4300},"""))
subs.append((
"""        buyx:{ cooler:2108, install:790, svcPlan:{1:3293,2:7904,3:11329},""",
"""        buyx:{ cooler:2108, install:790, svcPlan:{2:7904,3:11329},"""))

subs.append((
"""function svcPlanCost(x, yrs){
  var y = Math.max(1, Math.min(3, yrs | 0));""",
"""/* ── 1 Sep 2026 · THE ONE-YEAR PLAN IS WITHDRAWN ─────────────────────────
   Alex: "twice annual coffee machine calibration should also be included
   regardless of plan selected." That one sentence deletes the one-year rung,
   and it is worth writing down why rather than just removing it.

   The one-year plan existed because, per RATE-CARD §3, "the manufacturer
   warranty still carries parts, so it buys two scheduled visits and nothing
   else." Two scheduled visits WAS the plan. Once calibration twice a year comes
   with every machine, a one-year plan at 1,250 is charging for something the
   buyer already has — and a client who works that out in a meeting has learned
   something about the whole card, not just this line.

   So cover now starts at two years, and the ladder is a real choice: take cover
   or don't. The floor loses 750 of gross on a rung that was never the point;
   what it buys is a card that does not have to be defended. */
function svcPlanCost(x, yrs){
  var y = Math.max(2, Math.min(3, yrs | 0));   /* cover starts at 2 */"""))

# default svcYrs 1 -> 2
subs.append((
"""  m: { cm2:{q:0,mode:'rental',term:36,svcYrs:1,cooler:true,svc:true,wrap:true,counter:true},
       cm5:{q:0,mode:'rental',term:36,svcYrs:1,cooler:true,svc:true,wrap:true,counter:true},
       cm6:{q:0,mode:'rental',term:36,svcYrs:1,cooler:true,svc:true,wrap:true,counter:true},
       cm8:{q:0,mode:'rental',term:36,svcYrs:1,cooler:true,svc:true,wrap:true,counter:true} }""",
"""  /* svcYrs starts at 2 because 2 is now the shortest plan there is */
  m: { cm2:{q:0,mode:'rental',term:36,svcYrs:2,cooler:true,svc:true,wrap:true,counter:true},
       cm5:{q:0,mode:'rental',term:36,svcYrs:2,cooler:true,svc:true,wrap:true,counter:true},
       cm6:{q:0,mode:'rental',term:36,svcYrs:2,cooler:true,svc:true,wrap:true,counter:true},
       cm8:{q:0,mode:'rental',term:36,svcYrs:2,cooler:true,svc:true,wrap:true,counter:true} }"""))

# ── 2 · the dossier's rungs: No cover / 2 years / 3 years ──────────────────
subs.append((
"""    var COVROWS = {
      1:['Two scheduled visits a year','Parts under manufacturer warranty'],
      2:['Parts &amp; breakdown cover','Three scheduled visits a year','Wrap + impact counter free'],
      3:['Parts &amp; breakdown cover','Three scheduled visits a year','Wrap + impact counter free']
    };""",
"""    /* 0 is a real tile now, not a text link. Alex asked "what's the cover
       message about?" of the old "Decline cover" line, and the honest answer was
       that declining is a legitimate choice dressed up as a footnote. It is a
       column like the others, it states its price (nothing) and it states what
       you still get — which, since calibration became universal, is no longer
       nothing. That also removes the trap the withdrawn one-year plan created:
       a reader can see for themselves that the free column already includes the
       visits, so the paid columns have to be selling something else. */
    var COVROWS = {
      0:['Twice-yearly calibration, included','Parts under manufacturer warranty, year one'],
      2:['Parts &amp; breakdown cover','Three scheduled visits a year','Wrap + impact counter free'],
      3:['Parts &amp; breakdown cover','Three scheduled visits a year','Wrap + impact counter free']
    };"""))

subs.append((
"""    var rung = function(n){
      var t = svcPlanCost(x, n), lit = on && yrs === n;
      return '<button type="button" class="nfbd-cov' + (lit ? ' is-on' : '') +
        '" data-nfbd-yrs="' + n + '" aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (n === 2 ? '<span class="rec">Recommended</span>' : '') +
        '<span class="tick" aria-hidden="true"></span>' +
        '<span class="yr">' + n + (n === 1 ? ' year' : ' years') + '</span>' +
        '<p class="pr">' + money(t) + '</p>' +
        '<span class="pm">' + CUR() + '&middot; ' + money0(t / (12 * n)) + ' a month</span>' +
        '<ul>' + COVROWS[n].map(function(r){ return '<li>' + r + '</li>'; }).join('') + '</ul>' +
      '</button>';
    };""",
"""    var rung = function(n){
      var none = (n === 0);
      var t = none ? 0 : svcPlanCost(x, n);
      var lit = none ? !on : (on && yrs === n);
      return '<button type="button" class="nfbd-cov' + (lit ? ' is-on' : '') + (none ? ' is-none' : '') +
        '" data-nfbd-yrs="' + n + '" aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (n === 2 ? '<span class="rec">Recommended</span>' : '') +
        '<span class="tick" aria-hidden="true"></span>' +
        '<span class="yr">' + (none ? 'No cover' : n + ' years') + '</span>' +
        '<p class="pr">' + (none ? 'Nothing' : money(t)) + '</p>' +
        '<span class="pm">' + (none ? 'Pay as you go' : CUR() + '&middot; ' + money0(t / (12 * n)) + ' a month') + '</span>' +
        '<ul>' + COVROWS[n].map(function(r){ return '<li>' + r + '</li>'; }).join('') + '</ul>' +
      '</button>';
    };"""))

subs.append((
"""          '<div><div class="nfbd-secthd"><p class="nfbd-sect">Choose how long it is covered</p>' +
            (on ? '<button type="button" class="nfbd-decline" data-nfbd-yrs="0">Decline cover</button>' : '') +
            '</div><div class="nfbd-covs">' + rung(1) + rung(2) + rung(3) + '</div></div>' +""",
"""          '<div><div class="nfbd-secthd"><p class="nfbd-sect">Choose how long it is covered</p>' +
            '<span class="nfbd-always">Calibration twice a year is included on every machine</span>' +
            '</div><div class="nfbd-covs">' + rung(0) + rung(2) + rung(3) + '</div></div>' +"""))

# ── 3 · calibration is stated on the card's own list too, in BOTH modes ────
subs.append((
"""        { k:'install', nm:'Delivery &amp; installation', fixed:true, buy:x.install },""",
"""        { k:'install', nm:'Delivery &amp; installation', fixed:true, buy:x.install },
        /* 1 Sep — universal, and it belongs on the list in both modes because it
           is true in both. On a purchase it is the one line that is free whether
           or not any plan is taken, which is exactly why it has to be visible on
           the resting card and not only inside the cover panel. */
        { k:'calib',  nm:'Calibration, twice a year', fixed:true, buy:0,
          sub:'included, every machine' },"""))

# ── 4 · the card's own in-card rung row, which still asked for a 1-year price ──
subs.append((
"""          row += '<div class="qi-yrs" role="group" aria-label="Servicing plan length">' +
            rung(1) + rung(2) + rung(3) + '</div>';""",
"""          /* 1 Sep — 1 is gone here too. This sub-row is inside .q-eq-incl, which
             block 23 hides entirely on a purchase, so it renders nowhere today —
             but it would have asked svcPlanCost for a one-year price that no
             longer exists and drawn a "1 yr" button quoting the two-year figure.
             Dead code that is WRONG is worse than dead code. */
          row += '<div class="qi-yrs" role="group" aria-label="Servicing plan length">' +
            rung(2) + rung(3) + '</div>';"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = r'''
/* ── 27 · THE "NO COVER" RUNG AND THE UNIVERSAL CALIBRATION LINE ──────────
   Declining is a column now rather than a link in the heading. It is styled as
   a peer of the paid rungs but quieter: same box, same tick, dimmed figure —
   so it reads as a choice with a consequence, not as an opt-out hidden in the
   furniture. Lit, it inverts like the others; nothing here depends on hue. */
#nfConsoleWrap .nfbd-cov.is-none .pr{font-family:var(--body,sans-serif);font-weight:600;
  font-size:17px;letter-spacing:0;opacity:.75;}
#nfConsoleWrap .nfbd-cov.is-none:not(.is-on){border-style:dashed;}
#nfConsoleWrap .nfbd-always{font-family:var(--body,sans-serif);font-size:11.5px;
  color:rgba(255,232,195,.7);white-space:nowrap;}
@media(max-width:1180px){#nfConsoleWrap .nfbd-always{display:none;}}
/* a fixed row that costs nothing prints no figure — "0.00" beside a line that
   says "included" is noise, and the rider already carries the meaning */
#nfConsoleWrap .qi.is-fixed .qi-v:empty{display:none;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("calibration + two-rung ladder applied")
