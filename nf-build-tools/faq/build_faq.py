#!/usr/bin/env python3
"""Build /faqs as a real page inside a built SHIP bundle.

  python3 build_faq.py <bundle>/index.html <bundle>/faqs/index.html [sg|ae|uk]

Rather than styling a page from scratch and hoping it matches, this takes a
page the site already builds, keeps its shell — head, fonts, nav, footer, the
whole stylesheet — and swaps the route section for the FAQ one. Same approach
as split.py, and it means the FAQ cannot drift from the site's own type,
colour and chrome, because it is literally the same document.

The visible HTML and the FAQPage JSON-LD are generated from one object in
faq_content.py, so they cannot disagree. The brief is explicit that schema must
mirror the page; generating both from the same source is the only way to keep
that true after the next copy edit.

Every answer is in the initial HTML. <details> hides it visually and nothing
else. No fetch, no injection, no hydration.
"""
import io, json, os, re, sys, html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from faq_content import (CATEGORIES, ORIGINS_ROW, STRIP_DATE, INTRO,
                         TECHLINE, H1, H1_A, H1_B, KICKER, HERO_IMG, HERO_ALT,
                         HERO_CAP_1, HERO_CAP_2, TITLE, DESC, TITLE_AE, DESC_AE,
                         TITLE_UK, DESC_UK)


# the stylesheet is swappable so two row treatments can be built from the same
# markup and looked at side by side: NF_FAQ_CSS=faq-capsule.css python3 build_faq.py ...
_HERE = os.path.dirname(os.path.abspath(__file__))
CSS = ('<style id="nf-faq-css">\n'
       + "\n".join(io.open(os.path.join(_HERE, f), encoding="utf-8").read()
                   for f in os.environ.get("NF_FAQ_CSS", "faq.css").split(","))
       + "\n</style>")

JS = """
<script id="nf-faq-js">
/* The accordion is visual only. Every answer is already in the DOM above;
   this script never fetches or writes copy. It does three things: keeps the
   six category panels mutually exclusive, opens the right panel and question
   when the page is loaded with a hash, and gives each question a copyable
   link. Nothing here is required to read the page — with JS off, every
   <details> still opens on click. */
(function () {
  var groups = Array.prototype.slice.call(document.querySelectorAll('.nf-faq-group'));

  groups.forEach(function (g) {
    g.addEventListener('toggle', function () {
      if (!g.open) return;
      groups.forEach(function (o) { if (o !== g) o.open = false; });
    });
  });

  function reveal(id, scroll) {
    var item = document.getElementById(id);
    if (!item) return false;
    var grp = item.closest('.nf-faq-group');
    if (grp) {
      groups.forEach(function (o) { o.open = (o === grp); });
    }
    item.open = true;
    if (scroll) {
      try { item.scrollIntoView({ block: 'start', behavior: 'smooth' }); }
      catch (e) { item.scrollIntoView(); }
    }
    return true;
  }

  function fromHash() {
    var h = (location.hash || '').replace(/^#/, '');
    if (h) reveal(h, true);
  }
  window.addEventListener('hashchange', fromHash);
  if (location.hash) {
    /* the route has to be on screen before scrollIntoView means anything */
    setTimeout(fromHash, 60);
  }

  /* the trail is walked rather than printed: --walk runs 0 to 1 as the file
     passes the middle of the viewport, and the CSS clips the prints to it.
     rAF-throttled, passive, and skipped entirely when the browser says the
     reader does not want motion. */
  var zone = document.querySelector('.faq-zone');
  if (zone && !(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) {
    var pending = false;
    function walk() {
      pending = false;
      var r = zone.getBoundingClientRect(), vh = window.innerHeight || 800;
      var p = (vh * 0.72 - r.top) / Math.max(1, r.height * 0.72);
      zone.style.setProperty('--walk', Math.max(0, Math.min(1, p)).toFixed(3));
    }
    function onScroll() {
      if (pending) return;
      pending = true;
      (window.requestAnimationFrame || setTimeout)(walk);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    walk();
  }

  /* clicking a question writes its anchor to the address bar, so a colleague
     can be sent straight to the answer rather than to the top of the page */
  document.querySelectorAll('.nf-faq-item').forEach(function (item) {
    var s = item.querySelector('summary');
    if (!s) return;
    s.addEventListener('click', function () {
      if (item.open || !item.id) return;
      try { history.replaceState(null, '', '#' + item.id); } catch (e) {}
    });
  });
})();
</script>
"""


def strip_html(frag):
    """Answer text for the JSON-LD. Schema.org wants text, and the brief wants
    it to match what a reader sees, so this flattens the same fragment rather
    than keeping a second hand-written copy that can drift."""
    t = re.sub(r'<br\s*/?>', ' ', frag)
    t = re.sub(r'</p>|</li>', ' ', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()


def section_html():
    """The markup, composed as a section record rather than a list.

    Each category is a [data-beat] element carrying a .beat-hd .sn folio. That
    is the site's own index contract: stampFolios renumbers the folios 01..06
    on load, and the left rail's marker tracks the same elements on scroll. So
    the rail follows the category you are reading without a second scroll
    system being written for this page.
    """
    out = []
    a = out.append
    a('<section class="route on" id="faq" data-title="FAQs">')
    # hero, on paper: copy left, one real landscape right
    a('<div class="faq-hero"><div class="faq-wrap faq-hero-grid">')
    a('<div class="faq-hero-copy">')
    a('<p class="faq-kicker">%s</p>' % html.escape(KICKER))
    a('<h1 class="faq-h1"><span>%s</span><span class="hl-o">%s</span></h1>'
      % (html.escape(H1_A), html.escape(H1_B)))
    a('<p class="faq-intro">%s</p>' % html.escape(INTRO))
    a('<p class="faq-techline">%s</p>' % TECHLINE)
    a('</div>')
    # width and height are declared so the image reserves its box before it
    # loads; the site's own CLS problem came from images that did not
    a('<figure class="faq-hero-fig">'
      '<img src="%s" alt="%s" width="1200" height="1500" decoding="async">'
      '<figcaption><b>%s</b><br>%s</figcaption></figure>'
      % (HERO_IMG, html.escape(HERO_ALT, quote=True),
         html.escape(HERO_CAP_1), html.escape(HERO_CAP_2)))
    a('</div>')
    a('</div>')
    # the index: one sheet of paper carrying the file line and the four
    # categories, separated by rules. The file line is stated once, here, and
    # the categories carry their own number and class instead of repeating it.
    nq = sum(len(c["items"]) for c in CATEGORIES)
    a('<div class="faq-zone">')
    # the trail: decorative, aria-hidden, and outside the reading order
    a('<div class="faq-trail" aria-hidden="true"><i></i></div>')
    a('<div class="faq-body"><div class="faq-wrap">')
    a('<div class="faq-panel">')
    a('<div class="faq-strip">'
      '<span class="st-lead">FAQ file</span><span><b>%d</b> questions</span>'
      '<span><b>%02d</b> sections</span><span>Updated <b>%s</b></span></div>'
      % (nq, len(CATEGORIES), STRIP_DATE))

    for ci, c in enumerate(CATEGORIES, 1):
        n = len(c["items"])
        a('<details class="nf-faq-group" id="grp-%s" data-beat%s>'
          % (c["id"], " open" if c.get("open") else ""))
        # one component, used four times: number and class on one mono line,
        # count and mark closing it, title and strap beneath. No photograph —
        # a picture on a closed row is decoration, and the ones that prove
        # something now sit inside the answers that need them.
        a('<summary><span class="grp-head">')
        a('<span class="grp-top">'
          '<span class="beat-hd"><span class="sn">%s</span> · %s</span>'
          '<span class="grp-right">'
          '<span class="grp-count">%d question%s</span>'
          '<span class="grp-mark" aria-hidden="true"></span>'
          '</span></span>' % (c["n"], html.escape(c["cls"]), n,
                              "" if n == 1 else "s"))
        a('<span class="grp-copy">')
        a('<h2 class="grp-t">%s</h2>' % c["title"])
        a('<span class="grp-s">%s</span>' % c["strap"])
        a('</span>')
        a('</span></summary>')
        a('<div class="grp-body">')
        for qi, q in enumerate(c["items"], 1):
            a('<details class="nf-faq-item" id="%s">' % q["id"])
            a('<summary><span class="q-n">%02d</span><h3 class="q-t">%s</h3>'
              '<span class="q-mark" aria-hidden="true"></span></summary>'
              % (qi, html.escape(q["q"])))
            a('<div class="faq-a"><span class="a-lab">Answer · %s.%02d</span>%s'
              % (c["n"], qi, q["a"].strip()))
            # photography sits inside the answer, where it is evidence, rather
            # than on the closed row, where it was decoration
            if q.get("img"):
                a('<figure class="faq-ev">'
                  '<img src="%s" alt="%s" width="1200" height="675" loading="lazy" decoding="async">'
                  '<figcaption>%s</figcaption></figure>'
                  % (q["img"], html.escape(q["alt"], quote=True), html.escape(q["cap"])))
            a('</div>')
            a('</details>')
        if c.get("origins_row"):
            a('<nav class="org-row" aria-label="The four origins">')
            for name, region, href in ORIGINS_ROW:
                a('<a href="%s"><span class="org-k">Origin</span>'
                  '<span class="org-n">%s</span><span class="org-r">%s</span></a>'
                  % (href, html.escape(name), html.escape(region)))
            a('</nav>')
        a('</div></details>')

    a('</div>')
    a('</div></div></div></section>')
    return "\n".join(out)


def jsonld(base="https://nofilter.sg/faqs"):
    # 7 Sep · base is the market's own /faqs URL; every question anchors under it
    qs = []
    for c in CATEGORIES:
        for q in c["items"]:
            qs.append({
                "@type": "Question",
                "name": q["q"],
                "url": base + "#" + q["id"],
                "acceptedAnswer": {"@type": "Answer", "text": strip_html(q["a"])},
            })
    doc = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qs}
    return ('<script type="application/ld+json" id="nf-faq-schema">%s</script>'
            % json.dumps(doc, ensure_ascii=False, separators=(",", ":")))


def build(src, out, market="sg"):
    s = io.open(src, encoding="utf-8", errors="replace").read()

    # 1 · the shell keeps everything; only the route section is replaced
    m = re.search(r'<section class="route on" id="[a-z]+"', s)
    if not m:
        raise SystemExit("no active route section in %s: is this a split page?" % src)
    start = m.start()
    depth, i = 0, start
    # a real scan, not a regex: '<section' appears inside scripts and comments
    from html.parser import HTMLParser

    class Span(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.d = 0; self.end = None; self.started = False
        def handle_starttag(self, tag, attrs):
            if tag == "section":
                self.d += 1; self.started = True
        def handle_endtag(self, tag):
            if tag == "section" and self.started:
                self.d -= 1
                if self.d == 0 and self.end is None:
                    self.end = self.getpos()

    p = Span(); p.feed(s[start:])
    if p.end is None:
        raise SystemExit("route section never closes")
    lines = s[start:].split("\n"); off = [0]
    for l in lines:
        off.append(off[-1] + len(l) + 1)
    end = start + off[p.end[0] - 1] + p.end[1] + len("</section>")

    s = s[:start] + section_html() + s[end:]

    # 2 · head: title, description, canonical, og, and the schema
    # 6 Sep · three markets. The UK is a path tree on the Singapore domain
    # (there is no .uk host), so its canonical is /uk/faqs on nofilter.sg while
    # the UAE's is /faqs on its own domain — hence base, not just host.
    host = "nofilter.ae" if market == "ae" else "nofilter.sg"   # kept: used by the JSON-LD below
    base = {"ae": "https://nofilter.ae/faqs",
            "uk": "https://nofilter.sg/uk/faqs"}.get(market, "https://nofilter.sg/faqs")
    title = {"ae": TITLE_AE, "uk": TITLE_UK}.get(market, TITLE)
    desc  = {"ae": DESC_AE,  "uk": DESC_UK}.get(market, DESC)
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % html.escape(title), s, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda mm: mm.group(1) + html.escape(desc, quote=True) + mm.group(2), s, count=1)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
               lambda mm: mm.group(1) + base + mm.group(2), s, count=1)
    for prop, val in (("og:title", title), ("og:description", desc),
                      ("og:url", base),
                      ("twitter:title", title), ("twitter:description", desc)):
        s = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % re.escape(prop),
                   lambda mm, v=val: mm.group(1) + html.escape(v, quote=True) + mm.group(2), s, count=1)
    s = re.sub(r'<link rel="alternate" hreflang="en-sg" href="[^"]*"',
               '<link rel="alternate" hreflang="en-sg" href="https://nofilter.sg/faqs"', s, count=1)
    s = re.sub(r'<link rel="alternate" hreflang="en-ae" href="[^"]*"',
               '<link rel="alternate" hreflang="en-ae" href="https://nofilter.ae/faqs"', s, count=1)
    s = re.sub(r'<link rel="alternate" hreflang="en-gb" href="[^"]*"',
               '<link rel="alternate" hreflang="en-gb" href="https://nofilter.sg/uk/faqs"', s, count=1)
    s = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*"',
               '<link rel="alternate" hreflang="x-default" href="https://nofilter.sg/faqs"', s, count=1)

    s = s.replace("</head>", CSS + jsonld(base) + "\n</head>", 1)
    s = s.replace("</body>", JS + "\n</body>", 1)

    # 3 · the router: register the route so the page knows what it is
    s = s.replace('ROUTES=["home","why","origins","shop","work","quote"]',
                  'ROUTES=["home","why","origins","shop","work","quote","faq"]', 1)
    s = s.replace('ROUTE_META={home:{path:"/"',
                  'ROUTE_META={faq:{path:"/faqs",title:%s,desc:%s},home:{path:"/"'
                  % (json.dumps(title), json.dumps(desc)), 1)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    io.open(out, "w", encoding="utf-8").write(s)

    nq = sum(len(c["items"]) for c in CATEGORIES)
    print("  %-46s %8d b | %d categories | %d questions" % (out, len(s), len(CATEGORIES), nq))


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "sg")
