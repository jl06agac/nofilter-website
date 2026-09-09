#!/usr/bin/env python3
"""Make /faqs findable. Two treatments, applied to a built page so they can be
looked at rather than described.

  python3 wire_links.py <page.html> <out.html> [nav|foot|both]

NAV   a fifth item after the rotating one. Tried, then withdrawn on 4 Sep:
      THE LINE / ORIGINS / SHOP / IN ZOOS are all steps in the buying journey
      and a reference page does not sit at that level. The default is now
      footer only; "nav" is kept because the argument could go the other way.

FOOT  a mono link in the footer grid, set like the SG / UAE labels already
      there. Present on every page, out of the way, conventional.

The two are independent; "both" applies each.
"""
import io, re, sys

NAV_LINK = '<a href="/faqs" data-r="faq">FAQS</a>'

FOOT_CSS = """<style id="nf-footlinks-css">
.foot-links{display:flex;gap:18px;align-items:center;padding-top:14px}
.foot-links a{font-family:var(--mono);font-size:11px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--dim);text-decoration:none;
  border-bottom:1px solid transparent;padding-bottom:2px}
.foot-links a:hover{color:var(--signal);border-bottom-color:var(--signal)}
@media (prefers-reduced-motion:no-preference){
  .foot-links a{transition:color .14s var(--ease),border-color .14s var(--ease)}}
</style>"""

FOOT_HTML = '<div class="foot-links"><a href="%s/faqs">FAQs</a></div>'   # %s = market base ('' or '/uk')


def add_nav(s):
    m = re.search(r'(<nav class="nav" id="nav"[^>]*>.*?)(</nav>)', s, re.S)
    if not m:
        raise SystemExit("nav not found")
    if 'href="/faqs"' in m.group(1):
        return s, False
    return s[:m.end(1)] + " " + NAV_LINK + " " + s[m.end(1):], True


def add_foot(s, base=""):
    if 'class="foot-links"' in s:
        return s, False
    # sit it under the contact block, inside the footer's own grid
    m = re.search(r'<div class="foot-contact">', s)
    if not m:
        raise SystemExit("foot-contact not found")
    # close of that div: scan forward balancing <div>
    i = m.end()
    depth = 1
    while depth and i < len(s):
        nd = s.find("<div", i)
        ne = s.find("</div>", i)
        if ne < 0:
            raise SystemExit("unbalanced footer")
        if 0 <= nd < ne:
            depth += 1; i = nd + 4
        else:
            depth -= 1; i = ne + 6
    s = s[:i] + (FOOT_HTML % base) + s[i:]
    s = s.replace("</head>", FOOT_CSS + "\n</head>", 1)
    return s, True


def base_for(rel):
    """the market tree a page lives in: '/uk' for uk/**, '' otherwise (the .ae
    host rewrites bare paths, so ae/** links to /faqs like the root does)"""
    rel = rel.replace("\\", "/")
    return "/uk" if rel == "uk" or rel.startswith("uk/") else ""


def wire_site(bundle):
    """7 Sep · every route page gets the footer link (04a had it on 20 of 21
    pages; the 6 Sep rebuild ran this on the FAQ page only, so /faqs was
    orphaned from 06b to 07c). Skips 404.html; idempotent."""
    import os
    n = 0
    for root, _, files in os.walk(bundle):
        for f in files:
            if not f.endswith(".html") or f == "404.html":
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(os.path.dirname(path), bundle)
            rel = "" if rel == "." else rel
            s = io.open(path, encoding="utf-8", errors="replace").read()
            s, ok = add_foot(s, base_for(rel))
            if ok:
                io.open(path, "w", encoding="utf-8").write(s); n += 1
    print("  footer FAQ link added to %d pages in %s" % (n, bundle))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--site":
        wire_site(sys.argv[2]); sys.exit(0)
    src, out = sys.argv[1], sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "foot"
    base = sys.argv[4] if len(sys.argv) > 4 else ""
    s = io.open(src, encoding="utf-8", errors="replace").read()
    did = []
    if mode in ("nav", "both"):
        s, ok = add_nav(s); did.append("nav" if ok else "nav(already)")
    if mode in ("foot", "both"):
        s, ok = add_foot(s, base); did.append("footer" if ok else "footer(already)")
    io.open(out, "w", encoding="utf-8").write(s)
    print("  %-52s %s" % (out, ", ".join(did)))
