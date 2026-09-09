import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 74 · RESERVED ROWS, ONE TYPE FLOOR, ONE TRACK GEOMETRY ════════════════
# Alex: "still really bad, and now lost its standardisation".
#
# Measured at his window before this block, every offset relative to the top of
# the card:
#
#         eyebrow   cap   hero   meta   TRACK   button    rung
#   3A       —       —     93     —      218     314      compact2
#   3B       67      92    122    185    260     348      compact3
#   3C       —       85    134    249     —       —       none
#
# Three faults, all downstream of one decision in block 73.
#
# (a) NOTHING SHARES A Y. A gap gives consistent SPACING; it cannot give
#     consistent POSITION, because the phases do not have the same rows. 3A has
#     no eyebrow, no caption, no meta row; 3C has no sub and no button. Centre
#     three rows and six rows in the same box and they land differently. The old
#     bottom:137px was wrong for the card height, but it WAS the same 137px on
#     every phase, which is the one thing it got right and I threw away.
#
# (b) THE TYPE SHRANK, AND DIFFERENTLY PER PHASE. Different row counts mean
#     different total heights, which put each phase on a different compaction
#     rung — so the hero changed size as you walked 3A → 3B → 3C. Compaction
#     also had no floor, so it would go as small as it liked.
#
# (c) 3C's TRACK RAN THE FULL WIDTH OF THE CARD. Mine, from block 73:
#         .morph-stage #mCtlVol:not(.hide){ … width:100% }
#     carries an ID, so it outranked `.morph-ctl{width:min(720px,88%)}` and the
#     volume slider stopped being the same instrument width as the other two.
#     Same specificity trap as the two before it in this file.
#
# The fix for (a) and (b) is the same thing: RESERVE the rows. Every zone keeps
# its height whether or not this phase has content for it. All three phases then
# have identical content height → the same rung → the same size → every row on
# the same Y. And the rung ladder gets a floor, so the hero cannot shrink into
# body copy to make room.
#
# The room for that comes from two places rather than from the type:
#   · the eyebrow row goes. On 3B it read "FROM YOUR SGD 51.00/KG" directly
#     above a meta chip reading "Price · SGD 51.00/kg · 10% [EDIT]" — the same
#     number twice, in two type styles, on consecutive rows.
#   · the instrument's own band compresses on the tighter rungs. Its 86px is
#     mostly air above the badges and below the endpoints.

# ── 1 · the hero's size is a rung question, not a phase question ───────────
old = """      /* block 73 — a property, not an inline font-size, so the compaction
         rungs can still act on it. See the note in guard(). */
      figure.style.fontSize = '';
      stage.style.setProperty('--mfig', phase===2 ? 'clamp(38px,7vw,88px)' : 'clamp(44px,8.5vw,104px)');"""
new = """      /* block 74 — neither an inline size nor a per-phase property. The rung
         owns the size; .year scales it by a fixed ratio in CSS. One band
         height, one baseline, all three phases. */
      figure.style.fontSize = '';
      stage.style.removeProperty('--mfig');"""
assert src.count(old) == 1, "mfig anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 2 · the width bug, fixed at its source ────────────────────────────────
old = """.morph-stage #mCtlVol:not(.hide){display:flex;flex-direction:column;align-items:center;width:100%;}"""
new = """/* block 74: width:100% removed — it carried an ID, outranked the instrument's
   own width:min(720px,88%), and stretched 3C's track across the whole card. */
.morph-stage #mCtlVol:not(.hide){display:flex;flex-direction:column;align-items:center;}"""
assert src.count(old) == 1, "mCtlVol width anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 3 · the side cards show on their phase, not on hover ──────────────────
# Alex: "Screens 3B and 3C dropped the left and right framing cards seen on 3A".
# They exist on both — block 68 built them — but they were gated on hovering the
# unified track. On the year phase that control is display:none, so the year
# pair could never be triggered at all; the top-up pair only appeared if the
# pointer happened to be over the slider. The price phase's cards are not gated,
# which is why 3A always looked framed and the other two did not.
old = """      if(window.__nfTopupGutters && p!==1) window.__nfTopupGutters.hide();"""
new = """      /* block 74 — each phase's pair is shown by the phase, like 3A's. The
         timeout is one tick, so the class and the control the cards measure
         against are in place before they are positioned. */
      if(window.__nfTopupGutters){
        if(p===1) setTimeout(window.__nfTopupGutters.show,80); else window.__nfTopupGutters.hide(); }
      if(window.__nfYearGutters){
        if(p===2) setTimeout(window.__nfYearGutters.show,80); else window.__nfYearGutters.hide(); }"""
assert src.count(old) == 1, "gutter anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 74 · RESERVED ROWS ═══════════════════════════════════════════════════ */

/* ── the type ladder, with a floor ────────────────────────────────────────
   --mfigbase is the hero size. The rungs scale it, but max() stops the first
   two rungs going below 64px — the figure is the whole point of this card and
   it is not allowed to become body copy to buy back padding. Only the last
   rung, which exists for the shortest windows, may go under, and not past 52.
   The year phase takes 84.6% of whatever that is — the 88/104 ratio the file
   already used, stated as a ratio rather than a second clamp so the two cannot
   drift apart. */
.morph-stage{--mfigbase:clamp(44px,8.5vw,104px);}
.morph-stage.m-compact {--mfigbase:max(var(--mfigfloor), calc(clamp(44px,8.5vw,104px) * .82));}
.morph-stage.m-compact2{--mfigbase:max(var(--mfigfloor), calc(clamp(44px,8.5vw,104px) * .70));}
.morph-stage.m-compact3{--mfigbase:max(var(--mfigfloor), calc(clamp(44px,8.5vw,104px) * .58));}
/* the floor is 64px, but it has to yield on a narrow window: the figure is
   white-space:nowrap, and the year phase's line is the longest string on the
   card, so a hard 64 would run it off the sides (and block 73 clips the column,
   so it would be cut rather than spill). min() ties the floor to the width. */
.morph-stage{--mfigfloor:min(64px, 7.2vw);}

/* ── row 1 · a band of fixed height on every phase ────────────────────────
   The band is 1.20x the base size on ALL phases; only the glyphs inside change
   size. Centred by the line box rather than by flex: the figure is one nowrap
   line, so a line-height equal to the band height centres the type in it — and
   unlike display:flex it leaves the inline run (SGD · 51.00 · /kg · = · 9.2¢ ·
   /cup) intact. Flex would have made every one of those spans its own item and
   thrown away the baseline they share. */
.morph-stage .morph-inner > .morph-figure{
  font-size:var(--mfigbase);
  line-height:calc(var(--mfigbase) * 1.20);
  min-height:calc(var(--mfigbase) * 1.20);
  padding-bottom:0;
}
.morph-stage.year .morph-inner > .morph-figure{font-size:calc(var(--mfigbase) * .846);}
/* the band's line-height is a layout number, not a typographic one — the inline
   runs inside the equation keep their own tight leading */
.morph-stage .morph-figure > *{line-height:1;}

/* ── the eyebrow row goes ─────────────────────────────────────────────────
   It only ever carried "FROM YOUR SGD 51.00/KG" on the top-up phase, one row
   above a chip reading "Price · SGD 51.00/kg · 10% [EDIT]". The meta row is
   where that lives now, and it has the edit link. */
.morph-stage .morph-inner > .morph-eyebrow{display:none !important;}

/* ── rows that exist on every phase, content or not ───────────────────────
   !important because block 73 hides them when empty and the phase engine
   writes display:none on the caption inline. Collapsing an empty row is what
   moved everything under it. */
.morph-stage .morph-inner > .morph-cap{
  display:block !important;position:static !important;
  /* stated in px, and the size stated with it. An em reserve was 1-2px out
     because the top-up phase sets its caption to 12.5px while the others use
     11.5 — so 1.5em reserved a different number of pixels per phase and the
     whole stack under it landed 2px apart. A reserved row cannot be measured
     in a unit that changes between the things it is reserving for. */
  font-size:12.5px;line-height:1.5;min-height:19px;}
.morph-stage .morph-inner > .morph-sub{
  display:block !important;min-height:1.45em;}
/* the sub keeps its BOX on every phase but not its text: it belongs to the
   price screen ("to conservation, built into every cup") and the phase engine
   only ever adds .hide to it, leaving the old string in place. Forcing display
   back on therefore printed the price screen's line on the year screen.
   Reserved by visibility, which holds the row without showing the words. */
.morph-stage .morph-inner > .morph-sub.hide{visibility:hidden;}
.morph-stage .morph-inner > .morph-locked{
  display:flex !important;min-height:21px;}
/* the year phase hides the lock button with visibility, which reserves its
   space. It must not ALSO be display:none, or 3C loses a row 3A and 3B keep
   and everything above it slides down. */
.morph-stage.year .morph-inner > .morph-lockbtn{display:flex !important;}

/* ── row 3 · one instrument geometry, two instruments ─────────────────────
   Every part of the unified track is absolutely placed inside .uni-wrap, so
   the wrap's height and the track's offset inside it are the two numbers that
   decide where the line sits. Both are variables now, so the tighter rungs can
   compress the band instead of the type — and #mCtlVol takes the same offset
   as padding, which is what puts 3C's track on 3A's and 3B's Y. */
.morph-stage .uni-wrap{height:var(--uniH,86px);}
.morph-stage .uni-mklab{top:var(--uniLab,14px);}
.morph-stage .uni-mk{top:var(--uniMk,30px);}
.morph-stage .uni-track,
.morph-stage .uni-fill-p,
.morph-stage .uni-fill-t{top:var(--uniTrk,38px);}
.morph-stage .uni-zone{top:calc(var(--uniTrk,38px) - 4px);}
.morph-stage .uni-pin{top:calc(var(--uniTrk,38px) - 14px);}
.morph-stage .uni-thumb{top:calc(var(--uniTrk,38px) + 3px);}
.morph-stage .uni-end{top:calc(var(--uniTrk,38px) + 22px);}
.morph-stage #mCtlVol{padding-top:var(--uniTrk,38px);}

.morph-stage.m-compact2{--uniH:70px;--uniLab:6px;--uniMk:22px;--uniTrk:30px;}
.morph-stage.m-compact3{--uniH:62px;--uniLab:2px;--uniMk:18px;--uniTrk:26px;}

/* the control's own reserved height, so the button below it is on one Y too */
.morph-stage .morph-inner > .morph-ctl{
  /* 158, measured: the unified instrument's natural height at the loosest rung
     is 16 + 86 (wrap) + 16 + 38 (the status line and its margin) = 156.4, and a
     min-height under that let 3C's shorter control sit 8px smaller — which
     re-centred the whole column and put the year phase 4px below the other
     two. The reserve has to clear the tallest of the two instruments. */
  min-height:var(--mctl,158px);
  width:min(720px,88%);}
.morph-stage.m-compact2{--mctl:120px;}
.morph-stage.m-compact3{--mctl:106px;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("rows reserved; phases aligned")
