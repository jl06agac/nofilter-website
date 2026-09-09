import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 53 · THE BUILDER'S MARKET SWITCH BECOMES THE RAIL'S ───────────────────
# Alex: "almost think top left can be more discrete with a uae and sg flag like
# intro page instead of 'priced in sgd aed'."
#
# The rail solved this on 20 Aug — his words then were "it should just be the
# flags" — and the builder kept the old wording, so the same decision is stated
# twice in one document in two different shapes. Harvested from #mktSel: the two
# flag SVGs verbatim (line ~8382), and its state grammar unchanged — .5 opacity
# at rest, full opacity with a 1.06 scale and a brighter ring when pressed.
#
# Both cues are lightness and size, not hue, which is deliberate: this control
# now carries no words at all, and the two flags it shows are red/white against
# red/green/white/black. Which one is live must never rest on telling red from
# green. Screen readers and hover still get "Singapore · SGD" and "United Arab
# Emirates · AED" from the canon's own title and aria-label.
#
# Three seams, and nothing else:
#   1 · the rail sits on ink and rings its flags in cream; this bar is paper, so
#       the ring is ink at the same two weights.
#   2 · the pressed background is the rail's tint inverted for the same reason.
#   3 · the UK flag does not come across. The rail carries it as "not yet
#       trading"; this control's only job is to pick the currency the quote is
#       priced in, and there is no UK price to pick.
# The data-deckmkt / aria-pressed contract is untouched, so paint() and the
# delegation to the rail's own buttons keep working exactly as they were.

old = """    + '<div class="dt-mkt" role="group" aria-label="Pricing market">'
    +   '<span class="dt-mkt-k">Priced in</span>'
    +   '<button type="button" class="dt-mkt-b" data-deckmkt="SG">SGD</button>'
    +   '<button type="button" class="dt-mkt-b" data-deckmkt="AE">AED</button>'
    + '</div>';"""
new = """    + '<div class="dt-mkt" role="group" aria-label="Pricing market">'
    /* flags harvested verbatim from the rail's #mktSel (see the market toggle
       at the top of <body>); see block 53 for the three seams. */
    +   '<button type="button" class="dt-mkt-b" data-deckmkt="SG"'
    +     ' title="Singapore \\u00b7 SGD" aria-label="Singapore market, prices in SGD">'
    +     '<span class="mkflag"><svg viewBox="0 0 30 20" aria-hidden="true">'
    +     '<rect width="30" height="10" fill="#ED2939"/><rect y="10" width="30" height="10" fill="#fff"/>'
    +     '<circle cx="8.2" cy="5" r="3.7" fill="#fff"/><circle cx="9.9" cy="5" r="3.7" fill="#ED2939"/>'
    +     '<g fill="#fff"><circle cx="11.6" cy="2.7" r=".62"/><circle cx="13.7" cy="4.2" r=".62"/>'
    +     '<circle cx="12.9" cy="6.7" r=".62"/><circle cx="10.3" cy="6.7" r=".62"/>'
    +     '<circle cx="9.5" cy="4.2" r=".62"/></g></svg></span></button>'
    +   '<button type="button" class="dt-mkt-b" data-deckmkt="AE"'
    +     ' title="United Arab Emirates \\u00b7 AED" aria-label="UAE market, prices in AED">'
    +     '<span class="mkflag"><svg viewBox="0 0 30 20" aria-hidden="true">'
    +     '<rect width="30" height="6.67" fill="#00732F"/><rect y="6.67" width="30" height="6.66" fill="#fff"/>'
    +     '<rect y="13.33" width="30" height="6.67" fill="#000"/><rect width="7.5" height="20" fill="#FF0000"/>'
    +     '</svg></span></button>'
    + '</div>';"""
assert src.count(old) == 1, "market markup anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ── 53 · the builder's market switch, as flags (see the JS note) ──────────
   Ported from #mktSel. Everything about the state grammar is the rail's; only
   the ring and the pressed tint are restated for a paper ground. */
#nfConsoleWrap .dt-mkt{gap:2px;}
#nfConsoleWrap .dt-mkt-b{
  padding:5px 7px;min-width:0;display:inline-flex;align-items:center;justify-content:center;
  gap:0;background:transparent;border:1px solid transparent;border-radius:5px;cursor:pointer;
  transition:border-color .2s ease,background .2s ease,opacity .2s ease;
}
#nfConsoleWrap .dt-mkt-b .mkflag{display:block;width:26px;height:17px;border-radius:2.5px;
  overflow:hidden;opacity:.5;
  box-shadow:0 0 0 1px rgba(26,24,21,.26);        /* seam 1 — ink, not cream */
  transition:opacity .2s ease,box-shadow .2s ease,transform .2s ease;}
#nfConsoleWrap .dt-mkt-b .mkflag svg{display:block;width:100%;height:100%;}
#nfConsoleWrap .dt-mkt-b:hover .mkflag{opacity:.85;}
#nfConsoleWrap .dt-mkt-b[aria-pressed="true"] .mkflag{opacity:1;transform:scale(1.06);
  box-shadow:0 0 0 1px rgba(26,24,21,.85);}
#nfConsoleWrap .dt-mkt-b[aria-pressed="true"]{background:rgba(26,24,21,.07);
  border-color:rgba(26,24,21,.2);}                 /* seam 2 */
#nfConsoleWrap .dt-mkt-b:focus-visible{outline:2px solid var(--or,#EE4D17);outline-offset:2px;}
/* the old pill styling would otherwise still be painting a dashed border and an
   orange fill around a flag */
#nfConsoleWrap .dt-mkt-b{border-style:solid;color:inherit;letter-spacing:normal;}
#nfConsoleWrap .dt-mkt-b:hover{transform:none;border-color:rgba(26,24,21,.2);}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("builder market switch is now the rail's flags")
