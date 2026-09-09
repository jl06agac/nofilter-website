import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 55 · THE PERIODIC HITCH IN THE DECK ───────────────────────────────────
# Alex: "we still have the judder/snap on this page on scrolling."
#
# Not the blur this time — nothing inside the quote screen computes a
# backdrop-filter any more (checked at runtime, the list comes back empty).
# It is fill(), which I wrote, and the way it is armed.
#
# fill() clears an inline padding on EVERY screen, writes a min-height, then
# reads f.scrollHeight — a write/read pair, which forces a synchronous layout
# of the whole deck. That is fine as a response to something changing. But it
# is also on `setInterval(arm, 1200)`, and arm() calls it unconditionally. So
# every 1.2 seconds, forever, the deck is re-laid-out from scratch whether or
# not anything moved — and if that lands inside a scroll, the frame is dropped.
# A hitch on a fixed cadence is exactly what "judder/snap" describes, and the
# frame trace agrees: median 17ms, but a p99 of 44.6ms with the long frames
# arriving about a second apart.
#
# Two changes, no behaviour lost:
#
# 1 · fill() takes a cheap signature first — the deck's client height, which
#     screen is active, and that screen's own height — and returns before
#     touching anything if it is unchanged. Every input the pass depends on is
#     in that signature, so a no-op call now costs three reads instead of a
#     full relayout.
#
# 2 · and it never runs mid-gesture. If the eased scroller is animating or the
#     band is out, the pass is deferred rather than performed under the reader's
#     hand — resize and step changes still land, just at the first still moment
#     after them.

old = """      var lastFilled = null;
      var fill = function(){
        var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
        if(!f) return;
        var act0 = f.querySelector('.deck-screen.is-active');"""
new = """      var lastFilled = null, lastSig = '', deferred = false;
      var fill = function(){
        var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
        if(!f) return;
        var act0 = f.querySelector('.deck-screen.is-active');

        /* ── block 55 · do nothing, cheaply, when nothing has changed ───────
           Three reads. Everything the pass depends on is in here, so an
           unchanged signature means the relayout below would reproduce exactly
           what is already on screen. A step change is caught by act0 being a
           different node, which also forces the reset underneath. */
        var sig = f.clientHeight + '|' + (act0 ? act0.offsetHeight : -1);
        if(act0 === lastFilled && sig === lastSig) return;

        /* ── and never under the reader's hand ─────────────────────────────
           A forced layout mid-scroll is a dropped frame. The pass is not
           urgent; the first still moment will do. */
        if(act0 === lastFilled && (running || bouncing)){
          if(!deferred){
            deferred = true;
            setTimeout(function(){ deferred = false; fill(); }, 220);
          }
          return;
        }
        lastSig = sig;"""
assert src.count(old) == 1, "fill head anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# the signature must be re-read AFTER the pass, since the pass itself changes
# the active screen's height — otherwise the next call sees a stale value and
# does the whole relayout again.
old = """        if(slack > 0 && slack <= 3){
          s = parseFloat(a.style.minHeight) || 0;
          a.style.minHeight = Math.max(0, s - slack) + 'px';
        }"""
new = """        if(slack > 0 && slack <= 3){
          s = parseFloat(a.style.minHeight) || 0;
          a.style.minHeight = Math.max(0, s - slack) + 'px';
        }
        /* restate the signature from the settled layout — the pass moved the
           very height it is measured by, so recording the pre-pass value would
           make every later call miss and relayout again (block 55) */
        lastSig = f.clientHeight + '|' + a.offsetHeight;"""
assert src.count(old) == 1, "correction tail anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# and arm() stops re-observing a deck that has not changed
old = """      var arm = function(){
        var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
        if(!f) return;
        mo.disconnect();
        mo.observe(f, {attributes:true, subtree:true, attributeFilter:['class']});
        fill();
      };"""
new = """      var armed = null;
      var arm = function(){
        var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
        if(!f) return;
        /* the observer only needs re-attaching when the deck node itself is
           replaced; disconnecting and re-observing the same node every 1.2s
           was pure cost (block 55) */
        if(f !== armed){
          armed = f;
          mo.disconnect();
          mo.observe(f, {attributes:true, subtree:true, attributeFilter:['class']});
        }
        fill();
      };"""
assert src.count(old) == 1, "arm anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── and a named frame trace, so the next report of judder arrives measured ──
old = """    window.__nfWheelTrace = function(){"""
new = """    /* Run window.__nfJudder() and then scroll for a few seconds. It reports the
       frame times it saw — median, p90, p99, the worst, and how many frames ran
       long — plus the scroll steps, so a stutter can be told apart from a snap. */
    window.__nfJudder = function(ms){
      ms = ms || 4000;
      var f = document.querySelector('.nf-console-wrap.nf-focus-sec');
      if(!f) return 'deck not in focus mode';
      var fr = [], tops = [], last = performance.now(), t0 = last, stop = false;
      (function s(){
        var n = performance.now();
        fr.push(n - last); last = n;
        tops.push(Math.round(f.scrollTop));
        if(n - t0 < ms && !stop) requestAnimationFrame(s); else report();
      })();
      function report(){
        var a = fr.slice(4).sort(function(x,y){ return x - y; });
        var q = function(p){ return +a[Math.floor(a.length * p)].toFixed(1); };
        var back = 0, i;
        for(i = 1; i < tops.length; i++) if(tops[i] < tops[i-1] - 1) back++;
        console.log('[nf judder]', JSON.stringify({
          frames: a.length, median: q(.5), p90: q(.9), p99: q(.99),
          worst: +a[a.length-1].toFixed(1),
          over32ms: a.filter(function(x){ return x > 32; }).length,
          over50ms: a.filter(function(x){ return x > 50; }).length,
          scrolled: Math.max.apply(null, tops) - Math.min.apply(null, tops),
          backwardsSteps: back,
          range: f.scrollHeight - f.clientHeight }));
      }
      return 'measuring for ' + (ms/1000) + 's — scroll now';
    };

    window.__nfWheelTrace = function(){"""
assert src.count(old) == 1, "trace anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("periodic relayout removed; frame trace exposed")
