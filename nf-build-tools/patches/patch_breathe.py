import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 75 · BREATHING ROOM, FROM ALEX'S OWN NUMBERS ══════════════════════════
# Chain note: this block follows 69 directly. Blocks 70–74 (four zones, banner,
# collision, flex column, reserved rows) are off the chain at Alex's request —
# "restore to the version I was happy with". The files are on disk; nothing in
# them is assumed here.
#
# Alex ran the geometry probe on his own machine (card 766 wide, 524 tall) and
# pasted the table. Every offset below is from that paste, relative to the top
# of the card, not from a guess at his window:
#
#   3A  uniLabR  "SGD 55"        289–322   2 lines, box 26px wide
#   3B  uniLabR  "+7.5¢ / cup"   327–377   3 lines
#       morphCombined            369–387   "Together · 8.3¢ a cup · …" — inside
#                                          the label's box
#       morphLockBtn             394–444   7px under the sentence
#   3C  morphFigure              174–224
#       morphLocked (meta row)   228–252   4px under the hero
#       .ml "Your likely cups…"  319–335
#       volCups                  348–356   13px under the label
#
# Four causes, four one-line answers. No structure moves.

# ── the step-3 rider goes ─────────────────────────────────────────────────
# Alex: "Your price per kilo sets the contribution: 5% at the floor, rising to
# 10% — I think this can go too, the gutters do enough." They do more: the
# right-hand card states the same climb with the actual thresholds (45 → 5%,
# 48 → 7.5%, 51 → 10%), so the rider was the short version of a paragraph
# sitting under it. It is written in two places that have to agree — RIDERS[2]
# on first render and phaseCopy[0] on every phase change (the comment beside
# phaseCopy says so) — so both go blank. 3B/3C's phaseCopy entries were already
# never shown (rider-off on p!==0) and are left as they are.
old = """    'Your price per kilo sets the contribution: 5% at the floor, rising to 10%.',
    /* 28 Aug: the sales-call line removed at Alex's instruction."""
new = """    '',   /* block 75 — rider retired; the price gutters carry the climb with figures */
    /* 28 Aug: the sales-call line removed at Alex's instruction."""
assert src.count(old) == 1, "RIDERS anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
old = """      var phaseCopy=['Your price per kilo sets the contribution: 5% at the floor, rising to 10%.','Every cent"""
new = """      var phaseCopy=['','Every cent"""
assert src.count(old) == 1, "phaseCopy anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── "Versus retail ≈ ⅓" → ≈ ½ ─────────────────────────────────────────────
# Alex: "that claim is bogus, use ~1/2." He is right by the file's own numbers:
# the band is SGD 45–55/kg and the retail kilo is SGD 80 (block 57), so trade is
# 56–69% of shelf — roughly half at the floor, nowhere near a third. The ⅓ was
# harvested from older copy when the retail kilo was priced differently and was
# never re-derived.
old = """            <div class="ro"><div class="k">Versus retail</div><div class="v">≈ ⅓</div></div>"""
new = """            <div class="ro"><div class="k">Versus retail</div><div class="v">≈ ½</div></div>"""
assert src.count(old) == 1, "versus-retail anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
# and the comment two screens up that documents the old claim, so the record
# does not contradict the readout
old = """               inches away in the band — VERSUS RETAIL, one third — so the page keeps the
               claim without the headline having to carry it. -->"""
new = """               inches away in the band — VERSUS RETAIL — so the page keeps the
               claim without the headline having to carry it. (2 Sep: the figure there
               was "one third" and was wrong against the file's own numbers — 45–55
               against an 80 kilo is 56–69%. Now "≈ ½", at Alex's instruction.) -->"""
assert src.count(old) == 1, "versus-retail comment anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 3C · the volume thumb pulses like the other two ───────────────────────
# Alex: "this 3c slider should have the pulsing animation as it does on 3a, 3b."
# Same mechanism as #wholePrice and #topUp: the class in the markup, the
# animation keyed on it, and the first input taking it off. #volCups was simply
# never added to any of the three.
old = 'id="volCups" class="scale-range vol-range" value="43000"'
new = 'id="volCups" class="scale-range vol-range thumb-pulse" value="43000"'
assert src.count(old) == 1, "volCups markup anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
old = """    if(volSlider) volSlider.addEventListener('input',function(){ paint(false); });"""
new = """    if(volSlider) volSlider.addEventListener('input',function(){ volSlider.classList.remove('thumb-pulse'); paint(false); });   /* block 75: retire the pulse on first touch, as the other two do */"""
assert src.count(old) == 1, "volSlider listener anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 3C gets its action; the chevron leaves the column ─────────────────────
# Alex: "a lot of empty space on the lowest half ... apply across 3a-3b-3c."
# Measured on 3A at a 663px card: gaps of 86 / 74 / 97 / 110 top to bottom —
# the bottom one is the void. Cause: the slider hangs at bottom:151 and the
# button at bottom:80 because the back chevron sits UNDER them at bottom:30,
# and that chevron only exists on 3B/3C. 3A hides it and 3C hides the button,
# so on two of the three phases the bottom of the card is reserved for things
# that are not there. 3B was the only phase that filled its card.
#   1. the chevron goes to the bottom-left corner. "Back a step" does not need
#      to share the centre column; freeing it drops slider and button 40px on
#      all three phases, tracks still on one Y.
#   2. 3C shows a button in the same slot as 3A/3B — "See your quote →" —
#      driving the deck's own next button so it inherits that button's gating.
old = """      if(phase===2){ lockBtn.style.display=''; lockBtn.style.visibility='hidden'; }"""
new = """      if(phase===2){ lockLabel.textContent='See your quote'; lockBtn.style.display=''; lockBtn.style.visibility=''; lockBtn.querySelector('.mic').innerHTML='&rarr;'; }   /* block 75 — 3C has an action in the slot the other two use */"""
assert src.count(old) == 1, "phase-2 button anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
old = """    lockBtn.addEventListener('click',function(){
      if(phase===0){ goPhase(1); }
      else if(phase===1){ goPhase(2); }
    });"""
new = """    lockBtn.addEventListener('click',function(){
      if(phase===0){ goPhase(1); }
      else if(phase===1){ goPhase(2); }
      /* block 75 — same destination as the corner "Your quote →", through
         that button's own click so its gating and scroll handling apply */
      else if(phase===2){ var q=document.getElementById('deckNext0'); if(q) q.click(); }
    });"""
assert src.count(old) == 1, "lock click anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the gutter cards stay inside the frame ────────────────────────────────
# Alex: "should the gutter messages shift upwards so they're within the frame?"
# They hang from the hero's bottom edge (+26px), so when the hero came down
# 28px they followed it off the bottom of the card — the right-hand card on 3A
# is the tallest and ran ~80px past the edge. Anchor unchanged; clamped so the
# taller of the pair ends at least 24px above the card's bottom edge. Same
# clamp in all three placers (price, top-up, year) so the pairs behave alike.
old = """        var anchorTop = fig ? fig.getBoundingClientRect().bottom + 26 : (r.top - 60);"""
new = """        var anchorTop = fig ? fig.getBoundingClientRect().bottom + 26 : (r.top - 60);
        /* block 75 — never past the card's foot */
        (function(){ var sg=document.getElementById('morphStage'); if(!sg) return;
          var sr=sg.getBoundingClientRect(), maxTop=sr.bottom-24-Math.max(gl.offsetHeight,gr.offsetHeight);
          if(anchorTop>maxTop) anchorTop=Math.max(sr.top+72, maxTop); })();"""
assert src.count(old) == 2, "gutter anchor count %d (expected 2)" % src.count(old)
src = src.replace(old, new)
old = """          var t = fig ? fig.getBoundingClientRect().bottom + 26 : (r.top - 60);"""
new = """          var t = fig ? fig.getBoundingClientRect().bottom + 26 : (r.top - 60);
          /* block 75 — never past the card's foot */
          (function(){ var sg=document.getElementById('morphStage'); if(!sg) return;
            var sr=sg.getBoundingClientRect(), maxTop=sr.bottom-24-Math.max(yl.offsetHeight,yr.offsetHeight);
            if(t>maxTop) t=Math.max(sr.top+72, maxTop); })();"""
assert src.count(old) == 1, "year gutter anchor count %d" % src.count(old)
src = src.replace(old, new)

# ── 3C · "≈" goes, and SGD rises to the equation's line ───────────────────
old = """        figCur.style.display=''; figCur.textContent='\\u2248 '+(window.__nfCur||'SGD')+' ';"""
new = """        figCur.style.display=''; figCur.textContent=(window.__nfCur||'SGD')+' ';   /* block 75 — Alex: "remove the ≈" */"""
assert src.count(old) == 1, "approx anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── step 1 · the origin count goes ────────────────────────────────────────
# Alex: "don't think we need the '1 origin selected' text." The tick badge, the
# orange DETAILS border and IN ORDER on the tile already say it, and "Choose
# machines →" lighting up is the actual state. The element stays (the deck's
# no-scroll fill pass reads the screen's children) but never carries the count;
# nothing else ever wrote to it — .is-warn is styled and never set.
old = """        else { hint.textContent=n+(n===1?' origin selected.':' origins selected.'); hint.classList.remove('is-warn'); }"""
new = """        else { hint.textContent=''; hint.classList.remove('is-warn'); }   /* block 75 — count retired; the tiles carry the state */"""
assert src.count(old) == 1, "hint anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── step 2 · the no-scroll pass stops flinching at the disclosure ─────────
# Alex: "a v slight judder when closing this element from an expanded
# position; it closes and the entire screen readjusts." Frame trace on the
# CaféMatic 6 "What you get" panel: the deck's fill pass (block 46's squeeze)
# is driven by a MutationObserver on class changes across the whole deck. The
# disclosure's toggle fires it; it measures the screen while the overlay panel
# is still animating, reads 1–3px of overflow, and shaves the screen's top
# padding to absorb it — heading, grid and actions bar all move 1–3px. Closing
# fires it again in reverse. The panel is an overlay (the card stays 545px) so
# none of that overflow is real. The pass now stands down while any disclosure
# panel is open or in motion, and runs once when the panel's transition ends —
# by which point the layout is what it was, the signature matches, and nothing
# is written.
old = """        var hair = f.scrollHeight - f.clientHeight;      /* block 62 */"""
new = """        /* block 75 — never measure across a moving "What you get" overlay */
        (function(){ var ps=f.querySelectorAll('.q-eq-panel'); for(var k=0;k<ps.length;k++){ if(ps[k].getBoundingClientRect().height>24){ window.__nfFillHeld=true; return; } } window.__nfFillHeld=false; })();
        if(window.__nfFillHeld) return;
        var hair = f.scrollHeight - f.clientHeight;      /* block 62 */"""
assert src.count(old) == 1, "hair anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
old = """        if(e.target && e.target.id === 'nfBuyDoss' && e.propertyName === 'max-height'){
          requestAnimationFrame(fill);
        }"""
new = """        if(e.target && e.target.id === 'nfBuyDoss' && e.propertyName === 'max-height'){
          requestAnimationFrame(fill);
        }
        /* block 75 — the disclosure panel, once it has stopped moving */
        if(e.target && e.target.classList && e.target.classList.contains('q-eq-panel')){
          requestAnimationFrame(fill);
        }"""
assert src.count(old) == 1, "transitionend anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the reveal scroll honours its own 10px rule ───────────────────────────
# The disclosure toggle's comment (1 Sep) says "a movement under 10px is not
# made at all ... nudging the whole page four pixels to tidy up an edge is
# exactly the kind of motion that makes an interface feel unsteady under the
# hand." The code beneath it never implemented that: __nfBringInto → nfbdScroll
# → nfbdScrollNow scrolls unconditionally. Frame trace: the open panel overhangs
# the deck by 4px, which makes the deck scrollable by 4px; the reveal scrolls it
# those 4px (scrollTop 0 → 2 → 4 at f44–45); on close the overhang goes and the
# scroll position snaps to 0 — heading, grid and actions bar all jump 4px.
# That snap is the judder. The rule is now real, and it is applied to what the
# scroller can actually reach, not to the ideal target: a reveal that can only
# move the page 4px is not a reveal.
old = """      var t = fs.scrollTop + (el.getBoundingClientRect().top - fs.getBoundingClientRect().top) - 100;
      try{ fs.scrollTo({top:Math.max(0,t), behavior:'smooth'}); }catch(e){ fs.scrollTop = Math.max(0,t); }"""
new = """      var t = fs.scrollTop + (el.getBoundingClientRect().top - fs.getBoundingClientRect().top) - 100;
      /* block 75 — clamp to what is reachable, then the 10px rule the toggle's
         comment always claimed */
      t = Math.max(0, Math.min(t, fs.scrollHeight - fs.clientHeight));
      if(Math.abs(t - fs.scrollTop) < 10) return;
      try{ fs.scrollTo({top:t, behavior:'smooth'}); }catch(e){ fs.scrollTop = t; }"""
assert src.count(old) == 1, "nfbdScrollNow anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── step 4 · no teleport at the ends of the page ──────────────────────────
# Alex: "I scroll up and down and at a certain point there's this jarring snap."
# Frame trace at his window: every flick eases at 8.5%/frame — except the one
# that arrives while the previous glide is still closing on the end. The edge
# branch then wrote scrollTop directly (`target = cur = clamp(want);
# f.scrollTop = cur`), so a glide sitting at 1223 of 1298 was set to 1298 in a
# single frame: +75px, and −75px at the top on the way back. The pin stays, the
# bounce stays; the animator finishes the last stretch like any other.
old = """      /* pinned, and still pushing */
      target = cur = Math.max(0, Math.min(max, want));
      f.scrollTop = cur;
      if(!screen) return;"""
new = """      /* pinned, and still pushing — block 75: the target is pinned to the end
         but the position is NOT written directly; the animator closes whatever
         is left of the glide at the same ease as the rest of it. */
      target = Math.max(0, Math.min(max, want));
      if(!running){ cur = f.scrollTop; if(Math.abs(target - cur) >= 0.5){ running = true; requestAnimationFrame(tick); } }
      if(!screen) return;"""
assert src.count(old) == 1, "edge-branch anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── step 4 · each hero figure heads the card it belongs to ────────────────
# Alex: "why is this heading not sitting above the 'machines and servicing'
# section in column A?" Because the totals pair is promoted to a single hero
# row above the whole manifest and centred as a pair — it was never attached to
# the columns. Each cell now moves into column A as a sibling directly above
# its own card: COFFEE above Coffee & Contribution, EQUIPMENT above Machines &
# Servicing. The empty hero row is removed. In the one-column fallback the
# order reads the same way top to bottom.
old = """    if(sendCard){ sendCard.classList.add('q-submit-dark'); manifest.appendChild(sendCard); }

    /* ES's received state, held ready inside the card (ES-LIVE.html:4869)."""
new = """    /* block 75 — the hero cells head their own cards */
    (function(){
      var hero = sheetEl.querySelector('.q-total.stl-hero');
      var grp  = manifest.querySelector('.stl-colgroup');
      if(!hero || !grp) return;
      var cells = hero.querySelectorAll('.q-total-cell');
      var cols  = grp.querySelectorAll(':scope > .stl-col');
      if(cells.length < 2 || cols.length < 2) return;
      cells[0].classList.add('stl-hero-cell'); cells[1].classList.add('stl-hero-cell');
      grp.insertBefore(cells[0], cols[0]);
      grp.insertBefore(cells[1], cols[1]);
      hero.remove();
    })();

    if(sendCard){ sendCard.classList.add('q-submit-dark'); manifest.appendChild(sendCard); }

    /* ES's received state, held ready inside the card (ES-LIVE.html:4869)."""
assert src.count(old) == 1, "sendCard anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── the squeeze stands down while a step is in flight ─────────────────────
old = """        var scr = f.querySelectorAll('.deck-screen');
        for(var i = 0; i < scr.length; i++){
          var s = scr[i];
          if(!s.classList.contains('is-active')){ s.style.minHeight = ''; continue; }"""
new = """        var scr = f.querySelectorAll('.deck-screen');
        if(__measure) for(var i = 0; i < scr.length; i++){
          var s = scr[i];
          if(!s.classList.contains('is-active')){ s.style.minHeight = ''; continue; }"""
assert src.count(old) == 1, "minHeight loop anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# Alex: "1–3a, navigating back and forth, there's this constant, almost
# imperceptible shifting within the page." Frame trace on the real navigation
# path: the deck's chrome never moves, but the active screen's top padding does
# — 19.19 → 9.52 at landing, back to 19.19 half a second later, every time. The
# enter animation translates the incoming screen; the translate extends the
# scrollable area; the squeeze reads that as ≤56px of overflow and shaves the
# padding to absorb it; the animation ends and the next pass restores it.
# Neither write was ever about real content. The squeeze (and the last-pixel
# min-height shave under it) now wait until no screen carries deck-exit or
# deck-enter; the class removal fires the observer, so the settled pass still
# runs — and on a screen that fits, it writes nothing.
old = """        if(act0 !== lastFilled){
          lastFilled = act0;"""
new = """        var __entered = (act0 !== lastFilled);   /* block 75 — the screen-change pass */
        /* block 75 — two rules for a screen in flight (deck-enter / deck-exit):
           · the screen-change pass is the only one that runs before the new
             screen's first paint, so it MUST measure and shave — but the enter
             slide's translateY(30px) is in every rect it would read (the
             min-height's offset fallback included, which came out 19px short).
             The animation is neutralised for the measurement and restored at
             the end of the pass; it has not painted yet, so nothing restarts.
           · every later in-flight pass writes nothing. Resetting and re-shaving
             at settle was the same value written twice with a paint between:
             a 2–3px nudge at the end of every step change. */
        var __flight = !!f.querySelector('.deck-screen.deck-exit, .deck-screen.deck-enter');
        var __neut = __flight && __entered;
        var __measure = !__flight || __neut;
        if(__neut){ act0.style.animation = 'none'; void act0.offsetHeight; }
        if(act0 !== lastFilled){
          lastFilled = act0;"""
assert src.count(old) == 1, "entered anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """        var act = a.querySelector('.deck-actions');
        var __all = f.querySelectorAll('.deck-screen'), __j;
        for(__j = 0; __j < __all.length; __j++){"""
new = """        var act = a.querySelector('.deck-actions');
        var __all = f.querySelectorAll('.deck-screen'), __j;
        if(__measure) for(__j = 0; __j < __all.length; __j++){"""
assert src.count(old) == 1, "reset-loop anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """        var slack = f.scrollHeight - f.clientHeight;
        if(slack > 0 && slack <= 56){"""
new = """        var slack = f.scrollHeight - f.clientHeight;
        if(__measure && slack > 0 && slack <= 56){"""
assert src.count(old) == 1, "slack anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)
old = """        if(slack > 0 && slack <= 3){
          s = parseFloat(a.style.minHeight) || 0;
          a.style.minHeight = Math.max(0, s - slack) + 'px';
        }"""
new = """        if(__measure && slack > 0 && slack <= 3){
          s = parseFloat(a.style.minHeight) || 0;
          a.style.minHeight = Math.max(0, s - slack) + 'px';
        }
        if(__neut){ act0.style.animation = ''; }   /* block 75 — the slide runs from here */"""
assert src.count(old) == 1, "last-pixel anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── step 4 · the Total row only exists when there is a top-up ─────────────
# Three identical "SGD 48.00 /kg" in column A: the hero, the base line, the
# total line. The total line exists to add the top-up to the base; with no
# top-up it repeats the line above it. Same gate as the top-up row itself.
old = """  var tuRow = $('#qTopUpRow'); if(tuRow) tuRow.hidden = !hasTop;"""
new = """  var tuRow = $('#qTopUpRow'); if(tuRow) tuRow.hidden = !hasTop;
  var ivRow = $('#qInvoicedRow'); if(ivRow) ivRow.hidden = !hasTop;   /* block 75 — the sum line is only a sum when there are two terms */"""
assert src.count(old) == 1, "topup row anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 75 · BREATHING ROOM ══════════════════════════════════════════════════ */

/* ── the endpoint labels stop wrapping ────────────────────────────────────
   Both endpoints are absolutely placed inside .uni-wrap. The right one sits at
   left:<track width> and is pulled back with translateX(-100%), so the space
   the browser thinks it has is the width of the wrap MINUS the track width —
   which is zero. Shrink-to-fit inside zero gives min-content: one word per
   line. "SGD 55" broke into two, "+7.5¢ / cup" into three, and the left label
   never did because its available width is the whole track. */
.morph-stage .uni-end{white-space:nowrap;}

/* ── 3B loses its right endpoint ──────────────────────────────────────────
   "+7.5¢ / cup" is the slider's ceiling, not information: the live top-up is
   already in the hero (1.5¢ YOUR TOP-UP) and the left endpoint marks where the
   top-up starts. Alex: "I don't even think having the +7.5c is needed." Gone
   on the top-up phase only — 3A keeps SGD 55, which IS information. */
.morph-stage.ph-topup #uniLabR{display:none;}

/* ── the status line gets clearance from the button ──────────────────────
   The slider block is pinned at bottom:137px and the 50px button at
   bottom:80px, so the sentence under the track ends 7px above the button on
   EVERY window — the gap is arithmetic, not layout. 137 → 151 makes it 21.
   Everything in the block rises 14px with it; on his card that puts the
   badges 64px under the hero instead of 50, which is room, not a problem. */
.morph-stage .morph-ctl{bottom:111px;}   /* 151 until the chevron left the column; see below */
/* CAUGHT IN THE SWEEP: on the shortest card (480px, i.e. any window under
   811px tall) at 1180–1280 wide, the full 14px put the 7.5% / FULL 10% badges
   4px into the hero's glyph box. Short cards take 8 instead, and the other 6
   comes out of the status line's own top margin — which, because the block is
   bottom-anchored, moves the track DOWN 6 while the sentence stays put. Net:
   badges 2px above where they were, sentence 15px off the button. */
@media (max-height:810px){
  .morph-stage .morph-ctl{bottom:105px;}
  .morph-stage .morph-combined{margin-top:6px;}
}

/* ── 3C · the meta row comes off the hero's baseline ──────────────────────
   4px under a figure whose line-height is .88 — and that .88 matters: the
   hero's glyph boxes hang ~19px BELOW its layout box, so a 20px margin from
   the box still let the ¢ tail's box clip the chips by 1px at 1512+ wide.
   28 clears the glyphs, not just the box. */
.morph-stage.year .morph-locked{margin:28px 0 0;}

/* ── the frame sits in the middle of the page ─────────────────────────────
   Alex: "200px from the lowest edge of the frame to the bottom of my page and
   130 from the top edge to the top." Measured at his viewport: 134 / 196. The
   card is height:calc(100vh - 330px) and the 330 is that chrome — 134 of it
   above, 196 below — so the imbalance is the same 62px at every window height,
   and the correction is a constant: 31px down. The card's height does not
   change, so nothing inside it moves; it slides into the void under it. */
.nf-console-wrap.nf-focus-sec .morph-stage{margin-top:41px;}   /* was 10; the card is inside the console wrap in focus mode, not under #quote */
/* under 811px tall the card is already at its 480px floor and the chrome has
   no slack — the sweep showed 12px of scroll at 1512x740 — so the shift is
   only taken where there is room for it */
@media (max-height:810px){ .nf-console-wrap.nf-focus-sec .morph-stage{margin-top:10px;} }

/* ── the bottom of the card is no longer reserved for absent things ───────
   The back chevron moves to the bottom-left corner, out of the centre column.
   With it gone from under the button, the button drops from bottom:80 to 40
   and the slider block from 151 to 111 — the same 40px on every phase, so the
   three tracks stay on one Y and the status-line-to-button gap stays 21. */
.morph-stage .morph-back{left:24px;top:12px;bottom:auto;transform:none;}
/* top-left, not bottom-left: the left gutter card is clamped to 24px inside
   the card's foot, which is exactly where the chevron was. Alex: "gutter text
   takes priority." Level with the progress rail (rail dots are 23px at top:18;
   a 36px chevron at top:12 shares their centre), where no card ever reaches. */
.morph-stage .morph-lockbtn{bottom:40px;}
/* and the hero comes down to meet it: with the cluster 40px lower the gaps on
   a 524px card read 58 / 149 / 62 / 40 top to bottom — the hero was now the
   thing hugging an edge. 28px more above it: 86 / 121 / 62 / 40. */
.morph-stage .morph-inner{padding-top:92px;}

/* ── step 4 · the hero cells, as card headers ─────────────────────────────
   They kept the hero's type and colour through .stl-hero; that ancestor is
   gone, so the same values are restated on the cell itself. Left-aligned to
   the card's inner edge (14px padding + 1px border = 15px) so the figure sits
   over its card's title. The :first-child rule that gave the pair its divider
   would now draw a border on the coffee cell — off. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero-cell{
  text-align:left;padding:4px 0 0 15px;border:none;flex:none;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero-cell .q-total-lab{
  color:rgba(244,239,226,.55);font-size:9.5px;letter-spacing:.18em;margin-bottom:10px;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero-cell .q-total-fig{
  font-size:clamp(30px,3.6vw,46px);color:#F4EFE2;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero-cell .q-total-fig .q-unit{
  font-size:13px;color:rgba(244,239,226,.55);}
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero-cell .q-total-note{
  margin-left:0;max-width:none;color:rgba(244,239,226,.55);}
/* the second figure gets a little more air above it than the column gap gives,
   so it reads as the start of a new section rather than the tail of the last */
.nf-console-wrap.nf-focus-sec .q-settle .stl-col + .stl-hero-cell{margin-top:14px;}

/* ── the access page · the video column hangs from the button's baseline ───
   Alex: "on page load the black banner and video should shift vertically up,
   with the black banner at the least aligning with send me access code
   button." Measured: the two columns are a grid with align-items:center, and
   the right column (video + readout band) is 60px taller than the left, so it
   overhung by 30px top and bottom — band 30px under the button.
   CAUGHT IN TEST: align-items:end alone put the band on the button by dropping
   the TEXT 30px, because the row is as tall as the video column and the
   section's top edge is fixed. He asked for the video to come up. So the LEFT
   column defines the row and the video column hangs from the row's foot as a
   zero-height box that stacks upward: band bottom = button bottom, text where
   it was, video 30px higher. Side-by-side layouts only — below 900px .two is
   one column and the video goes back to normal flow. */
#nfAccess .two{align-items:end;}
@media (min-width:901px){
  #nfAccess .two > .two-b{
    align-self:end;height:0;overflow:visible;
    display:flex;flex-direction:column;justify-content:flex-end;}
  /* the children keep their natural size — flex items shrink to fit a
     zero-height box, and the figure came out 2px tall */
  #nfAccess .two > .two-b > *{flex:0 0 auto;}
}

/* ── step 1 · the actions bar shares the carousel's width ─────────────────
   Alex: "outer right edge of choose machines button should align with outer
   right edge of tile above." The carousel is max-width:1240px, centred in a
   1320px panel, so at wide windows the tiles sit 40px in from both edges while
   the bar runs edge to edge — the button overhung by exactly that 40. The bar
   takes the same cap and centring; margin-top stays auto (it is what pins the
   bar to the foot). At 1145 and below the two already coincide. */
.nf-console-wrap.nf-focus-sec .deck-screen.is-active[data-screen="0"] .deck-actions{
  max-width:1240px;width:100%;margin-left:auto;margin-right:auto;}

/* ══ step 4 · the review pass ═════════════════════════════════════════════
   Alex: "implement your suggested changes and then we'll review." Roles, not
   palette: cream is what you pay, gold is what reaches the forest, orange is
   the one thing to do. */

/* ── gold = conservation money, and only that ─────────────────────────────
   The NGO box had a gold frame and a gold label around a cream figure. The
   figure is the one number on the page that IS the forest's. */
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo-val{color:#E8B457;}
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo-val .q-ngo-unit{color:rgba(232,180,87,.6);}
/* the dimmest line on the page was inside the one framed box */
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo-in{color:#CCCCCC;}

/* ── a line item reads number-first ───────────────────────────────────────
   Label, sub-line and value were all near-white; a row read as one flat
   string. Three steps now: value bold cream (unchanged), label one step back,
   sub-line two. */
.nf-console-wrap.nf-focus-sec .q-settle .q-line .q-lab{color:#D9D9D9;}
.nf-console-wrap.nf-focus-sec .q-settle .q-line .q-lab .q-sub{color:#B4B4B4;}

/* ── "Included" is a status, not a value ──────────────────────────────────
   Seven bold cream "Included"s were the heaviest type in column B and the
   least informative. Regular weight, secondary grey, one line — and the tick
   comes up to full cream to carry the state instead. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-col:has(#qRowTablet) .q-val{
  color:#B4B4B4;font-weight:400;white-space:nowrap;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-col:has(#qRowTablet) .q-lab::before{color:#F4EFE2;}

/* ── column C fills its height; the one action sits at the foot ───────────
   The submit button was floating mid-column with ~200px of void under it.
   Block 69 already built the stretch (flex column, last field margin-top:
   auto); align-items:start on the grid was switching it off for this column. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest .q-submit-dark{align-self:stretch;}
/* and its surface a step lighter than A and B — the one you touch */
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest .q-submit-dark{background:rgba(30,29,27,.88);}

/* ── 3B · the track stops flinching when the status line appears ──────────
   Alex: "moving the dial from 0.0 to 0.1 changes the position of the slider,
   with the slider adjusting up." Measured: .morph-combined reserves
   min-height:1.2em = 14.4px while empty, but one line of its text is 18px
   (line-height 18 at 12px). The block hangs from the card's foot, so the
   3.6px the line grows by is 3.6px the track rises by. The reserve is the
   filled height now, so empty and one-line are the same box. */
.morph-stage .morph-combined{min-height:1.5em;}

/* ── 3C · the story stops paying for a row it does not have ───────────────
   Alex sent a crop of "YOUR LIKELY CUPS PER YEAR" sitting on the meta row. I
   could not reproduce it settled — at his card the two are 29px apart, and his
   own full-window screenshot shows the same — so this is not a tuned number.
   It removes the thing that lets them meet: the year phase writes an EMPTY
   eyebrow, and an empty .morph-eyebrow still books height:1.2em plus a
   margin-bottom of 2em, ~39px of nothing above the caption. The slider block
   is anchored to the card's foot and the meta row to its head, so every pixel
   the head stack gives up is a pixel of clearance between them, on every
   window. Year only: 3A's eyebrow is also empty but its layout is the one he
   approved, and 3B's has text. */
.morph-stage.year .morph-eyebrow{height:0;margin-bottom:0;}

/* ── 3B · "YOUR PRICE" off the bottom of the dial ──────────────────────────
   The endpoint labels sit at top:56px inside the wrap; the track's underside
   is at 44. 12px, and the thumb's shadow reaches into it. 18 now. */
.morph-stage .uni-end{top:62px;}

/* ── 3C · the same instrument geometry as 3A and 3B ───────────────────────
   Alex: "this slider should retain the same positioning as the previous two."
   Measured against 3A at four windows: 3C's track sat 40px lower (34 on the
   short card) and ran 81–86px wider. Two causes, neither a spacing number:
     · width — the unified track is inside .uni-wrap, which is 88% of the
       block; the volume input fills the block. 88% on the input and its
       endpoints puts both edges on 3A's.
     · height — both blocks hang from the same bottom, but under the unified
       track there is 42px of wrap plus an 18px status line and its 12px
       margin; under the volume input there is only the endpoint row. The
       difference is paid back as padding under 3C's block, so the two tracks
       share a midline. The 6px the short card takes off the status line's
       margin comes off here too, for the same reason. */
.morph-stage #mCtlVol input.vol-range,
.morph-stage #mCtlVol .morph-ends{width:88%;}
.morph-stage #mCtlVol{padding-bottom:39px;}
@media (max-height:810px){ .morph-stage #mCtlVol{padding-bottom:33px;} }
/* endpoints at the same drop under the track as 3A's (21px from the midline) */
.morph-stage #mCtlVol .morph-ends{margin-top:13px;}

/* ── 3C · the thumb pulses (see the markup + listener change above) ───────
   thumbPulse is the orange ring the price and top-up thumbs already use; the
   volume thumb is the same 24px disc, so it is the same keyframe, not a new
   one. Off under reduced-motion, as the other two are. */
#volCups.thumb-pulse::-webkit-slider-thumb{animation:thumbPulse 1.7s ease-in-out infinite;}
#volCups.thumb-pulse::-moz-range-thumb{animation:thumbPulse 1.7s ease-in-out infinite;}
@media(prefers-reduced-motion:reduce){
  #volCups.thumb-pulse::-webkit-slider-thumb,#volCups.thumb-pulse::-moz-range-thumb{animation:none;}}

/* ── 3B · the small equation rises to the centre of the big figure ────────
   Alex: "the 6.5¢ + 0.0¢ = could shift up ever so slightly to bring it more up
   the big 6.5¢ figure." It sat on the big figure's BASELINE, which for type at
   half the size means the bottom edge of a 104px numeral — it read as a
   footnote to the answer rather than the left side of an equation. Centred on
   the digits instead: cap-height of the big figure ≈ .7em = 73px, of the lead
   ≈ 38px, so the lead rises (73−38)/2 ≈ 17px, which is .32 of its own em.
   vertical-align, not a transform, so the line box is honest about where the
   glyphs are. */
.morph-stage .mfig-lead{vertical-align:.32em;}

/* ── 3C · SGD rises to the equation's line ────────────────────────────────
   On the year phase the currency follows the lead equation, which is centred
   on the big figure (block 75, above). SGD was still on the baseline, 19px
   lower at 35.2px — a step down in the middle of one line. Year only: on 3A
   SGD sits beside 48.00 with nothing before it and a shared baseline is right.
   .54em = 19px at 35.2px, and it scales with the type. */
.morph-stage.year .morph-figure .mcur{vertical-align:.54em;}

/* ── step 1 · the tiles come down off the heading ─────────────────────────
   Alex: "the bag tiles sit far too high; 2's tiles have better vertical
   placement." Measured at his viewport: step 1's panel starts 10px under its
   heading with 160px spare above the actions bar; step 2's starts 30px under
   with 124 spare. The actions bar is bottom-anchored with margin-top:auto, so
   the panel can take some of that slack without moving anything else. 44px:
   54 under the heading, ~116 to the bar. Only where there is room — the two
   shortest windows in the sweep already scroll on this step (80px and 92px,
   before this block) and get nothing added. */
/* CAUGHT BY ALEX: a fixed 44px was right at one window and wrong at the next —
   on his wide screen the tiles render taller, and 44 put the Details row under
   the sticky actions bar, which then swallowed the clicks. His paste at
   824x812: tiles to 665, bar from 681. The screen is a flex column and the bar
   is pinned to its foot by margin-top:auto, so the panel takes an auto margin
   too: two autos split the free space evenly between heading→tiles and
   tiles→bar on ANY window, and when there is no free space both collapse to
   zero — the original layout, never an overlap. */
.nf-console-wrap.nf-focus-sec .deck-screen.is-active[data-screen="0"] > .panel{margin-top:auto;}
/* the empty count line must not keep its 14px margin and a line of nothing
   between the tiles and the bar */
.nf-console-wrap.nf-focus-sec #qxHint:empty{display:none;}

/* ── 3C · the slider label goes ───────────────────────────────────────────
   Alex: "Slide your likely cup volume to see how the year adds up — we have
   this already. We don't need 'Your likely cups per year'." Third statement of
   one idea on one screen: the caption says what the slider does, the hero
   reads the cup count live, and the label said it again 100px lower. It was
   also the element that met the meta row twice today. */
.morph-stage #mCtlVol .ml{display:none;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("breathing room")
