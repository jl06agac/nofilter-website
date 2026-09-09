# Rollout, search and the London question
### 5 September 2026 · revised after Alex corrected §5

---

## 1 · What is in SHIP-2026-09-04a now

The bundle is complete and ready to upload. Since last night it has gained the
FAQ page and the wiring that makes it a real route.

**The page.** `/faqs` and `/ae/faqs`, sixteen questions in four sections, built
from the same source as its FAQPage JSON-LD so the two cannot disagree. Every
answer is in the initial HTML; the accordion only hides it visually. The final
cut carries the two brand devices: the mark is the wordmark's own cross, the
same two paths the site cursor uses, and the Tapanuli hand prints run down the
left margin, revealed as you scroll. Both are embedded in the page, so neither
depends on the shared CDN.

**The wiring**, all four files edited in place in the bundle:

- `netlify.toml` — a cache header for `/faqs` so it revalidates like the other
  route pages rather than falling through to the platform default; eight rewrite
  rows so `nofilter.ae/faqs` serves `/ae/faqs` in both path forms and all four
  scheme and www spellings, placed above the `/ae/*` guard so the order still
  holds; and `/faq` 301 to `/faqs`, since the singular is the commoner typing.
- `sitemap.xml` — both FAQ URLs with their hreflang set. Twenty URLs now, ten
  pages across two domains, and it parses.
- `llms.txt` — the FAQ added, and four things corrected that were simply wrong:
  it claimed the site has no `rel=canonical` (every page has one, pointing at
  itself on its own domain), it said "five pages" where there are ten, it said
  the sitemap holds ten URLs where it held eighteen, and it said the United
  Kingdom is not a priced market when the build prices it in full. The last one
  matters most, because this is the file written to be read by answer engines.
- `_superseded/` — the two comparison folders from yesterday moved out of the
  bundle to `_faq-superseded-2026-09-05/`, so nothing spare gets uploaded.

**The toolchain** is now at `nf-build-tools/faq/` with a README. It was only in
the cloud session before, which meant the next rebuild would have had no way to
regenerate the page.

---

## 2 · What I checked, rather than assumed

- 36 assertions on the page itself: every palette value, the type hierarchy, the
  row geometry, the answer block, the two devices, the mobile layout. All pass.
- Deep links (`/faqs#certification` opens the right section and question),
  mutual exclusion of the four sections, 390px with no horizontal overflow,
  every answer present with JavaScript disabled, zero console errors.
- Across all twenty pages: one `<h1>` each, a self-referencing canonical, three
  hreflang links, an `og:image`, a title inside the length a result shows and a
  description inside the length a snippet shows. No duplicate titles or
  descriptions anywhere. That last one was not true an hour ago: the two FAQ
  pages shared an 83-character title and a 219-character description, both of
  which would have been truncated. They are now per market, like every other
  page pair.
- The structured data graph on every page: `Organization`, both legal entities
  as `LocalBusiness`, `WebSite`, the wholesale `Service`, and the four coffees as
  `Product`. `/faqs` adds `FAQPage`. All of it parses.
- `robots.txt` names GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-User,
  PerplexityBot, Google-Extended, Applebot-Extended, Amazonbot and Bingbot and
  allows each one. That is the right call and it is unusual; most sites have
  either blocked them by accident or never thought about it.
- With JavaScript off, the pages still carry 1,000 to 1,600 words each. The site
  is genuinely crawlable, not a shell that fills itself in.

---

## 3 · Before you upload

Four things, in order, and none of them take long.

1. Open `localhost:8000/faqs/` and `localhost:8000/ae/faqs/` and click through
   the four sections. I have looked at these in your Chrome, but you have not.
2. Check the drone photograph in "How do you verify the forests and coffee
   origins?" is the frame you would want there. I wrote its caption and alt text
   from the filename, having never seen it: it is described as a verification
   pass over mapped plots. It appears on twelve other pages, so if the wording
   is wrong it is wrong in more than one place.
3. Confirm the two source links in the Rainforest Alliance and Fairtrade answer
   still resolve to the pages they claim. I have had no network to them from
   this session and they are marked unverified in my notes.
4. Upload the folder. Then fetch `nofilter.ae/faqs` and `nofilter.sg/faq` once
   each and confirm the first serves the UAE page and the second redirects.

---

## 4 · Search and AI discovery: the honest state

The technical side is in good shape and I would not spend more time on it. What
is missing is vocabulary, and it is missing in a way that costs you the exact
queries you named.

I counted every phrase in the visible copy of all twenty pages. The strong
terms are strong: *forest* appears 323 times, *NGO* 190, *conservation coffee*
48 on twenty of twenty-one pages, *rainforest* 48, *orangutan* 44, *agroforestry*
24. Nobody will be confused about what NoFilter is.

These appear **zero times anywhere on the site**:

| Term | Why it matters |
|---|---|
| deforestation, deforestation-free | The phrase procurement teams and journalists now use, and the one the incoming regulation is written in |
| espresso, bean-to-cup, coffee machine | You lease bean-to-cup machines; none of those three words is on the site |
| CaféMatic 2 / 5 / 6 / 8 | The model names never appear in visible text on any page, with JavaScript on or off. They are inside a script, behind a click |
| Dubai, Abu Dhabi | *UAE* appears 54 times; the cities people actually search do not appear at all |
| coffee supplier, corporate coffee | The phrases a buyer types |
| biodiversity | Missing from a site about conservation |
| London, United Kingdom as a market | Covered in §5, and it is the biggest of these |

*office coffee* appears twice, on two pages, though `netlify.toml` itself records
that "/office-coffee is the phrase with the most search volume of any spelling of
this page". *traceability* appears twice. *single-origin* appears four times.

None of this is a content rewrite. Five or six sentences placed in existing
paragraphs would close most of it. Proposed, for you to accept, change or bin:

- **On `/wholesale-coffee`, in the machine section.** "The machines are
  bean-to-cup espresso equipment: a CaféMatic 2, 5, 6 or 8 depending on how many
  cups a day you need." That single sentence puts four model names, *bean-to-cup*
  and *espresso* into crawlable text for the first time.
- **On `/wholesale-coffee` or `/faqs`, on the UAE side.** Name Dubai, Abu Dhabi
  and Sharjah once where the site currently says "across the UAE". You already
  say Singapore 117 times; the UAE cities get nothing.
- **In the FAQ answer "What does conservation coffee actually mean?"** A sentence
  distinguishing what you do from deforestation-free compliance: that a
  deforestation-free claim says a plot was not cleared, while your contribution
  says money went to the organisation holding the forest. That is a real
  distinction, it is yours, and it puts the term on the page without making a
  claim you would have to defend.

I have not made any of these edits. Copy is yours and you have been clear about
that.

---

## 5 · London, and the UK

**Correction first.** The first version of this note said there is no UK entity
and no UK rate card. The second half is wrong. I took it from `llms.txt`, which
says "The United Kingdom is not a priced market", and I did not check it against
the build. I should have.

**What the build actually does.** `MARKETS.UK` in the quote builder is a
complete, priced market: `priced: true`, GBP, `en-GB`, its own wholesale ladder,
its own three contribution bands at the same rates as Singapore and the UAE, its
own rental and purchase prices, its own service and callout rates, and a
different equipment range entirely — Dr.Coffee rather than CaféMatic. The
footer carries "United Kingdom · NoFilter Pte. Ltd · Now accepting UK enquiries
· alex@nofilter.sg". A visitor clicks the Union Jack and gets a real UK quote.

So the only true part of what I wrote is that there is no UK-registered company.
The UK is served by NoFilter Pte. Ltd, which is a normal arrangement for
exporting and not a gap that needs closing before you sell.

**The real problem, which is worse than the one I described.** The UK market has
no URL. It is a state inside the page, held in `nf-mk` and applied by
`applyMarket()`. Every consequence of that runs against you:

- There is no page for Google to rank for a UK query. Not a weak page. None.
- `hreflang` on all twenty pages is `en-sg`, `en-ae`, `x-default`. There is no
  `en-gb`, so no page is offered to Britain.
- The sitemap has twenty URLs and none is British.
- A crawler, and every AI answer engine, sees the Singapore market. It cannot
  click a flag. Your UK pricing, the Dr.Coffee range and "Now accepting UK
  enquiries" are invisible to all of them.
- You cannot link to it. There is no URL to put in an email, a deck or a
  LinkedIn post that opens on GBP.

**What I would do, in order.**

1. **Give the UK URLs on the domain you already own.** Mirror what `/ae` does:
   a `/uk` tree, market pinned server-side, `en-gb` added to the hreflang set on
   every page, ten more URLs in the sitemap. This is the single highest-value
   change on this list and it needs no new domain, no new company and no new
   copy. The machinery exists and has been debugged once already.
2. **Then** decide on a domain. A `.co.uk` would add a strong UK signal on top
   of pages that already exist and already rank a little. Buying one first, and
   pointing it at a market with no pages, buys nothing. I could not check
   availability from this session; the registry lookup needed a permission
   nobody was there to give.
3. `llms.txt` is corrected as of this morning: the UK is described as the priced
   market it is, with no numbers published, and the note that it has no URL of
   its own is stated plainly so an answer engine does not go looking for one.

**The London pitch that is missing from all of it.** Coffee is one of eight
commodities in the UK's forest risk commodity regime. Legislation is expected in
2027, it will apply to businesses over £1m turnover, and it will require them to
hold **geolocation data about the origin of the products they use**. You have
that already: plot boundaries, buffer, forest beyond, mapped with partners and
checked against satellite monitoring. It is on `/origins` and in the FAQ.

That is the argument for a London buyer, and it is nowhere on the site. Not
"our coffee is nice" but "when your due diligence obligation lands, we can
already hand you the polygon". The EU version applies to large and medium
operators from 30 December 2026 and to small ones from 30 June 2027, so any
London buyer with a European parent is being asked about it now.

I am not a lawyer and neither of us should present the obligation to a customer
as advice. Pointing at the regime and saying what you hold is safe ground.

## 6 · After launch, in order

1. Register both domains in Google Search Console and Bing Webmaster Tools, and
   submit `https://nofilter.sg/sitemap.xml` in each. Bing feeds Copilot and
   DuckDuckGo, so it matters more than its market share suggests.
2. In Search Console, watch the Saucy Bean 301s land. Eight old Squarespace URLs
   are redirected in `netlify.toml`; you want to see the credit move, not
   evaporate.
3. Ask PRCF to update the `apes-for-apes` link from `saucybean.co` to
   `nofilter.sg`. The 301 passes it on, but a direct link is worth more and it is
   one email.
4. Only then look at rankings. Nothing before six weeks means anything.

---

## 7 · Still open, needing you

- The drone photograph's caption and alt text, above.
- The two source URLs in the certification answer.
- The Xero templates: both loose-file sets still to upload, the OCBC account
  number to verify, whether WIO accepts non-AED, and the credit-advice tear-off
  decision.
- Your own pass through the quote builder end to end. The Netlify functions
  cannot be tested locally, so nobody has run it since the split.

---

**Sources for §5.** The UK regime and its scope:
[GOV.UK, The UK's approach to deforestation regulations](https://www.gov.uk/government/publications/the-uks-approach-to-deforestation-regulations/the-uks-approach-to-deforestation-regulations).
The EUDR dates after the latest delay:
[VinciWorks, EUDR delayed again](https://vinciworks.com/blog/eudr-delayed-again-what-changed-what-is-now-fixed-and-what-businesses-should-do-in-2026/).
