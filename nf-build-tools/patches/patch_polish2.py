import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ══ 63 · STEP 4, THE LEGIBILITY PASS ═════════════════════════════════════
   Alex's review, six points. The first one needs recording because it is a
   repeat of a mistake this file has already documented once.

   HIS #1 WAS REAL AND IT WAS MY RULE LOSING. Block 59c set the sub-lines to
   #CCCCCC and I reported it as done. Measured at runtime it was still
   rgba(244,239,226,.45) — about 4.4:1 on this ground, which is what he is
   squinting at. Line ~5681 carries

       .nf-console-wrap.nf-focus-sec .q-settle .q-lab .q-sub{…,.45}

   at specificity (0,4,1), and my .q-settle .q-sub sits at (0,2,0). Same trap as
   block 30's paper ground: a rule stated later does not win, a rule stated
   HIGHER wins. Restated at the winning weight and verified by reading the
   computed colour back, not by reading the stylesheet.
   ───────────────────────────────────────────────────────────────────────── */
.nf-console-wrap.nf-focus-sec .q-settle .q-lab .q-sub,
.nf-console-wrap.nf-focus-sec .q-settle .q-sub,
.nf-console-wrap.nf-focus-sec .q-settle .q-total-note{color:#D1D1D1;}

/* ── 2 · mono is for numbers ──────────────────────────────────────────────
   "Using a monospaced code/terminal font for multi-line explanatory paragraphs
   makes the layout feel like a raw developer log." Correct. The rates keep it —
   a column of figures wants a fixed advance so the decimals line up — and every
   descriptive run moves to the body sans. */
.nf-console-wrap.nf-focus-sec .q-settle .q-sub,
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo-sub,
.nf-console-wrap.nf-focus-sec .q-settle .q-total-note,
.nf-console-wrap.nf-focus-sec .q-settle .q-taste-opt span,
.nf-console-wrap.nf-focus-sec .q-settle .q-taste-t{
  font-family:var(--body,'Archivo',system-ui,sans-serif);
  letter-spacing:normal;font-size:11.5px;line-height:1.6;
}
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo-sub{font-size:11.5px;}
.nf-console-wrap.nf-focus-sec .q-settle .q-total-note{font-size:11px;}
/* the labels are prose too; only the values and the card titles stay mono */
.nf-console-wrap.nf-focus-sec .q-settle .q-lab{
  font-family:var(--body,'Archivo',system-ui,sans-serif);}
.nf-console-wrap.nf-focus-sec .q-settle .q-val,
.nf-console-wrap.nf-focus-sec .q-settle .stl-col > .q-group,
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo-hd{
  font-family:var(--mono,'IBM Plex Mono',monospace);}

/* ── 3 · the impact box gets an identity ──────────────────────────────────
   "It sits as a dark hole inside an already dark card." A warm gold rather than
   the forest green he offered as an alternative: this document is read by
   someone who does not separate red from green, so the accent that marks the
   one block on the page worth finding must not be the one hue that can vanish.
   The 3px stroke does the work anyway — an edge is a shape, and a shape is
   legible to everyone. */
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo{
  background:rgba(255,232,195,.08);
  border:1px solid rgba(255,213,138,.42);
  border-left:3px solid #E8B457;
  border-radius:12px;
}
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo-hd{color:#E8B457;}
.nf-console-wrap.nf-focus-sec .q-settle .q-ngo-val{color:#FFF3DC;}

/* ── 4 · the inputs read as inputs ────────────────────────────────────────
   They were a .22 hairline on a dark fill, which at this size is close to no
   edge at all. A stated border, and a focus state that says so twice — ring
   plus border — because a colour-only focus ring is not a focus state. */
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld input,
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld select{
  background:rgba(255,232,195,.05);
  border:1px solid #444444;
  border-radius:8px;
}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld input:hover,
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld select:hover{
  border-color:#5E5E5E;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld input:focus,
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld select:focus{
  border-color:var(--or,#EE4D17);
  box-shadow:0 0 0 3px rgba(238,77,23,.22);
  outline:none;
}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld input::placeholder{color:#7C7C7C;}

/* ── 5 · the inclusions column stops being a wall ─────────────────────────
   Row padding from 7px to 12/14, and each perk gets a tick. The tick is a
   glyph, not a colour — it reads as "this one is on" without asking anyone to
   tell green from grey, and it gives the eye a left edge to run down instead of
   seven identical paragraph starts. Rows that are NOT included lose it, so the
   mark stays a statement rather than decoration. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-col:has(#qRowTablet) .q-line{
  padding:12px 0 14px;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-col:has(#qRowTablet) .q-lab{
  position:relative;padding-left:22px;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-col:has(#qRowTablet) .q-lab::before{
  content:"\2713";position:absolute;left:0;top:1px;
  font-family:var(--mono,monospace);font-size:11px;line-height:1.35;
  color:#E8B457;
}
/* A declined or charged row is not an inclusion and must not wear the tick.
   TWO THINGS CAUGHT IN TEST, both mine:
     · a rule re-asserting the tick on any row with a value sat here, doing
       nothing except outranking these — :has(#qRowTablet) carries the
       specificity of an ID, so it beat the dash and every declined row kept a
       tick. Deleted rather than fought;
     · and #qRowCoolers is in the MACHINES column, not this one, so marking it
       put a bare dash in front of "Milk Fridge" where no tick baseline exists.
       The dash is scoped to the inclusions column, and the coolers row is left
       out of the marking entirely. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-col:has(#qRowTablet) .q-line.is-off .q-lab::before{
  content:"\2013";color:#8A8A8A;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-col:has(#qRowTablet) .q-line.is-off .q-val{
  color:#B9B9B9;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

# ── and the rows say which state they are in, so the tick can follow ──────
# The mark has to be driven by the same resolution that writes the value, not
# guessed from the text: syncInclusions() already knows, so it flags the row.
old = """    /* the wrap */
    setv('#qCobrandVal', !units ? 'Included'"""
new = """    /* block 63 — flag the rows that are NOT inclusions, so the tick in the
       margin can become a dash on them. Driven by the same branch that writes
       the value; nothing infers state from the printed words. */
    var mark = function(sel, on){ var e = $(sel); if(e) e.classList.toggle('is-off', !on); };
    mark('#qRowTablet',  !(buy && !rent));

    /* the wrap */
    setv('#qCobrandVal', !units ? 'Included'"""
assert src.count(old) == 1, "mark anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """    setv('#qFleetSub', (buy && !rent && !svcBought)"""
new = """    mark('#qRowCobrand', !(buy && !rent && !wrapTaken));
    mark('#qRowFleet',   !(buy && !rent && !svcBought));
    setv('#qFleetSub', (buy && !rent && !svcBought)"""
assert src.count(old) == 1, "mark2 anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("legibility pass applied")
