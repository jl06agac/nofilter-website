# NoFilter website — handoff to the next cowork session

Working file: `Marketing/NoFilter-Website/index.PREVIEW-htl-glitch.html`
(a PREVIEW copy — the real `index.html` is PROTECTED, do not touch it.)

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
- `NoFilter/_CDN-INCOMPLETE-DO-NOT-DEPLOY/` = an earlier partial folder — do not use.
- Still owed before deploy: Alex pasted only a PARTIAL live file list. Get the FULL Netlify
  deploy file list and diff it against `_CDN-UPLOAD-SAFE` to confirm 100% coverage.
- Claude does NOT deploy. Hand Alex the drag-drop steps. See `_CDN-COMPLETE-HOW-TO-DEPLOY.md`.

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
