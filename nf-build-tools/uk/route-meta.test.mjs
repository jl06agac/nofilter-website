// What the page RENDERS must match what the server SENT, for every route page.
//
// The bug this exists for: applyRouteMeta() rewrites the title and description
// on every client-side route change. With market tables for SG and AE only it
// overwrote the /uk pages' correct served metadata with the SINGAPORE strings,
// so a crawler that renders JS saw the wrong title on all ten UK pages.
//
// The first version of this test stubbed marketKey() by having documentElement
// return the market — which is exactly what the real DOM does NOT do. It passed
// while the live site was still wrong. So it now lifts the REAL marketKey out of
// the built page and gives it a realistic document: no data-mkt on <html> (the
// attribute is only ever on the market buttons), the page's own nf-market pin,
// and the hostname the tree is served from.
import { readFileSync } from 'node:fs';
const BUNDLE = process.argv[2];
const src = readFileSync(`${BUNDLE}/index.html`, 'utf8');
const grab = (re, n) => { const m = src.match(re); if (!m) { console.error('missing:', n); process.exit(1); } return m[0]; };
// a non-greedy regex stops at the first '}', which truncates a function that
// contains a try/catch — take the whole body by matching braces instead
const fnAt = (name) => {
  const i = src.indexOf(`function ${name}(`);
  if (i < 0) { console.error('missing:', name); process.exit(1); }
  let d = 0, j = src.indexOf('{', i);
  for (let k = j; k < src.length; k++) {
    if (src[k] === '{') d++;
    else if (src[k] === '}') { d--; if (d === 0) return src.slice(i, k + 1); }
  }
  console.error('unterminated:', name); process.exit(1);
};

const tables = ['ROUTE_META','ROUTE_META_AE','ROUTE_META_UK','ORIGIN_META','ORIGIN_META_AE','ORIGIN_META_UK']
  .map(n => grab(new RegExp(`var ${n}=\\{[\\s\\S]*?\\};`), n)).join('\n');
const marketKey = fnAt('marketKey');
const applyRouteMeta = fnAt('applyRouteMeta');

const ROUTES  = { home:'', origins:'origins', shop:'shop', work:'wholesale-coffee', quote:'trade-pricing' };
const ORIGINS = ['batang-toru','batang-gadis','gayo-lues','arakan-mountains'];
const TREES   = { SG:{pref:'',    host:'nofilter.sg'},
                  AE:{pref:'ae/', host:'nofilter.ae'},
                  UK:{pref:'uk/', host:'nofilter.sg'} };
const dec = s => s.replace(/&amp;/g,'&').replace(/&#39;/g,"'").replace(/&quot;/g,'"');

function page(rel){
  const t = readFileSync(`${BUNDLE}/${rel}index.html`, 'utf8');
  return { title: (t.match(/<title>(.*?)<\/title>/)||[])[1],
           desc:  (t.match(/<meta name="description" content="([^"]*)"/)||[])[1],
           pin:   (t.match(/<meta name="nf-market" content="([^"]*)"/)||[])[1] || null };
}

function rendered(p, host, route, origin){
  let desc = null;
  const doc = {
    title: p.title,
    // the real DOM: nothing ever sets data-mkt on <html>
    documentElement: { getAttribute: () => null },
    querySelector: (sel) => {
      if (sel === 'meta[name="nf-market"]') return p.pin ? { getAttribute: () => p.pin } : null;
      if (sel === 'meta[name="description"]') return { getAttribute: () => p.desc, setAttribute: (_,v) => { desc = v; } };
      return null;
    },
  };
  const f = new Function('document','location','openOrigin', `
    ${tables} ${marketKey} ${applyRouteMeta}
    applyRouteMeta(${JSON.stringify(route)});
    return [document.title, marketKey()];`);
  const [title, mk] = f(doc, { hostname: host }, origin || null);
  return { title, desc: desc === null ? p.desc : desc, market: mk };
}

let fail = 0;
for (const [want, { pref, host }] of Object.entries(TREES)) {
  for (const [route, path] of Object.entries(ROUTES)) {
    const p = page(pref + (path ? path + '/' : ''));
    const r = rendered(p, host, route, null);
    if (r.market !== want) { fail++; console.log(`  FAIL ${pref||'/'}${path} marketKey -> ${r.market} (want ${want})`); }
    if (dec(p.title) !== r.title) { fail++; console.log(`  FAIL ${pref||'/'}${path} title\n       served:   ${p.title}\n       rendered: ${r.title}`); }
    if (dec(p.desc)  !== r.desc)  { fail++; console.log(`  FAIL ${pref||'/'}${path} description\n       served:   ${p.desc}\n       rendered: ${r.desc}`); }
  }
  for (const o of ORIGINS) {
    const p = page(`${pref}origins/${o}/`);
    const r = rendered(p, host, 'origins', o);
    if (dec(p.title) !== r.title) { fail++; console.log(`  FAIL ${pref}origins/${o} title\n       served:   ${p.title}\n       rendered: ${r.title}`); }
  }
}
console.log(fail ? `${fail} mismatches` : 'all 27 route pages: marketKey resolves to the page\'s own market, and the rendered title and description match what was served');
process.exit(fail ? 1 : 0);
