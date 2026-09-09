import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 93 · A ROUTE'S MEDIA WARMS ON ARRIVAL, NOT UNDER THE READER'S THUMB ═══
# Alex, 3 Sep: "the judder still exists on the wholesale coffee section, when
# scrolling up and down." Measured in his own Chrome on 02g, a scripted
# top-to-bottom-and-back over At Work: the first pass had 7 frames over 32ms
# (worst 74ms) and the second pass, same page, had 1 (worst 44ms) and no long
# tasks either time. So it is not layout or script — it is the first-pass
# cost of things starting mid-scroll: since block 86 each video is given its
# file and starts decoding only as it comes within a screen of the viewport,
# and the evidence-map iframe boots Google Maps 1400px out. Both are the
# right thing for a route nobody has opened; they are the wrong thing while
# the reader is scrolling through it.
#   · on arrival at a route, its videos are given their files (src, load) one
#     every 200ms, so the bytes buffer and the decoders can be primed while
#     the reader is still on the first screen; play still waits for the
#     observer, as before, so nothing off-screen decodes;
#   · the evidence-map iframe loads 1.2s after arrival on At Work rather than
#     when the reader is 1400px from it.
# Off-route media is untouched: still lazy, still nothing until its route.
fix("""  function hydrate(v){
    if(v.__nfWet) return; v.__nfWet = true;
    var nodes = [v].concat([].slice.call(v.querySelectorAll('source[data-src]'))), did = false;
    nodes.forEach(function(n){
      var s = n.getAttribute('data-src');
      if(s && !n.getAttribute('src')){ n.setAttribute('src', s); n.removeAttribute('data-src'); did = true; }
    });
    if(!did) return;
    if(v.dataset && v.dataset.poster){ v.poster = v.dataset.poster; delete v.dataset.poster; }
    try{ v.load(); }catch(e){}
    if(v.classList.contains('vf') && typeof armVideos === 'function'){ armVideos(); return; }
    if(RMq) return;
    try{ var p = v.play(); if(p && p.catch) p.catch(function(){}); }catch(e){}
  }""",
    """  /* block 93 — wet(): the file, the poster and load(), nothing more; the
     route warms its videos with this on arrival */
  function wet(v){
    if(v.__nfWet) return true; v.__nfWet = true;
    var nodes = [v].concat([].slice.call(v.querySelectorAll('source[data-src]'))), did = false;
    nodes.forEach(function(n){
      var s = n.getAttribute('data-src');
      if(s && !n.getAttribute('src')){ n.setAttribute('src', s); n.removeAttribute('data-src'); did = true; }
    });
    if(!did) return false;
    if(v.dataset && v.dataset.poster){ v.poster = v.dataset.poster; delete v.dataset.poster; }
    try{ v.load(); }catch(e){}
    return true;
  }
  function hydrate(v){
    if(v.__nfPlayed) return; v.__nfPlayed = true;
    if(!wet(v)) return;
    if(v.classList.contains('vf') && typeof armVideos === 'function'){ armVideos(); return; }
    if(RMq) return;
    try{ var p = v.play(); if(p && p.catch) p.catch(function(){}); }catch(e){}
  }
  window.__nfWarmRoute = function(root){
    if(!root || !root.querySelectorAll) return;
    var list = [].slice.call(root.querySelectorAll('video')).filter(function(v){
      return !v.__nfWet && (v.getAttribute('data-src') || v.querySelector('source[data-src]'));
    });
    list.forEach(function(v, i){ setTimeout(function(){ wet(v); }, 300 + i * 200); });
  };""")

fix("""  routeFrames(r);            /* deferred iframes load on arrival — see pass101 */            /* everything off this route stops decoding */""",
    """  routeFrames(r);            /* deferred iframes load on arrival — see pass101 */            /* everything off this route stops decoding */
  if(window.__nfWarmRoute) window.__nfWarmRoute(sec);          /* block 93 */
  try{ document.dispatchEvent(new CustomEvent('nf:route', { detail: r })); }catch(e){}""")

fix("""    function load(){ if(!frame.src) frame.src = frame.getAttribute('data-counter-src'); }""",
    """    function load(){ if(!frame.src) frame.src = frame.getAttribute('data-counter-src'); }
    /* block 93 — on arrival at At Work the map boots while the reader is on
       the first screen, not when they are 1400px from it mid-scroll */
    document.addEventListener('nf:route', function(e){
      if(e.detail === 'work') setTimeout(load, 1200);
    });
    if(window.__nfRoute === 'work') setTimeout(load, 1200);""")

io.open(F, "w", encoding="utf-8").write(src)
print("route media warms on arrival")
