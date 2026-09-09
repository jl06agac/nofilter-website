import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 101 · THE TRADE DOOR, IN THE READER'S TERMS ════════════════════════════
# Alex, 3 Sep, on the intro: "much clearer than 'configure equipment…' and
# leads with their space / their choices / what they get." His copy, as
# agreed (the "no sales call" close dropped at his call). The card after
# submission is the agreed rewrite: the reader's first name inside "Nearly
# there.", the address they gave, and "send yourself a fresh one" as a link
# that actually re-sends — the form is still filled in on the left, so one
# click, no retyping; the old note said "ask us for another" and went
# nowhere. The first name is the first word of the name field, used only
# when it looks like a name (letters, 2+); anything else gets plain
# "Nearly there." so it never reads oddly.
# Two things his screenshot of 02m showed, fixed here because black made
# them visible: Chrome's autofill fill (pale blue, dark text — a light-mode
# form in a dark page) now takes the input's own surface; and once the code
# is issued, the right column, which hangs from the row's foot so the plate
# lines up with the button, sat the card at the bottom of an empty column on
# a tall screen — it now sits at the top, where the plate was.

fix("""          <p class="body-lg fade d1x">Configure equipment, coffee volume, and
            servicing for your space in under two minutes. Real wholesale pricing and live conservation
            metrics&mdash;calculated instantly without waiting for a sales call. Enter your work email to
            unlock the terminal.</p>""",
    """          <!-- block 101 — Alex's copy, 3 Sep -->
          <p class="body-lg fade d1x">Build a setup that works for your space. Choose your machines,
            coffee volume and servicing, and see your wholesale rate, monthly cost and conservation
            contribution update as you go. It takes about two minutes. Enter your work email and
            we&rsquo;ll send you a code to open the builder.</p>""")

fix("""            <p class="acc-p-note" id="accNoteLive" hidden>We&rsquo;ve just sent a code to <b id="accDest">your work address</b>
              &mdash; it should be with you in a moment. Click <b>Enter the code</b> below, type or paste it in,
              and you&rsquo;ll be straight through. It keeps working for 24 hours, so there&rsquo;s no rush.
              Nothing yet? Have a quick look in your spam folder, or ask us for another.</p>""",
    """            <!-- block 101 — the agreed card copy; the resend is a real action -->
            <p class="acc-p-note" id="accNoteLive" hidden>We&rsquo;ve sent a code to <b id="accDest">your work address</b>.
              Pop it in and your quote builder opens straight away.<br>
              The code works for 24 hours, so there&rsquo;s no rush. Can&rsquo;t see it? Check your spam folder, or
              <a href="#" id="accResend">send yourself a fresh one</a>.</p>""")

# the greeting, and the resend
fix("""      var dest = $('#accDest'); if(dest) dest.textContent = email;
      codeEl.textContent = 'Nearly there.';
      if(hd) hd.textContent = 'Access code sent';""",
    """      var dest = $('#accDest'); if(dest) dest.textContent = email;
      /* block 101 — first name into the line, when the first word reads as one */
      var first = name.split(/\\s+/)[0] || '';
      codeEl.textContent = /^[A-Za-z][A-Za-z'\\u2019-]+$/.test(first) ? 'Nearly there, ' + first + '.' : 'Nearly there.';
      if(hd) hd.textContent = window.__nfResent ? 'Fresh code sent' : 'Access code sent';
      var rs = $('#accResend'); if(rs && window.__nfResent){ rs.textContent = 'sent again just now'; }
      window.__nfResent = false;""")

fix("""  $('#accEnter').addEventListener('click', openGate);""",
    """  $('#accEnter').addEventListener('click', openGate);
  /* block 101 — "send yourself a fresh one": the form on the left is still
     filled in, so this is the same request again */
  var resend = $('#accResend');
  if(resend) resend.addEventListener('click', function(ev){
    ev.preventDefault();
    window.__nfResent = true;
    if(form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event('submit', { cancelable:true }));
  });""")

CSS = r'''
/* ══ 101 · AUTOFILL, THE CARD'S SEAT, THE RESEND LINK ══════════════════════ */
#quote .acc-f input:-webkit-autofill,#quote .acc-f input:-webkit-autofill:hover,#quote .acc-f input:-webkit-autofill:focus{
  -webkit-box-shadow:0 0 0 1000px #111816 inset;-webkit-text-fill-color:#F4F2EE;caret-color:#F4F2EE;
  border-color:#343a36;transition:background-color 9999s ease-out}
#quote .acc-f input:-webkit-autofill:focus{border-color:var(--signal)}
/* once the code is issued the column stops hanging from the row's foot and
   sits at its head, where the plate was */
@media (min-width:901px){
  #nfAccess .two:has(#accIssued:not([hidden])) > .two-b{align-self:start;height:auto;justify-content:flex-start}
}
.acc-p-note a{color:var(--cream);border-bottom:1px solid rgba(244,242,238,.4);text-decoration:none}
.acc-p-note a:hover{border-bottom-color:var(--signal);color:#FFC9A8}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

io.open(F, "w", encoding="utf-8").write(src)
print("the trade door speaks to the reader")
