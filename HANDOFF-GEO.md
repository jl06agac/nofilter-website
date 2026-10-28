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
- OPEN QUESTION: founding year. The site's JSON-LD says 2019; the UEN suggests 2018 incorporation. Ask Alex which year (and month) before setting the Google Business Profile opening date.

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

## Still to do, in priority order

1. Search Console, nofilter.ae property: request indexing for `https://nofilter.ae/wholesale-coffee` and `https://nofilter.ae/faqs` (yesterday's quota is spent; Google allows about 10 a day).
2. AI-assistant baseline. Ask ChatGPT (with search), Perplexity and Google AI Mode these questions and record whether NoFilter is named, how it's described, and who is named instead:
   "office coffee supplier Singapore", "office coffee supplier Dubai", "office coffee Abu Dhabi", "office coffee supplier London", "EUDR compliant coffee supplier", "sustainable coffee for offices Singapore".
   Save the results as a dated table. The monthly check repeats this and compares.
3. Wikidata (Alex creates it in his own account; fields already given to him): label NoFilter; description "coffee company supplying offices, cafés and hotels in Singapore, the UAE and the UK, sourcing from conservation projects"; aliases NoFilter Coffee, NoFilter Pte. Ltd, NoFilter LLC; instance of business; industry coffee industry; country Singapore + United Arab Emirates; HQ Singapore; inception (confirm year); official website nofilter.sg + nofilter.ae; LinkedIn company ID nofiltercoffee; product coffee. When he sends the Q-number, add `https://www.wikidata.org/wiki/Q...` to the Organization `sameAs` in the template JSON-LD and rebuild.
4. Business Profile finishing: the opening date (after the founding-year answer), plus the UAE profile once verified.
5. Multi-page build (about a day of work; the biggest remaining gain). Today every URL serves the whole SPA, so crawlers that don't run JS (GPTBot, ClaudeBot, PerplexityBot) see the same blob at 30 addresses. Change the build pipeline, not the master, so each URL's HTML carries only its own route section plus shared chrome, with its own H1, title, description and canonical. The router must still work when people navigate within the site. Verify every route renders, check for JS errors with Playwright, and check that the access-verify function still serves rates.
6. Known, harmless: Search Console reports "Product snippets: 4 invalid items" because the four coffees are typed as Product with no offers. Leave it until the shop opens and real prices exist; then add `offers`.
7. Parked by Alex: roundup or directory pitches that need favours; event write-ups (Davos, World of Coffee Indonesia, Singapore International Agri-Food Week) pending his facts; 020.co.uk; Crunchbase; a comparison page (certification vs conservation sourcing).

## Monthly check

The prompt is in the entity profiles doc, under "Monthly check: scheduled task prompt". It wasn't scheduled, because the scheduler refused it; Alex can set it up himself. It covers Search Console figures for both properties, the AI-assistant question set, Business Profile status, and drift in the facts-that-must-match table.
