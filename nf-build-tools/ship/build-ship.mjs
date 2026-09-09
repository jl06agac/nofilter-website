#!/usr/bin/env node
// build-ship.mjs — turn NoFilter-Website-Master.html into a SHIP bundle.
//
//   node build-ship.mjs <master.html> <template SHIP folder> <out SHIP folder>
//
// The previous builder (tools/build.js, 29-30 Aug) is not on disk, so this one
// reconstructs its output from evidence rather than memory:
//   · index.html = master, HTML/JS/CSS comments stripped, whitespace collapsed
//     conservatively, every ../../_CDN-UPLOAD-SAFE/ and bare media reference
//     rewritten to https://nofilter-shared.netlify.app/.
//   · every other page = index.html with the SAME edits the template bundle
//     applied to its copy of that page (title, description, canonical, og,
//     hreflang, which <section class="route"> is "on", an origin's open
//     drawer). Those edits are read off the template by token diff and
//     transplanted; each must land exactly once or the build stops.
//   · everything that is not an HTML page (fonts, functions, toml, robots,
//     favicon, og-card, 404) is copied from the template untouched.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync, copyFileSync, existsSync } from 'node:fs';
import { basename, join, relative, dirname } from 'node:path';
import { minify } from 'html-minifier-terser';
import { purgeDocument } from './purge-css.mjs';

const [,, MASTER, TPL, OUT] = process.argv;
if (!MASTER || !TPL || !OUT) { console.error('usage: build-ship.mjs <master> <template SHIP> <out SHIP>'); process.exit(2); }

const CDN = 'https://nofilter-shared.netlify.app/';
let src = readFileSync(MASTER, 'utf8');

// ── 1 · asset references ──────────────────────────────────────────────────
src = src.split('../../_CDN-UPLOAD-SAFE/').join(CDN);
// bare media names the master keeps relative so it can be viewed beside them
const bare = new Set(src.match(/(?:src|data-src|poster|href)="([A-Za-z0-9_\-]+\.(?:mp4|webm|jpg|jpeg|png|webp|svg|mp3))"/g) || []);
for (const m of bare) {
  const name = m.slice(m.indexOf('"') + 1, -1);
  src = src.split(m).join(m.replace(name, CDN + name));
}
console.log('bare media rewritten:', [...bare].map(m => m.split('"')[1]).join(', ') || 'none');

// ── 1b · the ladder leaves the document (block 114, 7 Sep) ────────────────
// The master declares RATES {SG,AE,UK: kg, bands, mach, cover, buyx} beside
// MARKETS and merges it back in at load, so the file behaves unsplit on disk.
// The SHIPPED pages carry neither the literal nor the inline merge; the literal
// is written into netlify/functions/access-verify.js (step 4b), which returns
// it with a valid access code. Every check here is fatal on purpose: a page
// that still carries the ladder, or a function that has nothing to return,
// must not become a bundle.
function balanced(str, from) {           // index just past the {...} starting at `from`
  let d = 0, q = null;
  for (let i = from; i < str.length; i++) {
    const c = str[i];
    if (q) { if (c === '\\') { i++; continue; } if (c === q) q = null; continue; }
    if (c === '"' || c === "'" || c === '`') { q = c; continue; }
    if (c === '{') d++;
    else if (c === '}') { d--; if (d === 0) return i + 1; }
  }
  throw new Error('unbalanced literal');
}
const ratesHead = src.match(/\nvar RATES = \{/);
if (!ratesHead) { console.error('RATES literal not found in the master (patch_ratesplit not applied?)'); process.exit(1); }
const rStart = src.indexOf('{', ratesHead.index);
const rEnd = balanced(src, rStart);
const ratesLiteral = src.slice(rStart, rEnd);
let RATES;
try { RATES = new Function('return (' + ratesLiteral + ')')(); } catch (e) { console.error('RATES literal does not evaluate:', e.message); process.exit(1); }
for (const k of ['SG', 'AE', 'UK']) for (const g of ['kg', 'bands', 'mach', 'cover', 'buyx'])
  if (!RATES[k] || RATES[k][g] === undefined) { console.error(`RATES.${k}.${g} missing`); process.exit(1); }
// remove "var RATES = {...};" (the statement, incl. its trailing semicolon)
let cutEnd = rEnd; if (src[cutEnd] === ';') cutEnd++;
src = src.slice(0, ratesHead.index + 1) + '/* 114: RATES lifted out by build-ship; served by access-verify on a valid code */' + src.slice(cutEnd);
// remove the inline merge the master runs when unsplit
const mergeLine = /\n[^\n]*NF_MERGE_INLINE[^\n]*/;
if (!mergeLine.test(src)) { console.error('NF_MERGE_INLINE line not found'); process.exit(1); }
src = src.replace(mergeLine, '\n/* 114: inline merge removed by build-ship; the ladder arrives with the access answer */');
// nothing of the ladder may survive in the page text
// (ref:{kg,floor,rate} stays public by design — the gate's readout shows the floor)
for (const probe of [/\bceil\s*:\s*\d/, /\bfull\s*:\s*\d/, /\br24\s*:\s*[1-9]/, /\br36\s*:\s*[1-9]/, /\bbands\s*:\s*\[\s*\{\s*id/, /\bcalloutHr\s*:/])
  if (probe.test(src)) { console.error('ladder figure survived in the page source:', probe); process.exit(1); }
console.log(`RATES lifted: ${ratesLiteral.length} chars, ${Object.keys(RATES).join('/')}`);

// ── 2 · minify ────────────────────────────────────────────────────────────
const minified = await minify(src, {
  collapseWhitespace: true,
  conservativeCollapse: true,
  removeComments: true,
  minifyCSS: true,
  minifyJS: { compress: false, mangle: false, format: { comments: false } },
  keepClosingSlash: true,
  processConditionalComments: false,
  continueOnParseError: false,
});
let index = minified;
console.log(`index: ${src.length} -> ${index.length} bytes (minified, fonts still embedded)`);
if (index.includes('_CDN-UPLOAD-SAFE')) { console.error('a _CDN-UPLOAD-SAFE reference survived minification'); process.exit(1); }

// ── 2b · fonts: the master embeds thirteen faces as base64; the bundle
//         serves them from /assets/fonts (29 Aug: first paint 3440ms → 1608ms).
//         Each embedded rule is swapped for the template's file-backed rule of
//         the same family/style/weight. ──────────────────────────────────────
const tplIndex = readFileSync(join(TPL, 'index.html'), 'utf8');
// The family is quoted only when it has a space: minified CSS writes
// font-family:Archivo but font-family:'IBM Plex Mono'. The 2 Sep bundle's
// matcher took only the quoted form, so every Archivo weight fell through to
// one rule (the 700 file) and all body text shipped bold. Both forms now.
const faceKey = r => {
  const m = r.match(/font-family:(?:'([^']+)'|([^;']+));font-style:(\w+);font-weight:(\d+)/);
  if (!m) { console.error('unreadable @font-face:', r.slice(0, 120)); process.exit(1); }
  return `${m[1] || m[2]}|${m[3]}|${m[4]}`;
};
const tplFaces = new Map();
for (const r of tplIndex.match(/@font-face\{[^}]*\}/g) || []) if (r.includes('/assets/fonts/')) {
  const k = faceKey(r);
  if (tplFaces.has(k)) { console.error('template declares face twice:', k); process.exit(1); }
  tplFaces.set(k, r);
}
let swapped = 0; const used = new Set();
index = index.replace(/@font-face\{[^}]*\}/g, r => {
  if (!r.includes('data:font')) return r;
  const k = faceKey(r), t = tplFaces.get(k);
  if (!t) { console.error('no file-backed rule for embedded face', k); process.exit(1); }
  if (used.has(k)) { console.error('embedded face declared twice:', k); process.exit(1); }
  used.add(k); swapped++; return t;
});
console.log(`fonts: ${swapped} embedded faces swapped for /assets/fonts files (${tplFaces.size} available)`);
if (swapped !== 13 || used.size !== 13 || tplFaces.size !== 13) { console.error('expected 13 distinct faces, one file each'); process.exit(1); }
for (const k of tplFaces.keys()) if (!used.has(k)) { console.error('template face never used:', k); process.exit(1); }
// the built page must carry exactly the template's thirteen file-backed rules
const builtFaces = (index.match(/@font-face\{[^}]*\}/g) || []).filter(r => r.includes('/assets/fonts/')).sort();
const tplFaceList = [...tplFaces.values()].sort();
if (JSON.stringify(builtFaces) !== JSON.stringify(tplFaceList)) { console.error('font-face rules differ from template'); process.exit(1); }
// ── 2b' · font-display (3 Sep, block 92): PageSpeed on 02d flagged "font
//          display — est. savings 340 ms". Every face was `block`, so all text
//          waited invisible for its file. The text faces now `swap` (they are
//          preloaded, so the fallback is rarely seen); Big Shoulders keeps
//          `block` — a swap on the hero title would be a visible re-set. ─────
{
  let n = 0;
  index = index.replace(/@font-face\{[^}]*\}/g, r => {
    if (!r.includes('/assets/fonts/') || r.includes('Big Shoulders')) return r;
    n++; return r.replace('font-display:block', 'font-display:swap');
  });
  if (n !== 10) { console.error('expected 10 text faces to swap, got', n); process.exit(1); }
  console.log('font-display: swap on 10 text faces, block on the 3 display faces');
}

// ── 2c · the SEO head: title, description, canonical, og, twitter, JSON-LD,
//         preloads — the old builder generated these from ROUTE_META; the
//         template carries the result, so it is grafted verbatim from
//         <meta charset> up to the font stylesheet. ─────────────────────────
const cut = (s, a, b) => [s.indexOf(a), s.indexOf(b)];
const [na, nb] = cut(index, '<meta charset="utf-8">', '<style');
const [ta, tb] = cut(tplIndex, '<meta charset="utf-8">', '<style id="nf-fonts">');
if (na < 0 || nb < 0 || ta < 0 || tb < 0) { console.error('head anchors missing', na, nb, ta, tb); process.exit(1); }
index = index.slice(0, na) + tplIndex.slice(ta, tb) + index.slice(nb);
// the bundle name, so the live site can say which build it is
// (curl -s https://nofilter.sg | grep -o 'nf-ship" content="[^"]*"'); the
// template's own stamp sits before <meta charset> and is not grafted
index = index.replace('<meta charset="utf-8">', `<meta charset="utf-8"><meta name="nf-ship" content="${OUT.replace(/\/+$/, '').split('/').pop()}">`);
// the home route is pre-rendered "on" so the page has content before JS runs;
// each route page then moves the "on" to its own section (transplanted below)
if (index.split('<section class="route" id="home"').length !== 2) { console.error('home route tag not unique'); process.exit(1); }
index = index.replace('<section class="route" id="home"', '<section class="route on" id="home"');
// the origin drawers carry data-o="slug" in the bundle (the origin pages open
// one of them pre-rendered); the master's drawers do not, so they are added
for (const tag of tplIndex.match(/<div class="fbh-drawer" id="[^"]+" data-o="[^"]+" hidden>/g) || []) {
  if (index.includes(tag)) continue;                       // the master carries data-o itself (block 88)
  const bare = tag.replace(/ data-o="[^"]+"/, '');
  if (index.split(bare).length !== 2) { console.error('drawer tag not unique:', bare); process.exit(1); }
  index = index.replace(bare, tag);
}
// the keystroke audio script ships under /assets (the master keeps it beside
// itself); since block 89 the gate loads it by name from a script string
index = index.replace('<script src="keystroke-audio.js"></script>', '<script src="/assets/keystroke-audio.js"></script>');
index = index.split("'keystroke-audio.js'").join("'/assets/keystroke-audio.js'").split('"keystroke-audio.js"').join('"/assets/keystroke-audio.js"');
if (!index.includes('/assets/keystroke-audio.js')) { console.error('keystroke-audio.js reference not found'); process.exit(1); }
// ── 2d · dead CSS: a rule naming a class or id that appears nowhere in the
//         page outside its styles cannot match; see purge-css.mjs ──────────
{
  const { html, stats } = purgeDocument(index);
  index = html;
  console.log(`css purge: ${stats.rules} rules, ${stats.removedRules} removed (${stats.removedSelectors} selectors, ${stats.keyframesRemoved} keyframes); ${stats.before} -> ${stats.after} bytes`);
}
console.log(`head grafted: ${tb - ta} bytes of template head replace ${nb - na} bytes of master head; index now ${index.length} bytes`);

// ── 3 · transplant each template page's edits onto the new index ──────────
const tok = s => s.split(/(?<=>)/);
function opcodes(a, b) {
  // Myers-lite: a straightforward LCS on token arrays via difflib-style matching blocks
  const A = tok(a), B = tok(b);
  // dynamic programming on the (small) number of differing regions is too big
  // for 30k tokens; use a hash-anchored greedy: walk both, resync on the next
  // shared token that is unique in both.
  const ops = []; let i = 0, j = 0;
  const idxB = new Map(); B.forEach((t, k) => { if (!idxB.has(t)) idxB.set(t, []); idxB.get(t).push(k); });
  while (i < A.length && j < B.length) {
    if (A[i] === B[j]) { i++; j++; continue; }
    // find the next resync point: smallest (di+dj) with A[i+di] === B[j+dj]
    let best = null;
    for (let di = 0; di < 400 && i + di < A.length; di++) {
      const cand = idxB.get(A[i + di]); if (!cand) continue;
      for (const k of cand) { if (k < j) continue; const dj = k - j; if (dj > 400) break;
        if (!best || di + dj < best[0] + best[1]) best = [di, dj]; }
    }
    if (!best) { ops.push([i, A.length, j, B.length]); i = A.length; j = B.length; break; }
    ops.push([i, i + best[0], j, j + best[1]]); i += best[0]; j += best[1];
  }
  if (i < A.length || j < B.length) ops.push([i, A.length, j, B.length]);
  return ops.filter(([a1, a2, b1, b2]) => a2 > a1 || b2 > b1).map(([a1, a2, b1, b2]) => [A.slice(a1, a2).join(''), B.slice(b1, b2).join('')]);
}

const pages = [];
(function walk(d) {
  for (const e of readdirSync(d)) {
    const p = join(d, e);
    if (statSync(p).isDirectory()) { if (e !== 'netlify' && e !== 'assets') walk(p); }
    else if (e.endsWith('.html')) pages.push(relative(TPL, p));
  }
})(TPL);

// the grafted head (description, og, JSON-LD) still says PRCF where the master
// now says PRCF Indonesia (block 98, 3 Sep). The rename has to follow the
// transplant — the per-page edits are anchored on the template's own text,
// which still says PRCF — so it is the last thing done to every page.
const rename = html => html.replace(/\bPRCF\b(?! Indonesia| INDONESIA)/g, 'PRCF Indonesia');
mkdirSync(OUT, { recursive: true });
writeFileSync(join(OUT, 'index.html'), rename(index));
let built = 0;
for (const rel of pages) {
  const outPath = join(OUT, rel); mkdirSync(dirname(outPath), { recursive: true });
  if (rel === 'index.html') { writeFileSync(outPath, rename(index)); built++; continue; }
  if (rel === '404.html') {
    // copied verbatim, but the stamp is the build's to write: the template's
    // own 404 said SHIP-2026-08-30f on every bundle cut from it, five builds
    // adrift by 09-04a. Same treatment as llms.txt below (3 Sep).
    const stamp = basename(OUT.replace(/\/+$/, ''));
    let f = readFileSync(join(TPL, rel), 'utf8');
    const before = f;
    f = f.replace(/<meta name="nf-ship" content="[^"]*">/, `<meta name="nf-ship" content="${stamp}">`);
    if (f === before) { console.error('404.html: no nf-ship stamp to rewrite'); process.exit(1); }
    writeFileSync(outPath, f); continue;
  }
  const tplPage = readFileSync(join(TPL, rel), 'utf8');
  const edits = opcodes(tplIndex, tplPage);
  let page = index;
  for (const [a, b] of edits) {
    if (!a) { console.error(`${rel}: pure insertion cannot be placed:\n  ${b.slice(0, 160)}`); process.exit(1); }
    const n = page.split(a).length - 1;
    if (n !== 1) { console.error(`${rel}: edit anchor found ${n} times (need 1):\n  ${a.slice(0, 200)}`); process.exit(1); }
    page = page.replace(a, b);
  }
  // 3b · per-page preloads: the quote plate's poster is the first thing a
  //      reader of /trade-pricing looks at, and until block 86 wets the video
  //      it was not even requested; on the desktop layout that shows the
  //      plate it now goes out with the fonts (3 Sep, Alex: "slow to load")
  const PAGE_PRELOADS = {
    'trade-pricing/index.html':    [`<link rel="preload" as="image" href="${CDN}quote-pour-2.jpg" media="(min-width:881px)">`],
    'ae/trade-pricing/index.html': [`<link rel="preload" as="image" href="${CDN}quote-pour-2.jpg" media="(min-width:881px)">`],
    'uk/trade-pricing/index.html': [`<link rel="preload" as="image" href="${CDN}quote-pour-2.jpg" media="(min-width:881px)">`],
  };
  for (const tag of PAGE_PRELOADS[rel] || []) {
    const at = page.indexOf('<link rel="preload" as="font"');
    if (at < 0) { console.error(`${rel}: no font preload to anchor the page preload on`); process.exit(1); }
    page = page.slice(0, at) + tag + '\n' + page.slice(at);
  }
  // 3b2 · the page's OWN route is known at build time (7 Sep, Alex: "the shop
  //       bag tiles are blank for a split second, same with Poured at the
  //       counter"). Two causes, two fixes, both head/attribute-level:
  //       (a) posters. Every route video holds its still as data-poster so the
  //           one-page master would not fetch ~1.2 MB of stills for routes
  //           nobody opened (pass96). On a per-route PAGE that deferral only
  //           delays the still the reader is looking at until the router runs,
  //           ~2 s in on the live site. For the section this page IS, the
  //           attribute is promoted to poster= at build time and the still is
  //           preloaded, so it paints as the HTML parses. Off-route sections
  //           keep data-poster; routeVideo() still promotes them on a client-side
  //           route change and is a no-op where the poster is already set.
  //       (b) the shop tiles are built by script, so their images cannot be
  //           discovered by the parser at all; the four bag stills are preloaded
  //           on the shop pages so they are in cache when the tiles appear.
  {
    const tree = rel.replace(/^(ae|uk)\//, '');
    const route = tree === 'index.html' ? 'home'
                : tree.startsWith('shop/') ? 'shop'
                : tree.startsWith('wholesale-coffee/') ? 'work'
                : tree.startsWith('trade-pricing/') ? 'quote'
                : tree.startsWith('origins/') ? 'origins' : null;
    if (route) {
      const openM = page.match(new RegExp(`<section class="route(?: on)?" id="${route}"`));
      if (!openM) { console.error(`${rel}: route section #${route} not found`); process.exit(1); }
      const open = openM.index;
      const nextM = page.slice(open + 10).match(/<section class="route(?: on)?"/);
      let close = nextM ? open + 10 + nextM.index : page.indexOf('</main>', open);
      let sec = page.slice(open, close);
      const posters = [];
      sec = sec.replace(/<video\b[^>]*?\sdata-poster="([^"]+)"[^>]*>/g, (tag, url) => { posters.push(url); return tag.replace(/\sdata-poster="/, ' poster="'); });
      page = page.slice(0, open) + sec + page.slice(close);
      const wanted = posters.slice();
      if (route === 'shop') for (const o of ['batang-toru', 'batang-gadis', 'gayo-lues', 'arakan']) wanted.push(`${CDN}bag-${o}-640.webp`);
      const at = page.indexOf('<link rel="preload" as="font"');
      if (at < 0) { console.error(`${rel}: no font preload to anchor image preloads on`); process.exit(1); }
      const tags = [...new Set(wanted)].filter(u => !page.includes(`as="image" href="${u}"`)).map(u => `<link rel="preload" as="image" href="${u}">`);
      if (tags.length) page = page.slice(0, at) + tags.join('\n') + '\n' + page.slice(at);
      if (posters.length || tags.length) console.log(`${rel}: ${posters.length} poster(s) promoted, ${tags.length} image preload(s)`);
    }
  }
  // 3c · the template's head (description, og, JSON-LD) still says PRCF where
  //      the master now says PRCF Indonesia (block 98, 3 Sep) — same rename,
  //      same word-boundary rule, applied to the whole page so no copy of the
  //      name is left behind
  page = rename(page);
  writeFileSync(outPath, page); built++;
  console.log(`${rel}: ${edits.length} edits transplanted${PAGE_PRELOADS[rel] ? ', ' + PAGE_PRELOADS[rel].length + ' preload' : ''}`);
}

// ── 4 · everything else, copied verbatim ──────────────────────────────────
(function copy(d) {
  for (const e of readdirSync(d)) {
    const p = join(d, e), rel = relative(TPL, p);
    if (statSync(p).isDirectory()) { mkdirSync(join(OUT, rel), { recursive: true }); copy(p); }
    else if (!e.endsWith('.html')) copyFileSync(p, join(OUT, rel));
  }
})(TPL);

// ── 4b · the ladder goes into the access function (block 114) ─────────────
{
  const fn = join(OUT, 'netlify', 'functions', 'access-verify.js');
  if (!existsSync(fn)) { console.error('access-verify.js missing from the bundle'); process.exit(1); }
  const before = readFileSync(fn, 'utf8');
  const marker = '/*NF_RATES*/null';
  if (!before.includes(marker)) { console.error('access-verify.js: NF_RATES marker missing'); process.exit(1); }
  writeFileSync(fn, before.replace(marker, JSON.stringify(RATES)));
  // the function must still parse, and the page must not carry the ladder
  const built = readFileSync(join(OUT, 'index.html'), 'utf8');
  if (/\br24\s*:\s*[1-9]/.test(built) || /var RATES\s*=/.test(built)) { console.error('built index.html still carries the ladder'); process.exit(1); }
  console.log('access-verify.js: RATES written (' + JSON.stringify(RATES).length + ' chars)');
}

// llms.txt: the partner names (block 98 — PRCF Indonesia; GJI in the roll-call)
const llms = join(OUT, 'llms.txt');
if (existsSync(llms)) {
  let t = readFileSync(llms, 'utf8').replace(/\bPRCF\b(?! Indonesia| INDONESIA)/g, 'PRCF Indonesia');
  const anchor = 'before it is sent.\n';
  if (!t.includes(anchor)) { console.error('llms.txt: partner passage anchor missing'); process.exit(1); }
  if (!t.includes('GJI')) t = t.replace(anchor, anchor + 'NoFilter\'s NGO partners, in full: PRCF Indonesia, SRI, OIC, GJI, Fauna & Flora\nMyanmar and ACCA.\n');
  // 3 Sep · the build stamp, stamped by the build.
  // The audit found llms.txt announcing "# build: SHIP-2026-08-30f" on a live
  // site running 02v — four days and a dozen blocks adrift. It was hand-typed
  // once and then left, which is what hand-typed build numbers do. The sitemap
  // has had its lastmod written by this script for weeks; this is the same
  // treatment for the one file whose entire job is telling an assistant what
  // is true right now.
  const stamped = `# build: ${basename(OUT)}\n# generated ${new Date().toISOString().slice(0,10)} — do not hand-edit this line\n`;
  t = /^# build:.*\n(# generated.*\n)?/.test(t) ? t.replace(/^# build:.*\n(# generated.*\n)?/, stamped) : stamped + t;
  writeFileSync(llms, t);
}

// sitemap lastmod → today
const sm = join(OUT, 'sitemap.xml');
if (existsSync(sm)) {
  const today = new Date().toISOString().slice(0, 10);
  writeFileSync(sm, readFileSync(sm, 'utf8').replace(/<lastmod>[^<]+<\/lastmod>/g, `<lastmod>${today}</lastmod>`));
}
console.log(`built ${built} pages into ${OUT}`);
