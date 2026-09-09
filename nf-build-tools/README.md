# NoFilter website — build tools (snapshot 3 Sep 2026)

The master, `Marketing/NoFilter-Website/NoFilter-Website-Master.html`, is the
single source of truth and is fully built (blocks through 98). These tools are
how it was made and how a SHIP bundle is cut from it. They lived in Claude's
session workspace, which is discarded between sessions — this folder is the copy
that survives.

## What is here

- `base/NoFilter-Website-Master-2026-08-31.html` — the master as it stood on 31 Aug, before the patch
  chain. `build.sh` rebuilds the current master from it: copy, then run every
  `patches/patch_*.py` in the order listed in the script (each asserts its
  anchors and stops the build if the master has drifted).
- `patches/` — 89 numbered edits, one file each, with the reasoning for each
  block in the comments at the top. The master already contains all of them;
  they are history and a place to read *why*.
- `ship/build-ship.mjs` — master → SHIP bundle:
  `node build-ship.mjs <master.html> SHIP-2026-08-30f <out folder>`
  (CDN rewrite, minify, fonts to /assets/fonts, font-display, SEO head graft
  from the template, CSS purge, per-page transplant, page preloads, the
  PRCF Indonesia rename, llms.txt, sitemap lastmod).
- `ship/SHIP-2026-08-30f/` — the template bundle the builder grafts heads and
  per-page edits from. Keep it; every build reads it.
- `ship/purge-css.mjs` — the dead-CSS pass the builder calls.
- `ship/verify-ship.mjs`, `access.mjs`, `qmail.mjs`, `nav.mjs`, `route.mjs`,
  `netload.mjs`, `board.mjs`, `sound.mjs`, `gis.mjs`, `warm.mjs`, `hd.mjs`,
  `lhserve.mjs` … — the checks run on each bundle (Playwright + local
  Chromium; `npm install` in `ship/` for the node deps).
- `_nf-ship-stamp.mjs` (beside the master on the Desktop) — stamps the bundle
  name into each page after a build.

## The iteration loop (set 9 Sep 2026, when this folder went into git)

Before git, every iteration was a dated SHIP folder: 13 of them plus 23 tarballs,
361 MB, `07a` through `07h` in one evening, because there was nowhere else to put
"the state of things at 2:17am". Iterations now live in the commit history.

    1. write a patch      patches/patch_<name>.py, add its name to build.sh
    2. bash build.sh      master rebuilt IN PLACE. One file, one name, no date
    3. git commit         <- THIS is the iteration. Permanent, with the reasoning
    4. cut the bundle     see below
    5. drag to nofilter-site
    6. forget the bundle  .gitignore drops it; step 2 regenerates it any time

**Step 3 comes before step 4, always.** Commit the master, then build from it.
Deploying a bundle whose source was never committed is how the master, the newest
build and the live site ended up three different states on 7-9 Sep.

To go back to an earlier state: `git log` to find it, `git checkout <commit>` to get
the folder as it was, then cut a bundle from that. Old bundles are never kept --
the master plus the patch chain reproduce them byte for byte, which is verified
before any change by rebuilding the current master and matching its md5 first.

## To cut the next bundle

    cd ship && npm install
    node build-ship.mjs ../../NoFilter-Website-Master.html SHIP-2026-08-30f SHIP-<date>

The template argument is ALWAYS `SHIP-2026-08-30f`. Pointing it at a finished
bundle fails with `head anchors missing … -1`, because only the template keeps
`<style id="nf-fonts">` — the builder strips that id on the way out.

Then the FAQ chain, which is NOT in the master and NOT in build-ship.mjs. Skip it
and the bundle ships with 53 files instead of 56 and no FAQ page in any market:

    cd ../faq
    python3 build_faq.py <bundle>/index.html    <bundle>/faqs/index.html    sg
    python3 build_faq.py <bundle>/ae/index.html <bundle>/ae/faqs/index.html ae
    python3 build_faq.py <bundle>/uk/index.html <bundle>/uk/faqs/index.html uk
    python3 wire_links.py --site <bundle>

Stamp, then check:

    node ../../_nf-ship-stamp.mjs <bundle>
    node ../ship/verify-ship.mjs <bundle>

`verify-ship.mjs` needs playwright and a chromium and hard-codes `/home/claude/ship/`,
so it does not run on the Mac as written. Run it in a cloud session, and read its
output against the CURRENT LIVE bundle as a baseline rather than in isolation: loaded
over `file://` every bundle reports "30 pages with errors" (CORS on the font files)
and `0.00/mo` prices (RATES are lifted into the Netlify function). Both are artefacts
of the harness. What matters is that the new bundle matches the live one.

Then drop the SHIP folder on **nofilter-site**.

Only drop `_CDN-UPLOAD-SAFE` on **nofilter-shared** if an asset is genuinely missing
from the live bucket, and only after proving the folder is a superset of it. A drop
replaces the whole bucket. Check what the build actually needs first:

    while read -r f; do c=$(curl -s -o /dev/null -w '%{http_code}' \
      "https://nofilter-shared.netlify.app/$f"); [ "$c" != 200 ] && echo "$c $f"; \
      done < ../../_cdn-referenced-assets.txt
