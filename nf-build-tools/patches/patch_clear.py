import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

old = """    var unhideCards = function(){
      var all = document.querySelectorAll('.q-eq-card');
      for(var i = 0; i < all.length; i++){
        all[i].style.opacity = ''; all[i].style.transition = '';
      }
    };
    unhideCards();
    card.style.transition = 'opacity .1s ease';
    card.style.opacity = '0';
    var unhideT = setTimeout(unhideCards, 1400);   /* fires whatever happens */"""

new = """    /* ── 1 Sep · THE ROW IS CLEARED BEFORE THE CARD MOVES ──────────────────
       Alex: "our 'see more details' drop animation never ever crosses over the
       resting tiles above ... the transition is simply wrong and not clearing
       the tiles when it begins animation."

       He is right, and I had it backwards. I traced the coffee flight properly
       this time instead of reasoning about it, and the numbers say plainly why
       it never crosses anything:

         .cx-viewport during openDossier ...... {t:0, b:0, w:0, h:0}
         .cx-detailcard (the flight's origin) . {t:153, h:539}
         morph top over the flight ............ 153 -> 736
         maximum overlap with the tile row .... NONE. The row is not there.

       By the time "Find out more" is pressed the carousel has already collapsed
       into a single detail card — pressing "Details" did that — so the proxy
       descends through empty space. There is nothing to cross. The animation I
       built descends 600px straight through three intact neighbours, because
       our reader presses Configure from the row itself with no detail step in
       between.

       So the row is cleared for the flight and brought back as the proxy
       expands. Fading the GRID rather than the cards one by one is deliberate:
       its box keeps its size so nothing reflows, the origin card goes with it
       so there is no separate hide to get wrong, and the restore is one
       property on one element instead of bookkeeping across four. */
    var grid = document.getElementById('mcards');
    var unhideCards = function(){
      if(grid){ grid.style.opacity = ''; grid.style.transition = ''; }
      var all = document.querySelectorAll('.q-eq-card');
      for(var i = 0; i < all.length; i++){
        all[i].style.opacity = ''; all[i].style.transition = '';
      }
    };
    unhideCards();
    if(grid){
      grid.style.transition = 'opacity .18s ease';
      grid.style.opacity = '0';
    }
    /* safety only — past the watchdog's worst case (1800ms + 760ms expand), so
       it can never restore the row while a healthy flight still owns it */
    var unhideT = setTimeout(unhideCards, 3000);"""

assert src.count(old) == 1, "hide anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old2 = """      /* the row is whole again the moment the proxy stops looking like a card */
      card.style.transition = 'opacity .28s ease';
      card.style.opacity = '1';
      setTimeout(unhideCards, 320);"""
new2 = """      /* ── 1 Sep (2) · THE ROW STAYS DOWN UNTIL THE PROXY IS GONE ─────────
         v1 restored the row here, at expand — reasoning the proxy was "below
         the row" by now. Alex's flight recorder, run on HIS machine on the
         coffee flow, ended that reasoning: the coffee row reads
         rowBottom: 0 on EVERY frame of the flight. Not faded — absent. The
         coffee morph cannot overlap its row because the row has no box while
         the proxy exists. Every overlap screenshot Alex sent shows my
         expand-phase restore: grid at full opacity, proxy still wide on
         screen. Two things that, in the origin component, never coexist.
         So the restore moves to landed(), where the proxy is display:none and
         the real panel is painted. While a proxy exists with any width, the
         row is at opacity 0 — the coffee invariant, kept by construction. */"""
assert src.count(old2) == 1, "expand anchor not unique (%d)" % src.count(old2)
src = src.replace(old2, new2)

# close_ clears the grid too
old3 = """    /* belt and braces for the flight hide — see unhideCards in open_ */
    (function(){ var a = document.querySelectorAll('.q-eq-card');
      for(var i = 0; i < a.length; i++){ a[i].style.opacity = ''; a[i].style.transition = ''; } })();"""
new3 = """    /* belt and braces for the flight hide — see unhideCards in open_ */
    (function(){ var g = document.getElementById('mcards');
      if(g){ g.style.opacity = ''; g.style.transition = ''; }
      var a = document.querySelectorAll('.q-eq-card');
      for(var i = 0; i < a.length; i++){ a[i].style.opacity = ''; a[i].style.transition = ''; } })();"""
assert src.count(old3) == 1, "close anchor not unique (%d)" % src.count(old3)
src = src.replace(old3, new3)

io.open(F, "w", encoding="utf-8").write(src)
print("row cleared for the flight, as the coffee dossier does")
