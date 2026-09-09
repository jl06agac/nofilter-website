import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the plan is priced on the years NoFilter actually carries risk ─────
subs.append((
"""        buyx:{ cooler:800, install:300, svcPlan:{2:3000,3:4300},""",
"""        /* svcPlan — repriced 1 Sep 2026. The key is now "covered to N years of
           ownership", not "N years of plan", and the money is the risk NoFilter
           carries: nothing in year one, 1,000 a year after. 2 => cover to 24
           months (one real year, Y2). 3 => cover to 36 months (Y2 and Y3). */
        buyx:{ cooler:800, install:300, svcPlan:{2:2000,3:3600},"""))
subs.append((
"""        buyx:{ cooler:2108, install:790, svcPlan:{2:7904,3:11329},""",
"""        buyx:{ cooler:2108, install:790, svcPlan:{2:5269,3:9485},"""))

# ── 2 · the extras reward moves to the top rung alone ──────────────────────
subs.append((
"""function wrapCost(x, cfg){ return (cfg.svc && (cfg.svcYrs || 1) >= 2) ? 0 : x.wrap; }""",
"""/* 1 Sep — THE REWARD MOVES TO THE TOP RUNG ALONE. It sat at >= 2 when the
   two-year plan was 3,000; against a cover-to-24 plan of 2,000 it would be
   giving away 2,000 of hardware on a 2,000 sale, which is not a reward, it is
   the whole price. Both extras now attach to cover-to-36 only, and that is what
   keeps the inversion working: cover-to-24 WITH the extras bought is 13,100,
   cover-to-36 with them free is 12,700 — so 400 buys a second year of cover and
   the buyer is still ahead. */
function wrapCost(x, cfg){ return (cfg.svc && (cfg.svcYrs || 2) >= 3) ? 0 : x.wrap; }"""))
subs.append((
"""function counterCost(x, cfg){ return (cfg.svc && (cfg.svcYrs || 1) >= 2) ? 0 : x.counter; }""",
"""function counterCost(x, cfg){ return (cfg.svc && (cfg.svcYrs || 2) >= 3) ? 0 : x.counter; }"""))
subs.append((
"""        if(n >= 2){ cfg.wrap = true; cfg.counter = true; }""",
"""        if(n >= 3){ cfg.wrap = true; cfg.counter = true; }"""))

# ── 3 · the rungs say what each one really is ──────────────────────────────
subs.append((
"""    var COVROWS = {
      0:['Twice-yearly calibration, included','Parts under manufacturer warranty, year one'],
      2:['Parts &amp; breakdown cover','Three scheduled visits a year','Wrap + impact counter free'],
      3:['Parts &amp; breakdown cover','Three scheduled visits a year','Wrap + impact counter free']
    };""",
"""    /* ── 1 Sep 2026 · THE LADDER IS ABOUT WHO CARRIES THE RISK ──────────────
       Alex: "Y1 warranty is there, my liability is v little ... Y2 is where my
       risk goes up ... full coverage/insurance on parts is a big win for clients
       as it lowers their risk of machine failure and them being billed for it."

       That sentence is the product. In year one the manufacturer carries parts,
       labour and breakdowns, so NoFilter carries the servicing instead and does
       not charge for it — two maintenance visits, free, with calibration done on
       the same trips. From month thirteen the risk transfers, and THAT is what
       the plan sells: not a schedule, an insurance.

       The free column was briefly labelled "No cover", which was both alarming
       and untrue — Alex: "you can't leave it entirely unserviced and only respond
       in the event of a breakdown." Quite. It is serviced; it simply is not yet
       insured by us, because it does not need to be. */
    var COVROWS = {
      0:['Two maintenance visits, free','Parts &amp; labour under manufacturer warranty'],
      2:['Every part and breakdown insured, from month 13','Three scheduled visits a year'],
      3:['Every part and breakdown insured, from month 13','Three scheduled visits a year','Wrap + impact counter free']
    };"""))

subs.append((
"""      var none = (n === 0);
      var t = none ? 0 : svcPlanCost(x, n);
      var lit = none ? !on : (on && yrs === n);
      return '<button type="button" class="nfbd-cov' + (lit ? ' is-on' : '') + (none ? ' is-none' : '') +
        '" data-nfbd-yrs="' + n + '" aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (n === 2 ? '<span class="rec">Recommended</span>' : '') +
        '<span class="tick" aria-hidden="true"></span>' +
        '<span class="yr">' + (none ? 'No cover' : n + ' years') + '</span>' +
        '<p class="pr">' + (none ? 'Nothing' : money(t)) + '</p>' +
        '<span class="pm">' + (none ? 'Pay as you go' : CUR() + '&middot; ' + money0(t / (12 * n)) + ' a month') + '</span>' +""",
"""      var none = (n === 0);
      var t = none ? 0 : svcPlanCost(x, n);
      var lit = none ? !on : (on && yrs === n);
      /* the sub-line is PER YEAR OF COVER, not per month. Per month was the right
         unit while year one was inside the plan and the ladder could get cheaper
         monthly as it lengthened; priced on real cover it cannot — two years of
         cover is genuinely more money than one. Per covered year restores an
         honest discount that runs the right way: 2,000 then 1,800. */
      var covYears = n - 1;                    /* cover to 24 mo = 1 year, to 36 = 2 */
      return '<button type="button" class="nfbd-cov' + (lit ? ' is-on' : '') + (none ? ' is-none' : '') +
        '" data-nfbd-yrs="' + n + '" aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (n === 3 ? '<span class="rec">Recommended</span>' : '') +
        '<span class="tick" aria-hidden="true"></span>' +
        '<span class="yr">' + (none ? 'Year one' : 'Cover to ' + (n * 12) + ' months') + '</span>' +
        '<p class="pr">' + (none ? 'Included' : money(t)) + '</p>' +
        '<span class="pm">' + (none ? 'Nothing to pay' : CUR() + '&middot; ' + money0(t / covYears) + ' a year of cover') + '</span>' +"""))

subs.append((
"""            '<span class="nfbd-always">Calibration twice a year is included on every machine</span>' +""",
"""            '<span class="nfbd-always">Year one is serviced and under warranty &mdash; cover insures it after that</span>' +"""))

# ── 4 · the card's own list tells the same story in both modes ─────────────
subs.append((
"""        { k:'calib',  nm:'Calibration, twice a year', fixed:true, buy:0,
          sub:'included, every machine' },""",
"""        { k:'calib',  nm:'Machine servicing', fixed:true, buy:0,
          sub:(isBuy ? 'two visits in year one, free' : 'full schedule, included') },"""))

# ── 5 · the tiles' own "free" note has to move with the rule ──────────────
subs.append((
"""    var wrapFree = on && yrs >= 2;""",
"""    /* CAUGHT IN TEST: this stayed at >= 2 while wrapCost and counterCost moved
       to >= 3, so at cover-to-24 both tiles announced "Free on this plan" for
       extras the total was correctly still charging for. A panel that contradicts
       its own arithmetic is worse than one that is simply expensive. */
    var wrapFree = on && yrs >= 3;"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = r'''
/* the free column is no longer a refusal, so it stops looking like one: solid
   border like its peers, and its figure reads as a word rather than a price */
#nfConsoleWrap .nfbd-cov.is-none:not(.is-on){border-style:solid;}
#nfConsoleWrap .nfbd-cov.is-none .pr{font-size:19px;opacity:.85;}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("risk-based cover ladder applied")
