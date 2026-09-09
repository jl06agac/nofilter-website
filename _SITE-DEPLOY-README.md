# The website deploy target — read this before dragging anything

**Written 30 Aug 2026 after Claude told Alex to drop the website build on `nofilter-shared`.
That is the media CDN. A Netlify drop replaces the entire site, so following that instruction
would have destroyed 203 files / 233 MB of shared assets that every client pitch and every
video on the live site loads by absolute URL. Alex caught it. It is written down here because
the information existed and was still got wrong.**

---

## There are two different Netlify sites. They are not interchangeable.

| | site | domain | what you drop on it | source folder |
|---|---|---|---|---|
| **The website** | **`nofilter-site`** | **nofilter.sg** / nofilter.ae | the built site — 44 files, ~13 MB | `Marketing/NoFilter-Website/SHIP-YYYY-MM-DD<letter>/` |
| The media CDN | `nofilter-shared` | nofilter-shared.netlify.app | the whole asset library — 203 files, ~233 MB | `NoFilter/_CDN-UPLOAD-SAFE/` |

- Website admin: `https://app.netlify.com/projects/nofilter-site`
- CDN siteId: `7e2274d8-fa6c-44b9-9af6-779cc0e89ad0`

Deploying the site does **not** require touching the CDN. The two only ever move together if
a change adds or replaces an asset — and asset work is additive, never a replacement
(see `CDN-DEPLOY-README.md`).

## How the website deploys

Netlify Drop. `app.netlify.com/projects/nofilter-site` -> Project overview -> "Drag and drop
your project folder here to deploy new changes". Drag the `SHIP-...` **folder itself**, not
its contents.

A healthy deploy reports roughly: 18 generated pages changed, 126 redirect rules,
11 header rules, 4 functions. If the function count is 0, `netlify/functions/` did not make it
into the folder and the quote form is dead on arrival.

## The rule that makes both of these safe

Netlify drag-and-drop **replaces the whole site**. Whatever you drop is the site; anything not
in it is gone. So the folder must always be a complete superset, never a subset — and it must
be the superset for the *right* site. Check the project name in the Netlify header before you
let go of the folder.


## Stamp the bundle before you drop it (added 30 Aug 2026)

    node ../../DO-NOT-TOUCH-Claude-files/_tools/nf-ship-stamp.mjs SHIP-2026-08-30f

Every SHIP bundle from the 29th and 30th carried `data-nf-build="nf-2026-08-28"` — the stamp of
the SOURCE file, identical across all of them — and 30d, 30e and 30f had no visible text
differences at all. So "which version is live?" could not be answered without a Netlify login.

The stamper writes the folder's own name into all 19 pages and into `llms.txt`. After that:

    curl -s https://nofilter.sg | grep nf-ship

answers it from any machine, with no login. Run it on the folder immediately before dragging.
