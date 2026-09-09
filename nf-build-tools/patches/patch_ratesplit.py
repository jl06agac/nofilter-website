import io, re, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 114 · THE RATE CARD LEAVES THE DOCUMENT ════════════════════════════════
# Found 5 Sep by reading the shipped HTML rather than the rendered page. The
# MARKETS object is 4.6KB of JavaScript in 18 of the 19 published files, and it
# carries the COMPLETE commercial position for all three markets: every band
# threshold and contribution rate, every machine at 24-month rental, 36-month
# rental and purchase, the service cover figures and eleven extras each —
# cooler, install, first-year service, annual service, wrap, callout base,
# callout hourly, counter. View Source and it is all there, in three currencies.
#
# The access code was never gating any of this. It gates the INTERFACE: the
# numbers are already in the browser before anyone types a code, so unlocking
# is a client-side reveal of data the visitor already has. Alex's instruction is
# that only a real enquiry through the quote builder should receive pricing.
#
# What this patch does NOT do is serve different content to crawlers than to
# people. That is cloaking, Google treats it as a spam violation, and it does
# not work anyway: anything GPTBot can fetch, a competitor can fetch by sending
# the same request. The split is by AUDIENCE-WITH-A-CODE, not by user agent, so
# it holds for everyone equally.
#
# The split:
#   MARKETS  stays in the page. Identity and formatting only — currency code,
#            locale, tax label, cup wording, the retail bag prices (which are
#            public by design on the shop page), the legal entity, and machMeta
#            (model names and specs, which are marketing copy worth indexing).
#            Plus ref{}, ONE indicative per-kilo price and rate per market, so
#            the public estimator on the home and wholesale pages still works.
#            These are the numbers already rendered publicly today, so this
#            publishes nothing that is not on the page already.
#   RATES    the ladder. kg, bands, mach, cover, buyx, per market. Declared here
#            so the master remains one readable source of truth, and lifted out
#            of the published HTML by build-ship.mjs, which writes it into
#            netlify/functions/access-verify.js instead. A function's source runs
#            on Netlify and is never sent to a browser.
#
# In the master, RATES is merged straight back in at load, so opening the master
# locally behaves exactly as it does today. Only the SHIPPED build is split.

GATED = ("kg", "bands", "mach", "cover", "buyx")


def span(s, i):
    """the balanced {...} or [...] run starting at i"""
    open_c = s[i]
    close_c = {"{": "}", "[": "]"}[open_c]
    d = 0
    j = i
    while True:
        if s[j] == open_c:
            d += 1
        elif s[j] == close_c:
            d -= 1
            if d == 0:
                return j + 1
        j += 1


# ── 1 · find the MARKETS literal ──────────────────────────────────────────
m = re.search(r"var MARKETS\s*=\s*\{", src)
assert m, "MARKETS literal not found"
obj_start = src.index("{", m.start())
obj_end = span(src, obj_start)
markets = src[obj_start:obj_end]

# ── 2 · lift the gated keys out of each market record ─────────────────────
rates = {}
cut = []          # (start, end) slices to remove from the MARKETS text
for mk in re.finditer(r"\n\s{2}(SG|AE|UK)\s*:\s*\{", markets):
    key = mk.group(1)
    rec_start = markets.index("{", mk.start())
    rec_end = span(markets, rec_start)
    rec = markets[rec_start:rec_end]
    taken = []
    for g in GATED:
        km = re.search(r"(^|[\s,{])" + g + r"\s*:\s*[\{\[]", rec)
        if not km:
            continue
        vs = rec.index(km.group(0)[-1], km.start())
        ve = span(rec, vs)
        # take the whole "key: value," run, and the comment that precedes it
        ks = rec.index(g, km.start())
        te = ve
        if rec[te:te + 1] == ",":
            te += 1
        taken.append((g, rec[ks:ve]))
        cut.append((rec_start + ks, rec_start + te))
    assert len(taken) >= 4, "%s: only lifted %s" % (key, [t[0] for t in taken])
    rates[key] = taken

for a, b in sorted(cut, reverse=True):
    markets = markets[:a] + markets[b:]
# tidy the holes the removals leave
markets = re.sub(r"\n\s*\n(\s*\n)+", "\n\n", markets)
markets = re.sub(r",(\s*),", r",\1", markets)

# ── 3 · the public reference figures, taken from the values just lifted ────
#        def price, floor and the middle band's rate: the numbers already
#        rendered on the public wholesale page and the access gate today.
for key, taken in rates.items():
    d = dict(taken)
    defp = re.search(r"def\s*:\s*([\d.]+)", d.get("kg", ""))
    flr = re.search(r"floor\s*:\s*([\d.]+)", d.get("kg", ""))
    mid = re.findall(r"rate\s*:\s*([\d.]+)", d.get("bands", ""))
    assert defp and flr and len(mid) >= 2, "%s: cannot read ref figures" % key
    # 7 Sep: floor added. The access gate's readout ("Band from SGD 45.00 / kg")
    # is public copy by Alex's decision (24 Aug pass), so the floor is already
    # on every trade-pricing page before a code is typed; withholding it here
    # would silently change that line to the list price.
    ref = "ref:{ kg:%s, floor:%s, rate:%s }," % (defp.group(1), flr.group(1), mid[1])
    anchor = re.search(r"\n(\s*)" + key + r"\s*:\s*\{", markets)
    ins = markets.index("{", anchor.start()) + 1
    markets = (markets[:ins] + "\n" + anchor.group(1) + "      "
               + "/* 114: the one public price and rate, for the estimator */\n"
               + anchor.group(1) + "      " + ref + markets[ins:])

# ── 4 · write RATES beside MARKETS ────────────────────────────────────────
blocks = []
for key in ("SG", "AE", "UK"):
    body = ",\n        ".join(v for _, v in rates[key])
    blocks.append("  %s: { %s }" % (key, body))
seed_js = (
    "\n/* 114 · with the ladder withheld — which is every published page until\n"
    "   someone unlocks the console — the rate keys are seeded from ref{} so no\n"
    "   downstream code has to learn about a second shape. Without this, the\n"
    "   first read of MKT.kg.def throws and takes the rest of its script block\n"
    "   with it: measured, the page drops from 673 rendered words to 228. */\n"
    "function nfSeedPublicRates(){\n"
    "  for(var k in MARKETS){ var m=MARKETS[k], r=m&&m.ref; if(!r) continue;\n"
    "    if(!m.kg)    m.kg={floor:(r.floor!=null?r.floor:r.kg),def:r.kg,ceil:r.kg,step:0.25,full:r.kg};\n"
    "    /* three entries because applyMarket reads bands[0..2].from for the\n"
    "       dial marks; all three carry the same public figure, so the shape is\n"
    "       satisfied without the thresholds being published */\n"
    "    if(!m.bands) m.bands=[{id:1,from:r.kg,to:r.kg,rate:r.rate,label:'',range:''},\n"
    "                          {id:2,from:r.kg,to:r.kg,rate:r.rate,label:'',range:''},\n"
    "                          {id:3,from:r.kg,to:r.kg,rate:r.rate,label:'',range:''}];\n"
    "    if(!m.mach)  m.mach={};\n"
    "    if(!m.cover) m.cover={};\n"
    "    if(!m.buyx)  m.buyx={}; }\n"
    "}\n"
    "nfSeedPublicRates();\n")

rates_js = ("\n\n/* 114 · THE LADDER. Lifted out of the published HTML by\n"
            "   build-ship.mjs and served by netlify/functions/access-verify.js\n"
            "   on a valid access code. Present here so the master stays one\n"
            "   readable source of truth. Do not render from this directly —\n"
            "   read MARKETS, which nfMergeRates() fills in once rates arrive. */\n"
            "var RATES = {\n" + ",\n".join(blocks) + "\n};\n"
            "function nfMergeRates(r){\n"
            "  if(!r) return false;\n"
            "  for(var k in r){ if(!MARKETS[k]) continue;\n"
            "    for(var q in r[k]) MARKETS[k][q]=r[k][q]; }\n"
            "  try{ if(typeof applyMarket==='function' && typeof MKTK!=='undefined') applyMarket(MKTK); }catch(e){}\n"
            "  return true;\n"
            "}\n"
            "/* 115: MARKETS lives inside this IIFE; the CRT device that receives the\n"
            "   access answer is another script block, so the merge is published. */\n"
            "window.__nfMergeRates = nfMergeRates;\n"
            "/* the master runs unsplit; build-ship removes the next line */\n"
            "if (typeof RATES !== 'undefined') nfMergeRates(RATES);  /* NF_MERGE_INLINE */\n")

src = src[:obj_start] + markets + src[obj_end:] 
tail = src.index(";", src.index(markets) + len(markets))
src = src[:tail + 1] + rates_js + seed_js + src[tail + 1:]

io.open(F, "w", encoding="utf-8").write(src)
print("patch_ratesplit: lifted %s per market; MARKETS %d -> %d chars"
      % (", ".join(GATED), len(src[obj_start:obj_end]), len(markets)))
