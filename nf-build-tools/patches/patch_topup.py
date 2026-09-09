import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 58 · THE TOP-UP IS A NUMBER THE QUOTE HAS TO CARRY ────────────────────
# Alex: "Why 'Together · 7.5¢ a cup to conservation'?? wrong and this shouldn't
# even show on page 1. also if the client says contributes separately a top up
# of 6 cents per cup. i.e. roughly $3.33 per kg direct to conservation."
#
# Two faults, and the second is the serious one.
#
# 1 · THE CHIP ESCAPED ITS OWN SCREEN. #morphCombined is the top-up screen's
#     live status line — the stylesheet says so where it is defined. It is
#     written on every render regardless of phase, so once a top-up has been
#     set, stepping back to PRICE leaves it on a screen where the figure above
#     it reads 4.0¢ and the chip underneath reads 7.5¢. Both are correct — 4.0
#     is the band, 7.5 is band plus his 3.5¢ top-up — and printing them together
#     with no relationship stated is what makes it read as wrong. It now renders
#     only in the phase that owns it.
#
# 2 · THE TOP-UP NEVER REACHED THE QUOTE AT ALL. derived() pushes the price out
#     through __nfSetPrice and drops topUp on the floor, so a client could set
#     6¢ a cup in the instrument and the quote sheet would still print the band
#     contribution alone. The money was real and the document did not know about
#     it. It travels now, and it is stated in the unit the coffee is bought in:
#         6.0¢/cup ÷ 100 × (1000 ÷ 18 g) = SGD 3.33 per kg
#     which is his own figure, arrived at by the dose this file already uses
#     everywhere else.

# ── the top-up travels ────────────────────────────────────────────────────
old = """window.__nfSetPrice = function(p){
  if(Math.abs(Q.price - p) < 0.001) return;
  Q.price = p;
  if(slider) slider.value = String(p);
  recalc();
};"""
new = """window.__nfSetPrice = function(p){
  if(Math.abs(Q.price - p) < 0.001) return;
  Q.price = p;
  if(slider) slider.value = String(p);
  recalc();
};
/* 1 Sep · block 58 — the instrument's top-up, in cents per cup, published to
   the quote. Its own setter because a top-up can change while the price does
   not, and __nfSetPrice returns early on an unchanged price. */
window.__nfTopUpCents = 0;
window.__nfSetTopUp = function(c){
  c = +c || 0;
  if(Math.abs(window.__nfTopUpCents - c) < 0.001) return;
  window.__nfTopUpCents = c;
  recalc();
};"""
assert src.count(old) == 1, "setPrice anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """      var rate=(window.__nfBandRate ? window.__nfBandRate(price) : (price>=49?0.10:(price>=47?0.075:0.05)));
      if(window.__nfSetPrice) window.__nfSetPrice(price);"""
new = """      var rate=(window.__nfBandRate ? window.__nfBandRate(price) : (price>=49?0.10:(price>=47?0.075:0.05)));
      if(window.__nfSetPrice) window.__nfSetPrice(price);
      if(window.__nfSetTopUp) window.__nfSetTopUp(topUp);   /* block 58 */"""
assert src.count(old) == 1, "derived anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── compute() folds it into what goes to the NGO ──────────────────────────
old = """  var coffee = kgTotal * Q.price;
  var band = bandFor(Q.price);
  var contrib = coffee * band.rate;"""
new = """  var coffee = kgTotal * Q.price;
  var band = bandFor(Q.price);
  var bandPerKg = Q.price * band.rate;                 /* the rate, per kg */
  /* block 58 — the instrument's top-up, converted from cents per 18g cup to a
     price per kilo using the dose every figure in this file derives from */
  var topCents  = +(window.__nfTopUpCents || 0);
  var topPerKg  = topCents / 100 * (1000/18);
  var contrib = kgTotal * (bandPerKg + topPerKg);"""
assert src.count(old) == 1, "contrib anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """  return { kgTotal:kgTotal, coffee:coffee, band:band, contrib:contrib,"""
new = """  return { kgTotal:kgTotal, coffee:coffee, band:band, contrib:contrib,
           bandPerKg:bandPerKg, topCents:topCents, topPerKg:topPerKg,"""
assert src.count(old) == 1, "compute return anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── and the sheet states it ───────────────────────────────────────────────
old = """  var perKg   = Q.price * c.band.rate;                 /* what the rate is worth per kg */
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
          : ' · at the ' + CUR() + floorP.toFixed(2) + ' entry price'));"""
new = """  var perKg   = c.bandPerKg;                           /* what the rate is worth per kg */
  var perCup  = perKg / (1000/18) * 100;               /* …and per 18g cup, in cents */
  var topKg   = c.topPerKg, topCup = c.topCents;       /* the separate top-up */
  var allKg   = perKg + topKg;
  var floorP  = (MKT.kg && MKT.kg.floor) || Q.price;
  var uplift  = Q.price - floorP;
  var hasUp   = uplift > 0.004;
  var hasTop  = topCup > 0.004;

  /* block 58 · the headline figure is everything reaching the NGO per kilo. The
     sub-line takes it apart, because the two halves are different promises: the
     band is a share of the price, the top-up is money the client adds on top
     and which passes through in full. */
  set('qTopUpLab', hasTop ? 'To conservation · rate + your top-up'
                          : 'Conservation contribution');
  set('qTopUpLine', CUR() + allKg.toFixed(2) + ' /kg');
  set('qTopUpSub',
      window.__nfPct(c.band.rate) + '% of ' + CUR() + Q.price.toFixed(2)
      + ' = ' + CUR() + perKg.toFixed(2) + '/kg (' + perCup.toFixed(1) + '\\u00a2 a cup)'
      + (hasTop
          ? ' + your ' + topCup.toFixed(1) + '\\u00a2 a cup top-up = ' + CUR()
            + topKg.toFixed(2) + '/kg, passed through in full'
          : '')
      + (hasUp
          ? ' · price set ' + CUR() + uplift.toFixed(2) + '/kg above the '
            + CUR() + floorP.toFixed(2) + ' entry'
          : ' · at the ' + CUR() + floorP.toFixed(2) + ' entry price'));"""
assert src.count(old) == 1, "paint anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """  set('qHeroCoffeeNote', CUR() + perKg.toFixed(2) + '/kg to conservation ('
      + window.__nfPct(c.band.rate) + '%) · ~' + CUR() + money0(c.contrib*12)
      + '/yr to NGO partners');"""
new = """  set('qHeroCoffeeNote', CUR() + allKg.toFixed(2) + '/kg to conservation ('
      + window.__nfPct(c.band.rate) + '%'
      + (hasTop ? ' + ' + topCup.toFixed(1) + '\\u00a2/cup top-up' : '')
      + ') · ~' + CUR() + money0(c.contrib*12) + '/yr to NGO partners');"""
assert src.count(old) == 1, "hero note anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the chip stays on its own screen, and says the per-kg too ─────────────
old = """        if(tier>=2)      chip.textContent = 'Past the 12¢ stretch — thank you ✦';
        else if(tier===1) chip.textContent = '10¢ a cup, all to the NGO ✓';
        else if(d.topUp>0) chip.textContent = 'Together · '+d.combined.toFixed(1)+'¢ a cup to conservation';
        else             chip.textContent = '';"""
new = """        /* block 58 — this line belongs to the TOP-UP screen and to no other.
           Written on every render, it followed the reader back to PRICE, where
           the figure above it states the band alone: 4.0¢ over the picture and
           7.5¢ underneath, with nothing saying the second includes a top-up. */
        var onTopUpPhase = stage.classList.contains('ph-topup');
        if(!onTopUpPhase) chip.textContent = '';
        else if(tier>=2)  chip.textContent = 'Past the 12¢ stretch — thank you ✦';
        else if(tier===1) chip.textContent = '10¢ a cup, all to the NGO ✓';
        else if(d.topUp>0) chip.textContent = 'Together · ' + d.combined.toFixed(1)
              + '¢ a cup · your top-up alone is ' + (d.topUp/100*(1000/18)).toFixed(2)
              + ' a kilo, straight to conservation';
        else             chip.textContent = '';"""
assert src.count(old) == 1, "chip anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("top-up reaches the quote; chip confined to its own phase")
