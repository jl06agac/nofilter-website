import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 84 · THE UK IN THE FOOTER, AND NO TALK OF AN OFFICE ═══════════════════
# Alex, 2 Sep: "add it, don't mention office to be announced, i don't need an
# office, just accepting uk enquiries". The footer had Singapore and the UAE
# and, beside them, "Showing prices for UK · GBP" over nothing. A third entity
# column now says who answers a UK enquiry — the Singapore company, until a
# deal makes a UK one worth registering (Alex, 2 Sep) — and the quote sheet's
# UK address line drops the office it was promising.
fix("""        addr:'UK office to be announced · now accepting UK enquiries · alex@nofilter.sg',""",
    """        addr:'Now accepting UK enquiries · alex@nofilter.sg',""")

fix("""        <p class="foot-mail"><a href="mailto:hello@nofilter.ae">hello@nofilter.ae</a></p>
      </div>
      <div class="foot-ent foot-ent-mkt">""",
    """        <p class="foot-mail"><a href="mailto:hello@nofilter.ae">hello@nofilter.ae</a></p>
      </div>
      <!-- block 84 — UK enquiries are answered by the Singapore company -->
      <div class="foot-ent">
        <span class="region">United Kingdom</span>
        <p>NoFilter Pte. Ltd<br>
           Now accepting UK enquiries</p>
        <p class="foot-mail"><a href="mailto:alex@nofilter.sg">alex@nofilter.sg</a></p>
      </div>
      <div class="foot-ent foot-ent-mkt">""")

# four columns on the wide footer; the 820px rule already pairs them and
# lets the market line take the full width
fix(""".foot-entities{grid-column:1/-1;display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(20px,3.4vw,64px);""",
    """.foot-entities{grid-column:1/-1;display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));gap:clamp(20px,3.4vw,64px);   /* block 84: 3 → 4 */""")

# ══ 85 · THE QUOTE EMAIL KNOWS WHAT THE READER CHOSE, PER KILO ════════════
# Alex, 2 Sep: "is the email system related to quote builder now working?"
# It is wired — quote-confirm (Resend, to the reader and to the desk) and the
# Netlify Forms backstop both fire from the master — but the 29/30 Aug bundles
# posted five more figures than this master did, and quote-confirm.js prints
# them in the desk email: the price per kilo, the band rate, the top-up per
# kilo, the conservation per kilo and the cups a year the volume implies.
# This master's compute() has each of them under its own names (Q.price,
# band.rate, topPerKg, bandPerKg + topPerKg, kgTotal at 18 g a cup); they are
# mapped to the names the function reads, so the desk email is whole again.
fix("""          contrib:  (c && c.contrib != null) ? c.contrib : null,
          kg:       (c && c.kgTotal != null) ? c.kgTotal : null
        })
      }).catch(function(){});""",
    """          contrib:  (c && c.contrib != null) ? c.contrib : null,
          kg:       (c && c.kgTotal != null) ? c.kgTotal : null,
          /* block 85 — the per-kilo figures the desk email prints */
          price:     (typeof Q === 'object' && Q.price != null) ? Q.price : null,
          rate:      (c && c.band && c.band.rate != null) ? c.band.rate : null,
          topUpKg:   (c && c.topPerKg) ? c.topPerKg : null,
          topUpMo:   (c && c.topPerKg && c.kgTotal) ? c.topPerKg * c.kgTotal : null,
          consPerKg: (c && c.bandPerKg != null) ? c.bandPerKg + (c.topPerKg || 0) : null,
          cupsY:     (c && c.kgTotal) ? Math.round(c.kgTotal * 12 * 1000 / 18) : null
        })
      }).catch(function(){});""")

fix("""        band_rate         : (band.rate != null) ? String(band.rate) : '',""",
    """        band_rate         : (band.rate != null) ? String(band.rate) : '',
        /* block 85 — same per-kilo figures as the confirmation email */
        coffee_price_kg   : (typeof Q === 'object' && Q.price != null) ? String(Q.price) : '',
        topup_kg          : (c && c.topPerKg) ? String(c.topPerKg) : '',
        conservation_kg   : (c && c.bandPerKg != null) ? String(c.bandPerKg + (c.topPerKg || 0)) : '',""")

io.open(F, "w", encoding="utf-8").write(src)
print("UK footer column; quote email per-kilo figures")
