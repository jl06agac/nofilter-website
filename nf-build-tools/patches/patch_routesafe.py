import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 113 · TWO COMPONENTS THAT ASSUME THE WHOLE PAGE IS PRESENT ═════════════
# Found by splitting the site into one page per route (the Option C prototype,
# 4 Sep) and reading the console instead of trusting the render. With the other
# five routes stripped out, exactly TWO statements throw. A thrown error kills
# every line after it in its script block, so each of these was silently
# blanking whole sections that had nothing to do with the shop or the machines.
#
# Both are the same mistake: reach for an element, use it without checking.
# Everything else in this file already guards properly — 20 of the 22 script
# blocks that touch a route's elements touch exactly ONE route, and the big
# 144KB block turned out to be 210 separate IIFEs, every one of them
# single-route. The codebase was already separable; these two lines were the
# only thing standing in the way.
#
# Harmless on the current one-page site: when #shopGrid and #mxBack are present
# the guards are no-ops. They cost nothing and they make the page survive being
# split, which is the whole question the router work is trying to answer.

# ── 1 · the shop product grid ─────────────────────────────────────────────
fix("var shopGrid = $('#shopGrid');\nORIGINS.forEach(function(o, i){",
    "var shopGrid = $('#shopGrid');\n"
    "/* 113: absent whenever the shop section is not on this page */\n"
    "if (shopGrid) ORIGINS.forEach(function(o, i){")

# ── 2 · the machine specs overlay ─────────────────────────────────────────
fix("  document.getElementById('mxBack').addEventListener('click',close);",
    "  /* 113: absent whenever the machine specs overlay is not on this page */\n"
    "  var mxBack = document.getElementById('mxBack');\n"
    "  if (mxBack) mxBack.addEventListener('click',close);")

# ── 3 · a GLOBAL utility that was living inside the home route ─────────────
# window.__nfRelayout is defined inside <section id="home"> and called from
# three places OUTSIDE any route. On the one-page site that works by accident:
# home is always in the document, so the definition is always there. Split the
# pages and every route except home loses a function three global callers need.
#
# It is hoisted into its own global script before the routes, which is where a
# window.* utility belonged in the first place. The definition is moved, not
# copied — leaving both would be two sources of truth for one function.
RELAYOUT = """window.__nfRelayout = function(el, fn){
  if(!el || !el.isConnected) return;
  if(!el.getClientRects().length) return;   /* hidden: the ResizeObserver has it */
  if(el.__nfPend) return;                   /* one chain, not one per caller */
  el.__nfPend = true;
  requestAnimationFrame(function(){ el.__nfPend = false; fn(); });
};"""
n = src.count(RELAYOUT)
assert n == 1, "__nfRelayout definition not found exactly once (%d)" % n
src = src.replace(RELAYOUT, "/* 113: hoisted out of #home to a global block, see below */", 1)
anchor = "<main class=\"shell\" id=\"shell\">"
assert src.count(anchor) == 1, "shell anchor moved"
src = src.replace(anchor,
    "<script>/* 113 \u00b7 global utility, hoisted out of the home route so every "
    "page has it */\n" + RELAYOUT + "\n</script>\n" + anchor, 1)

# ── 4 · a quote-page element written to from global code ──────────────────
# #sheetRef lives in the quote route; this line runs on every page.
fix("$('#sheetRef').textContent = QREF;",
    "var _sheetRef = $('#sheetRef');\n"
    "if (_sheetRef) _sheetRef.textContent = QREF;   /* 113: quote route only */")

# ── 5 · the quote console registers listeners from global scope ───────────
# 26 element references belonging to the quote route are made from code that
# sits OUTSIDE that route. Most are inside handlers that can only fire once the
# quote page is on screen, so they are unreachable rather than broken. Four run
# at load and throw, and each throw kills the rest of its block.
#
# Guarded at the registration, not the element: if the control is not on this
# page there is nothing to listen to. No behaviour changes where it is present.
for _el, _old, _new in (
  ("jumpSend",
   "$('#jumpSend').addEventListener('click', function(ev){",
   "var _jump = $('#jumpSend');\nif (_jump) _jump.addEventListener('click', function(ev){"),
  ("resetQuote",
   "$('#resetQuote').addEventListener('click', function(){",
   "var _reset = $('#resetQuote');\nif (_reset) _reset.addEventListener('click', function(){"),
  ("accEnter",
   "  $('#accEnter').addEventListener('click', openGate);",
   "  var _accEnter = $('#accEnter');\n  if (_accEnter) _accEnter.addEventListener('click', openGate);"),
  ("uniTrack",
   "    document.getElementById('uniTrack').addEventListener('mousedown',onDown);",
   "    var _uniTrack = document.getElementById('uniTrack');\n"
   "    if (_uniTrack) _uniTrack.addEventListener('mousedown',onDown);"),
):
    fix(_old, _new)

# ── 6 · the price slider ──────────────────────────────────────────────────
# Module B of the quote console, same class as the four above and the last one
# that throws at load. Found by fixing the others first: each throw hides the
# next, so they surface one at a time and the only way to know you are done is
# to keep running the page until the console is clean.
fix("var slider = $('#priceSlider');\n"
    "slider.addEventListener('input', function(){ Q.price = parseFloat(slider.value); recalc(); });",
    "var slider = $('#priceSlider');\n"
    "if (slider) slider.addEventListener('input', function(){ Q.price = parseFloat(slider.value); recalc(); });")

# ── 7 · recalc() paints the quote console from global scope ───────────────
# Guarding its seven writes line by line was the wrong shape: the whole body of
# recalc() is quote-console painting. One early return replaces six guards and
# still returns the computed figure to any caller, so nothing downstream changes.
fix("function recalc(){\n  var c = compute();",
    "function recalc(){\n  var c = compute();\n"
    "  /* 113: the quote console is not on this page — compute, paint nothing */\n"
    "  if (!document.getElementById('kgTotalHd')) return c;")

# ── 8 · the machine dossier card mount ────────────────────────────────────
import re as _re
_m = _re.search(r'^(\s*)mcards\.appendChild\(c\);', src, _re.M)
assert _m, "mcards mount not found"
fix(_m.group(0), "%sif (mcards) mcards.appendChild(c);" % _m.group(1))

# ── 9 · the router assumed every route is in the document ─────────────────
# go() falls back to 'home' for an unknown route and then toggles 'on' off
# every section that is not it. On a split page that means go('home') running
# on /shop switches the shop section off and leaves a blank page. It now falls
# back to the route that IS present. On the one-page site every route is there,
# so this branch can never be reached — it costs one lookup at boot.
fix("function go(r, push){\n  if(ROUTES.indexOf(r) < 0) r = 'home';",
    "function go(r, push){\n  if(ROUTES.indexOf(r) < 0) r = 'home';\n"
    "  /* 113: on a split build only one route is in the document. If the route\n"
    "     asked for is not here, the one that IS here is this page. */\n"
    "  if(!document.getElementById(r)){\n"
    "    var only = document.querySelector('.route');\n"
    "    if(only) r = only.id;\n"
    "  }")

# ── 10 · the machine grid ─────────────────────────────────────────────────
# Same family as #1. It only surfaced once the route boundaries were being read
# correctly: a regex depth-counter had been closing the work route 78 KB early,
# so 83 KB of work-route markup — the machine grid among it — was surviving on
# every page and #machGrid was always present by accident. Fix the boundaries
# and the real dependency appears. Boundaries are now read with an HTML parser.
import re as _re2
_m2 = _re2.search(r"^(\s*)machGrid\.appendChild\(el\);", src, _re2.M)
assert _m2, "machGrid mount not found"
fix(_m2.group(0), "%sif (machGrid) machGrid.appendChild(el);" % _m2.group(1))

# ── 11 · the two table bodies ─────────────────────────────────────────────
# machTb is $('#machTable tbody'), svcTb is $('#svcTable tbody'). Same family as
# the grids above: bound at load, appended to unconditionally. These were the
# last two. Found the only way that works — split the pages, run all five, fix
# the first error, run again, and repeat until the console is silent on every
# one of them. Each throw hides the next, so there is no way to know you are
# finished except to keep running it.
for _pat in (r"^(\s*)machTb\.appendChild\(tr\);", r"^(\s*)svcTb\.appendChild\(tr\);"):
    _m3 = _re2.search(_pat, src, _re2.M)
    assert _m3, "table body mount not found: %s" % _pat
    _var = "machTb" if "machTb" in _pat else "svcTb"
    fix(_m3.group(0), "%sif (%s) %s.appendChild(tr);" % (_m3.group(1), _var, _var))

# ── 12 · the delegated link handler ───────────────────────────────────────
# Found the only way it could be: Alex clicked ORIGINS on a split page and got
# the address bar saying /origins with the home page still on screen.
#
# The site catches every click on a link whose href resolves to a known route,
# calls preventDefault and switches section in place. That is what makes the
# one-page site feel instant, and while all six sections are in the document it
# is right. Once the pages are split it is wrong: the nav's href is a real URL
# to a different file, the section it names is not in this document, and
# swallowing the click leaves the visitor on the page they were already on
# while replaceState rewrites the URL to say otherwise.
#
# So: check the route is actually here before handling it ourselves. On the
# one-page site getElementById always finds it and nothing changes — verified
# by clicking all five nav links on the live bundle and on a guarded build of
# the same master: identical route, URL, section count and zero errors on both.
# On a split page it hands the click back to the browser. 48 click transitions
# across both domains: 40 failed before this line, 0 after.
fix("  if(r === null || (href && href.charAt(0) === '#')) return;    "
    "/* hash links have their own handler */\n"
    "  ev.preventDefault();",
    "  if(r === null || (href && href.charAt(0) === '#')) return;    "
    "/* hash links have their own handler */\n"
    "  if(!document.getElementById(r)) return;   "
    "/* not on this page - let the browser navigate */\n"
    "  ev.preventDefault();")

io.open(F, "w", encoding="utf-8").write(src)
print("12 route-safety fixes: the page survives being split")
