import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ── 43 · THE COFFEE TILE'S DETAILS BUTTON, AS IT IS ON THE SHOP ──────────
   Alex sent the shop's control and asked for it here. Nothing needed
   transcribing: it is the same .cx-details class, and #shop already overrides
   the base rule into a bordered pill. The builder is not inside #shop, so it
   was still getting the base treatment — a 9px underlined footnote sitting
   beside "Tap to add", which is why the same button reads as two different
   things on two pages.

   Ported verbatim from #shop .cx-details (line ~3150), with three seams and
   nothing else:

     1 · the tile row's foot is justify-content:space-between and carries the
         "Tap to add" / "In order" status, which the shop's column does not.
         width:100% would push that status out, so the button takes the free
         space with flex:1 and the status keeps its intrinsic width.
     2 · 10px/.14em in an ~11px-narrower tile ran the word to both borders;
         9.5px/.12em holds the shop's proportions at this size. Measured, not
         guessed — see the padding note below.
     3 · --ease is not declared on the tile's variable island (see the aliases
         at .cx-viewport), so the arrow's transition states its curve rather
         than inheriting a value that resolves to nothing here.

   The lit state keeps the file's convention: a picked tile turns its status
   orange, so the button follows with the same signal rather than inventing a
   second one. */
.nf-console-wrap .cx-foot{gap:9px;margin-top:9px;}
.nf-console-wrap .cx-details{
  flex:1 1 auto;display:flex;align-items:center;justify-content:center;gap:7px;
  font-family:var(--font-m,monospace);font-size:9.5px;letter-spacing:.12em;
  text-transform:uppercase;
  padding:9px 10px;border:1px solid rgba(26,24,21,.28);border-radius:9px;
  color:rgba(26,24,21,.78);background:none;cursor:pointer;
  transition:border-color .18s,color .18s,background .18s;
}
.nf-console-wrap .cx-details::after{
  content:"\2192";font-size:12px;
  transition:transform .2s cubic-bezier(.4,0,.2,1);
}
.nf-console-wrap .cx-details:hover{
  border-color:#1A1815;color:#1A1815;background:rgba(26,24,21,.04);
}
.nf-console-wrap .cx-details:hover::after{transform:translateX(3px);}
.nf-console-wrap .cx-tile.is-picked .cx-details{
  border-color:var(--or,#ed3326);color:var(--or,#ed3326);
}
.nf-console-wrap .cx-details:focus-visible{
  outline:2px solid var(--or,#ed3326);outline-offset:2px;
}
/* CAUGHT IN TEST: the pill is ~29px taller than the footnote it replaces, so
   the coffee screen grew 839px against the machines screen's 810 and its
   forward button dropped 30px below the shared position fixed an hour ago.
   The 28px above the tile row is where it comes back from — a gap sized for a
   row that ended in a text link, not one that now ends in a button. */
.nf-console-wrap .cx-viewport{margin-top:0;}

/* short viewports: the shop drops to a 30px minimum at its own breakpoint and
   this row is tighter still, so the padding comes off before anything else */
@media(max-height:860px){
  .nf-console-wrap .cx-details{padding-top:7px;padding-bottom:7px;}
  .nf-console-wrap .cx-foot{margin-top:7px;}
}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("coffee Details button matched to the shop")
