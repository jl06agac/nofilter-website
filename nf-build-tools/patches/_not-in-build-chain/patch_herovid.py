import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 91 · THE HERO VIDEO WAITS FOR THE PAGE; ITS TWO GHOSTS WAIT FOR IT ═════
# Alex, 3 Sep: "i loaded nofilter.sg this morning and it was really quite
# slow to load". PageSpeed (mobile, on 02d): first paint 1.7 s, largest paint
# 3.6 s, and the largest-paint element is the hero video — its poster, which
# arrives late because from the first script onwards it is sharing the line
# with three copies of a 3.2 MB video (the hero and the two RGB-split layers
# behind it, which are invisible except for a 0.6 s flicker on roughly one
# LINE glitch in five, and never before the twelve-second mark) and the
# 0.5 MB mega-farm layer. All four were hydrated the moment block 86's
# observer saw them, i.e. at boot.
#   · data-defer="load"   — the hero and the mega layer wait for the window's
#     load event: the poster, the fonts and the document are in by then, and
#     the poster is what the reader sees first either way;
#   · data-defer="settle" — the two glitch layers wait a further four seconds;
#     they come out of the HTTP cache once the hero has streamed, so this
#     costs bytes nothing and spares the CPU two decodes during the load.
# From disk nothing changes: file:// fires load in milliseconds.
fix("""    <video class="cover-video vf" poster="../../_CDN-UPLOAD-SAFE/hero-poster.jpg" autoplay muted loop playsinline preload="auto">
      <source data-src="hero-trim-fast.mp4" type="video/mp4">
    </video>
    <video class="cover-video cover-video--cyan" aria-hidden="true" autoplay muted loop playsinline preload="metadata">
      <source data-src="hero-trim-fast.mp4" type="video/mp4">
    </video>
    <video class="cover-video cover-video--red" aria-hidden="true" autoplay muted loop playsinline preload="metadata">
      <source data-src="hero-trim-fast.mp4" type="video/mp4">
    </video>
    <video class="cover-mega" aria-hidden="true" autoplay muted loop playsinline preload="auto">
      <source data-src="mega-farm-test-lite.mp4" type="video/mp4">
    </video>""",
    """    <video class="cover-video vf" poster="../../_CDN-UPLOAD-SAFE/hero-poster.jpg" autoplay muted loop playsinline preload="auto" data-defer="load">
      <source data-src="hero-trim-fast.mp4" type="video/mp4">
    </video>
    <video class="cover-video cover-video--cyan" aria-hidden="true" autoplay muted loop playsinline preload="metadata" data-defer="settle">
      <source data-src="hero-trim-fast.mp4" type="video/mp4">
    </video>
    <video class="cover-video cover-video--red" aria-hidden="true" autoplay muted loop playsinline preload="metadata" data-defer="settle">
      <source data-src="hero-trim-fast.mp4" type="video/mp4">
    </video>
    <video class="cover-mega" aria-hidden="true" autoplay muted loop playsinline preload="auto" data-defer="load">
      <source data-src="mega-farm-test-lite.mp4" type="video/mp4">
    </video>""")

fix("""  function scan(root){
    [].slice.call((root || document).querySelectorAll('video')).forEach(function(v){
      if(v.__nfWatched) return;
      if(!(v.getAttribute('data-src') || v.querySelector('source[data-src]'))) return;
      v.__nfWatched = true;
      if(io) io.observe(v); else hydrate(v);
    });
  }""",
    """  /* block 91 — a video may ask to wait for the page: data-defer="load" is
     watched from the load event, "settle" four seconds after it */
  function afterLoad(fn, extra){
    var go = function(){ if(extra) setTimeout(fn, extra); else fn(); };
    if(document.readyState === 'complete') go();
    else window.addEventListener('load', go, { once:true });
  }
  function watch(v){ if(io) io.observe(v); else hydrate(v); }
  function scan(root){
    [].slice.call((root || document).querySelectorAll('video')).forEach(function(v){
      if(v.__nfWatched) return;
      if(!(v.getAttribute('data-src') || v.querySelector('source[data-src]'))) return;
      v.__nfWatched = true;
      var d = v.getAttribute('data-defer');
      if(d === 'load') afterLoad(function(){ watch(v); });
      else if(d === 'settle') afterLoad(function(){ watch(v); }, 4000);
      else watch(v);
    });
  }""")

io.open(F, "w", encoding="utf-8").write(src)
print("hero video waits for load; glitch layers settle after")
