import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 88 · THE SITE ANSWERS TO ITS PATHS ════════════════════════════════════
# Found 2 Sep while chasing the slow shop load: on the rebuilt bundle every
# pre-rendered page — /shop, /origins, /origins/gayo-lues, /trade-pricing —
# booted to the home route, because this master routes by hash alone and the
# path router (28 Aug, pass16x: paths per route, titles and descriptions per
# route and market, origin deep links that open the record's drawer,
# pushState and popstate) lived only in the old builder's output. It is in
# the master now, and it is quiet from disk: on file:// there is no history
# to push, so the hash carries on exactly as it did.
#   · a route has a path; an origin has a path under /origins;
#   · on load and on back/forward the route is read from the hash first,
#     then the path; an origin path opens that record's drawer as well;
#   · a hash navigation is still what every nav link does (the seven
#     hashchange listeners that re-measure the page keep firing), and once it
#     has landed the hash is folded into the path with replaceState;
#   · links to "/" and "/origins" route in-page instead of reloading;
#   · the document title and description follow the route and the market.

fix("""var ROUTES = ['home','origins','shop','work','quote'];""",
    """var ROUTES = ['home','origins','shop','work','quote'];

/* ── block 88 · paths, titles, descriptions ─────────────────────────────── */
var ROUTE_META = {
  home:    { path:'/',                 title:'NoFilter — Conservation coffee · Singapore & UAE',
             desc:'Single-origin coffee from NGO-led conservation projects on the edge of rainforest still standing. A share of every sale goes to holding that line, by contract.' },
  origins: { path:'/origins',          title:'Coffee origins — Sumatra, Aceh and Myanmar | NoFilter',
             desc:'Four single origins bought through NGO-led conservation projects: Batang Toru, Batang Gadis, Gayo Lues and the Arakan Mountains.' },
  shop:    { path:'/shop',             title:'Shop conservation coffee — 250 g and 1 kg | NoFilter',
             desc:'Retail bags of our four single origins, from NGO-led conservation projects in Indonesia and Myanmar. The shop opens shortly.' },
  work:    { path:'/wholesale-coffee', title:'Wholesale coffee for offices, cafés and hotels | NoFilter',
             desc:'Single-origin conservation coffee supplied by the kilo to offices, cafés, hotels and visitor attractions, with bean-to-cup machines on lease.' },
  quote:   { path:'/trade-pricing',    title:'Trade pricing and quote builder | NoFilter',
             desc:'Choose your coffees and machines, set your cups a year, and see the wholesale rate, monthly cost and forest contribution before you send it.' }
};
var ROUTE_META_AE = {
  home:    { title:'NoFilter — Conservation coffee in the UAE',
             desc:'Single-origin coffee from NGO-led conservation projects on the edge of rainforest still standing. Supplied across the UAE, priced in AED.' },
  origins: { title:'Coffee origins — Sumatra, Aceh and Myanmar | NoFilter UAE',
             desc:'The four single origins we buy through NGO-led conservation projects, supplied across the UAE: Batang Toru, Batang Gadis, Gayo Lues, Arakan.' },
  shop:    { title:'Shop conservation coffee in the UAE — 250 g and 1 kg',
             desc:'Retail bags of our four single origins in 250 g and 1 kg, shipped within the UAE and priced in AED. The shop opens shortly.' },
  work:    { title:'Wholesale coffee for UAE offices and cafés | NoFilter',
             desc:'Single-origin conservation coffee supplied by the kilo to offices, cafés and hotels across the UAE, with bean-to-cup machines on lease.' },
  quote:   { title:'Trade pricing in AED and quote builder | NoFilter',
             desc:'Choose your coffees and machines, set your cups a year, and see the AED rate, monthly cost and forest contribution before you send it.' }
};
var ORIGIN_META = {
  'batang-toru':      { k:'toru',   path:'/origins/batang-toru',      title:'Batang Toru coffee — Tapanuli, North Sumatra | NoFilter',
                        desc:'Single-origin coffee from Batang Toru, the last refuge of the Tapanuli orangutan, bought direct from buffer-village smallholders with PRCF and OIC.' },
  'arakan-mountains': { k:'arakan', path:'/origins/arakan-mountains', title:'Arakan Mountains coffee — Magway, Myanmar | NoFilter',
                        desc:'Single-origin coffee from the Arakan Mountains of Magway, Myanmar, bought through Fauna & Flora and the Asho Chin Coffee Association.' },
  'batang-gadis':     { k:'gadis',  path:'/origins/batang-gadis',     title:'Batang Gadis coffee — Mandailing, North Sumatra | NoFilter',
                        desc:'Single-origin coffee from the edge of Batang Gadis National Park in Mandailing, North Sumatra, bought through the conservation programme run by SRI.' },
  'gayo-lues':        { k:'gayo',   path:'/origins/gayo-lues',        title:'Gayo Lues coffee — Aceh, Sumatra | NoFilter',
                        desc:'Single-origin coffee from Gayo Lues on the edge of the Leuser Ecosystem, where orangutans, tigers, elephants and rhinos still share one landscape.' }
};
var ORIGIN_META_AE = {
  'batang-toru':      { title:'Batang Toru coffee, Tapanuli | NoFilter UAE',
                        desc:'Single-origin coffee from Batang Toru, last refuge of the Tapanuli orangutan, supplied across the UAE by the kilo and in 250 g and 1 kg bags.' },
  'arakan-mountains': { title:'Arakan Mountains coffee, Myanmar | NoFilter UAE',
                        desc:'Single-origin coffee from the Arakan Mountains of Myanmar, bought with Fauna & Flora and the ACCA, and supplied across the UAE priced in AED.' },
  'batang-gadis':     { title:'Batang Gadis coffee, North Sumatra | NoFilter UAE',
                        desc:'Single-origin coffee from the edge of Batang Gadis National Park, North Sumatra, bought through SRI and supplied across the UAE priced in AED.' },
  'gayo-lues':        { title:'Gayo Lues coffee, Aceh | NoFilter UAE',
                        desc:'Single-origin coffee from Gayo Lues on the edge of the Leuser Ecosystem in Aceh, supplied across the UAE by the kilo and in retail bags.' }
};
/* paths are pushed only where there is a server to answer them */
var PATHS_ON = (location.protocol === 'http:' || location.protocol === 'https:') && !!(window.history && history.pushState);
var openOrigin = null;
function pathFor(r){
  if(r === 'origins' && openOrigin && ORIGIN_META[openOrigin]) return ORIGIN_META[openOrigin].path;
  return (ROUTE_META[r] && ROUTE_META[r].path) || '/';
}
/* an href, a pathname or a full URL on this origin → a clean path, or null */
function refPath(s){
  if(!s) return null;
  var t = String(s);
  if(t.charAt(0) === '#') return null;
  if(/^[a-z]+:/i.test(t)){ if(t.indexOf(location.origin) !== 0) return null; t = t.slice(location.origin.length) || '/'; }
  if(t.charAt(0) !== '/') return null;
  t = t.split('?')[0].split('#')[0];
  if(t.length > 1 && t.charAt(t.length-1) === '/') t = t.slice(0,-1);
  return t || '/';
}
function routeFromRef(s){
  if(!s) return null;
  var t = String(s);
  if(t.charAt(0) === '#'){ t = t.slice(1); return ROUTES.indexOf(t) >= 0 ? t : null; }
  var p = refPath(t); if(p === null) return null;
  for(var r in ROUTE_META) if(ROUTE_META[r].path === p) return r;
  return null;
}
function originFromRef(s){
  var p = refPath(s); if(p === null) return null;
  for(var o in ORIGIN_META) if(ORIGIN_META[o].path === p) return o;
  return null;
}
function marketKey(){
  var m = document.documentElement.getAttribute('data-mkt'); if(m) return m;
  try{ return /(^|\\.)nofilter\\.ae$/.test((location.hostname || '').toLowerCase()) ? 'AE' : 'SG'; }catch(e){ return 'SG'; }
}
/* open one origin's record (its drawer) and close the rest; null closes all */
function setOrigin(slug){
  if(slug !== null && !ORIGIN_META[slug]) slug = null;
  openOrigin = slug;
  var sec = document.getElementById('origins');
  if(sec){ if(slug) sec.setAttribute('data-oo', slug); else sec.removeAttribute('data-oo'); }
  $$('.fbh-drawer[data-o]').forEach(function(d){
    var on = slug !== null && d.getAttribute('data-o') === slug;
    var btn = document.querySelector('.fbh-more[aria-controls="' + d.id + '"]');
    if(on){ d.hidden = false; void d.offsetWidth; d.classList.add('is-open'); }
    else  { d.classList.remove('is-open'); d.hidden = true; }
    if(btn) btn.setAttribute('aria-expanded', on ? 'true' : 'false');
  });
}
function applyRouteMeta(r){
  var m = ROUTE_META[r]; if(!m) return;
  var ae = marketKey() === 'AE';
  if(ae && ROUTE_META_AE[r]) m = ROUTE_META_AE[r];
  if(r === 'origins' && openOrigin && ORIGIN_META[openOrigin]) m = (ae && ORIGIN_META_AE[openOrigin]) || ORIGIN_META[openOrigin];
  if(document.title !== m.title) document.title = m.title;
  var d = document.querySelector('meta[name="description"]');
  if(d && d.getAttribute('content') !== m.desc) d.setAttribute('content', m.desc);
}
window.__nfPathFor = pathFor;""")

fix("""  current = r; window.__nfRoute = r;      /* pass106 */""",
    """  current = r; window.__nfRoute = r;      /* pass106 */
  if(r !== 'origins' && openOrigin !== null) setOrigin(null);   /* block 88 */""")

fix("""  if(push && location.hash !== '#' + r) location.hash = '#' + r;
  updateIdx();
}
function fromHash(){
  var h = (location.hash || '').replace('#','');
  if(ROUTES.indexOf(h) >= 0) go(h, false);
  else if(!h) go('home', false);
}
window.addEventListener('hashchange', fromHash);""",
    """  if(push && location.hash !== '#' + r) location.hash = '#' + r;
  applyRouteMeta(r);                                             /* block 88 */
  updateIdx();
}
/* block 88 — the hash first (a nav click), then the path (a landing, or
   back/forward); an origin path also opens that record. Once landed, the
   hash is folded into the path so the address bar reads /shop, not /#shop. */
function fromHash(){
  var r = routeFromRef(location.hash);
  if(r === null) r = routeFromRef(location.pathname);
  var o = originFromRef(location.pathname);
  if(o !== null) r = 'origins';
  if(o !== openOrigin) setOrigin(o);
  go(r === null ? 'home' : r, false);
  if(o !== null){
    var k = ORIGIN_META[o].k, sec = document.getElementById('fbh-' + k);
    if(sec) setTimeout(function(){ try{ sec.scrollIntoView({block:'start'}); }catch(e){} }, 60);
  }
  if(PATHS_ON && location.hash){
    var h = routeFromRef(location.hash);
    if(h !== null){ try{ history.replaceState({nf:h}, '', pathFor(h) + (location.search || '')); }catch(e){} }
  }
}
window.addEventListener('hashchange', fromHash);
window.addEventListener('popstate', fromHash);
/* a link to "/" or "/origins" (or any route's path) routes in-page */
document.addEventListener('click', function(ev){
  if(ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
  var a = ev.target && ev.target.closest ? ev.target.closest('a[href]') : null;
  if(!a || a.hasAttribute('download')) return;
  var tg = a.getAttribute('target'); if(tg && tg !== '_self') return;
  var href = a.getAttribute('href');
  var o = originFromRef(href), r = (o !== null) ? 'origins' : routeFromRef(href);
  if(r === null || (href && href.charAt(0) === '#')) return;    /* hash links have their own handler */
  ev.preventDefault();
  if(o !== null && PATHS_ON){ try{ history.replaceState(null, '', ORIGIN_META[o].path); }catch(e){} }
  if(location.hash === '#' + r) fromHash(); else location.hash = '#' + r;
});""")

# the four drawers carry the origin slug they belong to
for k, slug in [('toru','batang-toru'), ('arakan','arakan-mountains'), ('gadis','batang-gadis'), ('gayo','gayo-lues')]:
    fix('<div class="fbh-drawer" id="fbhd-%s" hidden>' % k,
        '<div class="fbh-drawer" id="fbhd-%s" data-o="%s" hidden>' % (k, slug))

io.open(F, "w", encoding="utf-8").write(src)
print("paths, titles and origin deep links in the master")
