import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 117 · THE LADDER RESET (22-23 Sep 2026) ═══════════════════════════════════
# Source of truth: NoFilter/Business-docs/COFFEE-LADDER.md. Two named points per
# market instead of three whole-price bands: a floor at 5% and an opener at 10%,
# the rate RAMPING between them (quarter-point quantised) and flat 10% from the
# opener to the ceiling. SG 46 / 51 / 60, AE 150 / 165 / 200. The opener is the
# quoted price (the slider's default); the floor is a concession.
#
# Why: whole-price bands had cliffs (at 151 and 157 a client paying more left
# NoFilter with less), and a rising percentage inside the ladder gave the forest
# ~51% of every price step, so NoFilter barely improved margin as clients paid
# more. Above the opener the rate is flat, so every extra dirham is 90% ours
# and the NGO figure still climbs; generosity beyond that is the top-up dial.
#
# UK keeps its three stepped bands untouched: a market with more than two bands
# still steps; a market with exactly two ramps. Every reader of BANDS is made
# band-count agnostic, so nothing below assumes BANDS[2] exists.

# ── A · the ladder data ──────────────────────────────────────────────────────
fix("""  SG: { kg:{ floor:45.00, def:48.00, ceil:55.00, step:0.25, full:51.00 },
        bands:[ { id:1, from:45.00, to:47.99, rate:0.050, label:'BAND 01', range:'45.00–47.99' },
                { id:2, from:48.00, to:50.99, rate:0.075, label:'BAND 02', range:'48.00–50.99' },
                { id:3, from:51.00, to:55.00, rate:0.100, label:'BAND 03', range:'51.00+' } ],""",
    """  SG: { kg:{ floor:46.00, def:51.00, ceil:60.00, step:0.25, full:51.00 },
        /* 117: two points, the rate ramps between them (see rateFor) */
        bands:[ { id:1, from:46.00, to:50.99, rate:0.050, label:'BAND 01', range:'46.00–50.99' },
                { id:2, from:51.00, to:60.00, rate:0.100, label:'BAND 02', range:'51.00+' } ],""")
fix("""  AE: { kg:{ floor:145.00, def:155.00, ceil:165.00, step:0.50, full:157.00 },
        bands:[ { id:1, from:145.00, to:150.99, rate:0.050, label:'BAND 01', range:'145.00–150.99' },
                { id:2, from:151.00, to:156.99, rate:0.075, label:'BAND 02', range:'151.00–156.99' },
                { id:3, from:157.00, to:165.00, rate:0.100, label:'BAND 03', range:'157.00+' } ],""",
    """  AE: { kg:{ floor:150.00, def:165.00, ceil:200.00, step:0.50, full:165.00 },
        /* 117: two points, the rate ramps between them (see rateFor) */
        bands:[ { id:1, from:150.00, to:164.99, rate:0.050, label:'BAND 01', range:'150.00–164.99' },
                { id:2, from:165.00, to:200.00, rate:0.100, label:'BAND 02', range:'165.00+' } ],""")

# ── B · the public reference figures (shown before an access code) ───────────
fix("        ref:{ kg:48.00, floor:45.00, rate:0.075 }, k:'SG',",
    "        ref:{ kg:51.00, floor:46.00, rate:0.100 }, k:'SG',")
fix("        ref:{ kg:155.00, floor:145.00, rate:0.075 }, k:'AE',",
    "        ref:{ kg:165.00, floor:150.00, rate:0.100 }, k:'AE',")

# ── C · the rate function: ramp on a two-point market, step on three ─────────
fix("function bandFor(p){ for(var i=0;i<BANDS.length;i++){ if(p <= BANDS[i].to + 1e-9) return BANDS[i]; } return BANDS[2]; }",
    """/* 117: on a two-point market the rate ramps from the floor's rate to the opener's,
   quantised to a quarter of a point, so a client paying more never leaves NoFilter
   with less. Three-band markets (UK) keep stepping. */
function rateFor(p){
  var B=BANDS, lo=B[0], hi=B[B.length-1];
  if(B.length!==2) return bandFor(p).rate;
  if(p>=hi.from) return hi.rate;
  if(p<=lo.from) return lo.rate;
  return Math.round((lo.rate+(hi.rate-lo.rate)*(p-lo.from)/(hi.from-lo.from))*400)/400;
}
function bandFor(p){
  var b=null;
  for(var i=0;i<BANDS.length;i++){ if(p <= BANDS[i].to + 1e-9){ b=BANDS[i]; break; } }
  b = b || BANDS[BANDS.length-1];
  if(BANDS.length!==2) return b;
  var r=rateFor(p); if(r===b.rate) return b;
  var o={}; for(var k in b) o[k]=b[k]; o.rate=r; return o;
}""")

# quarter-point rates print as 6.25 / 7.5 / 10, never rounded to one decimal
fix("window.__nfPct = function(r){ return String(+(r * 100).toFixed(1)); };",
    "window.__nfPct = function(r){ return String(Math.round(r * 400) / 4); };")
fix("  $('#rateVal').textContent = (c.band.rate * 100).toFixed(1);",
    "  $('#rateVal').textContent = window.__nfPct(c.band.rate);")
fix("  $('#contribRate').textContent = (c.band.rate * 100).toFixed(1) + '%';",
    "  $('#contribRate').textContent = window.__nfPct(c.band.rate) + '%';")

# ── D · band marks for the dial: base / mid / full from whatever the market has ─
fix("  window.__nfBandMarks = { base: MKT.bands[0].from, mid: MKT.bands[1].from, full: MKT.bands[2].from };",
    """  (function(){ var b=MKT.bands, L=b[b.length-1];
     window.__nfBandMarks = { base: b[0].from, mid: (b.length>2 ? b[1].from : (b[0].from+L.from)/2), full: L.from }; })();""")

# ── E · band tiles rendered from the array, not three fixed rows ─────────────
fix("""  setT('#bR1', 'Band 01 · ' + BANDS[0].range);
  setT('#bR2', 'Band 02 · ' + BANDS[1].range);
  setT('#bR3', 'Band 03 · ' + BANDS[2].range);""",
    """  (function(){ var host=document.querySelector('.bands'); if(!host) return;
     var ramp = BANDS.length===2, h='';
     for(var i=0;i<BANDS.length;i++){ var b=BANDS[i], last=i===BANDS.length-1;
       var pct = ramp && !last ? window.__nfPct(b.rate)+'% → '+window.__nfPct(BANDS[BANDS.length-1].rate)+'%' : window.__nfPct(b.rate)+'%';
       var sub = last ? 'Full rate' : (ramp ? 'Rises with the price' : (i===0 ? 'Base share' : 'Stepped share'));
       h += '<div class="band" data-band="'+(i+1)+'"><span class="bl2" id="bR'+(i+1)+'">Band 0'+(i+1)+' · '+b.range+'</span><span class="bp">'+pct+'</span><span class="bl2">'+sub+'</span></div>'; }
     host.innerHTML = h; })();""")

# ── F · the step-up ledger: "next band" is whatever follows, not id<3 ─────────
fix("  } else if(c.band.id < 3){\n    var next = BANDS[c.band.id];",
    "  } else if(c.band.id < BANDS.length){\n    var next = BANDS[c.band.id];")

# ── G · the morph dial's encouragement and tier crossing: aim at the opener ───
fix("""              var nextPrice = atMid ? MK.full : MK.mid;      /* pass141: from the market */
              var nextRate  = atMid ? 0.10 : 0.075;""",
    """              /* 117: on a ramp the only named step is the opener; three-band markets keep the mid rung */
              var ramp = (typeof BANDS!=='undefined' && BANDS && BANDS.length===2);
              var nextPrice = (ramp || atMid) ? MK.full : MK.mid;
              var nextRate  = (ramp || atMid) ? 0.10 : 0.075;""")
fix("              var label = atMid ? 'the full 10%' : '7.5%';",
    "              var label = (ramp || atMid) ? 'the full 10%' : '7.5%';")

# ── H · the public "where it goes" card: two-point copy when the market ramps ─
fix("        var B = (M && M.bands) || [{from:45,rate:.05},{from:48,rate:.075},{from:51,rate:.1}];",
    "        var B = (M && M.bands) || [{from:46,rate:.05},{from:51,rate:.1}];")
fix("""          + '<p>At <b>'+cur+' '+Math.round(B[0].from)+'</b> that slice is <b>'+pct(B[0])+'</b>, about <b>'+cup(B[0])+' '+c.word+'</b> a cup. From <b>'+Math.round(B[1].from)+'</b> it steps up to <b>'+pct(B[1])+'</b> (about <b>'+cup(B[1])+' '+c.word+'</b>), and from <b>'+Math.round(B[2].from)+'</b> the full <b>'+pct(B[2])+'</b> (about <b>'+cup(B[2])+' '+c.word+'</b>).</p>'""",
    """          + (B.length===2
              ? '<p>At <b>'+cur+' '+Math.round(B[0].from)+'</b> that slice is <b>'+pct(B[0])+'</b>, about <b>'+cup(B[0])+' '+c.word+'</b> a cup. It rises with every step in price, and from <b>'+Math.round(B[1].from)+'</b> it is the full <b>'+pct(B[1])+'</b> (about <b>'+cup(B[1])+' '+c.word+'</b>), on the whole price, however high you go.</p>'
              : '<p>At <b>'+cur+' '+Math.round(B[0].from)+'</b> that slice is <b>'+pct(B[0])+'</b>, about <b>'+cup(B[0])+' '+c.word+'</b> a cup. From <b>'+Math.round(B[1].from)+'</b> it steps up to <b>'+pct(B[1])+'</b> (about <b>'+cup(B[1])+' '+c.word+'</b>), and from <b>'+Math.round(B[B.length-1].from)+'</b> the full <b>'+pct(B[B.length-1])+'</b> (about <b>'+cup(B[B.length-1])+' '+c.word+'</b>).</p>')""")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_ladder2 OK")
