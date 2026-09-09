import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

OLD = """      if(mode === 'purchase' && !c.__buyInit){
        c.__buyInit = true;
        Q.m[m.k].cooler = Q.m[m.k].svc = Q.m[m.k].wrap = Q.m[m.k].counter = false;
      }"""
NEW = """      if(mode === 'purchase' && !c.__buyInit){
        c.__buyInit = true;
        /* 1 Sep — THE FRIDGE IS STANDARD; EVERYTHING ELSE STARTS OFF.
           Alex: "i think we need to make the milk fridge with machine the
           standard, if they want to opt out then fine but otherwise the price
           should include it." That sat unactioned because it reads against the
           rule directly above it — a purchase opening on the largest number and
           asking a nervous reader to work downwards. Both hold, and they only
           looked like a conflict because I had lumped the fridge in with the
           genuine extras.

           It is not one. Every rental includes it, and this build's own
           like-for-like copy says why: "No fresh-milk drinks without one." A
           machine quoted without a fridge is not a cheaper machine, it is one
           that cannot make half its menu — so a purchase that starts without it
           opens on the not-like-for-like warning instead of on an offer.

           The reader still is not shown the maximum: cover, wrap and counter all
           start off and the figure only ever goes up from 9,100. And it earns
           300 a unit rather than costing anything (cost 500, sells 800). */
        Q.m[m.k].cooler = true;
        Q.m[m.k].svc = Q.m[m.k].wrap = Q.m[m.k].counter = false;
      }"""
assert src.count(OLD) == 1, "default anchor not unique: %d" % src.count(OLD)
io.open(F, "w", encoding="utf-8").write(src.replace(OLD, NEW))
print("default changed: fridge on")
