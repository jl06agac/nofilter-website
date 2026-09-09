#!/usr/bin/env python3
"""nf-split — one page per route, from the website master.

  python3 split.py <master.html> <route> <relative-prefix> <out.html>

WHY THIS EXISTS
  Every URL on nofilter.sg currently ships the same 498,250-byte body: all six
  routes, with JavaScript showing one and hiding five. Every page's <h1> reads
  "Hold the line". To a crawler the pages are indistinguishable, which is the
  duplicate-content problem behind the AI-searchability work.

WHAT IT DOES, AND WHAT EACH STEP COST TO FIND
  1. Keeps one route, removes the other five.
  2. RESCUES the <style> blocks that live INSIDE the removed routes. Six of the
     twelve stylesheets sit inside route sections — one in #why, one in
     #origins, four in #work totalling 36.8 KB — and they style other routes.
     Deleting them flattened the partner marquee to a vertical stack of 48
     logos. This step is not optional.
  3. Rewrites the 15 in-page #route anchors, and the nav's data-r links, to real
     page URLs. Without it "BUILD YOUR QUOTE" scrolls to nothing.
  4. Promotes the page's own first real heading to <h1>, so each page says what
     it is. A hidden h1 was tried and rejected: Google distrusts off-screen
     headings.

  The JavaScript side is NOT here — it is in the master, via
  nf-build-tools/patches/patch_routesafe.py (block 113). Nine guards, each one
  found by splitting the page and reading the console until it was silent.
  Every one is a no-op on the current one-page site: verified before and after
  at 1440x900, same active route, same text, same 5,318px document height.

VERIFIED 4 Sep 2026 — all five split pages: zero JavaScript errors.
"""
import io, os, re, sys, json

ROUTES = ["home","why","origins","shop","work","quote"]
ROUTE_PAGE = {"home":"index.html","why":"index.html","origins":"origins/index.html",
              "shop":"shop/index.html","work":"wholesale-coffee/index.html",
              "quote":"trade-pricing/index.html"}
H1 = {"home":None,  # home keeps Hold the line
      "origins":"Four forests. Four coffees.",
      "shop":"Conservation coffee, by the bag",
      "work":"Wholesale conservation coffee for offices and cafés",
      "quote":"Build your trade quote"}

from html.parser import HTMLParser

class _Spans(HTMLParser):
    """Find each <section class="route" id="..."> and its true end.

    This replaced a regex depth-counter that scanned for '<section' and
    '</section>' as plain text. That counter closed the work route 78 KB early,
    because a '<section' appearing inside an HTML comment or a JavaScript string
    counted as a real tag. The 82,860 bytes it left behind belonged to no route,
    so they survived every split and appeared on EVERY page — the machine
    counter, "your coffee setup tells a story", the on-site proof block.

    HTMLParser treats script and style content as raw text and routes comments
    to handle_comment, so neither can be mistaken for markup. Do not go back to
    a regex here.
    """
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.depth = 0; self.cur = None; self.start = None; self.out = {}
    def handle_starttag(self, tag, attrs):
        if tag != "section": return
        a = dict(attrs)
        if self.cur is None and "route" in (a.get("class") or "") and a.get("id"):
            self.cur = a["id"]; self.depth = 1; self.start = self.getpos()
        elif self.cur is not None:
            self.depth += 1
    def handle_endtag(self, tag):
        if tag != "section" or self.cur is None: return
        self.depth -= 1
        if self.depth == 0:
            self.out[self.cur] = (self.start, self.getpos()); self.cur = None

def route_spans(s):
    p = _Spans(); p.feed(s)
    lines = s.split("\n"); off = [0]
    for l in lines: off.append(off[-1] + len(l) + 1)
    def at(t): return off[t[0]-1] + t[1]
    return {r: (at(a), at(b) + len("</section>")) for r, (a, b) in p.out.items()}

def split(s, keep, pre):
    rescued, dropped = [], []
    for r in ROUTES:
        if r == keep: continue
        sp = route_spans(s).get(r)
        if not sp: continue
        i, j = sp
        seg = s[i:j]
        # rescue the stylesheets that live INSIDE this route: they are not
        # route-scoped and other routes depend on them
        rescued += re.findall(r'<style[^>]*>.*?</style>', seg, re.S)
        dropped.append((r, j - i))
        s = s[:i] + s[j:]
    s = re.sub(r'<section class="route(?: on)?" id="%s"' % keep,
               '<section class="route on" id="%s"' % keep, s, count=1)
    if rescued:
        s = s.replace("</head>", "\n".join(rescued) + "\n</head>", 1)
    # cross-route anchors and nav links become real page links
    n = 0
    for r, t in ROUTE_PAGE.items():
        if r == keep: continue
        for old in ('href="#%s"' % r,):
            c = s.count(old)
            if c: s = s.replace(old, 'href="%s%s"' % (pre, t)); n += c
    for r, t in ROUTE_PAGE.items():
        s = s.replace('data-r="%s"' % r, 'data-r="%s" href="%s%s"' % (r, pre, t))
    # ONE h1 per page, and a real visible one. Every page currently carries the
    # same "Hold the line" h1, which tells a crawler nothing about which page it
    # is on. A hidden h1 would be worse: Google treats off-screen headings as a
    # signal to distrust. So the page's own first real heading is promoted.
    h1txt = None
    if keep != "home":
        sp = route_spans(s).get(keep)
        if not sp: return s, dropped, len(rescued), n, None
        i, j = sp
        seg = s[i:j]
        for h in re.finditer(r'<h2\b([^>]*)>(.*?)</h2>', seg, re.S):
            inner = h.group(2)
            txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', inner)).strip()
            # Skip a heading whose first word is injected by JavaScript. The
            # quote page's heading carries a rotating word slot (mani-slot) that
            # cycles cafe / zoo / office, so promoting it produced an <h1>
            # reading "Z O O RATES. LIVE IMPACT MATH." — an h1 whose text
            # changes is worse than none. The stable h2 below it is the heading.
            if 'mani-slot' in inner or not txt[:1].isupper():
                continue
            if len(txt) > 3:
                promoted = '<h1%s>%s</h1>' % (h.group(1), h.group(2))
                seg = seg[:h.start()] + promoted + seg[h.end():]
                s = s[:i] + seg + s[j:]
                h1txt = txt
                break
    # 5. Assets. The MASTER references media as ../../_CDN-UPLOAD-SAFE/<file>,
    #    which only resolves inside the workspace. build-ship.mjs rewrites all
    #    120 of them to the CDN, and splitting the master without doing the same
    #    leaves every image and video a dead link — the page renders as a
    #    wireframe with a broken wordmark. Same rewrite, same target.
    CDN = 'https://nofilter-shared.netlify.app/'
    s = re.sub(r'(?:\.\./)*_CDN-UPLOAD-SAFE/', CDN, s)
    #    Six media files are referenced by BARE FILENAME rather than through the
    #    _CDN-UPLOAD-SAFE folder — hero-trim-fast.mp4, mono-coffee-poster.jpg and
    #    friends. They resolve next to the master inside the workspace and
    #    nowhere else, so they must be lifted to the CDN too. Missing these left
    #    the home page with no hero video and a "TAP TO PLAY" button over a dead
    #    <video>. build-ship.mjs does the same rewrite.
    for _f in ('hero-trim-fast.mp4', 'keeps-standing-lite.mp4', 'mega-farm-test-lite.mp4',
               'atwork-rain-loop-lite.mp4', 'mono-coffee-poster.jpg', 'atwork-rain-poster.jpg'):
        s = re.sub(r'(?<=["\'(])' + re.escape(_f), CDN + _f, s)
    return s, dropped, len(rescued), n, h1txt

if __name__ == "__main__":
    src, keep, pre, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    s = io.open(src, encoding="utf-8", errors="replace").read()
    s, dropped, ncss, nanch, h1 = split(s, keep, pre)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    io.open(out, "w", encoding="utf-8").write(s)
    print("  %-30s css %d | links %2d | h1: %s" % (out, ncss, nanch, h1 or "(hero)"))
