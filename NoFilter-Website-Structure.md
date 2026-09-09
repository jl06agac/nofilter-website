# NoFilter — Website Structure & Build Plan

*Drafted 5 Jul 2026. The public site, assembled from what's already built. Principle: harvest the strong recent builds (the v256 Generic shell + configurator, the Part 1 content library, the three live tools) — do **not** revive `Marketing/NF-Site/` (old, retired).*

---

## The idea in one line

**Part 1's content sections + the Generic's shell/nav/logomark/configurator + the three tools as embeds + four small net-new blocks = one coherent public site**, all inheriting the Generic's design system so it reads as one thing.

## Where this sits in the funnel

The website is **Layer 1–2** of a four-layer funnel. The lower layers already exist and stay separate (private), but share the same brand shell:

| Layer | What | Source | Public? |
|---|---|---|---|
| 1 — Story | Marketing site (this doc) | Part 1 sections + Generic shell | Public |
| 2 — Convert | Self-serve configurator | Generic §04 `price` | Public |
| 3 — Sell | Personalised pitch, stamped per client | Part 2 master + skin pipeline | Private URL |
| 4 — Signed | Live impact register after signing | Part 2 signed mode + tools | Private/auth |

---

## Public site — information architecture

Long-scroll home with anchored sections + the configurator as a focus takeover (as it already behaves in Part 2). "Pulls from" = verified source file; **net-new** = build from scratch.

| # | Section | Pulls from | Embeds / assets | Status |
|---|---|---|---|---|
| — | **Shell** (nav bar, logomark animation, sticky header, footer/colophon) | Generic `cover` header + colophon | brand tokens, Big Shoulders | Harvest + wire nav |
| 1 | **Hero** — "HOLD THE LINE." | Generic `cover` | logomark animation | Harvest |
| 2 | **The Line (Why)** — conservation thesis | Part 1 `why` + Generic `why` | — | Harvest + merge |
| 3 | **Impact (live)** — cups → conservation raised | Part 1 `impact` + Generic `impactCounter` | **NF-Cup-Counter** (Shelly→Worker) | Harvest + embed |
| 4 | **Origins** — the four coffees + sourcing | Part 1 `origins` + Generic `recap` | **NF-GIS-Map** (`nofilter-gis-map.netlify.app`) | Harvest + embed |
| 5 | **The Coffees** — product / roast / tasting | Part 1 `coffees` | — | Harvest *(Q-grader values pending)* |
| 6 | **Verify** — Layer 01–04 transparency scaffold | Part 1 `verify` | **NF-GIS-Map** | Harvest — the differentiator |
| 7 | **How it works** — the 5% / 10% model | Part 1 `how` | — | Harvest |
| 8 | **At Work** — office proposition, machines, servicing | Part 1 `workplace` | **NF-Servicing-Scheduler** (`nofilter-servicing.netlify.app`) | Harvest + embed |
| 9 | **Build your quote** — the configurator | Generic `price` (§04) | Netlify lead form (17-field schema) | Harvest — conversion engine |
| 10 | **Clients / proof** — logo wall + testimonial | — | Accenture, UWCSEA, Tanglin, Dulwich, zoos | **Net-new** |
| 11 | **About** — who NoFilter is | — | — | **Net-new** |
| 12 | **Sign-off** — the emotional close | Generic `signoff-orangutan` video | — | Harvest |
| 13 | **Footer CTA** — "book a tasting / talk to us" + colophon | Generic colophon | per-market entity | Harvest + **net-new soft CTA** |

---

## Design system (the glue)

Everything inherits from the Generic build so the harvested Part 1 sections don't look stitched on:

- **Type:** Big Shoulders Display (hero/display). *Flag: `--font-d` still leads with unlicensed "Tiempos Headline" → license or drop before launch.*
- **Colour:** the impact-trilogy semantics — amber = built-in share, orange = user top-up, white = totals. Plus the `#F27126` vs `#EE4D17` orange to resolve.
- **Motion:** logomark animation + the morph unified slider language.
- **Media:** everything references `nofilter-shared.netlify.app` by absolute URL — one bucket, never duplicated.

## Net-new work (the only from-scratch pieces)

1. **Client / social-proof wall** — logos + 1–2 testimonials.
2. **About / story** — short founder/why block.
3. **Soft CTA** — a low-commitment path beside the configurator (book a tasting / contact).
4. **Site chrome** — shared nav wiring + footer with per-market entity (SG / UAE / UK), legal/privacy.

---

## Build order

- **Phase 0 — Shell.** Extract nav + logomark + footer + brand tokens from the Generic into a reusable shell. Decide the deploy target/domain (consolidate the `nofilter-*.netlify.app` sprawl).
  - **Harden the HTL hero for web** (the `hero-holdtheline` shared partial). It's a keeper — RGB-split video glitch + `steps(2,end)` "materialise" cascade of HOLD / THE / LINE (~1.5s), reduced-motion guarded. Four web-readiness changes as it moves from one-shot pitch to revisited site: (1) **first-visit gate** — flag in `localStorage`, return visitors land on the resolved hero, no re-glitch; (2) **LCP** — poster-frame first paint + lazy-load the three layered `hero.mp4` copies so the glitch never reads as a blank delay on mobile/slow connections; (3) **reduced-motion** — confirm the accommodation stills the *video* RGB-split too, not just the title cascade (photosensitivity); (4) **de-zoo** — scrub the inherited `az-cover` / `az-cobrand` / `az-logo` structure + animation so nothing zoo-specific leaks into the generic hero.
- **Phase 1 — Assemble the story.** Port Part 1 sections into the shell in scroll order: Hero → Why → Impact → Origins → Coffees → Verify → How → At Work → Sign-off → Footer.
- **Phase 2 — Wire conversion.** Drop the configurator in as the "Build your quote" focus mode; connect the Netlify lead form.
- **Phase 3 — Net-new blocks.** Clients wall, About, soft CTA.
- **Phase 4 — Market tokenise & deploy.** Light-tokenise currency / country / tax for SG / UAE / UK via the stamp pipeline (`_tools/nf-stamp.mjs`); deploy.
- **Phase 5 — Connect lower funnel (later).** Link the personalised pitch + signed portal behind the same brand shell.

## Open decisions

1. **Domain / deploy** — one consolidated site, or keep tools on their own subdomains and iframe them in?
2. **Single-page vs multi-page** — long-scroll home (assumed here) vs breaking Coffees/Origins/Verify into their own routes.
3. **Client-layer visibility** — do Layers 3–4 share the public nav, or sit fully behind auth?

## Dependencies carried from the Part 2 backlog

- Q-grader confirmation of the four origins' acidity/body/roast values (feeds §5 Coffees).
- Gayo Lues real sourcing coordinate — still placeholder (feeds §4 Origins / GIS map).
- Batang Toru coordinate correction already done (1°38′18″N · 99°15′56″E) — verify the GIS map carries it.
- Font licensing + orange-hex resolution before public launch.

## Housekeeping note

**Reconciled 7 Aug 2026. This note previously said the opposite and was wrong.**

The canonical Generic build is the in-repo one:

    Clients/Generic/NoFilter-Generic-Part2-SG.html   473,065 bytes / 8 Jul 2026

`Clients/Generic/_live/index.html` is a hard link to it (same inode), so what is deployed is this file.

The Desktop copy the old note called canonical (443,870 bytes / 5 Jul 2026) predates the 7-8 Jul work recorded in the `PRE-SHOP-GRAFT` / `PRE-DOSSIER-GRAFT` / `PRE-FOOTER` / `PRE-PRICING` backups sitting beside the canonical file. It is archived at `Clients/Generic/_archive/NoFilter-Generic-Part2-SG.SUPERSEDED-desktop-copy-2026-07-05.html`. Nothing was deleted.

Both files labelled themselves `v256`, which is why the confusion survived three weeks. The version string inside the file is not a reliable identifier. The path is.
