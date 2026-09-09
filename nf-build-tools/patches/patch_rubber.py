import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 47 · THE BAND RESISTS, IT NEVER LATCHES ───────────────────────────────
# Two reports, one cause. Alex: "have we got some strange animation that holds
# a scroll in place for a split second at the extremity of the page? i can
# artificially, with quick scrolls keep the viewport in an extreme position.
# also why have you made my quote final screen unscrollable?"
#
# Both are this branch:
#
#     if(want < 0 || want > max){  ...elastic...  }
#
# It asks "does this gesture END past the edge", when the question is "were we
# ALREADY at the edge". On a step with a short range those are wildly different.
# The quote screen has ~300px of travel; one trackpad flick carries 300px or
# more in a single event. So the very first flick satisfied want > max, skipped
# the eased path entirely, snapped scrollTop to the end and rubber-banded. The
# screen never scrolled — it jumped and wobbled. That is the "unscrollable".
#
# And the return spring was a 110ms debounce, so it only fired once the wheel
# went quiet. Keep flicking and it is rescheduled forever: the band stays out
# at full stretch for as long as you keep scrolling. That is the "hold in an
# extreme position", and it is why the step heading in his screenshots is
# shoved up under the currency pills — a 44px displacement parked indefinitely,
# which reads as breakage rather than as physics.
#
# So: consume the available scroll FIRST and clamp into range, exactly as a
# real scroller does — a big flick now lands on the last pixel and stops. The
# band engages only on a gesture that pushes further while already pinned. And
# the overshoot decays every frame instead of waiting for silence, so sustained
# wheeling settles at a small equilibrium and letting go returns it in ~200ms.
# It cannot be parked, because nothing holds it out.

old = """      var want = (running ? target : cur) + d;

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
      if(!running){ running = true; requestAnimationFrame(tick); }"""

new = """      var pos  = running ? target : cur;
      var want = pos + d;

      /* Was there room in the direction of travel BEFORE this gesture? If so
         it is an ordinary scroll however far the flick reaches — clamped to the
         end, never handed to the band. */
      var edge = (max <= 0) ||
                 (d > 0 && pos >= max - 0.5) ||
                 (d < 0 && pos <= 0.5);

      e.preventDefault();

      if(!edge){
        ov = 0;
        target = Math.max(0, Math.min(max, want));
        if(!running){ running = true; requestAnimationFrame(tick); }
        return;
      }

      /* pinned, and still pushing */
      target = cur = Math.max(0, Math.min(max, want));
      f.scrollTop = cur;
      if(!screen) return;
      ov += d * 0.42;                              /* resistance on the way out */
      if(ov >  300) ov =  300;
      if(ov < -300) ov = -300;
      bounceEl = screen;
      if(!bouncing){ bouncing = true; requestAnimationFrame(bounceTick); }"""

assert src.count(old) == 1, "wheel branch anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the spring becomes a decay that runs whether or not the wheel stops ────
old = """    function spring(scr){
      clearTimeout(settle);
      settle = setTimeout(function(){
        ov = 0;
        if(!bounceEl) return;
        var el = bounceEl; bounceEl = null;
        el.style.transition = 'transform .5s cubic-bezier(.18,.9,.24,1.12)';
        el.style.transform = '';
        setTimeout(function(){ if(!bounceEl) el.style.transition = ''; }, 560);
      }, 110);
    }"""
new = """    /* One frame loop for the whole excursion. Every frame bleeds 14% off the
       overshoot and repaints, so the band is always on its way home even while
       the wheel is still turning — which is what makes it impossible to park at
       full stretch. New deltas push against that decay and reach a small steady
       state; stop pushing and it is back inside ~200ms.

       22px, down from 44. The excursion sits under the deck's own header, so a
       big one slides the step heading into the currency pills and reads as a
       broken layout rather than a bounce. A nudge is the whole point. */
    var bouncing = false;
    function bounceTick(){
      if(!bounceEl){ bouncing = false; return; }
      ov *= 0.86;
      if(Math.abs(ov) < 0.4){
        ov = 0;
        var el = bounceEl; bounceEl = null; bouncing = false;
        el.style.transition = 'transform .34s cubic-bezier(.18,.9,.24,1.12)';
        el.style.transform = '';
        setTimeout(function(){ if(!bounceEl) el.style.transition = ''; }, 360);
        return;
      }
      var mag = Math.min(22, Math.sqrt(Math.abs(ov)) * 1.9);
      bounceEl.style.transition = 'none';
      bounceEl.style.transform = 'translateY(' + (ov < 0 ? mag : -mag).toFixed(1) + 'px)';
      requestAnimationFrame(bounceTick);
    }"""
assert src.count(old) == 1, "spring anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("rubber band resists instead of latching")
