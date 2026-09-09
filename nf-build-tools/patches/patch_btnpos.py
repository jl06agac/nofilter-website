import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 1 · the coffee screen's CTA stops aligning to the tile edge ───────────
old = """            var vr=vp.getBoundingClientRect();
            var tileRight=vr.left+startX+tilesW;
            nb.style.marginRight='0px';
            var ar=nb.getBoundingClientRect();
            nb.style.marginRight=Math.max(0,Math.round(ar.right-tileRight))+'px';"""
new = """            var vr=vp.getBoundingClientRect();
            var tileRight=vr.left+startX+tilesW;
            /* 1 Sep — the CTA no longer chases the last tile's right edge.
               Alex: "the buttons should where possible be positioned in same
               place across all quote builder pages." Tile-edge alignment put
               this screen's button 21px left of every other screen's; the
               shared content edge wins. The header copy below keeps its tile
               alignment — it is prose, not a control the hand returns to. */
            nb.style.marginRight='0px';"""
assert src.count(old) == 1, "tile-align anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ── 42 · ONE PLACE FOR THE FORWARD BUTTON, EVERY SCREEN ──────────────────
   Alex: "the buttons should where possible be positioned in same place across
   all quote builder pages." Measured before this block, the forward button's
   box across the four screens: right edge 1357 / 1378 / 1378, top 755 / 773 /
   753. Two causes: the coffee screen's CTA was JS-aligned to its tile edge
   (fixed above), and the bars carry different paddings and heights per screen.
   Rather than reconcile four bars' internals, the button itself is pinned:
   every bar is sticky at the scroller's bottom, so anchoring the button to the
   bar's content-box bottom with ONE padding pair lands it at the same x AND y
   on every screen, whatever else the bar holds. */
#nfConsoleWrap .deck-screen.is-active .deck-actions{
  padding-top:clamp(12px,1.6vh,20px);
  padding-bottom:clamp(14px,2.6vh,30px);
}
#nfConsoleWrap .deck-screen.is-active .deck-actions .deck-next{
  align-self:flex-end;
}
/* the back link rides the same baseline so the pair reads as one bar */
#nfConsoleWrap .deck-screen.is-active .deck-actions .deck-back{
  align-self:flex-end;margin-bottom:16px;
}
/* the last 20px: with the paddings unified, the bars still sat at their
   screens' flow bottoms, and the machines screen ran 828px against its
   neighbours' 808 — the grid's 18px margin-bottom plus rounding, pushing it
   past the shared min-height while the others sat exactly on it. Zeroed here
   (the purchase panel brings its own spacing), which brings all three screens
   to the same height and the three buttons to the same box. */
#nfConsoleWrap #mcards{margin-bottom:0;}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("forward button pinned to one spot")
