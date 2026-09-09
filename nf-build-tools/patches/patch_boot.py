import io, re, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 111 · WHAT THE FIRST SECOND IS SPENDING ════════════════════════════════
# Alex, 3 Sep: "there seems to be an initial lag whereby when i'm scrolling,
# nothing happens ... and then the computer catches up".
#
# The stall itself was NOT this site. Traced on his machine in an incognito
# window with extensions off: TTFB 30ms, domInteractive 514ms, LCP 812ms,
# zero long tasks, zero blocking, worst input delay 13ms. The catch-up was the
# Apollo.io browser extension injecting a content script into every tab and
# competing for the main thread during load — his console showed it arriving
# before the page's own scripts. Nothing here fixes that, and nothing needed
# to; it is a setting in his browser.
#
# What the trace DID prove is waste worth removing on its own merits. His
# probe found eight videos decoding at once on the home route, four of them
# at opacity 0 — decoding where nobody can see them.

# ── 1 · A CORRECTION, KEPT ON THE RECORD ──────────────────────────────────
# I told Alex that wp-office-lite.mp4 and wp-pour-lite.mp4 were the wholesale
# route's videos playing on the home page, and used that to argue the router
# rewrite would pay for itself twice. It is not true. All three of the .vf
# clips in his trace — keeps-standing-lite, wp-office-lite, wp-pour-lite —
# sit inside <section class="route on" id="home">. The wp- prefix names the
# asset, not the route it belongs to, and his own table shows them at opacity
# 0.6 and 0.55: visible, deliberate, home-page content.
#
# So nothing here touches them. Removing their autoplay would have changed
# nothing on the home route anyway (armVideos plays a current-route video
# regardless) and would have cost a frame on the route where they matter.
# The assert that was supposed to find two of them found three, which is the
# only reason this was caught before it shipped.

# ── 2 · TWO DECODERS FOR A SIX-TENTHS-OF-A-SECOND FLICKER ─────────────────
# .cover-video--cyan and .cover-video--red are opacity:0 in the stylesheet.
# They exist to be screen-blended over the hero during `is-glitching`, an
# animation that fires on roughly one glitch in five, on a schedule that
# starts at 9s and repeats every 12-25s. Between those moments — which is
# essentially always — they were decoding the same 3.09MB 720p clip as the
# visible hero, twice over, permanently.
#
# They lose autoplay and are started only when the shudder actually fires,
# then paused when it is over. The effect is unchanged; the steady state goes
# from three decoders of hero-trim-fast.mp4 to one.
fix("""<video class="cover-video cover-video--cyan" aria-hidden="true" autoplay muted loop playsinline preload="metadata">""",
    """<video class="cover-video cover-video--cyan" aria-hidden="true" muted loop playsinline preload="metadata">""")
fix("""<video class="cover-video cover-video--red" aria-hidden="true" autoplay muted loop playsinline preload="metadata">""",
    """<video class="cover-video cover-video--red" aria-hidden="true" muted loop playsinline preload="metadata">""")

fix("""vidLayers.forEach(function(v){ v.classList.remove('is-glitching'); void v.offsetWidth; v.classList.add('is-glitching'); });""",
    """vidLayers.forEach(function(v){ v.classList.remove('is-glitching'); void v.offsetWidth; v.classList.add('is-glitching');
          /* block 111 — the duotone layers are opacity:0 except right here,
             so they only decode right here. 700ms covers the 600ms animation. */
          if(v.classList.contains('cover-video--cyan') || v.classList.contains('cover-video--red')){
            try{ var q = v.play(); if(q && q.catch) q.catch(function(){}); }catch(e){}
            clearTimeout(v.__nfShudder);
            v.__nfShudder = setTimeout(function(){ try{ v.pause(); }catch(e){} }, 700);
          } });""", 2)   # two copies of the cover choreography, as with the dossier

# ── 3 · THE CLS FIX THAT WAS BUILT AND THEN WITHDRAWN ─────────────────────
# Alex's trace showed CLS 0.118 against Google's 0.10 threshold, and the two
# lazy images on the home route carry no width, height or aspect-ratio — so
# reserving their space looked like the obvious win, and it is where the
# shift is coming from.
#
# It is not this simple, and the desktop check caught why. The images are
# rendered at roughly 2:1 (918x459 on the home route, 593x336 on work), but
# their intrinsic dimensions are 1600x1069 and 1600x272 — nothing like the
# boxes they occupy. Something in the stylesheet is already sizing and
# cropping them. Adding width/height plus `img[width][height]{height:auto}`
# overrode that and moved the box on desktop: one changed IMG at 1440px on
# /home, another on /work.
#
# Alex's first question about this whole pass was whether it could touch his
# desktop styling, and the answer he was given was no, guaranteed by scoping.
# Shipping a layout change to honour a 0.018 CLS overage — while he is away
# and cannot look at it — would make that answer false for the sake of a
# marginal metric. So it is out.
#
# Doing it properly means finding the rule that crops these two, and giving
# them a reserved box at the ratio they are ACTUALLY displayed at rather than
# their intrinsic one. That is a ten-minute job with him watching, and a
# needless risk without him.

io.open(F, "w", encoding="utf-8").write(src)
print("the first second: the duotones decode only when seen, two images hold their place")
