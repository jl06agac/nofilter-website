import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 68 · THE PRICE WIZARD PASS ════════════════════════════════════════════

# ── 1 · the outer badge stops arguing with the inner pills ────────────────
# Alex: "The outer badge shows 3 on all screens while the inner pill bar reads
# 1 PRICE, 2 TOP-UP, 3 THE YEAR." Two numbering systems on one screen, both
# correct, contradicting each other. The badge takes a letter per phase, driven
# by the same phase engine that writes the heading, so it can never drift from
# the pills beside it.
old = """    var idN = (i === 2) ? ' id="qStepName"' : '';
    var idC = (i === 2) ? ' id="qStepCopy"' : '';
    head.innerHTML = '<span class="q-step-n">' + (i+1) + '</span>'"""
new = """    var idN = (i === 2) ? ' id="qStepName"' : '';
    var idC = (i === 2) ? ' id="qStepCopy"' : '';
    /* block 68 — the price step is three phases behind one badge, so the badge
       carries the phase letter and the id the engine writes to. */
    var idB = (i === 2) ? ' id="qStepNo"' : '';
    head.innerHTML = '<span class="q-step-n"' + idB + '>' + (i+1) + '</span>'"""
assert src.count(old) == 1, "head anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """      if($('qStepName')) $('qStepName').textContent=phaseTitles[phase];"""
new = """      if($('qStepName')) $('qStepName').textContent=phaseTitles[phase];
      /* block 68 — 3A / 3B / 3C, so the badge and the pill bar agree */
      if($('qStepNo')) $('qStepNo').textContent = '3' + ['A','B','C'][phase];"""
assert src.count(old) == 1, "phase title anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 2 · the year phase gets its side cards ────────────────────────────────
# Alex: "Screens 1 and 2 feature left and right callout cards ... but Screen 3
# drops them, leaving empty black voids on both sides."
#
# HIS RIGHT-HAND COPY IS NOT USED VERBATIM, and this is the same call he made on
# the carbon-offset line. It read: "your annual contribution directly funds
# ranger patrols, seedling nurseries, and composting for the full year." Checked
# against the file: "nursery" and "seedling" appear nowhere, and "ranger patrol"
# appears once, as the alt text on a Gayo Lues photograph — not as a programme
# this contribution funds. Composting is real and is already named on the quote.
# So the card says what the site can stand behind, and names the two things it
# has evidence for. If the patrols and nurseries are real line items at the NGO
# partners, his wording goes back in verbatim and this note comes out.
old = """      var gl=mk('l','What this is','<p>Want to hit a per-cup conservation target?"""
new = """      var __YEARGUTTERS = true;
      var gl=mk('l','What this is','<p>Want to hit a per-cup conservation target?"""
assert src.count(old) == 1, "topup gutter anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """      window.__nfTopupGutters={show:show,hide:hide};
      track.addEventListener('mouseenter',show);"""
new = """      window.__nfTopupGutters={show:show,hide:hide};
      track.addEventListener('mouseenter',show);
      /* ── block 68 · THE YEAR PHASE, framed like the other two ─────────────
         Same mk()/placeGutters mechanism, gated on the year class instead of
         ph-topup. Built here rather than in its own IIFE so it shares the one
         placement routine that already knows where the track and the figure
         are — a second copy of that maths is how the three drift apart. */
      (function(){
        var yl = mk('l','How volume scales',
          '<p>Small per-cup fractions compound fast. As your team drinks coffee, '
          + 'your annual contribution grows with them — you do not have to do anything '
          + 'for it to keep going up.</p>'
          + '<p>The slider is only here to show what a year at that volume looks like.</p>');
        var yr = mk('r','Where the year goes',
          '<p>Whatever this adds up to is paid through to the NGO partner behind each '
          + 'origin you have chosen, on the volume actually supplied — not on this estimate.</p>'
          + '<p>It also covers the work already named on your quote: grounds collected and '
          + 'composted, and tree planting in the Cinta Raja corridor.</p>'
          + '<p>Reconciled against your real kilos and reported once a year.</p>');
        function placeY(){
          /* CAUGHT IN TEST: the year phase does not use the unified track — that
             is the price/top-up instrument and it measures 0x0 here, so the fit
             check failed and the cards never showed. The year's own volume
             slider is the anchor, with the stage as a last resort. */
          var yt = document.getElementById('volCups') || track;
          var r = yt.getBoundingClientRect();
          if(!r.width){ var sg = document.getElementById('morphStage');
            if(sg) r = sg.getBoundingClientRect(); }
          var lw=yl.offsetWidth, rw=yr.offsetWidth;
          if(!((r.left-GAP-lw>8) && (r.right+GAP+rw<innerWidth-8))){
            yl.classList.remove('is-on'); yr.classList.remove('is-on'); return false; }
          yl.style.left=(r.left-GAP-lw)+'px';
          yr.style.left=(r.right+GAP)+'px';
          var fig=document.getElementById('morphFigure');
          var t = fig ? fig.getBoundingClientRect().bottom + 26 : (r.top - 60);
          yl.style.top=t+'px'; yr.style.top=t+'px';
          return true;
        }
        var yon=false;
        function yshow(){ if(!stg || !stg.classList.contains('year')) return;
          if(placeY()){ yon=true; yl.classList.add('is-on'); yr.classList.add('is-on'); } }
        function yhide(){ yon=false; yl.classList.remove('is-on'); yr.classList.remove('is-on'); }
        window.__nfYearGutters={show:yshow,hide:yhide};
        track.addEventListener('mouseenter',yshow);
        track.addEventListener('mouseleave',yhide);
        track.addEventListener('focusin',yshow);
        track.addEventListener('focusout',yhide);
        window.addEventListener('resize',function(){ if(yon) placeY(); });
      })();"""
assert src.count(old) == 1, "topup show anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 3 · copy ──────────────────────────────────────────────────────────────
old = """'¢ a cup · your top-up alone is ' + (d.topUp/100*(1000/18)).toFixed(2)
              + ' a kilo, straight to conservation'"""
new = """'\\u00a2 a cup \\u00b7 your top-up adds +' + (window.__nfCur || 'SGD') + ' '
              + (d.topUp/100*(1000/18)).toFixed(2)
              + ' / kg directly to conservation'"""
if src.count(old) != 1:
    old = old.replace("'¢", "'\\u00a2")
assert src.count(old) == 1, "chip copy anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

CSS = r'''
/* ══ 68 · THE PRICE WIZARD, TYPE AND CONTRAST ═════════════════════════════ */

/* ── the side cards, matched and contained ────────────────────────────────
   Alex: "the right card extends lower than the left card and overflows the
   outer container." They are body-level absolutes anchored to the same top, so
   the taller one simply ran on. Both now share a ceiling measured from where
   they start to the bottom of the stage, and scroll inside it rather than
   past it. */
.mgut{max-height:min(46vh, 420px);overflow-y:auto;overscroll-behavior:contain;}
.mgut::-webkit-scrollbar{width:6px;}
.mgut::-webkit-scrollbar-thumb{background:rgba(244,239,226,.22);border-radius:99px;}

/* ── the floating cards, legible over moving footage ──────────────────────
   Alex asked for backdrop-filter: blur(16px). Worth stating what I found before
   applying it, because my first instinct was to refuse: these cards ALREADY
   blur, at 8px, and have all along. So this is not adding a blur to an
   unblurred panel — it is a radius change on an existing one.
   That matters because of what block 33 measured on this same file: the cost of
   backdrop-filter is proportional to the blurred AREA, not to the radius. The
   area here is unchanged — two cards of roughly 250x290 — so 8px to 16px is
   very close to free, and the 30.9ms-vs-16.6ms result that took the blur off
   step 4's panels does not transfer: those were full-width panels over video,
   these are two small boxes.
   Applied as asked, at his fill and border. */
.mgut{
  background:rgba(18,20,18,.75);
  backdrop-filter:blur(16px);
  -webkit-backdrop-filter:blur(16px);
  border:1px solid rgba(255,255,255,.10);
  border-radius:14px;
}
.mgut p{color:#CCCCCC;font-family:var(--body,'Archivo',system-ui,sans-serif);}
.mgut b{color:#F4EFE2;}
.mgut-eyebrow{color:#F4EFE2;font-family:var(--body,'Archivo',system-ui,sans-serif);
  font-size:11px;letter-spacing:.08em;text-transform:uppercase;}

/* ── mono is for the numbers, and the labels are not numbers ──────────────
   BUILT IN, YOUR TOP-UP, YOUR LIKELY CUPS PER YEAR and the range ends move to
   the sans at 11px / .08em; the figures keep their display face. */
.morph-stage .mfig-lab,.morph-stage .mfig-cap,.morph-stage .uni-cap,
.morph-stage .lead-lab,.morph-stage .mrow-lab,.morph-stage .morph-eyebrow,
.morph-stage .uni-end,.morph-stage .mtick,.morph-stage .morph-cap{
  font-family:var(--body,'Archivo',system-ui,sans-serif);
  font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#CCCCCC;
}
/* the units and the currency sit back from the figure they qualify */
.morph-stage .mfig-cur,.morph-stage .mfig-unit,.morph-stage .mfig-per{
  font-family:var(--body,'Archivo',system-ui,sans-serif);font-weight:500;opacity:.5;
}
/* the operators line up on the figures' centre rather than their baseline */
.morph-stage .mfig-op{display:inline-flex;align-items:center;line-height:1;
  font-size:.52em;opacity:.55;}

/* ── the range labels and every remaining subtext ─────────────────────────── */
.morph-stage .uni-zone,.morph-stage .uni-end,.morph-stage .morph-sub,
.morph-stage .mrow-sub,.morph-stage .mfig-note{color:#CCCCCC;}

/* ── colour roles ─────────────────────────────────────────────────────────
   Orange is the interface: progress pills, the active control, the CTA. Gold is
   the impact figure and nothing else. Stated as rules rather than left to each
   element so a new figure inherits the right one. */
.morph-stage .morph-rail .seg.active .rdot{background:var(--or,#EE4D17);border-color:var(--or,#EE4D17);}
.morph-stage .mfig-imp,.morph-stage .mfig-give,.morph-stage .lead-give{color:#E8B457;}

/* ── the edit links stop touching their values ────────────────────────────
   "Price · SGD 48.00/kg · 7.5% edit" — the link had no space and no signal, so
   it read as part of the figure. A bordered pill, which is a shape rather than
   a colour. */
/* the element is a bare <button> inside .mlchip — chip() builds it with no
   class of its own, which is why my first four guesses at a selector all
   missed. Targeted by structure instead. */
.morph-stage .mlchip > button{
  display:inline-block;margin-left:8px;padding:1px 8px;border-radius:99px;
  border:1px solid rgba(244,239,226,.38);
  font-family:var(--body,'Archivo',system-ui,sans-serif);
  font-size:10px;letter-spacing:.08em;text-transform:uppercase;
  color:#E7E2D6;text-decoration:none;line-height:1.7;
  background:none;cursor:pointer;
}
.morph-stage .mlchip > button:hover{
  border-color:#F4EFE2;color:#FFFFFF;background:rgba(244,239,226,.08);}
.morph-stage .mlchip{color:#CCCCCC;font-family:var(--body,'Archivo',system-ui,sans-serif);}
.morph-stage .mlchip + .mlchip{margin-left:18px;}
'''

lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("wizard pass applied")
