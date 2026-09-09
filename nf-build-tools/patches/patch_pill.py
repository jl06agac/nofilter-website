import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

old = """#nfConsoleWrap .q-eq-card.is-buy .q-eq-lengths{display:none;}"""
new = """/* ── 1 Sep · THE ROW KEEPS ITS HEIGHT WHEN THE CHOICE GOES ────────────────
   Alex: "me clicking purchase/rental should not move the pill up even by a
   fraction. right now there's a miniscule jump."

   Measured: 5.17px, and every pixel of it came from this line. .q-eq-terms is
   a centred flex row whose height is set by its TALLEST child, and the two
   children are not the same height — .q-eq-modes is 28.5px (11px text, 5px
   padding) while .q-eq-lengths is 33.5px (13px text, 6px padding, a 1.5px
   border). display:none took the taller one out of layout entirely, the row
   collapsed to the shorter one, and everything below it — the price pill, the
   figure inside it — rose by the difference.

   visibility:hidden instead. The element still occupies its box, so the row is
   the same height in both modes and the figure does not move at all; it is not
   painted, not clickable, and not in the accessibility tree or the tab order,
   so nothing about "the choice does not exist on a purchase" changes for
   anyone. Height is reserved BY THE ELEMENT THAT DEFINES IT rather than by a
   min-height I would have to keep in sync with the button's font size — this
   file's own font-stress test at 1.3x letter-spacing is exactly the thing that
   breaks a hard-coded number. */
#nfConsoleWrap .q-eq-card.is-buy .q-eq-lengths{visibility:hidden;pointer-events:none;}"""

assert src.count(old) == 1, "anchor not unique (%d)" % src.count(old)
io.open(F, "w", encoding="utf-8").write(src.replace(old, new))
print("term-row height stabilised")
