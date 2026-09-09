import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 71 · the CTA in Title Case ────────────────────────────────────────────
old = """                    SUBMIT PROPOSAL &amp; EMAIL ME A COPY <span class="ar">→</span></button>"""
new = """                    Submit Proposal &amp; Email Me a Copy <span class="ar">→</span></button>"""
assert src.count(old) == 1, "cta anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 71 · THE HEADER BANNER SITS OVER ITS COLUMNS ═════════════════════════
   Measured first, at 1512x1250:

     manifest columns   130-534 (cx 332)   552-956 (cx 754)   974-1378 (cx 1176)
     hero cells         cx 419                                cx 1089

   The pair was centred on the card as a whole, so neither figure stood over
   the column it belongs to — COFFEE floated 87px right of the coffee card and
   EQUIPMENT 335px right of the machines one. The hero takes the manifest's own
   grid instead of its own centring, so the two are locked together by
   definition rather than by a number that has to be maintained. */
.nf-console-wrap.nf-focus-sec .q-settle .q-total.stl-hero{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:clamp(12px,1.5vw,18px);
  justify-content:stretch;
}
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero .q-total-cell:nth-of-type(1){grid-column:1;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero .q-total-cell:nth-of-type(2){grid-column:2;}
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero .q-total-cell{text-align:center;}

/* ── the category label ───────────────────────────────────────────────────
   Was rgba(244,239,226,.55) at 9.5px — the dimmest type on the card, over the
   largest figure on it. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero .q-total-lab{
  color:#CCCCCC;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  font-family:var(--body,'Archivo',system-ui,sans-serif);
  margin:0 0 8px;
}

/* ── the unit suffix, on the digits' baseline ─────────────────────────────
   /kg and /mo were 13px mono riding wherever the inline box put them. Baseline
   alignment, 6px of air, 16px, 60%. */
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero .q-total-fig .q-unit{
  vertical-align:baseline;
  margin-left:6px;
  font-size:16px;
  /* colour, not opacity: the inherited colour is ALREADY rgba(...,.55), so an
     opacity of .6 on top of it composited to .33 and made the suffix dimmer
     than before. Stated once, at the 60% asked for. */
  color:rgba(244,239,226,.6);opacity:1;
  letter-spacing:normal;
  font-family:var(--body,'Archivo',system-ui,sans-serif);
}
/* the currency prefix keeps its own weight but stops shouting */
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero .q-total-fig .qcur{
  font-family:var(--body,'Archivo',system-ui,sans-serif);
  font-weight:500;color:rgba(244,239,226,.6);opacity:1;font-size:.42em;letter-spacing:.02em;
  vertical-align:baseline;margin-right:6px;
}

/* ── the one-line subtext ─────────────────────────────────────────────────── */
.nf-console-wrap.nf-focus-sec .q-settle .stl-hero .q-total-note{
  color:#CCCCCC;font-size:12px;margin-top:8px;
  font-family:var(--body,'Archivo',system-ui,sans-serif);
}

/* ── the form labels, the last dark mono run on the card ──────────────────
   Measured at rgba(244,239,226,.65), IBM Plex Mono, 9.5px. Everything else on
   this card had already been lifted; these had not, which is why they kept
   coming back in his review. */
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld label{
  color:#CCCCCC;font-size:11px;letter-spacing:.08em;
  font-family:var(--body,'Archivo',system-ui,sans-serif);
}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld .fld-opt{color:#9A9A9A;}

/* ── the CTA reads as a sentence ──────────────────────────────────────────── */
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel #ctaSend{
  text-transform:none;letter-spacing:.01em;
  font-family:var(--body,'Archivo',system-ui,sans-serif);
  font-size:13px;font-weight:600;
}

/* the border he asked for twice */
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld input,
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld select{border-color:#333333;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld input:hover,
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld select:hover{border-color:#555555;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("banner aligned to the columns")
