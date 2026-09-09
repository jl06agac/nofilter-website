#!/usr/bin/env python3
"""Generate the /uk market tree inside the ship TEMPLATE bundle, and add en-gb
hreflang to every page in it.

The UK is a fully priced market in the build (GBP, en-GB, its own wholesale
ladder, contribution bands and the Dr.Coffee range) but until now it had no URL:
it was a state inside the page, reachable only by clicking the flag. A crawler
cannot click a flag, so no page was offered to Britain and none could be linked.

/ae is the precedent, with one difference: /ae is pinned by the .ae hostname and
there is no .uk hostname, so a UK page declares its own market with
<meta name="nf-market" content="UK">, which nfHomeMarket() reads (master, step 1b).

Bodies are identical between market trees — only the head differs — so each UK
page is its SG counterpart with eight SEO fields rewritten, the hreflang set
extended and the market pin added. Copy is mirrored mechanically from the UAE
pages (UAE->UK, AED->GBP) so the three trees read the same; it is Alex's to change.

    python3 build_uk.py <template-bundle>          # writes uk/*, patches hreflang
    python3 build_uk.py <template-bundle> --check  # report only, write nothing
"""
import os, re, sys, json

SG, AE, UK = 'https://nofilter.sg', 'https://nofilter.ae', 'https://nofilter.sg/uk'
PAGES = ['index.html', 'origins/index.html', 'origins/arakan-mountains/index.html',
         'origins/batang-gadis/index.html', 'origins/batang-toru/index.html',
         'origins/gayo-lues/index.html', 'shop/index.html', 'trade-pricing/index.html',
         'wholesale-coffee/index.html']

def uae_to_uk(s):
    """The UAE string, said about Britain. Order matters: longest first."""
    for a, b in (('the UAE', 'the UK'), ('UAE offices', 'UK offices'), ('UAE', 'UK'),
                 ('AED', 'GBP'), ('en_AE', 'en_GB')):
        s = s.replace(a, b)
    return s

def head_of(s):
    return s[:s.index('<style')]

def field(h, pat):
    m = re.search(pat, h)
    return m.group(1) if m else None

def route_path(rel):
    """The site path for a template page, without the market prefix."""
    p = '/' + rel[:-len('index.html')].rstrip('/')
    return '' if p == '/' else p

def build(tpl, write=True):
    made, patched, problems = [], [], []

    # ── 1 · the UK pages ────────────────────────────────────────────────────
    for rel in PAGES:
        sg_p, ae_p = os.path.join(tpl, rel), os.path.join(tpl, 'ae', rel)
        if not (os.path.exists(sg_p) and os.path.exists(ae_p)):
            problems.append(f'missing source for {rel}'); continue
        sg, ae = open(sg_p, encoding='utf-8').read(), open(ae_p, encoding='utf-8').read()
        hsg, hae = head_of(sg), head_of(ae)
        path = route_path(rel)

        ae_title = field(hae, r'<title>(.*?)</title>')
        ae_desc  = field(hae, r'<meta name="description" content="([^"]*)"')
        title, desc = uae_to_uk(ae_title), uae_to_uk(ae_desc)
        sg_title = field(hsg, r'<title>(.*?)</title>')
        sg_desc  = field(hsg, r'<meta name="description" content="([^"]*)"')

        out = sg
        subs = [
            (f'<title>{sg_title}</title>', f'<title>{title}</title>'),
            # the pin rides on the description tag: build-ship diffs the template
            # page against the template index token by token and cannot place a
            # PURE insertion, so a new tag has to arrive fused to one that is
            # already changing. The description differs on both sides, so it is
            # the anchor. (A standalone tag before <title> fails: the differ
            # resyncs on the identical <title> token and the edit comes out empty.)
            (f'<meta name="description" content="{sg_desc}">',
             f'<meta name="nf-market" content="UK"> <meta name="description" content="{desc}">'),
            (f'<link rel="canonical" href="{SG}{path or "/"}">',
             f'<link rel="canonical" href="{UK}{path}">'),
            (f'<meta property="og:url" content="{SG}{path or "/"}">',
             f'<meta property="og:url" content="{UK}{path}">'),
            ('<meta property="og:locale" content="en_SG">',
             '<meta property="og:locale" content="en_GB">'),
            ('<meta property="og:locale:alternate" content="en_AE">',
             '<meta property="og:locale:alternate" content="en_SG">'),
            (f'<meta property="og:title" content="{sg_title}">',
             f'<meta property="og:title" content="{title}">'),
            (f'<meta property="og:description" content="{sg_desc}">',
             f'<meta property="og:description" content="{desc}">'),
            (f'<meta name="twitter:title" content="{sg_title}">',
             f'<meta name="twitter:title" content="{title}">'),
            (f'<meta name="twitter:description" content="{sg_desc}">',
             f'<meta name="twitter:description" content="{desc}">'),
        ]
        for a, b in subs:
            n = out.count(a)
            if n != 1:
                problems.append(f'{rel}: anchor x{n}: {a[:90]}'); break
            out = out.replace(a, b, 1)
        else:
            # JSON-LD: the page-specific nodes (origin pages carry WebPage + crumb)
            def fix_ld(m):
                ld = m.group(1)
                ld = ld.replace(f'"{SG}{path}#', f'"{UK}{path}#')
                ld = ld.replace(f'"url":"{SG}{path}"', f'"url":"{UK}{path}"')
                ld = ld.replace(f'"item":"{SG}{path}"', f'"item":"{UK}{path}"')
                ld = ld.replace('"item":"https://nofilter.sg/"', f'"item":"{UK}"')
                ld = ld.replace('"item":"https://nofilter.sg/origins"', f'"item":"{UK}/origins"')
                if sg_title: ld = ld.replace(json.dumps(sg_title)[1:-1], json.dumps(title)[1:-1])
                if sg_desc:  ld = ld.replace(json.dumps(sg_desc)[1:-1],  json.dumps(desc)[1:-1])
                return '<script type="application/ld+json">' + ld + '</script>'
            out = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, out, flags=re.S)
            dst = os.path.join(tpl, 'uk', rel)
            if write:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'w', encoding='utf-8').write(out)
            made.append(('uk/' + rel, title))

    # ── 2 · en-gb hreflang on every page in the bundle ──────────────────────
    for root, dirs, files in os.walk(tpl):
        dirs[:] = [d for d in dirs if d not in ('netlify', 'assets')]
        for fn in files:
            if not fn.endswith('.html') or fn == '404.html': continue
            p = os.path.join(root, fn)
            s = open(p, encoding='utf-8').read()
            if 'hreflang="en-gb"' in s: continue
            m = re.search(r'<link rel="alternate" hreflang="en-ae" href="([^"]+)">', s)
            if not m:
                problems.append(f'{os.path.relpath(p, tpl)}: no en-ae hreflang to anchor on'); continue
            ae_href = m.group(1)
            path = ae_href[len(AE):].rstrip('/')
            gb = f'<link rel="alternate" hreflang="en-gb" href="{UK}{path}">'
            s2 = s.replace(m.group(0), m.group(0) + ' ' + gb, 1)
            if write: open(p, 'w', encoding='utf-8').write(s2)
            patched.append(os.path.relpath(p, tpl))
    return made, patched, problems

if __name__ == '__main__':
    tpl = sys.argv[1] if len(sys.argv) > 1 else '.'
    write = '--check' not in sys.argv
    made, patched, problems = build(tpl, write)
    print(f'{"wrote" if write else "would write"} {len(made)} UK pages:')
    for rel, t in made: print(f'  {rel:44s} {t}')
    print(f'{"added" if write else "would add"} en-gb hreflang to {len(patched)} pages')
    if problems:
        print('PROBLEMS:'); [print('  ' + p) for p in problems]; sys.exit(1)
    print('ok')
