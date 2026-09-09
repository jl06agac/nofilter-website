import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the plan becomes an explicit ladder, per market ────────────────────
subs.append((
"""        buyx:{ cooler:800, install:300, svcYr1:1250, svcYr:1750, wrap:1000, wrapOff:400,""",
"""        /* svcPlan — 1 Sep 2026. The plan was svcYr1 + (y-1)*svcYr, which forces
           an arithmetic progression: 1,250 / 3,000 / 4,750. That shape puts the
           MONTHLY UP as the commitment lengthens (104 / 125 / 132), so the
           longest, most-locked-in customer read the worst deal on the card.
           With both extras now free from two years, the three-year rung had
           nothing left to offer but a bigger bill. It is a lookup now, so the
           ladder can be priced rather than generated: 104 / 125 / 119 a month,
           the third year genuinely cheaper. Alex, 1 Sep: "3 year plan needs a
           slight discount vs 2 yrs if we're giving them away." */
        buyx:{ cooler:800, install:300, svcPlan:{1:1250,2:3000,3:4300},
               svcYr1:1250, svcYr:1750, wrap:1000, wrapOff:400,"""))

subs.append((
"""        buyx:{ cooler:2108, install:790, svcYr1:3293, svcYr:4611, wrap:2635, wrapOff:1054,""",
"""        /* AE placeholders, the SG ladder at the same 2.6346 the rest of this
           block uses. Still owed a real Dubai servicing budget — see RATE-CARD §4. */
        buyx:{ cooler:2108, install:790, svcPlan:{1:3293,2:7904,3:11329},
               svcYr1:3293, svcYr:4611, wrap:2635, wrapOff:1054,"""))

subs.append((
"""function svcPlanCost(x, yrs){
  var y = Math.max(1, yrs | 0);
  return (x.svcYr1 || x.svcYr) + (y - 1) * x.svcYr;
}""",
"""function svcPlanCost(x, yrs){
  var y = Math.max(1, Math.min(3, yrs | 0));
  /* the priced ladder, with the old progression kept as a fallback so a market
     that has not been given a svcPlan block still quotes something sane */
  if(x.svcPlan && x.svcPlan[y] != null) return x.svcPlan[y];
  return (x.svcYr1 || x.svcYr) + (y - 1) * x.svcYr;
}"""))

# ── 2 · the counter joins the wrap from two years ──────────────────────────
subs.append((
"""function counterCost(x, cfg){ return x.counter; }""",
"""/* ── 1 Sep 2026 · THE COUNTER IS FREE FROM TWO YEARS ──────────────────────
   This returned x.counter unconditionally, and the note above records why: on
   31 Aug the two-year giveaway of both extras was withdrawn because it cost
   1,250 of gross to save the buyer 250. That arithmetic was right and the
   conclusion was wrong, because it weighed only what the BUYER got for it.

   What changed is a fact I did not have: a rental or a purchase obliges the
   client to buy their beans from us — exclusive supply, no minimum volume, in
   contract. So the machine is the acquisition and the beans are the annuity.
   Against that, 1,000 of one-off gross is recovered in two to eight months of
   coffee on any plausible volume, and a third locked year is worth several
   times it.

   And the counter earns its keep twice. With exclusivity and no MOQ the
   exposure is not under-ordering, it is a machine quietly running someone
   else's bean — and the live counter is the only instrument that would show
   it: cups times ~8g against kilos actually ordered. Selling it to one-year
   buyers and withholding it from three-year ones had that exactly backwards.

   Wrap and counter now move together, so wrapCost above and this function
   answer the same question and must stay in step. */
function counterCost(x, cfg){ return (cfg.svc && (cfg.svcYrs || 1) >= 2) ? 0 : x.counter; }"""))

# ── 3 · picking a 2/3-year rung switches BOTH on ───────────────────────────
subs.append((
"""        if(n >= 2) cfg.wrap = true;""",
"""        if(n >= 2){ cfg.wrap = true; cfg.counter = true; }"""))

# ── 4 · the rungs say what they now include ────────────────────────────────
subs.append((
"""      2:['Parts &amp; breakdown cover','Three scheduled visits a year','Livery wrap included'],
      3:['Parts &amp; breakdown cover','Three scheduled visits a year','Livery wrap included']""",
"""      2:['Parts &amp; breakdown cover','Three scheduled visits a year','Wrap + impact counter free'],
      3:['Parts &amp; breakdown cover','Three scheduled visits a year','Wrap + impact counter free']"""))

# ── 5 · the extras tiles say so too ────────────────────────────────────────
subs.append((
"""            ex('counter','Live impact counter','Cups &amp; funds &middot; ' + CUR() + money(x.counter), x.counter, 'smiirl-counter.jpg') +""",
"""            ex('counter','Live impact counter',
               (wrapFree ? 'Free on this plan' : 'Cups &amp; funds &middot; ' + CUR() + money(x.counter)),
               x.counter, 'smiirl-counter.jpg') +"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("ladder + counter-free-from-2yr applied")
