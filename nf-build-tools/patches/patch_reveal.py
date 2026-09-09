import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

old = """    var bar  = document.querySelector('.deck-screen.is-active .deck-actions');
    var barH = bar ? bar.getBoundingClientRect().height : 0;"""

new = """    var bar  = document.querySelector('.deck-screen.is-active .deck-actions');
    /* ── 1 Sep · ONLY RESERVE THE BAR IF THE BAR IS THERE ────────────────────
       This reserved 133px at the foot for a sticky action bar that, since the
       panel started standing it down, is not painted while the panel is open.
       getBoundingClientRect still returns its box under visibility:hidden — by
       design, that is what keeps the layout still — so the measurement stayed
       133 and the panel was being scrolled to clear something invisible. On a
       700px screen that is a fifth of the window given to nothing, and it is
       why the foot kept coming up one trim short.
       The bar's height still governs whenever it IS visible, which is every
       other screen in the deck. */
    var barVis = bar && getComputedStyle(bar).visibility !== 'hidden';
    var barH = barVis ? bar.getBoundingClientRect().height : 0;"""

assert src.count(old) == 1, "reveal anchor not unique (%d)" % src.count(old)
io.open(F, "w", encoding="utf-8").write(src.replace(old, new))
print("reveal no longer reserves a hidden bar")
