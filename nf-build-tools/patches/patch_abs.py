import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the morph is ABSOLUTE inside the deck, in content coordinates ─────
subs.append((
"""    if(morph.parentNode !== host) host.appendChild(morph);
    return morph;""",
"""    if(morph.parentNode !== host) host.appendChild(morph);
    /* ── 1 Sep · ABSOLUTE, NOT FIXED, INSIDE THE DECK ─────────────────────
       Measured on a 1512px window: the proxy took off at x 660-981 while its
       own card sat at 710-1031 — fifty pixels out, straddling the neighbour.
       The deck carries a live transform (an entrance settle at scale
       0.999754 that never quite reaches 1), and a transformed ancestor
       becomes the containing block for position:fixed descendants — so the
       morph's "fixed" coordinates stopped being viewport pixels the moment I
       parented it in here. The file WARNED about this: the original .cx-morph
       is parked on <body> with a comment saying an ancestor's transform is
       exactly why. I moved it inside for CSS scoping and walked past the
       warning.
       The scoping is still wanted, so instead of moving back out, the morph
       stops pretending: position:absolute, coordinates in the deck's own
       scrolled content space (viewport + scrollTop, taken while the page is
       frozen). As content, it also scrolls WITH the deck by construction —
       which retires the entire fixed-vs-scroll family of races for good. */
    morph.style.position = (host === document.body) ? 'fixed' : 'absolute';
    return morph;"""))

# ── 2 · take-off in content coordinates ───────────────────────────────────
subs.append((
"""    mo.style.left = f.left + 'px'; mo.style.top = f.top + 'px';""",
"""    /* content space: viewport coordinates plus the deck's scroll, which the
       freeze above has pinned for the duration of the flight */
    var __sx = fsFreeze ? fsFreeze.scrollLeft : 0;
    var __sy = fsFreeze ? fsFreeze.scrollTop  : 0;
    mo.style.left = (f.left + __sx) + 'px'; mo.style.top = (f.top + __sy) + 'px';"""))

# ── 3 · descent and expand targets likewise ───────────────────────────────
subs.append((
"""      mo.style.top = l.top + 'px';
    }, 150);""",
"""      mo.style.top = (l.top + __sy) + 'px';
    }, 150);"""))

subs.append((
"""        mo.style.left = l.left + 'px'; mo.style.width = l.width + 'px';""",
"""        mo.style.left = (l.left + __sx) + 'px'; mo.style.width = l.width + 'px';"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("morph absolute in deck content space")
