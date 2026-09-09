import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []
Q3 = "'''"

# ── 1 · per-machine cover rates + a year-one servicing price ──────────────
subs.append((
"""        buyx:{ cooler:800, install:300, svcPlan:{2:2000,3:3600},""",
"""        /* ── 1 Sep 2026 · PRICED OFF THE ACTUAL BONCAFE CONTRACT ──────────
           Alex supplied the signed Boncafe | Saucy Bean agreement (02/11/2025).
           It prices by PLAN, not by model — a C2 on Comprehensive costs exactly
           what a C8 does — which killed the assumption that a C2 could be
           serviced for 750:

               Bi-Annual      400/yr   2 PM visits, labour covered
               Basic          800/yr   4 PM visits + wear parts at PM
               Comprehensive 1050/yr   4 PM visits + ALL parts and labour,
                                       preventive AND reactive, + pooled sessions

           Modelled here at Boncafe +10% (Alex's instruction): 440 / 880 / 1155.

           So the machine tiering happens on OUR side, by choosing which Boncafe
           plan each model sits on. A one-grinder countertop C2 does not need
           four visits a year; it goes on Bi-Annual, which is also what makes its
           cover proportionate to a 3,600 machine. C5 upward carry Comprehensive,
           because "every part and every breakdown, no invoice" is the product
           and it cannot be said on Basic.

           svc1 is year-one servicing: the same Bi-Annual product, sold as an
           option on every model, because in year one the manufacturer warranty
           carries the parts and only the visits are missing.

           cover{} is per machine per year. svcPlan is gone — a single global
           ladder cannot express a cost base that is flat while machine prices
           run 3,600 to 10,500.

           STANDING RISK, recorded here because it is a code-level assumption:
           the Boncafe agreement is TWELVE MONTHS per machine and re-quoted at
           every renewal (cl. 1.0-1.2). These numbers assume 1,155 holds for the
           life of a three-year plan sold on top of it. */
        cover:{ cm2:750, cm5:1800, cm6:2200, cm8:2400 },
        buyx:{ cooler:800, install:300, svc1:750,"""))

subs.append((
"""        buyx:{ cooler:2108, install:790, svcPlan:{2:5269,3:9485},""",
"""        cover:{ cm2:1976, cm5:4742, cm6:5796, cm8:6323 },
        buyx:{ cooler:2108, install:790, svc1:1976,"""))

# ── 2 · the cost function now needs the MACHINE, not just the market ──────
subs.append((
"""function svcPlanCost(x, yrs){
  var y = Math.max(2, Math.min(3, yrs | 0));   /* cover starts at 2 */""",
"""/* the per-machine annual cover rate for the live market */
function coverRate(m){
  var c = (MKT && MKT.cover) || MARKETS.SG.cover;
  return (m && c && c[m.k]) || 0;
}
/* yrs is "covered to N years of ownership": 2 => one insured year (Y2),
   3 => two insured years (Y2 and Y3). Year one is never in here — it belongs to
   the warranty, and its optional servicing is buyx.svc1. */
function svcPlanCost(m, yrs){
  var y = Math.max(2, Math.min(3, yrs | 0));
  return coverRate(m) * (y - 1);
}
/* the old market-wide shape, kept only so a stale caller is obvious in test
   rather than silently quoting zero */
function svcPlanCostLegacy(x, yrs){
  var y = Math.max(2, Math.min(3, yrs | 0));"""))

# ── 3 · buyTotal ──────────────────────────────────────────────────────────
subs.append((
"""function buyTotal(m, cfg){
  var x = buyExtras(), yrs = (cfg.svcYrs || 1);
  return m.buy + x.install
       + (cfg.cooler  ? x.cooler             : 0)
       + (cfg.svc     ? svcPlanCost(x, yrs)  : 0)
       + (cfg.wrap    ? wrapCost(x, cfg)      : 0)
       + (cfg.counter ? counterCost(x, cfg)   : 0);
}""",
"""function buyTotal(m, cfg){
  var x = buyExtras(), yrs = (cfg.svcYrs || 2);
  return m.buy + x.install
       + (cfg.cooler  ? x.cooler             : 0)
       + (cfg.svc1    ? x.svc1               : 0)   /* year-one servicing, optional */
       + (cfg.svc     ? svcPlanCost(m, yrs)  : 0)   /* cover, from month 13 */
       + (cfg.wrap    ? wrapCost(x, cfg)      : 0)
       + (cfg.counter ? counterCost(x, cfg)   : 0);
}"""))

# ── 4 · every other call site ─────────────────────────────────────────────
subs.append(("""          buy:isBuy ? svcPlanCost(x, yrs) : x.svcYr * yrs },""",
             """          buy:isBuy ? svcPlanCost(m, yrs) : x.svcYr * yrs },"""))
subs.append(("""      var svc  = s.svc     ? svcPlanCost(x, yrs) : 0;""",
             """      var svc  = s.svc     ? svcPlanCost(m, yrs) : 0;
      var svc1 = s.svc1    ? x.svc1              : 0;"""))
subs.append(("""            var tot = svcPlanCost(x, nY);""",
             """            var tot = svcPlanCost(m, nY);"""))
subs.append(("""      var t = none ? 0 : svcPlanCost(x, n);""",
             """      var t = none ? 0 : svcPlanCost(m, n);"""))

# ── 5 · state ─────────────────────────────────────────────────────────────
subs.append((
"""  m: { cm2:{q:0,mode:'rental',term:36,svcYrs:2,cooler:true,svc:true,wrap:true,counter:true},
       cm5:{q:0,mode:'rental',term:36,svcYrs:2,cooler:true,svc:true,wrap:true,counter:true},
       cm6:{q:0,mode:'rental',term:36,svcYrs:2,cooler:true,svc:true,wrap:true,counter:true},
       cm8:{q:0,mode:'rental',term:36,svcYrs:2,cooler:true,svc:true,wrap:true,counter:true} }""",
"""  m: { cm2:{q:0,mode:'rental',term:36,svcYrs:2,svc1:false,cooler:true,svc:true,wrap:true,counter:true},
       cm5:{q:0,mode:'rental',term:36,svcYrs:2,svc1:false,cooler:true,svc:true,wrap:true,counter:true},
       cm6:{q:0,mode:'rental',term:36,svcYrs:2,svc1:false,cooler:true,svc:true,wrap:true,counter:true},
       cm8:{q:0,mode:'rental',term:36,svcYrs:2,svc1:false,cooler:true,svc:true,wrap:true,counter:true} }"""))
subs.append((
"""        Q.m[m.k].cooler = true;
        Q.m[m.k].svc = Q.m[m.k].wrap = Q.m[m.k].counter = false;""",
"""        Q.m[m.k].cooler = true;
        Q.m[m.k].svc = Q.m[m.k].svc1 = Q.m[m.k].wrap = Q.m[m.k].counter = false;"""))

# ── 6 · rung copy follows the Boncafe plan the machine actually sits on ───
subs.append((
"""    var COVROWS = {
      0:['Two maintenance visits, free','Parts &amp; labour under manufacturer warranty'],
      2:['Every part and breakdown insured, from month 13','Three scheduled visits a year'],
      3:['Every part and breakdown insured, from month 13','Three scheduled visits a year','Wrap + impact counter free']
    };""",
"""    /* the promise has to match the plan we actually buy. C5 upward sit on
       Boncafe Comprehensive, where all parts and labour are covered preventive
       AND reactive, so "every part and breakdown insured" is literally true. A
       C2 sits on Bi-Annual — two visits, labour at PM — so it says the weaker,
       accurate thing instead. Claiming full insurance on a plan that does not
       carry reactive parts would be the one lie on this card. */
    var comp = coverRate(m) >= 1000;
    var COVROWS = {
      0:['Nothing to pay after the machine','Warranty carries parts and labour in year one'],
      2:[(comp ? 'Every part and breakdown insured' : 'Serviced and maintained') + ', from month 13',
         (comp ? 'Four scheduled visits a year' : 'Two scheduled visits a year')],
      3:[(comp ? 'Every part and breakdown insured' : 'Serviced and maintained') + ', from month 13',
         (comp ? 'Four scheduled visits a year' : 'Two scheduled visits a year'),
         'Wrap + impact counter free']
    };"""))

subs.append((
"""        '<span class="yr">' + (none ? 'Year one' : 'Cover to ' + (n * 12) + ' months') + '</span>' +
        '<p class="pr">' + (none ? 'Included' : money(t)) + '</p>' +
        '<span class="pm">' + (none ? 'Nothing to pay' : CUR() + '&middot; ' + money0(t / covYears) + ' a year of cover') + '</span>' +""",
"""        '<span class="yr">' + (none ? 'No cover' : 'Cover to ' + (n * 12) + ' months') + '</span>' +
        '<p class="pr">' + (none ? 'Nothing' : money(t)) + '</p>' +
        '<span class="pm">' + (none ? 'Warranty only' : CUR() + '&middot; ' + money0(t / covYears) + ' a year') + '</span>' +"""))

# ── 7 · year-one servicing: its own full-width row under the rungs ────────
subs.append((
"""'</div><div class="nfbd-covs">' + rung(0) + rung(2) + rung(3) + '</div></div>' +""",
"""'</div><div class="nfbd-covs">' + rung(0) + rung(2) + rung(3) + '</div>' +
            /* YEAR-ONE SERVICING IS NOT HARDWARE. It went into the extras row
               first, which made four tiles where three fit and wrapped every
               label onto three lines — and it was wrong on its own terms: that
               section is called Extra hardware and this is labour. It belongs
               under the cover rungs, which are the other half of the same
               question (who services it, and from when), and it is full width
               because it is a sentence rather than a product with a picture. */
            '<button type="button" class="nfbd-svc1' + (cfg.svc1 ? ' is-on' : '') +
              '" data-nfbd-x="svc1" aria-pressed="' + (cfg.svc1 ? 'true' : 'false') + '">' +
              '<span class="nfbd-sw" aria-hidden="true"><i></i></span>' +
              '<span class="t">Add year-one servicing</span>' +
              '<span class="d">Two visits, in the year the warranty covers the parts</span>' +
              '<span class="p">' + CUR() + money(x.svc1) + '</span>' +
            '</button></div>' +"""))

subs.append((
"""            '<span class="nfbd-always">Year one is serviced and under warranty &mdash; cover insures it after that</span>' +""",
"""            '<span class="nfbd-always">Year one is under manufacturer warranty &mdash; cover takes over from month 13</span>' +"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = "\n".join([
"/* year-one servicing is ONE ROW under the cover rungs, not a fourth hardware",
"   tile. It reads as a sentence with a price on the end, which is what it is. */",
"#nfConsoleWrap .nfbd-svc1{",
"  display:flex;align-items:center;gap:12px;width:100%;",
"  background:none;border:1.4px solid rgba(244,242,238,.2);border-radius:11px;",
"  padding:9px 14px 9px 11px;margin:0 0 20px;cursor:pointer;",
"  color:inherit;font-family:inherit;text-align:left;",
"  transition:border-color .18s,background .18s;}",
"#nfConsoleWrap .nfbd-svc1:hover{border-color:rgba(244,242,238,.45);background:rgba(244,242,238,.05);}",
"#nfConsoleWrap .nfbd-svc1.is-on{border-color:rgba(244,242,238,.7);background:rgba(244,242,238,.1);}",
"#nfConsoleWrap .nfbd-svc1 .t{font-size:12.5px;font-weight:600;flex:0 0 auto;}",
"#nfConsoleWrap .nfbd-svc1 .d{font-family:var(--mono,monospace);font-size:9.5px;",
"  letter-spacing:.04em;color:rgba(255,232,195,.62);flex:1 1 auto;min-width:0;",
"  overflow:hidden;white-space:nowrap;text-overflow:ellipsis;}",
"#nfConsoleWrap .nfbd-svc1 .p{font-family:var(--mono,monospace);font-size:11px;flex:0 0 auto;color:#F4F2EE;}",
"@media(max-height:860px){#nfConsoleWrap .nfbd-svc1{padding:6px 12px 6px 9px;margin-bottom:12px;}}",
"@media(max-width:900px){#nfConsoleWrap .nfbd-svc1 .d{display:none;}}",
])

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("per-machine cover + year-one servicing applied")
