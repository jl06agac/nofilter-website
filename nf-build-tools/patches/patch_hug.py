import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ── 66 · THE CARDS HUG THEIR CONTENT ─────────────────────────────────────
   Moving the impact panel to column two closed the void in the middle and
   opened one on the left: the manifest is align-items:stretch, so column one
   was still being pulled to the height of its taller neighbour and ended in
   ~140px of empty black under "Final billed rate per kilo". The void was
   relocated, not removed.

   The stretch was there to make three columns read as one band. They still do —
   they share a top edge, a border and a ground — and a card that stops where its
   content stops is the more honest object anyway: an empty quarter of a panel
   reads as something missing rather than as something finished.

   Column three keeps its full-height span: it is the tallest by nature and is
   the thing the other two are measured against. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest{align-items:start;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest .stl-col:nth-of-type(3){
  align-self:stretch;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("cards hug their content")
