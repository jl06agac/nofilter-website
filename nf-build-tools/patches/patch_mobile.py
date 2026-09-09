import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 110 · THE PHONE ════════════════════════════════════════════════════════
# Alex, 3 Sep, from an iPhone 15 Pro: "the shop page debacle, the see more
# details disaster, the overlapping numbers on the wholesale page".
# Measured at 393px in headless Chromium before touching anything, because
# three of the four faults had a cause that was not the obvious one.
#
# EVERYTHING HERE IS SCOPED. The tile and numeral fixes live inside
# max-width media queries, so no rule in this block can reach a desktop
# render — that was Alex's first question and it is answered by construction,
# not by assertion. The two JS changes (roller hold, autoplay fallback) are
# deliberate at every width and are marked as such.

# ── 1 · THE SHOP TILES ────────────────────────────────────────────────────
# Measured: at a 393px viewport the four coffee tiles come out 80px wide,
# sitting at left 204 and 297. The cause is one line —
#     function tileW(){ return (vp.clientWidth - GAP*3)/4; }
# — a hard four, in a component whose cells are absolutely positioned by
# script rather than laid out by CSS. There is no swipe handler, no arrows
# and no drag anywhere in it: the row is meant to be seen all at once, so
# narrowing it to a scroller would strand three of the four coffees behind a
# gesture that does not exist.
#
# So the cells come out of the absolute track on a phone and stack. This is
# done in CSS rather than by rewriting the geometry in two places (the shop
# owns cxTrack, the quote builder owns qxTrack, and both carry the same
# maths) because a stylesheet !important beats a non-important inline style —
# which is exactly what the script sets — and because a media query cannot
# affect a width it does not match. The script goes on computing its desktop
# geometry into inline styles; below 640px the stylesheet simply wins.
#
# Opacity is deliberately NOT forced. The script parks the closed detail cell
# at opacity 0, and overriding that would leave a dead card sitting under
# every list. Tiles are forced visible; the detail cell keeps its own state.
CSS_TILES = r'''
/* ══ 110 · THE TILE ROW ON A PHONE ═══════════════════════════════════════ */
@media(max-width:640px){
  .cx-track,#cxTrack,#qxTrack{
    height:auto!important;display:flex;flex-direction:column;gap:14px;
    transition:none!important}
  .cx-cell{
    position:static!important;width:100%!important;
    transform:none!important;transition:none!important}
  .cx-cell:not([data-detail]){opacity:1!important;pointer-events:auto!important}
  /* the viewport clipped a track it no longer has to clip */
  .cx-viewport{overflow:visible!important}
  /* the tile's own inner photo was sized against a 300px column */
  .cx-tile{padding:14px}
}
'''

# ── 2 · THE SECTION NUMERALS ──────────────────────────────────────────────
# Measured on /wholesale-coffee at 393px: 03, 04, 05 and 06 all overlap their
# own headline; 01 and 02 escape only because their headlines happen to sit
# clear. Two causes compounding, both from the 24 Aug treatment:
#   · font-size:clamp(56px,7vw,112px) — 7vw is 27px on this screen, so the
#     clamp pins to its 56px FLOOR and there is no mobile override anywhere.
#   · line-height:.82 — a 56px glyph in a 46px line box overflows its own
#     box by about 10px top and bottom, straight into the headline beneath.
# Both are undone below the breakpoint and nowhere above it. The treatment
# Alex asked for on 24 Aug is untouched at the width he asked for it.
CSS_NUMS = r'''
/* ══ 110 · THE SECTION NUMBERS ON A PHONE ════════════════════════════════ */
@media(max-width:700px){
  #work .beat-hd{gap:10px;margin-bottom:18px}
  #work .beat-hd .sn,
  #work .cx-eyebrow b[data-folio],
  #work .nw-foot b[data-folio]{
    font-size:30px;line-height:1;letter-spacing:-.02em}
}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS_TILES + CSS_NUMS)
src = "\n".join(lines)

# ── 3 · THE NAV ROLLER ────────────────────────────────────────────────────
# The fourth nav item cycles IN OFFICES → IN CAFÉS → IN ZOOS → IN HOTELS
# through a scramble drawn from A-Z. Alex: "the nav is fine, the roller
# cycling is intentional. But if you feel lengthening hold is correct, then
# fine." It is: HOLD 2600 against MOVE 460 + ROLL 560 leaves the label
# unreadable for about a fifth of every cycle, and on a phone the bar is
# pinned in view the whole time rather than scrolled past — which is why four
# of eleven screenshots caught it mid-scramble ("RH ZGQI", "UF NPLSP").
# 6000 keeps the effect and takes the unreadable share from ~28% to ~15%.
# This one is deliberate at every width.
fix("var HOLD=opts.hold||2600, MOVE=460, ROLL=560, SWAP=45;",
    "var HOLD=opts.hold||6000, MOVE=460, ROLL=560, SWAP=45;   /* block 110 */")

# ── 4 · THE HERO VIDEO ────────────────────────────────────────────────────
# Alex: "the intro hero video doesn't auto play". The markup is already
# correct — autoplay muted loop playsinline preload="auto" is every attribute
# iOS asks for — so this is not a markup fault. What is missing is what
# happens when iOS says no anyway, which it does under Low Power Mode as a
# matter of policy (Alex's battery reads 27% in every screenshot he sent).
# The rejection was swallowed by an empty catch, so a refused autoplay left a
# poster with no way to start it and no signal that anything had happened.
# Now the refusal is recorded on the element, a tap starts it, and the poster
# carries a play affordance in the meantime. Deliberate at every width: a
# desktop browser with autoplay disabled had exactly the same dead poster.
fix("""    var p = v.play();
    if(p && p.catch) p.catch(function(){ /* autoplay refused or codec rejected — poster stands in */ });""",
    """    var p = v.play();
    if(p && p.catch) p.catch(function(){
      /* block 110 — autoplay refused (Low Power Mode is the common one) or
         the codec was rejected. The poster stands in either way, but it now
         says so and a tap starts it, instead of looking broken. */
      v.setAttribute('data-noauto','1');
      var go = function(){
        var q = v.play();
        if(q && q.then) q.then(function(){ v.removeAttribute('data-noauto'); }, function(){});
      };
      v.addEventListener('click', go);
      v.addEventListener('touchend', go, {passive:true});
      var host = v.parentElement;
      if(host) host.addEventListener('click', go);
    });""")

CSS_VID = r'''
/* ══ 110 · A VIDEO IOS REFUSED TO START ══════════════════════════════════ */
video[data-noauto]{cursor:pointer}
video[data-noauto] + .nf-tap,
.nf-tap{display:none}
video[data-noauto]{outline:none}
/* the affordance rides on the video's own box via its parent */
*:has(> video[data-noauto])::after{
  content:"TAP TO PLAY";position:absolute;left:50%;top:50%;
  transform:translate(-50%,-50%);z-index:4;pointer-events:none;
  font-family:var(--mono);font-size:10px;letter-spacing:.18em;
  color:#F4EFE2;background:rgba(20,22,20,.62);border:1px solid rgba(244,239,226,.4);
  border-radius:999px;padding:9px 16px;backdrop-filter:blur(3px)}
@media(prefers-reduced-motion:reduce){*:has(> video[data-noauto])::after{content:"TAP TO PLAY"}}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS_VID)
src = "\n".join(lines)

io.open(F, "w", encoding="utf-8").write(src)
print("the phone: tiles stack, numbers shrink, the roller holds, a refused video says so")
