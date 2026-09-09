import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 65 · THE GRID PASS ════════════════════════════════════════════════════
# Alex's restructuring list. Everything here is layout and copy except the last
# item, which is a promise — see the note on the disclaimer below.

# ── A · the impact box moves to the middle column ─────────────────────────
# It is authored in the coffee run, so the settle transform sweeps it into
# column one with the rows above it. Rather than re-author the sheet — the
# printable letter wants it where it is, next to the lines it explains — it is
# relocated after the manifest is built, which is the same place the send card
# is already re-parented. Column two is found by the row it owns, not by index:
# a column order that changes must not silently move this somewhere else.
old = """    if(sendCard){ sendCard.classList.add('q-submit-dark'); manifest.appendChild(sendCard); }"""
new = """    /* block 65 — the pass-through panel joins MACHINES & SERVICING, which is the
       shortest column and was leaving a black void under it. Nothing about the
       figure changes; it is the same node, moved. */
    (function(){
      var ngo = sheetEl.querySelector('.q-ngo');
      if(!ngo) return;
      var cols = manifest.querySelectorAll('.stl-col');
      for(var i = 0; i < cols.length; i++){
        if(cols[i].querySelector('#qMachRows')){ cols[i].appendChild(ngo); return; }
      }
    })();

    if(sendCard){ sendCard.classList.add('q-submit-dark'); manifest.appendChild(sendCard); }"""
assert src.count(old) == 1, "sendcard anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── B · copy ──────────────────────────────────────────────────────────────
subs = [
("""<span class="q-sub">Tree planting in the Cinta Raja corridor &mdash; rainforest restoration built into every account</span>""",
 """<span class="q-sub">Tree sapling planting in the Cinta Raja corridor &mdash; rainforest restoration built into every account</span>"""),
("""                    SEND PROPOSAL TO MY EMAIL <span class="ar">→</span></button>""",
 """                    SUBMIT PROPOSAL &amp; EMAIL ME A COPY <span class="ar">→</span></button>"""),
]

# ── C · the disclaimer ────────────────────────────────────────────────────
# Replaced as asked, and flagged rather than argued: the line it replaces was
# there because the form did not send. It does now — nfQuoteSubmit posts the
# lead to Netlify Forms AND asks netlify/functions/quote-confirm to email the
# reader — but the second of those is fire-and-forget and only works on a deploy
# where RESEND_API_KEY is set. On a file:// preview, and on any deploy without
# that key, the lead is still captured and the email is not sent. So this copy
# is true in production and false in preview, which is the right way round; it
# is worth confirming Resend is live before this goes up, because the sentence
# now promises something the page cannot verify for itself.
subs.append((
"""              <div class="lab" style="margin-top:12px;line-height:1.7">Nothing is sent yet &mdash;
                this is a preview, so pressing send lays your quote out below instead of
                emailing it.</div>""",
"""              <div class="lab q-send-note">A copy of this proposal will be sent to your
                email, and our team will be in touch within 1 business day.</div>"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:60])
    src = src.replace(old, new)

CSS = r'''
/* ── 65 · the grid pass ───────────────────────────────────────────────────
   Rows tighten, the form goes inline, and the two taste options sit side by
   side. Every measure here is about getting the form above the fold on a
   1000px window without taking anything off the page. */

/* the inclusions column: 12/14 down to 10/12, ~80px off the column */
.nf-console-wrap.nf-focus-sec .q-settle .stl-col:has(#qRowTablet) .q-line{
  padding:10px 0 12px;}

/* the form, on a six-track grid: 3+3 then 2+2+2 */
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .frm{
  display:grid;grid-template-columns:repeat(6,1fr);gap:12px 14px;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld{grid-column:span 6;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(1),
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(2){grid-column:span 3;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(3),
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(4),
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(5){grid-column:span 2;}
.nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld.full{grid-column:1/-1;}
/* below ~900px of card width the three-up row stops being readable and the
   pairs take over */
@media(max-width:1180px){
  .nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(3),
  .nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(4),
  .nf-console-wrap.nf-focus-sec .q-settle #sendPanel .fld:nth-of-type(5){grid-column:span 3;}
}

/* the two tasting options, side by side, equal height */
.nf-console-wrap.nf-focus-sec .q-settle .q-taste{
  display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:stretch;}
.nf-console-wrap.nf-focus-sec .q-settle .q-taste-hd{grid-column:1/-1;}
.nf-console-wrap.nf-focus-sec .q-settle .q-taste-opt{margin-top:0;height:100%;}
/* the border-top separator was for a stacked pair and reads as a stray rule
   once they are beside each other */
.nf-console-wrap.nf-focus-sec .q-settle .q-taste-opt+.q-taste-opt{
  border-top:1px solid rgba(244,239,226,.18);margin-top:0;padding-top:11px;}
@media(max-width:820px){
  .nf-console-wrap.nf-focus-sec .q-settle .q-taste{grid-template-columns:1fr;}
}

/* the note under the button: one centred line, at the contrast the rest of the
   card uses */
.nf-console-wrap.nf-focus-sec .q-settle .q-send-note{
  margin-top:12px;text-align:center;color:#CCCCCC;
  font-family:var(--body,'Archivo',system-ui,sans-serif);
  font-size:11.5px;line-height:1.6;letter-spacing:normal;text-transform:none;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("grid pass applied")
