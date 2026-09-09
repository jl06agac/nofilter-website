import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 50 · is-morphing NEVER CAME OFF ON CLOSE ──────────────────────────────
# The whole "i cannot scroll this page at all". Traced on a real journey —
# pick a coffee, configure the CaféMatic 8, Save & add to quote, advance to the
# quote step — with the wheel trace running:
#
#   [nf wheel] {"deltaY":160,"max":442,"scrollTop":0,"running":false,
#               "step":"3","morphing":TRUE,"insideDeck":true}   ×12
#
# 442px of range, twelve gestures, nothing moves. The deck was never the
# problem and neither was the quote screen: close_() ADDS is-morphing at the
# top of the close animation and nothing ever takes it off again. The 1080ms
# tail restores transform and opacity and leaves the class sitting there for
# the rest of the session.
#
# It was harmless for a year because its only job was CSS — hiding .nfbd-body
# and .nfbd-shot during the flight, invisible once the panel is shut. Then I
# made three systems ask about it:
#
#   · the wheel shim treats it as "a morph is in flight, swallow this gesture"
#     → every wheel dead, on every step, from the first close onward
#   · nfbdScroll's flight hold re-queues itself every 120ms while it is set
#     → the panel's own positioning never fires again either
#   · nfbdSync is gated on it → the panel stops syncing on reopen
#
# One stuck class, three dead systems, and none of them noticed because the
# class is legitimate on the way in. So: take it off where it should always
# have come off — and stop the readers trusting it on its own.
#
# 1 · CLOSE CLEARS IT, on both paths.
old = """    setTimeout(function(){
      if(openK) return;
      doss.style.transition = 'none'; doss.style.transform = ''; doss.style.opacity = '';
    }, 1080);
  }"""
new = """    setTimeout(function(){
      if(openK) return;
      doss.style.transition = 'none'; doss.style.transform = ''; doss.style.opacity = '';
      /* 1 Sep — and the flight flag comes off with it. See block 50: this line
         is the one that was missing, and its absence killed scrolling for the
         whole session the first time a panel was closed. */
      doss.classList.remove('is-morphing');
    }, 1080);
  }"""
assert src.count(old) == 1, "close tail anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """    if(reduce){
      doss.style.transition = 'none'; doss.style.maxHeight = '0px';
      doss.classList.remove('is-open');
      nfbdScroll(document.getElementById('mcards'));
      return;
    }"""
new = """    if(reduce){
      doss.style.transition = 'none'; doss.style.maxHeight = '0px';
      doss.classList.remove('is-open','is-morphing');
      nfbdScroll(document.getElementById('mcards'));
      return;
    }"""
assert src.count(old) == 1, "reduce branch anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# 2 · AND THE READERS STOP TRUSTING THE CLASS ON ITS OWN. A morph only exists
#     while the panel is open; once it is shut there is nothing in flight
#     whatever the class says. Cheap, and it means a future stray class can
#     never take scrolling away again.
old = """      if(doss.classList.contains('is-morphing')){ e.preventDefault(); return; }"""
new = """      /* is-open too — a morph cannot be in flight over a closed panel, and
         trusting the class alone is what block 50 is about. */
      if(doss.classList.contains('is-morphing') && doss.classList.contains('is-open')){
        e.preventDefault(); return;
      }"""
assert src.count(old) == 1, "wheel morph guard anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """      if(doss.classList.contains('is-morphing')){
        nfbdScrollT = setTimeout(run, 120);
        return;
      }"""
new = """      if(doss.classList.contains('is-morphing') && doss.classList.contains('is-open')){
        /* and never wait forever: the hold is for a flight, and a flight that
           has not landed in two seconds is not going to. */
        if(!run.__t0) run.__t0 = Date.now();
        if(Date.now() - run.__t0 < 2000){
          nfbdScrollT = setTimeout(run, 120);
          return;
        }
      }
      run.__t0 = 0;"""
assert src.count(old) == 1, "scroll hold anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

old = """        if(openK && !doss.classList.contains('is-morphing')) nfbdSync();"""
new = """        if(openK && !(doss.classList.contains('is-morphing') && doss.classList.contains('is-open'))) nfbdSync();"""
assert src.count(old) == 1, "sync gate anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("is-morphing cleared on close; readers no longer trust it alone")
