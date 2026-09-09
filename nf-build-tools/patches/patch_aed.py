import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 76 · THE WIZARD SPEAKS THE MARKET'S CENTS ═════════════════════════════
# Alex: "mechanism is broken here for AED sums, it still shows cents, it
# should reflect aed choices."
#
# What the AED screen showed: 20.9¢ BUILT IN + 0.0¢ YOUR TOP-UP = 20.9¢/cup,
# and "Past the 12¢ stretch — thank you ✦" before the reader had touched
# anything. Every one of those is an SGD assumption that survived the market
# switch:
#   · the unit. AED 155/kg at 7.5% over 55.56 cups is 20.9 — but 20.9 FILS,
#     not cents. The glyph was a literal ¢ in fourteen places.
#   · the tiers. 10¢ "all to the NGO" and the 12¢ stretch are SGD numbers: the
#     full 10% band tops out at 9.9¢ on a 55 kilo. On a 165 kilo the same band
#     is 29.7 fils, so an AED reader started the top-up screen already "past
#     the stretch".
#   · the top-up ceiling. #topUp's max is 7.5, written in the markup, read once
#     at init, and never re-read on a market change.
#   · the dial's own labels. __nfSyncMorph writes "AED 145" straight onto the
#     end label and the track does not re-render on a market change, so the
#     top-up screen showed a price endpoint under a pin that means "your price".
#
# One table per market now carries the cup-level numbers, derived the same way
# the rest of the AE card is: scaled by the ceiling ratio 165/55 = 3.0, so the
# tiers sit at the same point of the band on both cards. Flagged for Alex: the
# AED tier and ceiling figures are DERIVED, not agreed.

# ── 1 · the per-market cup table ──────────────────────────────────────────
old = """        kg:{ floor:45.00, def:48.00, ceil:55.00, step:0.25, full:51.00 },"""
new = """        kg:{ floor:45.00, def:48.00, ceil:55.00, step:0.25, full:51.00 },
        /* block 76 — the cup-level numbers, per market. sym is what follows a
           per-cup figure; topMax/topStep drive the top-up dial; ten/stretch
           are the two milestones the wizard celebrates. */
        cup:{ sym:'\\u00a2', word:'cents', topMax:7.5, topStep:0.1, ten:10, stretch:12 },"""
assert src.count(old) == 1, "SG kg anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """        kg:{ floor:145.00, def:155.00, ceil:165.00, step:0.50, full:157.00 },"""
new = """        kg:{ floor:145.00, def:155.00, ceil:165.00, step:0.50, full:157.00 },
        /* block 76 — DERIVED, not agreed: SG's cup figures × 3.0, the ratio of
           the two ceilings (165/55), so each milestone sits at the same point
           of the band it sits at in SGD. The unit is the fil. */
        cup:{ sym:' fils', word:'fils', topMax:22.5, topStep:0.5, ten:30, stretch:36 },"""
assert src.count(old) == 1, "AE kg anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 2 · one accessor, and the market switch pushes the numbers down ───────
# CAUGHT IN TEST: the runtime is one strict-mode IIFE, MKT is closure-local,
# and recalc() runs during initialisation — before execution reaches an
# assignment placed beside applyMarket. So the accessor is a hoisted function
# declaration at the top of the IIFE (callable from the first line), and the
# three quote-page call sites inside the IIFE use it by name; the wizard,
# which is a later script block, reads it off window.
old = """(function(){
'use strict';
/* ══════════════════════════════════════════════════════════════════════════
   NOFILTER · OPTION C — INSTRUMENT · runtime"""
new = """(function(){
'use strict';
/* block 76 — the market's cup table, with SG's numbers as the fallback so a
   market without one behaves exactly as everything did before this block.
   A function declaration, so it is hoisted above the first recalc(). */
function __nfCupTable(){
  return (typeof MKT !== 'undefined' && MKT && MKT.cup) || { sym:'\\u00a2', word:'cents', topMax:7.5, topStep:0.1, ten:10, stretch:12 };
}
window.__nfCup = __nfCupTable;
/* ══════════════════════════════════════════════════════════════════════════
   NOFILTER · OPTION C — INSTRUMENT · runtime"""
assert src.count(old) == 1, "IIFE head anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """function applyMarket(k){
  var sel = MARKETS[k] ? k : 'SG';
  MKTK = sel;
  MKT  = MARKETS[MARKETS[sel].use || sel];   /* UK borrows SG's numbers */
"""
new = """function applyMarket(k){
  var sel = MARKETS[k] ? k : 'SG';
  MKTK = sel;
  MKT  = MARKETS[MARKETS[sel].use || sel];   /* UK borrows SG's numbers */
  /* block 76 — the top-up dial takes the market's ceiling and step; its value
     is clamped by the browser when max drops, so an SG top-up carried into
     AED cannot exceed the AED range */
  (function(){ var t = document.getElementById('topUp'); if(!t) return;
    var c = __nfCupTable(); t.max = c.topMax; t.step = c.topStep;
    var u = document.querySelector('#morphFigure .mu-imp'); if(u) u.textContent = c.sym; })();
"""
assert src.count(old) == 1, "applyMarket anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 3 · the dial re-renders after a market switch ─────────────────────────
old = """    if('ResizeObserver' in window) new ResizeObserver(render).observe(wrap);
    window.addEventListener('resize',render);
    render();"""
new = """    if('ResizeObserver' in window) new ResizeObserver(render).observe(wrap);
    window.addEventListener('resize',render);
    window.__nfUniRender = render;   /* block 76 — the market switch calls this */
    render();"""
assert src.count(old) == 1, "render expose anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """  window.__nfMorphSync = true;
  try { w.dispatchEvent(new Event('input', {bubbles:true})); }
  finally { window.__nfMorphSync = false; }"""
new = """  window.__nfMorphSync = true;
  try { w.dispatchEvent(new Event('input', {bubbles:true})); }
  finally { window.__nfMorphSync = false; }
  /* block 76 — the unified track listens to phase flips and its own drags,
     not to this event, so the labels written above stood until the next
     phase change: "AED 145" under a pin that means "your price". */
  if(window.__nfUniRender) window.__nfUniRender();"""
assert src.count(old) == 1, "sync dispatch anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 4 · the track re-reads the top-up range each frame, like the price ────
old = """      PMIN=+pS.min; PMAX=+pS.max; PSTEP=+pS.step||PSTEP;"""
new = """      PMIN=+pS.min; PMAX=+pS.max; PSTEP=+pS.step||PSTEP;
      TMAX=+tS.max||TMAX; TSTEP=+tS.step||TSTEP;   /* block 76 — same reason, for the top-up */"""
assert src.count(old) == 1, "PMIN reread anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """        labR.style.left=w+'px'; labR.textContent='+'+TMAX+'\\u00a2 / cup';"""
new = """        labR.style.left=w+'px'; labR.textContent='+'+TMAX+window.__nfCup().sym+' / cup';"""
assert src.count(old) == 1, "labR anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 5 · the milestones come from the market ───────────────────────────────
old = """      var shown = Math.round(d.combined*10)/10;
      var tier = shown>=12 ? 2 : (shown>=10 ? 1 : 0);"""
new = """      var shown = Math.round(d.combined*10)/10;
      var __c = window.__nfCup();   /* block 76 — 10/12 were SGD's numbers */
      var tier = shown>=__c.stretch ? 2 : (shown>=__c.ten ? 1 : 0);"""
assert src.count(old) == 1, "tier anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """        else if(tier>=2)  chip.textContent = 'Past the 12¢ stretch — thank you ✦';
        else if(tier===1) chip.textContent = '10¢ a cup, all to the NGO ✓';"""
new = """        else if(tier>=2)  chip.textContent = 'Past the ' + __c.stretch + __c.sym + ' stretch — thank you ✦';
        else if(tier===1) chip.textContent = __c.ten + __c.sym + ' a cup, all to the NGO ✓';"""
assert src.count(old) == 1, "tier chip anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 6 · every per-cup figure takes the market's unit ──────────────────────
reps = [
 ("""              + '\\u00a2 a cup \\u00b7 your top-up adds +' + (window.__nfCur || 'SGD') + ' '""",
  """              + window.__nfCup().sym + ' a cup \\u00b7 your top-up adds +' + (window.__nfCur || 'SGD') + ' '"""),
 ("""      if($('mTopupEcho')) $('mTopupEcho').textContent = d.topUp>0 ? (' · +'+d.topUp.toFixed(1)+'¢ per cup') : '';""",
  """      if($('mTopupEcho')) $('mTopupEcho').textContent = d.topUp>0 ? (' · +'+d.topUp.toFixed(1)+window.__nfCup().sym+' per cup') : '';"""),
 ("""        figUnit.textContent='¢'; figPer.style.display=''; figPer.textContent='/cup';""",
  """        figUnit.textContent=window.__nfCup().sym; figPer.style.display=''; figPer.textContent='/cup';"""),
 ("""        if(ld1) ld1.innerHTML='<span class="lb">'+d.baseCents.toFixed(1)+'¢</span><span class="lead-lab">built in</span><span class="lead-op">+</span><span class="lt">'+d.topUp.toFixed(1)+'¢</span><span class="lead-lab">your top-up</span><span class="lead-op">=</span>';""",
  """        if(ld1) ld1.innerHTML='<span class="lb">'+d.baseCents.toFixed(1)+window.__nfCup().sym+'</span><span class="lead-lab">built in</span><span class="lead-op">+</span><span class="lt">'+d.topUp.toFixed(1)+window.__nfCup().sym+'</span><span class="lead-lab">your top-up</span><span class="lead-op">=</span>';"""),
 ("""<span class="lw">'+d.combined.toFixed(1)+'¢</span><span class="lead-op">=</span>';""",
  """<span class="lw">'+d.combined.toFixed(1)+window.__nfCup().sym+'</span><span class="lead-op">=</span>';"""),
 ("""      if(phase>=2) lockedRow.appendChild(chip('Top-up · '+(d.topUp>0?'+'+d.topUp.toFixed(1)+'¢':'none'),1));""",
  """      if(phase>=2) lockedRow.appendChild(chip('Top-up · '+(d.topUp>0?'+'+d.topUp.toFixed(1)+window.__nfCup().sym:'none'),1));"""),
 ("""  set('qCoffeeSub', 'Includes ' + bandCup.toFixed(1) + '\\u00a2/cup built-in NGO share ('""",
  """  set('qCoffeeSub', 'Includes ' + bandCup.toFixed(1) + __nfCupTable().sym + '/cup built-in NGO share ('"""),
 ("""  set('qTopUpSub', '+' + topCup.toFixed(1) + '\\u00a2/cup top-up · '""",
  """  set('qTopUpSub', '+' + topCup.toFixed(1) + __nfCupTable().sym + '/cup top-up · '"""),
 ("""      + ' passed directly to NGO partners · ~' + ngoCup.toFixed(1) + '\\u00a2/cup.'""",
  """      + ' passed directly to NGO partners · ~' + ngoCup.toFixed(1) + __nfCupTable().sym + '/cup.'"""),
 ("""+'\\u00a2 a cup, ~'+CURP+' '+dYr+'/yr more to the forests';""",
  """+window.__nfCup().sym+' a cup, ~'+CURP+' '+dYr+'/yr more to the forests';"""),
 ("""+gainCup.toFixed(1).replace(/\\.0$/,'')+'¢ a cup, and ~'+CURP+' '+gainYr.toLocaleString('en-SG')""",
  """+gainCup.toFixed(1).replace(/\\.0$/,'')+window.__nfCup().sym+' a cup, and ~'+CURP+' '+gainYr.toLocaleString('en-SG')"""),
]
for old, new in reps:
    n = src.count(old)
    assert n == 1, "unit anchor not unique (%d): %s" % (n, old[:70])
    src = src.replace(old, new)


# ── 7 · the gutter cards speak the market too ─────────────────────────────
# Alex: "ensure guttering position and message within also reacts to AED.
# right now it's stuck in SGD parlance. likewise on 3b."
# The three pairs are built once, at init, from literal SGD prose ("At SGD 45
# that slice is 5%, about 4.1 cents a cup ... a voluntary few cents per cup ...
# cent for cent"). They become templates over the market's band table and cup
# words, rebuilt by the market switch. The per-cup figures use the same
# 1000/18 conversion as the hero, so card and figure cannot disagree.
old = """      var gr=mk('r','Where it goes','<p>Every kilo you buy carries a conservation share: a slice of <b>what you pay</b> that goes straight to the NGOs and farmers, on top of the coffee itself.</p><p>At <b>SGD 45</b> that slice is <b>5%</b>, about <b>4.1 cents</b> a cup. From <b>48</b> it steps up to <b>7.5%</b> (about <b>6.5 cents</b>), and from <b>51</b> the full <b>10%</b> (about <b>9.2 cents</b>).</p><p>Small numbers on a cup, real money at the forest edge: across the climb, what reaches the forest <b>more than doubles</b>.</p>');"""
new = """      /* block 76 — the right card is a template over the market's bands */
      function __whereItGoes(){
        var M = window.__nfMkt ? window.__nfMkt() : null;
        var c = window.__nfCup();
        var cur = window.__nfCur || 'SGD';
        var B = (M && M.bands) || [{from:45,rate:.05},{from:48,rate:.075},{from:51,rate:.1}];
        var cup = function(b){ return (b.from*b.rate/(1000/18)*100).toFixed(1); };
        var pct = function(b){ return (b.rate*100).toString().replace(/\\.0$/,'')+'%'; };
        return '<p>Every kilo you buy carries a conservation share: a slice of <b>what you pay</b> that goes straight to the NGOs and farmers, on top of the coffee itself.</p>'
          + '<p>At <b>'+cur+' '+Math.round(B[0].from)+'</b> that slice is <b>'+pct(B[0])+'</b>, about <b>'+cup(B[0])+' '+c.word+'</b> a cup. From <b>'+Math.round(B[1].from)+'</b> it steps up to <b>'+pct(B[1])+'</b> (about <b>'+cup(B[1])+' '+c.word+'</b>), and from <b>'+Math.round(B[2].from)+'</b> the full <b>'+pct(B[2])+'</b> (about <b>'+cup(B[2])+' '+c.word+'</b>).</p>'
          + '<p>Small numbers on a cup, real money at the forest edge: across the climb, what reaches the forest <b>more than doubles</b>.</p>';
      }
      var gr=mk('r','Where it goes',__whereItGoes());
      window.__nfRefreshPriceGutter = function(){ gr.innerHTML='<p class="mgut-eyebrow">Where it goes</p>'+__whereItGoes(); };"""
assert src.count(old) == 1, "where-it-goes anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """      var gl=mk('l','What this is','<p>Want to hit a per-cup conservation target? This is the dial: a voluntary few cents per cup, on top of the price you just set.</p><p>Every cent goes to the conservation NGOs; none of it touches our margin. Skipping it changes nothing about your agreement.</p>');
      var gr=mk('r','How it adds up','<p>Your price already sends its built-in share, the figure above. The top-up stacks on that, cent for cent.</p><p>Small numbers travel: at scale, a cent a cup is real money at the forest edge.</p>');"""
new = """      /* block 76 — the top-up pair takes the market's cup words */
      function __whatThisIs(){ var c=window.__nfCup();
        return '<p>Want to hit a per-cup conservation target? This is the dial: a voluntary few '+c.word+' per cup, on top of the price you just set.</p><p>Every '+c.one+' goes to the conservation NGOs; none of it touches our margin. Skipping it changes nothing about your agreement.</p>'; }
      function __howItAddsUp(){ var c=window.__nfCup();
        return '<p>Your price already sends its built-in share, the figure above. The top-up stacks on that, '+c.one+' for '+c.one+'.</p><p>Small numbers travel: at scale, a '+c.one+' a cup is real money at the forest edge.</p>'; }
      var gl=mk('l','What this is',__whatThisIs());
      var gr=mk('r','How it adds up',__howItAddsUp());
      window.__nfRefreshTopupGutters = function(){
        gl.innerHTML='<p class="mgut-eyebrow">What this is</p>'+__whatThisIs();
        gr.innerHTML='<p class="mgut-eyebrow">How it adds up</p>'+__howItAddsUp(); };"""
assert src.count(old) == 1, "topup gutters anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# the cup table gains the singular; the market is exposed for the template
old = """        cup:{ sym:'\\u00a2', word:'cents', topMax:7.5, topStep:0.1, ten:10, stretch:12 },"""
new = """        cup:{ sym:'\\u00a2', word:'cents', one:'cent', topMax:7.5, topStep:0.1, ten:10, stretch:12 },"""
assert src.count(old) == 1; src = src.replace(old, new)
old = """        cup:{ sym:' fils', word:'fils', topMax:22.5, topStep:0.5, ten:30, stretch:36 },"""
new = """        cup:{ sym:' fils', word:'fils', one:'fil', topMax:22.5, topStep:0.5, ten:30, stretch:36 },"""
assert src.count(old) == 1; src = src.replace(old, new)
old = """window.__nfCup = __nfCupTable;"""
new = """window.__nfCup = __nfCupTable;
window.__nfMkt = function(){ return (typeof MKT !== 'undefined') ? MKT : null; };"""
assert src.count(old) == 1; src = src.replace(old, new)

# the market switch rebuilds the cards and flags the hero's unit style
old = """  if(window.__nfUniRender) window.__nfUniRender();"""
new = """  if(window.__nfUniRender) window.__nfUniRender();
  if(window.__nfRefreshPriceGutter) window.__nfRefreshPriceGutter();
  if(window.__nfRefreshTopupGutters) window.__nfRefreshTopupGutters();
  /* a one-glyph unit (¢) rides at the digits' size; a word (fils) at
     full display size ran the hero under both gutter cards */
  (function(){ var f=document.getElementById('morphFigure'); if(f) f.classList.toggle('unit-word', __nfCupTable().sym.trim().length>1); })();"""
assert src.count(old) == 1; src = src.replace(old, new)

# ── 8 · the hero's unit is wrapped so a word can be sized ─────────────────
reps2 = [
 ("""        if(ld1) ld1.innerHTML='<span class="lb">'+d.baseCents.toFixed(1)+window.__nfCup().sym+'</span><span class="lead-lab">built in</span><span class="lead-op">+</span><span class="lt">'+d.topUp.toFixed(1)+window.__nfCup().sym+'</span><span class="lead-lab">your top-up</span><span class="lead-op">=</span>';""",
  """        if(ld1) ld1.innerHTML='<span class="lb">'+d.baseCents.toFixed(1)+'<span class="lu">'+window.__nfCup().sym+'</span></span><span class="lead-lab">built in</span><span class="lead-op">+</span><span class="lt">'+d.topUp.toFixed(1)+'<span class="lu">'+window.__nfCup().sym+'</span></span><span class="lead-lab">your top-up</span><span class="lead-op">=</span>';"""),
 ("""<span class="lw">'+d.combined.toFixed(1)+window.__nfCup().sym+'</span><span class="lead-op">=</span>';""",
  """<span class="lw">'+d.combined.toFixed(1)+'<span class="lu">'+window.__nfCup().sym+'</span></span><span class="lead-op">=</span>';"""),
]
for old, new in reps2:
    assert src.count(old) == 1, "lead wrap anchor not unique: %s" % old[:60]
    src = src.replace(old, new)

# ── 9 · the gutters shrink to fit rather than climbing onto the hero ───────
# Block 75's clamp moved a card UP when it could not fit under the hero; on
# AED, where the hero is taller and the right card longer, that put the card
# on the figure. Cards keep their anchor and take a max-height instead — they
# already scroll inside (block 68).
old = """        (function(){ var sg=document.getElementById('morphStage'); if(!sg) return;
          var sr=sg.getBoundingClientRect(), maxTop=sr.bottom-24-Math.max(gl.offsetHeight,gr.offsetHeight);
          if(anchorTop>maxTop) anchorTop=Math.max(sr.top+72, maxTop); })();"""
new = """        (function(){ var sg=document.getElementById('morphStage'); if(!sg) return;
          /* block 76 (2) — Alex: "allow the gutter to render full size without
             the scroll." No clamp, no clip: the card is as tall as its copy.
             It records how far past the frame's foot it runs, for the trim
             decision, and does nothing else about it. */
          var sr=sg.getBoundingClientRect();
          gl.style.maxHeight=''; gr.style.maxHeight='';
          gl.dataset.over=Math.max(0,Math.round(anchorTop+gl.offsetHeight-(sr.bottom-24)));
          gr.dataset.over=Math.max(0,Math.round(anchorTop+gr.offsetHeight-(sr.bottom-24))); })();   /* block 76 */"""
assert src.count(old) == 2, "gutter clamp count %d (expected 2)" % src.count(old)
src = src.replace(old, new)
old = """          (function(){ var sg=document.getElementById('morphStage'); if(!sg) return;
            var sr=sg.getBoundingClientRect(), maxTop=sr.bottom-24-Math.max(yl.offsetHeight,yr.offsetHeight);
            if(t>maxTop) t=Math.max(sr.top+72, maxTop); })();"""
new = """          (function(){ var sg=document.getElementById('morphStage'); if(!sg) return;
            var sr=sg.getBoundingClientRect();
            yl.style.maxHeight=''; yr.style.maxHeight='';
            yl.dataset.over=Math.max(0,Math.round(t+yl.offsetHeight-(sr.bottom-24)));
            yr.dataset.over=Math.max(0,Math.round(t+yr.offsetHeight-(sr.bottom-24))); })();   /* block 76 */"""
assert src.count(old) == 1, "year gutter clamp not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 76 · A UNIT THAT IS A WORD ═══════════════════════════════════════════
   ¢ is one glyph and rides at the digits' size. "fils" is four, and at 104px
   it put the AED hero under both gutter cards and hid the currency behind the
   left one. When the market's unit is a word it is set small, off the digits'
   baseline, with a hair of space. */
.morph-figure.unit-word .mu,
.morph-figure.unit-word .mu-imp{font-size:.42em;margin-left:.12em;letter-spacing:0;}
.morph-figure.unit-word .mfig-lead .lu{font-size:.62em;margin-left:.1em;}

/* ── the gutter cards are as tall as their copy ───────────────────────────
   Block 68 gave them max-height:min(46vh,420px) and an inner scrollbar; a
   card you can only scroll while hovering the slider is unreadable. */
.mgut{max-height:none;overflow:visible;}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)


# ── 10 · the cards stay for the phase; the pointer may leave the track ────
# Alex: "the moment my cursor leaves the line the gutter disappears which
# means I can't scroll up and down it." Hover-gating on the TRACK meant the
# card vanished the instant you moved toward it. Each pair is shown by its
# phase now and hidden by the next; enter/focus still show (harmless), leave/
# blur no longer hide.
old = """      track.addEventListener('mouseleave',hide);
      track.addEventListener('focusin',show);
      track.addEventListener('focusout',hide);"""
assert src.count(old) == 2, "hover hide count %d (expected 2)" % src.count(old)
src = src.replace(old, """      /* block 76 — no hide on leave: the card is a thing to read, not a tooltip */
      track.addEventListener('focusin',show);""")
old = """        track.addEventListener('mouseleave',yhide);
        track.addEventListener('focusin',yshow);
        track.addEventListener('focusout',yhide);"""
assert src.count(old) == 1, "year hover hide not unique (%d)" % src.count(old)
src = src.replace(old, """        track.addEventListener('focusin',yshow);   /* block 76 — no hide on leave */""")
old = """      if(window.__nfTopupGutters && p!==1) window.__nfTopupGutters.hide();
      if(window.__nfPriceGutters && p!==0) window.__nfPriceGutters.hide();"""
new = """      /* block 76 — each phase shows its own pair and retires the others. The
         timeout is one tick so the phase class and the control the cards are
         measured against are in place first. */
      if(window.__nfPriceGutters){ if(p===0) setTimeout(window.__nfPriceGutters.show,80); else window.__nfPriceGutters.hide(); }
      if(window.__nfTopupGutters){ if(p===1) setTimeout(window.__nfTopupGutters.show,80); else window.__nfTopupGutters.hide(); }
      if(window.__nfYearGutters){  if(p===2) setTimeout(window.__nfYearGutters.show,80);  else window.__nfYearGutters.hide(); }"""
assert src.count(old) == 1, "phase hide anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
# and the price pair appears on first load without waiting for a phase change
old = """      window.__nfPriceGutters={show:show,hide:hide};"""
new = """      window.__nfPriceGutters={show:show,hide:hide};
      setTimeout(show, 400);   /* block 76 — on first load, before any phase change */"""
assert src.count(old) == 1
src = src.replace(old, new)


# ── 11 · "See your quote" drives the real button; the corner one steps aside ─
# Alex: "see your quote doesn't work, also confusing as we have 'your quote'
# which does work." #deckNext0 does not exist — the corner button was never
# given that id — so the in-card click was a no-op, and the corner button's
# own show/hide (dn0) has been dead code since it was written. The in-card
# button now clicks the active screen's real .deck-next; on 3C the corner one
# is hidden so there is one action, and it returns on 3A/3B.
old = """      else if(phase===2){ var q=document.getElementById('deckNext0'); if(q) q.click(); }"""
new = """      else if(phase===2){ var q=document.querySelector('.deck-screen.is-active .deck-next'); if(q) q.click(); }"""
assert src.count(old) == 1, "in-card click anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
old = """      var dn0=$('deckNext0'); if(dn0) dn0.style.display = (p>=2 || maxPhase>=2) ? '' : 'none';"""
new = """      /* block 76 — the corner "Your quote →" yields to the in-card button on
         the year phase; #deckNext0 never existed, so the old line did nothing */
      (function(){ var dn=document.querySelector('.deck-screen.is-active .deck-next'); if(dn) dn.style.visibility = (p===2) ? 'hidden' : ''; })();"""
assert src.count(old) == 1, "dn0 anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 12 · the gutters leave with the wizard ────────────────────────────────
# Alex: "the gutter survives into quote page too." The pairs are fixed-position
# body children shown by wizard PHASE, and moving to step 4 changes the deck's
# screen, not the phase. A class observer on the deck hides every pair when
# the active screen is not the price step, and re-shows the phase's pair when
# it is again.
old = """      window.__nfPriceGutters={show:show,hide:hide};
      setTimeout(show, 400);   /* block 76 — on first load, before any phase change */"""
new = """      window.__nfPriceGutters={show:show,hide:hide};
      setTimeout(show, 400);   /* block 76 — on first load, before any phase change */
      (function(){
        var wrap=document.getElementById('nfConsoleWrap'); if(!wrap || !window.MutationObserver) return;
        var last=null;
        function check(){
          var scr=[...wrap.querySelectorAll('.deck-screen')], idx=scr.findIndex(function(s){ return s.classList.contains('is-active'); });
          if(idx===last) return; last=idx;
          var on = idx===2 && wrap.classList.contains('nf-focus-sec');
          var P=window.__nfPriceGutters, T=window.__nfTopupGutters, Y=window.__nfYearGutters;
          if(!on){ P&&P.hide(); T&&T.hide(); Y&&Y.hide(); return; }
          var st=document.getElementById('morphStage');
          var ph = st ? (st.classList.contains('year') ? 2 : (st.classList.contains('ph-topup') ? 1 : 0)) : 0;
          setTimeout(function(){ if(ph===0&&P) P.show(); if(ph===1&&T) T.show(); if(ph===2&&Y) Y.show(); }, 120);
        }
        new MutationObserver(check).observe(wrap,{attributes:true,subtree:true,attributeFilter:['class']});
      })();"""
assert src.count(old) == 1, "gutter observer anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("wizard speaks the market's cents")
