# /faqs — the toolchain

Run AFTER build-ship.mjs has produced a SHIP bundle. It takes a built page,
keeps the whole shell (head, fonts, nav, footer, stylesheet) and swaps the
route section for the FAQ one, so the page cannot drift from the site's own
type, colour and chrome.

    python3 build_faq.py <bundle>/index.html    <bundle>/faqs/index.html    sg
    python3 build_faq.py <bundle>/ae/index.html <bundle>/ae/faqs/index.html ae
    python3 build_faq.py <bundle>/uk/index.html <bundle>/uk/faqs/index.html uk
    python3 wire_links.py --site <bundle>      # footer FAQ link on EVERY page, per tree

7 Sep: `wire_links.py --site` replaced the per-page invocation. From 06b to 07c
the footer link had been applied to the FAQ page only, so /faqs was reachable
from nowhere on the site (04a had it on every page). --site walks the bundle,
skips 404.html, links /faqs from the root and ae trees and /uk/faqs from uk/,
and is idempotent. build_faq.py's FAQPage JSON-LD now anchors its questions
under the market's own /faqs URL rather than nofilter.sg for all three.

Then check it rather than trusting it:

    node brief.mjs <bundle>      # 36 assertions: palette, type, geometry, a11y
    node shot.mjs  <bundle>      # deep links, mutual exclusion, mobile, JS off

Both need playwright and a chromium; on the cloud side they ran against
/opt/pw-browsers/chromium-1194/chrome-linux/chrome and a small static server
(serve.mjs), so those two paths need repointing to run them locally.

## The files

- faq_content.py  copy and metadata. ONE source for the visible answers and the
                  FAQPage JSON-LD, so the two cannot disagree. Titles and
                  descriptions are per market.
- build_faq.py    the markup, the head rewrite, the route registration, the JS.
- faq.css         the stylesheet, inlined into the page at build time. Carries
                  the wordmark cross as a mask and the Tapanuli trail as a data
                  URI, so neither depends on the CDN.
- wire_links.py   the footer link. "nav" is kept but withdrawn: the FAQ is a
                  reference page, not a step in the buying journey.

## Not yet done

/faqs exists only in the SHIP bundle. It is not a patch in the master, so a
rebuild from NoFilter-Website-Master.html and build.sh produces a site without
it until this chain is run again. That is fine as a routine (it is one command
per market) but it is worth knowing before someone looks for the FAQ in the
master and cannot find it.
