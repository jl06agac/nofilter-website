import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

old = """  function nfbdSync(){
    if(!openK) return;
    doss.style.transition = 'none';
    doss.style.maxHeight = doss.scrollHeight + 'px';
    void doss.offsetWidth;
    doss.style.transition = '';
  }"""

new = """  function nfbdSync(){
    if(!openK) return;
    doss.style.transition = 'none';
    doss.style.maxHeight = doss.scrollHeight + 'px';
    void doss.offsetWidth;
    doss.style.transition = '';
  }

  /* ── 1 Sep · THE PIN RE-MEASURES ITSELF ──────────────────────────────────
     This panel is a max-height disclosure, so its height is a NUMBER measured
     once and written to the element. Every call site so far has been a state
     change I could see coming — a toggle, a rung, a quantity — and each of
     them calls nfbdSync by hand. The failure mode is everything else: a
     webfont arriving after the panel opened, a longer currency string, a
     browser zoom, an accessibility text size. The content grows, the pin does
     not, and the foot of the panel is silently cut off.

     Caught by the 1.3x letter-spacing stress test, which is the standing proxy
     for exactly this — the container's fallback mono is narrower than real IBM
     Plex Mono, and that gap has bitten twice before. Rather than shave another
     30px of copy to buy slack that the next paragraph spends again, the pin
     now watches the content and re-measures when it moves.

     No loop: nfbdSync writes max-height on the PANEL, and what is observed is
     the SHEET inside it, whose own height depends on its content and not on
     the panel's max-height. The observer is created once and re-pointed after
     each build, because build() replaces the sheet wholesale. */
  var sheetRO = null;
  function nfbdWatch(){
    if(!window.ResizeObserver) return;
    var sheet = doss.querySelector('.nfbd-sheet');
    if(!sheet) return;
    try{
      if(!sheetRO) sheetRO = new ResizeObserver(function(){
        if(openK) nfbdSync();
      });
      sheetRO.disconnect();
      sheetRO.observe(sheet);
    }catch(e){}
  }"""

assert src.count(old) == 1, "nfbdSync anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# call it at the end of build(k) — the sheet is new on every build
old2 = """    doss.innerHTML =
    '<div class="nfbd-sheet">' +"""
assert src.count(old2) == 1
src = src.replace(old2, """    /* nfbdWatch() at the foot of this function re-points the observer at the
       sheet this assignment is about to create. */
    doss.innerHTML =
    '<div class="nfbd-sheet">' +""")

# find the close of build(k): the innerHTML assignment ends with "    '</div>';\n  }"
old3 = """      '</div>' +
    '</div>';
  }"""
assert src.count(old3) == 1, "build tail not unique (%d)" % src.count(old3)
src = src.replace(old3, """      '</div>' +
    '</div>';
    nfbdWatch();
  }""")

io.open(F, "w", encoding="utf-8").write(src)
print("pin re-measures on content change")
