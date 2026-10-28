"""Reviewed, one-off master edit. Not part of the build chain."""
from pathlib import Path
import re
p=Path(__file__).resolve().parents[3]/'NoFilter-Website-Master.html'
s=p.read_text()
assert 'id="nfServiceIntro"' not in s
block='''
<style id="nf-service-css">
.nf-service{padding:28px 0;background:var(--paper,#F4F2EE);color:var(--ink,#1A1815)}
.nf-service h1{font-family:var(--body,sans-serif);font-size:clamp(22px,3vw,34px);line-height:1.2;margin:0 0 12px}
.nf-service p{font-family:var(--body,sans-serif);font-size:15px;line-height:1.65;max-width:80ch;margin:8px 0}
.nf-service a{color:inherit;text-decoration:underline;text-underline-offset:3px}
</style>
<div class="nf-service" id="nfServiceIntro"><div class="wrap">
<div data-nf-market-copy="SG">
<h1>Office coffee supply in Singapore</h1>
<p>NoFilter supplies offices, hotels and cafés in Singapore with whole-bean coffee, bean-to-cup machines on rental or purchase, servicing, fresh milk and consumables.</p>
</div>
<div data-nf-market-copy="AE" hidden>
<h1>Office coffee supply in Dubai and Abu Dhabi</h1>
<p>NoFilter supplies workplace clients in Dubai and is ready to serve offices in Abu Dhabi and across the UAE. Coffee, bean-to-cup machines on rental or purchase, servicing, milk and consumables are quoted in AED.</p>
</div>
<div data-nf-market-copy="UK" hidden>
<h1>Office coffee supply for London and the UK</h1>
<p>NoFilter welcomes enquiries and is taking on office coffee clients in London and across the UK. Coffee and equipment options are quoted in GBP, with supply and servicing arrangements agreed for each workplace.</p>
</div>
<p>For workplaces looking for sustainable office coffee, our approach starts at origin: mapped growing plots, satellite verification and named conservation NGO partners. A contractual 5–10% of the coffee price supports those partners, depending on the price band.</p>
<p><a href="/origins">Explore the origins and evidence</a> · <a href="/faqs#eudr">Read about traceability and EUDR</a> · <a href="/trade-pricing">Request trade access</a></p>
</div></div>
'''
anchor='<section class="route" id="work" data-title="ON THE COUNTER">'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+block)
anchor='function applyRouteMeta(r){\n'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+"  if(document.documentElement.hasAttribute('data-nf-page')) return; // built page head is authoritative\n")
anchor="function applyMarket(k){\n  var sel = MARKETS[k] ? k : 'SG';"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\n  document.querySelectorAll('[data-nf-market-copy]').forEach(function(el){ el.hidden = el.getAttribute('data-nf-market-copy') !== sel; });")
# Legacy programmatic route actions must navigate built documents.
old="function fromHash(){\n  var r = routeFromRef(location.hash);"
new="""function fromHash(){
  var r = routeFromRef(location.hash);
  /* Built documents navigate when a legacy action selects another route. */
  var builtPage = document.documentElement.getAttribute('data-nf-page');
  if(builtPage && r !== null && r !== builtPage){
    location.assign(pathFor(r) + (location.search || '')); return;
  }"""
assert old in s
s=s.replace(old,new,1)
# Quote values are populated by the access-verified runtime, never seeded in HTML.
for ident in ['qBand','qFull','wholePriceV','priceVal','bR1','bR2','qCoffeeLine','qInvoicedLine','qNgoVal','qConsAnnual','qHeroCoffee','qHeroCoffeeNote']:
    pat=r'(<([a-z0-9]+)\b[^>]*\bid="'+ident+r'"[^>]*>).*?(</\2>)'
    s,n=re.subn(pat,lambda m:m[1]+'Awaiting access'+m[3],s,count=1,flags=re.S)
    assert n==1,ident
s=re.sub(r'(<input\b[^>]*id="priceSlider"[^>]*>)',lambda m:re.sub(r'(min|max|value)="[^"]*"',r'\1="0"',m[0]),s,count=1)
p.write_text(s)
