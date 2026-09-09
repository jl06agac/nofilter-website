# ⛔ PROTECTED ASSETS — DO NOT DELETE OR OVERWRITE WITHOUT ALEX'S EXPLICIT PERMISSION

**Standing order (Alex, 2026-07-07).** Every file listed below is protected. Claude must **never delete, overwrite, rename, move, or re-stamp over any of these without Alex's explicit, per-item say-so.** These were built or recovered by hand and have been lost once already to an unsupervised re-stamp — that must not happen again. If a build/stamp/graft would touch one of these, STOP and ask first.

If you need to change one, the rule is: **duplicate → change the copy → get Alex's sign-off → only then replace**, and keep the prior version as a dated backup. Never edit-in-place-and-hope.

---

## THE WEBSITE MASTER (added 2026-08-30)

**`NoFilter-Website-Master.html`** — the live public site's working file. Renamed on 30 Aug 2026
from `_OPTION-D.html`, which was its name during the four-way design bake-off (A cinematic /
B dossier / C instrument / D paper). D won and kept its audition name for six weeks, filed under
a leading underscore that means "not the real thing" in this workspace. It is the real thing.

- **UPDATED 4 Sep 2026.** This file had drifted three patches behind the live site. It was
  rebuilt from `nf-build-tools/base/NoFilter-Website-Master-2026-08-31.html` (formerly
  `PRISTINE.html`) plus the 96 patches in `build.sh`, which reproduce it byte for byte. It now
  carries a dated banner at the top. **The filename is deliberately undated** — 24 files name it,
  six of them live tooling — so the convention is: dated filename means an old snapshot, undated
  means live.
- **Do not hand-edit it.** Write a patch and re-run `nf-build-tools/build.sh`. Editing it directly
  puts it out of step with its own generator, which is how the 4 Sep drift happened.
- **This is where website changes are made.** It carries `data-nf-build`; every `SHIP-…` bundle
  built from it carries the same stamp, which is how the built output is tied back to its source.
- Slider colouring is correct as it stands (Alex, 30 Aug). The 20 `var(--ad)`/`var(--lf)` declarations removed that day were leftovers, not a missing feature — do not "restore" them.
- **It is the current source of truth for the impact slider and the quote console** (§12 QUOTE
  CONSOLE). The 6 Jul standalones below are its ancestors, not its equals — see the register.
- `_OPTION-D.PRE-RENAME-2026-08-30.html.bak` — **DELETED 4 Sep 2026.** It said "keep until Alex
  confirms nothing referenced the old name"; he confirmed, and a group test showed zero
  identifiers lost with it and the three other 30 Aug backups removed together.
- The losing options `_OPTION-A-cinematic.html`, `_OPTION-B-dossier.html`,
  `_OPTION-C-instrument.html`, `_OPTION-D-paper.html` are **already gone** — removed before
  4 Sep 2026. This line survived as an instruction to archive files that no longer exist; it is
  kept only as the record that D won the bake-off.

## THE IMPACT SLIDER — RESOLVED 4 SEP 2026, NOTHING TO PROTECT HERE ANY MORE

The three files this section used to protect are **gone**, deliberately, on Alex's instruction
that ancestors be deleted where an updated version exists:

| Deleted 4 Sep | Was |
|---|---|
| `nf-impact-standalone.html` (444 KB, 6 Jul) | the origin of the morph slider |
| `_test-impact-slider.html` (290 KB, 6 Jul) | an extract of that origin |
| `workplace-builder.html` (433 KB, 6 Jul) | the standalone quote builder origin |
| `workplace-builder.PRE-CANON-SLIDER.html` (404 KB) | its pre-graft backup |

**How that was proven safe.** Every identifier in each file — ids, classes, function names, CSS
selectors, keyframes, variables — was extracted and checked against every other `.html` and `.js`
in the workspace (281 files, 7,999 distinct identifiers). All four returned **zero** identifiers
found nowhere else. Narrowed to the slider itself, the origin held 74 identifiers of which 8 were
absent from the master, and all 8 turned out to be the *zoo* top-up variant, present in 19 to 51
client files including the Zoos template and every Part 2 pitch.

**The slider now lives in the website master and nowhere else.** To take a standalone copy, run
`_tools/nf-extract-component.mjs` against the master. Never hand-maintain a sibling: three
generations existed at once in August because someone did, and it went unnoticed for seven weeks.

Current extracts, stamped `nf-2026-09-04`:
`_components/nf-impact-slider-2026-09-04.generated.html` and
`_components/nf-quote-console-2026-09-04.generated.html`.

## THE CRT ACCESS SYSTEM (request access → code → CRT → builder)

- **`workplace-access.html`** — the standalone CRT access page (harvested UWCSEA CRT monitor; type the shared code → power-off → hands off to the builder).
- **`crt-gate-PROTOTYPE-2026-07-06.html`** — CRT gate prototype (renamed 4 Sep 2026).
- **`keystroke.mp3`** — the CRT keystroke sound (copied from `Clients/_shared/`).
- **`keystroke-audio.js`** — base64-inlined keystroke buffer so the CRT sound works on local `file://`.
- **`nofilter-counter.html`** — demo split-flap counter board used by the private-reveal tablet tile.
- **`workplace-page-SOURCE-2026-07-07.html`** (was `workplace.src.html`; the stamped `workplace.html` beside it was deleted 4 Sep) — the At Work page source: the request-access section that links to `workplace-access.html`. **Kept because it is the only copy of the workplace access gate** — `wpGate`, `wpGateForm`, `wpGateOpen`, `wpGateErr`, `wp-gate`, `wpConfig`, `wpConfigStart` — and the odometer animation `awOdo`/`awFlash`/`awHead`/`awScroll`. All 12 exist nowhere else on the machine.

## THE MANIFESTO + ORIGINS PAGE (moved off the homepage)

- **`../../DO-NOT-TOUCH-Claude-files/_partials/manifesto-holdtheline.html`** — the **single source of truth** for the "Most … coffee" morph headline + ethos body (orange "matters most"). Every page that shows this manifesto includes THIS partial; edit it here, never a copy. (Careful: a partial must never contain its own `[[INCLUDE:…]]` token, even in a comment — it recurses.)
- **`origins-page-SOURCE-2026-07-07.html`** (was `origins.src.html`) / `origins.html` — the Origins page: seam immersive → manifesto → origins (four forests) → the coffees → "verified, not claimed" proof → CTA. Built from the homepage sections.
- `index.src.PRE-ORIGINS.html` — **deleted 4 Sep 2026**, group-tested: zero identifiers lost. **`../../DO-NOT-TOUCH-Claude-files/_partials/nfbar.PRE-ORIGINS.html`** remains, a pre-split backup; keep until Alex confirms the Origins split is good.
- **`index-page-SOURCE-2026-07-07.html`** and **`machines-page-SOURCE-2026-07-06.html`** (were `index.src.html`, `machines.src.html`) — the last two of the 7 Jul page pipeline, kept because between them they hold `nominate` and `mx-step`, which exist nowhere else.

## PROTOTYPES / RECOVERED WORK (keep as record)

Renamed 4 Sep 2026. They were called `_test-*`, which read as scratch and invited deletion of
protected work. A dated name now says what each one is and when it is from — matching the
convention set the same day: **a date in the filename means an old snapshot; no date means live.**

Each was kept rather than deleted because each holds markup found in **no other file on the
machine**, checked against all 281 html/js files in the workspace:

- **`private-reveal-PROTOTYPE-2026-07-06.html`** (was `_test-private-reveal.html`) — the private "what runs behind the scenes" reveal (tablet counter, servicing self-scheduling, map, money tiles). Sole copy of `vgrid`, `q-mail--confirm`, `th-note`.
- **`manifesto-squeeze-PROTOTYPE-2026-07-06.html`** (was `_test-mani-squeeze.html`) — the "Most … coffee" squeeze + letter-cycle animation prototype. Sole copy of `th-scroller`, `th-bar`, `th-note`.
- **`gutter-slider-SUPERSEDED-2026-07-06.html`** (was `_test-gutter-slider.html`) — the recovered **gutter slider** (the earlier hover-side-message concept). Superseded by the morph slider, kept as the record of that approach. Sole copy of `ps-title`, `ps-eyebrow`, `ps-foot`, `ps-hint`, `th-note`.
- **`crt-gate-PROTOTYPE-2026-07-06.html`** (was `_test-crt-gate.html`) — CRT gate prototype. Sole copy of `relock`, `gate-builder`, `th-bar`.

## RECOVERED-SLIDER CANON SOURCES (elsewhere in the repo — also protected)

- `DO-NOT-TOUCH-Claude-files/_Part2-Master/_device-donor/NoFilter-Part2-MASTER-merged-WIP.html` — holds the recovered gutter slider (the newest, clamped version).
- `Clients/Schools/UWCSEA/partnership-deploy/AED-slider-ONLY.html` — the earlier gutter-slider build.

---

_Last updated 2026-08-30 (was 2026-07-07). If you add a new hand-built or recovered component, add it to this list._
