import io, sys, re
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 1 · nfbdReveal becomes nfScrollTo, verbatim rule ──────────────────────
start = src.index("  function nfbdReveal(){")
end   = src.index("\n  }\n", start) + len("\n  }\n")
old_reveal = src[start:end]

new_reveal = """  /* ── 1 Sep · THIS IS nfScrollTo, AND NOTHING ELSE ───────────────────────
     Alex: "look how far you've now adjusted the wide panel, it's now at
     extreme bottom of screen rather than be centered ... can you closely
     examine the code for 'find out more' and replicate it."

     Read properly, the coffee dossier's entire scroll behaviour is three
     lines, called once, 260ms after landing:

         function nfScrollTo(el){ if(!el) return;
           var fs = document.querySelector('.nf-focus-sec');
           if(fs){ var t = fs.scrollTop
                     + (el.getBoundingClientRect().top - fs.getBoundingClientRect().top)
                     - 100;
             fs.scrollTo({top:Math.max(0,t), behavior:'smooth'}); }
           else { window.scrollTo({top:Math.max(0, el.getBoundingClientRect().top
                     + window.scrollY - 100), behavior:'smooth'}); } }

     It puts the element's TOP 100px below the top of the scroller. That is
     all. No sticky-bar reservation, no "bring the foot into view", no headroom
     cap, no minimum-movement threshold — every one of which I invented, and
     each of which was the cause of a bug Alex then had to report:

       · reserving the bar -> reserved 133px for a bar the panel had hidden
       · aligning on the FOOT -> a tall panel gets shoved to the extreme bottom
         of the screen, which is what he is looking at now
       · measuring before the disclosure settled -> two visible adjustments

     The foot-based rule was written to keep the panel's total clear of the
     sticky bar. That problem no longer exists: the bar stands down while the
     panel is open. So the special case goes, and this becomes the same three
     lines the coffee dossier uses, with the same 100px offset. */
  function nfbdReveal(){ nfbdScroll(doss); }
"""

src = src[:start] + new_reveal + src[end:]

# ── 2 · and nfbdScroll matches the origin exactly: 100, not 90 ────────────
src = src.replace(
"""      var t = fs.scrollTop + (el.getBoundingClientRect().top - fs.getBoundingClientRect().top) - 90;
      try{ fs.scrollTo({top:Math.max(0,t), behavior:'smooth'}); }catch(e){ fs.scrollTop = Math.max(0,t); }
    } else {
      try{ window.scrollTo({top:Math.max(0, el.getBoundingClientRect().top + window.scrollY - 90), behavior:'smooth'}); }catch(e){}""",
"""      /* 100, not 90 — the origin's number. Harvested components keep their
         constants; this one had drifted by 10px for no recorded reason. */
      var t = fs.scrollTop + (el.getBoundingClientRect().top - fs.getBoundingClientRect().top) - 100;
      try{ fs.scrollTo({top:Math.max(0,t), behavior:'smooth'}); }catch(e){ fs.scrollTop = Math.max(0,t); }
    } else {
      try{ window.scrollTo({top:Math.max(0, el.getBoundingClientRect().top + window.scrollY - 100), behavior:'smooth'}); }catch(e){}""")

# ── 3 · the card disclosure uses the same rule, on the card, once ─────────
s2 = src.index("      if(c.__open) (function(){")
e2 = src.index("      })();", s2) + len("      })();\n")
src = src[:s2] + """      /* ── 1 Sep · SAME RULE, ONE CALL ──────────────────────────────────
         The coffee carousel does exactly this when its detail cell opens:
         nfScrollTo(vp) — put the thing's TOP 100px down, once. So does this,
         on the CARD, once the disclosure has actually finished opening.

         v1 measured the panel's foot twice (next frame and 500ms) because the
         height is not known until the transition ends. That produced the double
         adjustment Alex reported, and the second measurement was also the one
         that shoved things to the bottom of the screen. transitionend on
         max-height is the honest signal; the timer is only a fallback for a
         browser that swallows it or a reduced-motion setting where the
         transition never runs. Whichever arrives first disarms the other. */
      if(c.__open) (function(){
        var panel = c.querySelector('.q-eq-panel');
        var done = false;
        var go = function(){
          if(done) return; done = true;
          if(panel) panel.removeEventListener('transitionend', onT);
          clearTimeout(fb);
          /* the PANEL, not the card. nfScrollTo puts a target's top 100px
             down; on the card that leaves the list hanging past the fold,
             because card + panel is ~760px tall. The reader pressed a control
             to see a list, so the list is what gets put at the top — which is
             also what the coffee carousel ends up doing, since opening Details
             replaces the row with the thing you opened. */
          if(c.__open && window.__nfBringInto)
            window.__nfBringInto(c.querySelector('.q-eq-panel') || c);
        };
        var onT = function(e){ if(e.propertyName === 'max-height') go(); };
        if(panel) panel.addEventListener('transitionend', onT);
        var fb = setTimeout(go, 620);
      })();
""" + src[e2:]

# ── 4 · __nfBringInto is nfScrollTo too ──────────────────────────────────
s3 = src.index("  window.__nfBringInto = function(el, minMove){")
e3 = src.index("\n  };\n", s3) + len("\n  };\n")
src = src[:s3] + """  /* the same three lines again, exposed so the card's own disclosure can use
     the one rule this file scrolls by. Deliberately NOT a second algorithm. */
  window.__nfBringInto = function(el){ nfbdScroll(el); };
""" + src[e3:]

io.open(F, "w", encoding="utf-8").write(src)
print("scroll behaviour replaced with nfScrollTo, verbatim")
