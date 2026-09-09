import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

old = """    var mo = ensureMorph(), clone = card.cloneNode(true);
    clone.style.margin = '0'; clone.style.width = '100%'; clone.style.height = '100%';
    clone.style.transition = 'opacity .16s ease';
    mo.innerHTML = ''; mo.appendChild(clone);
    mo.style.background = getComputedStyle(card).backgroundColor || '#FFFDF9';"""

new = """    var mo = ensureMorph(), clone = card.cloneNode(true);
    clone.style.margin = '0'; clone.style.width = '100%'; clone.style.height = '100%';
    clone.style.transition = 'opacity .16s ease';
    mo.innerHTML = ''; mo.appendChild(clone);
    /* ── 1 Sep · THE PROXY HAS TO BECOME THE PANEL, NOT VANISH INTO IT ──────
       Alex: "the machine drop down behaviour to expansion is not replicating
       our 'find out more' coffee drop down behaviour? have you closely examined
       it?"

       Examined properly this time, and there is one difference that accounts
       for the whole feel. In openDossier the proxy's background is set to
       c.color — and buildDossier writes the sheet as
           '<div class="cx-dsheet" style="background:' + c.color + '">'
       THE SAME COLOUR. So from the first frame the flying object already IS the
       dossier; the cloned card fades off the top of it, and when the proxy is
       switched off at landing there is nothing to see, because what was under
       it was the same colour all along.

       Mine could not do that, and I had not noticed: the machine card is cream
       (rgb 255,253,249) and the panel it lands on is ink (rgb 26,24,21).
       Measured mid-flight. So a CREAM rectangle descended, expanded to full
       width still cream, and was then cut to a black panel in one frame at the
       end. That is not a morph, it is a placeholder followed by a jump cut —
       and mid-descent it reads as a stray pale box passing over the row, which
       is what Alex photographed.

       The palette will not let me copy the trick, so this reproduces its
       EFFECT: the proxy takes off as the card, in the card's cream, and
       cross-fades to the sheet's own colour across the same .52s as the width
       and height. It lands already being the panel. */
    var SHEET_BG = (function(){
      var s = doss.querySelector('.nfbd-sheet');
      return (s && getComputedStyle(s).backgroundColor) || '#1A1815';
    })();
    mo.style.background = getComputedStyle(card).backgroundColor || '#FFFDF9';"""

assert src.count(old) == 1, "morph bg anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old2 = """        mo.style.transition = 'left .52s cubic-bezier(.4,0,.15,1), width .52s cubic-bezier(.4,0,.15,1), ' +
                              'height .52s cubic-bezier(.4,0,.15,1), border-radius .52s ease';
        mo.style.left = l.left + 'px'; mo.style.width = l.width + 'px';
        mo.style.height = l.height + 'px'; mo.style.borderRadius = '18px';"""
new2 = """        mo.style.transition = 'left .52s cubic-bezier(.4,0,.15,1), width .52s cubic-bezier(.4,0,.15,1), ' +
                              'height .52s cubic-bezier(.4,0,.15,1), border-radius .52s ease, ' +
                              'background-color .42s ease .06s';
        mo.style.left = l.left + 'px'; mo.style.width = l.width + 'px';
        mo.style.height = l.height + 'px'; mo.style.borderRadius = '18px';
        /* and it arrives as the panel — see SHEET_BG above. Slightly shorter
           than the geometry and started 60ms in, so the colour has settled
           before the box stops moving rather than after it. */
        mo.style.backgroundColor = SHEET_BG;"""

assert src.count(old2) == 1, "expand anchor not unique (%d)" % src.count(old2)
src = src.replace(old2, new2)

io.open(F, "w", encoding="utf-8").write(src)
print("proxy cross-fades into the panel's own colour")
