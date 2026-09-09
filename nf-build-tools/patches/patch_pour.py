import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 99 · THE QUOTE PLATE'S POUR, RESHOT ════════════════════════════════════
# Alex, 3 Sep: the old plate clip was "slow to load and also very zoomed in"
# — a portrait phone shot, so every landscape cut of it was a slice. He found
# a landscape 4K clip (Pexels 6204972: a rosetta poured into a yellow cup).
# quote-pour-2-lite.mp4 is seconds 6–16.5 of it, the rosetta forming, cropped
# right-of-centre to 4:3 so the cup stays whole with the jug still in frame,
# 1200×900 (2× the 595px plate), 24fps, 1.1 Mbps, 1.39 MB, with the last
# half-second dissolved into the first so the loop has no jump cut.
# quote-pour-2.jpg (40 KB) is the finished-art frame, the poster. The old
# files stay on the CDN untouched. The settle's footage layer (step 4 of the
# quote console) used the same clip and moves with it.
fix("""                   data-poster="../../_CDN-UPLOAD-SAFE/quote-pour.jpg"
                   aria-label="Milk poured into latte art at a NoFilter counter"
                   onerror="this.closest('.qplate').remove();"><source
                   data-src="../../_CDN-UPLOAD-SAFE/quote-pour-lite.mp4" type="video/mp4"></video>""",
    """                   data-poster="../../_CDN-UPLOAD-SAFE/quote-pour-2.jpg"
                   aria-label="Milk poured into latte art at a NoFilter counter"
                   onerror="this.closest('.qplate').remove();"><source
                   data-src="../../_CDN-UPLOAD-SAFE/quote-pour-2-lite.mp4" type="video/mp4"></video>""")
fix("""  var STL_VIDEO_SRC = '../../_CDN-UPLOAD-SAFE/quote-pour-lite.mp4';""",
    """  var STL_VIDEO_SRC = '../../_CDN-UPLOAD-SAFE/quote-pour-2-lite.mp4';   /* block 99 */""")
assert "quote-pour-lite.mp4" not in src and "quote-pour.jpg" not in src

io.open(F, "w", encoding="utf-8").write(src)
print("the quote plate pours the new clip")
