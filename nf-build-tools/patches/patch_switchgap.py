import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ── 52 · THE EXTRAS COPY STOPS SHORT OF THE TOGGLE ───────────────────────
   Alex, twice: "i dont think 'conservation data' 'with your logo' should be
   almost touching the dials."

   He was being generous — measured, they are not almost touching, they are
   underneath. Range-measuring the ink of the first line against the switch box
   on the three tiles at 1059 wide:

     Countertop Milk Fridge   ink ends 656 · switch starts 651  →  -5px
     Co-Branded Wrap          ink ends 931 · switch starts 938  →  +7px
     Live Impact Screen       ink ends 661 · switch starts 651  →  -10px

   Negative is overlap. The cause is that .txt and .nfbd-sw are flex siblings,
   but .txt measures out to the SAME right edge as the switch (437→687 against
   the switch's 651→687) rather than stopping short of it — so its text is free
   to run the full width and the switch is simply drawn on top of the last
   40-odd pixels. The 16px I put on .d in block 41 was measured against the
   text column's edge, which is the wrong edge: it buys nothing, because the
   column itself already extends under the control.

   So the reserve goes where it cannot be argued with — on the text runs
   themselves, sized from the switch (36px) plus a 12px channel. Both the title
   and the description carry it, so a longer product name can no more tuck
   under the toggle than the description can. */
#nfConsoleWrap .nfbd-ex .t,
#nfConsoleWrap .nfbd-ex .d{padding-right:48px;}
/* the price sits below the rule, clear of the switch entirely, and needs the
   full width for its right-aligned figure */
#nfConsoleWrap .nfbd-ex .xp{padding-right:0;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("extras copy cleared of the toggle")
