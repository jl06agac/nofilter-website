import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 73 · THE STAGE BECOMES A FLEX COLUMN ══════════════════════════════════
# Alex is right, and block 72 made it worse. Measured at 1024x640 on the build
# he is looking at:
#
#   3A  fig 220-297  figDeep 317   badge "7.5%" 306-325   track 330-336
#   3B  locked 231-252   fig 239-316  figDeep 336   track 330-336
#   3C  fig 305-368  figDeep 385   locked 371-392
#
# Three separate overlaps, one cause: .morph-ctl is position:absolute with
# bottom:137px, and .morph-lockbtn with bottom:80px. Those offsets were measured
# once, on a 480px card, and hard-coded. The card is
# height:clamp(480px,100vh-330px,860px), so on every other window the pinned
# block lands wherever it lands — and on a short one it lands ON the figure.
#
# Block 72 moved the meta row INTO that pinned block to stop it colliding. That
# made 3B and 3C worse, not better: the row inherited the pin, so instead of
# sitting under the figure it now sits ABOVE it (locked 231-252 against a figure
# starting at 239). My reasoning was wrong — I fixed the relationship between
# two elements and ignored that the anchor itself was arbitrary. Reverted below.
#
# The second reason nothing held: .morph-figure carries line-height:.88, so the
# glyph box is ~20px shorter than the glyphs. Every measurement the existing
# guard() made was 20px optimistic, which is why it reported "no collision"
# while the ¢ tail sat under a slider badge. figDeep vs fig above is that gap.
#
# So: no absolutes in the story column, one gap owning every vertical space, a
# line-height that contains its own type, and a guard that measures the column
# against the card instead of guessing at 34px of clearance.

# ── 1 · revert 72's DOM move: the row goes back into the flow ──────────────
old = """      /* block 72 — the meta row rides with the control it describes. The
         control is position:absolute against the stage, so a row left in the
         flow above it collides the moment the window is short. */
      (function(){
        var ctl = document.getElementById(phase===2 ? 'mCtlVol' : 'mCtlUni');
        if(ctl && lockedRow.parentNode !== ctl) ctl.insertBefore(lockedRow, ctl.firstChild);
      })();"""
new = """      /* block 73 — 72's move is reverted. The row belongs in the story
         column; it only collided because the control it was avoiding was
         pinned to the card's bottom edge. The control is in the flow now, so
         the row goes back where it reads: under the figure, above the
         instrument, its own row in the stack. */
      (function(){
        var inner = document.querySelector('#morphStage .morph-inner');
        if(inner && lockedRow.parentNode !== inner) inner.appendChild(lockedRow);
      })();"""
assert src.count(old) == 1, "72 move anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """.morph-stage .morph-ctl #morphLocked{
  order:-1;margin:0 0 24px;width:100%;}"""
new = """/* block 73: 72's order:-1 rule retired with the move that needed it. */"""
assert src.count(old) == 1, "72 order rule not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 2 · the 3C meta row loses the target chip ──────────────────────────────
# Alex: "Delete Target · 43,000 cups/yr — it is currently crashing directly into
# Top-up · none [EDIT]." It is also redundant: the figure two rows above it
# reads "43,000 CUPS x 6.5¢", so the chip restated the slider's own value.
old = """      if(phase>=2){
        var tgt=document.createElement('span'); tgt.className='mlchip mlchip--static';
        tgt.textContent='Target · '+fmt0(d.vol)+' cups/yr';
        lockedRow.appendChild(tgt);
      }"""
new = """      /* block 73 — the target chip is gone. The hero on this phase already
         reads "43,000 CUPS", and the chip was the third item on a row sized
         for two. Row is now: Price [edit] · Top-up [edit]. */"""
assert src.count(old) == 1, "target chip anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 3 · the hero's size stops being an inline style ───────────────────────
# The phase engine writes `figure.style.fontSize` on every phase change. An
# inline style beats every class, so .m-compact and .m-compact2 have been INERT
# on the hero for as long as that line has existed — the guard has been adding
# classes with nothing to change, which is the real reason the old compaction
# never rescued anything. The phase's size becomes a custom property; the
# compaction rungs scale it.
old = """      figure.style.fontSize = phase===2 ? 'clamp(38px,7vw,88px)' : 'clamp(44px,8.5vw,104px)';"""
new = """      /* block 73 — a property, not an inline font-size, so the compaction
         rungs can still act on it. See the note in guard(). */
      figure.style.fontSize = '';
      stage.style.setProperty('--mfig', phase===2 ? 'clamp(38px,7vw,88px)' : 'clamp(44px,8.5vw,104px)');
      /* set the floor synchronously, in the same tick as the phase's own
         writes, so the first painted frame is already inside the card */
      if(window.__nfMorphFloor) window.__nfMorphFloor();
      /* then two frames: one for the rest of this phase render, one for the
         layout it causes. Measuring inside the render fits a stale DOM. */
      if(window.requestAnimationFrame) requestAnimationFrame(function(){
        requestAnimationFrame(function(){ if(window.__nfMorphGuard) window.__nfMorphGuard(); });
      });"""
assert src.count(old) == 1, "figure font anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 4 · guard() measures the column, not a 34px guess ──────────────────────
old = """    function guard(){
      var vol=document.getElementById('mCtlVol');
      var ctl=(vol && getComputedStyle(vol).display!=='none') ? vol : document.getElementById('mCtlUni');
      if(!ctl || !document.getElementById('morphFigure')) return;
      stage.classList.remove('m-compact'); stage.classList.remove('m-compact2');
      if(storyBottom() + 34 > ctl.getBoundingClientRect().top){
        stage.classList.add('m-compact');
        if(storyBottom() + 34 > ctl.getBoundingClientRect().top) stage.classList.add('m-compact2');
      }
    }"""
new = """    var GSEQ = 0;
    var RUNGS = ['m-compact','m-compact2','m-compact3'];
    function LEVEL(){ var n=0; for(var i=0;i<RUNGS.length;i++) if(stage.classList.contains(RUNGS[i])) n=i+1; return n; }
    function SETLEVEL(n){ RUNGS.forEach(function(c,i){ stage.classList.toggle(c, i<n); }); }
    /* the card's height is known before anything is measured, so the first
       frame of a phase can start at a rung that is at worst too tight rather
       than at one that is visibly too loose. Tightening down from here is
       invisible; loosening up from nothing was the flash. */
    window.__nfMorphFloor = function(){
      var h = stage.clientHeight || 0;
      var floor = h < 520 ? 3 : (h < 640 ? 2 : (h < 720 ? 1 : 0));
      if(LEVEL() < floor) SETLEVEL(floor);
    };
    function guard(){
      /* block 73 — the old test was "is the story's bottom within 34px of the
         control's top", which asked whether two elements had met. With the
         control pinned to the card's bottom edge that question had no useful
         answer: the control's top was a constant, and shrinking the figure
         moved the story UP, away from a line that never moved.
         The column is a flex stack now, so the only question left is whether
         it fits the card. Two rungs: fonts, gaps and padding tighten together,
         because tightening one alone just moves the overflow somewhere else. */
      var inner=document.querySelector('#morphStage .morph-inner');
      if(!inner) return;
      /* CAUGHT IN TEST, twice.
         (a) comparing the column's scrollHeight to its OWN clientHeight is
             never greater — the inner is a flex item, so it grows with its
             content and spills out of the card instead of scrolling.
         (b) comparing it to the CARD's height still missed, because the column
             is justify-content:center: when it overflows it overflows in both
             directions, and content above the start edge is not counted in
             scrollHeight at all. At 1280x800 the hero was sitting 24px above
             the top of the card and the guard read "fits".
         So the rows are added up directly. Exact, and it cannot care which
         edge the overflow went out of. */
      function slack(){
        var cs=getComputedStyle(inner);
        var gap=parseFloat(cs.rowGap)||0, h=0, n=0;
        [].forEach.call(inner.children,function(e){
          var ecs=getComputedStyle(e);
          if(ecs.display==='none'||ecs.position==='absolute'||ecs.position==='fixed') return;
          var r=e.getBoundingClientRect(); if(r.height<1) return;
          h+=r.height; n++;
        });
        h += Math.max(0,n-1)*gap + parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
        return stage.clientHeight - h;   /* +ve = slack, -ve = overflow */
      }
      function over(){ return slack() < -1; }
      /* CAUGHT IN TEST: adding the rung and re-measuring in the same tick
         gave the PRE-compaction geometry back, so the ladder always fell
         through to the bottom rung — the price phase was running at 60% type
         with 100px of the card unused. One frame between rungs, and it settles
         on the loosest one that fits. */
      /* CAUGHT BY ALEX, and it is the flash he saw: the previous version
         cleared every rung, then stepped back up one frame at a time. So on
         every phase change the card rendered its FULL-SIZE layout for a frame
         or two before settling — hero across the progress rail, eyebrow
         escaping the top of the card onto the page heading — and then snapped
         into place. Correct final state, visibly broken on the way there.
         It never resets now. It starts from where the card already is and
         moves one rung at a time: tighten while it overflows, loosen while
         there is room, stop when neither. Nothing is ever rendered looser than
         what fits, so there is no frame to catch. */
      var my = ++GSEQ;
      var raf = window.requestAnimationFrame || function(f){ return setTimeout(f,16); };
      function settle(hops){
        if(my!==GSEQ || hops>6) return;   /* hop cap: a size that satisfies
                                             neither test cannot oscillate */
        var n = LEVEL();
        if(over()){
          if(n < RUNGS.length){ SETLEVEL(n+1); raf(function(){ settle(hops+1); }); }
          return;
        }
        /* only loosen on GENEROUS slack. A rung is worth 40-80px, so probing
           a looser one with 20px in hand renders an overflowing frame and puts
           it straight back — a one-frame graze on the progress rail, measured
           at 6px on the 1280x800 card. 90px means the looser rung will fit. */
        if(n > 0 && slack() > 90){
          SETLEVEL(n-1);
          raf(function(){
            if(my!==GSEQ) return;
            if(over()) SETLEVEL(n); else settle(hops+1);
          });
        }
      }
      settle(0);
    }
    /* block 73 — guard's only call site was the end of the instrument's paint
       routine, which runs BEFORE the phase engine writes the phase's classes,
       copy and hero size. So the card was always being fitted to the phase it
       had just left, and a phase change could leave a compaction rung on that
       nothing needed. Exposed so the phase engine can re-run it once it has
       finished writing, and re-run on resize, which nothing did at all. */
    window.__nfMorphGuard = guard;
    window.addEventListener('resize', function(){ try{ guard(); }catch(e){} });"""
assert src.count(old) == 1, "guard anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 73 · FOUR ROWS, ONE GAP, NO ABSOLUTE OFFSETS ═════════════════════════
   row 1  the hero equation
   row 2  the meta / edit summary
   row 3  the instrument, in a box of its own fixed height
   row 4  the lock button
   Spacing is owned by ONE property — the column's gap — so there is no second
   number anywhere that can disagree with it. Every ad-hoc margin on the rows
   below is zeroed for the same reason: a margin and a gap on the same seam is
   how the stack drifted in the first place. */
.morph-stage .morph-inner{
  --mgap:32px; --mpt:60px; --mpb:80px;
  /* a flex item's min-height defaults to auto, so the column would simply grow
     past the card rather than overflow it — and then nothing ever measures as
     too tall. Pinned to the card, so the guard has something to detect. */
  min-height:0;
  /* a hard stop. The column is centred, so anything that does not fit spills
     BOTH ways — and the top of this card is 130px under the page heading, so
     an overflowing hero lands on it. Clipping here is safe: the two side cards
     are position:fixed on document.body, not children of this box. */
  overflow:hidden;
  justify-content:center;
  gap:var(--mgap);
  padding-top:var(--mpt);
  padding-bottom:var(--mpb);   /* clears the back chevron, which stays pinned
                                  to the card foot — it is an affordance on the
                                  card edge, not a row of the story */
}
/* ── the three rungs ──────────────────────────────────────────────────────
   Two hard floors, and they are why there are three rungs rather than two:

     --mpt >= 52   the progress rail is pinned at top:18px and stands 23px, so
                   its bottom edge is 41px into the card. Anything less and the
                   hero starts inside the rail. This was 26px and the hero was
                   sitting ON 1 PRICE / 2 TOP-UP / 3 THE YEAR.
     --mpb >= 74   the back chevron is pinned 30px off the card foot and stands
                   36px. Anything less puts the lock button on it.

   That leaves ~350px of usable card at the 480px minimum, and the top-up phase
   needs six rows in it, so the last rung buys from the gap and the type rather
   than from padding it does not have. */
.morph-stage.m-compact  .morph-inner{--mgap:22px;--mpt:56px;--mpb:78px;}
.morph-stage.m-compact2 .morph-inner{--mgap:16px;--mpt:52px;--mpb:78px;}
.morph-stage.m-compact3 .morph-inner{--mgap:12px;--mpt:52px;--mpb:74px;}

.morph-stage.m-compact2 #uniWrap,.morph-stage.m-compact2 #volCups{
  margin-top:8px;margin-bottom:8px;}
.morph-stage.m-compact3 #uniWrap,.morph-stage.m-compact3 #volCups{
  margin-top:4px;margin-bottom:4px;}
.morph-stage.m-compact2 .morph-combined,
.morph-stage.m-compact3 .morph-combined{margin-top:6px;min-height:0;}
.morph-stage.m-compact2 #mCtlVol .morph-ends{margin-top:8px;}
.morph-stage.m-compact3 #mCtlVol .morph-ends{margin-top:4px;}
.morph-stage.m-compact2 .morph-lockbtn{padding-top:12px;padding-bottom:12px;}
.morph-stage.m-compact3 .morph-lockbtn{padding-top:10px;padding-bottom:10px;}
.morph-stage.m-compact3 .morph-sub{display:none;}

/* the year phase hides the lock button with visibility, which used to be free
   because the button was absolutely positioned. In the flow it still books its
   height and a gap — 60px of nothing on the phase with the least room. */
.morph-stage.year .morph-inner > .morph-lockbtn{display:none;}

/* ── the two pinned blocks join the flow ──────────────────────────────────
   137px and 80px from the card's bottom edge, measured once on a 480px card
   and applied to a card that is anywhere between 480 and 860. */
.morph-stage .morph-inner > .morph-ctl{
  position:static;bottom:auto;left:auto;right:auto;
  margin:0 auto;width:min(720px,88%);max-width:none;}
.morph-stage .morph-inner > .morph-lockbtn{
  position:static;bottom:auto;left:auto;transform:none;margin:0;}

/* ── rows do not collapse ─────────────────────────────────────────────────
   CAUGHT IN TEST, and it hid everything else: flex items shrink by default, so
   when the column overflowed the card, flexbox quietly crushed the rows that
   could give — the meta row went from 21px to its 1px min-height and the
   eyebrow to zero. Nothing looked overflowing because the overflow had been
   absorbed by squashing the content. Rows keep their height; overflow becomes
   visible, which is what the guard needs in order to see it. */
.morph-stage .morph-inner > *{flex:0 0 auto;}

/* ── flex order: every row stated, none left to the default ───────────────
   An unordered flex item is order:0, which would have put the control and the
   button ABOVE the figure (order:2) the moment they entered the flow. */
.morph-stage .morph-inner > .morph-eyebrow{order:0;}
.morph-stage .morph-inner > .morph-figure{order:2;}
.morph-stage .morph-inner > .morph-sub{order:3;}
.morph-stage .morph-inner > .morph-locked{order:4;}
.morph-stage .morph-inner > .morph-ctl{order:6;}
.morph-stage .morph-inner > .morph-lockbtn{order:7;}

/* ── the gap is the only spacer ───────────────────────────────────────────
   !important, deliberately, and this is the one place in the block that earns
   it. Nine rules across five earlier passes set margins on these six rows, and
   several are phase-scoped (.morph-stage.ph-topup .morph-cap, .morph-stage.year
   .morph-locked) so they outrank anything written without the phase class. The
   first version of this reset lost to them and the rendered gaps came out at
   20 / 26 / 36 / 44px against a stated 12 — which is exactly the disagreement
   the single-gap rule exists to end. Stated once, wins everywhere, and there
   is no second number left to drift. */
.morph-stage .morph-inner > .morph-eyebrow,
.morph-stage .morph-inner > .morph-cap,
.morph-stage .morph-inner > .morph-figure,
.morph-stage .morph-inner > .morph-sub,
.morph-stage .morph-inner > .morph-locked,
.morph-stage .morph-inner > .morph-lockbtn{
  margin-top:0 !important;margin-bottom:0 !important;}
.morph-stage .morph-inner > .morph-ctl{
  margin-top:0 !important;margin-bottom:0 !important;}
.morph-stage .uni-wrap{margin-top:0;margin-bottom:0;}
/* an empty row must not claim a gap: the price phase has no meta chips, and
   .morph-locked carries min-height:1px, so it booked 33px of nothing.
   ID selectors — block 70 states `.morph-stage #morphLocked{display:flex}`,
   which outranks any class-only rule here however far down the sheet it sits.
   Same trap that made the volume slider draw on all three phases. */
.morph-stage #morphLocked:empty{display:none;}
.morph-stage #morphEyebrow:empty{display:none;}
.morph-stage #morphCap:empty{display:none;}
.morph-stage .morph-cap:empty{display:none;}

/* ── row 1 contains its own type ──────────────────────────────────────────
   line-height:.88 on 104px display type puts the ¢ tail and the /kg descender
   roughly 20px below the element's own box. That is what the slider badges
   were landing on, and it is why every measurement taken from the figure's
   bounding rect — including the old guard's — read ~20px short. */
.morph-stage .morph-figure{
  line-height:1.02;padding-bottom:.18em;
  font-size:var(--mfig,clamp(44px,8.5vw,104px));}
.morph-stage.m-compact .morph-figure{font-size:calc(var(--mfig,clamp(44px,8.5vw,104px)) * .78);}
.morph-stage.m-compact2 .morph-figure{font-size:calc(var(--mfig,clamp(44px,8.5vw,104px)) * .62);}
.morph-stage.m-compact3 .morph-figure{font-size:calc(var(--mfig,clamp(44px,8.5vw,104px)) * .50);}
/* .18em is measured, not chosen: at 104px the deepest glyph in the equation
   (the ¢ tail) sat 18px below the element's own bottom edge. Now every
   measurement taken from this box — the guard's included — describes what is
   actually on screen. */

/* ── row 3 is a box of known height ───────────────────────────────────────
   .uni-wrap is 86px and every part of the instrument — badges at 14px, track
   at 38px, endpoints below — is absolutely placed INSIDE it. So the instrument
   already had its own container; it just had no fixed relationship to the row
   above. It does now. */
.morph-stage .uni-wrap{height:86px;}
/* the endpoints tuck 16px under the track (track bottom sits at 44px), not the
   12px they were at. Block 72 tried to do this with a margin, which an
   absolutely positioned element ignores. */
.morph-stage .uni-end{top:60px;}
/* :not(.hide) — CAUGHT IN TEST: `.morph-stage #mCtlVol{display:flex}` carries
   an ID and outranks `.morph-ctl.hide{display:none}`, so the volume slider
   drew on all three phases at once. */
.morph-stage #mCtlVol:not(.hide){display:flex;flex-direction:column;align-items:center;width:100%;}
.morph-stage #volCups{margin:16px 0;width:100%;}
.morph-stage #mCtlVol .morph-ends{margin-top:16px;width:100%;}

/* ── row 4 ────────────────────────────────────────────────────────────────
   the gap already gives it 32px; stated here so it survives a compaction rung
   that tightens everything else */
.morph-stage .morph-inner > .morph-lockbtn{margin-top:0;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("stage rebuilt as a flex column")
