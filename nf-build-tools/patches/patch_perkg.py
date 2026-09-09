import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 54 · WHAT THE CONTRIBUTION COSTS PER KG, STATED ───────────────────────
# Alex: "when i make the NGO contribution, say 4 more cents per cup, at the end
# page i'd want to know what my extra exposure is in terms of $ per kg. i.e.
# here we set at 48$, there was an optional top up made but we have no idea what
# that looks like per kg, it should be clear."
#
# He is right that it is missing, and the page was already built to say it: the
# sheet carries a #qTopUpRow — "Sustainability top-up … /kg" — that is hidden,
# never populated, and reset to 0.00 by one line in the market switch. Scaffold
# that was never wired.
#
# The arithmetic is already in the file and is not being re-derived here:
#     contribution/kg  = Q.price × band.rate          (compute(): coffee × rate)
#     cups per kg      = 1000 / 18                    (the 18g dose, as used by
#                                                      the cups/yr basis above)
#     cents per cup    = contribution/kg ÷ cupsPerKg × 100
# At the default SGD 48.00 that is 7.5% → SGD 3.60/kg → 6.5¢ a cup.
#
# TWO NUMBERS, NOT ONE, because "extra exposure" has two honest readings and
# they differ: what the contribution itself is worth per kg (3.60), and how far
# the chosen price sits above the entry price where an account can open (48.00
# − 45.00 = 3.00, which is what lifts the band from 5% to 7.5%). The row states
# the first and the sub-line states the second, so neither can be mistaken for
# the other.
#
# The row is only labelled a top-up when there IS one: at the market floor the
# contribution still exists, it simply has no uplift above it, and calling the
# default a "top-up" would credit the buyer with a choice they had not made.

# ── the row says what it now holds ────────────────────────────────────────
old = """    <div class="q-line" id="qTopUpRow" hidden>
      <div class="q-lab">Sustainability top-up <span class="q-sub" id="qTopUpSub">from sustainability budget &middot; pass-through to NGO in full</span></div>
      <div class="q-val" id="qTopUpLine">SGD 0.00<span class="q-unit"> /kg</span></div>
    </div>"""
if src.count(old) != 1:
    old = old.replace("&middot;", "·")
assert src.count(old) == 1, "top-up row anchor not unique (%d)" % src.count(old)
new = """    <div class="q-line" id="qTopUpRow">
      <div class="q-lab"><span id="qTopUpLab">Conservation contribution</span> <span class="q-sub" id="qTopUpSub">pass-through to NGO partners in full</span></div>
      <div class="q-val" id="qTopUpLine">SGD 0.00<span class="q-unit"> /kg</span></div>
    </div>"""
src = src.replace(old, new)

# ── and it is filled from the same numbers the sheet already computes ─────
old = """  set('qConsBasis', Math.round(c.kgTotal * (1000/18) * 12).toLocaleString('en-GB'));
  set('qConsAnnual', '~' + CUR() + money0(c.contrib * 12));
  set('qHeroCoffee', Q.price.toFixed(2));
  set('qHeroCoffeeNote', '+ ' + window.__nfPct(c.band.rate) + '% to conservation · ~'
      + CUR() + money0(c.contrib*12) + '/yr to NGO partners');"""
new = """  set('qConsBasis', Math.round(c.kgTotal * (1000/18) * 12).toLocaleString('en-GB'));
  set('qConsAnnual', '~' + CUR() + money0(c.contrib * 12));

  /* ── 1 Sep · THE CONTRIBUTION IN THE UNIT THE COFFEE IS BOUGHT IN ───────
     See block 54. Both figures come from numbers already on this page; the
     only new thing is that they are now printed. */
  var perKg   = Q.price * c.band.rate;                 /* what the rate is worth per kg */
  var perCup  = perKg / (1000/18) * 100;               /* …and per 18g cup, in cents */
  var floorP  = (MKT.kg && MKT.kg.floor) || Q.price;
  var uplift  = Q.price - floorP;
  var hasUp   = uplift > 0.004;
  set('qTopUpLab', hasUp ? 'Conservation contribution · with your top-up'
                         : 'Conservation contribution');
  set('qTopUpLine', CUR() + perKg.toFixed(2) + ' /kg');
  set('qTopUpSub',
      window.__nfPct(c.band.rate) + '% of ' + CUR() + Q.price.toFixed(2)
      + ' · ' + perCup.toFixed(1) + '\\u00a2 a cup'
      + (hasUp
          ? ' · you set the price ' + CUR() + uplift.toFixed(2) + '/kg above the '
            + CUR() + floorP.toFixed(2) + ' entry, which lifts the rate to '
            + window.__nfPct(c.band.rate) + '%'
          : ' · at the ' + CUR() + floorP.toFixed(2) + ' entry price'));

  set('qHeroCoffee', Q.price.toFixed(2));
  set('qHeroCoffeeNote', CUR() + perKg.toFixed(2) + '/kg to conservation ('
      + window.__nfPct(c.band.rate) + '%) · ~' + CUR() + money0(c.contrib*12)
      + '/yr to NGO partners');"""
assert src.count(old) == 1, "paint anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the market switch stops blanking a row that now carries a real figure ─
old = """  setT('#qTopUpLine',   MKT.cur + ' 0.00');"""
new = """  /* 1 Sep — was blanking the contribution-per-kg row on every market change
     (block 54). recalc() repaints it with the new market's own figure, so the
     reset is not only unnecessary, it printed a zero that was never true. */"""
assert src.count(old) == 1, "market reset anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("contribution now stated per kg and per cup")
