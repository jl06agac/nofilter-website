import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · ONE close control, not two ────────────────────────────────────────
subs.append((
"""      '<button type="button" class="nfbd-close" data-nfbd-close>Close</button>' +""",
"""      /* ── 1 Sep · THE TOP-RIGHT "CLOSE" IS GONE ────────────────────────────
         Alex: "Stick to one dedicated close control to avoid UI clutter."
         There were two, and they did exactly the same thing: this one, and the
         button in the foot. Two controls for one action in one panel is the
         kind of thing that makes a reader hesitate over which is the safe one.
         The foot button survives because it is where the reader ends up — it
         now closes STEP 3 and says so ("Save & add to quote"), which is a
         better label for the same action than a corner X. */"""))

# ── 2 · the three steps ───────────────────────────────────────────────────
subs.append((
"""          '<div><div class="nfbd-secthd"><p class="nfbd-sect">Select care &amp; servicing plan</p>' +""",
"""          /* ── 1 Sep · THE PANEL IS THREE NUMBERED STEPS ───────────────────
             Alex's structure, and it fixes a real problem: the panel presented
             a required decision, an optional one and a total as three
             identically-weighted blocks, so nothing told the reader which of
             them she actually had to answer. Numbering them does; tagging one
             Required and one Optional does the rest. */
          '<div>' + step(1, 'Select care &amp; servicing plan', 'Required',
                         'Choose your warranty and preventative maintenance schedule.') +
          /* .nfbd-secthd held the heading and, before that, the decline link.
             Both have moved, so the wrapper is an empty flex row with a 10px
             margin — deleted rather than left to add invisible space. */
          '' +"""))

# the </div> that closed .nfbd-secthd goes with it
subs.append((
"""            '</div><div class="nfbd-covs">' + rung(0) + rung(2) + rung(3) + '</div>' +""",
"""            '<div class="nfbd-covs">' + rung(0) + rung(2) + rung(3) + '</div>' +"""))

subs.append((
"""          '<div><p class="nfbd-sect">Extra hardware</p><div class="nfbd-extras">' +""",
"""          '<div>' + step(2, 'Choose extra hardware &amp; add-ons', 'Optional',
                          'Fresh-milk fridge, custom livery wrap, live impact screen.') +
          '<div class="nfbd-extras">' +"""))

subs.append((
"""          '<div class="nfbd-buy">' +
            '<div class="nfbd-price"><small>Total purchase price</small>' +""",
"""          step(3, 'Review &amp; confirm', '',
               'This is the one-off price for the machines as configured above.',
               'nfbd-step--rev') +
          '<div class="nfbd-buy">' +
            '<div class="nfbd-price"><small>Total purchase price</small>' +"""))

# the step() builder itself, next to the rung builder
subs.append((
"""    var rung = function(n){
      var none = (n === 0);""",
"""    /* a numbered badge, the title, an optional Required/Optional tag, and one
       line of help. The tag is a WORD, not a colour: this reader is red-green
       colourblind and every state in this file has to survive being read in
       grey. */
    var step = function(n, title, tag, help, cls){
      return '<div class="nfbd-step' + (cls ? ' ' + cls : '') + '">' +
          '<span class="nfbd-stepno">Step ' + n + '</span>' +
          '<span class="nfbd-steptt">' + title + '</span>' +
          (tag ? '<span class="nfbd-steptag' + (tag === 'Required' ? ' is-req' : '') + '">' +
                 tag + '</span>' : '') +
        '</div>' +
        (help ? '<p class="nfbd-stephelp">' + help + '</p>' : '');
    };
    var rung = function(n){
      var none = (n === 0);"""))

# ── 3 · the RECOMMENDED badge sits INSIDE the card, and reserves its row ──
subs.append((
"""        (n === 3 ? '<span class="rec">Recommended</span>' : '') +""",
"""        /* ── 1 Sep · IN THE FLOW, NOT ON THE BORDER ──────────────────────
           Alex: "The pill badge uses absolute positioning (top:-10px) without
           adding extra top padding inside the card to push the text down. The
           badge breaks the card border line and crowds the title underneath."
           Correct on both counts. It is the first element in the card now.

           But it renders on ALL THREE columns, empty on two of them: put it in
           the flow on one card only and that card's title drops ~20px below its
           neighbours', so fixing the badge would break the row it sits in. The
           two ghosts reserve the line and are hidden the same way the add-on
           row is — unpainted, and out of the accessibility tree. */
        '<span class="rec' + (n === 3 ? '' : ' is-ghost" aria-hidden="true') + '">Recommended</span>' +"""))

# ── 4 · the foot button says what it does ─────────────────────────────────
subs.append((
"""            '<button type="button" class="nfbd-done" data-nfbd-close>Done</button>' +""",
"""            /* 1 Sep — "Done" becomes the step's own action. It was deliberately
               NOT called "Save" in August, on the grounds that every toggle is
               already live and a Save label would imply the changes did not
               count until pressed. That still holds — and it is outweighed now
               that this is the ONLY close control in the panel and the foot of
               a numbered Step 3. A button that ends a step needs to name the
               step's outcome, and "add to quote" is what pressing it leaves the
               reader with. */
            '<button type="button" class="nfbd-done" data-nfbd-close>' +
              'Save &amp; add to quote <span aria-hidden="true">&rarr;</span></button>' +"""))

# ── 5 · removing a machine forgets what was configured on it ──────────────
subs.append((
"""    if(t.hasAttribute('data-nfbd-close')){ close_(); return; }
    if(t.hasAttribute('data-nfbd-remove')){ Q.m[k].q = 0; recalc(); close_(); return; }""",
"""    if(t.hasAttribute('data-nfbd-close')){ close_(); return; }
    if(t.hasAttribute('data-nfbd-remove')){ dropBuy(k); return; }"""))

subs.append((
"""      cfg.q = Math.max(0, Math.min(20, cfg.q + parseInt(t.getAttribute('data-nfbd-q'), 10)));
      if(cfg.q === 0){ recalc(); close_(); return; }
    } else if(t.hasAttribute('data-nfbd-remove')){
      cfg.q = 0; recalc(); close_(); return;""",
"""      cfg.q = Math.max(0, Math.min(20, cfg.q + parseInt(t.getAttribute('data-nfbd-q'), 10)));
      if(cfg.q === 0){ dropBuy(k); return; }
    } else if(t.hasAttribute('data-nfbd-remove')){
      dropBuy(k); return;"""))

subs.append((
"""  function open_(k){
    var card = document.querySelector('.q-eq-card[data-m="' + k + '"]');""",
"""  /* ── 1 Sep · A REMOVED MACHINE COMES BACK AS A BLANK ─────────────────────
     Alex: "if i 'remove from quote' the quote builder machine purchase price
     should default to the base level not retain the options i've just
     selected."
     It did retain them, and the reason is worth writing down: the purchase
     defaults are seeded ONCE per card, behind a __buyInit flag, so that
     flipping to Rental and back does not wipe out choices the reader has made.
     That is right for a toggle and wrong for a removal — removing is the
     reader saying "forget this machine", and coming back to a card still
     carrying a 5,150 cover plan they thought they had deleted is the worst
     kind of surprise on a quote.
     So removal clears the flag as well as the quantity, and the next open
     re-seeds from the same defaults a first-time reader gets. */
  function dropBuy(k){
    var cfg = Q.m[k]; if(!cfg) return;
    cfg.q = 0;
    cfg.svcYrs = 2;
    cfg.svc = cfg.svc1 = cfg.wrap = cfg.counter = false;
    cfg.cooler = true;                       /* standard on a purchase, as on a rental */
    var card = document.querySelector('.q-eq-card[data-m="' + k + '"]');
    if(card) card.__buyInit = false;          /* let the default seeder run again */
    recalc();
    close_();
  }

  function open_(k){
    var card = document.querySelector('.q-eq-card[data-m="' + k + '"]');"""))

# ── 6 · the step's forward action stands down while the panel is open ─────
subs.append((
"""    doss.classList.add('is-open');
    doss.setAttribute('aria-hidden','false');""",
"""    doss.classList.add('is-open');
    /* ── 1 Sep · THE STICKY BAR STANDS DOWN ──────────────────────────────
       Alex: "Confirm machines → ... should disappear prior to configure
       selection opening up the full bleed bar, right now it stays on page
       while the configure expands. bad ux."
       It is the step's forward action sitting live under a panel that has its
       own forward action, so two buttons compete for the same press and one of
       them silently abandons the configuration in progress. In August I argued
       against hiding it — that it would strand a reader who had finished — but
       that was before the panel's foot became "Save & add to quote", which
       ends the step properly and brings the bar straight back.
       visibility, not display: the bar's height is what nfbdReveal measures to
       keep the panel clear of it, and collapsing it would move the thing the
       measurement is about. The rule reads #nfBuyDoss.is-open through :has(),
       so there is no flag here to set and none to strand. */
    doss.setAttribute('aria-hidden','false');"""))

subs.append((
"""  function close_(){
    if(!openK) return;
    openK = null;""",
"""  function close_(){
    if(!openK) return;
    openK = null;
    /* belt and braces: if an older build of this page left the flag on the
       document, clear it so a stale class can never hide a forward action. */
    document.documentElement.classList.remove('nfbd-panel-open');"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = r'''
/* ── 28 · NUMBERED STEPS ──────────────────────────────────────────────────
   A badge, a title and a tag on one baseline, with the help line under it.
   The badge is the only orange thing in the panel besides the primary button,
   which is deliberate: it is the reader's place-marker, so it should be the
   thing the eye finds when it comes back from reading a column. */
#nfConsoleWrap .nfbd-step{display:flex;align-items:center;gap:9px;margin:0 0 5px;flex-wrap:wrap;}
#nfConsoleWrap .nfbd-stepno{font-family:var(--mono,monospace);font-size:9.5px;font-weight:700;
  letter-spacing:.11em;text-transform:uppercase;color:#fff;background:var(--or,#ed3326);
  border-radius:4px;padding:3px 8px;flex:0 0 auto;}
#nfConsoleWrap .nfbd-steptt{font-family:var(--mono,monospace);font-size:10.5px;font-weight:600;
  letter-spacing:.13em;text-transform:uppercase;color:#F4F2EE;}
/* Required / Optional is a WORD in a bordered chip. No hue carries it — this
   reader is red-green colourblind, so the two states differ by border weight
   and text, and read identically in grey. */
#nfConsoleWrap .nfbd-steptag{font-family:var(--body,sans-serif);font-size:10px;font-weight:600;
  letter-spacing:.04em;color:rgba(255,232,195,.7);border:1px solid rgba(255,232,195,.3);
  border-radius:99px;padding:1px 8px;flex:0 0 auto;}
#nfConsoleWrap .nfbd-steptag.is-req{color:#F4F2EE;border-color:rgba(244,242,238,.65);}
#nfConsoleWrap .nfbd-stephelp{font-family:var(--body,sans-serif);font-size:11.5px;
  line-height:1.45;color:rgba(255,232,195,.6);margin:0 0 11px;}
/* step 3 sits on the divider the total already had, so the rule moves up to it */
#nfConsoleWrap .nfbd-step--rev{border-top:1px solid rgba(244,242,238,.2);padding-top:16px;}
#nfConsoleWrap .nfbd-buy{border-top:0;padding-top:0;}

/* the badge in the flow. The two ghosts hold the line the real one sits on so
   all three column titles stay level — same reservation trick as the add-on
   row, and for the same reason. */
#nfConsoleWrap .nfbd-cov .rec{position:static;display:inline-block;margin:0 0 8px;
  align-self:flex-start;}
#nfConsoleWrap .nfbd-cov .rec.is-ghost{visibility:hidden;}
#nfConsoleWrap .nfbd-cov{display:flex;flex-direction:column;padding-top:11px;}
#nfConsoleWrap .nfbd-cov .tick{top:14px;}

/* COMPACT. The three step headers add about 130px of chrome, which at a 700px
   viewport is the difference between the panel fitting and the total sliding
   under the fold. The help lines go first — they explain a decision the column
   titles already name — then the badge row tightens. Nothing that carries a
   price or a state is touched. */
@media(max-height:860px){
  #nfConsoleWrap .nfbd-stephelp{display:none;}
  #nfConsoleWrap .nfbd-step{margin-bottom:9px;}
  #nfConsoleWrap .nfbd-step--rev{padding-top:12px;}
}
@media(max-height:760px){
  #nfConsoleWrap .nfbd-step{margin-bottom:4px;}
  #nfConsoleWrap .nfbd-steptt{font-size:9.5px;}
  #nfConsoleWrap .nfbd-step--rev{padding-top:8px;}
  #nfConsoleWrap .nfbd-stepno{padding:2px 7px;}
  #nfConsoleWrap .nfbd-cov{padding-top:8px;}
  #nfConsoleWrap .nfbd-cov .rec{margin-bottom:5px;}
  /* the last 30px, found in the places that cost the least: the gap under the
     columns, the leading inside them, and the gap under the add-on row. Checked
     at 1.3x letter-spacing, because the container's fallback mono is narrower
     than real IBM Plex and this trap has bitten twice. */
  #nfConsoleWrap .nfbd-covs{margin-bottom:6px;}
  #nfConsoleWrap .nfbd-cov li{line-height:1.28;margin-bottom:2px;}
  #nfConsoleWrap .nfbd-svc1{margin-bottom:8px;}
}

/* ── the step's forward action while the panel owns the screen ────────────
   BROKEN IN TEST, and Alex hit it: "what have you done with my proceed
   button, i can't even go to next screen?"

   v1 keyed this off a class on <html>, set in open_ and removed in close_.
   Two faults, and the second is the serious one:

   · close_() begins `if(!openK) return`, so any path that left openK null
     without running the body stranded the class — and once stranded there is
     no way back, because only close_() removes it.
   · and an <html> class says nothing about WHICH screen the panel is on. The
     selector then matched `.deck-screen.is-active`, i.e. whichever step the
     reader was looking at. Stranded on step 1, it took away the coffee
     selector's Continue button. That is a dead end, not a cosmetic bug.

   State that lives in the DOM should be read from the DOM. :has() asks the
   only question that matters — is the panel open INSIDE this screen — so it
   is self-clearing by construction and cannot reach a screen the panel is not
   in. The file already uses :has() for the deck's own layout rules. */
#nfConsoleWrap .deck-screen.is-active:has(#nfBuyDoss.is-open) .deck-actions{
  visibility:hidden;pointer-events:none;}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)
io.open(F, "w", encoding="utf-8").write(src)
print("steps + single close + badge in flow + reset on remove")
