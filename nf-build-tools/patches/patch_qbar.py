import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ── 51 · THE BACK LINK STOPS GHOSTING THROUGH THE QUOTE CARD ─────────────
   Caught while chasing the quote page's "strange glitch, or break, as i scroll
   down". Two faults there; this is the visible one.

   .deck-actions is position:sticky bottom:0 on every step, which is right for
   the steps whose forward button must stay under the hand. The quote step has
   no forward button — it carries only "← back to your impact", and its own
   call to action ("Send me this quote") lives INSIDE the card. So the sticky
   bar has nothing to hold; it just parks a link at the bottom of the window for
   the whole scroll.

   And it parks it UNDERNEATH the card, which since the backdrop-filter removal
   (block 33) is rgba(20,19,17,.82) rather than opaque — so the cream link bleeds
   up through the dark panel as a grey smear across the orange Send button.
   Nothing is broken in the layout; it just looks like something is, which for a
   quote page is the same problem.

   On this step the bar goes back into the flow. It ends up below the card,
   where a "back" belongs once you have read to the bottom, and there is nothing
   left to bleed through. */
#nfConsoleWrap .deck-screen.is-active[data-screen="3"] .deck-actions{
  position:static;
  background:none;
  margin-top:18px;
}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("quote step's back link returned to the flow")
