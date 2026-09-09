import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ── 44 · THE PAGE BEHIND THE BUILDER WAS NEVER LOCKED ────────────────────
   Alex, twice: "i can force scroll down as far as i want." I spent the last
   two rounds measuring the DECK and reporting zero overflow, which was true
   and beside the point. Measured properly at his 1512x1250, with the builder
   open:

     document scrollHeight  5929
     viewport               1250
     SCROLLABLE BEHIND      4679px
     deck's own overflow    0

   The deck is position:fixed and covers the screen, so it does not move — but
   the document underneath it is four and a half thousand pixels tall and fully
   live. Nothing ever locked it. Wheel input happened to be caught by the deck's
   own handler, which is why this survived every wheel test I ran; everything
   else went straight past:

     · End / PageDown / Space / arrows   scrolled the document 4726px
     · the scrollbar                     present and draggable
     · a wheel over the ✕                #nfxClose is appended to <body>, not
                                         to the deck, so it missed the guard

   That is "as far as i want" — unbounded, because it is the page, not the
   panel. One line closes all of it. Chrome keeps scrollTop through an
   overflow:hidden, and the ✕ handler already returns the page to the top, so
   nothing needs saving and restoring. macOS overlay scrollbars take no width,
   so removing the bar shifts nothing. */
html.nf-focus-on,
html.nf-focus-on body{overflow:hidden;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

# ── the deck claims every wheel while it is up ────────────────────────────
old = """      var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
      if(!f || !f.contains(e.target)) return;
      if(e.ctrlKey || e.metaKey) return;                 /* zoom is the browser's */"""
new = """      var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
      if(!f) return;
      if(e.ctrlKey || e.metaKey) return;                 /* zoom is the browser's */
      /* 1 Sep — the deck owns EVERY wheel while it is up, not only the ones
         landing inside it. The ✕ is a child of <body>, so a wheel over it used
         to fall through to the page scroller behind the deck. With the document
         locked (block 44) there is nothing back there to move, but a delta that
         reaches the page scroller still moves its internal target and the page
         lurches on close. Swallowed here instead. */
      if(!f.contains(e.target)){ e.preventDefault(); return; }
      /* and the fill pass must have run before this gesture decides whether
         there is anything to scroll: it is armed on load and re-armed on a
         1.2s interval, leaving a window just after the deck opens where the
         screen still carries its calc() height and reports false overflow —
         the wheel would scroll a step that fits. Cheap, and only until the
         screen has been sized once. */
      var __as = f.querySelector('.deck-screen.is-active');
      if(__as && !__as.style.minHeight && window.__nfDeckFill) window.__nfDeckFill();"""
assert src.count(old) == 1, "wheel guard anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# expose fill() so the wheel handler can force it
old = """      addEventListener('resize', fill);
      var mo = new MutationObserver(function(){ requestAnimationFrame(fill); });"""
new = """      addEventListener('resize', fill);
      window.__nfDeckFill = fill;
      var mo = new MutationObserver(function(){ requestAnimationFrame(fill); });"""
assert src.count(old) == 1, "fill anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── AND fill() STOPS MANUFACTURING THE SCROLL IT EXISTS TO REMOVE ─────────
# Caught in test straight after the lock landed: fill() sized the screen to
# 1214px and the deck reported zero overflow, then eight wheel ticks pushed the
# same screen to 1259px and 45px of scroll appeared out of nothing.
#
# It was measuring its own tail. The screen's offset came from
# getBoundingClientRect().top, which is a VIEWPORT reading: scroll the deck 1px
# and the screen's top reads 1px higher, so fill() concludes it has 1px more
# room and grows the screen 1px — which creates 1px more scroll. A ratchet, and
# every wheel tick fed it. The elastic transform moved the same rect and fed it
# too.
#
# offsetTop is layout, not paint: unaffected by scroll position and unaffected
# by transforms. Walking it up to the scroller gives the screen's distance from
# the top of the CONTENT, which is what the sum was always supposed to be.
old = """          var off = s.getBoundingClientRect().top - f.getBoundingClientRect().top;"""
new = """          var off = 0, __n = s, __g = 0;
          while(__n && __n !== f && __g++ < 12){ off += __n.offsetTop; __n = __n.offsetParent; }
          if(__n !== f) off = s.getBoundingClientRect().top - f.getBoundingClientRect().top + f.scrollTop;"""
assert src.count(old) == 1, "fill offset anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the diagnostic stays, minus the guesswork ─────────────────────────────
old = """  window.__nfNestedScrollable = function(el){"""
new = """  /* Kept from the hunt: window.__nfWhyScroll() reports the deck's overflow AND
     the document's, so the next report of "it scrolls" names which of the two
     is moving instead of costing a round of measurement. */
  window.__nfWhyScroll = function(){
    var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
    if(!f) return 'deck not in focus mode';
    var s = f.querySelector('.deck-screen.is-active'), esc = [];
    var sb = s ? s.getBoundingClientRect().bottom : 0;
    if(s) s.querySelectorAll('*').forEach(function(e){
      var r = e.getBoundingClientRect();
      if(r.height && r.bottom > sb + 1) esc.push({
        el: (e.className || e.tagName) + '', past: Math.round(r.bottom - sb) });
    });
    esc.sort(function(a, b){ return b.past - a.past; });
    return { deckOverflowY: f.scrollHeight - f.clientHeight,
             deckOverflowX: f.scrollWidth - f.clientWidth,
             documentScrollable: document.scrollingElement.scrollHeight - innerHeight,
             htmlOverflow: getComputedStyle(document.documentElement).overflow,
             screenMinH: s ? (s.style.minHeight || '(unset - fill() never ran)') : null,
             viewport: innerWidth + 'x' + innerHeight,
             escapers: esc.slice(0, 6) };
  };

  window.__nfNestedScrollable = function(el){"""
assert src.count(old) == 1, "diag anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("document locked behind the deck")
