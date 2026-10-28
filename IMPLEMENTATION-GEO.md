# SEO and route build implementation

Baseline completed on 28 October 2026 before source edits: 21 interface responses each from ChatGPT Search, Perplexity and Google AI Mode. The canonical baseline is the existing responses.json record, not a new run.

## Implementation

- Integrate the existing HTML-parser route splitter into build-ship.mjs after template transplantation and market substitutions. Preserve shared styles, shell and guarded runtime.
- Render one active route per file. Origin detail URLs retain one origin record plus common verification content and links to the origin index. Give every page one visible H1.
- Use normal page navigation for routes and market changes. Preserve anchor interactions within a page and the existing design. Keep canonical and hreflang metadata authoritative after JavaScript starts.
- Add concise service information in the master, with market variants applied by the builder. Cover Singapore, Dubai, Abu Dhabi, UAE, London and UK on the existing three market pages. No new city pages: distinct operational information is insufficient to justify them.
- Correct the brand launch to May 2024, Singapore incorporation to 2018, and leave UAE incorporation unspecified. Record this in HANDOFF-GEO.md.
- Clarify availability versus existing clients, conservation partners, 5–10% contributions and the limits of plot mapping. Update FAQs and llms.txt from their existing sources.
- Keep the existing rate extraction and server verification. Do not expose rates or access credentials in reports or screenshots.

## Validation and release

Run the exact handoff commands with SHIP-2026-08-30f and rebuild the existing SHIP-2026-10-28a in place, preserving .netlify. Check every route, metadata, initial HTML, pricing leakage, JavaScript syntax, browser navigation and markets, mobile/desktop and successful/denied pricing access. Produce a draft Netlify deployment only if access is available, never nofilter-shared. Production deployment requires preview review.

The original repository is read-only in this session. Work is prepared in the current workspace checkout; source application and commit in the original remain blocked until write access is available.

## Coverage review

| Area | Prepared change and remaining limit |
|---|---|
| General office supply | Existing wholesale pages remain the primary commercial routes. Singapore, Dubai/Abu Dhabi/UAE, and London/UK each have explicit service and availability text. |
| Sustainable office coffee | The same pages explain mapped plots, satellite verification, NGO partnerships and contractual 5–10% contributions. No near-duplicate city pages were added. |
| Titles and descriptions | Market-specific office-supplier titles and sustainability-led descriptions; London added to the UK title. Browser metadata preservation remains to be tested. |
| Headings and visible copy | One H1 in each generated page. Quote H1 is in the public gate, not the hidden console. Initial HTML contains the relevant service/origin record. Visual layout is not yet verified. |
| FAQs | One content source generates visible answers and FAQ schema. Client status and EUDR wording corrected; links use the appropriate market tree. |
| Internal links | Real route anchors, origin-detail index links and footer FAQ links. Runtime interception uses document navigation. Browser/back/forward tests remain required. |
| Canonical and hreflang | Thirty routes retain their expected canonical and en-SG/en-AE/en-GB/x-default links, checked statically. |
| Structured data | Brand launch and Singapore incorporation separated; UAE incorporation left unspecified. Toru NGO partners corrected. Product offers remain parked. |
| Sitemaps and llms.txt | Existing sitemap generation retained. llms.txt describes market availability, traceability limits and the new route-specific output. |
| Pricing | Server-side rates extraction retained, HTML placeholders neutralised and non-pricing pages omit the quote letter. Handler integration tests passed with intercepted email. Browser gate and deployed static-source denial still need verification. |

## Current verification boundary

Static assertions pass on all 30 content pages and 54 distinct inline scripts parse. Generated request/verification handlers pass access and denial checks without real email transmission. These are not end-to-end browser results. Local preview server startup, file-based browser preview and Netlify CLI settings writes were blocked by the session. There is no draft or production deployment. The source commit is a review checkpoint pending browser QA, not a release-ready claim.
