import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 59b · the numbers behind the new step-4 layout ────────────────────────
old = """  /* the coffee lines */
  set('qCoffeeLine', CUR() + Q.price.toFixed(2));
  set('qCoffeeSub', CUR() + Q.price.toFixed(2) + ' / kg · ' + window.__nfPct(c.band.rate) + '% to conservation');
  set('qConsBasis', Math.round(c.kgTotal * (1000/18) * 12).toLocaleString('en-GB'));
  set('qConsAnnual', '~' + CUR() + money0(c.contrib * 12));"""
new = """  /* ── the coffee lines · block 59 ────────────────────────────────────────
     Four figures, each stated once and never re-derived on the page:
       base       what the coffee is invoiced at, before anything voluntary
       topKg      the top-up, converted from \\u00a2/cup at 1000/18 g
       invoiced   base + topKg — the number on the invoice
       ngoKg      band share + topKg — the number reaching the NGOs
     The band percentage is taken on the BASE rate, per Alex's decision: a
     voluntary top-up must not push the band into the next tier and get
     counted twice. */
  var CUPS_KG = 1000/18;
  var base     = Q.price;
  var bandKg   = c.bandPerKg;
  var bandCup  = bandKg / CUPS_KG * 100;
  var topKg    = c.topPerKg, topCup = c.topCents;
  var hasTop   = topCup > 0.004;
  var invoiced = base + topKg;
  var ngoKg    = bandKg + topKg;
  var ngoCup   = ngoKg / CUPS_KG * 100;

  set('qCoffeeLine', CUR() + base.toFixed(2) + ' /kg');
  set('qCoffeeSub', 'Includes ' + bandCup.toFixed(1) + '\\u00a2/cup built-in NGO share ('
      + window.__nfPct(c.band.rate) + '% of the rate)');

  var tuRow = $('#qTopUpRow'); if(tuRow) tuRow.hidden = !hasTop;
  set('qTopUpLine', '+ ' + CUR() + topKg.toFixed(2) + ' /kg');
  set('qTopUpSub', '+' + topCup.toFixed(1) + '\\u00a2/cup top-up · '
      + CUPS_KG.toFixed(1) + ' cups/kg conversion');

  set('qInvoicedLine', CUR() + invoiced.toFixed(2) + ' /kg');

  set('qNgoVal', CUR() + ngoKg.toFixed(2));
  set('qNgoSub', '100% of the built-in share (' + CUR() + bandKg.toFixed(2) + '/kg)'
      + (hasTop ? ' + your top-up (' + CUR() + topKg.toFixed(2) + '/kg)' : '')
      + ' passed directly to NGO partners · ~' + ngoCup.toFixed(1) + '\\u00a2/cup.'
      /* restoration, not an offset — see block 59 */
      + ' Includes tree planting at the Cinta Raja restoration site.');
  set('qConsBasis', Math.round(c.kgTotal * CUPS_KG * 12).toLocaleString('en-GB'));
  set('qConsAnnual', '~' + CUR() + money0(c.contrib * 12));"""
assert src.count(old) == 1, "coffee paint anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# the old block-58 paragraph goes: its job is now done by the table above
old = """  var perKg   = c.bandPerKg;                           /* what the rate is worth per kg */
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
          : ' · at the ' + CUR() + floorP.toFixed(2) + ' entry price'));

  set('qHeroCoffee', Q.price.toFixed(2));
  set('qHeroCoffeeNote', CUR() + allKg.toFixed(2) + '/kg to conservation ('
      + window.__nfPct(c.band.rate) + '%'
      + (hasTop ? ' + ' + topCup.toFixed(1) + '\\u00a2/cup top-up' : '')
      + ') · ~' + CUR() + money0(c.contrib*12) + '/yr to NGO partners');"""
new = """  /* the headline pair · block 59 — the invoiced rate leads, the split sits
     under it, so the first number a finance reader meets is the billed one */
  set('qHeroCoffee', invoiced.toFixed(2));
  set('qHeroCoffeeNote', CUR() + base.toFixed(2) + ' base'
      + (hasTop ? ' + ' + CUR() + topKg.toFixed(2) + ' voluntary top-up' : '')
      + ' · ' + CUR() + ngoKg.toFixed(2) + '/kg passed to NGOs');"""
assert src.count(old) == 1, "block58 paint anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the servicing sub-line, and the equipment note, both told the truth ───
old = """    /* servicing — the row a buyer is most likely to read as free */
    setv('#qFleetVal', !units ? 'Included'
      : buy && !rent ? (svcBought ? 'Purchased · see servicing plan above' : 'NOT INCLUDED — plan declined')
      : mixed ? 'Included on the rented units' : 'Included');"""
new = """    /* servicing — the row a buyer is most likely to read as free */
    setv('#qFleetVal', !units ? 'Included'
      : buy && !rent ? (svcBought ? 'Purchased · see servicing plan above' : 'NOT INCLUDED — plan declined')
      : mixed ? 'Included on the rented units' : 'Included');
    /* block 59 — and its sub-line follows it. Alex's copy said "every 4 months"
       flat; the real cadence is twice-yearly in years one and two and
       four-monthly in year three, and on a purchase with no plan there is no
       cadence at all. A schedule printed over a declined plan is the one thing
       on this card that could be read as a commitment. */
    setv('#qFleetSub', (buy && !rent && !svcBought)
        ? 'Sold separately · no servicing plan taken on this quote'
        : (buy && !rent)
          ? 'Per the servicing plan itemised above · parts and labour included'
          : 'Twice-yearly in years 1–2, every four months in year 3 · parts and labour included');

    /* the lease line under the equipment figure — term read from what is
       actually on the quote, inclusions named only where they are free */
    var term = 0;
    MACHINES.forEach(function(mm){ var st = Q.m[mm.k];
      if(st.q && st.mode !== 'purchase' && !term) term = st.term; });
    window.__nfLeaseTerm = term;"""
assert src.count(old) == 1, "fleet anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """  set('qHeroEquipNote', c.capex > 0
      ? ('plus ' + CUR() + money(c.capex) + ' one-time · machine, cooler, install & servicing plan')
      : 'our leasing partner · cooler, install, servicing, wrap & counter included');"""
new = """  set('qHeroEquipNote', c.capex > 0
      ? ('plus ' + CUR() + money(c.capex) + ' one-time · machine, cooler, install & servicing plan')
      : (c.units
          ? (window.__nfLeaseTerm || 36) + '-month lease · includes milk fridge, servicing, wrap & impact screen'
          : 'our leasing partner · cooler, install, servicing, wrap & counter included'));"""
assert src.count(old) == 1, "equip note anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ── 59c · STEP 4, READ BY PROCUREMENT ────────────────────────────────────
   Alex's spec: separate the invoiced rate from the pass-through, lift the
   secondary text off the background, and stop the card reading like a
   derivation. The contrast move is the one that matters most — the sub-lines
   were rgba(244,239,226,.45) on #141311, which is about 4.4:1 and legible only
   if you already know what it says. #CCC on the same ground is 9.6:1. */
.q-settle .q-lab .q-sub,
.q-settle .q-sub{color:#CCCCCC;}
.q-settle .q-total-note{color:#CCCCCC;}

/* the invoiced total closes the table: a rule above it and the same weight as
   a figure that gets signed off */
.q-settle .q-line--sum{border-top:1px solid rgba(244,239,226,.28);margin-top:2px;}
.q-settle .q-line--sum .q-lab{font-weight:600;letter-spacing:.01em;}
.q-settle .q-line--sum .q-val{color:#FFFFFF;font-weight:600;}

/* the pass-through panel — a card inside the card, because it answers a
   different question from the three lines above it and must not be mistaken
   for a fourth billed line */
.q-settle .q-ngo{margin-top:14px;padding:13px 14px;border-radius:12px;
  background:rgba(255,232,195,.06);border:1px solid rgba(255,232,195,.18);}
.q-settle .q-ngo-hd{font-family:var(--font-m,monospace);font-size:9.5px;letter-spacing:.16em;
  text-transform:uppercase;color:#CCCCCC;margin-bottom:6px;}
.q-settle .q-ngo-val{font-size:19px;color:#FFE8C3;line-height:1.2;}
.q-settle .q-ngo-unit{font-size:12px;color:#CCCCCC;}
.q-settle .q-ngo-in{display:block;font-family:var(--font-m,monospace);font-size:9.5px;
  letter-spacing:.06em;color:#CCCCCC;margin-top:3px;}
.q-settle .q-ngo-sub{font-family:var(--font-m,monospace);font-size:10px;line-height:1.65;
  color:#CCCCCC;margin-top:8px;}

/* the taste options become cards rather than two loose checkbox lines */
.q-settle .q-taste-hd{color:#F4EFE2;}
.q-settle .q-taste-opt{display:flex;gap:10px;align-items:flex-start;
  padding:11px 12px;margin-top:8px;border-radius:11px;
  border:1px solid rgba(244,239,226,.18);background:rgba(244,239,226,.04);
  cursor:pointer;transition:border-color .18s,background .18s;}
.q-settle .q-taste-opt:hover{border-color:rgba(244,239,226,.42);background:rgba(244,239,226,.07);}
.q-settle .q-taste-opt:has(input:checked){border-color:var(--or,#EE4D17);
  background:rgba(238,77,23,.10);}
.q-settle .q-taste-t{display:block;color:#F4EFE2;font-weight:600;margin-bottom:3px;}
/* "free" is set as a mark rather than a colour: the reader this is aimed at may
   not see an orange word as different from a cream one */
.q-settle .q-taste-t i{font-style:normal;font-family:var(--font-m,monospace);font-size:9px;
  letter-spacing:.12em;text-transform:uppercase;border:1px solid currentColor;
  border-radius:99px;padding:1px 6px;margin-left:7px;vertical-align:1px;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("step 4 numbers, servicing truth and card styling")
