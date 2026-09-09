import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 102 · THE TERMINAL TAKES A PASTE ═══════════════════════════════════════
# Alex, 3 Sep: "copying the custom code from email into CRT terminal isnt
# working, i just get 'v' in the CRT." Exactly so: the device listens to
# keydown, and ⌘V arrives there as the key "v" — a printable character, so
# it was typed and the event cancelled, which also cancelled the paste. The
# email says "type or paste this in"; now both are true.
#   · a key pressed with ⌘ / Ctrl / Alt is the browser's, not the device's;
#   · a paste while the gate is up is read from the clipboard, cleaned to the
#     characters a code can contain, and typed in one go — or buffered, like
#     early keystrokes, if the prompt is not live yet. Enter still submits,
#     as the email tells the reader.
fix("""  document.addEventListener('keydown', function(e){
    if(finished) return;
    if(!document.body.classList.contains('nf-gate-open')) return;   /* only while the gate is up */
    if(!inputEnabled){""",
    """  document.addEventListener('keydown', function(e){
    if(finished) return;
    if(!document.body.classList.contains('nf-gate-open')) return;   /* only while the gate is up */
    if(e.metaKey || e.ctrlKey || e.altKey) return;                  /* block 102: ⌘V is a paste, not a "v" */
    if(!inputEnabled){""")
fix("""  // mute knob — toggles the keystroke sound
  var mb=document.getElementById('crtMute');""",
    """  /* block 102 — the paste itself */
  document.addEventListener('paste', function(e){
    if(finished) return;
    if(!document.body.classList.contains('nf-gate-open')) return;
    var cd = e.clipboardData || window.clipboardData; if(!cd) return;
    var text = String(cd.getData('text') || '').replace(/[^A-Za-z0-9]+/g, '').toUpperCase();
    if(!text) return;
    e.preventDefault();
    if(!inputEnabled){ buffered += text; return; }
    entry += text; renderEntry(); playKey();
  });

  // mute knob — toggles the keystroke sound
  var mb=document.getElementById('crtMute');""")

io.open(F, "w", encoding="utf-8").write(src)
print("the terminal takes a paste")
