import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

OLD_TICK = """    raf = 0;
    var dx = tx - x, dy = ty - y;"""
NEW_TICK = """    raf = 0;
    lastTick = performance.now();   /* the watchdog below judges by this, not by `raf` */
    var dx = tx - x, dy = ty - y;"""

OLD = """  addEventListener('mousemove', move, {passive:true});"""
NEW = """  /* CAPTURE PHASE, 1 Sep. This sat on the bubble phase at window level, which
     makes it the LAST listener in the document to see a mousemove — so anything
     anywhere below that calls stopPropagation on a move event silences the
     cursor completely. Nothing in this file does today; capture makes it
     impossible for anything added later to. Costs nothing. */
  addEventListener('mousemove', move, {passive:true, capture:true});"""

OLD2 = """  addEventListener('visibilitychange', function(){ if(!document.hidden) raf = 0; });
  addEventListener('focus', function(){ raf = 0; });"""

NEW2 = """  var lastTick = 0;                 /* hoisted: tick() above stamps it every frame */
  addEventListener('visibilitychange', function(){ if(!document.hidden) raf = 0; });
  addEventListener('focus', function(){ raf = 0; });

  /* ══ THE STALL WATCHDOG ══════════════════════════════════════════════════
     Alex, 1 Sep: "my cursor hover, i.e. the + sometimes gets trapped, for
     example in the photo, it's a bit unpro."

     I COULD NOT REPRODUCE IT, and would rather say so than invent a cause.
     Driven across a machine photo in nine real steps the follower tracked to
     within 1px the whole way, and the three structural suspects all came back
     clean: .nfcur already carries pointer-events:none so it cannot catch
     itself; nothing in this file calls stopPropagation on a move event; and
     tick() has cleared its own handle on entry since the last freeze fix, so a
     throw inside it costs one frame rather than the session.

     So this guards the FAILURE MODE instead, which is knowable and is the same
     whatever triggers it: the drawn position stops agreeing with the pointer
     and no frame arrives to close the gap. That is what happens when a
     scheduled callback is dropped rather than delivered — a compositor stall, a
     long task, a dropped frame while the console portals itself to <body> —
     because move() sees a non-zero `raf`, reasonably declines to schedule a
     second one, and then nothing is left to notice that the first never came.

     IT MUST NOT TRUST `raf`, AND THE FIRST VERSION DID. It opened with
     `if(raf) return`, which is the very handle whose staleness is the fault;
     under a forced stall it declined to act forever and reproduced the freeze
     it existed to cure. The test caught that. It therefore judges by whether
     tick has actually RUN. A live chain runs every frame, so "no tick for
     400ms" means there is no live chain whatever the handle claims — which is
     also why overwriting the handle here cannot leave two loops running in any
     state a person could perceive.

     Four times a second, and in the healthy case it is two subtractions and a
     comparison that schedule nothing. This does not mask a stall — frames are
     still dropped — it stops a dropped frame from being permanent, which is
     the part that reads as unprofessional. */
  setInterval(function(){
    if(!root.classList.contains('nfcur-live')) return;
    if(Math.abs(tx - x) < 0.5 && Math.abs(ty - y) < 0.5) return;   /* settled, correctly */
    if(performance.now() - lastTick < 400) return;                 /* a chain really is running */
    raf = requestAnimationFrame(tick);                             /* stale handle and all */
  }, 250);
  /* free kicks from signals that mean the pointer is certainly alive but that
     carry no position of their own */
  addEventListener('pointerover', function(){ if(!raf) raf = requestAnimationFrame(tick); }, {passive:true});
  addEventListener('wheel',       function(){ if(!raf) raf = requestAnimationFrame(tick); }, {passive:true});"""

for name, o in (("tick", OLD_TICK), ("mousemove", OLD), ("watchdog", OLD2)):
    assert src.count(o) == 1, "%s anchor not unique: %d" % (name, src.count(o))
src = src.replace(OLD_TICK, NEW_TICK).replace(OLD, NEW).replace(OLD2, NEW2)

io.open(F, "w", encoding="utf-8").write(src)
print("cursor watchdog installed")
