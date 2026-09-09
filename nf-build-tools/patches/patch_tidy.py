import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the extras tile: description and PRICE are two different things ───
subs.append((
"""    var ex = function(key, name, note, cost, img){
      var lit = !!cfg[key];
      return '<button type="button" class="nfbd-ex' + (lit ? ' is-on' : '') + '" data-nfbd-x="' + key + '"' +
        ' aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (img ? '<span class="nfbd-th"><img src="' + ASSET + img + '" alt="" loading="lazy" onerror="this.style.display=\\'none\\'"></span>'
             : '<span class="nfbd-th is-todo" aria-hidden="true"></span>') +
        '<span class="txt"><span class="t">' + name + '</span><span class="d">' + note + '</span></span>' +
        '<span class="nfbd-sw" aria-hidden="true"><i></i></span>' +
      '</button>';
    };""",
"""    /* ── 1 Sep · THE PRICE IS NOT PART OF THE SENTENCE ────────────────────
       Alex: "The middle hardware card's subtext is cutting off its price tag
       ('Signature NoFilter artwork with your logo - SGD...')."

       It was, and the cause is that the description and the price were one
       string. I clamp that line to two rows so the tile keeps a fixed height —
       necessary, because a tile that grows when the copy changes moves the
       whole panel — and the clamp cut wherever the text happened to run out.
       With the price welded to the end of the sentence, the price is what got
       cut. The one thing on the tile that must never be ambiguous.

       So `note` is now the description ALONE and the price is its own element
       on its own line, right-aligned under the switch. The description clamps;
       the price cannot, because nothing else shares its line. */
    var ex = function(key, name, note, price, cost, img){
      var lit = !!cfg[key];
      return '<button type="button" class="nfbd-ex' + (lit ? ' is-on' : '') + '" data-nfbd-x="' + key + '"' +
        ' aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (img ? '<span class="nfbd-th"><img src="' + ASSET + img + '" alt="" loading="lazy" onerror="this.style.display=\\'none\\'"></span>'
             : '<span class="nfbd-th is-todo" aria-hidden="true"></span>') +
        '<span class="txt"><span class="t">' + name + '</span>' +
          '<span class="d">' + note + '</span>' +
          '<span class="xp">' + price + '</span></span>' +
        '<span class="nfbd-sw" aria-hidden="true"><i></i></span>' +
      '</button>';
    };"""))

subs.append((
"""            ex('cooler','Countertop milk fridge',
               (cfg.cooler ? 'Standard' : 'Undercounter') + ' &middot; ' + CUR() + money(x.cooler),
               x.cooler, '') +""",
"""            ex('cooler','Countertop milk fridge',
               'Sits beside the machine',
               'Standard &middot; ' + CUR() + money(x.cooler),
               x.cooler, '') +"""))

subs.append((
"""            ex('wrap','Co-branded machine wrap',
               wrapFree ? 'Free on this plan'
                        : 'Signature NoFilter artwork with your logo &middot; ' + CUR() + money(x.wrap),
               0, 'machine-livery-uwcsea.png') +""",
"""            ex('wrap','Co-branded machine wrap',
               'Our artwork, your logo',
               wrapFree ? 'Free on this plan' : CUR() + money(x.wrap),
               0, 'machine-livery-uwcsea.png') +"""))

subs.append((
"""            ex('counter','Live impact counter',
               (wrapFree ? 'Free on this plan' : 'Cups &amp; funds &middot; ' + CUR() + money(x.counter)),""",
"""            ex('counter','Live impact counter',
               'Cups and funds, on screen',
               (wrapFree ? 'Free on this plan' : CUR() + money(x.counter)),"""))

# ── 2 · Remove from quote goes back to the header ─────────────────────────
subs.append((
"""            '<div class="nfbd-qrow"><div class="nfbd-qty">' +
                '<button type="button" data-nfbd-q="-1" aria-label="' +
                  (q <= 1 ? 'Remove ' + m.name + ' from the quote' : 'One fewer ' + m.name) + '">&minus;</button>' +
                '<b>' + q + '</b>' +
                '<button type="button" data-nfbd-q="1" aria-label="One more ' + m.name + '">+</button>' +
              '</div><span class="nfbd-qnote">' +
              (q === 1 ? '1 machine' : q + ' machines, same spec') + '</span>' +
              /* an explicit way out, because a stepper that reaches zero is not
                 discoverable — you have to press minus and hope. This says it. */
              '<button type="button" class="nfbd-remove" data-nfbd-remove>Remove from quote</button>' +
              '</div>' +""",
"""            /* ── 1 Sep · STEP 3 KEEPS ONLY WHAT MOVES THE SALE ON ───────────
               Alex: "The bottom row is overloaded with competing elements ...
               Keep Step 3 strictly focused on positive conversion (Price + Qty
               + CTA)."
               Right — five things were sharing that row and one of them was the
               destructive one, sitting between the reader and the button they
               came to press. Price, quantity, CTA stay. "Remove from quote"
               moves to the sheet's top-right, the slot the old CLOSE vacated:
               present, findable, and nowhere near the primary action. */
            '<div class="nfbd-qrow"><div class="nfbd-qty">' +
                '<button type="button" data-nfbd-q="-1" aria-label="' +
                  (q <= 1 ? 'Remove ' + m.name + ' from the quote' : 'One fewer ' + m.name) + '">&minus;</button>' +
                '<b>' + q + '</b>' +
                '<button type="button" data-nfbd-q="1" aria-label="One more ' + m.name + '">+</button>' +
              '</div><span class="nfbd-qnote">' +
              (q === 1 ? '1 machine' : q + ' machines, same spec') + '</span>' +
              '</div>' +"""))

subs.append((
"""    doss.innerHTML =
    '<div class="nfbd-sheet">' +""",
"""    doss.innerHTML =
    '<div class="nfbd-sheet">' +
      /* the way out of a configured machine — quiet, cornered, and deliberately
         not adjacent to anything green-lit. It is still the only affordance
         that says what pressing minus at 1 would do, so it has to be visible. */
      '<button type="button" class="nfbd-remove" data-nfbd-remove>Remove from quote</button>' +"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = r'''
/* ── 33 · THE EXTRAS TILE, THREE PARTS ────────────────────────────────────
   name / description (clamped to three rows, so the tile height never moves
   whatever the copy says) / price on its own line. The price is right-aligned under the switch because
   that is where the eye already is when it reaches for the toggle, and because
   a right edge is the one place a number cannot be mistaken for the end of a
   sentence. */
#nfConsoleWrap .nfbd-ex{align-items:flex-start;padding:9px 11px 9px 8px;}
#nfConsoleWrap .nfbd-th{margin-top:1px;}
#nfConsoleWrap .nfbd-ex .txt{display:flex;flex-direction:column;}
#nfConsoleWrap .nfbd-ex .d{margin-bottom:5px;}
#nfConsoleWrap .nfbd-ex .xp{display:block;text-align:right;
  font-family:var(--mono,monospace);font-size:11px;letter-spacing:.03em;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}

/* ── THE COLOURS, STATED AGAINST THE PAPER GROUND ─────────────────────────
   Two faults caught by reading the computed colour rather than the render:

   1 · block 30's brightening never took. .beat[data-ground="paper"] restates
       .nfbd-ex .d at 65% cream, and an attribute selector plus an id beats a
       plain #nfConsoleWrap chain. Exactly the repaint trap this file already
       documents twice. So the paper selector is restated here, later, rather
       than argued with.

   2 · I had .is-on invert .d and .xp to ink — copied from the cover rungs,
       where the lit state really does go cream-on-ink. The extras tile does
       NOT: .nfbd-ex.is-on only lifts its background to rgba(244,242,238,.1),
       which is still almost black. Ink on that is invisible, and it was the
       PRICE. Same mistake I made on .mx-cfg last week, same cause: assuming
       two components share a lit state because they share a shape.
   Both states are cream, because both grounds are dark. */
.beat[data-ground="paper"] #nfBuyDoss .nfbd-ex .d,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-ex.is-on .d,
#nfConsoleWrap .nfbd-ex .d,
#nfConsoleWrap .nfbd-ex.is-on .d{color:rgba(255,246,232,.9);}
.beat[data-ground="paper"] #nfBuyDoss .nfbd-ex .xp,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-ex.is-on .xp,
#nfConsoleWrap .nfbd-ex .xp,
#nfConsoleWrap .nfbd-ex.is-on .xp{color:#F4F2EE;}
/* three lines, not two. At this width "Signature NoFilter artwork with your
   logo" needs a third row and was being cut — which is the truncation Alex
   reported, just moved off the price and onto the sentence. The box is fixed
   at three so every tile stays the same height whatever its copy says. */
#nfConsoleWrap .nfbd-ex .d{-webkit-line-clamp:3;min-height:3.9em;}
/* the switch keeps its own vertical centre against the whole tile */
#nfConsoleWrap .nfbd-ex .nfbd-sw{align-self:center;}
@media(max-height:860px){
  #nfConsoleWrap .nfbd-ex .d{margin-bottom:3px;}
}
/* the third description line costs 12px a tile and the 700px case had only 4px
   of headroom left. Taken back from the tile's own padding and the row's gap
   rather than from the copy — the truncation Alex reported is the thing being
   fixed here, so shortening the text at small sizes would just move it. */
@media(max-height:760px){
  #nfConsoleWrap .nfbd-ex{padding:7px 10px 7px 7px;}
  #nfConsoleWrap .nfbd-ex .d{margin-bottom:2px;}
  #nfConsoleWrap .nfbd-ex .t{margin-bottom:1px;}
}

/* ── 34 · REMOVE, IN THE CORNER ───────────────────────────────────────────
   Absolute at the sheet's top-right — the slot the old CLOSE button used, so
   nothing new is competing for space. Underlined rather than boxed: it is a
   destructive action and should read as a link you have to mean to press, not
   as a peer of the two buttons that move the quote forward. */
#nfConsoleWrap .nfbd-sheet{position:relative;}
#nfConsoleWrap .nfbd-remove{position:absolute;top:16px;right:18px;z-index:4;
  margin-left:0;background:none;border:0;padding:2px 0;cursor:pointer;
  font-family:var(--body,sans-serif);font-size:11.5px;font-weight:500;
  color:rgba(255,232,195,.6);border-bottom:1px solid rgba(255,232,195,.26);
  transition:color .15s ease,border-color .15s ease;}
#nfConsoleWrap .nfbd-remove:hover{color:#F4F2EE;border-color:#F4F2EE;}
#nfConsoleWrap .nfbd-remove:focus-visible{outline:2px solid var(--or,#ed3326);outline-offset:3px;}
/* Step 3's row is now price, quantity, CTA and nothing else */
#nfConsoleWrap .nfbd-buy .nfbd-qrow{margin:0;gap:11px;flex:0 0 auto;align-items:center;}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("extras price freed + remove moved to the corner")
