import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 59 · STEP 4 FOR PROCUREMENT AND FINANCE ═══════════════════════════════
# Alex's finalised spec for the "Your quote" screen. Three decisions he made
# when I put the conflicts to him, all of which shape what follows:
#
#   · the top-up IS billed — total invoiced = base + top-up — and the band
#     percentage keeps computing on the BASE rate, so voluntary money can never
#     silently push the band into the next tier and get counted twice;
#   · the Cinta Raja planting is written as RESTORATION, not as a carbon
#     offset. His copy said "toward your carbon offset commitment" twice; the
#     site's own canon (SYS_03) claims restoration and does not claim
#     accreditation, and an unaudited offset claim is the first thing a finance
#     team challenges. The existing wording is used instead;
#   · every "Included" tag stays conditional. syncInclusions() already resolves
#     what is free, chargeable or declined per unit and per mode; this rewrites
#     the copy AROUND it and does not flatten it. A purchase with no servicing
#     plan still reads "NOT INCLUDED — plan declined", not "Included".

# ── A · the coffee card becomes a line-item table ─────────────────────────
old = """    <div class="q-line">
      <div class="q-lab">Conservation coffee <span class="q-sub" id="qCoffeeSub">SGD 42.00 / kg · 5% to conservation</span></div>
      <div class="q-val" id="qCoffeeLine">SGD 42.00<span class="q-unit"> /kg</span></div>
    </div>
    <div class="q-line" id="qTopUpRow">
      <div class="q-lab"><span id="qTopUpLab">Conservation contribution</span> <span class="q-sub" id="qTopUpSub">pass-through to NGO partners in full</span></div>
      <div class="q-val" id="qTopUpLine">SGD 0.00<span class="q-unit"> /kg</span></div>
    </div>
    <div class="q-line">
      <div class="q-lab">Conservation contribution <span class="q-sub">to NGO partners &middot; at <span id="qConsBasis">43,000</span> cups/yr</span></div>
      <div class="q-val" id="qConsAnnual">~SGD 1,625<span class="q-unit"> /yr</span></div>
    </div>"""
new = """    <!-- block 59: no algebra on a page a finance team reads. Three billed lines
         and a separate pass-through panel, because what is invoiced and what
         reaches the NGOs are different questions with a shared number. -->
    <div class="q-line">
      <div class="q-lab">Base Conservation Coffee <span class="q-sub" id="qCoffeeSub">Includes built-in NGO share</span></div>
      <div class="q-val" id="qCoffeeLine">SGD 45.00<span class="q-unit"> /kg</span></div>
    </div>
    <div class="q-line" id="qTopUpRow" hidden>
      <div class="q-lab">Voluntary Impact Top-Up <span class="q-sub" id="qTopUpSub">passed through in full</span></div>
      <div class="q-val" id="qTopUpLine">+ SGD 0.00<span class="q-unit"> /kg</span></div>
    </div>
    <div class="q-line q-line--sum" id="qInvoicedRow">
      <div class="q-lab">Total Invoiced Coffee Rate <span class="q-sub">Final billed rate per kilo</span></div>
      <div class="q-val" id="qInvoicedLine">SGD 45.00<span class="q-unit"> /kg</span></div>
    </div>
    <div class="q-ngo" id="qNgoCard">
      <div class="q-ngo-hd">Total NGO Direct Funding</div>
      <div class="q-ngo-val"><span id="qNgoVal">SGD 2.25</span><span class="q-ngo-unit"> /kg</span>
        <span class="q-ngo-in">included in the total billed rate</span></div>
      <div class="q-ngo-sub" id="qNgoSub">&mdash;</div>
      <div class="q-ngo-sub" id="qConsBasisWrap">at <span id="qConsBasis">43,000</span> cups/yr &middot;
        <span id="qConsAnnual">~SGD 1,625</span>/yr</div>
    </div>"""
assert src.count(old) == 1, "coffee card anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── B · the perks column: Title Case, his copy, Cinta Raja added ──────────
subs = [
("""      <div class="q-lab">Live Impact Tablet <span class="q-sub" id="qTabletSub">cups poured and conservation raised, updating live</span></div>""",
 """      <div class="q-lab">Live Impact Screen <span class="q-sub" id="qTabletSub">Displays real-time cups poured and conservation funds raised</span></div>"""),
("""      <div class="q-lab">Branded machine decal <span class="q-sub">optional · your mark on the machine livery</span></div>""",
 """      <div class="q-lab">Co-Branded Machine Wrap <span class="q-sub">Customised NoFilter artwork featuring your company logo</span></div>"""),
("""      <div class="q-lab">Hosted impact tracker <span class="q-sub">private URL · conservation + composting, live after signing</span></div>
      <div class="q-val">Included</div>
    </div>""",
 """      <div class="q-lab">Hosted Impact Tracker <span class="q-sub">Private live URL tracking conservation and composting metric updates</span></div>
      <div class="q-val">Included</div>
    </div>
    <!-- block 59 · Cinta Raja. Written from the site's own SYS_03 card, which
         says "Active rainforest restoration built into every account · direct
         tree planting in the Cinta Raja corridor at zero extra charge" and
         claims restoration rather than an accredited offset. Alex chose that
         wording over the offset framing in his spec. Universal, so no
         conditional tag — it is the one row that is genuinely always on. -->
    <div class="q-line">
      <div class="q-lab">Cinta Raja Tree Restoration <span class="q-sub">Tree planting in the Cinta Raja corridor &mdash; rainforest restoration built into every account</span></div>
      <div class="q-val">Included</div>
    </div>"""),
("""      <div class="q-lab">Fleet service programme <span class="q-sub">twice-yearly Y1–Y2 · every four months Y3 · parts &amp; labour</span></div>""",
 """      <div class="q-lab">Servicing &amp; Maintenance <span class="q-sub" id="qFleetSub">Scheduled visits &middot; parts and labour included</span></div>"""),
("""      <div class="q-lab">Grounds collection &amp; composting <span class="q-sub">diverted to our composting partner</span></div>""",
 """      <div class="q-lab">Grounds Collection &amp; Composting <span class="q-sub">Spent grounds diverted directly to our composting partners</span></div>"""),
("""      <div class="q-lab">Yearly impact report <span class="q-sub">reconciled against actual kg supplied · issued annually</span></div>""",
 """      <div class="q-lab">Annual Impact Report <span class="q-sub">Reconciled against actual kg supplied and issued annually</span></div>"""),
("""      <div class="q-lab">Milk coolers <span class="q-sub" id="qCoolerSub">1 per machine · 2 included</span></div>""",
 """      <div class="q-lab">Milk Fridge <span class="q-sub" id="qCoolerSub">1 per machine</span></div>"""),
# ── C · the form ──────────────────────────────────────────────────────────
("""<input id="fName" name="name" type="text" autocomplete="name" placeholder="—" required>""",
 """<input id="fName" name="name" type="text" autocomplete="name" placeholder="Jane Doe" required>"""),
("""<input id="fCo" name="company" type="text" autocomplete="organization" placeholder="—" required>""",
 """<input id="fCo" name="company" type="text" autocomplete="organization" placeholder="Acme Corp" required>"""),
("""<input id="fEmail" name="email" type="email" autocomplete="email" placeholder="—" required>""",
 """<input id="fEmail" name="email" type="email" autocomplete="email" placeholder="jane@acme.com" required>"""),
("""<input id="fPhone" name="phone" type="tel" autocomplete="tel" placeholder="—">""",
 """<input id="fPhone" name="phone" type="tel" autocomplete="tel" placeholder="+65 9123 4567">"""),
("""                  <span class="q-taste-hd">Want to taste it first?</span>
                  <label class="q-taste-opt">
                    <input type="checkbox" id="fTasteShow" name="tasting_showroom">
                    <span>At our supply partner&rsquo;s showroom, on the machines you&rsquo;ve chosen &mdash; <b>no charge</b></span>
                  </label>
                  <label class="q-taste-opt">
                    <input type="checkbox" id="fTasteSite" name="tasting_onsite">
                    <span>On your own floor &mdash; quoted, with <b>half back</b> if you go ahead</span>
                  </label>""",
 """                  <span class="q-taste-hd">Taste test options</span>
                  <label class="q-taste-opt">
                    <input type="checkbox" id="fTasteShow" name="tasting_showroom">
                    <span><b class="q-taste-t">Showroom tasting <i>free</i></b>
                      Taste test on your chosen machines at our partner showroom</span>
                  </label>
                  <label class="q-taste-opt">
                    <input type="checkbox" id="fTasteSite" name="tasting_onsite">
                    <span><b class="q-taste-t">On-site office trial</b>
                      Test on your pantry floor &mdash; 50% credited back toward your order if you proceed</span>
                  </label>"""),
("""                    SEND ME THIS QUOTE <span class="ar">→</span></button>""",
 """                    SEND PROPOSAL TO MY EMAIL <span class="ar">→</span></button>"""),
]
for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:64])
    src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("step 4 markup restructured")
