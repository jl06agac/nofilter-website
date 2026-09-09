#!/usr/bin/env python3
"""SEO · give the pages that don't describe themselves a WebPage and a crumb.

Run against the TEMPLATE bundle (SHIP-2026-08-30f). build-ship.mjs grafts the
head from there verbatim into every built page, so this is where per-page
structured data lives — the master carries none of it.

3 Sep audit finding 04: every page ships the same global graph (Organization,
LocalBusiness, WebSite, Service, four Products), and on top of that the four
ORIGIN pages add a WebPage and a BreadcrumbList naming themselves. Shop,
trade-pricing, wholesale-coffee and the origins index add nothing, so in
structured-data terms they are anonymous — identical markup, and (finding 01)
identical body text, distinguishable only by their title tag.

Cheap to fix, and it compounds the day the router stops shipping every route's
content on every URL.
"""
import io, json, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "SHIP-2026-08-30f"

# path → (crumb label, breadcrumb trail above it)
PAGES = {
    "shop":             ("Shop",             []),
    "trade-pricing":    ("Trade pricing",    []),
    "wholesale-coffee": ("Wholesale coffee", []),
    "origins":          ("Origins",          []),
}

def head_of(d):
    return d[:d.index("</head>")]

def graph_block(d):
    """The one ld+json script in the head, and its span."""
    h = head_of(d)
    m = re.search(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)', h, re.S)
    assert m, "no ld+json in head"
    return m

def meta(d, name):
    m = re.search(r'<meta name="%s" content="([^"]*)"' % name, head_of(d))
    return m.group(1) if m else ""

def title_of(d):
    m = re.search(r"<title[^>]*>(.*?)</title>", head_of(d), re.S)
    return m.group(1).strip() if m else ""

def canonical(d):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', head_of(d))
    return m.group(1) if m else ""

def unescape(s):
    return (s.replace("&amp;", "&").replace("&quot;", '"')
             .replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">"))

changed = []
for market in ("", "ae/"):
    for path, (label, trail) in PAGES.items():
        f = os.path.join(ROOT, market + path, "index.html")
        if not os.path.exists(f):
            print("  skip (absent): %s" % f); continue
        d = io.open(f, encoding="utf-8").read()

        m = graph_block(d)
        try:
            obj = json.loads(m.group(2))
        except Exception as e:
            print("  skip (unparseable JSON-LD): %s — %s" % (f, e)); continue
        g = obj.get("@graph")
        if g is None:
            print("  skip (no @graph): %s" % f); continue
        if any(str(x.get("@type")) == "WebPage" for x in g):
            print("  already has WebPage: %s" % f); continue

        url = canonical(d)
        assert url, "no canonical in %s" % f
        site = url.split("/" + path)[0] or url.rstrip("/")
        home = site + "/"

        webpage = {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": unescape(title_of(d)),
            "description": unescape(meta(d, "description")),
            "inLanguage": "en",
            "isPartOf": {"@id": home + "#website"},
            "breadcrumb": {"@id": url + "#crumb"},
        }
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": home}]
        for i, (nm, href) in enumerate(trail, start=2):
            items.append({"@type": "ListItem", "position": i, "name": nm, "item": href})
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": label})
        crumb = {"@type": "BreadcrumbList", "@id": url + "#crumb",
                 "itemListElement": items}

        g.extend([webpage, crumb])
        new = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        d = d[:m.start(2)] + new + d[m.end(2):]
        io.open(f, "w", encoding="utf-8").write(d)
        changed.append(market + path)

print("WebPage + BreadcrumbList added to %d pages:" % len(changed))
for c in changed:
    print("   " + c)
