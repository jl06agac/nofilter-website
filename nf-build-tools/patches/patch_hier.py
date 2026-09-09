import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the card's CTA states what pressing it actually does ────────────────
subs.append((
"""        '<div class="mx-add-live">' +
          '<span class="mx-sum" data-addsub></span>' +""",
"""        '<div class="mx-add-live">' +
          '<span class="mx-sum" data-addsub></span>' +
          /* 1 Sep — the PURCHASE face of the live pill. On a rental the stepper
             below is the only place a count is set, so it stays. On a purchase
             the dossier now owns the quantity and has its own stepper, so a
             second one on the card is the same number driven from two places —
             the duplication this pass has cut four times. This replaces it and
             reopens the panel instead. */
          '<button type="button" class="mx-cfg" data-cfg aria-label="Edit the configuration for ' + m.name + '"></button>' +"""))

subs.append((
"""    var addBox = $('[data-addcta]', c);
    if(addBox) addBox.classList.toggle('is-on', q > 0);""",
"""    var addBox = $('[data-addcta]', c);
    if(addBox) addBox.classList.toggle('is-on', q > 0);
    /* ── 1 Sep · THE BUTTON SAYS WHAT PRESSING IT DOES ────────────────────
       Alex: "the 'add' button is a bit misleading, as when i click it it opens
       up this bottom more comprehensive panel, from where they add what they
       want." Exactly right, and it is the plainest statement yet of the
       complaint that started this whole thread — "i'd be super confused as a
       buyer, especially on the purchase".
       "Add +" is a promise of a one-click basket add. On a rental that promise
       is kept: the deal is pre-bundled and one press is the whole decision. On
       a purchase it is not — the press opens a panel and nothing is decided
       until you have chosen cover and hardware. So the label follows the mode.
       Once configured it stops being a stepper and reports state instead,
       because the panel owns the count now. */
    if(addBox){
      addBox.classList.toggle('is-cfg', isBuy);
      var cta = $('.mx-cta', addBox);
      if(cta) cta.innerHTML = isBuy
        ? 'Configure <span class="mx-plus" aria-hidden="true">&rarr;</span>'
        : 'Add <span class="mx-plus" aria-hidden="true">+</span>';
      /* SHORT. The first version read "N configured · Edit", which with the
         price beside it wanted ~330px inside a 268px pill — so the two ran
         straight through each other on the card. Caught on screen, not by the
         test, because the test asserted the label's TEXT and never looked at
         it. The count is carried by the ×N and the word Edit does the rest. */
      var cfg = $('.mx-cfg', addBox);
      if(cfg) cfg.innerHTML = '&times;' + q + ' <b>Edit</b>';
    }"""))

# ── 3 · the scroll target, which is what actually caused the collision ──────
subs.append((
"""      setTimeout(function(){ if(openK === k) nfbdScroll(doss); }, 260);""",
"""      setTimeout(function(){ if(openK === k) nfbdReveal(); }, 260);"""))

subs.append((
"""  function ensureMorph(){
    if(!morph){
      morph = document.createElement('div');
      morph.className = 'nfbd-morph';""",
"""  /* ── 1 Sep · REVEAL THE PANEL'S FOOT, NOT ITS HEAD ────────────────────────
     Alex: "there's also padding issues ... for the clashing going on at the
     bottom." Measured at three heights, and it is a SHORT-VIEWPORT fault, which
     is why it never appeared in my own renders at 1000px:

         viewport 1000   overlap with the sticky bar    0px
         viewport  820   overlap                       36px
         viewport  700   overlap                      152px, and 31px past the fold

     The mechanism is the one block 5 in the sheet already records for the
     cards — .deck-actions is position:sticky, bottom:0, with an opaque
     gradient, "measured at 73px of overlap on the machine cards". But the
     clearance is not the whole story here: nfbdScroll aligns a target's TOP
     90px below the viewport top, which is right for a card and wrong for a
     641px panel on an 820px screen, because it pushes the panel's own footer —
     the total and the button, the two things being scrolled TO — underneath
     the bar.

     So the panel gets its own reveal: bring its FOOT to rest just above the
     sticky bar, and only fall back to aligning the top when the panel is too
     tall to fit in the room that is left. Never scroll its head off the top. */
  function nfbdReveal(){
    var fs   = document.querySelector('.nf-focus-sec');
    var bar  = document.querySelector('.deck-screen.is-active .deck-actions');
    var barH = bar ? bar.getBoundingClientRect().height : 0;
    var r    = doss.getBoundingClientRect();
    var vTop = fs ? fs.getBoundingClientRect().top : 0;
    var vH   = fs ? fs.getBoundingClientRect().height : window.innerHeight;
    var foot = vTop + vH - barH - 14;            /* the last line clear of the bar */
    var d    = r.bottom - foot;                  /* scroll DOWN by this to reach it */
    var headroom = r.top - (vTop + 14);          /* never scroll the head out of view */
    if(d > headroom) d = headroom;               /* too tall: show the top instead */
    if(d < 0 && r.top >= vTop + 14) return;      /* already fully visible, leave it */
    if(fs){
      var t = fs.scrollTop + d;
      try{ fs.scrollTo({top:Math.max(0,t), behavior:'smooth'}); }catch(e){ fs.scrollTop = Math.max(0,t); }
    } else {
      try{ window.scrollTo({top:Math.max(0, window.scrollY + d), behavior:'smooth'}); }catch(e){}
    }
  }

  function ensureMorph(){
    if(!morph){
      morph = document.createElement('div');
      morph.className = 'nfbd-morph';"""))

subs.append((
"""      doss.style.transition = '';
      nfbdScroll(doss);
      return;
    }""",
"""      doss.style.transition = '';
      nfbdReveal();
      return;
    }"""))

# open the panel from the card's configured pill
subs.append((
"""    var t = e.target.closest ? e.target.closest('[data-q],[data-mode]') : null;
    if(!t) return;
    var card = t.closest('.q-eq-card'); if(!card) return;
    var k = card.getAttribute('data-m'); if(!k || !Q.m[k]) return;
    var isMode = t.hasAttribute('data-mode');""",
"""    var t = e.target.closest ? e.target.closest('[data-q],[data-mode],[data-cfg]') : null;
    if(!t) return;
    var card = t.closest('.q-eq-card'); if(!card) return;
    var k = card.getAttribute('data-m'); if(!k || !Q.m[k]) return;
    /* the "N configured · Edit" pill reopens the panel and changes nothing */
    if(t.hasAttribute('data-cfg')){ open_(k); return; }
    var isMode = t.hasAttribute('data-mode');"""))

# ── 4 · the payoff line reads as a sentence, the figure as a figure ────────
subs.append((
"""            '<button type="button" class="nfbd-done" data-nfbd-close>Done &rarr;</button>' +""",
"""            /* 1 Sep — DEMOTED, NOT REMOVED. Alex: "two bright orange buttons
               are competing for attention." They are, but they are not the same
               action: "Confirm machines" advances the step, this only shuts the
               panel. Hiding the step's forward action while the panel is open
               would strand someone who has finished, so the fix is weight, not
               removal — one primary on screen, and it is the one that moves you
               on. It is also NOT relabelled "Save": every toggle already writes
               into the quote and recalculates live, so a Save label would tell
               the buyer their changes do not count until they press it, which
               is false in the direction that costs confidence. */
            '<button type="button" class="nfbd-done" data-nfbd-close>Done</button>' +"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = r'''
/* ── 25 · BUTTON HIERARCHY AND THE BOTTOM COLLISION ───────────────────────
   Alex, 1 Sep, on the purchase screens. Four changes, all narrow. */

/* 1 · the purchase pill reports state instead of stepping. The .mx-grp stepper
   stays in the DOM because recalc() writes the count into its .qv span and
   there must be exactly one of those on the card — it is hidden, not removed. */
#nfConsoleWrap .mx-add.is-cfg .mx-grp{display:none;}
#nfConsoleWrap .mx-add:not(.is-cfg) .mx-cfg{display:none;}
/* CAUGHT IN RENDER: this was first written cream-on-translucent-cream, copying
   the .mx-gb stepper buttons — but those live on the ZERO-state pill, which is
   ink. The moment a machine is in, .mx-add.is-on repaints the pill LIGHT
   (rgba(26,24,21,.055) with ink text), so the label was cream on cream and
   invisible. It reads ink-on-light, like everything else on that face. */
#nfConsoleWrap .mx-cfg{
  font-family:var(--font-m,"IBM Plex Mono",monospace);font-size:10px;
  letter-spacing:.07em;text-transform:uppercase;
  background:rgba(26,24,21,.08);border:0;border-radius:99px;
  color:var(--nb,#1A1815);padding:8px 13px;cursor:pointer;white-space:nowrap;
  transition:background .15s ease;
}
#nfConsoleWrap .mx-cfg b{font-weight:600;text-decoration:underline;text-underline-offset:2px;}
#nfConsoleWrap .mx-cfg:hover{background:rgba(26,24,21,.16);}
/* AND THE OVERLAP IS MADE IMPOSSIBLE, not merely unlikely. .mx-add-live is a
   space-between flex row and .mx-sum carried white-space:nowrap with no flex
   basis, so once the two children wanted more than the pill's 268px of inner
   width they simply overran each other. The figure now yields and clips before
   it can reach the control; the control never shrinks. If a future currency or
   a longer figure runs out of room the price truncates — visibly wrong, which
   is recoverable — instead of printing through a button, which reads as broken. */
#nfConsoleWrap .mx-add.is-cfg .mx-sum{flex:1 1 auto;min-width:0;overflow:hidden;}
#nfConsoleWrap .mx-add.is-cfg .mx-cfg{flex:0 0 auto;margin-left:8px;}
#nfConsoleWrap .mx-cfg:focus-visible{outline:2px solid var(--or,#ed3326);outline-offset:2px;}

/* 2 · ONE PRIMARY ON SCREEN. "Done" closes a panel whose every change is
   already in the quote; "Confirm machines" is the one that moves the reader on,
   so it keeps the orange and this becomes a quiet outline. Still obviously a
   button — cream on ink at 1.4px is unmissable on this sheet — just no longer
   claiming to be the thing you came here to press. */
#nfConsoleWrap .nfbd-done{
  background:none;border:1.4px solid rgba(244,242,238,.5);color:#F4F2EE;
  box-shadow:none;font-size:13.5px;font-weight:600;padding:12px 22px;
}
#nfConsoleWrap .nfbd-done:hover{background:rgba(244,242,238,.14);filter:none;}

/* 3 · daylight under the panel. The scroll target does the real work (see
   nfbdReveal), but the panel should never sit flush against the bar either. */
#nfConsoleWrap #nfBuyDoss.is-open{margin-bottom:clamp(20px,4vh,40px);}

/* 4 · THE PAYOFF LINE IS A SENTENCE. Alex: "swap the bottom monospace rental
   comparison string to a clean sans-serif to match the rest of your modern
   typography." Agreed for the words — it is the most persuasive line in the
   panel and mono made it read as a system message rather than an argument.
   The FIGURE stays mono, because that is this file's convention for a
   machine-stated number and it is what makes 2,920.00 read as computed rather
   than claimed. And it goes up from 10.5px, which was smaller than anything
   else on the sheet making a case. */
#nfConsoleWrap .nfbd-vs{
  font-family:var(--body,sans-serif);font-size:12.5px;line-height:1.5;
  letter-spacing:0;color:rgba(255,232,195,.75);margin-top:13px;
}
#nfConsoleWrap .nfbd-vs b{
  font-family:var(--font-m,"IBM Plex Mono",monospace);font-size:12px;
  color:#F4F2EE;font-weight:400;
}

/* 5 · COMPACT ON A SHORT SCREEN. Measured at a 700px viewport: the sticky bar
   is 121px, leaving 551px of clear room, and the panel wanted 646 — so 81px of
   it sat under the bar even with the reveal aiming correctly. The photo is not
   the cause (431px); the BODY is, at the full 646. Nothing is removed and no
   type drops below the sizes already stress-tested — the padding and the two
   display figures give back the ~110px needed to fit. Above 860px tall this
   block does not apply at all and the panel is exactly as designed. */
@media (max-height:860px){
  /* 1 Sep, second pass: the risk-based rung copy ("Every part and breakdown
     insured, from month 13") runs longer than the old two-word lines and put the
     panel back over the sticky bar at 700px by 10px. Trimmed here rather than by
     shortening the copy, because that sentence IS the product. */
  #nfConsoleWrap .nfbd-body{padding-top:13px;padding-bottom:13px;}
  #nfConsoleWrap .nfbd-frame{padding:16px;}
  #nfConsoleWrap .nfbd-name{font-size:clamp(26px,2.6vw,32px);margin-bottom:10px;}
  #nfConsoleWrap .nfbd-eyebrow{margin-bottom:7px;}
  #nfConsoleWrap .nfbd-qrow{margin-bottom:13px;}
  #nfConsoleWrap .nfbd-covs{margin-bottom:10px;}
  #nfConsoleWrap .nfbd-cov{padding:10px 11px 10px;}
  #nfConsoleWrap .nfbd-cov .pm{margin-bottom:7px;}
  #nfConsoleWrap .nfbd-cov ul{padding-top:7px;}
  #nfConsoleWrap .nfbd-cov li{margin-bottom:3px;}
  #nfConsoleWrap .nfbd-extras{margin-bottom:10px;}
  #nfConsoleWrap .nfbd-ex{padding:6px 10px 6px 6px;}
  #nfConsoleWrap .nfbd-th{width:40px;height:40px;}
  #nfConsoleWrap .nfbd-buy{padding-top:14px;}
  #nfConsoleWrap .nfbd-price b{font-size:clamp(26px,2.6vw,32px);}
  #nfConsoleWrap .nfbd-vs{margin-top:9px;}
  /* third pass, 1 Sep: the per-machine build added a fourth extras tile and
     wrapped the insurance line onto two rows, putting 700px back over the bar
     by 20px. Trimmed the rung interiors and the thumbnails rather than the
     copy — every sentence in here is now doing commercial work. */
  #nfConsoleWrap .nfbd-cov li{line-height:1.3;margin-bottom:2px;}
  #nfConsoleWrap .nfbd-cov ul{padding-top:6px;}
  #nfConsoleWrap .nfbd-covs{margin-bottom:8px;}
  #nfConsoleWrap .nfbd-extras{margin-bottom:8px;}
  #nfConsoleWrap .nfbd-ex{padding:5px 9px 5px 5px;}
  #nfConsoleWrap .nfbd-th{width:34px;height:34px;}
  #nfConsoleWrap .nfbd-ex .d{font-size:9px;}
  /* fourth pass: the year-one servicing row is another ~45px. Trimmed the two
     display figures and the vertical rhythm rather than dropping any control —
     at this height every element on the panel is now load-bearing. */
  #nfConsoleWrap .nfbd-name{font-size:clamp(22px,2.2vw,26px);margin-bottom:7px;}
  #nfConsoleWrap .nfbd-qrow{margin-bottom:9px;}
  #nfConsoleWrap .nfbd-cov{padding:8px 10px;}
  #nfConsoleWrap .nfbd-svc1{margin-bottom:8px;}
  #nfConsoleWrap .nfbd-buy{padding-top:10px;}
  #nfConsoleWrap .nfbd-price b{font-size:clamp(22px,2.2vw,28px);}
  #nfConsoleWrap .nfbd-price small{margin-bottom:2px;}
}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("hierarchy + collision patch applied")
