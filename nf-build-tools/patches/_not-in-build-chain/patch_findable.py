# -*- coding: utf-8 -*-
"""126 · findable: what a crawler reads must be what the site says (28 Oct 2026).

Run ONCE against the committed master, not in build.sh. The patch chain stopped
reproducing the master at commit 122 (the origin Records were written straight
into the master), so build.sh must not be run in place any more.

Why: a Google / ChatGPT baseline on 28 Oct found NoFilter absent for every buyer
query in all four markets. Part of the cause is on the page itself — not in the
rendered site, but in the HTML the crawlers read before any script runs:
  · demo-only strings sat in the static HTML ("DEMO BUILD · CHECKOUT NOT WIRED",
    "Demo build. ... the code above is the one the door will accept")
  · the quote console's static placeholders still carried the August ladder
    (45/48/55, three bands, 7.5%) which the live RATES (46/51/60, two bands,
    5%/10%) overwrite only after the script runs
  · "Where the 10% goes" on the workplace route, where the rate is 5–10%
  · Batang Toru's partner read "PRCF Indonesia · SRI" in three places and
    "PRCF Indonesia, OIC" in the fact box (OIC is right, confirmed 6 Oct)
  · "Two markets" with the UK tree live since 6 Sep
  · nothing on the record a model could cite: Davos, World of Coffee Indonesia,
    Agri-Food Week, EUDR, named clients
The #why route and the two retired beats are stripped at ship time instead
(build-ship.mjs, same day) so the master keeps its history.
"""
import sys, io
p = sys.argv[1]
m = io.open(p, encoding='utf-8').read()
n0 = len(m)

def rep(old, new, count=1):
    global m
    c = m.count(old)
    assert c == count, 'expected %d, found %d: %r' % (count, c, old[:90])
    m = m.replace(old, new)

# 1 · demo strings leave the static HTML; the script that reveals them writes them
rep('<div class="lab" id="checkoutNote" style="display:none;color:var(--signal)">DEMO BUILD · CHECKOUT NOT WIRED TO A PAYMENT BACKEND.</div>',
    '<div class="lab" id="checkoutNote" style="display:none;color:var(--signal)"></div>')
rep("$('#checkoutBtn').addEventListener('click', function(){\n  $('#checkoutNote').style.display = 'block';",
    "$('#checkoutBtn').addEventListener('click', function(){\n  $('#checkoutNote').textContent = 'The shop opens shortly. Checkout is not open yet.';\n  $('#checkoutNote').style.display = 'block';")
rep('''<p class="acc-p-note" id="accNoteDemo"><b>Demo build.</b> On the live site this arrives in your inbox and
              is never shown here. Nothing has been emailed — the code above is the one the door will
              accept, so you can walk the whole journey now.</p>''',
    '''<p class="acc-p-note" id="accNoteDemo" hidden></p>''')
rep("      if(nDemo) nDemo.hidden = false; if(nLive) nLive.hidden = true;",
    "      if(nDemo){ nDemo.innerHTML = '<b>Demo build.</b> On the live site this arrives in your inbox and is never shown here. Nothing has been emailed \\u2014 the code above is the one the door will accept, so you can walk the whole journey now.'; nDemo.hidden = false; }\n      if(nLive) nLive.hidden = true;")

# 2 · static placeholders → the current SG ladder (RATES.SG: 46 / 51 / 60, 5% below 51, 10% from 51)
rep('<b id="estPrice">SGD 48.00</b>) &middot; <b id="estBand">7.5%</b> to conservation.',
    '<b id="estPrice">SGD 51.00</b>) &middot; <b id="estBand">10%</b> to conservation.')
rep('<span id="cxFig">0.086</span>', '<span id="cxFig">0.092</span>')
rep('<span class="mnum" id="mFigNum">42.00</span>', '<span class="mnum" id="mFigNum">51.00</span>')
rep('<span class="mnum mnum-imp" id="mFigNum2">3.8</span>', '<span class="mnum mnum-imp" id="mFigNum2">9.2</span>')
rep('<span class="mprice-mark mprice-mark--mid" id="mPriceMarkMid"><span class="mprice-mark-lab">7.5%</span></span>',
    '<span class="mprice-mark mprice-mark--mid" id="mPriceMarkMid"><span class="mprice-mark-lab"></span></span>')
rep('<input type="range" id="wholePrice" class="scale-range thumb-pulse" value="48.00" min="45" max="55" step="0.25">',
    '<input type="range" id="wholePrice" class="scale-range thumb-pulse" value="51.00" min="46" max="60" step="0.25">')
rep('<div class="morph-ends"><span id="mEndL">SGD 45</span><span id="mEndR">SGD 55</span></div>',
    '<div class="morph-ends"><span id="mEndL">SGD 46</span><span id="mEndR">SGD 60</span></div>')
rep('<div class="uni-mk" id="uniMk2"></div><div class="uni-mklab" id="uniMkLab2">7.5%</div>',
    '<div class="uni-mk" id="uniMk2"></div><div class="uni-mklab" id="uniMkLab2"></div>')
rep('<div class="uni-end" id="uniLabL">SGD 45</div>', '<div class="uni-end" id="uniLabL">SGD 46</div>')
rep('<div class="uni-end uni-end-r" id="uniLabR">SGD 55</div>', '<div class="uni-end uni-end-r" id="uniLabR">SGD 60</div>')
rep('<div class="sv2"><span id="priceVal">48.00</span></div>', '<div class="sv2"><span id="priceVal">51.00</span></div>')
rep('<input type="range" id="priceSlider" min="45" max="55" step="0.25" value="48"',
    '<input type="range" id="priceSlider" min="46" max="60" step="0.25" value="51"')
rep('<span id="slFloor">Floor 45.00</span><span id="slDef">Default 48.00</span><span id="slCeil">Ceiling 55.00</span>',
    '<span id="slFloor">Floor 46.00</span><span id="slDef">Default 51.00</span><span id="slCeil">Ceiling 60.00</span>')
rep('''                <div class="band" data-band="1"><span class="bl2" id="bR1">Band 01 · 45.00–45.49</span><span class="bp">5.0%</span><span class="bl2">Base share</span></div>
                <div class="band" data-band="2"><span class="bl2" id="bR2">Band 02 · 45.50–45.99</span><span class="bp">7.5%</span><span class="bl2">Stepped share</span></div>
                <div class="band" data-band="3"><span class="bl2" id="bR3">Band 03 · 46.00+</span><span class="bp">10.0%</span><span class="bl2">Full rate</span></div>''',
    '''                <div class="band" data-band="1"><span class="bl2" id="bR1">Band 01 · 46.00–50.99</span><span class="bp">5%</span><span class="bl2">Below the opener</span></div>
                <div class="band on" data-band="2"><span class="bl2" id="bR2">Band 02 · 51.00+</span><span class="bp">10%</span><span class="bl2">Full rate</span></div>''')
rep('<div class="v sig" id="accBand">SGD 45.00 / kg</div>', '<div class="v sig" id="accBand">SGD 46.00 / kg</div>')
rep('<div class="v" id="qBand">45.00 → 55.00 / kg</div>', '<div class="v" id="qBand">46.00 → 60.00 / kg</div>')
rep('<div class="v sig" id="qFull">46.00 / kg</div>', '<div class="v sig" id="qFull">51.00 / kg</div>')
rep('<div class="q-val" id="qCoffeeLine">SGD 45.00<span class="q-unit"> /kg</span></div>',
    '<div class="q-val" id="qCoffeeLine">SGD 51.00<span class="q-unit"> /kg</span></div>')
rep('<div class="q-val" id="qInvoicedLine">SGD 45.00<span class="q-unit"> /kg</span></div>',
    '<div class="q-val" id="qInvoicedLine">SGD 51.00<span class="q-unit"> /kg</span></div>')
rep('<span id="qNgoVal">SGD 2.25</span>', '<span id="qNgoVal">SGD 5.10</span>')
# 43,000 cups × 18 g = 774 kg × 51.00 × 10% ≈ 3,947
rep('<span id="qConsAnnual">~SGD 1,625</span>', '<span id="qConsAnnual">~SGD 3,947</span>')
rep('<span id="qHeroCoffee">48.00</span>', '<span id="qHeroCoffee">51.00</span>')
rep('<div class="q-total-note" id="qHeroCoffeeNote">+ 5% to conservation · ~SGD 1,625/yr to NGO partners</div>',
    '<div class="q-total-note" id="qHeroCoffeeNote">+ 10% to conservation · ~SGD 3,947/yr to NGO partners</div>')

# 3 · the workplace route does not pay a flat 10%
rep('<figcaption><b>Where the 10% goes</b>', '<figcaption><b>Where the contribution goes</b>')
rep("t:'Where the 10% goes', a:'Where the', b:'10% goes.',", "t:'Where the contribution goes', a:'Where the', b:'contribution goes.',")

# 4 · Batang Toru's partners are PRCF Indonesia and OIC (fact box was already right)
rep("partner:'PRCF Indonesia · SRI'", "partner:'PRCF Indonesia · OIC'", 3)
rep('<span>Partner</span>PRCF Indonesia · SRI', '<span>Partner</span>PRCF Indonesia · OIC', 1) if '<span>Partner</span>PRCF Indonesia · SRI' in m else None

# 5 · three priced markets since 6 Sep
rep('''          <h3 class="ncc-h">Two markets</h3>
          <p class="ncc-p">Priced transparently in SGD or AED, ex GST, to fit the way your finance
            and procurement teams already work.</p>''',
    '''          <h3 class="ncc-h">Three markets</h3>
          <p class="ncc-p">Priced transparently in SGD, AED or GBP, before tax, to fit the way your
            finance and procurement teams already work.</p>''')

# 6 · on the record: the proof a buyer (or a model answering one) can cite
PROOF = '''
    <!-- 126 · 28 Oct. Everything a procurement reader asks for in the first call,
         and nothing the site said anywhere: where the coffee has been served,
         who pours it daily, and what the traceability means for EUDR reporting.
         Facts as Alex stated them; no claim of certification. -->
    <section class="beat" data-beat data-ground="paper" id="record">
      <div class="beat-hd"><span class="sn">09</span><span class="st">On the record</span></div>
      <div class="two">
        <div class="two-a">
          <h2 class="d2"><span class="rl"><span>Where it has</span></span><span class="rl"><span style="color:var(--signal)">been poured.</span></span></h2>
          <p class="body-lg fade d1x" style="margin-top:20px">NoFilter coffee has been served at the World
            Economic Forum in Davos and at World of Coffee Indonesia, and was shown at Singapore
            International Agri-Food Week in October 2026 for EUDR-ready traceability.</p>
          <p class="body-sm fade d1x" style="margin-top:18px">Every origin is mapped to GPS plot boundaries
            and cross-checked with the conservation partner on the ground, so the geolocation an EU
            Deforestation Regulation due-diligence statement asks for is on file for each lot rather
            than reconstructed afterwards.</p>
        </div>
        <div class="two-b fade d1x">
          <p class="lab" style="margin-top:6px">Poured daily at</p>
          <p class="body-lg" style="margin-top:10px">Microsoft &middot; Accenture &middot; Eastspring &middot; Sprinklr &middot; Blackstone</p>
          <p class="lab" style="margin-top:22px">Markets</p>
          <p class="body-sm" style="margin-top:8px">Singapore and the United Arab Emirates, with workplace supply in Dubai and
            Abu Dhabi. Now taking on clients in the United Kingdom.</p>
        </div>
      </div>
    </section>
'''
anchor = '''        <span class="nw-close-n"><i class="nw-close-dot" aria-hidden="true"></i>Builder online
          &middot; takes about 60 seconds</span>
      </div>
    </div>
  </section>

</div>
'''
rep(anchor, anchor.replace('  </section>\n\n</div>\n', '  </section>\n' + PROOF + '\n</div>\n'))

io.open(p, 'w', encoding='utf-8').write(m)
print('patch_findable OK  %d -> %d bytes' % (n0, len(m)))
