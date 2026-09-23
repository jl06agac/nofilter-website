import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 119 · TWO POINTS MEANS TWO MARKS (23 Sep 2026) ═══════════════════════════
# 117 kept a 7.5% tick at the midpoint of the ramp as a "waypoint". Alex, on the
# live dial: "why is 7.5% still there". A third mark reads as a third rung, and
# the ladder now has two. On a two-point market the dial shows 5% and full 10%
# only, and the smaller "into 7.5%" celebration never fires; three-band markets
# (UK) keep their mid mark and mid burst. The "where it goes" card also grew
# taller than its 09b copy and, being anchored under the figure and lifted to
# stay inside the frame, rose into the headline and covered "/ cup". Copy cut
# back to the old length.

# A · publish the shape alongside the marks
fix("""     window.__nfBandMarks = { base: b[0].from, mid: (b.length>2 ? b[1].from : (b[0].from+L.from)/2), full: L.from }; })();""",
    """     window.__nfBandMarks = { base: b[0].from, mid: (b.length>2 ? b[1].from : (b[0].from+L.from)/2), full: L.from, two: b.length===2 }; })();""")

# B · the dial: no mid tick on a two-point market
fix("""        if(mk2){ mk2.style.left=mMid+'px'; mkl2.style.left=mMid+'px';
                 mk2.style.opacity=1; mkl2.style.opacity=1; }""",
    """        if(mk2){ mk2.style.left=mMid+'px'; mkl2.style.left=mMid+'px';
                 var showMid = !(BM.two);
                 mk2.style.opacity=showMid?1:0; mkl2.style.opacity=showMid?1:0; }""")

# C · the morph: no mid tier on a two-point market (no "into 7.5%" burst or class)
fix("          var atMid  = d.price>=MK.mid && d.price<MK.full;",
    "          var atMid  = !MK.two && d.price>=MK.mid && d.price<MK.full;")

# D · the card copy, back to the 09b length
fix("""              ? '<p>At <b>'+cur+' '+Math.round(B[0].from)+'</b> that slice is <b>'+pct(B[0])+'</b>, about <b>'+cup(B[0])+' '+c.word+'</b> a cup. It rises with every step in price, and from <b>'+Math.round(B[1].from)+'</b> it is the full <b>'+pct(B[1])+'</b> (about <b>'+cup(B[1])+' '+c.word+'</b>), on the whole price, however high you go.</p>'""",
    """              ? '<p>At <b>'+cur+' '+Math.round(B[0].from)+'</b> that slice is <b>'+pct(B[0])+'</b>, about <b>'+cup(B[0])+' '+c.word+'</b> a cup, rising with the price to the full <b>'+pct(B[1])+'</b> from <b>'+Math.round(B[1].from)+'</b> (about <b>'+cup(B[1])+' '+c.word+'</b>), however high you go.</p>'""")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_ladder3 OK")
