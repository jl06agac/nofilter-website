# /uk — the UK market tree

The UK has been a fully priced market in the build for weeks (GBP, en-GB, its
own wholesale ladder, its own contribution bands, and the Dr.Coffee range in
place of CaféMatic) but until 6 Sep it had no URL. It was a state inside the
page, held in `nf-mk` and reached by clicking the flag. Nothing could rank for
a UK query, no page was offered to Britain by hreflang, the sitemap had no
British URL, and there was no link to put in an email that opened in GBP.

It is published as a path tree on the Singapore domain, `https://nofilter.sg/uk`,
not on a `.co.uk`. A domain bought first and pointed at a market with no pages
buys nothing; these pages rank on the domain that already does, and a domain
can be added later on top of pages that exist.

## What makes a UK page different from its Singapore twin

Bodies are identical across all three market trees — only the head differs — so
each UK page is its SG counterpart with:

- title, description, og:title, og:description, twitter:title, twitter:description
  (mirrored mechanically from the UAE page: UAE→UK, AED→GBP)
- canonical and og:url on `https://nofilter.sg/uk…`
- `og:locale` en_GB, `og:locale:alternate` en_SG
- `<link rel="alternate" hreflang="en-gb">` — added to all thirty pages, not
  just these ten
- `<meta name="nf-market" content="UK">` — the market pin

## The two pieces of machinery

**The pin.** `/ae` is pinned by the `.ae` hostname. There is no `.uk` hostname,
so a UK page declares its own market and `nfHomeMarket()` reads it (master,
step 1b — after `?mkt=`, before the domain). Pages without the tag are
unaffected. The tag has to arrive *fused to a tag that already differs* (it
rides on the description meta): `build-ship.mjs` diffs each template page
against the template index token by token and cannot place a pure insertion.

**The base.** `NF_BASE` in the master. Without it the first nav click inside
/uk pushes `/shop` and the reader lands on Singapore pricing. It is read from
`location.pathname`, not from the pin, so a page opened off-domain still routes
inside its own tree, and it is empty on the root and on /ae — those are
unchanged. `pathFor()` prefixes it; `refPath()` strips it, so a link written
`/shop` and one written `/uk/shop` resolve to the same route.

## Running it

    python3 build_uk.py <template-bundle>          # writes uk/*, adds en-gb hreflang
    python3 build_uk.py <template-bundle> --check  # report only

Then the normal chain: `build-ship.mjs`, then the FAQ chain for all three
markets (`build_faq.py … uk` is the third), then the two tests here:

    node market-pin.test.mjs <bundle>    # every page resolves to its own market
    node route-base.test.mjs <bundle>    # a nav click inside /uk stays in /uk

Both lift the shipped functions out of the built page and run them against
stubbed locations, so they test what was built rather than what was intended.
There is still no renderer in this environment: neither test says the page
*looks* right.

## Not done here

- `netlify.toml`, `sitemap.xml` and `llms.txt` are edited in the template
  bundle, not generated — the UK rows were added by hand on 6 Sep.
- Copy: the titles and descriptions are mirrored from the UAE wording. Alex has
  not read them.
