import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ══ 83 · THE ACCESS CODE GOES BY EMAIL ON THE SITE, ON SCREEN IN THE FILE ═══
# Alex, 2 Sep, on the freshly deployed nofilter.ae: "why is the demo build
# notification in this? i should be receiving an email as we had in our live
# site".
# The live flow (28 Aug, pass163–178: access-request.js issues an HMAC code and
# emails it through Resend; access-verify.js checks what the CRT device is
# given; a name field so the email can say "Hi Alex") shipped in the 29/30 Aug
# bundles but was never carried back into this master, which still had the
# 24 Aug demo: a code made in the browser and printed beside the button that
# accepts it. The old builder papered over the gap; the rebuilt one did not
# know to. This block puts the live flow in the master, where it belongs, and
# keeps the demo for the one place it is right — this file opened from disk,
# where there are no functions to call. The switch is the protocol:
#   file:  → demo (code on screen, "Demo build." note, nothing emailed)
#   https: → live (code emailed, "Access code sent" note, server-checked)
# so Alex can still walk the whole journey from his Desktop, and a visitor on
# the site never sees a code that was not sent to them.
def fix(old, new):
    global src
    n = src.count(old)
    assert n == 1, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ── 1 · the form asks for a name (the email greets by it) ─────────────────
fix("""          <form class="acc-form" id="accForm" novalidate>
            <div class="acc-f">
              <label for="accEmail">Work email</label>""",
    """          <form class="acc-form" id="accForm" novalidate>
            <!-- block 83 — the email opens "Hi <first name>", so the form asks -->
            <div class="acc-f">
              <label for="accName">Your name</label>
              <input type="text" id="accName" name="name" autocomplete="name"
                     placeholder="Your name" required>
            </div>
            <div class="acc-f">
              <label for="accEmail">Work email</label>""")

# ── 2 · the panel carries both notes; JS shows the one that is true ───────
fix("""            <div class="acc-p-hd">Access code issued</div>
            <div class="acc-code" id="accCode">— — —</div>
            <p class="acc-p-note"><b>Demo build.</b> On the live site this arrives in your inbox and
              is never shown here. Nothing has been emailed — the code above is the one the door will
              accept, so you can walk the whole journey now.</p>""",
    """            <div class="acc-p-hd" id="accPanelHd">Access code issued</div>
            <div class="acc-code" id="accCode">— — —</div>
            <!-- block 83 — two notes, one shown: the demo note when this file is
                 opened from disk, the sent note on the site -->
            <p class="acc-p-note" id="accNoteDemo"><b>Demo build.</b> On the live site this arrives in your inbox and
              is never shown here. Nothing has been emailed — the code above is the one the door will
              accept, so you can walk the whole journey now.</p>
            <p class="acc-p-note" id="accNoteLive" hidden>We&rsquo;ve just sent a code to <b id="accDest">your work address</b>
              &mdash; it should be with you in a moment. Click <b>Enter the code</b> below, type or paste it in,
              and you&rsquo;ll be straight through. It keeps working for 24 hours, so there&rsquo;s no rush.
              Nothing yet? Have a quick look in your spam folder, or ask us for another.</p>""")

# ── 3 · the submit handler: email the code on the site, print it from disk ─
fix("""  var form = $('#accForm'); if(!form) return;
  var errEl = $('#accErr'), panel = $('#accIssued'), codeEl = $('#accCode');

  function fail(msg){ errEl.textContent = msg; errEl.hidden = false; }

  form.addEventListener('submit', function(ev){
    ev.preventDefault();
    errEl.hidden = true;
    var email = ($('#accEmail').value || '').trim().toLowerCase();
    var co    = ($('#accCo').value || '').trim();
    if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]{2,}$/.test(email)) return fail('That does not look like an email address.');
    if(!co) return fail('Please tell us which company this is for.');
    var domain = email.split('@')[1];
    if(FREE.indexOf(domain) >= 0){
      return fail('That is a personal inbox. Trade pricing needs a company address — '
                + 'or buy a bag on the shop page, which needs no code at all.');
    }
    var code = issueCode();
    window.__nfIssuedCode = code;
    codeEl.textContent = code;
    panel.hidden = false;
    panel.scrollIntoView({behavior:'smooth', block:'center'});
  });""",
    """  var form = $('#accForm'); if(!form) return;
  var errEl = $('#accErr'), panel = $('#accIssued'), codeEl = $('#accCode');

  function fail(msg){ errEl.textContent = msg; errEl.hidden = false; }

  /* block 83 — LIVE on the site (the code is emailed by
     /.netlify/functions/access-request and checked by access-verify), DEMO
     when this file is opened from disk (no functions exist there; the code is
     made here and shown, as it was on 24 Aug). window.__nfAccessLive is
     published so the CRT device makes the same choice. */
  var LIVE = window.__nfAccessLive = (location.protocol !== 'file:');

  form.addEventListener('submit', function(ev){
    ev.preventDefault();
    errEl.hidden = true;
    var name  = $('#accName') ? ($('#accName').value || '').trim() : '';
    var email = ($('#accEmail').value || '').trim().toLowerCase();
    var co    = ($('#accCo').value || '').trim();
    if(!name) return fail('Who should we address it to?');
    if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]{2,}$/.test(email)) return fail('That does not look like an email address.');
    if(!co) return fail('Please tell us which company this is for.');
    var domain = email.split('@')[1];
    if(FREE.indexOf(domain) >= 0){
      return fail('That is a personal inbox. Trade pricing needs a company address — '
                + 'or buy a bag on the shop page, which needs no code at all.');
    }
    window.__nfAccEmail = email;
    var hd = $('#accPanelHd'), nDemo = $('#accNoteDemo'), nLive = $('#accNoteLive');

    if(!LIVE){
      var code = issueCode();
      window.__nfIssuedCode = code;
      codeEl.textContent = code;
      if(hd) hd.textContent = 'Access code issued';
      if(nDemo) nDemo.hidden = false; if(nLive) nLive.hidden = true;
      panel.hidden = false;
      panel.scrollIntoView({behavior:'smooth', block:'center'});
      return;
    }

    var go = form.querySelector('.acc-go'), goHtml = go ? go.innerHTML : '';
    if(go){ go.disabled = true; go.innerHTML = 'Sending&hellip;'; }
    fetch('/.netlify/functions/access-request', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ email:email, company:co, name:name })
    }).then(function(r){
      if(r.status === 403) throw new Error('free');
      if(!r.ok) throw new Error('http ' + r.status);
      var dest = $('#accDest'); if(dest) dest.textContent = email;
      codeEl.textContent = 'Nearly there.';
      if(hd) hd.textContent = 'Access code sent';
      if(nDemo) nDemo.hidden = true; if(nLive) nLive.hidden = false;
      panel.hidden = false;
      panel.scrollIntoView({behavior:'smooth', block:'center'});
    }).catch(function(e){
      if(e && e.message === 'free'){
        fail('That is a personal inbox. Trade pricing needs a company address — '
           + 'or buy a bag on the shop page, which needs no code at all.');
      } else {
        fail('We could not send the code just now. Email alex@nofilter.sg and we will open it by hand.');
      }
    }).then(function(){ if(go){ go.disabled = false; go.innerHTML = goHtml; } });
  });""")

# ── 4 · the CRT device asks the server on the site, compares locally from disk
fix("""  function submit(){
    if(!inputEnabled) return;
    if(entry.replace(/\\s+/g,'').toUpperCase() === currentCode()){ unlock(); }
    else { deny(); }
  }""",
    """  function submit(){
    if(!inputEnabled) return;
    var typed = entry.replace(/[^A-Za-z0-9]+/g,'').toUpperCase();
    /* block 83 — from disk the code was made in this page and is compared
       here; on the site only access-verify knows it, so the device asks,
       says CHECKING… while it waits (the function sleeps 350ms on purpose),
       and unlocks or denies on the answer. A network failure is a denial —
       the same 'no' for every kind of failure, as the function itself gives. */
    if(!window.__nfAccessLive){
      if(typed === currentCode()){ unlock(); } else { deny(); }
      return;
    }
    if(!typed) return;
    inputEnabled = false;
    var chk = addLine('sm'); chk.style.color = 'rgba(244,239,226,.55)'; chk.textContent = 'CHECKING\\u2026';
    fetch('/.netlify/functions/access-verify', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ email: window.__nfAccEmail || '', code: typed })
    }).then(function(r){ return r.ok ? r.json() : {ok:false}; })
      .then(function(j){ return !!(j && j.ok); })
      .catch(function(){ return false; })
      .then(function(ok){
        if(chk.parentNode) chk.remove();
        inputEnabled = true;
        if(ok){ unlock(); } else { deny(); }
      });
  }""")

# the code has three digits now (TAPIRBASIN743) — the device takes digits too
old = """      if(e.key && e.key.length === 1 && /[a-zA-Z ]/.test(e.key)){
        e.preventDefault(); buffered += e.key.toUpperCase();
      }"""
new = """      if(e.key && e.key.length === 1 && /[a-zA-Z0-9 ]/.test(e.key)){   /* block 83: digits too */
        e.preventDefault(); buffered += e.key.toUpperCase();
      }"""
fix(old, new)
fix("""    if(e.key.length === 1 && /[a-zA-Z ]/.test(e.key)){ e.preventDefault(); entry += e.key.toUpperCase(); renderEntry(); if(e.key!==' ') playKey(); }""",
    """    if(e.key.length === 1 && /[a-zA-Z0-9 ]/.test(e.key)){ e.preventDefault(); entry += e.key.toUpperCase(); renderEntry(); if(e.key!==' ') playKey(); }   /* block 83: digits too */""")

io.open(F, "w", encoding="utf-8").write(src)
print("access code: emailed on the site, shown from disk")
