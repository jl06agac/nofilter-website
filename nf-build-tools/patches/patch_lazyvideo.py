import io, re, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 86 · A VIDEO LOADS WHEN IT IS ABOUT TO BE SEEN, NOT WHEN THE PAGE IS ═══
# Alex, 2 Sep, first load of /shop in incognito: "all bag tile images … aren't
# fast to load, i see them still loading for the first few seconds", and the
# same on the origin banners.
# Why: this file carries 22 <video> tags with a src, every one of them
# preload="metadata". A browser starts fetching metadata for each the moment
# the tag is parsed — hidden routes included — so a reader opening the shop
# had 22 range requests to the CDN in flight before the four bag tiles got a
# turn. The 29/30 Aug bundles did not have this: their builder moved every
# src to data-src and hydrated a video only as it approached the viewport.
# That lived only in the builder, so it was lost with it; it lives here now.
#   · every static <video src> and <source src> becomes data-src (the two
#     that are written by JS from a template are untouched);
#   · one IntersectionObserver watches every such video from boot, with a
#     100% root margin, and hydrates it when it is one screen away — a video
#     inside a display:none route or a hidden drawer never intersects, so it
#     never loads until its route or drawer opens;
#   · hydration sets src, promotes the deferred poster, load()s, hands .vf
#     videos to armVideos (which now skips anything still dry, so the 4.5s
#     "dead" verdict cannot fall on a video that was simply not asked for),
#     and plays unless the reader prefers reduced motion.
pat = re.compile(r'(<(?:video|source)\b[^>]*?)\ssrc="([^"]+\.mp4)"')
n = len(pat.findall(src))
assert n == 22, "expected 22 static video sources, found %d" % n
src = pat.sub(r'\1 data-src="\2"', src)

fix("""    var _r = v.closest('.route');
    if(_r && _r.id !== current) return;
    if(v.getAttribute('data-armed') === '1') return;""",
    """    var _r = v.closest('.route');
    if(_r && _r.id !== current) return;
    /* block 86 — not yet hydrated: nothing to arm, and nothing to call dead */
    if(v.getAttribute('data-src') || v.querySelector('source[data-src]')) return;
    if(v.getAttribute('data-armed') === '1') return;""")

fix("""/* ── 6b · HERO COVER TREATMENT ────────────────────────────────────────────""",
    """/* ── block 86 · LAZY VIDEO ─────────────────────────────────────────────── */
(function(){
  var RMq = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  function hydrate(v){
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
  }
  var io = ('IntersectionObserver' in window)
    ? new IntersectionObserver(function(es){
        es.forEach(function(e){ if(e.isIntersecting){ io.unobserve(e.target); hydrate(e.target); } });
      }, { rootMargin:'100% 0px' })
    : null;
  function scan(root){
    [].slice.call((root || document).querySelectorAll('video')).forEach(function(v){
      if(v.__nfWatched) return;
      if(!(v.getAttribute('data-src') || v.querySelector('source[data-src]'))) return;
      v.__nfWatched = true;
      if(io) io.observe(v); else hydrate(v);
    });
  }
  scan(document);
  window.__nfLazyVideoScan = scan;   /* for anything that inserts a <video data-src> later */
})();

/* ── 6b · HERO COVER TREATMENT ────────────────────────────────────────────""")

# ══ 87 · THE BAG TILES LOAD THE 640px CUT ═════════════════════════════════
# The four bag images are drawn at tile size, yet every reference was to the
# 1024×1536 cut (≈387 KB each, 1.5 MB for the set). The 640×960 cuts have been
# in _CDN-UPLOAD-SAFE since 28 Aug (≈64 KB each) and the 29/30 Aug bundles
# used them — by builder rewrite, again. The master now names them itself.
bags = re.compile(r"bag-(arakan|batang-gadis|batang-toru|gayo-lues)\.webp")
n = len(bags.findall(src))
assert n == 12, "expected 12 bag references, found %d" % n
src = bags.sub(r"bag-\1-640.webp", src)

io.open(F, "w", encoding="utf-8").write(src)
print("videos hydrate on approach; bag tiles take the 640 cut")
