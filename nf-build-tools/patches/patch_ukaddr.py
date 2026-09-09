import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 82 · THE UK QUOTE SHEET'S ISSUER AND ADDRESS ══════════════════════════
# Alex, 2 Sep: "GBP, where the office details are i think we can state
# 'accepting enquiries' or the like, given we don't have an address yet" —
# and, asked which entity issues a UK quote: NoFilter Pte. Ltd (SG), trading
# in the UK until a UK company exists.
# Two things were wrong before this block: the UK entity line was a draft
# placeholder ("UK company number to follow"), and the address line under it
# fell through to the Singapore street address because that code only knew
# SG and AE. Each market now carries its own `addr`; the UK one says where
# the office stands (to be announced), that enquiries are open, and how to
# reach us — an address line's job, done without an address.
def fix(old, new):
    global src
    n = src.count(old)
    assert n == 1, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

fix("""        entity:'NoFilter Pte. Ltd · UEN 201839882N',
        bag250:24.00, bag1kg:80.00,""",
    """        entity:'NoFilter Pte. Ltd · UEN 201839882N',
        addr:'31 Kaki Bukit Road 3 · #01-02C Techlink · Singapore 417818',
        bag250:24.00, bag1kg:80.00,""")

fix("""        entity:'NoFilter LLC · Sharjah Media City (Shams) · TL 2540001.01',
        bag250:77.50, bag1kg:232.50,""",
    """        entity:'NoFilter LLC · Sharjah Media City (Shams) · TL 2540001.01',
        addr:'Sharjah Media City (Shams) · Sharjah, United Arab Emirates',
        bag250:77.50, bag1kg:232.50,""")

fix("""        /* UK ENTITY NOT YET CONFIRMED — placeholder line, replace before quoting */
        entity:'NoFilter Ltd · UK company number to follow',""",
    """        /* block 82 — UK quotes issue from the Singapore company, trading in the
           UK, until a UK entity exists (Alex, 2 Sep). No UK premises yet, so
           the address line says so and gives the route in. Swap `addr` for
           the street address the day there is one. */
        entity:'NoFilter Pte. Ltd · UEN 201839882N',
        addr:'UK office to be announced · now accepting UK enquiries · alex@nofilter.sg',""")

fix("""  if(addr) addr.textContent = MKTK === 'AE'
      ? 'Sharjah Media City (Shams) · Sharjah, United Arab Emirates'
      : '31 Kaki Bukit Road 3 · #01-02C Techlink · Singapore 417818';""",
    """  /* block 82 — each market carries its own address line; the SG one is the
     fallback so an unpriced market never prints another market's street */
  if(addr) addr.textContent = MKT.addr || MARKETS.SG.addr;""")

io.open(F, "w", encoding="utf-8").write(src)
print("UK issuer and address line set")
