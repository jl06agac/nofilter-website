import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 46 · A STEP NEVER SCROLLS BY A HAIR ───────────────────────────────────
# Alex's own reading at 1059x812 (his real window — I had been testing at
# 1512x1250 and should have asked for his size three rounds earlier):
#
#   deckOverflowY 18 · escapers [] · screenMinH 778px
#
# Nothing was escaping. The step's content was simply 18px taller than the
# space, so it scrolled 18px — far too little to reveal anything and far too
# much to feel still. My own repro at that size found the same shape on step 1:
# 2px. That is the whole complaint in miniature. A scroll range you cannot read
# anything in is not a scroll range, it is looseness.
#
# The fix is not to clip it and not to raise the "close enough" threshold until
# real content gets hidden. It is to take the difference out of the GAPS, which
# are decorative, before it is allowed to become scroll. The step's top padding
# and the forward bar's padding are breathing room sized by a vh clamp; at a
# short window that clamp is generous by more than the shortfall. So a small
# overflow is absorbed there, proportionally, down to hard floors — and if the
# floors are reached and it still does not fit, the step scrolls honestly,
# because then the content really is too tall.
#
# Bounded at 56px on purpose. Beyond that the step is genuinely overfull (the
# quote letter on the last step runs ~300px past an 812px window) and squeezing
# padding would only cramp it without solving anything.
old = """        var a = f.querySelector('.deck-screen.is-active');
        if(!a) return;
        var slack = f.scrollHeight - f.clientHeight;
        if(slack > 0 && slack <= 3){
          s = parseFloat(a.style.minHeight) || 0;
          a.style.minHeight = Math.max(0, s - slack) + 'px';
        }"""
new = """        var a = f.querySelector('.deck-screen.is-active');
        if(!a) return;

        /* the gaps give way before the reader has to scroll — see block 46.
           Reset EVERY screen first, not just this one. Caught immediately in
           test: the padding rule is scoped to .is-active, so an inactive screen
           normally contributes none — but an INLINE padding left behind by a
           previous squeeze outlives the class, and a height:0 box still stacks
           its padding. Each step visited pushed the next one's offsetTop down
           another 16px (34 → 50 → 65 → 81). Same ratchet as the offsetTop bug
           one block up, arriving by a different door. */
        var act = a.querySelector('.deck-actions');
        var __all = f.querySelectorAll('.deck-screen'), __j;
        for(__j = 0; __j < __all.length; __j++){
          __all[__j].style.paddingTop = '';
          var __ab = __all[__j].querySelector('.deck-actions');
          if(__ab){ __ab.style.paddingTop = ''; __ab.style.paddingBottom = ''; }
        }

        var slack = f.scrollHeight - f.clientHeight;
        if(slack > 0 && slack <= 56){
          /* each gap offers what it has above its floor */
          var pt  = parseFloat(getComputedStyle(a).paddingTop) || 0;
          var apt = act ? (parseFloat(getComputedStyle(act).paddingTop) || 0) : 0;
          var apb = act ? (parseFloat(getComputedStyle(act).paddingBottom) || 0) : 0;
          var give = [ [a,   'paddingTop',    pt,  8],
                       [act, 'paddingTop',    apt, 8],
                       [act, 'paddingBottom', apb, 10] ];
          var pool = 0, i2;
          for(i2 = 0; i2 < give.length; i2++){
            if(give[i2][0]) pool += Math.max(0, give[i2][2] - give[i2][3]);
          }
          if(pool > 0){
            var take = Math.min(slack, pool);
            for(i2 = 0; i2 < give.length; i2++){
              var g = give[i2];
              if(!g[0]) continue;
              var room = Math.max(0, g[2] - g[3]);
              if(!room) continue;
              g[0].style[g[1]] = (g[2] - room * (take / pool)).toFixed(2) + 'px';
            }
          }
          slack = f.scrollHeight - f.clientHeight;
        }

        /* and the last pixel or two, which come from the beat around the screen
           rounding up independently of the screen itself */
        if(slack > 0 && slack <= 3){
          s = parseFloat(a.style.minHeight) || 0;
          a.style.minHeight = Math.max(0, s - slack) + 'px';
        }"""
assert src.count(old) == 1, "correction anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("hair-width scroll absorbed into the gaps")
