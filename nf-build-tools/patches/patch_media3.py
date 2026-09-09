import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 120 · LOSSLESS LEFTOVERS FROM THE 7 SEP LIGHTHOUSE PASS ══════════════════
# Alex: "fine to implement them as long as there is no quality loss". Four
# items, none of which changes what a reader sees at full size:
#
# (a) the Batang Gadis sign-off still: the 1600 px master (287 KB) was the only
#     candidate, so a phone downloaded it to paint a 390 px plate. A 1000 px
#     twin (128 KB, same q80 WebP) now sits beside it and the browser picks by
#     slot width. Desktop keeps the 1600 where the screen wants it (2x).
#     The plate also carried the master as an inline background-image behind
#     the <img>; a headless check showed that background fetching the 1600
#     master on every width regardless of srcset, so the srcset alone saved
#     nothing and cost desktop an extra file. The <img> covers the plate
#     (100%/100%, object-fit cover), so the duplicate background goes; the
#     plate keeps .vp-media's black ground while the lazy image arrives.
# ---- srcset: parked 9 Sep 2026 (morning), restored 9 Sep 2026 (afternoon) -----
# batang-gadis-signoff-1000.webp was built 7 Sep but sat only in _CDN-UPLOAD-SAFE;
# the bucket returned 404 and browsers do NOT fall back to another srcset candidate
# when one 404s, so the sign-off photograph would have blanked at 1x desktop.
# Restored once the full folder was verified live: all 301 servable files 200 on
# nofilter-shared.netlify.app (only _headers 404s, which Netlify consumes, never
# serves). Saving: 131 KB instead of 287 KB at every width up to 1000 px.
fix("""                <img src="../../_CDN-UPLOAD-SAFE/batang-gadis-signoff.webp"
                     alt="Komanja growers, PRCF Indonesia and SRI members""",
    """                <img src="../../_CDN-UPLOAD-SAFE/batang-gadis-signoff.webp"
                     srcset="../../_CDN-UPLOAD-SAFE/batang-gadis-signoff-1000.webp 1000w, ../../_CDN-UPLOAD-SAFE/batang-gadis-signoff.webp 1600w"
                     sizes="(max-width:900px) 100vw, 850px"
                     alt="Komanja growers, PRCF Indonesia and SRI members""")
# The duplicate background-image removal below is kept: it needs no new asset
# and was the larger saving, a second 287 KB fetch on every visit at every width.
# ----------------------------------------------------------------------------

fix("""<div class="vp-media" style="background-image:url(../../_CDN-UPLOAD-SAFE/batang-gadis-signoff.webp)">""",
    """<div class="vp-media">""")

# (b) the "this was forest" tape scrawl is a small overlay; the 800 px variant
#     already on the CDN (15 KB) is indistinguishable from the 1200 px master
#     (28 KB) at the size it is ever drawn.
fix("""<img class="scrawl" src="../../_CDN-UPLOAD-SAFE/tape-this-was-forest.webp" """,
    """<img class="scrawl" src="../../_CDN-UPLOAD-SAFE/tape-this-was-forest-w800.webp" """)

# (c) footer copyright line: .36 alpha cream on the black footer sat at ~2.4:1,
#     the one contrast failure Lighthouse flagged that Alex did not choose to
#     keep (the orange buttons stay by his decision). .55 clears 4.5:1 and still
#     reads as the quiet small print it is.
fix("""  line-height:1.7;color:rgba(244,239,226,.36);text-align:left;}""",
    """  line-height:1.7;color:rgba(244,239,226,.55);text-align:left;}""")

# (d) the floating contact button is icon-only, so it had no accessible name;
#     screen readers and agent crawlers announced "button". One attribute.
fix("""<button class="ctc-btn" id="nfCtcBtn" type="button" aria-expanded="false" aria-controls="nfCtcPanel">""",
    """<button class="ctc-btn" id="nfCtcBtn" type="button" aria-label="Contact" aria-expanded="false" aria-controls="nfCtcPanel">""")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_media3 ok")
