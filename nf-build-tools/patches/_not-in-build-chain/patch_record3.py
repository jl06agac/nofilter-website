# -*- coding: utf-8 -*-
"""129 · the strip carries its own names (Alex, 28 Oct: "can we not improve GEO
simply by using our logos ... this just adds clutter").
The visible line from 128 goes. The marquee is built by script, so a crawler
received an empty track; the same markup the script writes is now in the HTML
with each client's name as alt text. The script still runs and overwrites it,
so what the reader sees is unchanged. When CLIENTS changes, re-run this file's
gen() on the new roster (it reads the array out of the master)."""
import sys, io, re, json
p = sys.argv[1]; m = io.open(p, encoding='utf-8').read()
def rep(a, b, c=1):
    global m; assert m.count(a) == c, (m.count(a), a[:80]); m = m.replace(a, b)
# 128 line out
m2 = re.sub(r'\n  <!-- 128 · the strip above is built by script.*?</p>', '', m, count=1, flags=re.S)
assert m2 != m and 'cmq-note">' not in m2; m = m2
rep('.cmq-note{margin:clamp(14px,1.6vw,20px) var(--gut,32px) 0;text-align:center;line-height:1.9;text-transform:none;letter-spacing:.06em;font-size:11px;max-width:980px;margin-left:auto;margin-right:auto}\n', '')
# roster, read from the script so the two cannot disagree at the time of writing
blk = m[m.index('  var CLIENTS = ['):]
blk = blk[:blk.index('];') + 2]
live = re.findall(r"\{ name:'([^']+)',\s*logo:'([^']+)',\s*s:([0-9.]+) \}", blk)
assert len(live) == 9, live
items = live[:]
while len(items) < 8: items += live
def markup(c):
    return '<div class="cmq-item" style="--cmq-s:%s"><img src="../../_CDN-UPLOAD-SAFE/%s" alt="%s" loading="lazy"></div>' % (c[2], c[1], c[0])
static = ''.join(markup(c) for c in items) * 2
rep('    <div class="cmq-track" id="cmqTrack"></div>',
    '    <!-- 129 · pre-rendered from CLIENTS so the names reach a crawler; the script below redraws it -->\n    <div class="cmq-track" id="cmqTrack">' + static + '</div>')
io.open(p, 'w', encoding='utf-8').write(m); print('patch_record3 OK', len(live), 'clients ×', len(items) * 2)
