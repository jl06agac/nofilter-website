import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ── 56 · THE CONTACT ICONS RETURN TO THE WORDMARK ────────────────────────
   Alex, 1 Sep, on the master about to replace the live site: "why have you
   changed footer positioning so that icons are now on the right?"

   Worth recording what the check found, because the answer was not what either
   of us assumed. The footer region is byte-identical across every master on his
   disk — PRE-DENSITY 09:19, PRE-C3 10:06, PRE-PRICEPILL 10:31, PRE-SPECLIST
   11:49, PRE-DOSSIER 14:58 and today's build, all 10,806 bytes, md5
   5a683f09b811 — and all 33 .ctc rules match too. The live site is simply an
   older lineage: shop.html and nofilter-site.html carry no <footer> element at
   all. So nothing drifted; the deploy predates this footer. (Older than
   31 Aug 09:19 I cannot see, and did not claim to.)

   He wants the deployed arrangement regardless, which is the right call — the
   master is what ships. Measured before this block at 1512 wide:

     .foot-brand    50 → 823   (773px holding a 73px wordmark)
     .foot-contact  883 → 1462 (icons right-aligned inside it)

   Two free columns of a 1.05fr/1.5fr grid, so the icons ended up a screen-width
   away from the mark they belong to. The brand column now takes only what the
   wordmark needs and the icon row starts where the wordmark ends — the pairing
   Alex asked for on 21 Aug ("nofilter logo needs to align with the icons imo")
   finally reading as one object rather than two edges.

   The entity columns and the colophon below are untouched: they are a separate
   grid row and already run the full width. */
.foot-grid{grid-template-columns:auto minmax(0,1fr);}
.foot-contact{justify-self:start;}
.fc-icons{justify-content:flex-start;}
/* CAUGHT IN TEST: column one stayed 773px wide even set to auto, because the
   © line is a child of the same grid and sits in that column on a later row —
   so the column was being sized by the longest sentence in the footer, not by
   the 73px wordmark. It spans, like the entity row above it, and the column
   collapses to the mark. */
.foot-copy{grid-column:1/-1;}
.foot-entities{grid-column:1/-1;}
/* the gap was sized to separate two far-apart columns; beside the wordmark it
   only has to read as a space */
.foot-grid{column-gap:clamp(18px,2.2vw,36px);}
@media(max-width:1080px){
  /* the stacked breakpoint keeps its own arrangement — the brand already spans
     both columns there, so the icons sit under the mark rather than beside it */
  .foot-grid{grid-template-columns:1fr 1fr;}
}
@media(max-width:720px){.foot-grid{grid-template-columns:1fr;}}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

# ── and the seal spins in the builder too ─────────────────────────────────
# Alex: "pretty sure these badges used to be animated, i.e. the 10%." It is,
# on the shop; this rule switched it off inside the console and is present in
# every backup, so it predates this session. He wants it back. The cost is one
# 22s linear rotate on a ~40px SVG, which is why it never needed switching off.
old = """.nf-console-wrap .cx-seal svg{animation:none;}"""
new = """/* 1 Sep — was animation:none. Alex asked for the seal to turn in the builder
   as it does on the shop; the spin is the same cxSpin the shop card uses, and
   the reduced-motion guard on .cx-mseal above still governs anyone who has
   asked the OS for less movement. */
.nf-console-wrap .cx-seal svg{animation:cxSpin 22s linear infinite;}
@media(prefers-reduced-motion:reduce){.nf-console-wrap .cx-seal svg{animation:none;}}"""
assert src.count(old) == 1, "seal anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("footer icons beside the wordmark; builder seal spins")
