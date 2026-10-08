import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 125 · CAFÉMATIC MOCK-UPS, CURRENT WRAP (8 Oct 2026) ═══════════════════════
# Alex: "Update the NoFilter website's Cafematic machine images using these
# existing mockups … for the quote builder section primarily where we have the
# cafematics listed." The July renders (black machine, orange lower panel, old
# wordmark) go; the 6 Oct Codex renders of the current wrap (oversized plus,
# parchment tear, greyscale forest, orange fascia) come in. Same 1254x1254
# frame on the same cream ground, so every square well they sit in is
# unchanged. NEW filenames, not overwrites: the CDN caches by name, and the old
# files are still referenced by client pitches off the shared folder.
#   cafematic-2-v4-w1254.webp   CaféMatic 2
#   cafematic-5-v4-w1254.webp   CaféMatic 5, corrected powder hopper
#   cafematic-6-v4-w1254.webp   CaféMatic 6
#   cafematic-8-v4-w1254.webp   CaféMatic 8   (+ cafematic-8-v4.jpg, the <picture> fallback)
#   cafematic-angle-fridge-w1536.webp   angled machine with the branded milk fridge (uploaded, not yet placed — see 4)
# Copy, specs and prices are untouched.

# 1 · the quote builder's machine cards, dossier and purchase panel all read m.img
for k in ('2', '5', '6', '8'):
    fix("img:'../../_CDN-UPLOAD-SAFE/cafematic-%s-w1400.webp' }" % k,
        "img:'../../_CDN-UPLOAD-SAFE/cafematic-%s-v4-w1254.webp' }" % k)

# 2 · the specs sheet's fallback photo (SG/AE, where the market has not swapped the machine)
fix("              : '../../_CDN-UPLOAD-SAFE/cafematic-'+SLUG[machine].slice(2)+'.png';",
    "              : '../../_CDN-UPLOAD-SAFE/cafematic-'+SLUG[machine].slice(2)+'-v4-w1254.webp';   /* 125 */")

# 3 · wholesale "on-site proof": the CaféMatic 8 that swaps with the turning bag
fix("""            <source srcset="../../_CDN-UPLOAD-SAFE/cafematic-8-w1400.webp" type="image/webp">
            <img class="nw-sw is-on" src="../../_CDN-UPLOAD-SAFE/cafematic-8.png\"""",
    """            <!-- 125 (8 Oct): current-wrap render; JPEG fallback instead of the 1.49 MB PNG. -->
            <source srcset="../../_CDN-UPLOAD-SAFE/cafematic-8-v4-w1254.webp" type="image/webp">
            <img class="nw-sw is-on" src="../../_CDN-UPLOAD-SAFE/cafematic-8-v4.jpg\"""")

# 4 · NOT the "03 · the unit" film. That slot is a tall portrait well (499x1106 on
#     desktop, 270x456 on a phone; the stock photo it holds was chosen at 422x750 for
#     it), and the angled machine-and-fridge render is 3:2. It cannot sit there without
#     either cropping the fridge away or letterboxing a counter scene above and below.
#     Tried 8 Oct with aspect-ratio:3/2 + contain; the figure then sized itself off the
#     row height and overflowed its column to 1659px. Reverted; unit-machine.jpg stays
#     until a slot the render fits is chosen. cafematic-angle-fridge-w1536.webp is on
#     the CDN ready for that.

# 5 · comments that name the old files, so the next reader is not sent to the wrong asset
fix("   (cafematic-*-w1400.webp) are product photography on a cream ground of",
    "   (cafematic-*-v4-w1254.webp) are product photography on a cream ground of")
fix("     '../../_CDN-UPLOAD-SAFE/cafematic-6-w1400.webp'. */",
    "     '../../_CDN-UPLOAD-SAFE/cafematic-6-v4-w1254.webp'. */")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_machimg OK")
