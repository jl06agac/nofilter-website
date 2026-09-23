import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 118 · THE FOOTER, TIGHTENED (23 Sep 2026) ═════════════════════════════════
# Alex: "it's huge". 443px for four short columns and a row of icons, most of it
# air: the FAQ link on its own line, generous column padding. Now 277px. Orange
# stays an accent, not a field: a 3px signal rule where the footer begins, the
# live market value in orange, icon hovers in orange. The wordmark is the CDN
# orange SVG and is untouched. The FAQ link is injected by faq/wire_links.py
# after build-ship; its rules are addressed with .foot .foot-links so they win
# regardless of where that stylesheet lands.
fix(""".foot-grid{column-gap:clamp(18px,2.2vw,36px);}
@media(max-width:1080px){""",
""".foot-grid{column-gap:clamp(18px,2.2vw,36px);}
/* 118: tightened. Padding trimmed, the FAQ link in the top row opposite the
   wordmark, a signal rule at the top, the live market value in signal. */
.foot{padding-top:0!important;padding-bottom:clamp(18px,2.4vh,28px)!important;border-top:0;}
.foot::before{content:"";display:block;height:3px;background:var(--signal);}
.foot-grid{padding-top:clamp(18px,2.2vw,26px);row-gap:16px;grid-template-columns:auto minmax(0,1fr) auto;}
.foot-brand{align-self:center;}
.foot-contact{grid-column:2;grid-row:1;}
.foot .foot-links{padding-top:0;grid-column:3;grid-row:1;justify-self:end;align-self:center;}
.foot .foot-links a{color:rgba(244,242,238,.7);}
.foot-entities{padding-top:clamp(14px,1.6vw,20px);gap:clamp(16px,3vw,56px);}
.foot-ent p{line-height:1.7;}
.foot-ent .region{color:rgba(244,242,238,.5);}
.foot-ent-mkt p{color:var(--signal);}
.foot-copy{margin-top:16px;}
.foot .fc-ico:hover{border-color:var(--signal);color:var(--signal);background:rgba(238,77,23,.08);}
@media(max-width:1080px){
  .foot .foot-links{grid-column:1/-1;grid-row:auto;justify-self:start;}""")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_footer OK")
