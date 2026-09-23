import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 120 · ONE STEP AT THE OPENER (23 Sep 2026) ════════════════════════════════
# 117 ramped the rate between the two points. Alex: "ramping up the price
# basically translated into no extra margin for me." Inside a ramp NoFilter kept
# 6 of every 15 dirhams a client added. Now, on a two-point market, any price
# from the floor up is for sale: 5% below the opener, 10% at the opener and
# above. Between floor and opener every dirham is 95% NoFilter's; above the
# opener, 90%. The step at the opener is the device: "165 is where the forest
# gets the full 10%". Alex chose it knowing a client at 164.50 leaves 156.28
# and at 165 leaves 148.50. UK (three bands) is untouched.

# A · the rate: a step at the opener, no ramp
fix("""function rateFor(p){
  var B=BANDS, lo=B[0], hi=B[B.length-1];
  if(B.length!==2) return bandFor(p).rate;
  if(p>=hi.from) return hi.rate;
  if(p<=lo.from) return lo.rate;
  return Math.round((lo.rate+(hi.rate-lo.rate)*(p-lo.from)/(hi.from-lo.from))*400)/400;
}""",
"""function rateFor(p){
  var B=BANDS, lo=B[0], hi=B[B.length-1];
  if(B.length!==2) return bandFor(p).rate;
  return p>=hi.from-1e-9 ? hi.rate : lo.rate;
}""")

# B · the quote reset carried a stale SG literal (48) whatever the market; it resets to the market's opener
fix("  Q.price = 48.00; slider.value = '48';",
    "  Q.price = MKT.kg.def; slider.value = String(MKT.kg.def);   /* 120: was a stale 48 */")

# C · the card copy: two prices
fix("""              ? '<p>At <b>'+cur+' '+Math.round(B[0].from)+'</b> that slice is <b>'+pct(B[0])+'</b>, about <b>'+cup(B[0])+' '+c.word+'</b> a cup, rising with the price to the full <b>'+pct(B[1])+'</b> from <b>'+Math.round(B[1].from)+'</b> (about <b>'+cup(B[1])+' '+c.word+'</b>), however high you go.</p>'""",
    """              ? '<p>At <b>'+cur+' '+Math.round(B[0].from)+'</b> that slice is <b>'+pct(B[0])+'</b>, about <b>'+cup(B[0])+' '+c.word+'</b> a cup. From <b>'+Math.round(B[1].from)+'</b> it is the full <b>'+pct(B[1])+'</b> (about <b>'+cup(B[1])+' '+c.word+'</b>), on the whole price, however high you go.</p>'""")

# D · the (hidden) band tiles say what the market does
fix("""       var pct = ramp && !last ? window.__nfPct(b.rate)+'% → '+window.__nfPct(BANDS[BANDS.length-1].rate)+'%' : window.__nfPct(b.rate)+'%';
       var sub = last ? 'Full rate' : (ramp ? 'Rises with the price' : (i===0 ? 'Base share' : 'Stepped share'));""",
    """       var pct = window.__nfPct(b.rate)+'%';
       var sub = last ? 'Full rate' : (ramp ? 'Below the opener' : (i===0 ? 'Base share' : 'Stepped share'));""")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_ladder4 OK")
