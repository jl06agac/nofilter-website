import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ═══ A · the cover rungs top-align ════════════════════════════════════════
# (CSS appended below — nothing to swap here)

# ═══ B · the "no cover" escape hatch says what it is ══════════════════════
subs.append((
"""          '<div><p class="nfbd-sect">Choose how long it is covered' +
            (on ? ' &middot; <button type="button" data-nfbd-yrs="0" style="background:none;border:none;color:inherit;font:inherit;text-decoration:underline;cursor:pointer;padding:0">no cover</button>' : '') +
            '</p><div class="nfbd-covs">' + rung(1) + rung(2) + rung(3) + '</div></div>' +""",
"""          /* 1 Sep — Alex: "what's the cover message about?" Fair, and the
             answer is that it was badly built. This is the escape hatch for
             declining servicing altogether, which has to exist: the quote's
             like-for-like logic counts a missing plan as a gap and refuses to
             print a saving while one is open, so a buyer must be able to say
             no. But it was set in the same mono, the same size and the same
             line as the SECTION HEADING, separated by a middle dot — so it read
             as a second half of the label rather than as something you could
             press, and "no cover" on its own states a condition rather than
             offering an action. It is now on the right of the header row, in
             its own weight, and it says what pressing it does. */
          '<div><div class="nfbd-secthd"><p class="nfbd-sect">Choose how long it is covered</p>' +
            (on ? '<button type="button" class="nfbd-decline" data-nfbd-yrs="0">Decline cover</button>' : '') +
            '</div><div class="nfbd-covs">' + rung(1) + rung(2) + rung(3) + '</div></div>' +"""))

# ═══ C · the CRT retime — REVERTED 1 Sep ═════════════════════════════════
# Alex: "your CRT has that same problem as before now, revert to what we had
# prior this change which was better."
#
# Reverted whole. The retime was measured and the numbers were right on their
# own terms — 1.8s of dead black removed, the console's entrance made visible —
# but it reintroduced the exact fault pass56 recorded and that I quoted while
# arguing it could not recur: the CRT and the page fighting each other during
# the handoff. My reasoning was that the stage reached 0 before the lift began,
# and the DOM samples agreed. They were measuring opacity, which is not what he
# is looking at: the .crt-poweroff overlay and the dot are still on screen, and
# once the gate starts lifting at 380ms the page beneath is coming up through
# all of it. Faster made the collision more visible, not less.
#
# The old numbers (1400 / 2050, .7s stage, .95s gate, 900ms hold, 980ms hide)
# are slow precisely BECAUSE they keep those layers apart. That is what they
# were bought with, and I traded it away for tempo without understanding what I
# was spending. Left exactly as it was; if the pacing is worth revisiting it
# needs a different approach than compressing this one.

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = r'''
/* ── 26 · COVER RUNG ALIGNMENT AND THE DECLINE CONTROL ────────────────────
   Alex, 1 Sep: "the lines, $ amount, year, should be on same line, look at
   year 1."

   He is right and the cause is a default I walked into. .nfbd-cov is a
   <button>, and a button vertically CENTRES its content box — so the 1-year
   rung, which carries two bullets where the others carry three, floated its
   whole block down inside a grid cell stretched to the tallest sibling.
   Measured: its "1 YEAR" line sat 19px below the other two, and its rule and
   its price with it. Nothing was wrong with the type; the box was centring it.

   A button that is really a card has to be told to behave like one. */
#nfConsoleWrap .nfbd-cov{
  display:flex;flex-direction:column;align-items:stretch;justify-content:flex-start;
}

/* the section header is a row now, so the decline control can sit at its right
   edge instead of trailing the heading like a second half of the label */
#nfConsoleWrap .nfbd-secthd{
  display:flex;align-items:baseline;justify-content:space-between;gap:14px;margin:0 0 10px;
}
#nfConsoleWrap .nfbd-secthd .nfbd-sect{margin:0;}
#nfConsoleWrap .nfbd-decline{
  font-family:var(--body,sans-serif);font-size:11.5px;font-weight:500;
  background:none;border:0;padding:0;cursor:pointer;white-space:nowrap;
  color:rgba(255,232,195,.7);
  border-bottom:1px solid rgba(255,232,195,.35);
  transition:color .15s ease,border-color .15s ease;
}
#nfConsoleWrap .nfbd-decline:hover{color:#F4F2EE;border-color:#F4F2EE;}
#nfConsoleWrap .nfbd-decline:focus-visible{outline:2px solid var(--or,#ed3326);outline-offset:3px;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("cover alignment + decline control + CRT retime applied")
