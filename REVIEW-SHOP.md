# Shop checkout: hand-over for review (pre-launch)

Branch `shop-checkout` (commits 139 to 160). Built by Claude; for Codex to review before anything merges.
Nothing here is on `main` or on nofilter.sg. In the master, `SHOP_LIVE` is `{ SG: false, AE: false, UK: false }`;
launch flips `SG` to `true` only. Alex has asked to launch Singapore once this review is done, with the UAE and UK
held as "coming soon".

This file replaces the earlier version, which described the embedded Stripe form and the project picker. Both
are gone.

## Codex review of `59ee89f`: fixes in 161

1. **Codes on subscriptions** (`checkout.js`, `subscriptionCodeOk`): a code is built into subscription prices only
   if it is meant to last: percentage, duration `forever`, valid, active, no customer, no first-order or
   minimum-spend rule, not expired, redemptions not used up. Otherwise the subscription stays at 5% and the code
   is not reported as applied. One-off orders still pass the code to Stripe, which enforces its own rules.
   Known limit: a code built into prices is not counted in Stripe's `times_redeemed`, so redemption caps only
   bite on one-off orders. Workplace codes for subscribers must be created as `forever` codes.
2. **Renewal contributions after discounts** (`shop-ngo-report.js`): each invoice line's `discount_amounts` are
   subtracted before the 10%.
3. **Partial swaps** (`order-summary.js`): a swap must list every coffee in the subscription exactly once; a
   partial or duplicated list gets 409 ("subscription changed; reload the page"). The page always sends every row.
4. **Long invoices** (`shop-ngo-report.js`): when the embedded `lines` list has more, all lines are paged through
   `invoices/{id}/lines`.
5. **20 bags an order** (`checkout.js` `MAX_BAGS`, basket stepper, checkout button): across the whole order, not
   per line. The basket's + stops at 20 in total; checkout says "Up to 20 bags an order. For more, write to
   hello@nofilter.sg."
6. **Checkout focus**: focus moves to the panel's Close on open, Tab and Shift+Tab stay inside, Escape or Close
   returns focus to the basket button.

Tests: 17 pass (new: code eligibility and its effect on the session, the 20-bag order cap, discounted and
multi-page renewal invoices, partial and duplicate swaps). Browser: focus trap and the basket cap at 1440 px and
iPhone 13. Still not exercised against live Stripe test mode: a discounted renewal invoice and a swap; to do
before launch.

## Codex re-review of `7b66f30`: fix in 164

- **Restricted codes on subscriptions**: `subscriptionCodeOk(promo, coupon)` now also rejects any redemption cap
  (on the code or the coupon, used or not) and any product restriction (`applies_to.products`).
- **Found while fixing it**: the code lookup asked Stripe for `expand[]=data.coupon`. On Stripe's current API a
  promotion code holds its coupon as an ID under `promotion.coupon`, so on an account on that version the
  lookup would fail and a `?code=` from the counter QR would be dropped silently. The lookup now has no expand;
  for a subscription the coupon is fetched separately (`coupons/{id}?expand[]=applies_to`), which works on old
  and new versions.
- Tests 19 pass, including Codex's two reproductions.

## Trade access and quote (162, 163), checked on draft 6af089ce

- `/api/access-verify` answers (405 to a GET); `/.netlify/functions/access-verify` and `access-request` are 404;
  rapid POSTs got 429 from Netlify after about 13, so the rate-limit rule is accepted on this plan.
- On drafts the access functions answer 503 (no `RESEND_API_KEY` / `ACCESS_SECRET` in the deploy-preview
  context); unchanged from before.

## What it does now

1. **Shop and coffee pages**: 250 g SGD 24, 1 kg SGD 75 (`MARKETS.SG.bag250/bag1kg`; the functions' defaults
   `PRICE_BAG_250G` 2400, `PRICE_BAG_1KG` 7500). Each coffee page has a Subscribe & save 5% widget (one-time or
   subscribe, every 1 to 4 weeks), shared via `window.__nfPlan`, armed only by that page's Add button.
2. **Basket** (`renderCart`): per-line One-time / Subscribe −5% switch, frequency chips (one frequency per basket,
   Stripe's rule), delivery line (SGD 4 under SGD 50, free from SGD 50) with a free-delivery nudge, the 10% to
   conservation and split by partner, landscape film. A client code arriving as `?code=` is kept.
3. **Checkout panel** (`openPay`): left, the landscape film, "SGD X to conservation", one sentence on the 10%,
   and each landscape's partner and share. No project picker (removed 158 until partners' projects are
   confirmed; `checkout.js` still accepts and whitelists `choice`, the page sends `''`). Right, the live order
   summary (per-line switch, frequency, delivery, first payment, "Then SGD X every N weeks"). "Continue to secure
   payment" POSTs `{lines, code, choice}` to `checkout.js` and redirects to Stripe's hosted page. Payment note:
   card, Apple Pay or Google Pay for subscriptions; adds PayNow and GrabPay for one-off orders.
4. **`checkout.js`**: prices set server-side (page sends names, sizes, quantities, frequency only), 20-bag cap,
   unknown items refused. One-off: `mode: payment`, shipping rate on the full-price subtotal. Any subscribed
   line: `mode: subscription` with catalogue Prices (`_lib/catalogue.js`, lookup key
   `nf-sub-{origin}-{size}-w{n}-p{pct}`, created on first use) at `max(5%, client code %)`, never both; one-off
   lines ride along; a recurring Delivery line when a delivery's coffee is under SGD 50. Order number
   `NF-XXXXXX` on the session and payment. Stripe error detail masked from the page.
5. **Order confirmation** (`paidPanel`, `/shop/?paid=1&order=cs_…`): thanks by first name, roast Wednesday and
   dispatch shortly after, order card, delivery address, card brand and last four, where the receipt went,
   running total to conservation by partner, stay-in-touch tick boxes (stored on the Stripe customer).
   Subscriptions: swap coffee or size, quantity, change frequency (from the end of the paid period, via
   `trial_end`), skip the next delivery (`pause_collection: void`), and "Card, address or cancel" (Stripe
   portal, config `metadata.nf = shop-v1`, cancel at period end). Data from `order-summary.js`.
6. **What each NGO is owed**: `shop-ngo-report.js` (GET, `x-report-key`), 10% of each paid line after discounts,
   by origin and partner, including renewal invoices; delivery lines excluded; refunds listed, not netted.
7. **Markets** (160): the shop switch is per market and follows the price-board toggle live. In a market that is
   off, Add opens the "Coming soon to the UAE / the UK" card (dispatch list sign-up) and nothing reaches the
   cart (`__nfCartSet` wrapped). Checkout refuses any market but SG (`MKTK !== 'SG'`).
8. **Draft preview**: on draft hosts only (`…--nofilter-site.netlify.app`, localhost), a 503 from checkout opens
   a stand-in that lands on the confirmation page with figures from the cart. Never on nofilter.sg.
9. **Terms**: `/subscription-terms/` (standalone, noindex), linked from Stripe's page via `custom_text`.

## Files

- `NoFilter-Website-Master.html`: basket, coffee-page widget, `openPay`, `paidPanel`, the pre-launch switch
- `nf-build-tools/ship/SHIP-2026-08-30f/netlify/functions/checkout.js`, `order-summary.js`, `shop-ngo-report.js`,
  `_lib/catalogue.js`
- `nf-build-tools/ship/SHIP-2026-08-30f/subscription-terms/index.html` (exempted in `build-ship.mjs`,
  `split-bundle.py`, `wire_links.py`)
- `nf-build-tools/ship/tests/shop-functions.test.cjs` (14 tests)

## How it was checked

- Unit tests: 14 pass
- Playwright at 1440 px and iPhone 13: basket, subscription widget, checkout panel to a stubbed Stripe redirect,
  the 503 preview path to the confirmation page, the confirmation page's subscription controls, and the market
  switch (SG buys; AE and UK get the coming-soon card, cart untouched; all-off shows coming soon everywhere).
  No page errors.
- Live Stripe test mode on drafts: hosted checkout and a subscription payment went through. Swap, skip and
  frequency change are covered by unit tests against a mocked Stripe; worth one live run before launch.

## Please look hard at

1. **Price integrity**: can the page influence any amount, discount level, delivery or frequency beyond the
   whitelist? (`cleanLines`, env prices, `subOff`, the Delivery line)
2. **Subscription changes** (`order-summary.js` POST): only the subscription belonging to that paid session;
   swap keeps the discount tier; delivery added or dropped correctly across the SGD 50 line; skip on a past_due
   subscription; `trial_end` shows the subscription as trialing.
3. **Personal data**: `order-summary.js` returns first name, email, delivery address and card last four for the
   session holder. Confirm nothing else (phone, billing address, other card details).
4. **Report**: timing-safe key check, pagination, renewals counted once, delivery excluded.
5. **Market switch**: no route into a paid order outside SG (cart model, checkout guard, server: `checkout.js`
   is SGD-only).
6. **Preview path** can never run on production.
7. **Accessibility**: dialog roles, focus on open, Escape, reduced motion.

## Known gaps (not bugs)

- Refunds are not netted off in the report.
- No order notification to NoFilter and no weekly roast list yet (Stripe dashboard is the record until then).
- Customers can't pick a project for their 10% until partners' projects are confirmed.

## Launch steps (after review)

1. Alex runs "Set Stripe test keys.command" with **live** keys (the script needs its `sk_test_` check changed to
   accept `sk_live_`; Claude does that on request). Claude never handles the keys.
2. In Stripe (live mode): receipts on (Settings, Emails, Successful payments); Branding background `#F4F2EE`,
   accent `#EE4D17`; Apple Pay domain `nofilter.sg`; client promotion codes if wanted.
3. One real low-value order on a draft with live keys, then refund it.
4. Merge `shop-checkout` to `main`, flip `SG` to `true`, build, deploy production from the Mac (Alex says go).
5. Decisions still open with Alex: Arakan in the shop or not; terms wording; roast cut-off; courier cost per
   parcel against the SGD 4 charge.
