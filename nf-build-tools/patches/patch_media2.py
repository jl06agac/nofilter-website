import io, sys, re
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 118 · LIGHTER MEDIA, SAME PICTURES (7 Sep, from the Lighthouse run) ═════
# 1 · The hero's two duotone glitch layers (cyan / red) each streamed their own
#     3.2 MB copy of hero-trim-fast.mp4 — 9.5 MB of a 13.6 MB home page for one
#     film. They are visible for 0.6 s at ≤32% opacity, sliced and jittered, and
#     they were never time-synced to the main layer (they play from wherever
#     they paused). A 360p CRF-33 encode of the same clip (610 KB) is
#     indistinguishable in that role. The main layer keeps the full file.
fix("""    <video class="cover-video cover-video--cyan" aria-hidden="true" muted loop playsinline preload="metadata">
      <source data-src="hero-trim-fast.mp4" type="video/mp4">""",
    """    <video class="cover-video cover-video--cyan" aria-hidden="true" muted loop playsinline preload="metadata">
      <source data-src="hero-trim-fast-lo.mp4" type="video/mp4">""")
fix("""    <video class="cover-video cover-video--red" aria-hidden="true" muted loop playsinline preload="metadata">
      <source data-src="hero-trim-fast.mp4" type="video/mp4">""",
    """    <video class="cover-video cover-video--red" aria-hidden="true" muted loop playsinline preload="metadata">
      <source data-src="hero-trim-fast-lo.mp4" type="video/mp4">""")

# 2 · JPEG/PNG -> WebP at the SAME pixel dimensions. Photos at q80 (no visible
#     change); the four PNG logos lossless. New files beside the originals in
#     _CDN-UPLOAD-SAFE; nothing on the shared CDN is overwritten. Two candidates
#     were tried and rejected because WebP came out no smaller (mono-coffee-
#     poster, atwork-rain-poster): the footage is grain-heavy.
SWAPS = {
  "batang-gadis-signoff.jpg":        ("batang-gadis-signoff.webp",        3),   # 360 -> 280 KB
  "verify-drone-poster.jpg":         ("verify-drone-poster.webp",         2),   # 316 -> 261
  "batang-toru-banner-poster.jpg":   ("batang-toru-banner-poster.webp",   2),   # 217 -> 194
  "batang-gadis-banner-poster.jpg":  ("batang-gadis-banner-poster.webp",  1),   # 178 -> 154
  "batang-arakan-banner-poster.jpg": ("batang-arakan-banner-poster.webp", 2),   #  72 ->  49
  "gayo-lues-banner-poster.jpg":     ("gayo-lues-banner-poster.webp",     1),   #  71 ->  52
  "orangutan-batang-toru.jpg":       ("orangutan-batang-toru.webp",       2),   # 268 -> 109
  "wp-pour-poster.jpg":              ("wp-pour-poster.webp",              2),   #  86 ->  57
  "ngo-kub.png":                     ("ngo-kub.webp",                     2),   # 191 -> 100 lossless
  "ngo-acca.png":                    ("ngo-acca.webp",                    2),   #  54 ->  23
  "ngo-prcf.png":                    ("ngo-prcf.webp",                    2),   #  30 ->  12
  "ngo-ff.png":                      ("ngo-ff.webp",                      2),   #  25 ->  11
}
for old, (new, n) in SWAPS.items():
    fix(old, new, n)

io.open(F, "w", encoding="utf-8").write(src)
print("patch_media2 OK: hero overlays -> -lo, %d image names -> webp" % len(SWAPS))
