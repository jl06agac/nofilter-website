// Run nfHomeMarket() exactly as shipped, against a stubbed document/location,
// for every page in the bundle. This is the closest thing to proof available
// without a renderer: the function is lifted from the built file, not retyped.
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
const BUNDLE = process.argv[2];
const pages = [];
(function walk(d){ for (const e of readdirSync(d)) { const p=join(d,e);
  if (statSync(p).isDirectory()) { if (!['netlify','assets'].includes(e)) walk(p); }
  else if (e==='index.html') pages.push(relative(BUNDLE,p)); } })(BUNDLE);

const src = readFileSync(join(BUNDLE,'index.html'),'utf8');
const m = src.match(/function nfHomeMarket\(\)\{[\s\S]*?return"SG"\}/);
if (!m) { console.error('nfHomeMarket not found in the built page'); process.exit(1); }
const fnSrc = m[0];

function run(pageHtml, {host, path, search='', tz='Asia/Singapore'}) {
  const pin = (pageHtml.match(/<meta name="nf-market" content="([^"]+)">/)||[])[1] || null;
  const sandbox = {
    document: { querySelector: (sel) => sel==='meta[name="nf-market"]' && pin
        ? { getAttribute: () => pin } : null },
    location: { hostname: host, search, pathname: path },
    Intl: { DateTimeFormat: () => ({ resolvedOptions: () => ({ timeZone: tz }) }) },
  };
  const f = new Function('document','location','Intl', fnSrc + '; return nfHomeMarket();');
  return f(sandbox.document, sandbox.location, sandbox.Intl);
}

let fail = 0;
const cases = [];
for (const rel of pages.sort()) {
  const html = readFileSync(join(BUNDLE,rel),'utf8');
  const path = '/' + rel.replace(/index\.html$/,'').replace(/\/$/,'');
  const tree = rel.startsWith('uk/') ? 'UK' : rel.startsWith('ae/') ? 'AE' : 'SG';
  // each tree served from the domain it lives on
  const host = tree==='AE' ? 'nofilter.ae' : 'nofilter.sg';
  const got = run(html, {host, path});
  const want = tree;
  cases.push([rel, host, got, want, got===want]);
  if (got!==want) fail++;
}
// and the awkward ones
const uk = readFileSync(join(BUNDLE,'uk/index.html'),'utf8');
const sg = readFileSync(join(BUNDLE,'index.html'),'utf8');
const extra = [
  ['/uk from a London clock',      run(uk,{host:'nofilter.sg',path:'/uk',tz:'Europe/London'}), 'UK'],
  ['/uk from a Dubai clock',       run(uk,{host:'nofilter.sg',path:'/uk',tz:'Asia/Dubai'}),    'UK'],
  ['/uk on the .ae domain',        run(uk,{host:'nofilter.ae',path:'/uk'}),                    'UK'],
  ['/uk with ?mkt=sg (reader wins)',run(uk,{host:'nofilter.sg',path:'/uk',search:'?mkt=sg'}),  'SG'],
  ['root, London clock (as before)',run(sg,{host:'netlify.app',path:'/',tz:'Europe/London'}),  'UK'],
  ['root on .sg (as before)',       run(sg,{host:'nofilter.sg',path:'/'}),                     'SG'],
  ['root on .ae (as before)',       run(sg,{host:'nofilter.ae',path:'/'}),                     'AE'],
];
console.log('per-page market resolution:');
for (const [rel,host,got,want,ok] of cases) if (!ok) console.log('  FAIL', rel, host, got, '!=', want);
console.log(`  ${cases.length - fail}/${cases.length} pages resolve to their own market`);
console.log('edge cases:');
for (const [name,got,want] of extra) { const ok = got===want; if(!ok) fail++; console.log(`  ${ok?'ok  ':'FAIL'} ${name.padEnd(32)} -> ${got} (want ${want})`); }
process.exit(fail?1:0);
