# Shop checkout: hand-over for review

Branch `shop-checkout` (commits 139 to 144). Built by Claude; for Codex to review before anything merges.
Nothing here is on `main` or on nofilter.sg. `SHOP_LIVE` is still `false` in the master.

## What it does

1. **Basket** (cart drawer in `NoFilter-Website-Master.html`): bag photo per line, quantity stepper, a muted
   looping film of the landscape most of the basket comes from (captioned with its partner), subtotal, the 10%
   to conservation, and the split by partner when there are two or more coffees. A client code arriving as
   `?code=` (the impact counter's shop QR) is kept and shown.
2. **Checkout**: the page posts names, sizes and quantities only to `netlify/functions/checkout.js`, which
   sets prices, refuses anything off its list, and creates a Stripe **embedded** Checkout Session. The Stripe
   form is mounted inside our own panel (`openPay`), beside the film and three projects the customer can point
   their 10% at (same three as the counter). A choice is written to the open session (`action: 'choose'`).
3. **Order confirmation page** (148): Stripe returns to `/shop/?paid=1&order=cs_…`; a full page (not a pop-up)
   thanks the customer by first name, says we roast every Wednesday and dispatch shortly after, shows the
   order number (`NF-XXXXXX`, set in `checkout.js` on the order and its payment), bags, discount, total paid,
   delivery address, card brand and last four, where the confirmation was emailed, the conservation share by
   partner and the chosen project, and hello@nofilter.sg for help. Data from `order-summary.js`.
4. **What each NGO is owed**: `shop-ngo-report.js` (GET, `x-report-key` header) totals 10% of each paid
   line's amount after discounts, by origin and partner, and by choice, for a date range. Stripe is the record;
   nothing is stored. Refunded orders are listed, not netted off.
5. **Draft preview** (commit 142): on draft links only (`…--nofilter-site.netlify.app`, `localhost`,
   `127.0.0.1`) a 503 from checkout (no Stripe key) opens the same panel with a labelled stand-in form and a
   "Pay (preview)" button that goes to the thank-you with figures computed from the cart. nofilter.sg and
   `nofilter-site.netlify.app` never match the pattern and keep the plain "Checkout is not open yet" message.

## Files

- `NoFilter-Website-Master.html`: cart markup and CSS, `renderCart`, checkout handler, `openPay`,
  `paidPanel` (blocks numbered 139 to 144)
- `nf-build-tools/ship/SHIP-2026-08-30f/netlify/functions/checkout.js`, `order-summary.js`, `shop-ngo-report.js`
- `nf-build-tools/ship/SHIP-2026-08-30f/assets/shop/*.webp` (the three project images)
- `nf-build-tools/ship/tests/shop-functions.test.cjs` (8 tests)

## How it was checked

- `node --test nf-build-tools/ship/tests/shop-functions.test.cjs`: 8 pass
- Playwright, 1440 px and iPhone 13: full journey with a stubbed Stripe.js (real path) and with a 503
  (preview path); no page errors; screens reviewed for layout at both sizes
- Preview pattern tested against `nofilter.sg` (no), `nofilter-site.netlify.app` (no), a draft host (yes)

## Please look hard at

1. **Price and cart integrity**: can the page influence an amount? (`cleanLines`, env prices, 20-bag cap)
2. **`action: 'choose'`**: only open, shop-created sessions; choice whitelisted. Anyone holding a session id
   could change the choice; the id is only in the payer's browser. Acceptable?
3. **`order-summary.js`**: paid shop orders only. It now returns the email, first name, delivery address and
   card last four for the confirmation page (as Stripe's return-page guidance does; the session id is long,
   random and only in the payer's browser). Confirm it never returns the phone, billing address or other card details
4. **Report**: timing-safe key check; pagination; `amount_total` per line is after discounts; refunds listed
5. **Preview path**: confirm it can never run on production, and that the preview figures (cart prices, before
   any discount) are not mistaken for real ones anywhere
6. **Partner data**: Batang Toru was "PRCF Indonesia, SRI" in the site's coffee record; corrected to
   "PRCF Indonesia, OIC" (matches the site's own fact box and Alex). Only the shop reads that field.
7. **Accessibility**: dialog roles, focus on open, Escape to close, reduced motion on the count-up

8. **Site headers** (`netlify.toml`, 151): `payment=()` became `payment=(self js.stripe.com checkout.stripe.com
   pay.google.com)` so wallets work in Stripe's frame, and the opener policy became `same-origin-allow-popups` for
   payment methods that confirm in a pop-up. Site-wide; check nothing else relied on the stricter values.
9. **Stripe API change**: embedded checkout is now `ui_mode: embedded_page`, mounted with
   `createEmbeddedCheckoutPage` from `js.stripe.com/endive/stripe.js` (falls back to `initEmbeddedCheckout`).

10. **Subscriptions** (152): Subscribe & save 10% on each coffee page (a widget beside the picker, shared
   choice `window.__nfPlan`, armed only by the coffee page's Add button) and a switch on each basket line.
   Every 1-4 weeks; one frequency per basket (Stripe's rule). `checkout.js` switches to `mode: subscription`
   with weekly recurring price_data at 10% off; one-off lines ride along. With a client code: the better of the
   two, applied to the prices (a Stripe code would apply to every future delivery). `order-summary.js` returns the
   subscription (frequency, next charge), a running total of the customer's paid orders and renewals, opens
   Stripe's customer portal (`&manage=1`, needs the portal saved once in the Stripe dashboard) and records
   report-back / news consent on the Stripe customer (POST). The NGO report counts renewal invoices
   (`billing_reason: subscription_cycle`). Terms page: `/subscription-terms/` (draft for Alex to approve).

11. **Swap, skip, change** (153): the range lives in Stripe as real Products (one per coffee and size, with
   origin and partner) and weekly Prices (every 1-4 weeks, 10% off, by lookup key), created on first use by
   `_lib/catalogue.js`. Subscription lines use them, so the order page can swap coffee, size or quantity
   (`proration_behavior: none`, from the next delivery), change frequency (`trial_end` = end of the paid
   period, so no charge today) and skip the next delivery (`pause_collection: void` until just after it).
   Card, address, invoices and cancel (at period end) are Stripe's portal, with its own configuration
   (`metadata.nf = shop-v1`). The portal can't swap: it only updates single-item subscriptions.
   Worth checking: `trial_end` shows the subscription as trialing until then; skip on a past_due subscription.

## Known gaps (not bugs)

- Retail ships within Singapore only; other markets get a message instead of checkout.
- Refunds are not netted off in the report; they are listed for manual exclusion.
- The choice can only be made in the checkout panel, not after paying.

## Before launch (for Alex)

1. Create the Stripe account (NoFilter Pte. Ltd.), then in Netlify, site `nofilter-site`, Environment
   variables: `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` (test keys first, `sk_test_` / `pk_test_`),
   and `REPORT_KEY` (any long random phrase; it unlocks the NGO report).
2. In Stripe: switch on Apple Pay, Google Pay, PayNow and Link (Settings, Payment methods); switch on
   receipts (Settings, Emails, Successful payments); verify the Apple Pay
   domain `nofilter.sg`; Branding: background `#F4F2EE` (the shop's cream), accent `#EE4D17`, corners rounded, logo.
3. Create the client promotion codes (10% off, e.g. `SPRINKLR10`, `EASTSPRING10`).
4. Rehearse with test card 4242 4242 4242 4242 on a draft; then swap to live keys.
5. Decide: does Arakan stay in the shop while Myanmar is phased out?
6. Launch = merge this branch, flip `SHOP_LIVE` to `true`, build the bundle, deploy from the Mac.
