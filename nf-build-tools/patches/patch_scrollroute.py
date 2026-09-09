import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 119 · THE TREACLY SCROLL MUST LET GO ON A ROUTE CHANGE (7 Sep) ═══════════
# Alex: "if I'm on origins at a certain height and click Wholesale, the new
# page opens where I left the old one." Chrome and Safari alike. Reproduced
# with real wheel input: the damper's rAF loop is still easing toward its
# target for ~1 s after the last wheel tick; go() scrolls to 0, and the next
# frame of that loop writes the old position straight back (measured: click
# 300 ms after scrolling, land at 3,013 px instead of 110). Scripted scrolls
# never wake the loop, which is why every earlier check passed.
# Fix: each run of the loop carries a generation; a route change (the nf:route
# event go() already dispatches) bumps it, so any pending frame exits without
# writing, and target/cur re-baseline from wherever the router left the page.
fix("""  var EASE=0.085, target=window.scrollY||0, cur=target, running=false;""",
    """  var EASE=0.085, target=window.scrollY||0, cur=target, running=false, gen=0;   /* 119: gen */""")

fix("""  function tick(){
    cur+=(target-cur)*EASE;
    if(Math.abs(target-cur)<0.5){ cur=target; window.scrollTo(0,cur); running=false; return; }
    window.scrollTo(0,cur);
    requestAnimationFrame(tick);
  }""",
    """  function tick(g){
    if(g!==gen) return;                                       /* 119: a route change ended this run */
    cur+=(target-cur)*EASE;
    if(Math.abs(target-cur)<0.5){ cur=target; window.scrollTo(0,cur); running=false; return; }
    window.scrollTo(0,cur);
    requestAnimationFrame(function(){ tick(g); });
  }
  /* 119: go() has just put the page at the top; drop any run in flight and
     re-baseline, so the old position is never written back over the new route */
  document.addEventListener('nf:route', function(){
    gen++; running=false; target=cur=window.scrollY||0;
  });""")

fix("""    if(!running){ running=true; requestAnimationFrame(tick); }""",
    """    if(!running){ running=true; var g=gen; requestAnimationFrame(function(){ tick(g); }); }""")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_scrollroute OK")
