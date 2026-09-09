import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 95 · THE COUNTER BOARD, NATIVE ════════════════════════════════════════
# Alex, 3 Sep: "it would have been nice to have the video always scrolling
# without the judder … why does [the servicing tablet] react smoothly
# regardless of me scrolling or not" — and, given the choice, "build native".
# The servicing tablet is drawn by this page; the counter was a second web
# page (nf-counter-v2.html, a 116 KB Vestaboard-style app) in an iframe, and
# a live cross-origin document cannot be scrolled past smoothly in Chrome:
# measured on nofilter.sg, 27 of 297 frames over 32ms on a slow pass with
# the frame live (worst 164ms), 25 with the frame promoted to its own layer.
# The 27 Aug still-while-moving swap was the honest answer for an iframe.
# The board is now page elements: a 22×5 split-flap drawn with the page's
# own mono face, flaps that rotate with transforms only, and the same story
# the iframe told — beat for beat, colour for colour, timing for timing —
# ported from nf-counter-v2.html's NoFilter layer. What it does not do:
#   · flip while the page is moving. A flap that lands mid-scroll is a style
#     change on a composited layer, cheap, but a hundred of them are not, so
#     the story holds its frame until the page has been still for 400ms —
#     the same threshold the old swap used, but nothing is swapped: the
#     board simply stays put, which is what a split-flap does between words;
#   · anything off screen. It also holds while its route is not the live
#     one, while the board is out of the viewport, and while the tab is
#     hidden. The story picks up where it paused;
#   · sound. The iframe's click and the milestone call are not carried over
#     in this pass.
# The iframe, its still, its lead and the swap are gone from this beat; the
# nf-counter files stay on the CDN untouched for the pitch decks that embed
# them.

fix("""          <iframe class="nw-gis nw-cf" data-counter-src="../../_CDN-UPLOAD-SAFE/nf-counter-v2.html"
                  data-lead="1400px 0px" title="Live split-flap counter"
                  loading="lazy" scrolling="no" allow="autoplay"></iframe>""",
    """          <!-- block 95 — the board is drawn here, not embedded; see the script at the foot -->
          <div class="nfb" id="nfBoard" role="img" aria-label="Split-flap board telling the story of a cup counted and held for the forest"></div>""")

CSS = r'''
/* ══ 95 · THE NATIVE SPLIT-FLAP BOARD ═══════════════════════════════════ */
.nfb{position:absolute;inset:0;display:grid;place-items:center;background:#0f0f0f;
  container-type:inline-size;contain:layout style paint}
.nfb-grid{display:grid;grid-template-columns:repeat(22,1fr);gap:.62cqw;width:96%;padding:1.1cqw;box-sizing:border-box;
  background:#101010;border-radius:1cqw;box-shadow:inset 0 0 0 1px rgba(255,255,255,.04)}
.nfb-c{position:relative;aspect-ratio:1/2.05;font-family:var(--mono,ui-monospace,monospace);font-weight:400;
  font-size:3.3cqw;line-height:1;color:#F4F2EE;perspective:160cqw;--bg:#181818}
.nfb-c .h{position:absolute;left:0;right:0;height:50%;overflow:hidden;background:var(--bg);
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.05)}
.nfb-c .h span,.nfb-c .f span{position:absolute;left:0;right:0;height:200%;display:grid;place-items:center}
.nfb-c .t{top:0;border-radius:.6cqw .6cqw 0 0}
.nfb-c .t span,.nfb-c .ff span{top:0}
.nfb-c .b{bottom:0;border-radius:0 0 .6cqw .6cqw}
.nfb-c .b span,.nfb-c .fb span{bottom:0}
.nfb-c .b::before{content:"";position:absolute;left:0;right:0;top:0;height:1px;background:rgba(0,0,0,.55);z-index:1}
/* the falling flap: front = the old character's top half, back = the new one's bottom half */
.nfb-c .f{position:absolute;left:0;right:0;top:0;height:50%;transform-origin:50% 100%;transform-style:preserve-3d;display:none;z-index:2}
.nfb-c .f .ff,.nfb-c .f .fb{position:absolute;inset:0;overflow:hidden;background:var(--bg);backface-visibility:hidden;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.05)}
.nfb-c .f .ff{border-radius:.6cqw .6cqw 0 0}
.nfb-c .f .fb{transform:rotateX(180deg);border-radius:0 0 .6cqw .6cqw}
.nfb-c.is-flipping .f{display:block;animation:nfbFlip var(--dur,340ms) ease-in-out forwards;will-change:transform}
@keyframes nfbFlip{from{transform:rotateX(0)}to{transform:rotateX(-180deg)}}
.nfb-c.is-field{--bg:var(--field,#1A1815)}
@media (prefers-reduced-motion:reduce){.nfb-c.is-flipping .f{animation-duration:1ms}}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

JS = r'''<script>
/* ── block 95 · THE SPLIT-FLAP BOARD, IN THE PAGE ──────────────────────────
   The story, palette and timings are nf-counter-v2.html's NoFilter layer,
   ported line for line; the engine underneath is this page's own. */
(function(){
  var host = document.getElementById('nfBoard'); if(!host) return;
  var COLS = 22, ROWS = 5, N = COLS * ROWS;
  var PAL = { orange:'#ee4d17', green:'#16a34a', yellow:'#eab308', blue:'#2563eb', purple:'#9333ea', red:'#e02424', cream:'#F4F2EE', dark:'#1A1815' };
  var RAIN = [PAL.orange, PAL.yellow, PAL.green, PAL.blue, PAL.purple, PAL.red];
  var PER_CUP = 0.10;
  var DUR = 340, COL_STAGGER = 38, ROW_STAGGER = 22;
  var RM = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);

  /* ── the cells ── */
  var grid = document.createElement('div'); grid.className = 'nfb-grid';
  var cells = [], chars = [];
  for(var i = 0; i < N; i++){
    var c = document.createElement('div'); c.className = 'nfb-c';
    c.innerHTML = '<div class="h t"><span></span></div><div class="h b"><span></span></div>'
                + '<div class="f"><div class="ff"><span></span></div><div class="fb"><span></span></div></div>';
    grid.appendChild(c); cells.push(c); chars.push(' ');
  }
  host.appendChild(grid);
  function sp(c, sel){ return c.querySelector(sel + ' span'); }
  function setStatic(i, ch){ var c = cells[i]; sp(c, '.t').textContent = ch; sp(c, '.b').textContent = ch; }
  function flipCell(i, to, delay, done){
    var c = cells[i], from = chars[i]; chars[i] = to;
    setTimeout(function(){
      sp(c, '.t').textContent = to;  sp(c, '.b').textContent = from;
      sp(c, '.ff').textContent = from; sp(c, '.fb').textContent = to;
      c.classList.add('is-flipping');
      setTimeout(function(){ sp(c, '.b').textContent = to; c.classList.remove('is-flipping'); if(done) done(); }, (RM ? 1 : DUR) + 10);
    }, delay);
  }
  function center(s, w){ s = String(s).slice(0, w); var pad = w - s.length, l = Math.floor(pad / 2); return ' '.repeat(l) + s + ' '.repeat(w - l - s.length); }
  function toGrid(lines){ var g = []; for(var r = 0; r < ROWS; r++){ var ln = center(String(lines[r] || '').toUpperCase(), COLS); for(var k = 0; k < COLS; k++) g.push(ln[k]); } return g; }
  function setDirect(target){ for(var i = 0; i < N; i++){ chars[i] = target[i]; setStatic(i, target[i]); } }
  function flipTo(target){
    return new Promise(function(res){
      var last = 0, n = 0;
      for(var i = 0; i < N; i++){
        if(chars[i] === target[i]) continue;
        var col = i % COLS, row = Math.floor(i / COLS), delay = RM ? 0 : col * COL_STAGGER + row * ROW_STAGGER;
        n++; last = Math.max(last, delay + (RM ? 1 : DUR));
        flipCell(i, target[i], delay);
      }
      setTimeout(res, n ? last + 40 : 0);
    });
  }
  function clearField(){ for(var i = 0; i < N; i++){ cells[i].classList.remove('is-field'); cells[i].style.removeProperty('--field'); } }
  function paintBlank(col){ for(var i = 0; i < N; i++){ if(chars[i] === ' '){ cells[i].style.setProperty('--field', col); cells[i].classList.add('is-field'); } } }
  function paintCell(i, col){ chars[i] = ' '; setStatic(i, ' '); cells[i].style.setProperty('--field', col); cells[i].classList.add('is-field'); }
  function hardReset(){ clearField(); setDirect(toGrid(['', '', '', '', ''])); }
  function money(c){ return '$' + (c * PER_CUP).toFixed(2); }
  var nap = function(ms){ return new Promise(function(r){ setTimeout(r, ms); }); };

  /* ── when the board may move: live route, on screen, tab visible, page still ── */
  var inView = true, moving = false, movingT = 0;
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(es){ inView = !!(es[0] && es[0].isIntersecting); }, { threshold: 0.15 }).observe(host);
  }
  addEventListener('scroll', function(){
    moving = true; clearTimeout(movingT);
    movingT = setTimeout(function(){ moving = false; }, 400);
  }, { passive:true });
  function ok(){ return !document.hidden && inView && !moving && (window.__nfRoute === 'work' || !window.__nfRoute); }
  function gate(){ return new Promise(function(res){ (function poll(){ if(ok()) res(); else setTimeout(poll, 120); })(); }); }

  /* ── the scenes, as the iframe played them ── */
  async function show(lines, readMs){
    await gate(); hardReset();
    await flipTo(toGrid(lines)); await nap(readMs || 2000);
  }
  async function showOnField(lines, field, readMs){
    await gate(); hardReset();
    await flipTo(toGrid(lines)); paintBlank(field); await nap(readMs || 2400);
  }
  function setCountDirect(c, label2){
    hardReset();
    setDirect(toGrid(['NOFILTER', '', String(c) + ' CUPS', '', money(c) + (label2 || ' RAISED')]));
  }
  async function tickUp(a, b, label2){
    for(var c = a; c <= b; c++){ await gate(); setCountDirect(c, label2); await nap(c === b ? 1100 : 300); }
  }
  async function cascade(passes){
    for(var p = 0; p < passes; p++){ for(var col = 0; col < COLS; col++){
      await gate();
      for(var row = 0; row < ROWS; row++) paintCell(row * COLS + col, RAIN[(col + row + p) % RAIN.length]);
      await nap(32);
    } }
    await nap(300);
  }
  async function story(){
    await show(['', 'HELLO', ''], 2000);
    await show(['', 'I COUNT', 'EVERY CUP', 'OF COFFEE', ''], 2400);
    await show(['', 'SERVED ON', 'YOUR FLOOR', ''], 2200);
    await tickUp(0, 6, ' RAISED');
    await show(['', 'EVERY CUP', 'COUNTS', 'UPWARDS', ''], 2200);
    await showOnField(['', 'EACH CUP', 'GIVES', '10 CENTS', ''], PAL.dark, 2400);
    await showOnField(['', 'TO THE', 'FOREST', ''], PAL.green, 2200);
    await tickUp(40, 48, ' TO FOREST');
    await show(['', 'AND WHEN', 'YOU REACH', 'A MILESTONE', ''], 2600);
    await gate(); setCountDirect(50, ' TO FOREST'); await nap(900);
    await cascade(2);
    await gate(); setCountDirect(50, ' TO FOREST'); await nap(2200);
    await showOnField(['', 'THERE IS', 'A LINE', ''], PAL.dark, 2200);
    await showOnField(['', 'SOME PEOPLE', 'STILL', 'HOLD IT', ''], PAL.orange, 2600);
    await showOnField(['', 'YOUR COFFEE', 'IS HOW', 'WE MAKE IT', 'LAST'], PAL.green, 3000);
    await show(['', 'YOUR NAME', 'x', 'NOFILTER', ''], 2600);
    await showOnField(['', 'LETS HOLD', 'THE LINE', 'TOGETHER', ''], PAL.orange, 3000);
    await nap(1600);
    story();
  }
  /* the frame the still used to show, so the board is never blank on arrival */
  setDirect(toGrid(['', 'AND WHEN', 'YOU REACH', 'A MILESTONE', '']));
  setTimeout(story, 1400);
  window.__nfBoard = { flipTo:flipTo, toGrid:toGrid, setDirect:setDirect, cells:cells };
})();
</script>
'''
fix("""<!-- block 89: keystroke-audio.js is loaded by the gate, on first open -->""",
    JS + """<!-- block 89: keystroke-audio.js is loaded by the gate, on first open -->""")

io.open(F, "w", encoding="utf-8").write(src)
print("the counter board is native")
