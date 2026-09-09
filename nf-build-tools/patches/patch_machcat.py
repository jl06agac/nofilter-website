import io, sys, re
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 117 · THE MACHINE CATALOGUE STOPS RESTATING THE SG RATE CARD (7 Sep) ═════
# MACHINES[] carried r24 / r36 / buy / price for every CaféMatic — SG's figures,
# a second copy of MARKETS.SG.mach that applyMarket() overwrote on every run.
# With the ladder lifted out of the page (114) this copy was the last place the
# machine prices were published. The catalogue keeps identity only (name, who
# it is for, specs, image); the rates are written in by applyMarket() from
# MKT.mach, which is empty until a valid code brings the ladder — so the copy
# guards, and prints 0 rather than throwing, on the seeded market. The machine
# grid and table that print m.price live inside the gated console, so nothing
# public changes.
for k, line in [("cm2", "    r24:380, r36:315, buy:3600,  price:315,   /* price = the 'From' figure = the 36-mo rate */\n"),
                ("cm5", "    r24:545, r36:425, buy:6500,  price:425,\n"),
                ("cm6", "    r24:565, r36:440, buy:8000,  price:440,\n"),
                ("cm8", "    r24:660, r36:500, buy:10500, price:500,\n")]:
    fix(line, "    r24:0, r36:0, buy:0, price:0,   /* 117: written by applyMarket() from MKT.mach */\n")

fix("""  MACHINES.forEach(function(m){
    var r = MKT.mach[m.k];
    m.r24 = r.r24; m.r36 = r.r36; m.buy = r.buy; m.price = r.r36;""",
"""  MACHINES.forEach(function(m){
    /* 117: MKT.mach is {} until the ladder arrives with a valid code */
    var r = (MKT.mach && MKT.mach[m.k]) || { r24:0, r36:0, buy:0 };
    m.r24 = r.r24; m.r36 = r.r36; m.buy = r.buy; m.price = r.r36;""")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_machcat OK")
