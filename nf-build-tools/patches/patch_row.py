import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the card does not move until the row has gone ─────────────────────
subs.append((
"""    requestAnimationFrame(function(){ requestAnimationFrame(function(){
      mo.style.transition = 'top .38s cubic-bezier(.45,0,.35,1)';
      mo.style.top = l.top + 'px';
    }); });""",
"""    /* ── 1 Sep · LIFT, THEN DROP ─────────────────────────────────────────
       Alex's flight recorder, run on his machine, frame 0 of the failing
       flight: proxyTop 130, rowOpacity 1, overlap 530. The card was already
       flying while the row it left was still fully painted, and the row did
       not reach 0 until the card was half way through it (rowOpacity .52 at
       t=62, .08 at t=125). The coffee version never shows this because its
       row is ALREADY gone before openDossier runs.
       So the descent waits 150ms — the length of the row's fade — before the
       top transition starts. What the eye gets is a beat: the row dims around
       the card, then the card drops through cleared space. */
    setTimeout(function(){
      mo.style.transition = 'top .38s cubic-bezier(.45,0,.35,1)';
      mo.style.top = l.top + 'px';
    }, 150);"""))

# ── 2 · the fade-out is quick enough to finish inside that beat ───────────
subs.append((
"""    if(grid){
      grid.style.transition = 'opacity .18s ease';
      grid.style.opacity = '0';
    }""",
"""    if(grid){
      grid.style.transition = 'opacity .13s ease';
      grid.style.opacity = '0';
    }"""))

# ── 3 · landed() brings the row back — the ONLY place that does ───────────
subs.append((
"""    var landed = function(){
      if(finished) return; finished = true;
      mo.removeEventListener('transitionend', onEnd); clearTimeout(morphT);
      clearTimeout(unhideT); unhideCards();""",
"""    var landed = function(){
      if(finished) return; finished = true;
      mo.removeEventListener('transitionend', onEnd); clearTimeout(morphT);
      clearTimeout(unhideT);
      /* ── 1 Sep · THE COFFEE INVARIANT, ENFORCED ─────────────────────────
         Alex's recorder on the WORKING coffee flight: rowBottom is 0 on every
         frame — while a proxy exists, the row does not. His recorder on MINE:
         rowOpacity climbing .11 -> 1.0 between t=445 and t=766 while the
         proxy was only 682px of 1320 wide. I was restoring the row at the
         expand beat, so a full-opacity row and a half-expanded proxy shared
         the screen — which is every overlap he photographed. The restore now
         happens HERE, two lines above display:none, and nowhere else: the row
         and the proxy can no longer coexist. */
      if(grid){ grid.style.transition = 'opacity .3s ease'; grid.style.opacity = '1'; }
      setTimeout(unhideCards, 340);"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("row and proxy can no longer coexist")
