# -*- coding: utf-8 -*-
"""127 · ground evidence is coming soon, not live (Alex, 28 Oct: "we do have some but
it's temperaneous"). Four statements on the site disagreed; this makes all agree:
two layers live (polygons, satellite), two coming (drone, ground)."""
import sys, io
p = sys.argv[1]; m = io.open(p, encoding='utf-8').read()
def rep(a, b, c=1):
    global m; assert m.count(a) == c, (m.count(a), a[:80]); m = m.replace(a, b)
rep('''        <article class="ev" data-state="live" style="--ev-key:#D9A441">   <!-- block 105: live -->''',
    '''        <article class="ev" data-state="pend" style="--ev-key:#D9A441">   <!-- 127: coming soon; the patrol evidence on file is occasional, not a running layer -->''')
rep('<div class="ev-cap"><span>Gayo Lues patrol · in service</span></div>',
    '<div class="ev-cap"><span>Gayo Lues patrol · sample, not yet in service</span></div>')
rep('<div class="ev-t"><span class="lab">Layer 04</span><span class="ls"><span class="led"></span>Live</span></div>',
    '<div class="ev-t"><span class="lab">Layer 04</span><span class="ls"><span class="led"></span>Coming soon</span></div>')
rep('<span class="chip pend"><span class="led off"></span>GROUND 2026</span>',
    '<span class="chip pend"><span class="led off"></span>GROUND SOON</span>')
rep('Three of the four layers are live today; the fourth is dimmed until it is.',
    'Two of the four layers are live today; the other two are dimmed until they are.')
io.open(p, 'w', encoding='utf-8').write(m); print('patch_layer04 OK')
