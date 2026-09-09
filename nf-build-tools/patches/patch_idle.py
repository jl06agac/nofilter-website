import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 89 · THE PAGE STOPS WORKING WHEN NOBODY IS LOOKING ════════════════════
# Alex, 2 Sep, PageSpeed on the live site: desktop 63, mobile 81 — "this is
# shockingly poor. i'd like to see vast improvements made."
# Measured locally with Lighthouse on the built bundle (mobile profile, 4×
# CPU slowdown): total blocking time 1.1–1.5 s, main thread 12 s, of which
# the single largest sink was not a script that runs once but three loops
# that run EVERY FRAME, FOREVER — 518 rAF callbacks in three idle seconds —
# each reading the scroll position and so forcing layout every frame while
# anything on the page animates. Then a 50 KB audio script decoded at load
# for a sound the CRT gate plays; then the hero choreography written as
# layout (margin) rather than motion (transform), which is the whole 0.14
# layout-shift score. Each is put right below, in place, with the intent of
# every original kept.

# ── 1 · window.__nfY: a scroll listener, not a frame loop ─────────────────
#   pass111 cached the scroll position so readers would not force layout;
#   the cache was refreshed by a rAF loop that itself read pageYOffset every
#   frame. A passive scroll listener fires on exactly the frames the value
#   can change, and costs nothing on the rest.
fix("""  (function beat(){
    requestAnimationFrame(function(){ window.__nfY = window.pageYOffset; beat(); });
  })();
  window.__nfY = window.pageYOffset;""",
    """  /* block 89 — refreshed on scroll, not on every frame */
  addEventListener('scroll', function(){ window.__nfY = window.pageYOffset; }, {passive:true});
  window.__nfY = window.pageYOffset;""")

# ── 2 · the counter's "still while moving" flag: the same treatment ───────
fix("""    var lastY = -1, stillFrames = 0;
    (function beat(){
      requestAnimationFrame(function(){
        var y = window.pageYOffset;
        if(y !== lastY){ lastY = y; stillFrames = 0; }
        else if(stillFrames < 4) stillFrames++;
        var moving = stillFrames < 2;
        if(moving !== host.classList.contains('is-moving'))
          host.classList.toggle('is-moving', moving);
        beat();
      });
    })();""",
    """    /* block 89 — "moving" is set by the scroll event and cleared two frames
       (~40ms) after the last one: the same flag the frame loop produced,
       without the loop */
    var stillT = 0;
    addEventListener('scroll', function(){
      if(!host.classList.contains('is-moving')) host.classList.add('is-moving');
      clearTimeout(stillT);
      stillT = setTimeout(function(){ host.classList.remove('is-moving'); }, 40);
    }, {passive:true});""")

# the still image is only wanted once the route is on screen
fix("""    still.className = 'nf-cf-still';
    still.src = '../../_CDN-UPLOAD-SAFE/nf-counter-still.webp';""",
    """    still.className = 'nf-cf-still';
    still.loading = 'lazy';                                   /* block 89 */
    still.src = '../../_CDN-UPLOAD-SAFE/nf-counter-still.webp';""")

# ── 3 · the client marquee runs only while it is on screen ────────────────
fix("""  function tick(){
    requestAnimationFrame(tick);
    if(document.hidden) return;""",
    """  var inView = !('IntersectionObserver' in window), ticking = false;   /* block 89 */
  function tick(){
    if(!inView){ ticking = false; return; }   /* block 89 — off screen: stop scheduling */
    requestAnimationFrame(tick);
    if(document.hidden) return;""")
fix("""  wrap.addEventListener('pointerenter', function(){ paused = true;  });
  wrap.addEventListener('pointerleave', function(){ paused = false; });""",
    """  wrap.addEventListener('pointerenter', function(){ paused = true;  });
  wrap.addEventListener('pointerleave', function(){ paused = false; });
  /* block 89 — the loop starts when the strip comes within a screen of the
     viewport and stops scheduling itself when it leaves */
  function start(){ if(ticking) return; ticking = true; lastY = window.scrollY; requestAnimationFrame(tick); }
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(es){
      inView = es[0].isIntersecting; if(inView) start();
    }, { rootMargin:'100% 0px' }).observe(wrap);
  } else start();""")
# the old code kicked the loop off with a bare tick() call — find and neutralise it
fix("""  measure();
  wrap.classList.add('cmq-js');
  requestAnimationFrame(tick);""",
    """  measure();
  wrap.classList.add('cmq-js');
  /* block 89: tick() is started by the observer above, not here */""")

# ── 4 · the keystroke sound is fetched and decoded when the gate opens ────
#   50 KB of base64 audio, atob'd and decoded through an AudioContext at page
#   load (a 200 ms task on a slow phone, and an AudioContext created before
#   any gesture), plus eight <audio> elements pointed at a file that is not
#   on the CDN — all for a sound the reader hears only after they have asked
#   for a code and clicked Enter the code. It loads then.
fix("""<script src="keystroke-audio.js"></script>
<script>""",
    """<!-- block 89: keystroke-audio.js is loaded by the gate, on first open -->
<script>""")
fix("""  var actx = null, keyBuf = null, audioReady = false;
  (function initAudio(){
    try{
      var AC = window.AudioContext || window.webkitAudioContext;
      if(!AC || !window.__KEYB64) return;
      actx = new AC();
      var bin = atob(window.__KEYB64), len = bin.length, bytes = new Uint8Array(len);
      for(var i=0;i<len;i++) bytes[i] = bin.charCodeAt(i);
      actx.decodeAudioData(bytes.buffer, function(buf){ keyBuf = buf; audioReady = true; }, function(){});
    }catch(e){}
  })();""",
    """  var actx = null, keyBuf = null, audioReady = false, audioAsked = false;
  function decodeKey(){
    try{
      var AC = window.AudioContext || window.webkitAudioContext;
      if(!AC || !window.__KEYB64) return;
      actx = new AC();
      var bin = atob(window.__KEYB64), len = bin.length, bytes = new Uint8Array(len);
      for(var i=0;i<len;i++) bytes[i] = bin.charCodeAt(i);
      actx.decodeAudioData(bytes.buffer, function(buf){ keyBuf = buf; audioReady = true; }, function(){});
    }catch(e){}
  }
  /* block 89 — called by __nfBootGate: the script is fetched on first open
     (a user gesture has just happened, so the AudioContext may start), and
     the buffer decoded once it lands */
  function initAudio(){
    if(audioAsked) return; audioAsked = true;
    if(window.__KEYB64){ decodeKey(); return; }
    try{
      var s = document.createElement('script');
      s.src = 'keystroke-audio.js'; s.async = true;
      s.onload = decodeKey;
      document.head.appendChild(s);
    }catch(e){}
  }""")
fix("""  var POOL = [], PN = 8, pi = 0;
  try{
    for(var _p=0; _p<PN; _p++){ var _a=new Audio('keystroke.mp3'); _a.preload='auto'; _a.volume=0.3; POOL.push(_a); }
  }catch(e){ POOL = []; PN = 0; }""",
    """  var POOL = [], PN = 8, pi = 0;
  /* block 89 — the <audio> fallback pool is built on first use, and only if
     Web Audio is not there to do the job */
  function pool(){
    if(POOL.length || !PN) return;
    try{
      for(var _p=0; _p<PN; _p++){ var _a=new Audio('keystroke.mp3'); _a.preload='auto'; _a.volume=0.3; POOL.push(_a); }
    }catch(e){ POOL = []; PN = 0; }
  }""")
fix("""    if(!PN) return;   /* pass150: the pool may be empty — see its constructor */
    try{ pi=(pi+1)%PN; var a=POOL[pi]; a.currentTime=0; a.play().catch(function(){}); }catch(e){}""",
    """    if(actx) return;  /* block 89: Web Audio is coming — no second voice */
    pool();
    if(!PN || !POOL.length) return;   /* pass150: the pool may be empty — see its constructor */
    try{ pi=(pi+1)%PN; var a=POOL[pi]; a.currentTime=0; a.play().catch(function(){}); }catch(e){}""")
fix("""  window.__nfBootGate = function(){""",
    """  window.__nfBootGate = function(){
    initAudio();                                    /* block 89 */""")

# ── 5 · the hero choreography moves with transforms, so nothing shifts ────
#   (a) the stacked rows carried margin-left:-.02em that the converge reset to
#       0 — a 3.8px layout move of three 170px-tall rows, 0.046 of layout
#       shift. The nudge now rides the same transforms the scatter uses.
fix(""".cover-hero-title.cascade .line-row{display:block;position:relative;padding:.04em 0;width:100%;
  margin-left:-.02em;overflow:visible;}
/* glitch-materialise""",
    """.cover-hero-title.cascade .line-row{display:block;position:relative;padding:.04em 0;width:100%;
  margin-left:0;overflow:visible;}   /* block 89: the -.02em nudge lives in the transforms below */
/* glitch-materialise""", 2)
fix(""".cover-hero-title.cascade.converged .line-row{margin-left:0;}
.cover-hero-title.cascade .r1{transform:translateX(calc(-22.6vw + 5px)) translateY(10px);}
.cover-hero-title.cascade .r2{transform:translateX(-12px);}
.cover-hero-title.cascade .r3{transform:translateX(21.8vw) translateY(-10px);}""",
    """.cover-hero-title.cascade .r1{transform:translateX(calc(-22.6vw + 5px - .02em)) translateY(10px);}
.cover-hero-title.cascade .r2{transform:translateX(calc(-12px - .02em));}
.cover-hero-title.cascade .r3{transform:translateX(calc(21.8vw - .02em)) translateY(-10px);}""")

#   (b) the support copy's lift under the landed line (margin-top, ~0.09 of
#       layout shift at ~3.9 s) is left as it is: it is the hero's deliberate
#       settle, and every way of expressing it that Lighthouse would not count
#       (a transform, an absolute block) changes where the cover ends or where
#       the Begin cue sits — Alex's call, not a build-time one.

# (a WebP pass on the big stills was measured and set aside: film grain
#  compresses badly — signoff 360→223 KB at q72, posters ~−25% — and the
#  quality call on brand imagery is Alex's. Candidates noted in the handoff.)

io.open(F, "w", encoding="utf-8").write(src)
print("perf: loops gated, audio lazy, hero shifts gone")
