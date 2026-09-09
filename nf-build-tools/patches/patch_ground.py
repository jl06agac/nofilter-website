import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 64 · THE PROPOSAL SITS ON A STATIC GROUND ─────────────────────────────
# Alex: "Kill the Live Video: Swap the background video for a static dark slate
# (#141614) featuring two faint ambient radial halos — a soft forest-green blur
# positioned behind Coffee, and a warm bronze blur behind Equipment."
#
# The video element goes rather than being hidden: a <video loop> that is
# painted over still decodes every frame, and this one sat under the whole card
# for as long as the reader had step 4 open. Removing the node removes the work,
# which is the same argument that took the backdrop-filters off in block 33.
#
# The halos are two radial gradients on the same layer, so the ground is one
# painted box with no extra elements and nothing to composite per frame. They
# are ambience and carry no meaning — nothing on this page is identified by
# them — which is the only reason a green and a bronze can sit side by side in a
# document read by someone who does not separate the two.
old = """    if(!sheetEl.querySelector('.stl-media')){
      var med = document.createElement('div');
      med.className = 'stl-media';
      med.innerHTML = '<video muted loop playsinline preload="metadata" ' +
        'onerror="this.style.display=\\'none\\';"><source src="' + STL_VIDEO_SRC +
        '" type="video/mp4"></video><div class="stl-scrim"></div>';
      sheetEl.insertBefore(med, sheetEl.firstChild);
    }"""
new = """    if(!sheetEl.querySelector('.stl-media')){
      var med = document.createElement('div');
      /* block 64 — a painted ground, not footage. The scrim stays: the sent
         state darkens it further and that rule still has something to act on. */
      med.className = 'stl-media stl-static';
      med.innerHTML = '<div class="stl-scrim"></div>';
      sheetEl.insertBefore(med, sheetEl.firstChild);
    }"""
assert src.count(old) == 1, "media anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ── 64 · the static ground ───────────────────────────────────────────────
   #141614 slate with two soft halos: forest behind the COFFEE figure on the
   left, bronze behind EQUIPMENT on the right. Both sit at the height of the
   hero pair, so they read as light behind those two numbers rather than as a
   pattern. Low alpha on purpose — at anything stronger the card stops being a
   document and starts being a poster. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-media.stl-static{
  background:
    radial-gradient(46% 38% at 27% 16%, rgba(74,124,89,.20), rgba(74,124,89,0) 70%),
    radial-gradient(46% 38% at 73% 16%, rgba(176,124,62,.20), rgba(176,124,62,0) 70%),
    #141614;
}
/* the scrim was sized to knock back moving footage; over a painted ground that
   much veil just greys the halos out, so it thins to a floor that keeps the
   text contrast the legibility pass established */
.nf-console-wrap.nf-focus-sec .q-settle .stl-static .stl-scrim{
  background:linear-gradient(180deg,rgba(20,22,20,.30),rgba(20,22,20,.52) 60%,rgba(20,22,20,.70));
}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("static ground with two halos")
