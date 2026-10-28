# -*- coding: utf-8 -*-
"""131 · the workplace route says what a buyer types (28 Oct).
A baseline search found NoFilter absent for "office coffee supplier Singapore",
"office coffee Dubai", "sustainable office coffee London" and their kin. The route
never used those words: it argued the forest and the counter and left the
buyer's own vocabulary to the quote builder. One short beat, first after the
orange band, in plain terms: who it is for, where, machines, servicing, invoice,
currency. Singapore copy lives here; build-ship.mjs swaps the market phrases
for the /ae and /uk trees (SCOPE table), so one beat serves three pages."""
import sys, io
p = sys.argv[1]; m = io.open(p, encoding='utf-8').read()
BEAT = '''    <!-- 131 · the buyer's words, first. Market phrases are swapped per tree by
         build-ship.mjs (SCOPE); edit them there, not here, for /ae and /uk. -->
    <style>#supply .ro .k{color:#6E6760}#supply .ro .v{color:#1A1815}#supply .ro .v.sig{color:var(--signal)}#supply .ro .v a{color:var(--signal)}</style>
    <section class="beat" data-beat data-ground="paper" id="supply">
      <div class="beat-hd"><span class="sn">01</span><span class="st">Office coffee supply &middot; Singapore</span></div>
      <div class="two">
        <div class="two-a">
          <h2 class="d2"><span class="rl"><span>Office coffee</span></span><span class="rl"><span style="color:var(--signal)">in Singapore.</span></span></h2>
          <p class="body-lg fade d1x" style="margin-top:22px">NoFilter is an office coffee supplier in Singapore.
            Whole-bean coffee by the kilo, bean-to-cup machines on rental or purchase, scheduled servicing,
            fresh milk and consumables, on one monthly invoice.</p>
          <p class="body-sm fade d1x" style="margin-top:16px">Four single origins from NGO-led conservation projects in Sumatra
            and Myanmar, roasted to order and delivered islandwide. A share of every kilo goes back to the
            conservation partner at the origin, written into the invoice. Prices in SGD, ex GST, from the quote
            builder in about two minutes.</p>
        </div>
        <div class="two-b fade d1x">
          <div class="readout">
            <div class="ro"><div class="k">For</div><div class="v">Offices &middot; hotels &middot; caf&eacute;s &middot; schools</div></div>
            <div class="ro"><div class="k">Machines</div><div class="v">CaféMatic 2 &middot; 5 &middot; 6 &middot; 8, rental or purchase</div></div>
            <div class="ro"><div class="k">Servicing</div><div class="v">Scheduled &middot; parts and labour on rental</div></div>
            <div class="ro"><div class="k">Coffee</div><div class="v sig">Per kg, 5&ndash;10% to conservation</div></div>
            <div class="ro"><div class="k">Delivery</div><div class="v">Islandwide, roasted to order</div></div>
            <div class="ro"><div class="k">Quote</div><div class="v"><a href="#quote">Build it online &rarr;</a></div></div>
          </div>
        </div>
      </div>
    </section>

'''
a = '    <!-- ══ EDITORIAL AUDIT, 21 Aug'
assert m.count(a) == 1
m = m.replace(a, BEAT + a)
io.open(p, 'w', encoding='utf-8').write(m); print('patch_market OK')

# ── ROUTE_META (client-side titles) say the same as the served heads ─────────
def rep(a, b):
    global m; assert m.count(a) == 1, a[:70]; m = m.replace(a, b)
m = io.open(p, encoding='utf-8').read()
rep("""  work:    { path:'/wholesale-coffee', title:'Wholesale coffee for offices, cafés and hotels | NoFilter',
             desc:'Single-origin conservation coffee supplied by the kilo to offices, cafés, hotels and visitor attractions, with bean-to-cup machines on lease.' },""",
    """  work:    { path:'/wholesale-coffee', title:'Office coffee supplier in Singapore | NoFilter',
             desc:'Office coffee supply in Singapore: conservation coffee by the kilo for offices, hotels and cafés, with bean-to-cup machines on rental, servicing and milk on one invoice.' },""")
rep("""  work:    { title:'Wholesale coffee for UAE offices and cafés | NoFilter',
             desc:'Single-origin conservation coffee supplied by the kilo to offices, cafés and hotels across the UAE, with bean-to-cup machines on lease.' },""",
    """  work:    { title:'Office coffee supplier in Dubai and Abu Dhabi | NoFilter',
             desc:'Office coffee supply for workplaces in Dubai and Abu Dhabi: conservation coffee by the kilo, bean-to-cup machines on rental or purchase, servicing and milk on one invoice.' },""")
rep("""  work:    { title:'Wholesale coffee for UK offices and cafés | NoFilter',
             desc:'Single-origin conservation coffee supplied by the kilo to offices, cafés and hotels across the UK, with bean-to-cup machines on lease.' },""",
    """  work:    { title:'Office coffee supplier for the UK | NoFilter',
             desc:'Now taking on office coffee clients in London and across the UK: conservation coffee by the kilo, bean-to-cup machines on rental or purchase, priced in GBP.' },""")
io.open(p, 'w', encoding='utf-8').write(m); print('route meta OK')
