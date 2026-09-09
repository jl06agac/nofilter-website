## 7 Sep 2026 — SHIP-2026-09-07h BUILT and HELD (not deployed; live = 07g). Lossless leftovers from the Lighthouse pass; nothing in it warrants a deploy alone.
- Chain: … patch_scrollroute patch_media3. Master == chain output (md5 707aa7c3de41). Same 56 files as 07g; ladder absent (probe hits are CSS .fld.full and the seed's ceil:r.kg, same as 07g); FAQ footer link on 30 pages; 3 UK tests pass.
- patch_media3: (a) signoff <img> srcset batang-gadis-signoff-1000.webp 1000w / master 1600w, sizes (max-width:900px) 100vw, 850px; the duplicate inline background-image on that .vp-media removed (headless check: the background fetched the 1600 master at every width, defeating the srcset). Measured pick: 1x desktop -> 1000 (128 KB, was 287); 2x desktop and 3x phones -> master (unchanged, no pixel loss). (b) tape scrawl -> tape-this-was-forest-w800.webp (already live on CDN). (c) .foot-copy alpha .36 -> .55 (the one contrast fail Alex did not choose to keep). (d) aria-label="Contact" on #nfCtcBtn.
- DEPLOY ORDER when the time comes: (1) drag the WHOLE _CDN-UPLOAD-SAFE folder onto nofilter-shared (adds batang-gadis-signoff-1000.webp; 404 on live until then), (2) drop SHIP-2026-09-07h onto nofilter-site.
- _CDN-UPLOAD-SAFE housekeeping: stray duplicate tape-this-was-forest-800.webp deleted (never on the CDN; -w800 is the live name).
- hero-poster.jpg preload with fetchpriority=high was ALREADY on the three home pages via the template head; mobile LCP 3.4 s is with it in place. Remaining LCP lever is the hero video/poster weight and the inline JS/CSS parse (Option C split), both parked.
- Orange buttons with white text (3.68:1) stay by Alex's decision: no SEO or AI-crawl penalty, Lighthouse a11y score only.

## 7 Sep 2026 — SHIP-2026-09-07g LIVE on nofilter-site (scroll carry-over on route change fixed; live source carries the generation check). Alex to confirm by trackpad.
- Alex: new page opened at the old page's scroll position (Chrome + Safari). Cause: the "treacly scroll" wheel damper's rAF loop keeps easing for ~1 s after the last wheel tick; go() scrolls to 0, the next frame writes the old position back. Only reproducible with REAL wheel input (scripted scrolls never wake the loop), which is why earlier checks passed. Measured before: click 300 ms after scrolling -> lands at 3,013 px. After patch_scrollroute (generation counter + nf:route listener): 0/110 px in all cases; wheel still works on the new route; 0 JS errors.
- Chain: … patch_media2 patch_scrollroute. Master == chain output (md5 f14015e1921d). Same 56 files; ladder absent; FAQ links on 30 pages; UK tests pass.
- Safari: hero autoplay refused + judder reported by Alex while his Mac was under load (this session's VM + another AI). Not diagnosed. Autoplay refusal on macOS Safari = Low Power Mode or the site's Auto-Play setting; the page already falls back to tap-to-play. Judder candidates if it persists unloaded: the clip-path glitch animations on the three video layers (Lighthouse: non-composited).

## 7 Sep 2026 — SHIP-2026-09-07f LIVE (CDN drag done first; all 13 new files 200 on nofilter-shared). Verified live: main hero streams the full file, both glitch layers stream hero-trim-fast-lo.mp4 (610 KB), no old .jpg/.png names referenced.
- 13 NEW files in _CDN-UPLOAD-SAFE (originals untouched): hero-trim-fast-lo.mp4 (360p CRF33, 610 KB; used ONLY by the two duotone glitch layers, which each streamed the full 3.2 MB — saves ~5.1 MB on the home page) and WebP twins at the same pixel size: batang-gadis-signoff, verify-drone-poster, batang-toru/-gadis/-arakan-banner-poster, gayo-lues-banner-poster, orangutan-batang-toru, wp-pour-poster (q80) + ngo-kub/-acca/-prcf/-ff (lossless). ~600 KB saved across origins/wholesale. Tried and dropped: mono-coffee-poster, atwork-rain-poster (WebP no smaller; grainy footage).
- Chain: … patch_machcat patch_media2 (repoints the two <source data-src> and 12 image names). faq_content.py: signoff + drone refs -> .webp. Master == chain output (md5 a6423d8b593d).
- Deploy order: (1) drag the WHOLE _CDN-UPLOAD-SAFE folder onto nofilter-shared (superset; adds the 13 files), (2) drop SHIP-2026-09-07f onto nofilter-site. Reversed order = 404 images until (1) lands.
- Honest note: WebP gains on these grain-heavy stills were 15-25%, not the "quarter of the bytes" I first estimated. The hero overlay is the real win.
- Still parked (creative/quality calls): banner-lite.mp4 trims (3.3-3.9 MB each), harder hero encode, bag stills.

## 7 Sep 2026 — SHIP-2026-09-07e built (perf: blank tiles / blank "Poured at the counter"), to drop
- Alex: "bag tiles blank for a split second on the shop page, same with the Poured at the counter video". Measured live on his Mac: TTFB 0.6 s, HTML (800 KB, 337 KB inline JS + 349 KB inline CSS) done + DCL at 2.2 s; shop tiles are script-built so their images are only discovered at ~2.2 s, then fetched from the CDN host; route videos hold their still as data-poster (pass96, sensible on the one-page master) so the still is attached only when routeVideo() runs.
- build-ship.mjs step 3b2: for the page's OWN route section, data-poster -> poster= at build time + <link rel=preload as=image> for each still; shop pages preload the four bag-*-640.webp. Off-route sections untouched (routeVideo still promotes them on client-side nav; no-op where poster already set). Verified in Chromium: preloaded stills/bags are the first CDN requests on every page; 0 JS errors; on-route videos carry poster at parse time.
- Same 56 files as 07d; ladder absent; FAQ footer link on 30 pages; 3 UK tests pass.
- Structural cause (1.6 s of download+parse per page, nothing cached between pages because all JS/CSS is inline) is NOT addressed; that is the external-shared-script split ("Option C"), a day or two with regression risk. Not this week.
- Pre-existing minor waste left alone: hero-poster.jpg + mono-coffee-poster.jpg (cover videos, outside .route) fetched on every page.

## 7 Sep 2026 — SHIP-2026-09-07d LIVE on nofilter-site (verified: footer FAQ link on every page in all three trees, per-market FAQ schema URLs, /home -> /, /the-misfits -> /shop, nofilter.ae on 07d). Fixes a regression Alex spotted.
- /faqs was ORPHANED from 06b through 07c: no page linked to it. 04a had the footer FAQ link on 20/21 pages; the 6 Sep rebuild ran wire_links.py on the FAQ page only. Now `wire_links.py --site <bundle>` puts the footer link on all 30 pages (/faqs from root+ae, /uk/faqs from uk). Rendered check: link visible, IBM Plex Mono, right href, on /, /uk/, /faqs/.
- FAQPage JSON-LD Question URLs now per market (nofilter.sg/faqs#, nofilter.ae/faqs#, nofilter.sg/uk/faqs#).
- netlify.toml (template + bundle): 301 /home -> /, /the-misfits -> /shop.
- Same 56 files as 07c; ladder still absent; three UK tests pass. Drop 07d on nofilter-site when convenient; nothing in it is urgent except the FAQ link.

## OPEN QUEUE as of 7 Sep 2026 night (live = SHIP-2026-09-07c)
Next drop (batch; none warrants a deploy alone):
- netlify.toml: 301 /home -> /  and /the-misfits -> /shop (old-site URLs still in Google's index, currently 404; the other old URLs already redirect).
- build_faq.py: FAQPage Question URLs hardcoded to https://nofilter.sg/faqs#… on all markets -> per-market base.
- Product JSON-LD `offers` per origin per market: ONLY once retail bag prices are commercial (MARKETS bag250/bag1kg are placeholders except SG 1 kg 80).
Human checks (Alex):
- One real unlock on /trade-pricing with an emailed code: builder must show prices (live function + real secret not exercised by the harness).
- Search Console: Validate fix pressed? Request indexing /wholesale-coffee, /origins (done?). Sitemaps resubmitted for both properties.
- UK copy (titles/descriptions) is mirrored UAE->UK wording, unapproved.
Unchecked code:
- quote-confirm.js / checkout.js may carry their own price copies (server-side only; not a visitor leak).
Note for the record: the "seven pages excluded" reading on 7 Sep was overstated — Google had indexed the no-slash canonicals and filed the slash forms as alternates. The Pretty-URLs fix removed the ambiguity, it did not rescue the pages.

## 7 Sep 2026 (night) — SHIP-2026-09-07c LIVE on nofilter-site (07b was never dropped)
- Verified live: every no-slash address (/wholesale-coffee, /origins, /shop, /trade-pricing, /uk/…) answers 200 directly — the Pretty URLs 301 is gone; /faq and /uk/faq still 301 to /faqs (intended). No ladder figure in any live page source. access-verify answers 401 {ok:false} to a bad code (function deployed). nofilter.ae on 07c, UAE titles. Alex to: Search Console → Page indexing → 'Alternate page with proper canonical tag' → Validate fix; URL-inspect + request indexing /wholesale-coffee and /origins. Still to confirm by a human: one real unlock on /trade-pricing populates the builder (needs a real emailed code).
- What: every published page used to carry MARKETS.{SG,AE,UK}.{kg,bands,mach,cover,buyx} (floors, band thresholds, machine r24/r36/buy, cover, extras) in plain source. Now build-ship lifts RATES out of the master into netlify/functions/access-verify.js, which returns {ok:true, rates} on a valid code; the CRT merges them (window.__nfMergeRates) before the builder is revealed. Pages keep only ref:{kg (list), floor, rate (middle band)} per market — the three figures already public on the wholesale page and the access gate readout — plus bag prices, cup, identity, machNote.
- Chain (build.sh) now ends: … patch_ukmarket patch_ratesplit patch_ratefetch patch_bandmarks patch_machcat. Master == chain output (md5 4535d955f6d0). patch_bandmarks removed a hardcoded {45,48,51} fallback; patch_machcat zeroed the SG r24/r36/buy/price duplicates in MACHINES[] (applyMarket writes them from MKT.mach; guarded for the seeded market).
- Template: ship/SHIP-2026-08-30f/netlify/functions/access-verify.js has `const RATES = /*NF_RATES*/null;` and returns rates; build-ship fails the build if the marker or the literal is missing, or if a ladder figure survives in index.html.
- Proven in Chromium (cloud, ratesplit-test.mjs) 07b vs 07c: public render IDENTICAL on /, /wholesale-coffee, /shop, /trade-pricing, /uk/trade-pricing (same word counts; only the random letter-scramble differs); after a real code via the function: unlocked builder IDENTICAL (SG 315/425/440/500, UK 290/370/550/570, band 45→55 / 39→46, AE toggle 1,035…); zero JS errors. Function RATES == the old inline ladder for all 15 market/key pairs. 0 of 30 pages carry a ladder figure.
- Netlify Pretty URLs was unticked by Alex but only applies on the next deploy — 07c is that deploy. After drop: check /wholesale-coffee answers 200 (no 301), then Search Console "Validate fix" + request indexing /wholesale-coffee, /origins.
- Not touched: quote-confirm.js / checkout.js (whether they hold their own price copies is unchecked). FAQPage Question URLs still point at nofilter.sg/faqs#… on all markets.

## 7 Sep 2026 (evening) — SHIP-2026-09-07b built, to be dropped on nofilter-site
- Why: Search Console shows the 7 main SG pages EXCLUDED ("Alternate page with proper canonical tag"): Netlify Pretty URLs 301'd /x -> /x/, the served page's canonical said /x, loop. Alex unticked Pretty URLs in Netlify (nofilter-site); the setting only applies on the next deploy, so 07b is that deploy. After the drop: verify /wholesale-coffee answers 200 with no redirect; then "Validate fix" in Search Console + request indexing for /wholesale-coffee and /origins. If the redirect persists, Option B: switch canonical/og:url/sitemap/hreflang to the slash form across all markets.
- 07b = 07a + GBP button on the shop price board (data-pbm="UK"). Same 56 files, superset. market-pin / route-base / route-meta tests pass; FAQ chain re-run for sg/ae/uk.
- GENERATOR REPAIRED: build.sh did not reproduce the master (the 6-7 Sep UK edits + GBP were edited straight into the master). Captured as patches/patch_ukmarket.py (9 hunks) and appended to the chain; build.sh output is now byte-identical to the master (md5 b7ec3ecea5c8). Rule going forward: every master edit is a patch in the chain, never a direct edit.
- patches/patch_ratesplit.py (5 Sep, moves the rate card out of the document) exists, applies cleanly, but is NOT in the chain and NOT in the master. Alex to decide whether it ships.

## 7 Sep 2026 — queued for the NEXT drop (master edited, NOT yet built/deployed)
- Master: shop price board now has a GBP button (data-pbm="UK"); it was hardcoded SGD/AED so /uk/shop showed no pressed currency. Rebuild + run route-meta/market-pin/route-base tests before shipping.
- Search Console flags the 4 Product JSON-LD entries: no offers/review/aggregateRating. Decision: leave until retail prices are commercial (master comment says bag prices are placeholders; only SG 1 kg 80 confirmed). When shop launches, add offers per market from MARKETS.bag250/bag1kg.
- Still queued: FAQPage Question URLs hardcoded to nofilter.sg/faqs; trailing-slash vs canonical mismatch (Netlify pretty URLs).

## 7 Sep 2026 (later) — SHIP-2026-09-07a LIVE on nofilter-site
- Alex deployed 07a. Verified live in browser: every /uk page serves AND renders UK title/description (06b bug gone); real click /uk/ -> /uk/shop keeps UK title; nofilter.ae unchanged (UAE title, AED); /uk/faq -> /uk/faqs/, /faq -> /faqs/; /uk routes 200 with must-revalidate; unknown /uk path -> 404.
- Known, not fixed: FAQPage JSON-LD Question URLs on all markets' /faqs point to nofilter.sg/faqs#... (pre-existing on AE too). Fix in nf-build-tools/faq/build_faq.py on next drop.
- Next: submit sitemap.xml in Search Console for nofilter.sg and nofilter.ae properties + Bing; optional URL inspection for /uk, /uk/wholesale-coffee, /uk/trade-pricing, /faqs.

# NoFilter website — handoff to the next cowork session

> **Current as of 7 Sep 2026.** Read the 7 Sep block, then 6 Sep, then 3 Sep.

## State on 7 Sep 2026

- **Drop `SHIP-2026-09-07a`.** 06b is live and still carries the bug 06b was
  built to fix. The tables were right; `marketKey()` was not. It reads
  `data-mkt` off `<html>` — which NOTHING sets, the attribute only ever lives on
  the market buttons — and falls through to a hostname test that can only answer
  AE or SG. So on /uk it said 'SG' and applyRouteMeta() rewrote every UK page's
  title and description with the Singapore ones a moment after load. `/ae` was
  never affected: its hostname answers for it.
- **The fix:** `marketKey()` now reads the page's own `nf-market` pin before
  falling back to the hostname, the same tag `nfHomeMarket()` reads. Additive —
  a page without a pin behaves exactly as before, so SG and AE are untouched.
- **The first version of `route-meta.test.mjs` passed while the site was wrong.**
  It stubbed `marketKey()` by having `documentElement` return the market, which
  is precisely what the real DOM does not do. It now lifts the REAL `marketKey`
  out of the built page and gives it a realistic document: no `data-mkt`, the
  page's pin, the tree's hostname. It fails on 06b (19 mismatches) and passes on
  07a. Lesson worth keeping: a test that stubs the thing under test proves
  nothing.

## State on 6 Sep 2026

- **`SHIP-2026-09-06b` supersedes 09-06a — drop it.** 09-06a went live and is
  fine to look at, but it carries a rendering bug: `applyRouteMeta()` rewrites
  the title and description on every client-side route change, and with tables
  for SG and AE only it was overwriting the /uk pages' correct served metadata
  with the SINGAPORE strings. The HTML said "Wholesale coffee for UK offices and
  cafés"; the rendered page said "Wholesale coffee for offices, cafés and
  hotels". Google renders JS, so all ten UK pages would have been indexed under
  Singapore titles — the one thing the tree exists to avoid. Fixed by generating
  `ROUTE_META_UK` / `ORIGIN_META_UK` from the UAE tables with the same
  UAE→UK, AED→GBP substitution that wrote the page heads, so served and rendered
  cannot disagree. `nf-build-tools/uk/route-meta.test.mjs` checks all 27 route
  pages across all three markets and fails on 09-06a.

- **Ready to deploy: `SHIP-2026-09-06a`** (56 files), a strict superset of
  `SHIP-2026-09-04a` — the same 46 files plus the ten `/uk` pages. Live is still
  `SHIP-2026-09-03c`; 09-04a was never dropped. **One drop, to `nofilter-site`
  only.** The CDN needs nothing: all 74 referenced shared assets are already on
  `nofilter-shared` (checked live, 200s), so do NOT touch that site.
- **What this bundle adds over what is live:** the `/faqs` and `/ae/faqs` pages
  with their wiring (from 09-04a, never shipped), and the new `/uk` tree.
- **`/uk` — the UK market finally has URLs.** Ten pages at
  `https://nofilter.sg/uk…`, path tree on the Singapore domain, no new domain.
  Toolchain and reasoning: `nf-build-tools/uk/README.md`. Two things to know:
  the market is pinned per page by `<meta name="nf-market">` (there is no .uk
  host to pin on), read by `nfHomeMarket()` step 1b in the master; and `NF_BASE`
  in the master keeps a reader inside the tree, without which the first nav
  click lands on Singapore pricing. Both are additive — the root and `/ae`
  behave exactly as before, and there are tests for that.
- **Two stamping bugs fixed.** 09-04a's pages said `SHIP-2026-09-04b` (folder
  said `a`), and `404.html` had been announcing `SHIP-2026-08-30f` on every
  bundle since 30 Aug because it was copied verbatim. `build-ship.mjs` now
  stamps the 404 like it stamps llms.txt.
- **The template bundle now carries the current config.** `netlify.toml`,
  `sitemap.xml` and `llms.txt` in `nf-build-tools/ship/SHIP-2026-08-30f` were
  four days stale, so any rebuild silently regressed the FAQ wiring. They were
  synced from 09-04a and then given the UK rows.

### Checked, on the built bundle

30 pages: no duplicate title, description or canonical; every page has one
`<h1>`, a self-referencing canonical, `og:url` equal to it, and the full
`en-sg / en-ae / en-gb / x-default` set. Sitemap 30 URLs, parses, every one
resolves to a file in the bundle. All JSON-LD parses. All 47 inline scripts in
the master pass `node --check`. `nf-build-tools/uk/market-pin.test.mjs`: all 30
pages resolve to their own market, and the seven edge cases (London clock on
/uk, /uk on the .ae domain, `?mkt=sg` overriding the pin, and the three
pre-existing root behaviours) pass. `route-base.test.mjs`: inside /uk every
route resolves to /uk/…, `/shop` and `/uk/shop` are the same route, and the
root and /ae are unchanged.

### Before it goes up — for Alex

1. **Nobody has looked at these pages.** Still no renderer here. Serve the
   bundle and click through, especially `/uk`, `/uk/trade-pricing` (it should
   open in GBP with the Dr.Coffee range) and `/uk/faqs`.
2. **The UK copy is mirrored, not written.** Every UK title and description is
   the UAE one with UAE→UK and AED→GBP. It reads correctly and no two pages in
   the bundle share a title, but it is nobody's chosen wording yet.
3. The three items still open from 5 Sep are unchanged: the FAQ drone
   photograph's caption was written from a filename, the two certification
   source links are marked unverified, and the vocabulary gaps in §4 of
   `NoFilter-rollout-and-search-2026-09-05.md` (deforestation, bean-to-cup,
   CaféMatic model names, Dubai, Abu Dhabi) are still gaps.
4. After the drop: submit the sitemap again, and request indexing for the ten
   `/uk` URLs.

---

> **Current as of 3 Sep 2026 — read this block first; everything below the rule is older
> and partly stale (kept for the reasoning, not the state).**

## State on 3 Sep 2026

- **Working file:** `Marketing/NoFilter-Website/NoFilter-Website-Master.html`, built through
  **block 109** (98b and 106 withdrawn). Live site: `SHIP-2026-09-02v` on nofilter-site (once dropped) (nofilter.sg / .ae); CDN
  `_CDN-UPLOAD-SAFE` (269 files) on nofilter-shared. Check what is live with
  `curl -s https://nofilter.sg | grep -o 'nf-ship" content="[^"]*"'`.
- **Build tools survive in `nf-build-tools/`** (this folder; README inside). The master is the
  source of truth; the tools are how a SHIP bundle is cut from it:
  `cd nf-build-tools/ship && npm install && node build-ship.mjs ../../NoFilter-Website-Master.html SHIP-2026-08-30f SHIP-<date>`
  then `node verify-ship.mjs SHIP-<date>`. `patches/` holds every block (89 scripts) with its
  reasoning; `base/NoFilter-Website-Master-2026-08-31.html` (renamed from `PRISTINE.html` 4 Sep) + `build.sh` rebuild the master from scratch.
- **Deploy order, always:** `_CDN-UPLOAD-SAFE` → nofilter-shared FIRST (whole folder, it must
  stay a superset — drag-drop replaces the site), then the SHIP folder → nofilter-site. Claude
  does not deploy; Alex drags. A missing CDN drop shows up as a broken image (it did on 02j).
- Verified this round: local Lighthouse desktop 95–97; PSI live mobile 85 / desktop 100 (02d);
  the At Work route has nothing live on the scroll path (native split-flap board, map behind a
  poster facade, board sound off by default behind a speaker pill).

## Open items (3 Sep)

0. **/trade-pricing is Field Black** (block 100, 02m): ground #0c0e0d with a deep-canopy radial wash sized to the first screen, hairline inputs with a held orange focus halo, readout on #101311, and the CRT gate room recoloured to match. Was teal #1F6F6B since 25 Aug. Block 101 (02n): Alex's intro copy, the issued card ("Nearly there, <first name>.", a working "send yourself a fresh one" resend), Chrome autofill on the input surface, card seated at the top of the column once issued. Block 102 (02o): the CRT accepts ⌘V/Ctrl+V (modifier keys ignored, a paste handler; buffered if the prompt is not live). The access-code email copy ("Your quote builder is ready.") lives in the TEMPLATE's `netlify/functions/access-request.js` in nf-build-tools/ship/SHIP-2026-08-30f — the builder copies functions from there. Block 103 (02p): step 3's corner "Your quote →" hidden (progression is 3A→3B→3C via #morphLockBtn, now signal-filled), #ctaSend wears the access button's glow (nfProceed + doorRing), quote form name/company/email pre-filled from the door on unlock (window.__nfPrefillQuote). Block 104 (02q): the confirmation email is now the reader's RECORD — coffee, machines, servicing, price/kg, share, top-up, machines-and-servicing monthly, capital; NO volume (Alex: the cups figure is a rough estimate for showing a plausible NGO contribution, and quoting it back can put someone off a setup whose only fault was their own guess). Servicing is derived per machine in compute() as svcLines. On screen: "04 · Submission received / Thank you." + reference; the tasting-offer panel is gone. Subjects are title case. EMAIL COPY LIVES IN THE TEMPLATE at nf-build-tools/ship/SHIP-2026-08-30f/netlify/functions/. Block 105 (02r): .vp-ov pills hug their words (align-items:flex-start); hand-capitalised strings say PRCF INDONESIA and the builder's rename now skips them; Plate 09 overlay pill removed (the bar is the caption); Ground evidence (Layer 04) is live; the shop/console dossier film gets a real poster= (block 86 had turned it into data-poster with no hydrate path), Alex then said the dossier motion had been fine until recently, so the wipe and the scroll order were put back exactly (02s) — only the poster fix stands. Block 106 (02s): fig. 02 (home canopy plate) was keeps-standing.mp4, a 10s montage that is mostly hand-picking close-ups under the hero's dusk poster — the "sometimes zoomed in" — now canopy-loop.mp4 / -lite / -poster.jpg cut from hero.mp4's two canopy shots (dissolve-looped). WITHDRAWN the same day at Alex's call ("put my video back"), along with the 98b HD switch: fig. 02 is keeps-standing-lite.mp4 under hero-poster.jpg again (02t). The canopy-loop files are on the CDN but unreferenced. Blocks 107–108 (02u), from Alex's console trace of the shop dossier: (107) the telemetry rail's slim/expand logic tested `location.hash===''` for home, true on every PATH route since block 88 — /shop was running home's 48px rail compensation; now `window.__nfRoute==='home'`. (108) nfRailGap() clears the shop lead's PINNED height (a hidden is-stuck clone, measured in-frame) so the landing scroll targets where the bar will be — one scroll instead of two; and the carousel clearance runs after the page has arrived, compensating by the measured shift (Chrome's scroll anchoring already holds the dossier; a fixed -vpSpace on top sent the page to 0). Probe: nf-build-tools/ship/probe.mjs. Block 109 (02v): ONE VOLUME — the 3C cups-a-year slider. The 25 Aug nominal 5 kg per pick (Q.kg) is now only the pick flag; compute() derives kg from window.__nfVolCups() at 18 g/cup ÷12, shared equally across picked origins; window.__nfRecalc() published; the slider recalcs the console; payload cupsY is the slider value. Desk email row is 'Coffee volume · their estimate'. The Netlify Forms backstop (formresponses@netlify.com) reads the same compute() so it is corrected too — its email notification can be switched off in Netlify → Forms if the desk copy is enough.

1. **Quote plate video:** done 3 Sep (block 99, SHIP-2026-09-02l) — quote-pour-2-lite.mp4 + quote-pour-2.jpg from Pexels 6204972; old files left on the CDN.
2. **Canopy plate (fig. 02, home):** best source is 1600×900; a 4K original would allow a sharp
   1920 encode for wide screens (block 98b picks `data-src-hd` at ≥1100px).
3. **GJI logo** for the NGO marquee (initials are in the roll-calls; no mark yet).
4. **Cleanup awaiting Alex's per-item OK:** `_SHIP-2026-09-02a…k.tgz`, `_ship30f.tgz`,
   `SHIP-2026-09-02a…j` folders (02k is live), `_pour-options.jpg`, `nf-build-tools-2026-09-03.tgz`
   (unpacked copy kept), and the contents of `_to_delete/`.
5. **Search Console:** request indexing for `/shop`, `/origins`, `/trade-pricing`,
   `/wholesale-coffee` and the four origin URLs (path router since block 88). PSI re-run on 02k.
6. Longer-term perf levers, in order of payoff: route-deferred quote-console boot (largest mobile
   TBT), hero video weight, JPG stills → WebP, hero settle CLS (0.09–0.11, Alex's call).

## Standing rules (unchanged)

One master, edited in place, no variant filenames. Never navigate or overwrite Alex's open Chrome
tab — open your own and close it. Never delete without explicit confirmation. Never move or rename
`Clients/` or `_shared/`. Never paste a live token into chat. Alex is red-green colourblind — no
information carried by red/green alone. Before writing `patch_<name>.py`, `ls` for it first (two
existing patches were overwritten this way and had to be recovered).

---

# (older handoff, pre-3 Sep — state below is historical)

Working file: **`Marketing/NoFilter-Website/NoFilter-Website-Master.html`**

> **Corrected 30 Aug 2026.** This line used to name `index.PREVIEW-htl-glitch.html`, which had
> not been the working file for weeks — the site moved to what was then called `_OPTION-D.html`
> (renamed to `NoFilter-Website-Master.html` on 30 Aug). Every session reading this note was
> being pointed at the wrong file. The old preview is archived at
> `_archive/tests-and-options/index.PREVIEW-htl-glitch.html`.
>
> The master carries `data-nf-build`; every `SHIP-…` bundle built from it carries the same stamp.
> Before dragging a SHIP folder to Netlify, run `_tools/nf-ship-stamp.mjs` on it so the live site
> can say which build it is: `curl -s https://nofilter.sg | grep nf-ship`.

---

## 1. HOW WE HANDLE ITERATIONS & RENDERS  ← read this first

**Claude cannot see the page.** There is no working renderer in this environment: headless
chromium is unavailable, and the Chrome MCP can't open a local `file://`. So Claude can prove a
file *parses*, never that it *looks right*. **Alex is the eyes.** Never say something "renders
correctly / looks good / crosses cleanly" — say what you changed and ask Alex to eyeball it.

**Do NOT iterate on visuals blind.** This session burned many cycles nudging CSS values by guess
(header size, frame position, overlaps) and repeatedly missing. What actually worked:

- **Build a side-by-side test file** when a layout direction is undecided. We made
  `_test-layouts-4up.html` (four layout skeletons, same content) and Alex picked one in a single
  pass. Do this instead of guessing one layout and re-rolling it five times.
- **Give Alex a live tuner** for numeric taste calls. A `*.TUNE.html` copy with sliders + drag,
  a live readout, and a "Copy values" button. Alex dials it, pastes the values, Claude bakes the
  exact numbers into the real file. This is how position/scale/size got settled.
- **Ask at forks.** Use the question tool at genuine decision points (which straw colour, which
  cartographic line, which layout) rather than picking blind and rebuilding.
- **One change → verify → next.** Atomic edits. After every JS edit: extract inline `<script>`
  blocks, strip HTML comments, `node --check` each. After structural edits: script-check tag
  balance (`<section>`/`</section>`, `<div>`/`</div>`, `<figure>`) over the edited region.

**To view WITH media, the file must be opened from its own folder** (Chrome `file://`) or served:
`cd` into `Marketing/NoFilter-Website` and `python3 -m http.server 8080`, open
`http://localhost:8080/index.PREVIEW-htl-glitch.html`. A preview card / fresh session sandbox
cannot reach sibling files, so local clips go blank there.

---

## 2. MEDIA / CDN — the render-everywhere problem (and the deploy landmine)

**Why videos "don't show" in a new session:** five editorial clips are referenced by *bare
filename* — `hero-trim.mp4`, `mono-coffee-long.mp4`, `clears-forest.mp4`, `keeps-standing.mp4`,
`mega-farm-test.mp4`. They only resolve when the HTML is opened beside them. Established assets
don't have this problem because they use absolute `https://nofilter-shared.netlify.app/…` URLs.

**Current state:** refs are RELATIVE right now (so Alex can view locally). When the CDN is
updated, flip those five to the absolute `nofilter-shared` URL and they'll show everywhere.
Do this flip ONLY at deploy time — absolute refs break local viewing until the assets are live.

**Deploy landmine (this went wrong TWICE — treat as sacred):** a Netlify drag-drop deploy
*replaces the entire site*. `nofilter-shared` hosts ~150+ shared assets used across every client
pitch. **Never deploy a folder containing only the new clips — it wipes everything.**
- Source of truth for the CDN = `Clients/_shared/` root (152 web assets). Do NOT move/rename
  `Clients/` or `_shared/` (breaks ~1,000 symlinks).
- Staged and SAFE: `NoFilter/_CDN-UPLOAD-SAFE/` = all 152 `_shared` assets + the 3 new clips =
  155 files, a verified superset of what's live. Deploy the WHOLE folder.
- `NoFilter/_CDN/_CDN-INCOMPLETE-DO-NOT-DEPLOY/` = an earlier partial folder — do not use.
- Still owed before deploy: Alex pasted only a PARTIAL live file list. Get the FULL Netlify
  deploy file list and diff it against `_CDN-UPLOAD-SAFE` to confirm 100% coverage.
- Claude does NOT deploy. Hand Alex the drag-drop steps. See `_CDN/_CDN-COMPLETE-HOW-TO-DEPLOY.md`.

---

## 3. WHERE THE DESIGN IS NOW

`index.PREVIEW-htl-glitch.html`, top to bottom:
- **HOLD THE LINE glitch hero** — hero-trim.mp4 intercut with mega-farm-test.mp4; "Hold / the /
  line." drop in word-by-word; on "the" the monoculture surfaces clean ~680ms then glitches out.
- **"What most coffee does / Grown where it's cheapest"** — cream band, **Polymer-style stack**
  (chosen from `_test-layouts-4up.html`): kicker → big headline → full-width 2:1 mono hero (the
  two-clip glitch-cut mono⇄cleared) → lede → thin rule → 3-col row ("One crop" stat + 2 body cols).
- **Torn seam** — jagged, slightly diagonal red line tearing cream away to reveal straw.
- **"NoFilter backs the ones still standing"** — straw (`--nf-straw:#ffe8c3`) band, same Polymer
  stack mirrored in treatment (warm canopy hero = keeps-standing.mp4, "5–10%" stat in red).

Editorial CSS is scoped under `.ed` / `.ed-band--problem` / `.ed-band--solution`. The section
runs wider than the site grid via `--ed-w:min(1520px,94vw)`.

**Stale:** `index.PREVIEW-htl-glitch.TUNE.html` was built for the earlier floating-frame model
and no longer maps to the Polymer layout. Rebuild it (around column-ratio + hero height) only if
Alex wants to fine-tune this version.

---

## 4. OPEN THREAD — the cold open (Alex's live concern)

Alex's words: the intro is "a hard intro… no context at all." A first-time visitor hits HOLD THE
LINE (a rallying cry) then the problem, never learning what NoFilter is or what "the line" means.

**Fix = a short orienting standfirst between hero and problem section.** CRITICAL: use NoFilter's
REAL positioning from the files, not invented copy. (Claude invented "specialty coffee" here and
was rightly corrected — always pull from source.) The real positioning, verbatim from
`index.html` / `origins.html`:
- "Coffee that keeps the forest standing." / meta: "Workplace coffee… 5% to 10% of every sale to
  our NGO partners."
- "NoFilter is the other kind: grown on that standing edge, under canopy, so buying it holds the
  ground instead of taking it."
- Origins: coffee grows in the **agroforestry** that hems threatened forests (Batang Toru, Leuser,
  Arakan highlands); "that agroforestry **is the line itself**… it only holds while the coffee
  finds a buyer." NGO partners: PRCF, SRI, YOSL-OIC, Fauna & Flora.

Draft standfirst (built only from the above), awaiting Alex's go:
> NoFilter is coffee that keeps the forest standing. It's grown under canopy, in the agroforestry
> that hems threatened forests — Batang Toru, Leuser, the Arakan highlands — a living, working edge
> that holds the clearing back. That edge is the line. And it only holds while the coffee finds a buyer.

Open question Alex hasn't answered: does it read as "workplace coffee" (the meta framing) or just
"coffee" — this preview looks like a general site, not the workplace one.

---

## 5. NON-NEGOTIABLE RULES (from workspace CLAUDE.md + earned this session)
- Files on disk are the source of truth. Never invent brand facts — grep the files.
- Preview-copy discipline: never edit protected `index.html`; work in the `*.PREVIEW-*` copy.
- Quarantine, don't delete. Confirm before rename/move/overwrite. Protected assets list:
  `Marketing/NoFilter-Website/_PROTECTED-DO-NOT-DELETE.md`.
- VERBATIM-OR-NOTHING when reusing canon components (copy the bytes, don't rebuild from memory).
- Verify every edit (`node --check` + tag balance); never claim it renders.
