import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 108 · THE DOSSIER SCROLLS TO WHERE THE BAR WILL BE, NOT WHERE IT IS ════
# The other half of the shop dossier's two-step (see block 107 for the first).
# Wrapping window.scrollTo during an open shows two smooth scrolls to two
# different targets — 103 then 172 on a 1250px window — for the same
# dossier. nfRailGap() adds --lead-bar, the shop lead's measured height: 108px
# while the page is at the top and the lead is its full self, 40px once the
# reader has scrolled and it has pinned as the slim bar. The first scroll,
# fired 260ms after landing with the page at 0, clears a 108px bar that
# will be 40px by the time the page arrives; the 900ms pass then notices the
# panel is 69px short and glides again. The gap is measured against the bar
# as it will be at the destination: a clone of the lead in its pinned state,
# measured and discarded in the same frame, so nothing paints.
fix("""        var lead=document.querySelector('#shop .shop-lead');
        if(lead && document.querySelector('#shop .shop-lead-slot')){
          var v=parseFloat(getComputedStyle(lead.parentElement).getPropertyValue('--lead-bar'));
          if(v) gap += v;
        }
        return gap;""",
    """        var lead=document.querySelector('#shop .shop-lead');
        if(lead && document.querySelector('#shop .shop-lead-slot')){
          var v=parseFloat(getComputedStyle(lead.parentElement).getPropertyValue('--lead-bar'));
          /* block 108 — a panel is scrolled to from above, so by the time the
             page gets there the lead is pinned: clear the PINNED bar, not the
             full one the page is looking at now */
          if(!lead.classList.contains('is-stuck')){
            try{
              var c=lead.cloneNode(true); c.classList.add('is-stuck');
              c.style.cssText='position:fixed;left:0;right:0;top:-9999px;visibility:hidden;pointer-events:none;transition:none';
              lead.parentElement.appendChild(c);
              var ph=c.getBoundingClientRect().height; c.remove();
              if(ph) v=ph;
            }catch(e){}
          }
          if(v) gap += v;
        }
        return gap;""")

# ── and the carousel is cleared once the page has arrived, not before ──────
# Also in both traces: at the instant the morph lands, scrollY snaps to 0 and
# the dossier hops 250–400px up the screen — the card flew to where the
# dossier WAS. "Full clearance" pulls the tile carousel out of flow at landing
# and compensates with scrollBy(-vpSpace); when the page is nearer the top
# than the carousel is tall, the compensation clamps at 0 and the difference
# is a jump. It now happens once the scroll has arrived at the dossier, where
# scrollY is always larger than the carousel, so the compensation is exact and
# nothing on screen moves. If the reader has scrolled back up meanwhile, the
# carousel simply stays.
fix("""          // full clearance: pull the tile carousel out of flow so ONLY the dossier shows; compensate scroll so nothing jumps
          if(vp && vp.style.display!=='none' && !document.querySelector('.nf-focus-sec')){ var vpSpace=vp.getBoundingClientRect().height+(parseFloat(getComputedStyle(vp).marginTop)||0)+(parseFloat(getComputedStyle(vp).marginBottom)||0); vp.style.display='none'; try{ window.scrollBy(0,-vpSpace); }catch(e){} }
          setTimeout(function(){ if(dossierIdx!==i) return; try{ nfScrollTo(dossier); }catch(e){} }, 260);""",
    """          setTimeout(function(){ if(dossierIdx!==i) return; try{ nfScrollTo(dossier); }catch(e){} }, 260);
          /* block 108 — full clearance: pull the tile carousel out of flow so ONLY the dossier shows,
             once the page has arrived and the compensation can be exact */
          setTimeout(function(){
            if(dossierIdx!==i) return;
            if(vp && vp.style.display!=='none' && !document.querySelector('.nf-focus-sec')){
              var vpSpace=vp.getBoundingClientRect().height+(parseFloat(getComputedStyle(vp).marginTop)||0)+(parseFloat(getComputedStyle(vp).marginBottom)||0);
              if(window.scrollY >= vpSpace){
                /* compensate by what actually moved: Chrome's scroll anchoring
                   usually holds the dossier still by itself when content above
                   it is removed, and a fixed -vpSpace on top of that sent the
                   page to 0 (measured) */
                var before=dossier.getBoundingClientRect().top;
                vp.style.display='none';
                var moved=dossier.getBoundingClientRect().top-before;
                if(Math.abs(moved)>0.5){ try{ window.scrollBy(0,moved); }catch(e){} }
              }
            }
          }, 880);""", 2)

io.open(F, "w", encoding="utf-8").write(src)
print("the dossier scrolls to the pinned bar")
