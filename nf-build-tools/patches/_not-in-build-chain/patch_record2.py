# -*- coding: utf-8 -*-
"""128 · the record goes under the logo strip, not in its own beat (Alex, 28 Oct:
"is there no way of just including it here?" on seeing the marquee).
The marquee is script-built, so a crawler never saw a client name; one static
line under it carries the names and the three appearances. The #work beat
added in 126 comes out."""
import sys, io, re
p = sys.argv[1]; m = io.open(p, encoding='utf-8').read()
def rep(a, b, c=1):
    global m; assert m.count(a) == c, (m.count(a), a[:80]); m = m.replace(a, b)
# the beat out, whole
a = m.index('    <!-- 126 · 28 Oct. Everything a procurement reader asks for in the first call,')
b = m.index('</section>', m.index('id="record"')) + len('</section>') + 1
m = m[:a] + m[b:]
assert 'id="record"' not in m
# the line in
rep('''  <div class="cmq-vp">
    <div class="cmq-track" id="cmqTrack"></div>
  </div>
</div>''', '''  <div class="cmq-vp">
    <div class="cmq-track" id="cmqTrack"></div>
  </div>
  <!-- 128 · the strip above is built by script, so this line is the only place a
       crawler meets a client name or an appearance. Static on purpose. -->
  <p class="lab cmq-note">Poured at Microsoft, Accenture, Blackstone, Eastspring, Sprinklr and Cempedak Island, and through ISS, EFS and Lyreco.
    Served at the World Economic Forum in Davos and World of Coffee Indonesia; shown at Singapore International Agri-Food Week, October 2026, for EUDR-ready traceability.</p>
</div>''')
rep('''.cmq-vp{position:relative;overflow:hidden;''',
    '''.cmq-note{margin:clamp(14px,1.6vw,20px) var(--gut,32px) 0;text-align:center;line-height:1.9;text-transform:none;letter-spacing:.06em;font-size:11px;max-width:980px;margin-left:auto;margin-right:auto}
.cmq-vp{position:relative;overflow:hidden;''')
io.open(p, 'w', encoding='utf-8').write(m); print('patch_record2 OK')
