import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 121 · UK ON THE SAME LADDER (23 Sep 2026) ═════════════════════════════════
# Alex: "apply it to UK model too". Two points: floor 39 at 5%, opener 43 at
# 10%, one step at the opener, ceiling 52 (about 20% above the opener, as SG and
# AE). The 7.5% rung at 41 goes. rateFor/bandFor already handle a two-point
# market; only the data changes. With this, no market steps three times, and
# the three-band branches in 117/120 become dormant rather than dead.
fix("""  UK: { kg:{ floor:39.00, def:41.00, ceil:46.00, step:0.25, full:43.00 },
        bands:[ { id:1, from:39.00, to:40.99, rate:0.050, label:'BAND 01', range:'39.00–40.99' },
                { id:2, from:41.00, to:42.99, rate:0.075, label:'BAND 02', range:'41.00–42.99' },
                { id:3, from:43.00, to:46.00, rate:0.100, label:'BAND 03', range:'43.00+' } ],""",
    """  UK: { kg:{ floor:39.00, def:43.00, ceil:52.00, step:0.25, full:43.00 },
        /* 121: two points, one step at the opener (see rateFor) */
        bands:[ { id:1, from:39.00, to:42.99, rate:0.050, label:'BAND 01', range:'39.00–42.99' },
                { id:2, from:43.00, to:52.00, rate:0.100, label:'BAND 02', range:'43.00+' } ],""")
fix("        ref:{ kg:41.00, floor:39.00, rate:0.075 }, k:'UK',",
    "        ref:{ kg:43.00, floor:39.00, rate:0.100 }, k:'UK',")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_ladder5 OK")
