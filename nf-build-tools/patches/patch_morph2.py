import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the card itself travels — the original stands down for the flight ──
subs.append((
"""    var expanded = false, finished = false;
    var landed = function(){
      if(finished) return; finished = true;
      mo.removeEventListener('transitionend', onEnd); clearTimeout(morphT);
      mo.style.display = 'none'; mo.style.opacity = '0'; mo.innerHTML = '';
      if(openK !== k) return;""",
"""    /* ── 1 Sep · THE CARD TRAVELS, NOT A COPY OF IT ────────────────────────
       Alex: "in the coffee page, i click on 'find out more' and the card itself
       in its entirety drops down. in our case a duplicate of the resting card
       drops down rather than the card itself. surely you can see that in
       examining code used for 'find out more'."

       I can, and he is right about the mechanism: openDossier hides its source
       the instant the proxy is placed —
           inlineCard.style.transition = 'opacity .1s ease';
           inlineCard.style.opacity = '0';
       — so there is only ever ONE card on screen and the illusion holds.

       I left that line out on 31 Aug for a reason that was also right at the
       time: the coffee version hides a TRANSIENT detail card that gets rebuilt,
       while this hides a permanent card in a comparison row, and my restore
       lived in one place behind a guard. Anything that interrupted the flight
       left a hole in the row. That was "the vanishing card".

       So the hide is back, and the restore is made impossible to strand:

       · unhideCards() clears the inline opacity on EVERY .q-eq-card, not the
         one it thinks it hid, so no bookkeeping can be wrong.
       · it runs on landing, on expand, at the top of every open, on close, and
         on an unconditional 1.4s timer armed at take-off. Five paths, none of
         which depends on the flight having gone as planned.
       · and the card comes back at EXPAND, not at landing — by then the proxy
         is a widening panel rather than a card, so the row is whole again
         before anyone looks back at it. The descent, which is the part Alex is
         actually describing, shows one card and one card only. */
    var unhideCards = function(){
      var all = document.querySelectorAll('.q-eq-card');
      for(var i = 0; i < all.length; i++){
        all[i].style.opacity = ''; all[i].style.transition = '';
      }
    };
    unhideCards();
    card.style.transition = 'opacity .1s ease';
    card.style.opacity = '0';
    var unhideT = setTimeout(unhideCards, 1400);   /* fires whatever happens */

    var expanded = false, finished = false;
    var landed = function(){
      if(finished) return; finished = true;
      mo.removeEventListener('transitionend', onEnd); clearTimeout(morphT);
      clearTimeout(unhideT); unhideCards();
      mo.style.display = 'none'; mo.style.opacity = '0'; mo.innerHTML = '';
      if(openK !== k) return;"""))

subs.append((
"""    var expand = function(){
      if(expanded) return; expanded = true;
      clone.style.opacity = '0';""",
"""    var expand = function(){
      if(expanded) return; expanded = true;
      /* the row is whole again the moment the proxy stops looking like a card */
      card.style.transition = 'opacity .28s ease';
      card.style.opacity = '1';
      setTimeout(unhideCards, 320);
      clone.style.opacity = '0';"""))

# and every other exit from the module clears it too
subs.append((
"""  function close_(){
    if(!openK) return;
    openK = null;""",
"""  function close_(){
    if(!openK) return;
    openK = null;
    /* belt and braces for the flight hide — see unhideCards in open_ */
    (function(){ var a = document.querySelectorAll('.q-eq-card');
      for(var i = 0; i < a.length; i++){ a[i].style.opacity = ''; a[i].style.transition = ''; } })();"""))

# ── 2 · opening "What you get" brings the panel into view ──────────────────
subs.append((
"""    if(t.hasAttribute('data-disc')){
      c.__open = !c.__open;
      if(c.__open) c.__seen = true;
      recalc();""",
"""    if(t.hasAttribute('data-disc')){
      c.__open = !c.__open;
      if(c.__open) c.__seen = true;
      recalc();
      /* ── 1 Sep · AND THE PANEL IT OPENS IS BROUGHT INTO VIEW ──────────────
         Alex: "for rental drop down 'what you get' collapsible panel, when a
         user opens it we are unable to see all without scrolling down, can the
         screen adjust downwards slightly?"
         It opens at the FOOT of a card that already fills most of the step, so
         on any normal window the rows it reveals are below the fold — the
         reader presses a control and, as far as they can tell, nothing happens.
         One frame later (the panel's height is not known until recalc has
         painted it) the scroller moves just enough to bring the card's foot
         clear, and no further: __nfBringInto refuses to scroll the head of the
         thing out of view to show its tail. */
      /* ── 1 Sep (2) · ONE ADJUSTMENT, ON THE TRANSITION, NOT ON A TIMER ────
         Alex: "the drop down screen adjust behaviour isnt good, it self adjusts
         down twice" — and, before that, "the drop down isn't easily interacted
         with/responsive."

         Those are the same bug seen from two sides, and the second is the one
         that matters. v1 measured on the next frame and again at 500ms, because
         the panel is a max-height disclosure whose height is not known until it
         has finished opening. Two measurements meant two scrolls: a visible
         double lurch, AND the page moving under the pointer after the click. A
         reader who reaches straight for the control again finds it somewhere
         else — which reads as an unresponsive control rather than as a moving
         page, because nothing appears to happen when they press.

         So it waits for the panel to actually finish, then moves once.
         transitionend on max-height is the real signal; the timer is only a
         fallback for a browser that swallows it or a reduced-motion setting
         where the transition never runs. Whichever arrives first wins, and the
         other is disarmed.

         And a movement under 10px is not made at all. The scroll exists to
         rescue a list that is off the bottom of the screen; nudging the whole
         page four pixels to tidy up an edge is exactly the kind of motion that
         makes an interface feel unsteady under the hand. */
      if(c.__open) (function(){
        var panel = c.querySelector('.q-eq-panel');
        var done = false;
        var go = function(){
          if(done) return; done = true;
          if(panel) panel.removeEventListener('transitionend', onT);
          clearTimeout(fb);
          if(c.__open && window.__nfBringInto){
            window.__nfBringInto(panel || c.querySelector('.q-eq-incl') || c, 10);
          }
        };
        var onT = function(e){ if(e.propertyName === 'max-height') go(); };
        if(panel) panel.addEventListener('transitionend', onT);
        var fb = setTimeout(go, 620);
      })();"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

# the shared reveal helper, defined next to nfbdReveal so both use one rule
old_h = """  function nfbdSync(){"""
new_h = """  /* the same "bring this into view without losing its head" rule the purchase
     panel uses, exposed so the card's own disclosure can share it. Scrolls the
     focus deck when there is one and the window otherwise. */
  window.__nfBringInto = function(el, minMove){
    if(!el) return;
    var fs   = document.querySelector('.nf-focus-sec');
    var bar  = document.querySelector('.deck-screen.is-active .deck-actions');
    var barH = (bar && getComputedStyle(bar).visibility !== 'hidden')
                 ? bar.getBoundingClientRect().height : 0;
    var r    = el.getBoundingClientRect();
    var vTop = fs ? fs.getBoundingClientRect().top : 0;
    var vH   = fs ? fs.getBoundingClientRect().height : window.innerHeight;
    var d    = r.bottom - (vTop + vH - barH - 14);
    var headroom = r.top - (vTop + 14);
    if(d > headroom) d = headroom;
    /* a movement too small to be worth making. Below this the scroll is not a
       rescue, it is a twitch — and a page that twitches under the pointer is
       what makes a control feel unresponsive. */
    if(d <= (minMove || 0)) return;
    if(fs){
      var t = fs.scrollTop + d;
      try{ fs.scrollTo({top:Math.max(0,t), behavior:'smooth'}); }catch(e){ fs.scrollTop = Math.max(0,t); }
    } else {
      try{ window.scrollBy({top:d, behavior:'smooth'}); }catch(e){ window.scrollBy(0,d); }
    }
  };

  function nfbdSync(){"""
assert src.count(old_h) == 1
src = src.replace(old_h, new_h)

CSS = r'''
/* ── 35 · THE BUILDER'S OWN EXIT, SMALLER ─────────────────────────────────
   Alex: "our x that exits the quote builder entirely is clashing with the
   black border, need to shrink the size of this x."
   44px of white disc at the same y as the panel's top-left corner reads as a
   control belonging to the panel rather than to the page. Smaller, quieter,
   and tucked further into the corner, so it stops competing with the sheet it
   is sitting next to. It is still a 34px target, above the 24px floor. */
.nfx-close{width:34px;height:34px;top:12px;right:14px;font-size:14px;
  background:rgba(255,255,255,.92);border-color:rgba(26,24,21,.14);}
.nfx-close:hover{background:#fff;border-color:rgba(26,24,21,.34);}

/* ── 36 · THE FOOT LINES UP ON THE FIGURE ─────────────────────────────────
   Alex: "Save & add to quote should be aligned with SGD 18,200.00."
   It was aligned to the BOTTOM of the price block, and that block carries a
   label above the figure and the per-unit row below it — so the button sat a
   row lower than the number it belongs to. Centring the row puts all three on
   the figure's own axis. */
#nfConsoleWrap .nfbd-buy{align-items:center;}

/* ── 39 · THE DISCLOSURE ANSWERS THE HAND ─────────────────────────────────
   Alex: "the drop down isn't easily interacted with/responsive. can you check."
   Checked: every click lands. Fourteen presses across the label, the middle,
   the chevron and both edges, plus four at 120ms apart — all fourteen toggled.
   The hit area is the whole 319x40 header, not just the chevron.

   So the fault is feedback, not hit-testing. This site replaces the system
   cursor with its own disc, so the pointer never changes shape over a control
   — and the only other signal was a hover tint at 5% ink, which is under the
   noise floor of a cream card. Nothing told the hand it had found a button,
   and the scroll that followed (see above) then moved the page out from under
   it. Firmer hover, a real press state, and the chevron's chip darkens with
   it — none of which depends on hue. */
#nfConsoleWrap .q-eq-disc{transition:background .12s ease,transform .1s ease;}
#nfConsoleWrap .q-eq-disc:hover{background:rgba(26,24,21,.085);}
#nfConsoleWrap .q-eq-disc:active{background:rgba(26,24,21,.15);transform:scale(.994);}
#nfConsoleWrap .q-eq-disc:hover .qd-ch{border-color:rgba(26,24,21,.8);}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("card travels + disclosure reveal + smaller exit + foot alignment")
