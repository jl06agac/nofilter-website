import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

old = """              (q > 1 ? '<p class="nfbd-per">' + q + ' &times; ' + CUR() + money(unit) + ' each</p>' : '') +"""
new = """              /* ── 1 Sep · THE PER-UNIT LINE ALWAYS OCCUPIES ITS ROW ──────────
                 Alex: "there's additional clear padding between photo 1 & 2,
                 and the photo of the machine adjusts downwards selecting 2
                 units."
                 Exactly right, and it is the same fault as the add-on toggle
                 and the extras subtext before it: this line only EXISTED at
                 q > 1, so going from one machine to two grew .nfbd-price by a
                 row, which grew the panel, which moved the photograph. Third
                 time this pattern has bitten in one session, so the rule is
                 now explicit — nothing inside this panel may enter or leave
                 the layout in response to a control. It renders in every
                 state; at one machine it is present, reserved and unpainted. */
              '<p class="nfbd-per' + (q > 1 ? '' : ' is-ghost" aria-hidden="true') + '">' +
                (q > 1 ? q + ' &times; ' + CUR() + money(unit) + ' each' : '&nbsp;') + '</p>' +"""

assert src.count(old) == 1, "anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* the reserved per-unit row. &nbsp; holds the line box, visibility:hidden
   keeps it off the page, aria-hidden keeps it out of the reading order. */
#nfConsoleWrap .nfbd-per.is-ghost{visibility:hidden;}
/* reserving the row costs ~21px of panel. A few modest gaps give it back at
   short heights — NOT the total's own figure, which is the number the reader
   came for and stays at full size. (The real headroom came from nfbdReveal no
   longer reserving space for a bar it had already hidden; see that patch.) */
@media(max-height:760px){
  #nfConsoleWrap .nfbd-per{font-size:9.5px;margin-top:3px;}
  #nfConsoleWrap .nfbd-price small{margin-bottom:2px;}
  #nfConsoleWrap .nfbd-covs{margin-bottom:4px;}
  #nfConsoleWrap .nfbd-svc1{margin-bottom:6px;}
  #nfConsoleWrap .nfbd-step--rev{padding-top:6px;}
}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("per-unit row reserved")
