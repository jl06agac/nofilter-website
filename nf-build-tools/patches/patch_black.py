import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 100 · THE TRADE ROUTE GOES TO FIELD BLACK ═════════════════════════════
# Alex, 3 Sep: four colour directions for /trade-pricing, mocked up on the
# new pour plate — field black, deep canopy, signal orange, field paper —
# "proceed with the build and black". The argument: the route already turns
# dark at the CRT gate and stays dark through the quote console, so on black
# it is one instrument from the first screen to the sent quote, and the teal
# → black cut at the hand-off (the only place on the site the ground changed
# under a reader mid-task) is gone.
# Values are Alex's spec, mapped onto the route's own selectors — the
# markup, ids and JS are untouched. The house signal orange stays; the
# specified #f04c1a was a second orange. Not flat: the faint deep-canopy
# radial wash behind the plate is the difference between this and "#111",
# and the route's own history (forest → teal, above) says a flat dark went
# dull. The wash is a sized background layer, not a pseudo-element, so no
# stacking context is added to the route. His grain layer is left out — a
# 5px dot field shimmers on a Retina panel during scroll, and this route was
# just cleared of everything that shimmers.
# Inputs: a hairline on the ground, orange on focus with a halo that fades
# in once and holds (a focus is a state, not an event — no pulse), still
# under prefers-reduced-motion.
fix("""#quote{background:#1F6F6B;--dim:#DCE9E0}""",
    """/* field black, 3 Sep (block 100). Was teal #1F6F6B. The wash is sized to the
   first screen so it sits behind the plate, not a third of the way down the
   whole route. */
#quote{background:radial-gradient(circle at 76% 44%,rgba(26,55,46,.24) 0%,rgba(18,35,30,.09) 24%,transparent 48%) 0 0/100% 100vh no-repeat,#0c0e0d;
  --dim:#a8ada6}""")
fix("""#quote .acc-f input{background:rgba(6,32,30,.66);border-color:rgba(255,255,255,.40);color:#F4F2EE}
#quote .acc-f input:hover{border-color:rgba(255,255,255,.62)}
#quote .acc-f input::placeholder{color:#9FB6B2}
#quote .readout{background:rgba(6,32,30,.55)}""",
    """#quote .acc-f input{background:#111816;border-color:#343a36;color:#F4F2EE;
  transition:border-color .15s ease,box-shadow .25s ease}
#quote .acc-f input:hover{border-color:#4a514c}
#quote .acc-f input::placeholder{color:#7d847e}
#quote .acc-f input:focus{border-color:var(--signal);box-shadow:0 0 0 3px rgba(238,77,23,.16)}
@media (prefers-reduced-motion:reduce){#quote .acc-f input{transition:none}}
#quote .readout{background:#343a36;border-color:#343a36}
#quote .readout .ro{background:#101311}
#quote .readout .ro .k{color:#8f9690}""")

# The gate room follows the page. 25 Aug made it teal so "the gate reads as
# the same room as the page that opened it" — that reasoning holds, the room
# has changed: black, lit from behind the monitor with the same deep-canopy
# light as the wash, falling to the page's ground at the edges. gate-off
# still cuts to #000. The refusal panel (.acc-err) was a darkening of teal;
# on black it takes the input panel's own surface so it still reads as a
# panel.
fix("""  background:radial-gradient(120% 120% at 50% 40%,#27837E 0%,#1F6F6B 52%,#0E3B38 100%);
  transition:background .45s ease}""",
    """  background:radial-gradient(120% 120% at 50% 40%,#1E4A3C 0%,#122A22 48%,#0c0e0d 100%);   /* block 100: was the teal room */
  transition:background .45s ease}""")
fix("""  margin:14px 0 0;padding:11px 14px;background:rgba(0,0,0,.28);
  border-left:3px solid var(--signal);border-radius:2px}""",
    """  margin:14px 0 0;padding:11px 14px;background:#111816;border:1px solid #343a36;   /* block 100 */
  border-left:3px solid var(--signal);border-radius:2px}""")

io.open(F, "w", encoding="utf-8").write(src)
print("the trade route is field black")
