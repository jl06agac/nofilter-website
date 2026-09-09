import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

CSS = r'''
/* ── 59d · two things the first render showed ─────────────────────────────
   1 · .q-val is white-space:nowrap, which is right for a figure and wrong for
       a sentence. On the inclusions column the value is sometimes a clause —
       "included with the cooler & servicing plan", "NOT INCLUDED — plan
       declined" — and an unbreakable clause squeezed "Live Impact Screen" onto
       two lines and pushed its own subtext into a narrow gutter. Figures still
       never break; only the inclusion clauses do, and they get a ceiling so the
       label always keeps half the row.
   2 · the taste options were inheriting the manifest's mono-uppercase
       treatment, so "Showroom tasting" arrived as SHOWROOM TASTING. They are
       option cards now and read as prose. */
/* scoped to the INCLUSIONS column only — selected by a row that exists only
   there. Letting every value wrap broke "SGD 48.00 /kg" across two lines in the
   coffee card, which is the opposite of the problem being solved: a figure and
   its unit are one token, a clause is not. */
.q-settle .stl-col:has(#qRowTablet) .q-val{white-space:normal;max-width:58%;text-align:right;}
.q-settle .stl-col:has(#qRowTablet) .q-lab{flex:1 1 auto;min-width:0;}

.q-settle .q-taste-t{font-family:var(--font-s,inherit);text-transform:none;
  letter-spacing:normal;font-size:12.5px;}
/* the descriptions are prose too — they were arriving as mono uppercase with
   the rest of the manifest, which is right for a status and wrong for a
   sentence a reader is being asked to choose between */
.q-settle .q-taste-opt span{color:#CCCCCC;font-family:var(--font-s,inherit);
  text-transform:none;letter-spacing:normal;font-size:12px;line-height:1.55;}
.q-settle .q-taste-opt input{margin-top:2px;flex:0 0 auto;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("value wrapping and taste-card typography")
