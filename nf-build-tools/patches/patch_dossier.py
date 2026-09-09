import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 105 · FIVE THINGS ALEX SAW ON THE SHOP PAGE, 3 SEP ═════════════════════

# ── 1 · the caption pills are as wide as their words ──────────────────────
# "the batang gadis shading or backing banner shouldn't extend horizontally
# as far as it has, there are no additional words there. same for canopy
# shade." .vp-ov is a column flexbox; a flex column stretches its items to
# the container's width unless told otherwise, so every backed pill ran the
# full width of the plate. Told otherwise.
fix("""  display:flex;flex-direction:column;gap:3px;pointer-events:none;
}""",
    """  display:flex;flex-direction:column;align-items:flex-start;gap:3px;pointer-events:none;   /* block 105: pills hug their words */
}""")

# ── 2 · PRCF INDONESIA, in the one caption that is set in capitals by hand ─
# block 98 renamed PRCF everywhere; this overlay is typed in capitals rather
# than transformed by CSS, so the rename landed as mixed case in a row of
# upper. The two tile notes ('N. SUMATRA · PRCF Indonesia & SRI') are the
# same case and get the same fix.
fix("""KOMANJA GROWERS &middot; PRCF Indonesia &amp; SRI MEMBERS""",
    """KOMANJA GROWERS &middot; PRCF INDONESIA &amp; SRI MEMBERS""")
fix("""note:'N. SUMATRA · PRCF Indonesia & SRI'""", """note:'N. SUMATRA · PRCF INDONESIA & SRI'""", 2)

# ── 3 · Plate 09 says its name once ───────────────────────────────────────
# "why the duplication of rain on the canopy?" The overlay pill on the film
# and the bar under it both carried the title. The bar is the plate's
# caption (number, title, origin); the pill goes.
fix("""              <div class="vp-rec"><span class="led"></span>Plate 09</div>
              <div class="vp-ov"><span>RAIN ON THE CANOPY · BATANG TORU</span></div>""",
    """              <div class="vp-rec"><span class="led"></span>Plate 09</div>""")

# ── 4 · Ground evidence is in service ─────────────────────────────────────
# "Gayo Lues patrol · not yet in service — it is in service. so change to
# live like the other two layer tiles." Same state, key and status the two
# live layers carry; the rollout sentence goes with the pending state.
fix("""        <article class="ev" data-state="pend" style="--ev-key:#9AAEC2">
          <div class="ev-media">
            <!-- Alex: "ground evidence should be the gayo lues patrol image." It was""",
    """        <article class="ev" data-state="live" style="--ev-key:#D9A441">   <!-- block 105: live -->
          <div class="ev-media">
            <!-- Alex: "ground evidence should be the gayo lues patrol image." It was""")
fix("""            <div class="ev-cap"><span>Gayo Lues patrol · not yet in service</span></div>""",
    """            <div class="ev-cap"><span>Gayo Lues patrol · in service</span></div>""")
fix("""            <div class="ev-t"><span class="lab">Layer 04</span><span class="ls"><span class="led"></span>Rolling out 2026</span></div>
            <h3 class="ev-h">Ground evidence</h3>
            <p class="ev-p">Field photography, camera traps and partner attestation tied back to the same
              polygon IDs. Rolling out through 2026.</p>""",
    """            <div class="ev-t"><span class="lab">Layer 04</span><span class="ls"><span class="led"></span>Live</span></div>
            <h3 class="ev-h">Ground evidence</h3>
            <p class="ev-p">Field photography, camera traps and partner attestation tied back to the same
              polygon IDs.</p>""")

# ── 5 · the dossier's film has its poster back ────────────────────────────
# "the 2-3 step movement of the banner video after selecting 'find out more'
# ... it's jarring." And, once the first pass had touched the choreography:
# "it did have a much smoother and working motion, it's only recently that
# it seems to have a 1-2 step microreadjustment." So the two-beat morph, the
# left-to-right wipe and the landing scroll — the 25 Aug design, which was
# right — are left exactly as they were. What changed recently is block 86
# (2 Sep): it turned every poster= into data-poster=, including the one
# inside this template string, whose video sets its src directly and never
# goes through the hydrate path that would have put the poster back. So the
# frame sat black until the first frame decoded, and the picture then popped
# in: a step that was never part of the design. The poster is set directly
# again, on both copies of the template (shop, and the console's picker).
fix("""'<div class="cx-film-frame"><div class="cx-dv"><video src="'+c.video+'"'+(c.poster?' data-poster="'+c.poster+'"':'')+' muted loop playsinline preload="metadata"></video>""",
    """'<div class="cx-film-frame"><div class="cx-dv"><video src="'+c.video+'"'+(c.poster?' poster="'+c.poster+'"':'')+' muted loop playsinline preload="metadata"></video>""", 2)

io.open(F, "w", encoding="utf-8").write(src)
print("pills hug, plate 09 once, ground evidence live, the film has its poster")
