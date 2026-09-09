import io, re, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 98 · PARTNERS: PRCF IS PRCF INDONESIA, GJI JOINS THE ROLL-CALL ═════════
# Alex, 3 Sep: "all mentions of PRCF need to be updated to PRCF Indonesia";
# "add GJI as a NGO partner that's mentioned" — not tied to an origin, and
# the initials only (his answers to the two questions). GJI therefore joins
# the places that list every partner (the home Partners readout, the quote
# sheet's footer) and not any origin's record; the logo marquee stays as it
# is until there is a mark to mount.
# PRCF → PRCF Indonesia everywhere the name is set in text, by word boundary,
# leaving alone the two that already say it (the marquee alts), the link
# (prcfoundation.org) and the file (ngo-prcf.png), which are lower-case.
n_before = len(re.findall(r"\bPRCF\b(?! Indonesia)", src))
src = re.sub(r"\bPRCF\b(?! Indonesia)", "PRCF Indonesia", src)
assert n_before == 17, "expected 17 bare PRCF mentions, found %d" % n_before
assert not re.search(r"\bPRCF\b(?! Indonesia)", src)

fix("""<div class="ro"><div class="k">Partners</div><div class="v">PRCF Indonesia · SRI · OIC · FFI</div></div>""",
    """<div class="ro"><div class="k">Partners</div><div class="v">PRCF Indonesia · SRI · OIC · FFI · GJI</div></div>""")
fix("""  h += '<div class="rfoot">Partner NGOs: PRCF Indonesia · SRI · OIC<br>Fauna &amp; Flora Myanmar · ACCA<br>' +""",
    """  h += '<div class="rfoot">Partner NGOs: PRCF Indonesia · SRI · OIC · GJI<br>Fauna &amp; Flora Myanmar · ACCA<br>' +""")

# ── 98b withdrawn, 3 Sep: the HD switch for the canopy plate is out. Alex: "put
#    my video back... your video implementation also seems to have slowed down my
#    intro page." The plate is keeps-standing-lite.mp4 under hero-poster.jpg, as it
#    was before 3 Sep. (The wide-screen file switch in wet() is not here either —
#    nothing else used it.)

io.open(F, "w", encoding="utf-8").write(src)
print("PRCF Indonesia, GJI")
