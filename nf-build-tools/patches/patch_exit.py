import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the two panels are mutually exclusive views ───────────────────────
subs.append((
"""    grid.classList.add('mx-exiting');
    document.body.classList.add('mx-detail-open');""",
"""    /* ── 1 Sep · THE SPECS SHEET AND THE PURCHASE PANEL CANNOT BOTH BE OPEN.
       Alex: "if i open the machine details/specs, it renders this below our
       actively open purchase option."
       They are two full-width takeovers of the same step and neither knew the
       other existed — the specs sheet was written months before the dossier. So
       you got a dark configurator stacked on top of a cream spec sheet, both
       live, both scrollable, with two different "back" affordances. Opening
       either now closes the other; see the matching call in MODULE C2. */
    if(window.__nfCloseBuyDoss) window.__nfCloseBuyDoss();
    grid.classList.add('mx-exiting');
    document.body.classList.add('mx-detail-open');"""))

subs.append((
"""  document.getElementById('mxBack').addEventListener('click',close);""",
"""  document.getElementById('mxBack').addEventListener('click',close);
  window.__nfCloseSpecs = close;   /* so the purchase panel can stand this down */"""))

subs.append((
"""    var reopen = (openK === k);
    openK = k;""",
"""    var reopen = (openK === k);
    /* the other full-width takeover of this step — see initSpecs' matching call.
       Only on a fresh open: a reopen has not been anywhere. */
    if(!reopen && window.__nfCloseSpecs) window.__nfCloseSpecs();
    openK = k;"""))

# ── 2 · quantity can reach zero, and says so ──────────────────────────────
subs.append((
"""    if(t.hasAttribute('data-nfbd-q')){
      cfg.q = Math.max(1, Math.min(20, cfg.q + parseInt(t.getAttribute('data-nfbd-q'), 10)));
    } else if(t.hasAttribute('data-nfbd-yrs')){""",
"""    if(t.hasAttribute('data-nfbd-q')){
      /* ── 1 Sep · ZERO IS REACHABLE AGAIN ──────────────────────────────────
         Alex: "no option for me to go back to 0 units in purchase, and
         reexplore other options, it's clunky."
         It was a dead end of my own making. The stepper floored at 1, and the
         card's own minus button had been replaced by the "xN Edit" pill — so
         once a machine was configured there was no control anywhere that could
         un-configure it. The only way out was switching to Rental and back.
         The stepper floors at 0 now: hitting zero drops the machine from the
         quote and shuts the panel, which returns the card to "Configure" and
         the reader to the row. */
      cfg.q = Math.max(0, Math.min(20, cfg.q + parseInt(t.getAttribute('data-nfbd-q'), 10)));
      if(cfg.q === 0){ recalc(); close_(); return; }
    } else if(t.hasAttribute('data-nfbd-remove')){
      cfg.q = 0; recalc(); close_(); return;
    } else if(t.hasAttribute('data-nfbd-yrs')){"""))

subs.append((
"""    if(t.hasAttribute('data-nfbd-close')){ close_(); return; }""",
"""    if(t.hasAttribute('data-nfbd-close')){ close_(); return; }
    if(t.hasAttribute('data-nfbd-remove')){ Q.m[k].q = 0; recalc(); close_(); return; }"""))

subs.append((
"""            '</div><span class="nfbd-qnote">' +
            (q === 1 ? '1 machine' : q + ' machines, configured the same') + '</span></div>' +""",
"""            '</div><span class="nfbd-qnote">' +
            (q === 1 ? '1 machine' : q + ' machines, configured the same') + '</span>' +
            /* an explicit way out, because a stepper that reaches zero is not
               discoverable — you have to press minus and hope. This says it. */
            '<button type="button" class="nfbd-remove" data-nfbd-remove>Remove from quote</button>' +
            '</div>' +"""))

subs.append((
"""              '<button type="button" data-nfbd-q="-1" aria-label="One fewer ' + m.name + '">&minus;</button>' +""",
"""              '<button type="button" data-nfbd-q="-1" aria-label="' +
                (q <= 1 ? 'Remove ' + m.name + ' from the quote' : 'One fewer ' + m.name) + '">&minus;</button>' +"""))

# ── 3 · and the delegated selector has to know the new control exists ─────
subs.append((
"""    var t = e.target.closest ? e.target.closest('[data-nfbd-q],[data-nfbd-yrs],[data-nfbd-x],[data-nfbd-close]') : null;""",
"""    /* CAUGHT IN TEST: [data-nfbd-remove] was handled in the body of this
       listener but never added to the selector that decides whether the
       listener runs at all — so the button was inert and the click fell through
       to nothing. Every control in this panel is delegated; adding one means
       adding it in both places. */
    var t = e.target.closest ? e.target.closest('[data-nfbd-q],[data-nfbd-yrs],[data-nfbd-x],[data-nfbd-close],[data-nfbd-remove]') : null;"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = "\n".join([
"/* the way out of a configured machine. Quiet, right-aligned, but present —",
"   a stepper that happens to reach zero is not a control anyone finds. */",
"#nfConsoleWrap .nfbd-remove{",
"  margin-left:auto;background:none;border:0;padding:0;cursor:pointer;",
"  font-family:var(--body,sans-serif);font-size:11.5px;font-weight:500;",
"  color:rgba(255,232,195,.65);border-bottom:1px solid rgba(255,232,195,.3);",
"  transition:color .15s ease,border-color .15s ease;}",
"#nfConsoleWrap .nfbd-remove:hover{color:#F4F2EE;border-color:#F4F2EE;}",
"#nfConsoleWrap .nfbd-remove:focus-visible{outline:2px solid var(--or,#ed3326);outline-offset:3px;}",
])
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("mutual exclusion + zero-quantity exit applied")
