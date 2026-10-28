# NoFilter findability (SEO/GEO): handoff

Written 28 Oct 2026, 12:10 SGT. For whoever continues this work (another AI or a person). Read all of it before touching anything.

## Goal

Make NoFilter findable in Google and in AI assistants (ChatGPT, Perplexity, Gemini, Claude) when B2B buyers search things like "office coffee supplier Singapore", "office coffee Dubai / Abu Dhabi", "office coffee London", "EUDR compliant coffee supplier". No agency. Nothing visible cluttering the site. Prefer work that doesn't involve asking third parties for favours.

## Facts that must stay consistent everywhere

- NoFilter supplies offices, hotels and cafés, and is set up for visitor attractions such as zoos (no zoo client yet; that's the point of saying it).
- Markets: Singapore (clients include hotels and cafés as well as offices) and the UAE (workplaces only so far; no Abu Dhabi client yet, but Abu Dhabi is served). UK: "now taking on clients in the UK / London". Never present the UK as an existing market.
- Named clients: Microsoft, Accenture, Blackstone, Eastspring Investments, Sprinklr. Do NOT list Compass Group publicly.
- Conservation NGOs (PRCF Indonesia, OIC, SRI, Fauna & Flora) are partners, never clients.
- Origins: Batang Toru (PRCF Indonesia, OIC), Batang Gadis (SRI), Gayo Lues (OIC), Sumatra; Arakan Mountains, Myanmar (being phased out).
- Contribution: 5 to 10% depending on the price band (5% below the opener, 10% at the opener and above). Do not write "a flat 5%".
- Not Fairtrade or Rainforest Alliance certified, by choice. Never call it "specialty coffee".
- Verification: plot polygons live, satellite live, drone rolling out 2026, ground evidence "coming soon".
- Founder: Alex Clark. Q Arabica Grader and Level 2 Processor.
- Phones: SG +65 8748 6814, UAE +971 56 966 7026. Entities: NoFilter Pte. Ltd (UEN 201839882N), NoFilter LLC (Sharjah, Shams).
- RESOLVED by Alex, 28 Oct 2026: NoFilter launched as a brand in May 2024. The Singapore company was incorporated in 2018 as Saucy Bean and later renamed NoFilter Pte. Ltd, retaining UEN 201839882N. The old 2019 date is incorrect. Use 2024-05 for the brand organisation, 2018 for the Singapore legal entity; do not invent a day or infer a UAE incorporation date. Business Profile opening dates must describe the relevant brand/business location.

## Alex's working rules (non-negotiable)

- British English. No em dashes. No disclaimers or provisos in client-facing copy. Understated, not salesy.
- Never paste a live token or secret into chat.
- One source of truth per thing; overwrite in place; no "-v2", ".PREVIEW", dated copies.
- Don't navigate or overwrite a browser tab he already has open; open a new one.
- When blocked, ask what he can supply; don't hand him a list of manual steps.
- He is red-green colourblind.

## The website and how it ships

Repo (git): `~/Desktop/NoFilter/Marketing/NoFilter-Website/`
- Master: `NoFilter-Website-Master.html`, a single-page app. Every URL serves the whole page with one `<section class="route">` switched on (routes: home, origins, shop, work, quote).
- Build: `nf-build-tools/ship/build-ship.mjs`. The template is ALWAYS `nf-build-tools/ship/SHIP-2026-08-30f`. Section 3b3 holds the per-market (sg/ae/uk) `SCOPE` string swaps for titles and descriptions. Section 2c strips retired markup.
- JSON-LD lives in the template's HTML heads (SHIP-2026-08-30f/**/*.html), not in the master.
- `llms.txt` lives in the template folder.
- FAQ content: `nf-build-tools/faq/faq_content.py` (19 questions, including office coffee supply, clients and EUDR).
- `build.sh` / the old patch chain no longer reproduce the master. Do not run it. Edit the master directly with small, reviewed patch scripts kept in `nf-build-tools/patches/_not-in-build-chain/`, then commit.

Rebuild IN PLACE (do not delete the SHIP folder; it holds the `.netlify` link):

```
cd ~/Desktop/NoFilter/Marketing/NoFilter-Website
S=SHIP-2026-10-28a
node nf-build-tools/ship/build-ship.mjs NoFilter-Website-Master.html nf-build-tools/ship/SHIP-2026-08-30f $S
python3 nf-build-tools/faq/build_faq.py $S/index.html $S/faqs/index.html sg
python3 nf-build-tools/faq/build_faq.py $S/ae/index.html $S/ae/faqs/index.html ae
python3 nf-build-tools/faq/build_faq.py $S/uk/index.html $S/uk/faqs/index.html uk
python3 nf-build-tools/faq/wire_links.py --site $S
node _nf-ship-stamp.mjs $S
```

Deploy (Alex runs this in his own Terminal; the sandboxes can't reach the Netlify API):

```
cd ~/Desktop/NoFilter/Marketing/NoFilter-Website/SHIP-2026-10-28a && netlify deploy --prod --dir . --functions netlify/functions
```

If it says "Not Found" for the site, run `netlify link --name nofilter-site` inside the SHIP folder first. Never deploy to the `nofilter-shared` site.

Git note: in this folder git can leave lock files behind. Clean with
`rm -f .git/HEAD.lock .git/objects/maintenance.lock .git/index.lock; find .git/objects -name 'tmp_obj_*' -delete`.

## What's done (live now, SHIP-2026-10-28a, commit 134)

Site:
- Per-market titles and descriptions: "Office coffee supplier in Singapore | NoFilter", "Office coffee supplier in Dubai and Abu Dhabi | NoFilter", "Office coffee supplier for the UK | NoFilter".
- The UK copy now says "now taking on clients"; the UAE copy says workplaces.
- Demo and placeholder strings that crawlers were reading as facts were moved into JS. Static console figures are correct. Partners are named correctly.
- Layer 04 (ground evidence) is shown as "Coming soon".
- The client logo marquee is pre-rendered with alt text naming the clients (no visible change).
- FAQ: added office coffee supply, clients and EUDR answers; 19 questions per market.
- llms.txt updated to match.
- JSON-LD: areaServed is Singapore, the UAE and the United Kingdom; the Service is named "Office coffee supply"; both entities carry their telephone numbers; foundingDate 2019; founder Alex Clark; knowsAbout includes "Office coffee supply" and "EUDR traceability".
- The nav venue link's aria-label is "Office coffee for offices, cafés, hotels and zoos" (the visible roller is unchanged).
- Retired #why route and retired beats are stripped from the bundle.

Off-site:
- Google Business Profile, Singapore: description updated and live; LinkedIn added under social profiles (pending Google review).
- Google Business Profile, UAE: created, NOT verified. Alex has to do "Get verified". After that: add the Abu Dhabi service area, description, photos and LinkedIn.
- LinkedIn company page (admin id 104435169): all fields updated; nofilter.sg and nofilter.ae added as approved email domains.
- Alex's personal LinkedIn About: final text agreed in chat (supplied to Alex; he pastes it himself).
- Bing Webmaster: both sites present; all 30 sitemap URLs submitted on 28 Oct.
- Google Search Console (domain properties sc-domain:nofilter.sg and sc-domain:nofilter.ae): indexing requested on 28 Oct for nofilter.sg home, /wholesale-coffee, /faqs, /uk, /uk/wholesale-coffee, /uk/faqs, and nofilter.ae home. The daily quota then ran out.
- Yellow Pages UAE: submitted.
- Entity profiles doc (Claude Docs artifact): canonical descriptions, per-platform fields, directories table, facts-that-must-match table, and the monthly-check prompt.

Baseline (Search Console, 3 months to 28 Oct): nofilter.sg 48 clicks, 7,690 impressions, average position 12.6; "arakan mountains" 5,587 impressions; "office coffee supplier" 70 impressions, 0 clicks. nofilter.ae: about 90 impressions.

## Status after this session, 28 Oct 2026

### Completed before website edits

All 63 expanded baseline responses were captured through the actual interfaces, 21 each in ChatGPT Search, Perplexity and Google AI Mode. Canonical evidence: https://chatgpt.com/library?file_id=libfile_b47236caf214819198f9f58fc873c451&account_id=personal. Summary and repeat protocol: https://chatgpt.com/library?file_id=libfile_f5107abf817481919ee628cd2e3ac539&account_id=personal.

NoFilter appeared in the conservation query in ChatGPT and Google, but none of the 54 location-specific answers. Perplexity cited NoFilter LinkedIn in the Singapore sustainable-office source list without naming it in the answer. Conditions differ across platforms; see the record. One run is a snapshot, not a stable ranking.

### External updates completed

- Search Console: indexing requests for https://nofilter.ae/wholesale-coffee and https://nofilter.ae/faqs were accepted on 28 Oct. Both were already indexed, with matching Google-selected canonicals. Last crawl shown: wholesale 7 Sep 2026 18:06:15; FAQ 13 Oct 2026 23:39:55, as displayed in the interface. Do not request again just to repeat this work.
- Singapore Business Profile: submitted May 2024, with no day, as the brand opening date for the Singapore service-area business. Save succeeded; Google displayed pending review. LinkedIn is present in the profile.
- UAE Business Profile: still verification required. No location-specific opening date has been inferred. Alex must complete verification before the remaining profile work.

### Source work prepared, not deployed

The original repository and the prior isolated copy still matched HEAD 68da69b and all 1,404 non-Git files at the initial comparison. The original had only its pre-existing .gitignore modification. A write probe in the original failed with Operation not permitted.

Current working checkout: /Users/alexanderclark/Documents/Codex/2026-10-28/new-chat-2/website-work/NoFilter-Website. It contains the source edits, template, dependencies, existing SHIP directory and preserved .netlify link. The original repository has not been edited. The unrelated .gitignore change is preserved and excluded from the intended commit.

See IMPLEMENTATION-GEO.md for the implementation and coverage review. The builder now projects each route from the master after the existing market/template transformations, rescues shared styles and retains guarded shared runtime code. Origin detail pages keep their own record. Native links and market navigation use document loads. FAQ pages retain their own metadata and content. The master retains standalone SPA behaviour.

Brand structured data uses 2024-05; the Singapore legal entity uses 2018. UAE incorporation is left unspecified. Service copy distinguishes existing clients from market availability. Mapping alone is explicitly not full EUDR compliance. Quote placeholders are neutral in source; the existing server-side rates extraction remains. Public reference figures remain public by design. The static function-source path is explicitly denied in Netlify redirects, but this still requires a deployed HTTP check.

The exact handoff build sequence ran in place in this checkout, using SHIP-2026-08-30f and SHIP-2026-10-28a. It produced 27 main/origin pages, three FAQs and the 404 page. No bundle was copied over the original.

Validation evidence is in validation/static-results.json and validation/access-results.txt. All 30 content pages passed the current static assertions; 54 distinct inline scripts passed syntax parsing. The actual generated access-request and access-verify handlers passed valid, invalid, wrong-email and expired-code tests. Both outbound emails were intercepted, so no third party was contacted and no live email-delivery claim is made.

### Required before preview or production

Browser route loading, cross-route navigation, back/forward, all market controls, desktop/mobile comparison, console/resource checks and an actual JavaScript-disabled browser run remain untested. The browser pricing flow and safe screenshot evidence remain required. Handler tests do not replace them. Do not mark this change release-ready.

This session blocked a local HTTP server (listen EPERM), and the browser security policy rejected file: URLs. Do not bypass those restrictions. Netlify status failed because the CLI could not write its settings temporary file under ~/Library/Preferences/netlify. No draft URL or production deployment exists. Original-source application and in-place original rebuild also remain blocked by read-only access.

Continue in a session permitted to write the original repository, run the local preview server and use Netlify's existing configuration. Recheck the original diff before applying source edits, preserve .gitignore and .netlify, complete browser QA, then create a draft deployment on the linked NoFilter site. Never deploy to nofilter-shared. Alex must see the draft before production.

## Wikidata review

Do not combine the NoFilter brand, Singapore legal company and UAE LLC as aliases for one undifferentiated legal entity. A brand item would use May 2024, month precision; a Singapore company item would use its incorporation date and former name. May 2024 is Alex-confirmed, but a suitable public reference for that precise month still needs to accompany a Wikidata claim.

Wikidata's policy permits a clearly identifiable entity described by serious public references; it is not the same as Wikipedia's article criteria. Review: https://www.wikidata.org/wiki/Wikidata:Notability. A public Companies.sg record supports the Singapore company name, UEN and former name Saucy Bean: https://www.companies.sg/business/201839882N/NOFILTER-PTE-LTD. It is a registry-derived secondary record, not an official ACRA extract. The company website and founder's launch announcement support brand identity and offering, but are self-published. The searches in this session did not establish strong independent coverage of the brand. Suitability is therefore plausible for the identifiable legal entity but not guaranteed; avoid presenting approval as certain.

Alex creates any item in his account as agreed. No item was created and no Q-number was supplied. Add a real Q URL only to the sameAs of the entity it actually describes, then rebuild. Do not invent an ID or add a company ID indiscriminately to every organisation node.

## Monthly comparison

Repeat the three exact office queries for Singapore, Dubai, Abu Dhabi, UAE, London and UK, plus conservation coffee supplier, traceable office coffee, and EUDR compliant coffee supplier. Use fresh interface searches, preserve responses and source panels, and record settings. Compare by platform plus exact query. Count answer mentions separately from source-only appearances; keep unavailable queries separate from absence. Keep the October evidence intact and append a new period for each month. No monitoring automation has been created.

## Parked work

- Product snippets: retain the known missing-offers issue until real shop offers exist. Do not invent prices or offers. The Toru partner wording was corrected to PRCF Indonesia and OIC without adding offers.
- Outreach/directory pitches, event write-ups awaiting Alex's facts, 020.co.uk, Crunchbase and the certification comparison page remain parked.
