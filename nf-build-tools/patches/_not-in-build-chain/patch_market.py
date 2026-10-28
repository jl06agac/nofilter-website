# -*- coding: utf-8 -*-
"""131/132 · the wholesale page's titles and descriptions name the market and the
search phrase (28 Oct). The on-page "supply" beat that shipped with 131 was
withdrawn the same morning (Alex: "extremely inelegant ... messed the flow up");
the offer lives in one FAQ answer instead. What remains here is ROUTE_META, the
client-side titles, kept equal to the heads build-ship.mjs writes (SCOPE)."""
import sys, io
p = sys.argv[1]
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
