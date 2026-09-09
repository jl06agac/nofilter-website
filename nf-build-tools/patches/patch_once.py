import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

old = """  function nfbdScroll(el){
    if(!el) return;
    var fs = document.querySelector('.nf-focus-sec');"""

new = """  /* ── 1 Sep · ONE SCROLL PER GESTURE, ENFORCED HERE ──────────────────────
     Alex, from the console:

         SCROLL from 0 -> 28   at nfbdScroll (...:16951)
         SCROLL from 0 -> 573  at nfbdScroll (...:16951)

     Two calls, same line, one gesture — and both read scrollTop 0, because a
     smooth scroll is asynchronous and the first had not moved yet when the
     second was issued. That is the double adjustment, and it is why chasing it
     at the CALL SITES kept failing: there is more than one call site (the
     panel's reveal, the card's disclosure, the close path back to the row) and
     a sequence exists where two of them fire for the same press.

     So it is settled where it can be settled once. Calls inside a 90ms window
     coalesce and the LAST target wins — which is the right one, because the
     later caller knows more about the state than the earlier one. Anything a
     reader would experience as a single action lands well inside 90ms; two
     genuinely separate gestures do not.

     This is deliberately not a "have I scrolled recently" lock. A lock drops
     the second target and leaves the view wherever the first call happened to
     put it, which is how the panel ended up at the bottom of the screen. This
     coalesces instead: one movement, to the destination the last caller asked
     for. */
  var nfbdScrollT = null, nfbdScrollEl = null;
  function nfbdScroll(el){
    if(!el) return;
    nfbdScrollEl = el;
    clearTimeout(nfbdScrollT);
    nfbdScrollT = setTimeout(function(){
      var target = nfbdScrollEl; nfbdScrollEl = null;
      if(target) nfbdScrollNow(target);
    }, 90);
  }
  function nfbdScrollNow(el){
    if(!el) return;
    var fs = document.querySelector('.nf-focus-sec');"""

assert src.count(old) == 1, "nfbdScroll anchor not unique (%d)" % src.count(old)
io.open(F, "w", encoding="utf-8").write(src.replace(old, new))
print("scroll calls coalesced")
