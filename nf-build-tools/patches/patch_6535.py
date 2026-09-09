import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 67 · THE 65/35 RESTRUCTURE ────────────────────────────────────────────
# Three things, and the first is a correction of mine.

# ── A · the impact panel goes back to the coffee card ─────────────────────
# Alex: "Moving Total NGO Direct Funding under machinery broke financial domain
# logic — impact funding belongs strictly with the coffee line items."
#
# He is right and I should have seen it: I moved it to fill a hole, which is a
# layout reason for a decision that is not a layout decision. The pass-through
# is a share of the coffee rate and its figure is derived from the three lines
# directly above it; sitting under a machine lease it reads as an equipment
# cost. The hole was never its problem to solve — block 66's align-items fix is
# what actually closed it, and that stays.
old = """    /* block 65 — the pass-through panel joins MACHINES & SERVICING, which is the
       shortest column and was leaving a black void under it. Nothing about the
       figure changes; it is the same node, moved. */
    (function(){
      var ngo = sheetEl.querySelector('.q-ngo');
      if(!ngo) return;
      var cols = manifest.querySelectorAll('.stl-col');
      for(var i = 0; i < cols.length; i++){
        if(cols[i].querySelector('#qMachRows')){ cols[i].appendChild(ngo); return; }
      }
    })();

"""
new = """    /* REVERTED 1 Sep (block 67). This moved the pass-through panel into the
       machines column to fill a void under it. Alex: "impact funding belongs
       strictly with the coffee line items" — correct, and the void was closed
       properly by block 66 anyway. The panel is authored in the coffee run and
       stays there; nothing needs to move it. */

"""
assert src.count(old) == 1, "ngo move anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── B · the step-4 rider goes ─────────────────────────────────────────────
old = """    /* 28 Aug: the sales-call line removed at Alex's instruction. */
    'Everything you have chosen, priced, with the contribution stated.'"""
new = """    /* 28 Aug: the sales-call line removed at Alex's instruction. 1 Sep: and its
       replacement goes too — the card below states every one of those things
       and states them with figures, so the rider was announcing a document the
       reader is already looking at. */
    ''"""
assert src.count(old) == 1, "rider anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ── 67 · MAIN FLOW + VALUE SIDEBAR, 65 / 35 ──────────────────────────────
   The bones of this were already right — two cards on the top left, the form
   spanning both beneath them, the inclusions list running the full height on
   the right. What was wrong was the split: 1.1 / 1.1 / 1.3 gives the sidebar
   37% and the main flow 63%, and the sidebar is a list of names while the main
   flow carries every figure and the form. The proportion now says which of the
   two is the document and which is the reassurance beside it.

   Written as explicit shares rather than fr guesses so the intent survives the
   next person to read it: 32.5 + 32.5 for the two cards, 35 for the sidebar. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest{
  grid-template-columns:32.5fr 32.5fr 35fr;}

/* the sidebar keeps its full-height span and the form keeps the 65%: both were
   already stated, restated here so the three rules that define this layout sit
   together rather than a screen apart */
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest .stl-col:nth-of-type(3){
  grid-column:3;grid-row:1 / span 2;align-self:stretch;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-manifest .q-submit-dark{
  grid-column:1 / 3;grid-row:2;align-self:start;margin:0;}

/* the impact panel is back under the coffee lines, so it gets the breathing
   room it had there — it closes that card rather than sitting mid-column */
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo{margin-top:16px;}

/* one narrow-window rule, since the sidebar cannot be a sidebar at tablet width */
@media(max-width:960px){
  .nf-console-wrap.nf-focus-sec .q-settle .stl-manifest{grid-template-columns:1fr;}
  .nf-console-wrap.nf-focus-sec .q-settle .stl-manifest .stl-col:nth-of-type(3),
  .nf-console-wrap.nf-focus-sec .q-settle .stl-manifest .q-submit-dark{
    grid-column:1;grid-row:auto;}
}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("65/35 restructure; impact panel restored to the coffee card")
