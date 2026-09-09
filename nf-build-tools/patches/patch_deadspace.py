import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ── 45 · THE 181px OF NOTHING UNDER THE OPEN PANEL ───────────────────────
   Alex, with the panel open at 1512x1250: "does the padding at the bottom look
   like a page that does not scroll up and down."

   No, and this is the measurement I should have taken a round ago. Walking the
   active screen's children with the panel open:

     .q-step-head      ot 59    h 60
     .panel            ot 129   h 1478
       #mcards         ot 149   h 566     (the grid, still in flow — correct,
                                           the tiles are meant to stay)
       #nfBuyDoss      ot 749   h 818     margin-bottom 40
     .deck-actions     ot 1607  h 141     visibility:hidden
     ───────────────────────────────────
     screen offsetHeight 1721, deck overflow 507

   The panel's ink ends at 1567. Everything after it is invisible: 40px of the
   panel's own bottom margin, then 141px of forward bar that is HIDDEN but
   still holding its space. visibility:hidden keeps the box. So the last 181px
   of the scroll range is a scroll into blank paper — which is exactly the
   padding he is pointing at, and exactly the "force scroll down" that survived
   locking the document.

   The bar was hidden (block 28) because while the panel is open the only
   sensible action is to close it. If it takes no part in the view it should
   take no part in the layout either; display:none finishes the job the
   visibility:hidden started. This does not touch the layout-stability rule —
   that governs the panel's OWN controls, which must never move the panel. This
   is the panel opening, which is a state change the reader asked for.

   The 40 comes down to a deliberate 24: enough that the panel's bottom edge is
   not flush against the window at the end of the scroll, small enough that it
   reads as a margin rather than somewhere to go. What remains scrollable above
   the panel is the machine grid, which is meant to still be there. */
#nfConsoleWrap .deck-screen.is-active:has(#nfBuyDoss.is-open) .deck-actions{
  display:none;
}
#nfConsoleWrap #nfBuyDoss.is-open{margin-bottom:24px;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

# ── and the fill pass re-runs when the panel finishes opening or closing ──
# The screen loses 181px the instant the bar leaves layout, and gains it back
# on close. fill() is armed on class changes, which covers .is-open — but the
# panel's max-height transition means the screen keeps growing for another
# .55s after that class lands, so the size it measures mid-flight is wrong.
# One more pass when the transition ends.
old = """      addEventListener('resize', fill);
      window.__nfDeckFill = fill;"""
new = """      addEventListener('resize', fill);
      window.__nfDeckFill = fill;
      /* the panel grows for .55s after .is-open lands, so the class-change pass
         measures a screen that is still moving. Settle it at the end. */
      addEventListener('transitionend', function(e){
        if(e.target && e.target.id === 'nfBuyDoss' && e.propertyName === 'max-height'){
          requestAnimationFrame(fill);
        }
      }, true);"""
assert src.count(old) == 1, "fill anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("dead space under the open panel removed")
