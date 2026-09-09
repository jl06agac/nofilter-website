import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

old = """  function nfbdScroll(el){"""
new = """  /* ── 1 Sep · THE EDGE ANSWERS THE HAND ──────────────────────────────────
     Alex: "both screens/viewports have sufficient space such that a scroll
     down or to the side should not allow for movement. i'd almost like it such
     that when a user does try to scroll they're met with the nice elastic feel
     as they realise they're already against the boundary."

     Exactly the macOS rubber-band, which Chrome does not provide: when an
     overflow:auto box has nothing to scroll, or is hard against an end, a
     wheel simply does nothing — the page feels dead rather than at rest.
     This shim supplies the physics. At a boundary (which includes the whole
     step fitting, when the deck is not scrollable at all) wheel input
     translates the active screen with square-root resistance, capped at 44px,
     and a spring returns it when the gesture ends. Trackpad momentum trains
     feed the same accumulator, so the bounce follows the finger rather than
     twitching per event.

     Guards: never during a morph flight (the proxy lives outside the screen,
     so a bouncing screen would shear under it — same family as the scroll
     hold above), and never while the purchase panel's own smooth scroll is
     running. The transform sits on the SCREEN, whose descendants are all
     in-flow; the morph is the wrap's child and is deliberately not moved. */
  /* ── AND THE WHEEL REACHES THE DECK AT ALL ──────────────────────────────
     Caught while testing the elastic: with the purchase panel open, no wheel
     anywhere scrolled the deck. The site's smooth-wheel interceptor
     (preventDefault + window scrolling) exempts targets inside a nested
     scrollable by walking UP AT MOST 12 ANCESTORS — and the panel's content
     sits deeper than that below the deck, so its wheels were captured and
     spent on the WINDOW, which the fixed deck ignores. Dead scroll. The
     interceptor reads window.__nfNestedScrollable first, precisely for this:
     anything inside the focus deck is the deck's to scroll, and page content
     keeps the original walk. */
  window.__nfNestedScrollable = function(el){
    if(el && el.closest && el.closest('.nf-console-wrap.nf-focus-sec')) return true;
    for(var n = 0; el && el !== document.body && n < 12; el = el.parentElement, n++){
      var cs = getComputedStyle(el), oy = cs.overflowY;
      if((oy === 'auto' || oy === 'scroll') && el.scrollHeight > el.clientHeight + 2) return true;
    }
    return false;
  };

  /* ── 1 Sep · THE DECK SCROLLS LIKE THE REST OF THE SITE ─────────────────
     Alex: "the treacly scroll that we have in the main site should definitely
     apply within the quote builder too, across all sections."

     The page has an eased wheel scroller — deltas accumulate into a target and
     a rAF loop closes the gap by EASE per frame (0.085), which is the treacle.
     The deck never had it: it is a position:fixed overflow:auto box, so the
     page scroller ignores it and the browser's raw wheel took over. Same
     constant, same shape, applied to the deck's own scrollTop so both surfaces
     feel identical.

     The elastic edge lives in the same handler because they are the same
     gesture: when the accumulated target would leave the scrollable range —
     including when there is nothing to scroll at all — the overshoot goes into
     a damped translate on the active screen instead, and springs back when the
     wheel stops. Square-root resistance, capped at 44px.

     One handler, non-passive, because both halves need preventDefault: the
     eased path must stop the browser scrolling underneath the loop, and the
     elastic path must stop the page scrolling behind the deck. */
  (function(){
    var EASE = 0.085;                        /* the page's own constant */
    var target = 0, cur = 0, running = false, tgtEl = null;
    var ov = 0, settle = null, bounceEl = null;

    function tick(){
      if(!tgtEl){ running = false; return; }
      cur += (target - cur) * EASE;
      if(Math.abs(target - cur) < 0.5){ cur = target; tgtEl.scrollTop = cur; running = false; return; }
      tgtEl.scrollTop = cur;
      requestAnimationFrame(tick);
    }

    function spring(scr){
      clearTimeout(settle);
      settle = setTimeout(function(){
        ov = 0;
        if(!bounceEl) return;
        var el = bounceEl; bounceEl = null;
        el.style.transition = 'transform .5s cubic-bezier(.18,.9,.24,1.12)';
        el.style.transform = '';
        setTimeout(function(){ if(!bounceEl) el.style.transition = ''; }, 560);
      }, 110);
    }

    addEventListener('wheel', function(e){
      var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
      if(!f || !f.contains(e.target)) return;
      if(e.ctrlKey || e.metaKey) return;                 /* zoom is the browser's */
      if(doss.classList.contains('is-morphing')){ e.preventDefault(); return; }
      var screen = f.querySelector('.deck-screen.is-active');
      var d = e.deltaY * (e.deltaMode === 1 ? 16 : (e.deltaMode === 2 ? f.clientHeight : 1));
      var max = Math.max(0, f.scrollHeight - f.clientHeight);

      /* resync before a new run — a programmatic smooth scroll (nfbdScroll) or
         a scrollbar drag may have moved us since the last gesture */
      if(!running || tgtEl !== f){ cur = f.scrollTop; tgtEl = f; }
      var want = (running ? target : cur) + d;

      if(want < 0 || want > max){
        /* past an end — or nowhere to go at all, when max is 0 */
        e.preventDefault();
        target = cur = Math.max(0, Math.min(max, want));
        f.scrollTop = cur;
        if(screen){
          ov += (want < 0) ? want : (want - max);
          var mag = Math.min(44, Math.sqrt(Math.abs(ov)) * 2.6);
          bounceEl = screen;
          screen.style.transition = 'none';
          screen.style.transform = 'translateY(' + (ov < 0 ? mag : -mag).toFixed(1) + 'px)';
          spring(f);
        }
        return;
      }

      e.preventDefault();
      ov = 0;
      target = want;
      if(!running){ running = true; requestAnimationFrame(tick); }
    }, {passive:false});

    /* ── AND THERE IS NOTHING TO SCROLL WHEN THE STEP FITS ─────────────────
       Alex: "there's unnecessary space below the buttons that we could remove
       so there's no space to scroll left right up or down."

       Measured: 91-101px of nothing under the forward button at every window
       height. The screen reserves calc(100vh - 92px), but its own top offset
       is only ~36px, so ~56px was being held at the foot for a gap that does
       not exist — and the 92 could never be right anyway, since the offset is
       a clamp that changes with the window.

       So the screen is told to fill exactly what is left below its own top,
       measured rather than assumed. It also settles the button alignment by
       construction: every screen now ends at the same line whatever its own
       padding does above. Recomputed on resize and whenever the active step
       changes; min-height only, so an open purchase panel still grows past it. */
    (function(){
      var fill = function(){
        var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
        if(!f) return;
        var scr = f.querySelectorAll('.deck-screen');
        for(var i = 0; i < scr.length; i++){
          var s = scr[i];
          if(!s.classList.contains('is-active')){ s.style.minHeight = ''; continue; }
          var off = s.getBoundingClientRect().top - f.getBoundingClientRect().top;
          /* floor, not round: the offset is fractional, and rounding UP left
             a stubborn 1px of scrollable overflow — enough for the browser to
             call the deck scrollable and skip the elastic entirely. */
          s.style.minHeight = Math.max(0, Math.floor(f.clientHeight - off)) + 'px';
        }
        /* one correction pass. Flooring the screen still left 1px of scrollable
           overflow, because the BEAT around it rounds up independently — and a
           single pixel is enough for the browser to call the deck scrollable
           and hand the wheel to it instead of the elastic. Measured after
           layout and given back, but only for a hair's worth: anything larger
           is real content and must stay scrollable. */
        var a = f.querySelector('.deck-screen.is-active');
        if(!a) return;
        var slack = f.scrollHeight - f.clientHeight;
        if(slack > 0 && slack <= 3){
          s = parseFloat(a.style.minHeight) || 0;
          a.style.minHeight = Math.max(0, s - slack) + 'px';
        }
      };
      addEventListener('resize', fill);
      var mo = new MutationObserver(function(){ requestAnimationFrame(fill); });
      var arm = function(){
        var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
        if(!f) return;
        mo.disconnect();
        mo.observe(f, {attributes:true, subtree:true, attributeFilter:['class']});
        fill();
      };
      addEventListener('load', arm);
      setInterval(arm, 1200);          /* the deck is built late and can rebuild */
    })();
  })();

  function nfbdScroll(el){"""

assert src.count(old) == 1, "anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* the deck never scrolls sideways, whatever a wide child tries */
.nf-console-wrap.nf-focus-sec{overflow-x:hidden;}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("elastic edge installed")
