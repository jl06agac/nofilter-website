import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── the two column-one cards share one grid cell ──────────────────────────
# CAUGHT IN TEST: placing them on rows 1 and 2 while the other two cards span
# both rows let the tall cards drive the row heights — row one grew to fit the
# form, and an 83px hole opened between the coffee card and the machines card.
# Grid always distributes a spanning item across the rows it spans, so no amount
# of alignment fixes it. One wrapper makes column one a single cell whose two
# cards stack inside it, and the row-sizing question disappears.
old = """    if(sendCard){ sendCard.classList.add('q-submit-dark'); manifest.appendChild(sendCard); }"""
new = """    /* block 69 — column one is one cell holding two cards */
    (function(){
      var cols = manifest.querySelectorAll('.stl-col');
      if(cols.length < 2) return;
      var grp = document.createElement('div');
      grp.className = 'stl-colgroup';
      manifest.insertBefore(grp, cols[0]);
      grp.appendChild(cols[0]);
      grp.appendChild(cols[1]);
    })();

    if(sendCard){ sendCard.classList.add('q-submit-dark'); manifest.appendChild(sendCard); }"""
if src.count(old) != 1:
    raise SystemExit("colgroup anchor not unique (%d)" % src.count(old))
src = src.replace(old, new)

CSS = r'''
/* ══ 69 · THE THREE-COLUMN DASHBOARD ══════════════════════════════════════
   Alex's final structure, and it reads left to right as an argument: what you
   pay for, what comes with it, how to say yes.

     col 1   Coffee & Contribution → NGO pass-through → Machines & Servicing
     col 2   Included with the Partnership
     col 3   Contact form → taste options → submit

   Thirds, not the 65/35 of block 67. Everything below is placement: the four
   cards are the same nodes in the same order, each one told where to sit. No
   JS moves, so the printable letter underneath is untouched. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest{
  grid-template-columns:repeat(3,1fr);
  grid-template-rows:auto;
  align-items:start;
}
/* col 1 is one cell: the coffee card above the machines card, so the
   pass-through panel and the hardware it is NOT part of share a column without
   either being mistaken for the other */
.nf-console-wrap.nf-focus-sec .q-settle .stl-colgroup{
  grid-column:1;grid-row:1;display:flex;flex-direction:column;
  gap:clamp(12px,1.5vw,18px);min-width:0;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest > .stl-col{
  grid-column:2;grid-row:1;align-self:start;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest .q-submit-dark{
  grid-column:3;grid-row:1;align-self:start;margin:0;
  display:flex;flex-direction:column;}

/* ── column three, stacked ────────────────────────────────────────────────
   The six-track inline form from block 65 was built for a full-width strip
   under two cards; in a third of the width it would put three inputs in ~120px
   each. Back to one per row, which is what a narrow column wants. */
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .frm{
  display:grid;grid-template-columns:1fr;gap:10px;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld,
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(1),
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(2),
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(3),
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(4),
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(5),
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld.full{
  grid-column:1;}
/* the two tasting options stack again for the same reason */
.nf-console-wrap.nf-focus-sec .q-settle .q-taste{grid-template-columns:1fr;}
.nf-console-wrap.nf-focus-sec .q-settle .q-taste-opt+.q-taste-opt{margin-top:8px;}

/* the button is full width and sits at the foot of the column, so all three
   columns finish on one line whatever the form does above it */
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .panel-bd{
  display:flex;flex-direction:column;height:100%;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .frm{flex:1 1 auto;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld.full:last-of-type{
  margin-top:auto;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel #ctaSend{width:100%;}

/* the narrow-window fallback: three thirds become one column, in the same
   reading order the wide layout states */
@media(max-width:1100px){
  .nf-console-wrap.nf-focus-sec .q-settle .stl-manifest{
    grid-template-columns:1fr;grid-template-rows:auto;}
  .nf-console-wrap.nf-focus-sec .q-settle .stl-colgroup,
  .nf-console-wrap.nf-focus-sec .q-settle .stl-manifest > .stl-col,
  .nf-console-wrap.nf-focus-sec .q-settle .stl-manifest .q-submit-dark{
    grid-column:1;grid-row:auto;}
}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("three-column dashboard")
