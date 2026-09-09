import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# the paragraph's gap is an inline style, so it has to change in the markup
old = """          <p class="body-lg fade d1x" style="margin-top:20px">Configure equipment, coffee volume, and"""
new = """          <!-- the 20px gap moved into CSS (block 32) so it can respond to viewport
               HEIGHT; an inline style cannot. -->
          <p class="body-lg fade d1x">Configure equipment, coffee volume, and"""
assert src.count(old) == 1, "paragraph anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ── 32 · THE TRADE GATE FITS THE WINDOW IT IS OPENED IN ──────────────────
   Alex: "i think this should all shift up so that on load everything including
   the Send me an access code button should be visible to the reader. i
   shouldn't need to scroll down for this page."

   The cause is one line: .beat carries padding:clamp(52px,7vw,104px), which
   scales with WIDTH. On a wide, short window — a MacBook with the dock and the
   menu bar taking their cut, which is most of them — that pays out the full
   100.8px top AND bottom for a viewport with about 700px to give. Measured
   before this block: the button's foot sat at 719px, so it cleared an 800px
   viewport by 80px and fell off a 700px one entirely. Alex's screenshot is the
   700px case.

   Every vertical gap in this beat is now min(its old value, a fraction of the
   viewport height). On a tall window nothing changes at all — the old number
   wins, which is why this is min() and not a media query that would snap the
   layout at one arbitrary height. On a short one each gap gives back its share:
   about 45px in total, which puts the button's foot at 650px in a 700px window
   — measured 719 before, 706/689/674/659/650 after at 1000/900/800/740/700.

   Only this beat. The rest of the page keeps .beat's width-based rhythm, which
   is right for sections a reader scrolls through rather than lands on. */
#quote .nf-access{
  padding-top:min(clamp(52px,7vw,104px), 8vh);
  padding-bottom:min(clamp(52px,7vw,104px), 8vh);
}
#quote .nf-access .beat-hd{margin-bottom:min(26px, 2.6vh);}
#quote .nf-access .body-lg{margin-top:min(20px, 2vh);}
#quote .nf-access .acc-form{margin-top:min(26px, 2.6vh);}
#quote .nf-access .acc-f{margin-bottom:min(14px, 1.6vh);}
/* NO headline trim. I tried min(1em, 6.4vh) here and it collapsed the display
   type from 148px to 27px — `1em` on an element resolves against its PARENT's
   font-size, not its own, so the "cap" was 16px. Caught in measurement. The
   gaps alone are enough anyway: the button's foot lands at 674px in an 800px
   window, 659px in a 740px one and 650px in a 700px one, so the headline never
   needs touching. */
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("trade gate fits short viewports")
