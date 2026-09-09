import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · hide the ORIGIN CARD, not the row ─────────────────────────────────
subs.append((
"""    if(grid){
      grid.style.transition = 'opacity .13s ease';
      grid.style.opacity = '0';
    }""",
"""    /* ── 1 Sep (final) · THE NEIGHBOURS NEVER DISAPPEAR ────────────────────
       Alex: "the point is the other tiles never disappeared when i selected
       the coffees, here the machines do."

       That sentence settles the spec, and it shows my grid fade was an
       over-correction: blanking all four cards to protect three that were
       never in danger. The geometry says why they never were — the proxy is
       one column wide (321px) and descends inside its own column's x-range;
       the expand begins below the row's bottom edge. The only thing the
       flight can cross is the origin card's own body and the empty strip
       under it.

       So only the ORIGIN goes dark — which is also what makes the card
       "itself" travel — and the other three stay painted from first frame to
       last, exactly like the coffee tiles. The lift-then-drop beat, the
       landed()-only restore, the freeze, the scroll hold and the disabled
       scroll anchoring all stay: they are what keeps the flight honest while
       the row remains on screen. */
    card.style.transition = 'opacity .13s ease';
    card.style.opacity = '0';"""))

# ── 2 · and the origin returns at landed(), with the panel painted ────────
subs.append((
"""      clearTimeout(unhideT);
      /* ── 1 Sep · THE COFFEE INVARIANT, ENFORCED ─────────────────────────
         Alex's recorder on the WORKING coffee flight: rowBottom is 0 on every
         frame — while a proxy exists, the row does not. His recorder on MINE:
         rowOpacity climbing .11 -> 1.0 between t=445 and t=766 while the
         proxy was only 682px of 1320 wide. I was restoring the row at the
         expand beat, so a full-opacity row and a half-expanded proxy shared
         the screen — which is every overlap he photographed. The restore now
         happens HERE, two lines above display:none, and nowhere else: the row
         and the proxy can no longer coexist. */
      if(grid){ grid.style.transition = 'opacity .3s ease'; grid.style.opacity = '1'; }
      setTimeout(unhideCards, 340);""",
"""      clearTimeout(unhideT);
      /* the origin card returns only once the proxy is gone and the real
         panel is painted — the restore lives HERE and nowhere else, which is
         the rule that ended the vanishing-card and overlap bugs alike. */
      card.style.transition = 'opacity .3s ease';
      card.style.opacity = '1';
      setTimeout(unhideCards, 340);"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("origin-only hide; neighbours stay painted")
