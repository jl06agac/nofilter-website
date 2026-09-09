import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 103 · ONE WAY FORWARD ON STEP 3, THE SEND GLOWS, THE FORM KNOWS YOU ═══
# Alex, 3 Sep, on the corner "Your quote →" of the Price & share step: "this
# button should be disabled all together as progression is already embedded
# in 3A-3C. we may just need to make those buttons more prominent." Then:
# "ideally too some level of pulsing/glowing animation on the final submit
# proposal button." And: name / company / work email in the quote form
# "should be pre-built in to save the user time given they would have
# already submitted their email and name via initial quote builder access."
#   · step 3's corner Next is gone from view (it stays in the DOM: the 3C
#     button reaches the quote by clicking it, so its gating and scroll
#     handling still apply — block 75). Back stays.
#   · the in-card button (Lock in the price → Lock in the top-up → See your
#     quote) was a ghost: transparent, hairline. It is now the page's primary
#     button — signal fill, white — since it is the only way forward. Its
#     `pulse` class pointed at keyframes that never existed; it does not pulse,
#     and it should not: the glow is reserved for the send.
#   · the send takes the Eastspring glow the access button already wears
#     (nfProceed breathe + doorRing ring, out of phase), so the two doors of
#     the route are lit the same way. It stops the moment the form is sent
#     or the button is disabled, and under prefers-reduced-motion.
#   · when the gate opens, the quote form's name, company and email are filled
#     from what the reader typed at the door, leaving anything they have
#     already typed alone. Phone stays optional and empty.

CSS = r'''
/* ══ 103 · STEP 3 · ONE WAY FORWARD; THE SEND GLOWS ══════════════════════ */
.deck-screen[data-screen="2"] .deck-actions .deck-next{display:none}
.morph-lockbtn{background:var(--signal);border-color:var(--signal);color:#fff;font-size:12.5px;padding:15px 28px;
  box-shadow:0 12px 30px rgba(238,77,23,.28)}
.morph-lockbtn:hover{background:var(--signal);border-color:var(--signal);color:#fff;filter:brightness(1.1);
  box-shadow:0 16px 38px rgba(238,77,23,.4)}
.morph-lockbtn .mic{font-size:14px}
#ctaSend{animation:nfProceed 2.8s ease-in-out infinite, doorRing 2.4s ease-out infinite;box-shadow:0 14px 34px rgba(238,77,23,.34)}
#ctaSend:hover{filter:brightness(1.12)}
#ctaSend:disabled,#sendPanel .sent #ctaSend,#sendPanel.is-sent #ctaSend{animation:none;box-shadow:none}
@media(prefers-reduced-motion:reduce){#ctaSend{animation:none}}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

# the form knows who came through the door
JS = r'''<script>
/* ── block 103 · the quote form is filled from the door ─────────────────── */
(function(){
  function val(id){ var el = document.getElementById(id); return el ? String(el.value || '').trim() : ''; }
  function put(id, v){ var el = document.getElementById(id); if(el && v && !String(el.value || '').trim()){ el.value = v; el.dispatchEvent(new Event('input', { bubbles:true })); } }
  function prefill(){
    put('fName',  val('accName'));
    put('fCo',    val('accCo'));
    put('fEmail', val('accEmail') || (window.__nfAccEmail || ''));
  }
  var grant = window.__nfGrantAccess;
  window.__nfGrantAccess = function(){ try{ prefill(); }catch(e){} return grant ? grant.apply(this, arguments) : undefined; };
  window.__nfPrefillQuote = prefill;
})();
</script>
'''
fix("""<!-- block 89: keystroke-audio.js is loaded by the gate, on first open -->""",
    JS + """<!-- block 89: keystroke-audio.js is loaded by the gate, on first open -->""")

io.open(F, "w", encoding="utf-8").write(src)
print("one way forward on step 3; the send glows; the form knows you")
