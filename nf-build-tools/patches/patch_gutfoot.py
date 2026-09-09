import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 81 · A GUTTER CARD NEVER RUNS PAST THE FRAME'S FOOT ═══════════════════
# Alex, 2 Sep (UK, 3A): "where it goes gutter clashing with button below".
# Block 76 removed the clamp at his request ("render full size without the
# scroll") and only RECORDED the overrun in dataset.over. The UK copy is
# longer than SG's ("pence" where SG has "¢"), so on his window the right
# card ran ~110px below the frame and sat on the Your quote button.
# Full size stays. What changes is where the card hangs: if it would pass the
# frame's foot it rises until its bottom sits 24px inside the frame — never
# above 24px below the frame's top. Each card decides for itself, so a short
# left card stays on the figure's anchor while a long right card rises.
def fix(old, new):
    global src
    n = src.count(old)
    assert n == 1, "anchor count %d for %r" % (n, old[:60])
    src = src.replace(old, new)

# price + top-up gutters (two identical blocks — patched by unique context)
old = """          gl.dataset.over=Math.max(0,Math.round(anchorTop+gl.offsetHeight-(sr.bottom-24)));
          gr.dataset.over=Math.max(0,Math.round(anchorTop+gr.offsetHeight-(sr.bottom-24))); })();   /* block 76 */
        gl.style.top=anchorTop+'px';
        gr.style.top=anchorTop+'px';
        return true;"""
new = """          gl.dataset.over=Math.max(0,Math.round(anchorTop+gl.offsetHeight-(sr.bottom-24)));
          gr.dataset.over=Math.max(0,Math.round(anchorTop+gr.offsetHeight-(sr.bottom-24)));
          /* block 81 — a card that would pass the foot rises to sit inside it */
          gl.__top=Math.max(sr.top+24, Math.min(anchorTop, sr.bottom-24-gl.offsetHeight));
          gr.__top=Math.max(sr.top+24, Math.min(anchorTop, sr.bottom-24-gr.offsetHeight)); })();   /* block 76 */
        gl.style.top=(gl.__top!=null?gl.__top:anchorTop)+'px';
        gr.style.top=(gr.__top!=null?gr.__top:anchorTop)+'px';
        return true;"""
assert src.count(old) == 2, "gutter top anchor count %d" % src.count(old)
src = src.replace(old, new)

# year gutters
fix("""            yl.dataset.over=Math.max(0,Math.round(t+yl.offsetHeight-(sr.bottom-24)));
            yr.dataset.over=Math.max(0,Math.round(t+yr.offsetHeight-(sr.bottom-24))); })();   /* block 76 */
          yl.style.top=t+'px'; yr.style.top=t+'px';""",
    """            yl.dataset.over=Math.max(0,Math.round(t+yl.offsetHeight-(sr.bottom-24)));
            yr.dataset.over=Math.max(0,Math.round(t+yr.offsetHeight-(sr.bottom-24)));
            /* block 81 — same rise as the price and top-up cards */
            yl.__top=Math.max(sr.top+24, Math.min(t, sr.bottom-24-yl.offsetHeight));
            yr.__top=Math.max(sr.top+24, Math.min(t, sr.bottom-24-yr.offsetHeight)); })();   /* block 76 */
          yl.style.top=(yl.__top!=null?yl.__top:t)+'px'; yr.style.top=(yr.__top!=null?yr.__top:t)+'px';""")

io.open(F, "w", encoding="utf-8").write(src)
print("gutters stay inside the frame")
