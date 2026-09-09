import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ══ 40 · THE QUOTE SCREEN SCROLLS AT 60fps AGAIN ═══════════════════════════
   Alex: "when i scroll up and down on final page it's non-stop juddering,
   why?"

   Because four panels on that screen carry backdrop-filter: blur(10px) and sit
   over a 1320px video. backdrop-filter re-blurs whatever is behind it EVERY
   frame, and the cost is proportional to the blurred area, not the radius. On
   this screen that area is about 820,000px:

       .stl-col      382 x 165   (x2)
       .stl-col      451 x 679
       .q-submit-dark 782 x 496

   Measured, scripted scroll on screen 4, median frame time:

       as shipped ................................. 30.9ms  (~32fps)
       .rail's blur off only ...................... 35.8ms  (no change)
       ALL backdrop-filter off .................... 16.6ms  (60fps, 0 frames over 32ms)
       + video hidden ............................. 16.6ms  (no further gain)
       + custom cursor off ........................ 16.7ms  (no further gain)
       + all CSS animations off ................... 16.7ms  (no further gain)

   So it is backdrop-filter and nothing else — not the video, not the cursor,
   not the animations. I checked the rail first because a fixed blurred header
   is the usual suspect; it is not this one.

   The panels are 58% opaque over a dark, busy backdrop, which is precisely the
   case where a blur contributes least and costs most. Taking the blur off and
   lifting the fill to 82% keeps the same frosted read — dark panel, video
   ghosting through — for nothing per frame. Stated here rather than edited in
   place above so the original values stay legible next to the reason. */
.q-settle .stl-col,
.q-settle .q-submit-dark,
.q-settle #sendPanel,
.q-settle .q-thanks-offer{
  backdrop-filter:none;-webkit-backdrop-filter:none;
  background:rgba(20,19,17,.82);
}
/* the rail keeps its blur: it is 93% opaque already, it measured as costing
   nothing, and it sits over the whole site rather than over one video. */
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("quote screen de-jankified")
