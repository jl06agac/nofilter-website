import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the flight plays on a FROZEN page ─────────────────────────────────
subs.append((
"""    doss.classList.add('is-flying','is-morphing');
    doss.style.transition = 'none';
    doss.style.maxHeight = doss.scrollHeight + 'px';
    void doss.offsetWidth;
    var sheet = doss.querySelector('.nfbd-sheet');
    var l = (sheet || doss).getBoundingClientRect();
    var f = card.getBoundingClientRect();""",
"""    /* ── 1 Sep · THE PAGE IS FROZEN BEFORE THE FLIGHT IS MEASURED ──────────
       Alex, on the proxy crossing the card row a THIRD time, after two fixes
       that measured clean: "once again you haven't fixed this, look at the
       overlap. why are you constantly failing on this?"

       Because I kept measuring a still page, and his page was moving. The
       proxy is position:fixed: it is measured against the viewport once, here,
       and then flies between two viewport positions. If the deck is still
       smooth-scrolling from the PREVIOUS action — a disclosure settling, a
       closed panel returning to the row — the row slides up underneath a proxy
       whose coordinates were true when they were taken. Every overlap
       screenshot he sent shows exactly that: geometry from one scroll
       position, painted over another. And every one of my traces started from
       rest, which is why they all came back "34px clear".

       A smooth scroll cannot be cancelled directly, but issuing an INSTANT
       scroll to the current position ends it. So the deck is stopped dead
       before f and l are measured, and any queued scroll of ours is cleared
       with it. The flight then plays over a page that cannot move — see
       nfbdScroll's is-morphing hold for the other half. */
    if(window.__nfbdCancelScroll) window.__nfbdCancelScroll();
    var fsFreeze = document.querySelector('.nf-focus-sec');
    if(fsFreeze){ try{ fsFreeze.scrollTo({top: fsFreeze.scrollTop, behavior:'auto'}); }catch(e){ fsFreeze.scrollTop = fsFreeze.scrollTop; } }

    doss.classList.add('is-flying','is-morphing');
    doss.style.transition = 'none';
    doss.style.maxHeight = doss.scrollHeight + 'px';
    void doss.offsetWidth;
    var sheet = doss.querySelector('.nfbd-sheet');
    var l = (sheet || doss).getBoundingClientRect();
    var f = card.getBoundingClientRect();"""))

# ── 2 · and nothing of ours may scroll while a flight is up ───────────────
subs.append((
"""  var nfbdScrollT = null, nfbdScrollEl = null;
  function nfbdScroll(el){
    if(!el) return;
    nfbdScrollEl = el;
    clearTimeout(nfbdScrollT);
    nfbdScrollT = setTimeout(function(){
      var target = nfbdScrollEl; nfbdScrollEl = null;
      if(target) nfbdScrollNow(target);
    }, 90);
  }""",
"""  var nfbdScrollT = null, nfbdScrollEl = null;
  /* open_ calls this before it measures the flight, so a scroll queued by a
     previous gesture can never fire mid-flight with stale coordinates */
  window.__nfbdCancelScroll = function(){
    clearTimeout(nfbdScrollT); nfbdScrollT = null; nfbdScrollEl = null;
  };
  function nfbdScroll(el){
    if(!el) return;
    nfbdScrollEl = el;
    clearTimeout(nfbdScrollT);
    nfbdScrollT = setTimeout(function run(){
      /* HOLD while the proxy is in flight. The proxy is position:fixed, so a
         scroll under it repaints the row through a card whose coordinates were
         measured before the page moved — the overlap Alex photographed three
         times. The scroll is not dropped; it waits out the flight and then
         goes where it was going. */
      if(doss.classList.contains('is-morphing')){
        nfbdScrollT = setTimeout(run, 120);
        return;
      }
      var target = nfbdScrollEl; nfbdScrollEl = null; nfbdScrollT = null;
      if(target) nfbdScrollNow(target);
    }, 90);
  }"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

# ── 3 · scroll anchoring is OFF in the deck ───────────────────────────────
# Instrumented with a wheel mid-flight: the deck's scrollTop jumped 160 while
# the grid DID NOT MOVE on screen. That is Chromium's scroll anchoring —
# scrollTop silently adjusted so content stays visually still when layout
# changes (a max-height panel opening, a disclosure growing). Harmless on its
# own, but poison to anything that trusts scrollTop as a measure of visual
# movement: a compensator I briefly attached to the proxy converted one of
# those invisible adjustments into a real 160px shift and CREATED a 126px
# overlap in an otherwise clean flight. It was removed the same hour, and this
# is the note that keeps anyone from reattaching one.
# With anchoring off, scrollTop moves only when the view really moves, and the
# freeze + hold above cover every mover we own.
CSS = """
/* scroll anchoring off: this deck animates heights (the purchase panel, the
   what-you-get disclosure) and anchoring answers those with silent scrollTop
   adjustments that make every measurement lie. See the note in the morph. */
.nf-console-wrap.nf-focus-sec{overflow-anchor:none;}
"""
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

io.open(F, "w", encoding="utf-8").write(src)
print("page frozen for the flight; scrolls hold; anchoring off")
