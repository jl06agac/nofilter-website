import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 114 · THE UK MARKET TREE (6-7 Sep) + GBP PRICE-BOARD BUTTON (7 Sep) ══════
# Captured mechanically on 7 Sep 2026 from the diff between build.sh's output
# and the shipped master. These edits had been made directly to the master, so
# the generator no longer reproduced it; this patch closes that gap. Contents:
#   - nfHomeMarket() step 1b: read <meta name="nf-market"> (the /uk pin)
#   - NF_BASE router prefix; pathFor()/refPath()/origin replaceState honour it
#   - ROUTE_META_UK / ORIGIN_META_UK; applyRouteMeta() picks tables by market
#   - marketKey(): data-mkt -> pin -> hostname (the 06b title-overwrite bug)
#   - shop price board: GBP button (data-pbm="UK")
# Anchors are the generated file's own lines with enough context to be unique.

fix('            <button type="button" data-pbm="AE" aria-pressed="false">AED</button>\n          </div>',
    '            <button type="button" data-pbm="AE" aria-pressed="false">AED</button>\n            <button type="button" data-pbm="UK" aria-pressed="false">GBP</button>\n          </div>')

fix('};\n/* paths are pushed only where there is a server to answer them */',
    "};\n/* 6 Sep · the UK equivalents of the two tables above. applyRouteMeta() rewrites\n   the title and description on every client-side route change, and without a\n   UK table it was rewriting the /uk pages' correct served metadata with the\n   SINGAPORE strings — the served HTML said 'Wholesale coffee for UK offices'\n   and the rendered page said 'Wholesale coffee for offices, cafés and hotels'.\n   A crawler that renders JS saw the Singapore title on all ten UK pages.\n   Generated from the UAE tables by the same UAE->UK, AED->GBP substitution\n   that wrote the page heads, so the two cannot disagree. */\nvar ROUTE_META_UK = {\n  home:    { title:'NoFilter — Conservation coffee in the UK',\n             desc:'Single-origin coffee from NGO-led conservation projects on the edge of rainforest still standing. Supplied across the UK, priced in GBP.' },\n  origins: { title:'Coffee origins — Sumatra, Aceh and Myanmar | NoFilter UK',\n             desc:'The four single origins we buy through NGO-led conservation projects, supplied across the UK: Batang Toru, Batang Gadis, Gayo Lues, Arakan.' },\n  shop:    { title:'Shop conservation coffee in the UK — 250 g and 1 kg',\n             desc:'Retail bags of our four single origins in 250 g and 1 kg, shipped within the UK and priced in GBP. The shop opens shortly.' },\n  work:    { title:'Wholesale coffee for UK offices and cafés | NoFilter',\n             desc:'Single-origin conservation coffee supplied by the kilo to offices, cafés and hotels across the UK, with bean-to-cup machines on lease.' },\n  quote:   { title:'Trade pricing in GBP and quote builder | NoFilter',\n             desc:'Choose your coffees and machines, set your cups a year, and see the GBP rate, monthly cost and forest contribution before you send it.' }\n};var ORIGIN_META_UK = {\n  'batang-toru':      { title:'Batang Toru coffee, Tapanuli | NoFilter UK',\n                        desc:'Single-origin coffee from Batang Toru, last refuge of the Tapanuli orangutan, supplied across the UK by the kilo and in 250 g and 1 kg bags.' },\n  'arakan-mountains': { title:'Arakan Mountains coffee, Myanmar | NoFilter UK',\n                        desc:'Single-origin coffee from the Arakan Mountains of Myanmar, bought with Fauna & Flora and the ACCA, and supplied across the UK priced in GBP.' },\n  'batang-gadis':     { title:'Batang Gadis coffee, North Sumatra | NoFilter UK',\n                        desc:'Single-origin coffee from the edge of Batang Gadis National Park, North Sumatra, bought through SRI and supplied across the UK priced in GBP.' },\n  'gayo-lues':        { title:'Gayo Lues coffee, Aceh | NoFilter UK',\n                        desc:'Single-origin coffee from Gayo Lues on the edge of the Leuser Ecosystem in Aceh, supplied across the UK by the kilo and in retail bags.' }\n};\n/* paths are pushed only where there is a server to answer them */")

fix('var openOrigin = null;\nfunction pathFor(r){',
    "var openOrigin = null;\n/* 6 Sep · THE MARKET BASE. The UK is published as a path tree, /uk, not as a\n   domain — a .co.uk pointed at a market with no pages buys nothing, whereas\n   these pages rank on the domain that already does. /ae gets away with bare\n   paths because the .ae host rewrites them; /uk has no host of its own, so\n   every path this router reads or writes is relative to the tree it is in.\n   Otherwise the first nav click leaves the UK behind and lands on SG pricing.\n   Read from the URL rather than the market pin, so a page opened off-domain\n   still routes inside its own tree. Empty on the root and on /ae: unchanged. */\nvar NF_BASE = (function(){\n  try{\n    var p = location.pathname || '/';\n    if(p === '/uk' || p === '/uk/' || p.indexOf('/uk/') === 0) return '/uk';\n  }catch(e){}\n  return '';\n})();\nfunction pathFor(r){")

fix("function pathFor(r){\n  if(r === 'origins' && openOrigin && ORIGIN_META[openOrigin]) return ORIGIN_META[openOrigin].path;\n  return (ROUTE_META[r] && ROUTE_META[r].path) || '/';\n}",
    "function pathFor(r){\n  var p = (r === 'origins' && openOrigin && ORIGIN_META[openOrigin])\n        ? ORIGIN_META[openOrigin].path\n        : ((ROUTE_META[r] && ROUTE_META[r].path) || '/');\n  if(!NF_BASE) return p;\n  return p === '/' ? NF_BASE : NF_BASE + p;\n}")

fix("  if(t.length > 1 && t.charAt(t.length-1) === '/') t = t.slice(0,-1);\n  return t || '/';",
    "  if(t.length > 1 && t.charAt(t.length-1) === '/') t = t.slice(0,-1);\n  /* inside a market tree, /uk/shop and /shop are the same route */\n  if(NF_BASE && (t === NF_BASE || t.indexOf(NF_BASE + '/') === 0)) t = t.slice(NF_BASE.length) || '/';\n  return t || '/';")

fix("  var m = document.documentElement.getAttribute('data-mkt'); if(m) return m;\n  try{ return /(^|\\.)nofilter\\.ae$/.test((location.hostname || '').toLowerCase()) ? 'AE' : 'SG'; }catch(e){ return 'SG'; }",
    '  var m = document.documentElement.getAttribute(\'data-mkt\'); if(m) return m;\n  /* 7 Sep · a market tree published as a PATH declares its own market, the same\n     tag nfHomeMarket() reads (step 1b). /ae is covered by the hostname test\n     below; /uk has no host of its own, and without this marketKey() answered\n     \'SG\' there — which had applyRouteMeta() rewriting every UK page\'s title and\n     description with the Singapore ones a moment after it loaded. Additive: a\n     page with no pin behaves exactly as before. */\n  try{\n    var pin = document.querySelector(\'meta[name="nf-market"]\');\n    var p = pin && pin.getAttribute(\'content\');\n    if(p === \'AE\' || p === \'SG\' || p === \'UK\') return p;\n  }catch(e){}\n  try{ return /(^|\\.)nofilter\\.ae$/.test((location.hostname || \'\').toLowerCase()) ? \'AE\' : \'SG\'; }catch(e){ return \'SG\'; }')

fix("  var m = ROUTE_META[r]; if(!m) return;\n  var ae = marketKey() === 'AE';\n  if(ae && ROUTE_META_AE[r]) m = ROUTE_META_AE[r];\n  if(r === 'origins' && openOrigin && ORIGIN_META[openOrigin]) m = (ae && ORIGIN_META_AE[openOrigin]) || ORIGIN_META[openOrigin];\n  if(document.title !== m.title) document.title = m.title;",
    "  var m = ROUTE_META[r]; if(!m) return;\n  var mk = marketKey();\n  var RM = mk === 'AE' ? ROUTE_META_AE  : mk === 'UK' ? ROUTE_META_UK  : null;\n  var OM = mk === 'AE' ? ORIGIN_META_AE : mk === 'UK' ? ORIGIN_META_UK : null;\n  if(RM && RM[r]) m = RM[r];\n  if(r === 'origins' && openOrigin && ORIGIN_META[openOrigin]) m = (OM && OM[openOrigin]) || ORIGIN_META[openOrigin];\n  if(document.title !== m.title) document.title = m.title;")

fix("  ev.preventDefault();\n  if(o !== null && PATHS_ON){ try{ history.replaceState(null, '', ORIGIN_META[o].path); }catch(e){} }\n  if(location.hash === '#' + r) fromHash(); else location.hash = '#' + r;",
    "  ev.preventDefault();\n  if(o !== null && PATHS_ON){ try{ history.replaceState(null, '', (NF_BASE || '') + ORIGIN_META[o].path); }catch(e){} }\n  if(location.hash === '#' + r) fromHash(); else location.hash = '#' + r;")

fix('    }\n  }catch(e){}',
    '    }\n  }catch(e){}\n\n  /* 1b · the page\'s own market. /uk and /ae are market trees served from a\n          domain that does not name them, so the page says which market it is.\n          Same reasoning as the domain below — the URL a reader opened IS the\n          choice — and it is the only signal a /uk page has, there being no\n          .uk host. Pages without the tag behave exactly as before. */\n  try{\n    var pin = document.querySelector(\'meta[name="nf-market"]\');\n    var pinned = pin && (pin.getAttribute(\'content\') || \'\').toUpperCase();\n    if(pinned === \'AE\' || pinned === \'SG\' || pinned === \'UK\') return pinned;\n  }catch(e){}')

io.open(F, "w", encoding="utf-8").write(src)
print("patch_ukmarket OK, 9 hunks")
