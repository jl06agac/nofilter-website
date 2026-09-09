import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 116 · ONE HARDCODED FALLBACK RESTATED THE SG BAND POINTS (7 Sep) ═════════
# Found by build-ship's own check after the ladder was lifted (114): the page
# still carried "45 / 48 / 51" — the SG floor and both band thresholds — as the
# fallback for window.__nfBandMarks in the quote-review cell. applyMarket()
# always publishes __nfBandMarks before that code can run, so the fallback was
# dead; but a dead literal is still a published number. It now derives from
# whatever MKT carries (the seeded public figures before a code, the real ladder
# after), so it states nothing on its own.
fix("          var MK = window.__nfBandMarks || { base:45, mid:48, full:51 };",
    "          var MK = window.__nfBandMarks || (function(){ var k=(typeof MKT!=='undefined'&&MKT&&MKT.kg)||{}; return { base:k.floor||0, mid:k.def||0, full:k.full||0 }; })();")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_bandmarks OK")
