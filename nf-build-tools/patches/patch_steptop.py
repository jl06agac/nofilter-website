import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 49 · A NEW STEP STARTS AT ITS OWN TOP ─────────────────────────────────
# The thing underneath "i cannot scroll this page at all". Reproduced:
#
#   panel screen, scrolled to the end   max/top = 692/692
#   advance to the quote screen         max = 442, scrollTop still pinned low
#   every wheel down                    nothing moves, 3.7px of wobble
#
# Nothing ever returned the deck to the top when the step changed. You arrive
# at a new step still holding the previous one's scroll offset — and if that
# offset is at or past the new step's end, every downward gesture is correctly
# refused as "already at the bottom" while the header still shows at the top of
# the window. It reads exactly like a dead page, and on the quote screen, which
# is the one step long enough to have a real scroll range, it is the difference
# between reading your quote and not.
#
# Block 48 stops a STALE target from causing this. This stops the state that
# feeds it: a step change puts the deck at that step's top and clears the
# animator, the same way every other route change in this file resets scroll.
#
# Scoped to a change of the active screen NODE, not to any class mutation — the
# purchase panel opening is a class change on the same screen, and its own
# nfbdScroll positioning must survive untouched.
old = """      var fill = function(){
        var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
        if(!f) return;"""
new = """      var lastFilled = null;
      var fill = function(){
        var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
        if(!f) return;
        var act0 = f.querySelector('.deck-screen.is-active');
        if(act0 !== lastFilled){
          lastFilled = act0;
          f.scrollTop = 0;
          running = false; target = 0; cur = 0; tgtEl = null;
          ov = 0; bounceEl = null; bouncing = false;
          if(act0) act0.style.transform = '';
        }"""
assert src.count(old) == 1, "fill head anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("each step starts at its own top")
