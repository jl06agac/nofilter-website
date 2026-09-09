import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 80 · THE COFFEE TILE'S FOOT, IN THE MACHINE CARD'S GRAMMAR ════════════
# Alex, 2 Sep: "still feel our details tap to add styling is weak here
# comparatively" — step 1's tiles end in a 9px mono "TAP TO ADD" beside an
# outlined DETAILS pill; step 2's cards end in a black pill with the figure
# left and a solid Add control right, and put "See full details" on the photo
# as a hover bar. Same builder, two grammars. Step 1 takes step 2's:
#   · Details becomes the rotated hover bar on the photo (touch: a resting
#     pill), the same .mx-specs-btn treatment, class kept so the existing
#     click binding and the tile's closest('.cx-details') guard still hold.
#   · The foot becomes the black 46px pill: status hard left in the deck's
#     mono caps, a solid "Add +" chip hard right. Picked: the pill turns to
#     the light face like a machine that is in the fleet, status "In order",
#     chip becomes "Remove −". The tile click still toggles — the chip is a
#     face of the same control, not a second one.
# The shop's copy of this tile (line ~22488) is untouched.

# ── 1 · markup: Details onto the photo, foot as a pill ────────────────────
old = """            +'<div class="cx-photo"><img src="'+c.img+'" alt="'+c.name+'" loading="lazy" onerror="this.style.opacity=0"></div>'
            +'<div class="cx-name">'+c.name+'</div>'"""
new = """            +'<div class="cx-photo"><img src="'+c.img+'" alt="'+c.name+'" loading="lazy" onerror="this.style.opacity=0">'
            /* block 80 — details rides the photo, as on the machine cards */
            +'<button class="cx-details" type="button" aria-label="Details for '+c.name+'"><span>Details</span></button></div>'
            +'<div class="cx-name">'+c.name+'</div>'"""
assert src.count(old) == 2, "photo anchor count %d" % src.count(old)
# only the DECK's build (the first occurrence); the shop keeps its own
i = src.index(old)
src = src[:i] + new + src[i+len(old):]

old = """            +'<div class="cx-foot"><span class="cx-status">'+(c.on?'In order':'Tap to add')+'</span>'
            +'<button class="cx-details" type="button">Details</button></div></div>';"""
new = """            +'<div class="cx-foot"><span class="cx-status">'+(c.on?'In order':'Tap to add')+'</span>'
            +'<span class="cx-cta" aria-hidden="true"><span class="cx-cta-add">Add <b>+</b></span><span class="cx-cta-rm">Remove <b>&minus;</b></span></span></div></div>';"""
assert src.count(old) == 1, "foot anchor count %d" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 80 · COFFEE TILE FOOT = MACHINE CARD FOOT ═══════════════════════════ */
/* the pill */
.nf-console-wrap .cx-foot{
  display:flex;align-items:center;justify-content:space-between;gap:10px;
  width:100%;height:46px;margin:9px 0 0;padding:0 5px 0 16px;box-sizing:border-box;
  border:1.5px solid var(--nb,#1A1815);border-radius:99px;
  background:var(--nb,#1A1815);color:var(--cr,#F4F2EE);
  transition:background .2s ease,color .2s ease,border-color .2s ease;
}
.nf-console-wrap .cx-status{
  font-family:var(--font-m,monospace);font-size:9.5px;letter-spacing:.14em;
  text-transform:uppercase;color:inherit;opacity:.85;white-space:nowrap;
}
.nf-console-wrap .cx-cta{
  display:flex;align-items:center;flex:0 0 auto;
  font-family:var(--font-b,sans-serif);font-size:12.5px;font-weight:600;line-height:1;
  background:rgba(244,242,238,.15);border-radius:99px;padding:8px 15px;
  transition:background .15s ease;
}
.nf-console-wrap .cx-cta b{font-weight:600;font-size:16px;line-height:1;margin-left:7px;opacity:.75;}
.nf-console-wrap .cx-cta-rm{display:none;}
.nf-console-wrap .cx-tile:hover .cx-cta{background:rgba(244,242,238,.26);}
/* the picked face — the light pill a machine in the fleet wears */
.nf-console-wrap .cx-tile.is-picked .cx-foot{
  background:rgba(26,24,21,.055);color:var(--nb,#1A1815);border-color:rgba(26,24,21,.22);}
.nf-console-wrap .cx-tile.is-picked .cx-status{color:var(--or,#ed3326);opacity:1;}
.nf-console-wrap .cx-tile.is-picked .cx-cta{background:rgba(26,24,21,.08);color:var(--nb,#1A1815);}
.nf-console-wrap .cx-tile.is-picked:hover .cx-cta{background:rgba(26,24,21,.14);}
.nf-console-wrap .cx-tile.is-picked .cx-cta-add{display:none;}
.nf-console-wrap .cx-tile.is-picked .cx-cta-rm{display:inline;}
.nf-console-wrap .cx-tile:focus-visible .cx-foot{outline:2px solid var(--or,#ed3326);outline-offset:2px;}

/* the details bar on the photo — the machine card's hover bar, verbatim in
   shape: full height, 34px, rotated label, slides in from the right */
.nf-console-wrap .cx-photo{overflow:hidden;}
.nf-console-wrap .cx-photo .cx-details{
  position:absolute;top:0;right:0;bottom:0;left:auto;width:34px;height:100%;
  margin:0;padding:0;border:0;border-radius:0;z-index:2;flex:none;
  background:var(--nb,#1A1815);cursor:pointer;display:grid;place-items:center;
  transform:translateX(100%);
  transition:transform .26s cubic-bezier(.4,0,.2,1),background .16s ease;
}
.nf-console-wrap .cx-photo .cx-details::after{content:none;}
.nf-console-wrap .cx-photo .cx-details span{
  writing-mode:vertical-rl;transform:rotate(180deg);
  font-family:var(--font-m,monospace);font-size:9.5px;letter-spacing:.14em;
  text-transform:uppercase;white-space:nowrap;color:#F4F2EE;
}
.nf-console-wrap .cx-photo:hover .cx-details,
.nf-console-wrap .cx-photo .cx-details:focus-visible{transform:translateX(0);}
.nf-console-wrap .cx-photo .cx-details:hover{background:#000;color:#F4F2EE;border-color:transparent;}
.nf-console-wrap .cx-photo .cx-details:focus-visible{outline:2px solid var(--or,#ed3326);outline-offset:-2px;}
/* the tile that has its dossier open keeps the bar out, as the machine card
   keeps its bar out while its sheet is open */
.nf-console-wrap .cx-tile.is-active .cx-photo .cx-details{transform:translateX(0);background:var(--or,#ed3326);}
@media (hover:none){
  .nf-console-wrap .cx-photo .cx-details{
    transform:none;top:auto;left:auto;right:8px;bottom:8px;width:auto;height:auto;
    padding:7px 11px;border-radius:99px;background:rgba(26,24,21,.85);}
  .nf-console-wrap .cx-photo .cx-details span{writing-mode:horizontal-tb;transform:none;}
}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("tile foot restyled")
