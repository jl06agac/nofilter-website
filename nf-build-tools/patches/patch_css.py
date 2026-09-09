import io, sys

F = "/Users/alexanderclark/Desktop/NoFilter/Marketing/NoFilter-Website/NoFilter-Website-Master.html"
F = sys.argv[1] if len(sys.argv) > 1 else F

CSS = r'''
/* ── 23 · THE PURCHASE DOSSIER ────────────────────────────────────────────
   Alex, 31 Aug: "i'm saying the draw can open downwards, i.e. exactly like our
   more details for our coffee selection" — then: "implement this into the
   master, i want to see it with imagery".

   He means the DOSSIER, not the detail card: the full-width accordion that
   opens BENEATH the row. Everything I had built before this — the squeeze, the
   split view, the leftward canvas push — was solving occlusion, and this
   pattern has none. Nothing is covered, so nothing is squeezed, slid or dimmed.

   HARVESTED, NOT IMITATED. Every value below comes from .cx-dossier / .cx-morph
   in this same file (the choose-your-coffees component, itself a verbatim lift
   from Marketing/NoFilter-Website/shop.html):

     panel      max-height 0 → measured scrollHeight
                          .55s cubic-bezier(.5,0,.15,1);  margin-top → 44px
     proxy · 1  descend   top .38s cubic-bezier(.45,0,.35,1)
                (150ms beat)
     proxy · 2  expand    left/width/height/border-radius
                          .52s cubic-bezier(.4,0,.15,1)
     children   opacity + translateY(12px), delays .04 .09 .14 .19 .24 .29 .34

   WHY IT EARNS ITS PLACE, in one number: the in-card disclosure gave the three
   servicing rungs a 291px column, which is what clipped "2 years" and started
   this whole thread. The dossier gives them the full row width. They sit side
   by side and the choice is one glance instead of three cramped buttons.

   SCOPING — the trap this file has already been bitten by. The console portals
   itself to <body> when the focus deck opens, so #nfConsoleWrap-scoped rules
   keep matching (the wrap travels with it) but anything parked directly on
   <body> does not. The flying proxy IS parked on <body>, exactly as .cx-morph
   and the price-slider gutters are, so its rules are deliberately UNSCOPED.
   Do not "tidy" .nfbd-morph under #nfConsoleWrap — it will stop matching and
   the descent becomes invisible. */

#nfConsoleWrap #nfBuyDoss{
  max-height:0;overflow:hidden;border-radius:18px;margin:0 auto;width:100%;
  color:#F4F2EE;
  transition:max-height .55s cubic-bezier(.5,0,.15,1),margin-top .5s ease;
  box-shadow:0 30px 70px -30px rgba(26,24,21,.5);
}
#nfConsoleWrap #nfBuyDoss.is-open{margin-top:34px;}
#nfConsoleWrap #nfBuyDoss.is-flying{opacity:0;}
#nfConsoleWrap .nfbd-sheet{position:relative;border-radius:18px;overflow:hidden;
  background:var(--nb,#1A1815);}

/* UNSCOPED ON PURPOSE — see the scoping note above. */
.nfbd-morph{position:fixed;z-index:900;border-radius:14px;pointer-events:none;
  display:none;opacity:0;overflow:hidden;
  box-shadow:0 34px 80px -34px rgba(26,24,21,.55);
  will-change:left,top,width,height;}

/* the staggered arrival, .cx-db > * verbatim */
#nfConsoleWrap .nfbd-body>*{transition:opacity .45s ease,transform .5s cubic-bezier(.4,0,.2,1);}
#nfConsoleWrap .nfbd-body>*:nth-child(1){transition-delay:.04s}
#nfConsoleWrap .nfbd-body>*:nth-child(2){transition-delay:.09s}
#nfConsoleWrap .nfbd-body>*:nth-child(3){transition-delay:.14s}
#nfConsoleWrap .nfbd-body>*:nth-child(4){transition-delay:.19s}
#nfConsoleWrap .nfbd-body>*:nth-child(5){transition-delay:.24s}
#nfConsoleWrap .nfbd-body>*:nth-child(6){transition-delay:.29s}
#nfConsoleWrap .nfbd-body>*:nth-child(7){transition-delay:.34s}
#nfConsoleWrap #nfBuyDoss.is-morphing .nfbd-body>*{opacity:0;transform:translateY(12px);}
#nfConsoleWrap .nfbd-shot{transition:opacity .55s ease,clip-path .65s cubic-bezier(.4,0,.2,1);
  clip-path:inset(0 0 0 0);}
#nfConsoleWrap #nfBuyDoss.is-morphing .nfbd-shot{opacity:0;clip-path:inset(0 100% 0 0);}

/* .cx-drow is 60/40 film-to-body. A configurator needs more than 40, so 36/64.
   Ratio only — the grid itself is the component's. */
#nfConsoleWrap .nfbd-row{display:grid;grid-template-columns:36% minmax(0,1fr);align-items:center;}
@media(max-width:980px){#nfConsoleWrap .nfbd-row{grid-template-columns:1fr;}}
#nfConsoleWrap .nfbd-frame{padding:22px;}
/* THE PHOTO WELL IS CREAM, NOT BLACK — and that is not a whim. The coffee
   dossier can use a #0c0c0b video well because its sheet is a saturated origin
   colour, so the well reads as a frame cut into it. Our machine shots
   (cafematic-*-w1400.webp) are product photography on a cream ground of
   #F0E9DE, which on an ink sheet would be a pale rectangle floating in the
   dark. So the well is GIVEN that cream instead: the photo's own ground runs
   out to the frame edge and the machine sits in a lit panel inset in a dark
   sheet — the same figure/ground relationship as the coffee dossier, inverted. */
#nfConsoleWrap .nfbd-shot{position:relative;overflow:hidden;border-radius:12px;
  background:#F0E9DE;aspect-ratio:1/1;
  box-shadow:0 16px 40px -20px rgba(0,0,0,.55);}
#nfConsoleWrap .nfbd-shot img{position:absolute;inset:0;width:100%;height:100%;
  object-fit:contain;display:block;}
#nfConsoleWrap .nfbd-shotk{position:absolute;left:14px;bottom:12px;
  font-family:var(--mono,monospace);font-size:9.5px;letter-spacing:.14em;
  text-transform:uppercase;color:rgba(26,24,21,.5);}
#nfConsoleWrap .nfbd-body{padding:30px 34px 30px clamp(6px,1vw,14px);align-self:center;}
#nfConsoleWrap .nfbd-close{position:absolute;top:14px;right:16px;z-index:4;
  font-family:var(--mono,monospace);font-size:10px;letter-spacing:.1em;
  text-transform:uppercase;background:rgba(0,0,0,.24);border:none;border-radius:7px;
  color:#F4F2EE;padding:8px 12px;cursor:pointer;opacity:.85;
  transition:opacity .15s,background .15s;}
#nfConsoleWrap .nfbd-close:hover{opacity:1;background:rgba(0,0,0,.36);}

#nfConsoleWrap .nfbd-eyebrow{font-family:var(--mono,monospace);font-size:10px;
  letter-spacing:.16em;text-transform:uppercase;opacity:.8;margin:0 0 9px;}
/* line-height .9 is the component's, but its names carry no accents.
   CAFEMATIC does, and at .9 the acute on the E clips. 1.0 costs nothing. */
#nfConsoleWrap .nfbd-name{font-family:var(--disp,sans-serif);font-weight:900;
  text-transform:uppercase;line-height:1;letter-spacing:-.01em;
  font-size:clamp(28px,3.1vw,42px);margin:0 0 14px;}
#nfConsoleWrap .nfbd-qrow{display:flex;align-items:center;gap:13px;margin:0 0 20px;flex-wrap:wrap;}
#nfConsoleWrap .nfbd-qty{display:inline-flex;align-items:center;gap:11px;
  border:1.4px solid rgba(244,242,238,.5);border-radius:10px;padding:6px 11px;}
#nfConsoleWrap .nfbd-qty button{width:26px;height:26px;border:none;border-radius:6px;
  background:rgba(244,242,238,.16);color:#F4F2EE;font-size:16px;line-height:1;
  cursor:pointer;transition:background .15s;}
#nfConsoleWrap .nfbd-qty button:hover{background:rgba(244,242,238,.32);}
#nfConsoleWrap .nfbd-qty b{font-family:var(--mono,monospace);font-size:13px;
  min-width:16px;text-align:center;font-weight:400;}
#nfConsoleWrap .nfbd-qnote{font-family:var(--mono,monospace);font-size:10px;
  letter-spacing:.06em;text-transform:uppercase;color:rgba(255,232,195,.65);}
#nfConsoleWrap .nfbd-sect{font-family:var(--mono,monospace);font-size:9.5px;
  letter-spacing:.14em;text-transform:uppercase;color:rgba(255,232,195,.55);margin:0 0 10px;}

/* THE PAYOFF — three rungs ACROSS. In the card they had 291px between them and
   "2 years" clipped; here they have the row. */
#nfConsoleWrap .nfbd-covs{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:0 0 20px;}
#nfConsoleWrap .nfbd-cov{background:rgba(244,242,238,.07);
  border:1.5px solid rgba(244,242,238,.18);border-radius:12px;padding:13px 13px 12px;
  cursor:pointer;position:relative;text-align:left;color:inherit;font-family:inherit;
  transition:background .18s,border-color .18s;}
#nfConsoleWrap .nfbd-cov:hover{background:rgba(244,242,238,.13);}
/* SELECTION IS CARRIED BY GROUND, BORDER AND A TICK — never by hue. Alex is
   red-green colourblind, so the lit rung inverts to a solid cream panel: it is
   the brightest thing in the group whatever the reader's colour vision. */
#nfConsoleWrap .nfbd-cov.is-on{background:#F4F2EE;color:var(--nb,#1A1815);border-color:#F4F2EE;}
#nfConsoleWrap .nfbd-cov .yr{font-family:var(--body,sans-serif);font-size:11px;
  letter-spacing:.04em;text-transform:uppercase;opacity:.72;display:block;margin:0 0 5px;}
#nfConsoleWrap .nfbd-cov .pr{font-family:var(--disp,sans-serif);font-weight:900;
  font-size:23px;letter-spacing:-.02em;line-height:1;margin:0 0 1px;}
#nfConsoleWrap .nfbd-cov .pm{font-family:var(--mono,monospace);font-size:9.5px;
  letter-spacing:.04em;opacity:.7;display:block;margin:0 0 9px;}
#nfConsoleWrap .nfbd-cov ul{margin:0;padding:9px 0 0;list-style:none;
  border-top:1px solid currentColor;opacity:.85;}
#nfConsoleWrap .nfbd-cov li{font-size:11px;line-height:1.42;margin:0 0 4px;
  padding-left:12px;position:relative;}
#nfConsoleWrap .nfbd-cov li:before{content:"";position:absolute;left:0;top:6px;
  width:4px;height:4px;border-radius:50%;background:currentColor;opacity:.6;}
#nfConsoleWrap .nfbd-cov .rec{position:absolute;top:-8px;left:11px;
  font-family:var(--mono,monospace);font-size:8.5px;letter-spacing:.11em;
  text-transform:uppercase;background:var(--or,#ed3326);color:#fff;
  border-radius:99px;padding:3px 9px;}
#nfConsoleWrap .nfbd-cov .tick{position:absolute;top:10px;right:11px;width:17px;height:17px;
  border-radius:50%;border:1.5px solid currentColor;opacity:.35;}
#nfConsoleWrap .nfbd-cov.is-on .tick{opacity:1;background:var(--nb,#1A1815);
  border-color:var(--nb,#1A1815);}
#nfConsoleWrap .nfbd-cov.is-on .tick:after{content:"";position:absolute;left:5px;top:3px;
  width:4px;height:8px;border:solid #F4F2EE;border-width:0 1.8px 1.8px 0;transform:rotate(42deg);}

/* EXTRAS, WITH THE THUMBNAILS ALEX ASKED FOR. From his design critique:
   "interactive add-on cards with micro-thumbnails ... switch toggles". A row
   rather than a stack, so the two sit beside each other at a glance. */
#nfConsoleWrap .nfbd-extras{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:0 0 20px;}
@media(max-width:1120px){#nfConsoleWrap .nfbd-extras{grid-template-columns:repeat(2,1fr);}}
#nfConsoleWrap .nfbd-ex{display:flex;align-items:center;gap:10px;
  border:1.4px solid rgba(244,242,238,.2);border-radius:11px;padding:8px 11px 8px 8px;
  cursor:pointer;transition:border-color .18s,background .18s;text-align:left;
  background:none;color:inherit;font-family:inherit;}
#nfConsoleWrap .nfbd-ex:hover{border-color:rgba(244,242,238,.45);background:rgba(244,242,238,.05);}
#nfConsoleWrap .nfbd-ex.is-on{border-color:rgba(244,242,238,.7);background:rgba(244,242,238,.1);}
#nfConsoleWrap .nfbd-th{width:46px;height:46px;flex:0 0 auto;border-radius:8px;overflow:hidden;
  background:#F0E9DE;position:relative;}
#nfConsoleWrap .nfbd-th img{width:100%;height:100%;object-fit:cover;display:block;}
/* the fridge has no photograph yet — it says so rather than borrowing one */
#nfConsoleWrap .nfbd-th.is-todo{background:rgba(244,242,238,.1);display:grid;place-items:center;
  border:1px dashed rgba(244,242,238,.3);}
#nfConsoleWrap .nfbd-th.is-todo:after{content:"photo";font-family:var(--mono,monospace);
  font-size:7.5px;letter-spacing:.08em;text-transform:uppercase;color:rgba(244,242,238,.5);}
#nfConsoleWrap .nfbd-ex .txt{flex:1;min-width:0;}
/* both are spans, so both need making blocks — as inlines they ran together and
   the row read "Fresh-milk fridgeUndercounter · SGD 800.00" on one wrapped line.
   Spans rather than p/div because a <p> inside a <button> is invalid markup and
   the browser closes the button early, which silently kills the toggle. */
#nfConsoleWrap .nfbd-ex .t{display:block;font-size:12.5px;font-weight:600;margin:0 0 2px;
  line-height:1.25;}
#nfConsoleWrap .nfbd-ex .d{display:block;font-family:var(--mono,monospace);font-size:9.5px;
  letter-spacing:.04em;color:rgba(255,232,195,.62);margin:0;line-height:1.3;}
#nfConsoleWrap .nfbd-sw{width:36px;height:21px;border-radius:99px;
  background:rgba(244,242,238,.22);position:relative;flex:0 0 auto;transition:background .2s ease;}
#nfConsoleWrap .nfbd-sw i{position:absolute;top:3px;left:3px;width:15px;height:15px;
  border-radius:50%;background:#fff;transition:transform .22s cubic-bezier(.32,.72,0,1);}
#nfConsoleWrap .nfbd-ex.is-on .nfbd-sw{background:#F4F2EE;}
#nfConsoleWrap .nfbd-ex.is-on .nfbd-sw i{transform:translateX(15px);background:var(--nb,#1A1815);}

#nfConsoleWrap .nfbd-buy{display:flex;align-items:flex-end;justify-content:space-between;
  gap:20px;flex-wrap:wrap;border-top:1px solid rgba(244,242,238,.2);padding-top:18px;}
#nfConsoleWrap .nfbd-price small{font-family:var(--mono,monospace);font-size:10px;
  font-weight:400;letter-spacing:.09em;text-transform:uppercase;
  color:rgba(255,232,195,.6);display:block;margin-bottom:5px;}
#nfConsoleWrap .nfbd-price b{font-family:var(--disp,sans-serif);font-weight:900;
  font-size:clamp(28px,3vw,38px);line-height:1;letter-spacing:-.02em;display:block;}
#nfConsoleWrap .nfbd-per{font-family:var(--mono,monospace);font-size:10.5px;
  letter-spacing:.05em;color:rgba(255,232,195,.7);margin:6px 0 0;}
#nfConsoleWrap .nfbd-done{font-family:var(--body,sans-serif);font-size:15px;font-weight:700;
  color:#fff;background:var(--or,#ed3326);border:none;border-radius:12px;padding:14px 24px;
  cursor:pointer;display:inline-flex;align-items:center;gap:9px;
  box-shadow:0 10px 26px rgba(238,77,23,.28);transition:transform .1s,filter .15s;white-space:nowrap;}
#nfConsoleWrap .nfbd-done:hover{filter:brightness(1.05);transform:translateY(-1px);}
#nfConsoleWrap .nfbd-done:active{transform:scale(.98);}
#nfConsoleWrap .nfbd-vs{font-family:var(--mono,monospace);font-size:10.5px;letter-spacing:.04em;
  color:rgba(255,232,195,.65);margin:11px 0 0;width:100%;}
#nfConsoleWrap .nfbd-vs b{color:#F4F2EE;font-weight:400;}

/* THE CARD'S OWN PURCHASE TAIL STANDS DOWN. Everything the in-card disclosure
   was cramming into 291px now has the full row, so leaving both would be the
   same information twice — the duplication this pass has cut three times
   already. Rental is untouched and keeps its "What you get" list exactly as it
   is; only .is-buy loses the tail. */
#nfConsoleWrap .q-eq-card.is-buy .q-eq-incl{display:none;}

/* ── 23b · THE DOSSIER IS A SELF-COLOURED ISLAND ──────────────────────────
   THE SAME FAULT THAT HIT THE COFFEE DOSSIER, AND FOR THE SAME REASON. See the
   note at "THE PICKER IS A SELF-COLOURED ISLAND" above: this panel lives inside
   a beat tagged data-ground="paper", and the paper ground repaints h2/h3/p to
   ink so ordinary copy reads on cream. The dossier is a DARK panel that happens
   to sit inside that beat, so its heading and every <p> in it were being painted
   #1A1815 on a #1A1815 sheet — the machine name, the eyebrow and all three
   servicing prices rendered invisible. Caught in the first render.

   Listed explicitly rather than with a blanket * so the component's own
   exceptions still win — the lit rung inverts to ink on cream and must not be
   dragged back to cream on cream, which a blanket rule would do. */
.beat[data-ground="paper"] #nfBuyDoss,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-eyebrow,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-name,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-qnote,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-cov:not(.is-on),
.beat[data-ground="paper"] #nfBuyDoss .nfbd-cov:not(.is-on) .pr,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-cov:not(.is-on) .pm,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-cov:not(.is-on) .yr,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-ex,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-ex .t,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-price,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-price b,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-close{color:#F4F2EE;}
/* and the quiet greys stay quiet rather than snapping to full cream */
.beat[data-ground="paper"] #nfBuyDoss .nfbd-sect,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-per,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-vs,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-ex .d{color:rgba(255,232,195,.65);}
/* the LIT rung is the one thing on this sheet that is legitimately ink, and it
   is stated last so nothing above can take it back */
.beat[data-ground="paper"] #nfBuyDoss .nfbd-cov.is-on,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-cov.is-on .pr,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-cov.is-on .pm,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-cov.is-on .yr,
#nfConsoleWrap .nfbd-cov.is-on,
#nfConsoleWrap .nfbd-cov.is-on .pr,
#nfConsoleWrap .nfbd-cov.is-on .pm,
#nfConsoleWrap .nfbd-cov.is-on .yr{color:var(--nb,#1A1815);}
/* the machine name must not inherit this build's display h3 treatment either */
#nfConsoleWrap .nfbd-name,
.beat[data-ground="paper"] #nfBuyDoss .nfbd-name{margin:0 0 14px;}
#nfConsoleWrap .nfbd-cov .pr{margin:0 0 1px;}

@media(prefers-reduced-motion:reduce){
  #nfConsoleWrap #nfBuyDoss{transition:opacity .3s ease;}
  #nfConsoleWrap .nfbd-body>*,#nfConsoleWrap .nfbd-shot{transition-duration:.01ms;transition-delay:0ms;}
}
'''

src = io.open(F, encoding="utf-8").read()
if "#nfBuyDoss" in src:
    print("ALREADY PATCHED — css skipped"); sys.exit(0)

lines = src.split("\n")
# the sheet that carries blocks 14-22 is <style id="nf-es-cover">; find its close
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("css inserted before line", end + 1)
