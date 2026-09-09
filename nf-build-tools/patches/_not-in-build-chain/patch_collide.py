import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 72 · THE 3C COLLISION, AND WHY MY MARGINS DID NOTHING ═════════════════
# Alex: "YOUR LIKELY CUPS PER YEAR is overlapping the Price · SGD 48.00/kg /
# EDIT text."
#
# Reproduced at 1024x640 — it is window-dependent, which is why it did not show
# at the 1512x1000 I had been testing at:
#
#   #morphLocked   396-417     the meta row, in normal flow under the figure
#   #mCtlVol       414-484     the slider block
#     .ml          414-431     "Your likely cups per year"   ← lands on 396-417
#
# The cause is one line I did not look up before writing block 70's margins:
#
#   .morph-ctl{position:absolute; left:0; right:0; bottom:137px; ...}
#
# The slider is anchored to the BOTTOM of the stage, not placed in the flow. So
# every margin I put on it was inert against a flow sibling, and at a short
# window the absolutely positioned block simply rose until it sat on top of the
# meta row. No amount of spacing on either element could have fixed that.
#
# The meta row moves INSIDE the control block instead — which is also exactly
# what Alex asked for ("place the single-line summary 24px above the line").
# Once it is a child of the thing it labels, the two cannot separate or collide
# at any window size, because they are one object.
old = """      lockedRow.innerHTML='';
      if(phase>=1) lockedRow.appendChild("""
new = """      /* block 72 — the meta row rides with the control it describes. The
         control is position:absolute against the stage, so a row left in the
         flow above it collides the moment the window is short. */
      (function(){
        var ctl = document.getElementById(phase===2 ? 'mCtlVol' : 'mCtlUni');
        if(ctl && lockedRow.parentNode !== ctl) ctl.insertBefore(lockedRow, ctl.firstChild);
      })();
      lockedRow.innerHTML='';
      if(phase>=1) lockedRow.appendChild("""
assert src.count(old) == 1, "lockedRow move anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 72 · THE SLIDER ZONE, FIXED AND UNCROWDED ════════════════════════════ */

/* the meta row now sits inside the control, 24px above the track.
   CAUGHT IN TEST: inserting it as firstChild was not enough — .morph-locked
   carries order:6, and the control is a flex column, so it obediently went to
   the BOTTOM of the stack and landed under the track instead of over it. DOM
   order does not decide anything in a flex container that has been given an
   order. */
.morph-stage .morph-ctl #morphLocked{
  order:-1;margin:0 0 24px;width:100%;}

/* "Your likely cups per year" goes: the hero above it already reads
   "43,000 CUPS", so the label was naming a number that names itself — and it
   was the element landing on the meta row. */
.morph-stage #mCtlVol .ml{display:none !important;}

/* the track keeps a fixed band of its own: 16px of nothing above and below,
   so nothing can be pushed onto it by a short window */
.morph-stage #uniWrap,.morph-stage #volCups{margin-top:16px;margin-bottom:16px;}

/* the pin and end labels tuck 16px under the track, faint, out of the thumb's
   way — they were 12px below it and reading at full strength */
.morph-stage #uniLabL,.morph-stage #uniLabR{margin-top:16px;color:#CCCCCC;}
.morph-stage .morph-ends{margin-top:16px;color:#CCCCCC;}
.morph-stage #uniLabL,.morph-stage #uniLabR,.morph-stage .morph-ends > *{
  pointer-events:none;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("collision closed; slider zone fixed")
