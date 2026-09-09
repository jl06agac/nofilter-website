// Lift NF_BASE, pathFor and refPath/routeFromRef out of the BUILT page and run
// them against stubbed locations. Proves a nav click inside /uk stays in /uk,
// and that the root and /ae trees are untouched.
import { readFileSync } from 'node:fs';
const BUNDLE = process.argv[2];
const src = readFileSync(`${BUNDLE}/index.html`,'utf8');

function grab(re, name){ const m = src.match(re); if(!m){ console.error('missing:',name); process.exit(1);} return m[0]; }
const meta   = grab(/var ROUTE_META=\{[\s\S]*?\};/, 'ROUTE_META');
const ometa  = grab(/var ORIGIN_META=\{[\s\S]*?\};/, 'ORIGIN_META');
const base   = grab(/var NF_BASE=function\(\)\{[\s\S]*?\}\(\);/, "NF_BASE");
const pfor   = grab(/function pathFor\(r\)\{[\s\S]*?\n?\}/, 'pathFor');
const rpath  = grab(/function refPath\(s\)\{[\s\S]*?return t\|\|"\/"\}/, 'refPath');
const rfrom  = grab(/function routeFromRef\(s\)\{[\s\S]*?return null\}/, 'routeFromRef');

function ctx(pathname){
  const f = new Function('location','ROUTES', `
    ${meta} ${ometa} var openOrigin=null; ${base} ${pfor} ${rpath} ${rfrom}
    return { NF_BASE:NF_BASE, pathFor:pathFor, refPath:refPath, routeFromRef:routeFromRef,
             ROUTE_META:ROUTE_META, setOrigin:function(o){openOrigin=o;} };`);
  return f({pathname, origin:'https://nofilter.sg', hash:'', search:''},
           ['home','why','origins','shop','work','quote']);
}

let fail=0;
const check=(name,got,want)=>{ const ok=String(got)===String(want); if(!ok)fail++;
  console.log(`  ${ok?'ok  ':'FAIL'} ${name.padEnd(52)} ${got}${ok?'':'   (want '+want+')'}`); };

console.log('on /uk/shop — a reader inside the UK tree:');
let c = ctx('/uk/shop');
check('NF_BASE', c.NF_BASE, '/uk');
for (const r of ['home','origins','shop','work','quote'])
  check(`pathFor("${r}")`, c.pathFor(r), r==='home' ? '/uk' : '/uk'+c.ROUTE_META[r].path);
check('a bare href "/shop" still resolves to its route', c.routeFromRef('/shop'), 'shop');
check('a "/uk/shop" href resolves to the same route',    c.routeFromRef('/uk/shop'), 'shop');
c.setOrigin('batang-toru');
check('an open origin drawer pushes inside the tree', c.pathFor('origins'), '/uk/origins/batang-toru');

console.log('on / — the Singapore tree, unchanged:');
c = ctx('/');
check('NF_BASE', c.NF_BASE===''?'(empty)':c.NF_BASE, '(empty)');
for (const r of ['home','origins','shop','quote'])
  check(`pathFor("${r}")`, c.pathFor(r), r==='home' ? '/' : c.ROUTE_META[r].path);
check('routeFromRef("/shop")', c.routeFromRef('/shop'), 'shop');

console.log('on /ae/shop — the UAE tree, unchanged:');
c = ctx('/ae/shop');
check('NF_BASE', c.NF_BASE===''?'(empty)':c.NF_BASE, '(empty)');
check('pathFor("shop")', c.pathFor('shop'), c.ROUTE_META.shop.path);

console.log('a /ukulele-shaped path must NOT be read as the UK tree:');
c = ctx('/ukulele');
check('NF_BASE', c.NF_BASE===''?'(empty)':c.NF_BASE, '(empty)');
process.exit(fail?1:0);
