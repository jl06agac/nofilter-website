import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 48 · THE WHEEL SHIM CAN NEVER LEAVE THE DECK DEAD ─────────────────────
# Alex: "FFS, i cannot scroll this page at all!!!!" — on the quote screen,
# whose content plainly runs past the window in his screenshot.
#
# My harness scrolls that screen correctly, so the fault is in a state my
# harness does not reach, and the design is what let a state do this much
# damage: the handler calls preventDefault on EVERY wheel inside the deck and
# then decides what to do. Any misjudgement, and the gesture is not redirected,
# it is destroyed. That is a shim that can silently take scrolling away from a
# page that scrolls perfectly well without it. Three changes so it cannot:
#
# 1 · THE POSITION IS CLAMPED BEFORE THE EDGE TEST. `target` is a closure
#     variable shared by every screen. Leave a taller step mid-animation — the
#     purchase panel's 692px, say — and it survives into a screen with 297px of
#     travel, where it reads as "already past the end" and sends every
#     subsequent gesture to the rubber band. Down-scrolls bounce, nothing
#     moves, the page is dead. Clamping into the CURRENT range makes a stale
#     value harmless.
#
# 2 · A STEP CHANGE RESYNCS. Same defect at the root rather than the symptom:
#     when the active screen is not the one the last gesture was steering, the
#     animator's position is re-read from the DOM rather than carried over.
#
# 3 · AND THE WHOLE THING FAILS OPEN. Wrapped in try/catch, with preventDefault
#     moved as late as it can go, so a throw anywhere in here leaves the
#     gesture untouched and the browser scrolls the deck natively. Losing the
#     treacle is a blemish; losing the ability to read your own quote is not.

old = """    addEventListener('wheel', function(e){
      var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
      if(!f) return;
      if(e.ctrlKey || e.metaKey) return;                 /* zoom is the browser's */"""
new = """    var lastScreen = null;
    addEventListener('wheel', function(e){
     try{
      var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
      if(!f) return;
      if(e.ctrlKey || e.metaKey) return;                 /* zoom is the browser's */"""
assert src.count(old) == 1, "wheel head anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """      /* resync before a new run — a programmatic smooth scroll (nfbdScroll) or
         a scrollbar drag may have moved us since the last gesture */
      if(!running || tgtEl !== f){ cur = f.scrollTop; tgtEl = f; }
      var pos  = running ? target : cur;
      var want = pos + d;"""
new = """      /* resync before a new run — a programmatic smooth scroll (nfbdScroll), a
         scrollbar drag, or a STEP CHANGE may have moved us since the last
         gesture. The step change is the one that mattered: without it the
         animator kept steering by a target belonging to a different screen. */
      if(!running || tgtEl !== f || lastScreen !== screen){
        cur = f.scrollTop; target = cur; tgtEl = f; lastScreen = screen;
      }
      /* and clamp regardless, so no stale value can masquerade as "at the end"
         and divert every gesture into the band */
      var pos  = Math.max(0, Math.min(max, running ? target : cur));
      var want = pos + d;"""
assert src.count(old) == 1, "resync anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """      bounceEl = screen;
      if(!bouncing){ bouncing = true; requestAnimationFrame(bounceTick); }
    }, {passive:false});"""
new = """      bounceEl = screen;
      if(!bouncing){ bouncing = true; requestAnimationFrame(bounceTick); }
     }catch(err){
      /* fail OPEN. Nothing below here has called preventDefault, so the browser
         still has the gesture and scrolls the deck itself. Reset the animator
         so the next wheel starts from a clean state rather than re-throwing. */
      running = false; bouncing = false; bounceEl = null; tgtEl = null;
      if(window.console && console.warn) console.warn('[nf] wheel shim stood down:', err);
     }
    }, {passive:false});

    /* Run window.__nfWheelTrace() and then scroll: the next six wheel events
       report what the shim decided and why. If scrolling is dead this names the
       reason on the first tick. */
    window.__nfWheelTrace = function(){
      var n = 6;
      var h = function(e){
        var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
        if(!f) return;
        var sc = f.querySelector('.deck-screen.is-active');
        var mx = Math.max(0, f.scrollHeight - f.clientHeight);
        console.log('[nf wheel]', JSON.stringify({
          deltaY: Math.round(e.deltaY), max: mx, scrollTop: Math.round(f.scrollTop),
          running: running, target: Math.round(target), cur: Math.round(cur),
          step: sc ? sc.getAttribute('data-screen') : null,
          morphing: doss.classList.contains('is-morphing'),
          insideDeck: f.contains(e.target),
          transform: sc ? (sc.style.transform || 'none') : null }));
        if(--n <= 0) removeEventListener('wheel', h, true);
      };
      addEventListener('wheel', h, true);
      return 'tracing the next 6 wheel events — scroll now';
    };"""
assert src.count(old) == 1, "wheel tail anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("wheel shim fails open; stale target clamped")
