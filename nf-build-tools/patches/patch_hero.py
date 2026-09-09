import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 61 · THE HERO STOPS DOING THE CARD'S JOB ──────────────────────────────
# Alex: "The top number is a hero anchor for quick scanning, not an explanatory
# box. Repeating the entire math formula in tiny, illegible monospaced text
# directly above a card that already breaks down Base + Top-Up = Total adds
# cognitive overload right where the user expects clarity."
#
# He is right, and it was my line. The card below states the split properly now,
# so the hero restating it was the same accounting twice, the second time in
# 9px mono across three wrapped lines. One line each.
old = """  set('qHeroCoffee', invoiced.toFixed(2));
  set('qHeroCoffeeNote', CUR() + base.toFixed(2) + ' base'
      + (hasTop ? ' + ' + CUR() + topKg.toFixed(2) + ' voluntary top-up' : '')
      + ' · ' + CUR() + ngoKg.toFixed(2) + '/kg passed to NGOs');"""
new = """  set('qHeroCoffee', invoiced.toFixed(2));
  set('qHeroCoffeeNote', 'Total invoiced coffee rate');"""
assert src.count(old) == 1, "hero coffee anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# and the equipment line loses its run-on. A purchase keeps its one-time figure,
# because that is the number a finance reader is looking for and it appears
# nowhere else in the hero — but it is a clause now, not a sentence.
old = """  set('qHeroEquipNote', c.capex > 0
      ? ('plus ' + CUR() + money(c.capex) + ' one-time · machine, cooler, install & servicing plan')
      : (c.units
          ? (window.__nfLeaseTerm || 36) + '-month lease · includes milk fridge, servicing, wrap & impact screen'
          : 'our leasing partner · cooler, install, servicing, wrap & counter included'));"""
new = """  set('qHeroEquipNote', c.capex > 0
      ? ('plus ' + CUR() + money(c.capex) + ' one-time')
      : (c.units
          ? (window.__nfLeaseTerm || 36) + '-month equipment lease'
          : 'Via our leasing partner'));"""
assert src.count(old) == 1, "hero equip anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* the note is one line now, so it can carry the off-white the rest of the card
   uses rather than the dim it needed when it was a paragraph */
.q-settle .q-total-note{color:#CCCCCC;white-space:nowrap;}
'''

# ── 62 · A HAIR OF SCROLL IS ALWAYS WORTH A PASS ──────────────────────────
# Alex: "once again i can scroll a bit in 1 and 2."
#
# I cannot reproduce it — steps 0-2 measure zero overflow at fifteen window
# sizes from 1280x800 to 2000x1250 — which means the cause is a timing I am not
# hitting rather than a layout I can see. So this stops relying on my being able
# to see it.
#
# Block 55 made fill() return early when its signature is unchanged, to kill a
# periodic relayout that was costing frames. The signature is the deck's client
# height and the active screen's own height, and there is a gap in it: if
# anything grows the CONTENT after the pass has run — a late image, a font swap,
# a reflow at a width the screen was not measured at — the screen can end up
# overflowing while both of those numbers stay put, and the early return then
# refuses to correct it forever. Before block 55 the 1.2s pass caught it by
# brute force.
#
# So the memo now yields to the one condition it must never win against: if the
# deck is scrollable by less than a step's worth, the pass runs, whatever the
# signature says. That is precisely the state the squeeze exists to remove, and
# it can only be entered by the drift the signature cannot see. Anything larger
# is real content and is left alone, so the periodic relayout stays dead for the
# case block 55 was about.
old = """        var sig = f.clientHeight + '|' + (act0 ? act0.offsetHeight : -1);
        if(act0 === lastFilled && sig === lastSig) return;"""
new = """        var sig = f.clientHeight + '|' + (act0 ? act0.offsetHeight : -1);
        var hair = f.scrollHeight - f.clientHeight;      /* block 62 */
        if(act0 === lastFilled && sig === lastSig && !(hair > 0 && hair <= 56)) return;"""
assert src.count(old) == 1, "sig anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("hero trimmed; hair-scroll always corrected")
