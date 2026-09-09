import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 78 · THE UK CARD ══════════════════════════════════════════════════════
# Alex, 2 Sep: "let's create our UK offering, with the equivalent machines for
# C2, C5, C6 & C8, ensure we have a similar margin to SG ... include the
# servicing add-ons too." Coffee: "use a base green price of 16sgd landed prior
# to roasting, and then factor in 20% roasting weight loss and follow the slot
# roasting to derive roasted, bagged 1kg cost, from there add in our usual
# profit margin and let me know recommended selling price per kg."
#
# ── COFFEE, per roasted kg, GBP (SGD→GBP ≈ 0.58) ───────────────────────────
#   green landed        SGD 16.00 = £9.28 per green kg  →  ÷ 0.80  = £11.60
#   roasting            £5.00 — Alex, 2 Sep: "assume worst roasting tier,
#                       lowest volume". Coffee by Tate's email (2 Sep): £4 per
#                       GREEN kg at 0–100 kg, £3 at 100–250, £2.50 at 250+, ex
#                       VAT, per order; £4 ÷ 0.80 = £5.00 per roasted kg exactly
#   packing + bag       Tate: 50p/kg basic packing + 50p per 1 kg bag = £1.00
#   DHL Tate → us       at cost + VAT, ~£0.50/kg
#   last-mile           £1.00
#   other (QC, storage — Tate's green storage is free)  £0.25
#   ── all-in cost      £19.35 per roasted kg IF VAT-registered
#
#   Alex, 2 Sep: the UK entity is NOT VAT-registered. So the 20% on the green
#   import, on Tate's roasting and packing, on DHL and on last-mile is a real
#   cost, not input tax:  green 13.92 · roasting 6.00 · packing+bag 1.20 ·
#   DHL 0.60 · last-mile 1.20 · other 0.25  = £23.17 per roasted kg.
#   Floor for ≥ 30% net at 5%: 23.17 / 0.65 = 35.65 → £36 (36/38/40/42 nets
#   30.6–34.8%). Alex, 2 Sep: "remember they get the other value adds though,
#   the decals, the ngo contribution, i think we can defend pricing a bit
#   higher" — so the ladder is set to SG-PARITY NET instead (SG nets 36.4 /
#   37.5 / 38.3 / 42.0% on its 45/48/51/55):
#   40 at 5% = 14.83 = 37.1% · 42 at 7.5% = 15.68 = 37.3% · 44 at 10% = 16.43
#   = 37.3% · 48 at 10% = 20.03 = 41.7%. Then Alex: "or we can put the range v
#   slightly below so it's right at the end of the high 30s" → 39/41/43/46:
#   39 at 5% = 13.88 = 35.6% · 41 at 7.5% = 14.76 = 36.0% · 43 at 10% = 15.53
#   = 36.1% · 46 at 10% = 18.23 = 39.6%. Registering for VAT (voluntary below
#   the £90k threshold) takes the cost back to 19.35 and adds ~£3.80/kg net.
#
#   The SG rule (pricing.md): at the LOWEST price the business nets ≥ 30%
#   after the contribution — see the VAT block above for the live ladder
#   (36 / 38 / 40 / 42). Same shape as SG (45/48/51/55).
#   Bags: SG 1 kg is 1.78 × floor and 250 g is 0.53 × floor → £69 / £21.
#   Cup: 1000/18 = 55.6 cups/kg. SG milestones 10¢/12¢ on a 45 floor scale to
#   9p/10p on 39; top-up ceiling 7.5¢ → 6.5p, step 0.1p.
#
# ── MACHINES, GBP ex VAT — Dr.Coffee UK distributor price list, 1 June 2026 ──
#   CafeMatic → Dr.Coffee equivalent, confirmed off drcoffee.uk / drcoffee.com:
#     C2 → F16            (1 hopper, 8 L tank or plumbed, 100 cups/day)
#     C5 → Coffee Zone T  (340×545 chassis, 1 hopper, 2 powder, wand + hot water)
#     C6 → F30 H          (2 × 1.2 kg hoppers, 2 grinders, no powder)
#     C8 → F30 Plus       (2 hoppers, 2 grinders, 2 powder)
#     fridge → SC12 10 L
#   Trade cost at 1–4 units (35% off RRP) — Alex, 2 Sep: "are you sure we're
#   following their 1-4 unit trade price": the first UK orders are one or two
#   machines, so the card is costed at the 1–4 tier, not the 5+ (37%) tier:
#     F16 1,332.50 · Zone T 2,177.50 · F30 H 4,777.50 · F30 Plus 5,102.50 ·
#     SC12 451.75   (5+ would be 1,291.50 / 2,110.50 / 4,630.50 / 4,945.50 /
#     437.85 — upside once volume arrives, not the base)
#   Servicing = Dr.Coffee UK Annual Comprehensive Service Contract (install
#     + training, 1 C500 filter exchange, 2 PPM visits, parts & labour,
#     helpdesk): F16 750 · Coffee Zone 900 · F30 995 per year.
#   Wrap 450 (SG cost 750 at FX, no UK quote yet). Counter 200 ASSUMED (a
#     tablet and mount; no figure on file). Filter head 22 (the cartridge is
#     in the contract).
#
#   RENTAL — Alex, 2 Sep: "are you sure ... we're making margin ... on
#   servicing fees per machine type". The first cut used the SG shape (year 1
#   free under warranty, contract from year 2). That is wrong for the UK: a
#   rental promises the full schedule from day one and nobody here does the
#   visits but Dr.Coffee, so the contract is bought from YEAR ONE — and it
#   carries the install and training, so there is no separate install line.
#   Delivery is NOT in the contract: Dr.Coffee charge £69 per machine (half
#   pallet, next day, mainland GB) — Alex, 2 Sep: "you've costed up for each
#   machine, the installation/delivery charge, the annual comp servicing".
#   (cost-in + fridge + delivery 69 + head 22 + wrap 450 + counter 200 +
#   contract × years) / 0.45 over the term, rounded DOWN to a clean 5:
#     C2  24: 4,025.25 → 372.7 → 370   36: 4,775.25 → 294.8 → 290
#     C5  24: 5,170.25 → 478.7 → 475   36: 6,070.25 → 374.7 → 370
#     C6  24: 7,960.25 → 737.1 → 735   36: 8,955.25 → 552.8 → 550
#     C8  24: 8,285.25 → 767.2 → 765   36: 9,280.25 → 572.9 → 570
#   `buy` = Dr.Coffee UK RRP (2,050 / 3,350 / 7,350 / 7,850) — a 35% line at
#   the 1–4 tier, the dealer structure the sheet itself defines.
#   PURCHASE EXTRAS, each ≥ 30% on its own cost (the SG rule):
#     fridge 695 on 451.75 (35%) · install+filter 550 on 379 [Dr.Coffee install
#     150 + delivery 69 + C500 138 + head 22] (31%) · year-one servicing 495 on 340 [two PPM
#     visits at 170] (31%) · cover per year 1,095 / 1,295 / 1,425 / 1,425 on
#     the contract 750 / 900 / 995 / 995 (31.5 / 30.5 / 30.2 / 30.2%) · wrap
#     595 on 450 (24% — a one-off, kept) · counter 595 on ~200 · callouts 175
#     + 75/hr (Dr.Coffee: 150 first hour + 35 per half hour).
#   The 3-year rung gives the wrap and counter free (global rule, Alex's
#   coffee-annuity call): F16 = 495 + 2 × 1,095 = 2,685 on 340 + 1,500 + 450
#   + 200 = 2,490 → 7%. Deliberate; recorded, not hidden.
#   The cover plans' "2 on-site coffee calibration sessions a year" — Alex,
#   2 Sep: "we'll have the engineer do it during visits", i.e. Dr.Coffee's two
#   PPM visits carry the calibration; no separate NoFilter visit, no extra cost.
#   YEAR-ONE LABOUR ON A PLAN: the plan says "from day one" but year one is
#   costed as two PPM visits (340), not the contract, so a year-one breakdown
#   callout (150 + 35 per half-hour) is NoFilter's. Alex, 2 Sep: "ok leave
#   it" — carried as a known risk against the ~31% rung; revisit with a year
#   of callout history.
#   KNOWN GAP: Dr.Coffee UK's 12-month warranty is PARTS ONLY; the card's
#   "Standard care · 1-year parts & labour" means NoFilter carries year-one
#   labour on a purchase (Dr.Coffee callout 150 + 35 per half hour).

# ── 1 · the market ────────────────────────────────────────────────────────
old = """  UK: { k:'UK', name:'UNITED KINGDOM', short:'UK', where:'the UK', priced:false, use:'SG' }"""
new = """  UK: { k:'UK', name:'UNITED KINGDOM', short:'UK', where:'the UK', cur:'GBP', loc:'en-GB',
        priced:true, tax:'VAT', email:'alex@nofilter.sg',
        /* UK ENTITY NOT YET CONFIRMED — placeholder line, replace before quoting */
        entity:'NoFilter Ltd · UK company number to follow',
        /* block 78 — coffee DERIVED 2 Sep 2026 from Alex's cost base: green
           SGD 16 landed (£9.28) ÷ 0.80 roast loss, Coffee by Tate roasting at
           the worst tier (£4 per green kg = £5 roasted), packing, DHL and
           last-mile — and, because the UK entity is NOT VAT-registered, the
           20% on every one of those as a real cost: £23.17 all-in per roasted
           kg. Priced just under SG-parity net — Alex: the wrap, counter and
           NGO contribution defend a higher price than the 30% floor, but the
           floor should sit "right at the end of the high 30s". Floor 39 at 5%
           nets 35.6%, default 41 at 7.5% 36.0%, full 43 at 10% 36.1%, ceiling
           46 at 10% 39.6% (SG: 36.4 / 37.5 / 38.3 / 42.0%). */
        bag250:21.00, bag1kg:69.00,
        kg:{ floor:39.00, def:41.00, ceil:46.00, step:0.25, full:43.00 },
        cup:{ sym:'p', word:'pence', one:'penny', topMax:6.5, topStep:0.1, ten:9, stretch:10 },
        bands:[ { id:1, from:39.00, to:40.99, rate:0.050, label:'BAND 01', range:'39.00–40.99' },
                { id:2, from:41.00, to:42.99, rate:0.075, label:'BAND 02', range:'41.00–42.99' },
                { id:3, from:43.00, to:46.00, rate:0.100, label:'BAND 03', range:'43.00+' } ],
        /* UK RATE CARD — derived 2 Sep 2026 from the Dr.Coffee UK distributor
           price list (1 June 2026), trade cost at the 1–4 unit tier (35% off
           RRP) because the first UK orders are one or two machines: F16
           1,332.50 · Coffee Zone T 2,177.50 · F30 H 4,777.50 · F30 Plus
           5,102.50 · SC12 fridge 451.75 (5+ is 37% off — upside). Rental: (cost-in + fridge + delivery 69
           + filter head 22 + wrap 450 + counter 200 + Dr.Coffee UK's Annual
           Comprehensive Service Contract for EVERY year of the term, year one
           included — it carries the install and training) / 0.45 over the
           term, rounded DOWN to a clean 5. The contract is F16 750 · Zone 900
           · F30 995 a year, so the UK fleet is serviced by the importer from
           day one, not by us. `buy` is Dr.Coffee UK RRP. Ex VAT. */
        mach:{ cm2:{ r24:370, r36:290, buy:2050 },
               cm5:{ r24:475, r36:370, buy:3350 },
               cm6:{ r24:735, r36:550, buy:7350 },
               cm8:{ r24:765, r36:570, buy:7850 } },
        /* cover per machine per year = the Dr.Coffee UK contract at ≥ 30%
           margin (750 → 1,095 · 900 → 1,295 · 995 → 1,425) */
        cover:{ cm2:1095, cm5:1295, cm6:1425, cm8:1425 },
        installLabel:'Delivery, install &amp; water filter',
        buyx:{ cooler:695, install:550, svc1:495,
               svcYr1:1590, svcYr:1295, wrap:595, wrapOff:250,
               calloutBase:175, calloutHr:75, counter:595, wrapFreeFrom:24 },
        /* the Dr.Coffee models that stand in for the CafeMatics on this card.
           Photos: Alex is sourcing them — drop the files in _CDN-UPLOAD-SAFE
           under these names and they appear; until then the photo well is
           blank (onerror hides the broken image). */
        machMeta:{
          cm2:{ name:'Dr.Coffee F16', spec:['1 grinder','Fresh-milk drinks','8L tank or plumbed'],
                specLine:'1 grinder · fresh-milk drinks · 8L tank or plumbed',
                img:'../../_CDN-UPLOAD-SAFE/drcoffee-f16-w1400.webp' },
          cm5:{ name:'Dr.Coffee Coffee Zone T', spec:['1 grinder','2 powder hoppers','Steam wand + hot water'],
                specLine:'1 grinder · 2 powder hoppers · steam wand + hot water',
                img:'../../_CDN-UPLOAD-SAFE/drcoffee-coffee-zone-t-w1400.webp' },
          cm6:{ name:'Dr.Coffee F30 H', spec:['2 grinders','Two beans side by side','No powder'],
                specLine:'2 grinders · two beans side by side · no powder',
                img:'../../_CDN-UPLOAD-SAFE/drcoffee-f30-h-w1400.webp' },
          cm8:{ name:'Dr.Coffee F30 Plus', spec:['2 grinders','2 powder hoppers','The fullest menu'],
                specLine:'2 grinders · 2 powder hoppers · the fullest menu',
                img:'../../_CDN-UPLOAD-SAFE/drcoffee-f30-plus-w1400.webp' } },
        machNote:'UK card, ex VAT. Dr.Coffee machines and fridge priced off the Dr.Coffee UK ' +
                 'trade list; install includes the water filter; servicing is Dr.Coffee UK\\'s ' +
                 'comprehensive contract. Rental is fully serviced and includes the milk fridge, ' +
                 'livery wrap and the live impact counter. Purchase is the machine only.' }"""
assert src.count(old) == 1, "UK market anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 2 · applyMarket swaps the machine identity with the market ───────────
old = """  MACHINES.forEach(function(m){
    var r = MKT.mach[m.k];
    m.r24 = r.r24; m.r36 = r.r36; m.buy = r.buy; m.price = r.r36;
  });
  Q.price = MKT.kg.def;"""
new = """  MACHINES.forEach(function(m){
    var r = MKT.mach[m.k];
    m.r24 = r.r24; m.r36 = r.r36; m.buy = r.buy; m.price = r.r36;
    /* block 78 — a market may put a different machine on the same rung (the
       UK sells Dr.Coffee, not CafeMatic). The catalogue defaults are kept on
       the machine the first time through, then either the override or the
       default is written back, and every place the identity is printed is
       repainted. Rates above are untouched by this. */
    if(!m.__def) m.__def = { name:m.name, forWho:m.forWho, spec:m.spec, specLine:m.specLine, img:m.img };
    var o = (MKT.machMeta && MKT.machMeta[m.k]) || {};
    ['name','forWho','spec','specLine','img'].forEach(function(f){ m[f] = (o[f] != null) ? o[f] : m.__def[f]; });
  });
  (function(){
    MACHINES.forEach(function(m, i){
      var card = $('.q-eq-card[data-m="' + m.k + '"]');
      if(card){
        var set = function(q, t){ var e = $(q, card); if(e) e.textContent = t; };
        set('.q-eq-name', m.name); set('.mx-size-badge', m.forWho);
        set('.q-eq-loc', m.spec.slice(0,2).join(' · ')); set('.q-eq-spec', m.specLine);
        var im = $('.q-eq-photo img', card);
        if(im && im.getAttribute('src') !== m.img){ im.style.display = ''; im.src = m.img; im.alt = m.name + ' bean-to-cup machine in NoFilter livery'; }
        var sb = $('.mx-specs-btn', card); if(sb) sb.setAttribute('aria-label', 'See full details for ' + m.name);
      }
      var g = $$('#machGrid .mach')[i];
      if(g){
        var set2 = function(q, t){ var e = $(q, g); if(e) e.textContent = t; };
        set2('.mn', m.name); set2('.mbd .lab', m.forWho);
        var ul = $('ul', g); if(ul) ul.innerHTML = m.spec.map(function(s){ return '<li>' + s + '</li>'; }).join('');
        var gi = $('.mimg img', g);
        if(gi && gi.getAttribute('src') !== m.img){ gi.style.display = ''; gi.onerror = function(){ this.style.display = 'none'; }; gi.src = m.img; gi.alt = m.name; }
      }
      var tr = $$('#machTable tbody tr')[i];
      if(tr){ var td = $$('td', tr); if(td[0]) td[0].textContent = m.name; if(td[1]) td[1].textContent = m.forWho; if(td[2]) td[2].textContent = m.specLine; }
    });
  })();
  Q.price = MKT.kg.def;"""
assert src.count(old) == 1, "applyMarket mach anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 3 · the spec sheet names the machine the market sells ─────────────────
old = """    nameEl.textContent=machine;
    capEl.textContent=CAP[machine].replace(/&amp;/g,'&');
    imgEl.style.opacity=''; imgEl.src='../../_CDN-UPLOAD-SAFE/cafematic-'+SLUG[machine].slice(2)+'.png';"""
new = """    /* block 78 — the sheet is keyed by the CafeMatic name, but the tile that
       opened it may be a Dr.Coffee (UK). Print the live name, and the live
       photo when the market has swapped it. The rows beneath describe the
       same machine either way — it is the same factory's product. */
    var __live = null, __mk = window.__nfMkt ? window.__nfMkt() : null;
    (window.__nfMachines || []).forEach(function(m){ if(SLUG[machine] && SLUG[machine] === m.k) __live = m; });
    nameEl.textContent = (__live && __live.name) || machine;
    capEl.textContent=CAP[machine].replace(/&amp;/g,'&');
    imgEl.style.opacity='';
    imgEl.src = (__live && __mk && __mk.machMeta && __mk.machMeta[__live.k]) ? __live.img
              : '../../_CDN-UPLOAD-SAFE/cafematic-'+SLUG[machine].slice(2)+'.png';"""
assert src.count(old) == 1, "spec sheet anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 4 · the UK flag is a live market now ──────────────────────────────────
old = """        <button type="button" data-mkt="UK" class="pend" aria-pressed="false" title="United Kingdom · not yet trading"
                aria-label="United Kingdom market, not yet trading -- Singapore card shown for reference">"""
new = """        <button type="button" data-mkt="UK" aria-pressed="false" title="United Kingdom · GBP"
                aria-label="UK market, prices in GBP">"""
assert src.count(old) == 1, "UK button anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 5 · the header note stops calling the UK unpriced ─────────────────────
old = """   UK  — NOT a priced market. No entity, no rate card, no finance partner. It
         renders the Singapore card as reference and says so, loudly. Do not
         invent GBP figures here; the whole proposition is that we do not make
         numbers up."""
new = """   UK  — PRICED from 2 Sep 2026 (block 78). Machines are Dr.Coffee's UK trade
         list run through the SG formula; coffee is derived from Alex's cost
         base (green SGD 16 landed, 20% roast loss, roasting at the worst
         £5/kg tier, VAT unrecoverable — the entity is not registered).
         Entity line and machine photos still to come."""
assert src.count(old) == 1, "header note anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 6 · the catalogue is reachable from outside the runtime IIFE ──────────
old = """var MXKEY = { cm2:'Caf\\u00e9matic 2', cm5:'Caf\\u00e9matic 5', cm6:'Caf\\u00e9matic 6', cm8:'Caf\\u00e9matic 8' };"""
new = old + """
/* block 78 — the spec sheet lives outside this IIFE and needs the live names */
window.__nfMachines = MACHINES;"""
assert src.count(old) == 1, "MXKEY anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)


# ── 7 · the quote deck's market chips get the UK flag ─────────────────────
# Alex, 2 Sep: "don't we now need to add the UK flag in the quote builder".
# The deck's chips were SG and AE only; the rail had all three. Same flag
# markup as the rail button, same delegation (the click forwards to the rail).
old = """    +   '<button type="button" class="dt-mkt-b" data-deckmkt="AE"'
    +     ' title="United Arab Emirates \\u00b7 AED" aria-label="UAE market, prices in AED">'
    +     '<span class="mkflag"><svg viewBox="0 0 30 20" aria-hidden="true">'
    +     '<rect width="30" height="6.67" fill="#00732F"/><rect y="6.67" width="30" height="6.66" fill="#fff"/>'
    +     '<rect y="13.33" width="30" height="6.67" fill="#000"/><rect width="7.5" height="20" fill="#FF0000"/>'
    +     '</svg></span></button>'
    + '</div>';"""
new = """    +   '<button type="button" class="dt-mkt-b" data-deckmkt="AE"'
    +     ' title="United Arab Emirates \\u00b7 AED" aria-label="UAE market, prices in AED">'
    +     '<span class="mkflag"><svg viewBox="0 0 30 20" aria-hidden="true">'
    +     '<rect width="30" height="6.67" fill="#00732F"/><rect y="6.67" width="30" height="6.66" fill="#fff"/>'
    +     '<rect y="13.33" width="30" height="6.67" fill="#000"/><rect width="7.5" height="20" fill="#FF0000"/>'
    +     '</svg></span></button>'
    /* block 78 — the UK is a priced market now; same flag as the rail */
    +   '<button type="button" class="dt-mkt-b" data-deckmkt="UK"'
    +     ' title="United Kingdom \\u00b7 GBP" aria-label="UK market, prices in GBP">'
    +     '<span class="mkflag"><svg viewBox="0 0 30 20" aria-hidden="true">'
    +     '<rect width="30" height="20" fill="#012169"/>'
    +     '<path d="M0,0 30,20 M30,0 0,20" stroke="#fff" stroke-width="4"/>'
    +     '<path d="M0,0 30,20 M30,0 0,20" stroke="#C8102E" stroke-width="2.2"/>'
    +     '<path d="M15,0 V20 M0,10 H30" stroke="#fff" stroke-width="6.6"/>'
    +     '<path d="M15,0 V20 M0,10 H30" stroke="#C8102E" stroke-width="4"/>'
    +     '</svg></span><span class="dt-mkt-t">GBP</span></button>'
    + '</div>';"""
assert src.count(old) == 1, "deck chip anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)


# ── 8 · three UK-only lines of copy and the VAT label ─────────────────────
# Alex, 2 Sep: "re: vat if i register i don't immediately have to apply for it
# so leave it off for now. update it to parts for uk. on change to 10L then."
# The market carries the three strings; SG and AE keep theirs. An empty tax
# label prints nothing rather than "EX " + nothing.
old = """      0:['1-year coverage on parts &amp; labour',"""
new = """      0:[(MKT.warrantyLine || '1-year coverage on parts &amp; labour'),"""
assert src.count(old) == 1, "warranty row anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """               'Direct-fit 6L cooler sitting alongside the unit',"""
new = """               (MKT.fridgeSub || 'Direct-fit 6L cooler sitting alongside the unit'),"""
assert src.count(old) == 1, "fridge sub anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """  setT('#specHd',  MKT.cur + ' · PER MONTH · EX ' + MKT.tax);"""
new = """  setT('#specHd',  MKT.cur + ' · PER MONTH' + (MKT.tax ? ' · EX ' + MKT.tax : ''));"""
assert src.count(old) == 1, "specHd anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """  set('qTaxLabel', MKT.tax);"""
new = """  set('qTaxLabel', MKT.tax);
  /* block 78 — an unregistered market has no tax to be "ex" of */
  (function(){ var t = $('#qTaxLabel'); if(!t) return; var n = t.previousSibling;
     if(n && n.nodeType === 3){ if(!t.__exTxt) t.__exTxt = n.textContent;
       n.textContent = MKT.tax ? t.__exTxt : t.__exTxt.replace(/Ex-\s*$/, ''); } })();"""
assert src.count(old) == 1, "qTaxLabel anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """        priced:true, tax:'VAT', email:'alex@nofilter.sg',
        /* UK ENTITY NOT YET CONFIRMED — placeholder line, replace before quoting */"""
new = """        priced:true, tax:'', email:'alex@nofilter.sg',
        /* tax is EMPTY on purpose: the UK entity is not VAT-registered, so no
           VAT is charged and nothing is "ex VAT" — Alex, 2 Sep: "leave it off
           for now". Set to 'VAT' the day registration goes live. */
        warrantyLine:'1-year coverage on parts',      /* Dr.Coffee UK: parts only */
        fridgeSub:'Direct-fit 10L cooler sitting alongside the unit',   /* SC12 */
        /* UK ENTITY NOT YET CONFIRMED — placeholder line, replace before quoting */"""
assert src.count(old) == 1, "UK head anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)


# ── 9 · the deck's market switch as a currency segmented control ──────────
# Alex, 2 Sep: "find this selector rather ugly". Three flag tiles with a grey
# frame for the chosen one read as a badge row. It is a currency choice, so it
# says so: one pill, three segments, flag as a small leading glyph, the
# currency code in the deck's own mono caps, the live one filled orange like
# every other pressed control beside it (24mo / 36mo). Same buttons, same
# delegation to the rail — only the paint changes.
old = """    +     '<circle cx="9.5" cy="4.2" r=".62"/></g></svg></span></button>'
    +   '<button type="button" class="dt-mkt-b" data-deckmkt="AE\""""
new = """    +     '<circle cx="9.5" cy="4.2" r=".62"/></g></svg></span><span class="dt-mkt-t">SGD</span></button>'
    +   '<button type="button" class="dt-mkt-b" data-deckmkt="AE\""""
assert src.count(old) == 1, "SG chip anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
old = """    +     '<rect y="13.33" width="30" height="6.67" fill="#000"/><rect width="7.5" height="20" fill="#FF0000"/>'
    +     '</svg></span></button>'
    /* block 78 — the UK is a priced market now; same flag as the rail */"""
new = """    +     '<rect y="13.33" width="30" height="6.67" fill="#000"/><rect width="7.5" height="20" fill="#FF0000"/>'
    +     '</svg></span><span class="dt-mkt-t">AED</span></button>'
    /* block 78 — the UK is a priced market now; same flag as the rail */"""
assert src.count(old) == 1, "AE chip anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 79 · THE MARKET SWITCH SAYS WHAT IT IS ═══════════════════════════════
   A currency segmented control. Overrides block 53's flag tiles by source
   order at the same specificity. */
#nfConsoleWrap .dt-mkt{gap:0;padding:2px;border:1px solid rgba(26,24,21,.22);border-radius:999px;
  background:rgba(255,255,255,.35);}
#nfConsoleWrap .dt-mkt-b{
  display:inline-flex;align-items:center;gap:6px;padding:4px 11px 4px 7px;min-width:0;
  border:0;border-radius:999px;background:transparent;
  font-family:var(--font-m,monospace);font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;
  color:rgba(26,24,21,.62);line-height:1;
  transition:background .18s ease,color .18s ease;}
#nfConsoleWrap .dt-mkt-b .mkflag{width:16px;height:11px;border-radius:2px;opacity:.7;
  box-shadow:0 0 0 1px rgba(26,24,21,.18);transform:none;}
#nfConsoleWrap .dt-mkt-b .dt-mkt-t{display:inline-block;}
#nfConsoleWrap .dt-mkt-b:hover{background:rgba(26,24,21,.06);color:var(--nb,#1A1815);border-color:transparent;transform:none;}
#nfConsoleWrap .dt-mkt-b:hover .mkflag{opacity:.9;}
#nfConsoleWrap .dt-mkt-b[aria-pressed="true"]{background:var(--or,#EE4D17);color:#fff;border-color:transparent;}
#nfConsoleWrap .dt-mkt-b[aria-pressed="true"] .mkflag{opacity:1;transform:none;box-shadow:0 0 0 1px rgba(255,255,255,.55);}
#nfConsoleWrap .dt-mkt-b:focus-visible{outline:2px solid var(--or,#EE4D17);outline-offset:2px;}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)


# ── 10 · the 3-year rung carries the extras it gives away (UK) ────────────
# Alex, 2 Sep: "make servicing margin at least 15-20% imo". The 3-year plan
# includes the wrap (450) and counter (~200) free; at the UK's cover rates
# that rung ran at 7-11%. A market may now add a fixed amount to the 3-year
# rung only — the 2-year rung and the cover rates are untouched. First cut
# 450 (20-21%); then Alex: "if anything it should be more" — the parts risk
# under a UK plan is Dr.Coffee's (their contract covers parts and labour), so
# the rung earns the card's 30% like every other line. UK: 950 → F16 3,635
# on 2,490 (31.5%) · Zone T 4,035 on 2,790 (30.9%) · F30s 4,295 on 2,980
# (30.6%). SG and AE carry no plan3Add, so nothing moves there.
old = """function svcPlanCost(m, yrs){
  var y = Math.max(2, Math.min(3, yrs | 0));
  var x = buyExtras();
  return (x.svc1 || 0) + coverRate(m) * (y - 1);
}"""
new = """function svcPlanCost(m, yrs){
  var y = Math.max(2, Math.min(3, yrs | 0));
  var x = buyExtras();
  /* block 78 — a market may price the wrap and counter the 3-year rung
     includes, rather than give them away below cost (UK: plan3Add) */
  return (x.svc1 || 0) + coverRate(m) * (y - 1) + ((y >= 3 && x.plan3Add) ? x.plan3Add : 0);
}"""
assert src.count(old) == 1, "svcPlanCost anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
old = """        buyx:{ cooler:695, install:550, svc1:495,"""
new = """        buyx:{ cooler:695, install:550, svc1:495, plan3Add:950,"""
assert src.count(old) == 1, "buyx UK anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("UK card built")
