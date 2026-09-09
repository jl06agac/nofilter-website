import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 107 · THE RAIL ONLY SLIMS ON HOME — BY ROUTE, NOT BY HASH ══════════════
# Alex, 3 Sep, on the shop dossier: "it did have a much smoother and working
# motion, it's only recently that it seems to have a 1-2 step
# microreadjustment." His console trace, and a local repeat of it, show the
# steps: at landing the page's scroll snaps to 0, then the dossier hops a
# further 47px, then a smooth scroll runs short and a second one finishes it.
# The 47px is the telemetry rail slimming (104 → 56, .shell padding with it),
# and the short scroll is a target measured against a rail that then changed
# height under it.
# The rail is only meant to slim on home — over the cover, while the headline
# moves (19 Aug). Its test was `location.hash === ''`. Until block 88 every
# route was a hash, so an empty hash meant home; since block 88 the routes are
# paths and the hash is empty on every page, so /shop, /origins and the rest
# have been running home's slim/expand logic — and its 48px scroll
# compensation — around a threshold measured off a cover that is not even
# displayed there. The test is the route now.
fix("""    var onHome=(location.hash==='' || location.hash==='#home' || location.hash==='#');""",
    """    var onHome = window.__nfRoute ? (window.__nfRoute === 'home')
               : (location.hash==='' || location.hash==='#home' || location.hash==='#');   /* block 107 */""")

io.open(F, "w", encoding="utf-8").write(src)
print("the rail slims on home only")
