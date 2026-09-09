import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 70 · FOUR ZONES, AND THE TRACK LEFT ALONE ═════════════════════════════
# Alex: "Separate each screen into four distinct vertical zones ... Remove
# microtext stacked directly against the slider track or pins."
#
# Measured before touching anything, phase 1 at 1512x1000:
#
#   #uniPinLab   549-563   "your price · SGD 48.00 · edit"   ← on the track
#   #uniMkLab    569-588   full 10% / 7.5% / 5%
#   #uniTrack    593-599
#   #uniLabL     611-627   "your price"
#   #uniLabR     611-660   "+7.5¢ / cup"        ← two lines
#   #uniHint     623-638   "price locked · tap the pin to edit"  ← inside 611-660
#
# Six things in 110px, two of them overlapping. The gap ABOVE the slider is
# already 190px; the suffocation is entirely inside the control. So the fix is
# not more air around the zone, it is taking the text OUT of the zone: the pin
# label and the hint move into one meta row under the figure, and what stays
# beneath the track is the two endpoints on one line.

# ── the meta row carries all three phases, not just the year ──────────────
old = """      lockedRow.innerHTML='';
      if(phase>=2) lockedRow.appendChild(chip('Price · '+CURP+' '+d.price.toFixed(2)+'/kg · '+window.__nfPct(d.rate)+'%',0));
      if(phase>=2) lockedRow.appendChild(chip('Top-up · '+(d.topUp>0?'+'+d.topUp.toFixed(1)+'¢':'none'),1));"""
new = """      /* block 70 — one horizontal meta row, written on every phase. It used to
         appear only on the year screen, which is why the price screen carried
         its price on a pin label and the top-up screen carried it twice. What
         each phase can still change is a chip with an edit; what it has already
         settled is a chip without one. */
      lockedRow.innerHTML='';
      if(phase>=1) lockedRow.appendChild(chip('Price · '+CURP+' '+d.price.toFixed(2)+'/kg · '+window.__nfPct(d.rate)+'%',0));
      if(phase>=2) lockedRow.appendChild(chip('Top-up · '+(d.topUp>0?'+'+d.topUp.toFixed(1)+'\\u00a2':'none'),1));
      if(phase>=2){
        var tgt=document.createElement('span'); tgt.className='mlchip mlchip--static';
        tgt.textContent='Target · '+fmt0(d.vol)+' cups/yr';
        lockedRow.appendChild(tgt);
      }"""
assert src.count(old) == 1, "lockedRow anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 70 · THE FOUR ZONES ══════════════════════════════════════════════════
   zone 1  the hero equation
   zone 2  the meta row  (price / top-up / target, each with its edit)
   zone 3  the slider, with 32px of nothing above and below it
   zone 4  the lock button and whatever the system is saying back
   Stated as margins on the four blocks rather than wrappers, so the phase
   engine keeps writing to exactly the elements it already knows about. */
.morph-stage #morphFigure{margin-bottom:24px;}
.morph-stage #morphLocked{
  display:flex;flex-wrap:wrap;justify-content:center;align-items:center;
  gap:0 18px;margin-bottom:32px;}
/* margin-top/bottom, NOT the shorthand: these blocks are centred with
   margin:0 auto and `margin:32px 0` silently replaced the auto, shunting the
   whole slider to the left edge of the stage. Caught in the render. */
.morph-stage #mCtlUni,.morph-stage #mCtlVol{margin-top:32px;margin-bottom:32px;}
.morph-stage #morphLockBtn{margin-top:32px;}
.morph-stage #morphCombined{margin-top:24px;}

/* ── zone 3 holds the track and nothing else ──────────────────────────────
   The pin label and the "tap the pin to edit" hint both said what the meta row
   above now says, in 13px, on top of the control they were describing. */
.morph-stage #uniPinLab,.morph-stage #uniHint{display:none !important;}

/* the endpoints: one line under the track, off-white, no wrapping */
.morph-stage #uniLabL,.morph-stage #uniLabR,
.morph-stage .morph-ends,.morph-stage .morph-ends > *{
  color:#CCCCCC;white-space:nowrap;
  font-family:var(--body,'Archivo',system-ui,sans-serif);
  font-size:11px;letter-spacing:.08em;text-transform:uppercase;
}

/* ── zone 1 · operators and units get their 8px ───────────────────────────
   "48.00" and "/kg" were touching, and the operators sat hard against the
   figures either side of them. */
.morph-stage #mFigEq,.morph-stage .lead-op,.morph-stage .mfig-op{
  margin:0 8px;}
.morph-stage #mFigPer,.morph-stage #mFigUnit,.morph-stage .mper,
.morph-stage .mu,.morph-stage .lead-lab,.morph-stage #mFigCur{
  margin:0 8px;}
/* the currency leads the figure, so it only needs the gap on its right */
.morph-stage #mFigCur{margin-left:0;}

/* ── zone 2 · the chips ───────────────────────────────────────────────────
   A settled value with no edit reads as a statement; one with an edit reads as
   a control. The dot between them is a separator, not a bullet list. */
.morph-stage .mlchip{
  color:#CCCCCC;font-family:var(--body,'Archivo',system-ui,sans-serif);
  font-size:11.5px;letter-spacing:.02em;display:inline-flex;align-items:center;}
.morph-stage .mlchip + .mlchip::before{
  content:"·";margin-right:18px;color:rgba(204,204,204,.55);}
.morph-stage .mlchip--static{opacity:.9;}

/* zone 4's status line is a sentence, so it reads as one — it was the last
   multi-word run still set in the terminal face */
.morph-stage #morphCombined{
  font-family:var(--body,'Archivo',system-ui,sans-serif);
  font-size:12px;letter-spacing:normal;text-transform:none;color:#CCCCCC;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("four zones; the track left alone")
