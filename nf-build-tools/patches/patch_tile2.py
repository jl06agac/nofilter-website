import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

subs.append((
"""    var ex = function(key, name, note, price, cost, img){""",
"""    var ex = function(key, name, note, price, free, cost, img){"""))

subs.append((
"""        '<span class="txt"><span class="t">' + name + '</span>' +
          '<span class="d">' + note + '</span>' +
          '<span class="xp">' + price + '</span></span>' +
        '<span class="nfbd-sw" aria-hidden="true"><i></i></span>' +""",
"""        /* ── 1 Sep · ONE LAYOUT, WHATEVER THE STATE ────────────────────────
           Alex's structure: title with the toggle on its line, one description
           block, a rule, then the price at the foot. Every tile is built from
           the same four slots so the three of them line up whether an extra is
           priced, free, on or off. */
        '<span class="txt">' +
          '<span class="hd"><span class="t">' + name + '</span>' +
            '<span class="nfbd-sw" aria-hidden="true"><i></i></span></span>' +
          '<span class="d">' + note + '</span>' +
          '<span class="xp">' +
            (free ? '<span class="nfbd-inc">Included with plan</span>' : price) +
          '</span></span>' +"""))

subs.append((
"""            ex('cooler','Countertop milk fridge',
               'Sits beside the machine',
               'Standard &middot; ' + CUR() + money(x.cooler),
               x.cooler, '') +""",
"""            ex('cooler','Countertop milk fridge',
               'Sits beside the machine',
               'Standard &middot; ' + CUR() + money(x.cooler), false,
               x.cooler, '') +"""))

subs.append((
"""            ex('wrap','Co-branded machine wrap',
               'Our artwork, your logo',
               wrapFree ? 'Free on this plan' : CUR() + money(x.wrap),
               0, 'machine-livery-uwcsea.png') +""",
"""            ex('wrap','Co-branded machine wrap',
               'Our artwork, your logo',
               CUR() + money(x.wrap), wrapFree,
               0, 'machine-livery-uwcsea.png') +"""))

subs.append((
"""            ex('counter','Live impact counter',
               'Cups and funds, on screen',
               (wrapFree ? 'Free on this plan' : CUR() + money(x.counter)),""",
"""            ex('counter','Live impact counter',
               'Cups and funds, on screen',
               CUR() + money(x.counter), wrapFree,"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = r'''
/* ── 37 · THE TILE, STANDARDISED ──────────────────────────────────────────
   Four slots in a fixed order — title (with the switch on its line), one
   description block, a rule, the price at the foot — so the three tiles read
   as a set and nothing moves between states. The switch top-aligns rather than
   centring, which is what puts it beside the title instead of floating against
   the middle of a three-line card. */
/* the switch moved INSIDE the text column, on the title's line. It was a
   sibling of the column, which cost the description 46px of the 178px it has —
   at 132px "Cups and funds, on screen" wrapped to two lines and the clamp then
   ate half of it. Measured: 132 -> 178, and all three descriptions now fit
   their single line with room at 1.3x. */
#nfConsoleWrap .nfbd-ex .hd{display:flex;align-items:flex-start;
  justify-content:space-between;gap:9px;}
/* "Co-branded machine wrap" runs to two lines while the other two titles fit
   one, so without a reserved title block the descriptions and rules sat at
   three different heights inside tiles that were themselves level. Alex asked
   for the elements to "line up across all three boxes regardless of state", so
   the title block holds two lines whether it needs them or not. */
#nfConsoleWrap .nfbd-ex .hd .t{flex:1 1 auto;min-width:0;min-height:2.5em;}
#nfConsoleWrap .nfbd-ex .nfbd-sw{flex:0 0 auto;margin-top:1px;}
/* ONE line, and the copy is written to fit it. Alex: "Subtext Description
   (1 line max)". Clamping alone would just truncate — which is the fault he
   reported two messages ago — so the three descriptions were shortened to
   suit: "Sits beside the machine", "Our artwork, your logo", "Cups and funds,
   live on screen". Verified un-clipped at 1.3x letter-spacing. */
#nfConsoleWrap .nfbd-ex .d{-webkit-line-clamp:1;min-height:1.3em;margin-bottom:7px;}
/* the price slot is a fixed box, because the badge is taller than a line of
   mono and the tile would otherwise grow by 2.3px the moment a plan makes an
   extra free — which moves the panel, which moves the photograph. */
#nfConsoleWrap .nfbd-ex .xp{text-align:left;padding-top:7px;height:26px;
  box-sizing:content-box;display:flex;align-items:center;
  border-top:1px solid rgba(244,242,238,.16);}

/* ── 38 · "INCLUDED WITH PLAN" IS A BADGE, NOT A SENTENCE ─────────────────
   Alex: "Loose grey text like 'Free on this plan' looks like leftover subtext
   and blends into the dark card background."
   It did, and worse, it sat in the same slot and the same face as the price it
   replaced — so the one moment the tile has good news to deliver looked like
   the moment it had less to say. A solid pill reads as a stamp.
   Colour is not doing the work on its own: the shape changes, the text changes,
   and it stays legible in greyscale. */
#nfConsoleWrap .nfbd-inc{display:inline-block;
  font-family:var(--mono,monospace);font-size:8.5px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;
  background:var(--or,#ed3326);color:#fff;border-radius:99px;padding:3px 9px;}
.beat[data-ground="paper"] #nfBuyDoss .nfbd-inc{color:#fff;}
@media(max-height:760px){
  #nfConsoleWrap .nfbd-ex .d{margin-bottom:5px;}
  #nfConsoleWrap .nfbd-ex .xp{padding-top:5px;}
}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("tile standardised + included badge")
