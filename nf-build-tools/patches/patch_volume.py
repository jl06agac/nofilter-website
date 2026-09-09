import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 109 · ONE VOLUME: THE CUPS THE READER SET ══════════════════════════════
# Alex, 3 Sep, on the desk email and the Netlify Forms copy: "why am i still
# getting this coffee volume nonsense of 5kg?! no one is selecting 5kg
# anywhere... i can only assume it's a relic." It is. On 25 Aug the per-origin
# kg stepper came off the coffee tiles ("picking an origin is the act") and Q
# was left holding a nominal 5 kg per pick so the maths had something to
# multiply. That nominal number then flowed into everything the reader never
# touched: the deck tally, the sheet's COFFEE line, the monthly total, the
# contribution per month, the desk email, the Forms backstop — and
# "estimated from 3,333 cups a year", which is the 5 kg worked backwards, not
# anything anyone said. Meanwhile the one volume control the reader DOES
# operate, the cups-a-year slider on 3C, fed only the story's own figures.
# Two volumes, and the emails reported the one nobody set.
# Now there is one: the slider. Kilos are derived from it at the dose every
# figure on the site uses (18 g a cup, ÷12 for a month) and shared equally
# across the origins picked; Q.kg is only the pick flag it had already become.
# Moving the slider recomputes the console, so the tally, the sheet and both
# emails say what the reader set.
fix("""function compute(){
  var kgTotal = 0, coffeeLines = [];
  ORIGINS.forEach(function(o){
    var kg = Q.kg[o.k]; if(!kg) return;
    kgTotal += kg;
    coffeeLines.push({ n: o.name + ' · ' + kg + ' kg', v: kg * Q.price });
  });""",
    """/* block 109 — the reader's volume, from the one control that sets it */
window.__nfVolCups = function(){ var vs = document.getElementById('volCups'); return vs ? (+vs.value || 0) : 43000; };
window.__nfVolKg = function(picks){
  if(!picks) return 0;
  return Math.round(window.__nfVolCups() * 18 / 1000 / 12 * 10) / 10;      /* kg a month at 18 g a cup */
};
function compute(){
  var kgTotal = 0, coffeeLines = [];
  var picked = ORIGINS.filter(function(o){ return !!Q.kg[o.k]; });
  var kgAll = window.__nfVolKg(picked.length);
  var share = picked.length ? Math.round(kgAll / picked.length * 10) / 10 : 0;
  picked.forEach(function(o){
    kgTotal += share;
    coffeeLines.push({ n: o.name + ' · ' + share + ' kg', v: share * Q.price });
  });
  kgTotal = Math.round(kgTotal * 10) / 10;""")

# the deck tally reads the same number
fix("""    var kg = 0, units = 0;
    try{ for(var k in window.__nfQ.kg) kg += window.__nfQ.kg[k]||0; }catch(e){}""",
    """    var kg = 0, units = 0, picks = 0;
    try{ for(var k in window.__nfQ.kg) if(window.__nfQ.kg[k]) picks++; }catch(e){}     /* block 109 */
    kg = window.__nfVolKg ? window.__nfVolKg(picks) : 0;""")

# the slider drives the console, not just the story. recalc() lives in the
# console's own scope (typeof recalc is 'undefined' from the page), so it is
# published beside __nfSetPrice, which is how the price dial already reaches it.
fix("""window.__nfSetPrice = function(p){
  if(Math.abs(Q.price - p) < 0.001) return;
  Q.price = p;
  if(slider) slider.value = String(p);
  recalc();
};""",
    """window.__nfSetPrice = function(p){
  if(Math.abs(Q.price - p) < 0.001) return;
  Q.price = p;
  if(slider) slider.value = String(p);
  recalc();
};
window.__nfRecalc = function(){ try{ recalc(); }catch(e){} };          /* block 109 */""")
fix("""    if(volSlider) volSlider.addEventListener('input',function(){ volSlider.classList.remove('thumb-pulse'); paint(false); });""",
    """    if(volSlider) volSlider.addEventListener('input',function(){ volSlider.classList.remove('thumb-pulse'); paint(false);
      if(window.__nfRecalc) window.__nfRecalc();                       /* block 109 */ });""")

# the payload says the cups as set, not the kilos worked backwards
fix("""          cupsY:     (c && c.kgTotal) ? Math.round(c.kgTotal * 12 * 1000 / 18) : null""",
    """          cupsY:     (c && c.kgTotal && window.__nfVolCups) ? window.__nfVolCups() : null   /* block 109 */""")

io.open(F, "w", encoding="utf-8").write(src)
print("one volume: the cups the reader set")
