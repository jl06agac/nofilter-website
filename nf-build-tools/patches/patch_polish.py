import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · THE MORPH IS VISIBLE AGAIN INSIDE THE FOCUS DECK ──────────────────
subs.append((
"""    if(!morph){
      morph = document.createElement('div');
      morph.className = 'nfbd-morph';     /* parked on <body>, so UNSCOPED — see block 23 */
      document.body.appendChild(morph);""",
"""    /* ── 1 Sep · THE DESCENT WAS HAPPENING BEHIND THE DECK ─────────────────
       Alex: "why has the animation changed now coming in the side rather than
       emulating the movement we have in the coffee selector where it drops
       down and then expands?"

       It never stopped dropping — I traced it frame by frame and the proxy
       does exactly that: 209px to 745px over .38s, then left/width from a
       321px card to the full 1320px. It was simply INVISIBLE. Two reasons,
       both from parking it on <body>:

       · z-index 900, under a focus deck that is position:fixed at z-index 1400
         with an opaque #F6F2E9 background. The whole descent played out behind
         a solid sheet of paper.
       · and the clone is a copy of a .q-eq-card, whose every rule is scoped to
         #nfConsoleWrap. On <body> not one of them matched, so even above the
         deck it would have descended as unstyled markup.

       The coffee dossier gets away with the same technique because it is not
       inside a focus deck. So the proxy now lives INSIDE #nfConsoleWrap while
       the deck is up: the scoped rules match the clone again, and a local
       z-index puts it over the deck's own content. position:fixed still
       resolves against the viewport — the deck is fixed and carries no
       transform, so nothing changes about the coordinates the FLIP measured.

       What Alex was actually watching was the tail: the panel arriving from
       below on nfbdReveal's scroll, which is the only part that was ever on
       screen. It reads as "coming in the side" because it is the expand, seen
       without the drop that explains it. */
    var host = document.querySelector('.nf-console-wrap.nf-focus-sec') || document.body;
    if(!morph){
      morph = document.createElement('div');
      morph.className = 'nfbd-morph';     /* deliberately UNSCOPED — see block 23 */
    }
    if(morph.parentNode !== host) host.appendChild(morph);
    return morph;
  }
  function __ensureMorphOld(){
    if(!morph){
      morph = document.createElement('div');
      morph.className = 'nfbd-morph';
      document.body.appendChild(morph);"""))

# ── 2 · the re-pin must not fire mid-flight ───────────────────────────────
subs.append((
"""      if(!sheetRO) sheetRO = new ResizeObserver(function(){
        if(openK) nfbdSync();
      });""",
"""      if(!sheetRO) sheetRO = new ResizeObserver(function(){
        /* NOT while the panel is in flight. The morph sets max-height by hand
           with transition:none and then hands over; a re-pin landing in the
           middle of that would reset the transition it is riding on. The
           observer fires once on attach, which is exactly mid-flight, so this
           guard is load-bearing rather than defensive. */
        if(openK && !doss.classList.contains('is-morphing')) nfbdSync();
      });"""))

# ── 3 · the quantity stepper moves to Step 3 ──────────────────────────────
subs.append((
"""          '<div class="nfbd-qrow"><div class="nfbd-qty">' +
              '<button type="button" data-nfbd-q="-1" aria-label="' +
                (q <= 1 ? 'Remove ' + m.name + ' from the quote' : 'One fewer ' + m.name) + '">&minus;</button>' +
              '<b>' + q + '</b>' +
              '<button type="button" data-nfbd-q="1" aria-label="One more ' + m.name + '">+</button>' +
            '</div><span class="nfbd-qnote">' +
            (q === 1 ? '1 machine' : q + ' machines, configured the same') + '</span>' +
            /* an explicit way out, because a stepper that reaches zero is not
               discoverable — you have to press minus and hope. This says it. */
            '<button type="button" class="nfbd-remove" data-nfbd-remove>Remove from quote</button>' +
            '</div>' +""",
"""          /* ── 1 Sep · THE STEPPER MOVED TO STEP 3 ──────────────────────────
             Alex: "The - 1 + 1 MACHINE control is still occupying prime space
             at the top right above Step 1. Shifting quantity selection down to
             Step 3 (Review & Confirm) right beside the SGD 9,100.00 total will
             clean up the top bar and make the step hierarchy start cleanly."
             Right on both counts, and there is a second reason: quantity is the
             one control that multiplies the total rather than changing what is
             in it, so it belongs where the total is and not above the first
             decision. See the .nfbd-qrow now built inside .nfbd-buy. */"""))

subs.append((
"""          '<div class="nfbd-buy">' +
            '<div class="nfbd-price"><small>Total purchase price</small>' +
              '<b>' + CUR() + money(tot) + '</b>' +
              (q > 1 ? '<p class="nfbd-per">' + q + ' &times; ' + CUR() + money(unit) + ' each</p>' : '') +
            '</div>' +""",
"""          '<div class="nfbd-buy">' +
            '<div class="nfbd-price"><small>Total purchase price</small>' +
              '<b>' + CUR() + money(tot) + '</b>' +
              (q > 1 ? '<p class="nfbd-per">' + q + ' &times; ' + CUR() + money(unit) + ' each</p>' : '') +
            '</div>' +
            '<div class="nfbd-qrow"><div class="nfbd-qty">' +
                '<button type="button" data-nfbd-q="-1" aria-label="' +
                  (q <= 1 ? 'Remove ' + m.name + ' from the quote' : 'One fewer ' + m.name) + '">&minus;</button>' +
                '<b>' + q + '</b>' +
                '<button type="button" data-nfbd-q="1" aria-label="One more ' + m.name + '">+</button>' +
              '</div><span class="nfbd-qnote">' +
              (q === 1 ? '1 machine' : q + ' machines, same spec') + '</span>' +
              /* an explicit way out, because a stepper that reaches zero is not
                 discoverable — you have to press minus and hope. This says it. */
              '<button type="button" class="nfbd-remove" data-nfbd-remove>Remove from quote</button>' +
              '</div>' +"""))

# ── 4 · copy Alex asked for ───────────────────────────────────────────────
subs.append((
"""    var visits = comp ? 'Four scheduled maintenance visits a year'
                      : 'Two scheduled maintenance visits a year';""",
"""    var visits = comp ? 'Four scheduled maintenance visits a year'
                      : 'Two scheduled maintenance visits a year';
    /* 1 Sep — "2 on-site coffee calibration sessions" replaces the Boncafé
       pooled OPERATOR TRAINING sessions I put here an hour ago. Better, and it
       also retires the flag I raised at the time: the training sessions are
       Boncafé's to deliver (§4.2) and putting them on the card created an
       obligation on someone else's calendar. Calibration is Alex's own —
       "i'll personally handle the calibration visits" — so it is a promise
       this company can keep on its own. It is also the more valuable of the
       two to an office: a machine that is serviced but out of calibration
       still makes bad coffee. */
    var calib = '2 on-site coffee calibration sessions';"""))

subs.append((
"""         (comp ? 'Two operator training sessions a year' : 'Year-one servicing included')],
      3:[(comp ? 'Breakdowns and parts covered for 3 full years'
                : 'Serviced and maintained for 3 full years'),
         visits,
         (comp ? 'Two operator training sessions a year' : 'Year-one servicing included'),
         'Free: livery wrap + live impact counter']""",
"""         calib],
      3:[(comp ? 'Breakdowns and parts covered for 3 full years'
                : 'Serviced and maintained for 3 full years'),
         visits,
         calib,
         'Free: co-branded wrap + live impact counter']"""))

subs.append((
"""            ex('cooler','Fresh-milk fridge',""",
"""            /* 1 Sep — the names say WHERE THE THING GOES and WHAT IT LOOKS
               LIKE, because that is what an office manager is deciding. Alex:
               "Specify Countertop Milk Fridge so office managers know it sits
               right beside the machine on the pantry counter." */
            ex('cooler','Countertop milk fridge',"""))

subs.append((
"""            ex('wrap','Livery wrap', wrapFree ? 'Free on this plan' : 'Your branding &middot; ' + CUR() + money(x.wrap), 0, 'machine-livery-uwcsea.png') +""",
"""            /* "Livery wrap" is in-house language — RATE-CARD and the Part 3
               contract both use it, and the quote sheet still does, but the
               tile a buyer reads should not. "Co-branded" also sets the right
               expectation: it is NoFilter's artwork carrying their logo, not a
               blank surface they art-direct. */
            ex('wrap','Co-branded machine wrap',
               wrapFree ? 'Free on this plan'
                        : 'Signature NoFilter artwork with your logo &middot; ' + CUR() + money(x.wrap),
               0, 'machine-livery-uwcsea.png') +"""))

subs.append((
"""                          'Fresh-milk fridge, custom livery wrap, live impact screen.') +""",
"""                          'Countertop milk fridge, co-branded machine wrap, live impact screen.') +"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = r'''
/* ── 29 · THE MORPH RIDES ABOVE THE DECK ──────────────────────────────────
   z-index 900 put the whole descent behind the focus deck's opaque paper
   (z-index 1400). Inside the deck this is a LOCAL z-index, so it only has to
   beat the deck's own children — but it is set at the file's morph rung
   anyway, below .nfx-close (1420) so the way out is never covered. */
.nfbd-morph{z-index:1410;}

/* the stepper, now in the foot beside the total */
#nfConsoleWrap .nfbd-buy .nfbd-qrow{margin:0;gap:10px;flex:0 1 auto;align-items:center;}
#nfConsoleWrap .nfbd-buy .nfbd-qnote{white-space:nowrap;}
#nfConsoleWrap .nfbd-buy .nfbd-remove{margin-left:0;}
@media(max-width:1100px){#nfConsoleWrap .nfbd-buy .nfbd-qnote{display:none;}}

/* the badge can never straddle: the card reserves the room above it */
#nfConsoleWrap .nfbd-cov{padding-top:12px;}
#nfConsoleWrap .nfbd-cov .rec{position:static;display:inline-block;align-self:flex-start;
  margin:0 0 9px;line-height:1.35;}

/* ── 30 · LEGIBILITY ON THE DARK TILES ────────────────────────────────────
   Alex: "The secondary labels on the dark hardware cards in Step 2 are dark
   grey on dark slate. Boost these to off-white." They were cream at 62%
   opacity over a 7%-cream tile — about 3.4:1, under the 4.5:1 floor, and it is
   the line carrying the PRICE. Now 88%, which measures past 7:1 on both the
   tile and the lit state. */
#nfConsoleWrap .nfbd-ex .d{color:rgba(255,246,232,.88);
  /* CAUGHT IN TEST: the longer wrap subtext ("Signature NoFilter artwork with
     your logo · SGD 1,000.00") runs to two lines, while "Free on this plan" is
     one — so picking the 3-year plan made the tile shorter and the whole panel,
     photograph included, moved. Exactly the jump Alex asked to be rid of two
     messages ago. The line box is fixed at two lines: short text keeps the room,
     long text clamps rather than pushing to three. */
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  overflow:hidden;min-height:2.6em;}
#nfConsoleWrap .nfbd-ex.is-on .d{color:rgba(26,24,21,.72);}
#nfConsoleWrap .nfbd-svc1 .d{color:rgba(255,246,232,.85);}
#nfConsoleWrap .nfbd-stephelp{color:rgba(255,246,232,.72);}

/* ── 31 · THE FINAL ACTION LOOKS LIKE ONE ─────────────────────────────────
   This was demoted to a quiet outline in August because "Confirm machines"
   sat live underneath it and two orange buttons were competing. That
   competition is over — the sticky bar stands down while the panel is open —
   so the one action on screen gets the weight back. */
#nfConsoleWrap .nfbd-done{
  background:var(--or,#ed3326);border:0;color:#fff;
  box-shadow:0 10px 26px rgba(238,77,23,.3);}
#nfConsoleWrap .nfbd-done:hover{background:var(--or,#ed3326);filter:brightness(1.06);}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("morph visible + stepper in step 3 + contrast + solid CTA + copy")
