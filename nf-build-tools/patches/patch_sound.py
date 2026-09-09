import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 97 · THE BOARD HAS ITS SOUND BACK ═══════════════════════════════════════
# Alex, 3 Sep, on the native board: "yes bring both back" — the flap click and
# the tiger call at the milestone.
# What the iframe actually had: the click was synthesised (nf-counter-v2.html
# fetches click.wav, which was never on the CDN, and falls back to a 35ms
# filtered-noise burst); the call was assets/roar.mp3, also never on the CDN,
# and both sat behind a speaker toggle the embed CSS hid — so on the site the
# board was always silent. Now:
#   · a speaker pill in the tablet's corner, OFF by default (a page must not
#     start making noise on its own, and the browser would refuse anyway
#     until a tap); the tap that turns it on is the gesture that unlocks
#     audio. The choice is remembered per browser.
#   · the click: the same synthesis, rendered once into a buffer at switch-on
#     and played per landing flap with the iframe's ±0.2 rate jitter, 25ms
#     minimum gap and 8-voice cap. Nothing is fetched for it.
#   · the call: nf-board-call.mp3 (Clients/_shared/roar.mp3, the Danum Valley
#     long-call, re-encoded mono 96k → 85KB), fetched only when sound is
#     switched on, played through the iframe's 6s envelope (1.2s in, 1.6s
#     out, peak .45) when the milestone lands, and faded out early if the
#     reader routes away, scrolls off or hides the tab mid-call.
#   · both obey the board's own gate: no sound off-route, off-screen, or in
#     a background tab.

# ── the toggle, in the tablet's corner ──────────────────────────────────────
fix("""          <div class="nfb" id="nfBoard" role="img" aria-label="Split-flap board telling the story of a cup counted and held for the forest"></div>
        </div></div>""",
    """          <div class="nfb" id="nfBoard" role="img" aria-label="Split-flap board telling the story of a cup counted and held for the forest"></div>
          <!-- block 97 — the board's sound, off until asked for -->
          <button type="button" class="nfb-snd" id="nfBoardSound" aria-pressed="false" aria-label="Board sound: off. Tap to turn on">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path class="w" d="M16 9a4 4 0 0 1 0 6"/><path class="w" d="M18.5 6.5a8 8 0 0 1 0 11"/><path class="x" d="M17 9l5 6M22 9l-5 6"/></svg>
            <span class="nfb-snd-t">Sound off</span>
          </button>
        </div></div>""")

CSS = r'''
/* ══ 97 · THE BOARD'S SPEAKER ══════════════════════════════════════════════ */
.nw-screen .nfb-snd{position:absolute;right:10px;bottom:10px;z-index:3;display:inline-flex;align-items:center;gap:7px;
  margin:0;font-family:var(--mono,ui-monospace,monospace);font-size:9px;letter-spacing:.18em;text-transform:uppercase;
  color:rgba(244,242,238,.62);background:rgba(11,12,14,.72);border:1px solid rgba(255,255,255,.08);border-radius:99px;
  padding:6px 10px 6px 8px;cursor:pointer;line-height:1;-webkit-tap-highlight-color:transparent}
.nw-screen .nfb-snd svg{width:13px;height:13px;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;flex:none}
.nw-screen .nfb-snd .w{display:none}
.nw-screen .nfb-snd[aria-pressed="true"]{color:#F4F2EE;border-color:rgba(238,77,23,.55)}
.nw-screen .nfb-snd[aria-pressed="true"] .w{display:block}
.nw-screen .nfb-snd[aria-pressed="true"] .x{display:none}
.nw-screen .nfb-snd:hover{color:#F4F2EE}
.nw-screen .nfb-snd:focus-visible{outline:2px solid var(--signal,#EE4D17);outline-offset:2px}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

# ── the engine, inside the board's own closure ──────────────────────────────
# hooks into block 95: a click as each flap starts to fall, the call at the
# milestone, and the gate's ok() so sound follows the board's own rules.
fix("""      sp(c, '.ff').textContent = from; sp(c, '.fb').textContent = to;
      c.classList.add('is-flipping');""",
    """      sp(c, '.ff').textContent = from; sp(c, '.fb').textContent = to;
      c.classList.add('is-flipping'); snd.click();                     /* block 97 */""")

fix("""    await gate(); setCountDirect(50, ' TO FOREST'); await nap(900);
    await cascade(2);""",
    """    await gate(); setCountDirect(50, ' TO FOREST'); await nap(900);
    snd.call();                                                        /* block 97 */
    await cascade(2);""")

fix("""  /* the frame the still used to show, so the board is never blank on arrival */
  setDirect(toGrid(['', 'AND WHEN', 'YOU REACH', 'A MILESTONE', '']));""",
    r"""  /* ── block 97 · the sound ── */
  var snd = (function(){
    var btn = document.getElementById('nfBoardSound');
    var on = false, actx = null, clickBuf = null, voices = 0, lastClick = 0;
    var VOL = 0.55, RATE = 1.5, MIN_GAP = 25, MAX_VOICES = 8;
    var CALL_SRC = '../../_CDN-UPLOAD-SAFE/nf-board-call.mp3';
    var CALL_LEN = 6.0, CALL_PEAK = 0.45, FADE_IN = 1.2, FADE_OUT = 1.6;
    var callEl = null, callRAF = 0, callStop = 0;
    var KEY = 'nf-board-sound';
    function ctx(){
      if(!actx){ var AC = window.AudioContext || window.webkitAudioContext; if(!AC) return null; try{ actx = new AC(); }catch(e){ return null; } }
      if(actx.state === 'suspended'){ try{ actx.resume(); }catch(e){} }
      return actx;
    }
    /* the iframe's synthClick, rendered once: 35ms of noise with a sine
       edge, exponential decay, high-passed at the click frequency and
       low-passed at three times it */
    function render(){
      var c = ctx(); if(!c || clickBuf) return;
      var sr = c.sampleRate, dur = 0.035, n = Math.floor(sr * dur), freq = 3500 * RATE;
      try{
        var off = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(1, n, sr);
        var buf = off.createBuffer(1, n, sr), d = buf.getChannelData(0);
        for(var i = 0; i < n; i++){ var t = i / sr; d[i] = (Math.random() * 2 - 1 + Math.sin(2 * Math.PI * freq * 1.5 * t) * 0.3) * Math.exp(-t / 0.003); }
        var s = off.createBufferSource(); s.buffer = buf;
        var hp = off.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = freq; hp.Q.value = 1.5;
        var lp = off.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = Math.min(freq * 3, 12000); lp.Q.value = 0.7;
        var g = off.createGain(); g.gain.setValueAtTime(1, 0); g.gain.exponentialRampToValueAtTime(0.001, dur);
        s.connect(hp); hp.connect(lp); lp.connect(g); g.connect(off.destination); s.start(0);
        off.startRendering().then(function(b){ clickBuf = b; });
      }catch(e){}
    }
    function click(){
      if(!on || !clickBuf || !ok()) return;
      var now = performance.now();
      if(now - lastClick < MIN_GAP || voices >= MAX_VOICES) return;
      var c = ctx(); if(!c || c.state !== 'running') return;
      lastClick = now;
      try{
        var s = c.createBufferSource(); s.buffer = clickBuf;
        s.playbackRate.value = 1 + (Math.random() * 0.4 - 0.2) / RATE;
        var g = c.createGain(); g.gain.value = VOL;
        s.connect(g); g.connect(c.destination);
        voices++; s.onended = function(){ voices--; };
        s.start();
      }catch(e){}
    }
    function el(){
      if(callEl) return callEl;
      callEl = new Audio(CALL_SRC); callEl.preload = 'auto'; callEl.volume = 0;
      return callEl;
    }
    /* the iframe's envelope: silence → peak (ease in), hold, peak → silence
       (ease out); cut short with a quick fade if the board's gate closes */
    function envelope(a){
      if(callRAF) cancelAnimationFrame(callRAF);
      var t0 = performance.now(), cutAt = -1;
      function frame(now){
        var t = (now - t0) / 1000, v;
        if(!ok() && cutAt < 0) cutAt = t;
        if(cutAt >= 0){ var q = 1 - (t - cutAt) / 0.5; v = q <= 0 ? 0 : CALL_PEAK * q * q; }
        else if(t < FADE_IN){ var p = t / FADE_IN; v = CALL_PEAK * (p * p * (3 - 2 * p)); }
        else if(t > CALL_LEN - FADE_OUT){ var r = Math.max(0, (CALL_LEN - t) / FADE_OUT); v = CALL_PEAK * (r * r * (3 - 2 * r)); }
        else v = CALL_PEAK;
        try{ a.volume = Math.max(0, Math.min(1, v)); }catch(e){}
        if(t < CALL_LEN && v > 0) callRAF = requestAnimationFrame(frame);
        else { stopCall(); }
      }
      callRAF = requestAnimationFrame(frame);
    }
    function stopCall(){
      if(callRAF){ cancelAnimationFrame(callRAF); callRAF = 0; }
      if(callStop){ clearTimeout(callStop); callStop = 0; }
      if(callEl){ try{ callEl.pause(); callEl.currentTime = 0; callEl.volume = 0; }catch(e){} }
    }
    function call(){
      if(!on || !ok()) return;
      var a = el(); stopCall();
      function go(){
        try{
          a.currentTime = 0; a.volume = 0;
          var p = a.play(); if(p && p.then) p.then(function(){ envelope(a); }).catch(function(){});
          else envelope(a);
          callStop = setTimeout(stopCall, (CALL_LEN + 0.5) * 1000);
        }catch(e){}
      }
      if(a.readyState >= 1) go(); else { a.addEventListener('loadedmetadata', go, { once:true }); try{ a.load(); }catch(e){} }
    }
    function paint(){
      if(!btn) return;
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.setAttribute('aria-label', on ? 'Board sound: on. Tap to turn off' : 'Board sound: off. Tap to turn on');
      var t = btn.querySelector('.nfb-snd-t'); if(t) t.textContent = on ? 'Sound on' : 'Sound off';
    }
    function set(v, fromTap){
      on = !!v; paint();
      try{ localStorage.setItem(KEY, on ? '1' : '0'); }catch(e){}
      if(on){
        render();
        /* the tap that turned it on is the gesture that unlocks the call
           element: play and pause it silently once */
        if(fromTap){ var a = el(); try{ a.volume = 0; var p = a.play(); if(p && p.then) p.then(function(){ a.pause(); a.currentTime = 0; }).catch(function(){}); }catch(e){} }
      } else stopCall();
    }
    if(btn) btn.addEventListener('click', function(){ set(!on, true); });
    /* a remembered ON needs a gesture before the browser lets audio run:
       the first tap or key anywhere on the page primes it */
    var remembered = false;
    try{ remembered = localStorage.getItem(KEY) === '1'; }catch(e){}
    if(remembered){
      on = true; paint();
      var prime = function(){ render(); ctx(); };
      ['pointerdown', 'keydown'].forEach(function(ev){ addEventListener(ev, prime, { once:true, capture:true, passive:true }); });
    }
    document.addEventListener('visibilitychange', function(){ if(document.hidden) stopCall(); });
    return { click:click, call:call, set:set, isOn:function(){ return on; } };
  })();

  /* the frame the still used to show, so the board is never blank on arrival */
  setDirect(toGrid(['', 'AND WHEN', 'YOU REACH', 'A MILESTONE', '']));""")

fix("""  window.__nfBoard = { flipTo:flipTo, toGrid:toGrid, setDirect:setDirect, cells:cells };""",
    """  window.__nfBoard = { flipTo:flipTo, toGrid:toGrid, setDirect:setDirect, cells:cells, sound:snd };   /* block 97 */""")

io.open(F, "w", encoding="utf-8").write(src)
print("the board has its sound back")
