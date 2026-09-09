import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 77 · THE AED CARD, DERIVED ════════════════════════════════════════════
# Alex, 2 Sep: "let's go price up the machinery rental/purchase options for
# AED as what we have is likely wrong" — then three Boncafé Middle East
# quotations (BCSC 020525-1, 150825-1, 150925-1, all "(PG) SAUCY BEAN") and
# the VAH General Trading tax invoice INV-202511-0300 of 10 Nov 2025.
#
# What the documents say, AED, ex VAT:
#
#                          list      special        transacted (Nov 25)
#   Cafematic 2            6,600     5,950 (×12)    —
#   Cafematic 5           13,000    11,310 (×7)     11,700  (−10%)
#   Cafematic 8           19,200    16,705 (×7)     —
#   SC08 milk cooler       1,900     1,655 / 1,710   1,710  (−10%)
#   SC10 milk cooler       2,490     2,241 (−10%)    —      (C5 / C5 Plus only)
#   BEST Protect XL filter   935     no discount     —      (direct water option)
#
#   Delivery & installation   complimentary, one-time, UAE city limits, within
#                             6 months of invoice. Outside city limits: transport
#                             extra. Machine relocation/reinstall excluded.
#   Servicing / AMC           NOT PRICED on any document. 12 months parts & labour
#                             warranty from invoice; year 2/3 extended warranty
#                             purchasable "at additional cost" and ONLY with a
#                             periodic maintenance contract. Scale damage from poor
#                             water is a warranty exclusion.
#   VAT                       5% on everything; every price above is ex VAT.
#   Storage                   1 week free; AED 800 + VAT / month after 4 weeks.
#   Terms                     100% in advance, ex-Dubai warehouse, valid 30 days.
#
# Cost-in is taken at 10% off list — the discount NoFilter actually transacts
# at 3–4 units. The 7-and-12-piece specials (≈13% off) are upside, not the base.
#
# Same formula as SG: (cost-in + cooler + install + wrap + servicing/yr for
# years 2..n) / 0.45, over the term, rounded DOWN to a clean 5.
#
#   cooler     1,710   SC08 at the transacted 10% (the invoice paired it with C5)
#   install      935   the BEST Protect XL filter set — Alex, 2 Sep: "the filter price
#                      that should be part of the install". Boncafé's own delivery
#                      and installation are complimentary; the filter is not.
#   wrap       2,200   SG cost 750 at ~2.85 SGD→AED, rounded UP to a nice number
#   servicing  3,000   SG provision 1,000 at ~2.85, rounded UP. Alex, 2 Sep: "keep
#                      servicing same structure and price, just AED equivalent
#                      rounded up to a nice number". Carries the ~735/yr cartridge.
#
#   C2   cost-in  5,940   24mo (13,785/0.45)/24 = 1,276 → 1,275   36mo (16,785/0.45)/36 = 1,036 → 1,035
#   C5   cost-in 11,700   24mo (19,545/0.45)/24 = 1,810 → 1,805   36mo (22,545/0.45)/36 = 1,392 → 1,390
#   C8   cost-in 17,280   24mo (25,125/0.45)/24 = 2,326 → 2,325   36mo (28,125/0.45)/36 = 1,736 → 1,735
#   C6   on no Boncafé document. BeanBurds retail 14,600 (C5/C8 there sit exactly
#        on Boncafé list, so taken as list); cost-in 13,140 → 1,940 / 1,480.
#
# `buy` is NOT list here. The Microsoft Gulf quote (06.10.25, approved) sold a
# C5 + milk cooler at USD 5,120 = AED 18,803; less the cooler at 1,900 that is
# 16,900 for the machine, 1.30 × Boncafé list (BeanBurds retail is exactly list,
# so a purchase at list would be a 10% line). The other three take the same
# 1.30: C2 8,600 · C6 19,000 · C8 25,000, clean hundreds. Microsoft also paid
# USD 300 (AED 1,100) for the year-one water filter, which is what buyx.install
# charges, and USD 200 (AED 735) a year for the cartridge from year two — the
# servicing provision has to carry that.
#
# The old note called CM8/36 at 1,211.89 "transacted". Under the inputs above
# that price is a 40% margin (25,990/0.6/36 = 1,203), not 45%.

old_start = src.index("        /* AED PASS STILL OWED. These are NOT a re-priced card")
old_end   = src.index("'(AED 1,211.89/mo) is a transacted figure; the rest scale from it.' },") \
            + len("'(AED 1,211.89/mo) is a transacted figure; the rest scale from it.' },")
new = """        /* AE RATE CARD — derived 2 Sep 2026 from Boncafé Middle East quotations
           BCSC 020525-1 / 150825-1 / 150925-1 and tax invoice INV-202511-0300.
           Same formula as SG: (cost-in + cooler 1,710 + install 935 + wrap 2,200
           + servicing 3,000/yr for years 2..n) / 0.45, over the term, rounded
           DOWN to a clean 5. Cost-in is Boncafé ME list less the 10% NoFilter
           transacts at: C2 5,940 · C5 11,700 · C8 17,280. Boncafé's delivery
           and installation are complimentary (UAE city limits, within 6 months
           of invoice); the 935 "install" is the BEST Protect XL water filter
           set, which Alex counts as part of the install.
           Wrap 2,200 and servicing 3,000/yr are the SG cost lines (750 and
           1,000) at ~2.85 SGD→AED, rounded UP — Alex, 2 Sep: "keep servicing
           same structure and price, just AED equivalent rounded up to a nice
           number". Boncafé ME priced NO servicing on any document (12-month
           warranty, extended warranty "at additional cost" and only with a
           maintenance contract), and the 3,000 also carries the ~735/yr
           filter cartridge Microsoft pays from year two. C6 is on no Boncafé document; its list is BeanBurds retail
           (14,600, 2 Sep 2026 — BeanBurds sells C5 and C8 at exactly Boncafé
           list, so it is taken as list): cost-in 13,140 → 1,790 / 1,345.
           `buy` is the Microsoft Gulf precedent (quote 06.10.25, approved):
           C5 + cooler at USD 5,120 = AED 18,803, i.e. 16,900 for the machine
           = 1.30 × Boncafé list; the other three take the same 1.30, clean
           hundreds. All figures ex VAT (5%). */
        mach:{ cm2:{ r24:1275, r36:1035, buy:8600  },
               cm5:{ r24:1805, r36:1390, buy:16900 },
               cm6:{ r24:1940, r36:1480, buy:19000 },
               cm8:{ r24:2325, r36:1735, buy:25000 } },
        /* cover and every servicing extra are the SG card at ~2.85 SGD→AED,
           each rounded UP to a nice number (SG in brackets): cover 750/1,800/
           2,200/2,400 → 2,200/5,200/6,300/7,000; svc1 750 → 2,200; svcYr1
           1,250 → 3,600; svcYr 1,750 → 5,000; wrap 1,000 → 3,000; wrapOff 400
           → 1,200; callouts 200 + 50/hr → 600 + 150/hr; counter 1,000 → 3,000.
           Same structure, same price, AED. cooler is the SC08 list price a
           buyer pays (NoFilter pays 1,710). install is the water filter:
           Boncafé delivers and installs free, Microsoft paid USD 300
           (AED 1,100) for the year-one BWT filter, cost 935. */
        cover:{ cm2:2200, cm5:5200, cm6:6300, cm8:7000 },
        installLabel:'Delivery, install &amp; water filter',
        buyx:{ cooler:1900, install:1100, svc1:2200,
               svcYr1:3600, svcYr:5000, wrap:3000, wrapOff:1200,
               calloutBase:600, calloutHr:150, counter:3000, wrapFreeFrom:24 },
        machNote:'UAE card, ex VAT. Machines and fridge priced off Boncafé Middle East ' +
                 'quotations; install includes the water filter. Rental is fully ' +
                 'serviced and includes the milk fridge, livery wrap and the live impact ' +
                 'counter. Purchase is the machine only.' },"""
src = src[:old_start] + new + src[old_end:]

# ── a fixed row at 0 reads "included", not "AED 0.00" ─────────────────────
old = """        } else if(r.fixed){                           /* true, and not up for debate */
          val = CUR() + money(r.buy); cls = ' is-fixed';"""
new = """        } else if(r.fixed){                           /* true, and not up for debate */
          /* block 77 — the UAE installs free; a fixed row at zero is a fact,
             not a price, and "AED 0.00" would read as a placeholder. */
          val = r.buy ? CUR() + money(r.buy) : 'included'; cls = ' is-fixed';"""
assert src.count(old) == 1, "fixed row anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the quote sheet's baseline line drops "+ install AED 0.00" ────────────
old = """      machLines.push({ n: 'Machine · ' + CUR() + money(m.buy) + ' + install '
                         + CUR() + money(x.install) + ' · baseline',"""
new = """      machLines.push({ n: 'Machine · ' + CUR() + money(m.buy)
                         + (x.install ? ' + install ' + CUR() + money(x.install)
                                      : ' · install included')
                         + ' · baseline',"""
assert src.count(old) == 1, "baseline line anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the install row names the filter where the market charges for it ──────
old = """        { k:'install', nm:'Delivery &amp; installation', fixed:true, buy:x.install },"""
new = """        { k:'install', nm:(MKT && MKT.installLabel) || 'Delivery &amp; installation', fixed:true, buy:x.install },"""
assert src.count(old) == 1, "install row anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("AED card derived")
