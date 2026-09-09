import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 57 · THE SG RETAIL KILO IS 80.00, NOT 72.00 ───────────────────────────
# Alex: "our version is showing 72$ per kg, the website's is 80, website's is
# correct." Checked before changing it: bag1kg has read 72.00 in every master on
# disk (PRE-DENSITY, PRE-DOSSIER, today's), so the master has been stale rather
# than drifting — the live site carries the newer figure.
#
# ONLY the SG kilo moves. bag250 (24.00) and the AED pair (77.50 / 232.50) are
# left exactly as they are, because he stated one number and the others are not
# derivable from it: 250g is not a third of a kilo by policy (24.00 against a
# 72.00 kilo is already a small-size premium), and the AED figures follow an FX
# and rounding rule I would be guessing at. They are flagged back to him rather
# than invented.
#
# The 10% contribution figures follow automatically — the shop card, the cart
# and the fork panel all take 10% of the bag price — so RAISED becomes SGD 8.00
# on the kilo without being restated anywhere.
old = "        bag250:24.00, bag1kg:72.00,"
new = "        bag250:24.00, bag1kg:80.00,   /* 1 Sep — was 72.00; the live site's figure, confirmed by Alex. See block 57. */"
assert src.count(old) == 1, "bag price anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# the comment that derives the fork panel's figure now states the arithmetic it
# actually performs
old = """                 MARKETS.SG.bag1kg = 72.00. Retail bags carry a flat 10% — no
                 band, no choice — so 72.00 x 10% = SGD 7.20, which is also the
                 figure the shop route and the cart already use."""
new = """                 MARKETS.SG.bag1kg, which is 80.00 as of 1 Sep (it read 72.00
                 when this note was written). Retail bags carry a flat 10% — no
                 band, no choice — so the panel shows 10% of the bag price, the
                 same figure the shop route and the cart already use."""
assert src.count(old) == 1, "fork note anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# the static fallback in the markup, so a JS-less render is not stale either
old = """            <div class="v"><span id="fork1kgGive">SGD 7.20</span><span class="ind">flat 10% on retail</span></div>"""
new = """            <div class="v"><span id="fork1kgGive">SGD 8.00</span><span class="ind">flat 10% on retail</span></div>"""
assert src.count(old) == 1, "fork value anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── and the colophon drops its last sentence ──────────────────────────────
# Alex: "remove - Site design, copy, photography and code are ours."
old = """    <p class="foot-copy">&copy; 2026 NoFilter Pte. Ltd. &amp; NoFilter LLC. All rights reserved.
       Site design, copy, photography and code are ours.</p>"""
new = """    <p class="foot-copy">&copy; 2026 NoFilter Pte. Ltd. &amp; NoFilter LLC. All rights reserved.</p>"""
assert src.count(old) == 1, "colophon anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("SG retail kilo 72 -> 80; colophon trimmed")
