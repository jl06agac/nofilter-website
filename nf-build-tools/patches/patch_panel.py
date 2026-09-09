import io, sys
F = sys.argv[1]

CSS = r'''
/* ── 24 · THE OPEN "WHAT YOU GET" PANEL GETS AN EDGE ──────────────────────
   Alex, 1 Sep: "can we have a black px outline around the collapsible box or a
   bit more shadow, i still feel it merges a bit too much into background" —
   then, when the first set of renders treated the whole card and showed the
   panel shut: "i'm only asking for treatment to the what you get collapsible
   panel". Correct on both counts. Option D from _test-panel-edge.html.

   WHAT WAS WRONG, measured rather than felt:
     page ground   #F6F2E9
     panel         #E9E1D2   contrast vs page 1.16:1
     panel border  none
     panel shadow  0 18px 34px -20px rgba(26,24,21,.5)
   That shadow is 18px DOWN with -20px spread, so effectively all of it lands
   under the bottom edge. The left and right edges carried nothing at all — the
   panel was defined on one side out of three, and 1.16 is not an edge.

   THE border:0 WAS MY OWN DELIBERATE CHOICE and the note above still says why:
   "no border of its own because it is not a separate surface any more". That
   is true while the panel is SHUT and flush inside the card. Open, it hangs
   145px past the card's bottom edge, absolutely positioned over whatever is
   below it — at which point it IS a separate surface and has to look like one.
   The reasoning was sound and the state it was reasoning about was the wrong
   one.

   NOT THE BLACK OUTLINE ASKED FOR, and he chose this after seeing that option
   rendered beside the others. Full ink is 15.86:1 against a card whose
   heaviest existing element is 1.16 — it does not strengthen the panel so much
   as become the loudest thing on the screen, and four of them turn a row of
   products into a grid of boxes.

   So: a 20% line to CONTAIN and a wrapping shadow to SEPARATE, neither heavy
   on its own. Three shadow layers instead of one, because the tight ambient
   pair is what finally reaches the sides. And no top border, plus the same
   side lines carried on the header band, so the header and the panel read as
   ONE object rather than a lid with a box under it.

   Distinguished by luminance, not hue — it works identically for this reader. */
#nfConsoleWrap .q-eq-incl.is-open .q-eq-panel{
  border:1px solid rgba(26,24,21,.20);
  border-top:0;                       /* joins the header rather than boxing under it */
  box-shadow:0 1px 3px rgba(26,24,21,.11),
             0 5px 12px -4px rgba(26,24,21,.15),
             0 18px 34px -18px rgba(26,24,21,.40);
}
/* the header band carries the panel's side lines while open, so the two are one
   continuous object. Inset rather than a real border: a border would change the
   band's box and shift the row by a pixel on every open. */
#nfConsoleWrap .q-eq-incl.is-open .q-eq-disc{
  box-shadow:inset 1px 0 0 rgba(26,24,21,.20), inset -1px 0 0 rgba(26,24,21,.20);
}
'''

src = io.open(F, encoding="utf-8").read()
assert "── 24 · THE OPEN" not in src, "already patched"
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("panel edge (option D) inserted before line", end + 1)
