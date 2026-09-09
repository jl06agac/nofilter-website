import io, sys

F = "/Users/alexanderclark/Desktop/NoFilter/Marketing/NoFilter-Website/NoFilter-Website-Master.html"
F = sys.argv[1] if len(sys.argv) > 1 else F

HTML_OLD = '<div id="mcards"></div>'
HTML_NEW = ('<div id="mcards"></div>\n'
            '              <!-- the purchase dossier opens HERE, directly under the machine row,\n'
            '                   exactly as the origin dossier opens under the coffee row. It is a\n'
            '                   sibling of #mcards rather than a child so its width is the row\'s\n'
            '                   width and the two always line up. -->\n'
            '              <div id="nfBuyDoss" aria-hidden="true"></div>')

JS = r'''
/* ══ MODULE C2 · THE PURCHASE DOSSIER ═══════════════════════════════════════
   Alex, 31 Aug: "the draw can open downwards, i.e. exactly like our more
   details for our coffee selection" → "implement this into the master, i want
   to see it with imagery".

   WHAT THIS REPLACES. On a purchase the card's own "What it costs" disclosure
   was carrying five priced rows, four checkboxes and a three-rung servicing
   control inside a 291px column. That is what clipped "2 years" and what he
   called being "super confused as a buyer". The rows are unchanged in kind —
   the same extras, the same ladder, the same money — they simply get the width
   of the row instead of a quarter of it. Block 23 in the sheet hides the tail
   on .is-buy so nothing is stated twice. RENTAL IS COMPLETELY UNTOUCHED.

   IT DRIVES THE SAME STATE. Every control here writes into Q.m[k] and calls
   recalc(), so buyTotal(), compute() and the quote sheet see exactly what they
   saw before. There is no second source of truth and no second price.

   THE MOTION is lifted from openDossier()/closeDossier() in this file — the
   two-phase FLIP, the 150ms beat, the watchdog, and nfScrollTo on both legs. */
(function(){
  var doss = document.getElementById('nfBuyDoss');
  if(!doss || typeof MACHINES === 'undefined') return;
  var morph = null, morphT = null, openK = null;

  /* asset paths are DERIVED from a machine's own img rather than typed, so if
     the CDN prefix ever moves these move with it. m.img is
     '../../_CDN-UPLOAD-SAFE/cafematic-6-w1400.webp'. */
  var ASSET = String((MACHINES[0] && MACHINES[0].img) || '').replace(/[^/]+$/, '');

  /* nfScrollTo — the console's scroller is .nf-focus-sec, NOT the document, so
     a plain window.scrollTo would silently do nothing in the focus deck. This
     is the component's own function, brought across whole. */
  function nfbdScroll(el){
    if(!el) return;
    var fs = document.querySelector('.nf-focus-sec');
    if(fs){
      var t = fs.scrollTop + (el.getBoundingClientRect().top - fs.getBoundingClientRect().top) - 90;
      try{ fs.scrollTo({top:Math.max(0,t), behavior:'smooth'}); }catch(e){ fs.scrollTop = Math.max(0,t); }
    } else {
      try{ window.scrollTo({top:Math.max(0, el.getBoundingClientRect().top + window.scrollY - 90), behavior:'smooth'}); }catch(e){}
    }
  }
  function ensureMorph(){
    if(!morph){
      morph = document.createElement('div');
      morph.className = 'nfbd-morph';     /* parked on <body>, so UNSCOPED — see block 23 */
      document.body.appendChild(morph);
    }
    return morph;
  }
  function mach(k){ for(var i=0;i<MACHINES.length;i++) if(MACHINES[i].k===k) return MACHINES[i]; return null; }

  /* max-height animates between 0 and a MEASURED height. The coffee dossier is
     static once built so it measures once; a configurator changes height on
     every choice, so the pin is re-taken with the transition suppressed. */
  function nfbdSync(){
    if(!openK) return;
    doss.style.transition = 'none';
    doss.style.maxHeight = doss.scrollHeight + 'px';
    void doss.offsetWidth;
    doss.style.transition = '';
  }

  function build(k){
    var m = mach(k); if(!m) return;
    var cfg = Q.m[k], x = buyExtras(), q = Math.max(1, cfg.q || 1);
    var yrs = cfg.svcYrs || 1, on = !!cfg.svc;
    var unit = buyTotal(m, cfg), tot = unit * q;
    /* the rental this is measured against is the SAME commitment (BUY_TERM)
       and the SAME quantity — comparing N machines bought against one machine
       rented is the arithmetic slip this panel exists to avoid making. */
    var rent = machRate(m, BUY_TERM) * BUY_TERM * q;
    var d = rent - tot;
    var gaps = (cfg.cooler ? 0 : 1) + (cfg.svc ? 0 : 1);

    var COVROWS = {
      1:['Two scheduled visits a year','Parts under manufacturer warranty'],
      2:['Parts &amp; breakdown cover','Three scheduled visits a year','Livery wrap included'],
      3:['Parts &amp; breakdown cover','Three scheduled visits a year','Livery wrap included']
    };
    var rung = function(n){
      var t = svcPlanCost(x, n), lit = on && yrs === n;
      return '<button type="button" class="nfbd-cov' + (lit ? ' is-on' : '') +
        '" data-nfbd-yrs="' + n + '" aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (n === 2 ? '<span class="rec">Recommended</span>' : '') +
        '<span class="tick" aria-hidden="true"></span>' +
        '<span class="yr">' + n + (n === 1 ? ' year' : ' years') + '</span>' +
        '<p class="pr">' + money(t) + '</p>' +
        '<span class="pm">' + CUR() + '&middot; ' + money0(t / (12 * n)) + ' a month</span>' +
        '<ul>' + COVROWS[n].map(function(r){ return '<li>' + r + '</li>'; }).join('') + '</ul>' +
      '</button>';
    };
    /* thumbnails. The fridge has no photograph on the CDN yet, so its tile
       says so rather than borrowing a picture of something else. */
    var ex = function(key, name, note, cost, img){
      var lit = !!cfg[key];
      return '<button type="button" class="nfbd-ex' + (lit ? ' is-on' : '') + '" data-nfbd-x="' + key + '"' +
        ' aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (img ? '<span class="nfbd-th"><img src="' + ASSET + img + '" alt="" loading="lazy" onerror="this.style.display=\'none\'"></span>'
             : '<span class="nfbd-th is-todo" aria-hidden="true"></span>') +
        '<span class="txt"><span class="t">' + name + '</span><span class="d">' + note + '</span></span>' +
        '<span class="nfbd-sw" aria-hidden="true"><i></i></span>' +
      '</button>';
    };
    var wrapFree = on && yrs >= 2;

    doss.innerHTML =
    '<div class="nfbd-sheet">' +
      '<button type="button" class="nfbd-close" data-nfbd-close>Close</button>' +
      '<div class="nfbd-row">' +
        '<div class="nfbd-frame"><div class="nfbd-shot">' +
          '<img src="' + m.img + '" alt="' + m.name + ' in NoFilter livery" loading="lazy" onerror="this.style.display=\'none\'">' +
          '<span class="nfbd-shotk">' + m.name + '</span>' +
        '</div></div>' +
        '<div class="nfbd-body">' +
          '<p class="nfbd-eyebrow">Buying outright &middot; ' + m.forWho + '</p>' +
          '<h3 class="nfbd-name">' + m.name + '</h3>' +
          '<div class="nfbd-qrow"><div class="nfbd-qty">' +
              '<button type="button" data-nfbd-q="-1" aria-label="One fewer ' + m.name + '">&minus;</button>' +
              '<b>' + q + '</b>' +
              '<button type="button" data-nfbd-q="1" aria-label="One more ' + m.name + '">+</button>' +
            '</div><span class="nfbd-qnote">' +
            (q === 1 ? '1 machine' : q + ' machines, configured the same') + '</span></div>' +
          '<div><p class="nfbd-sect">Choose how long it is covered' +
            (on ? ' &middot; <button type="button" data-nfbd-yrs="0" style="background:none;border:none;color:inherit;font:inherit;text-decoration:underline;cursor:pointer;padding:0">no cover</button>' : '') +
            '</p><div class="nfbd-covs">' + rung(1) + rung(2) + rung(3) + '</div></div>' +
          '<div><p class="nfbd-sect">Extra hardware</p><div class="nfbd-extras">' +
            /* the note says STANDARD, not just a price — a pre-ticked box with no
               explanation reads as a bundled upsell. This one is pre-ticked
               because a rental includes it and the machine cannot make a
               fresh-milk drink without it, and the tile now says so. */
            ex('cooler','Fresh-milk fridge',
               (cfg.cooler ? 'Standard' : 'Undercounter') + ' &middot; ' + CUR() + money(x.cooler),
               x.cooler, '') +
            ex('wrap','Livery wrap', wrapFree ? 'Free on this plan' : 'Your branding &middot; ' + CUR() + money(x.wrap), 0, 'machine-livery-uwcsea.png') +
            ex('counter','Live impact counter','Cups &amp; funds &middot; ' + CUR() + money(x.counter), x.counter, 'smiirl-counter.jpg') +
          '</div></div>' +
          '<div class="nfbd-buy">' +
            '<div class="nfbd-price"><small>Total purchase price</small>' +
              '<b>' + CUR() + money(tot) + '</b>' +
              (q > 1 ? '<p class="nfbd-per">' + q + ' &times; ' + CUR() + money(unit) + ' each</p>' : '') +
            '</div>' +
            '<button type="button" class="nfbd-done" data-nfbd-close>Done &rarr;</button>' +
            /* the like-for-like rule the card already enforces: while the buyer
               has declined something every rental includes, this is not a
               comparison and must not print a saving. */
            /* the warning NAMES ONLY WHAT IS ACTUALLY MISSING. It used to say
               "the fridge and the servicing plan" whatever the reader had
               chosen, so with the fridge now standard it was telling them they
               lacked a thing sitting ticked on screen. A caveat that misreports
               the configuration teaches the reader to stop believing the rest. */
            '<p class="nfbd-vs">' + (gaps
              ? 'Not like-for-like &mdash; a rental includes ' +
                (!cfg.cooler && !cfg.svc ? 'the fridge and the servicing plan'
                 : !cfg.cooler           ? 'the fresh-milk fridge'
                                         : 'the servicing plan') + '.'
              : (d >= 0
                  ? 'That is <b>' + CUR() + money(d) + ' less</b> than renting the same ' +
                    (q > 1 ? q + ' machines' : 'machine') + ' for ' + BUY_TERM + ' months.'
                  : 'That is <b>' + CUR() + money(-d) + ' more</b> than renting the same ' +
                    (q > 1 ? q + ' machines' : 'machine') + ' for ' + BUY_TERM + ' months.')) +
            '</p>' +
          '</div>' +
        '</div>' +
      '</div>' +
    '</div>';
  }

  /* recalc() repaints the cards; the dossier has to follow the same beat or it
     drifts the moment anything outside it changes (a market switch reprices
     every extra). Exposed for the __paint wrapper installed below. */
  window.__nfBuyDossPaint = function(k){
    if(!openK || (k && k !== openK)) return;
    build(openK); nfbdSync();
  };

  function open_(k){
    var card = document.querySelector('.q-eq-card[data-m="' + k + '"]');
    if(!card) return;
    var reopen = (openK === k);
    openK = k;
    doss.style.transform = ''; doss.style.opacity = '';   /* clear a prior close's transient */
    build(k);
    doss.classList.add('is-open');
    doss.setAttribute('aria-hidden','false');
    if(reopen){ nfbdSync(); return; }                     /* already down — just re-measure */

    doss.classList.add('is-flying','is-morphing');
    doss.style.transition = 'none';
    doss.style.maxHeight = doss.scrollHeight + 'px';
    void doss.offsetWidth;
    var sheet = doss.querySelector('.nfbd-sheet');
    var l = (sheet || doss).getBoundingClientRect();
    var f = card.getBoundingClientRect();

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(reduce){
      doss.classList.remove('is-flying','is-morphing');
      doss.style.transition = '';
      nfbdScroll(doss);
      return;
    }

    var mo = ensureMorph(), clone = card.cloneNode(true);
    clone.style.margin = '0'; clone.style.width = '100%'; clone.style.height = '100%';
    clone.style.transition = 'opacity .16s ease';
    mo.innerHTML = ''; mo.appendChild(clone);
    mo.style.background = getComputedStyle(card).backgroundColor || '#FFFDF9';
    mo.style.borderRadius = '14px';
    mo.style.left = f.left + 'px'; mo.style.top = f.top + 'px';
    mo.style.width = f.width + 'px'; mo.style.height = f.height + 'px';
    mo.style.transition = 'none'; mo.style.display = 'block'; mo.style.opacity = '1';
    void mo.offsetWidth;
    /* ── BUG, 31 Aug: "bad glitch where the machine you select disappears" ──
       This line used to read
           card.style.transition='opacity .1s ease'; card.style.opacity='0';
       copying the coffee dossier, which hides its inline detail card so the
       proxy appears to BE it. On a machine card that is a bad trade. The card
       is a permanent object in a comparison row, its restore lived in exactly
       one place (landed(), behind an `if(openK !== k) return`), and anything
       that interrupted the sequence — a recalc mid-flight, a swallowed
       transitionend, a second click — left a hole in the row with the card's
       space still reserved. That is what Alex saw, and it survived the close
       because close_() could only restore what it could still find.

       The illusion the hide bought is worth about 100ms: the proxy starts
       exactly on top of the card, pixel for pixel, and leaves immediately. Not
       hiding it costs a brief overlap nobody will see, and makes the failure
       mode structurally impossible rather than merely unlikely. Nothing in
       this module writes to a card's opacity any more. */

    var expanded = false, finished = false;
    var landed = function(){
      if(finished) return; finished = true;
      mo.removeEventListener('transitionend', onEnd); clearTimeout(morphT);
      mo.style.display = 'none'; mo.style.opacity = '0'; mo.innerHTML = '';
      if(openK !== k) return;
      doss.classList.remove('is-flying','is-morphing');
      doss.style.transition = '';
      /* 260ms after landing, not on click. The descent IS the wayfinding: you
         watch the card travel to where the panel will be. Scrolling while it is
         still in flight moves the destination and the two motions fight. */
      setTimeout(function(){ if(openK === k) nfbdScroll(doss); }, 260);
    };
    var expand = function(){
      if(expanded) return; expanded = true;
      clone.style.opacity = '0';
      setTimeout(function(){
        mo.style.transition = 'left .52s cubic-bezier(.4,0,.15,1), width .52s cubic-bezier(.4,0,.15,1), ' +
                              'height .52s cubic-bezier(.4,0,.15,1), border-radius .52s ease';
        mo.style.left = l.left + 'px'; mo.style.width = l.width + 'px';
        mo.style.height = l.height + 'px'; mo.style.borderRadius = '18px';
      }, 150);
    };
    var onEnd = function(e){
      if(e.propertyName === 'top' && !expanded) expand();
      else if(expanded && (e.propertyName === 'width' || e.propertyName === 'height')) landed();
    };
    mo.addEventListener('transitionend', onEnd);
    requestAnimationFrame(function(){ requestAnimationFrame(function(){
      mo.style.transition = 'top .38s cubic-bezier(.45,0,.35,1)';
      mo.style.top = l.top + 'px';
    }); });
    /* the component's own watchdog: a swallowed transitionend must not strand
       a proxy on screen */
    clearTimeout(morphT);
    morphT = setTimeout(function(){ if(!expanded) expand(); setTimeout(landed, 760); }, 1800);

    /* THE MACHINE ROW STAYS PUT. The coffee dossier pulls its tile row out of
       flow on landing — but its own code guards that with
         !document.querySelector('.nf-focus-sec')
       i.e. it does NOT do it inside a focus deck. The console IS one, and the
       row is the comparison this step exists for, so it stays. */
  }

  function close_(){
    if(!openK) return;
    openK = null;
    clearTimeout(morphT);
    if(morph){ morph.style.display = 'none'; morph.style.opacity = '0'; morph.innerHTML = ''; }
    doss.setAttribute('aria-hidden','true');
    doss.classList.add('is-morphing');

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(reduce){
      doss.style.transition = 'none'; doss.style.maxHeight = '0px';
      doss.classList.remove('is-open');
      nfbdScroll(document.getElementById('mcards'));
      return;
    }
    /* CLOSE IS THE REVERSE OF OPEN and it travels too: the panel contracts UP
       toward the row while the view returns to it, so the row you are handed
       back to is what you are looking at when the panel shrinks into it. */
    doss.style.transformOrigin = 'top center';
    doss.style.transition = 'transform .48s cubic-bezier(.5,0,.15,1), opacity .38s ease';
    doss.style.transform = 'translateY(-22px) scale(.42)';
    doss.style.opacity = '0';
    setTimeout(function(){ nfbdScroll(document.getElementById('mcards')); }, 80);
    setTimeout(function(){
      if(openK) return;                                  /* reopened mid-close */
      doss.style.transition = 'max-height .3s ease';
      doss.style.maxHeight = '0px';
      doss.classList.remove('is-open');
    }, 380);
    setTimeout(function(){
      if(openK) return;
      doss.style.transition = 'none'; doss.style.transform = ''; doss.style.opacity = '';
    }, 1080);
  }

  /* ── controls, all delegated: build() rewrites the panel on every change ── */
  doss.addEventListener('click', function(e){
    var t = e.target.closest ? e.target.closest('[data-nfbd-q],[data-nfbd-yrs],[data-nfbd-x],[data-nfbd-close]') : null;
    if(!t || !openK) return;
    var k = openK, cfg = Q.m[k];
    if(t.hasAttribute('data-nfbd-close')){ close_(); return; }
    if(t.hasAttribute('data-nfbd-q')){
      cfg.q = Math.max(1, Math.min(20, cfg.q + parseInt(t.getAttribute('data-nfbd-q'), 10)));
    } else if(t.hasAttribute('data-nfbd-yrs')){
      var n = parseInt(t.getAttribute('data-nfbd-yrs'), 10);
      /* 0 is the "no cover" link in the section header. Declining has to stay
         reachable: the quote sheet counts it as a like-for-like gap and the
         saving line refuses to appear while one is open. */
      if(n === 0){ cfg.svc = false; }
      else {
        cfg.svc = true; cfg.svcYrs = n;
        /* A 2- AND 3-YEAR RUNG SAYS "LIVERY WRAP INCLUDED" ON ITS FACE, AND
           wrapCost() ALREADY CHARGES ZERO FOR IT AT THOSE LENGTHS. But the
           quote sheet lists what cfg.wrap says, so leaving the flag off meant
           the panel promising a wrap the quote would not mention and we would
           never ship. Caught in the interaction test. Turning it on costs
           nothing (wrapCost is 0 here) and makes the promise real; the buyer
           can still switch it off if they do not want branding on the machine. */
        if(n >= 2) cfg.wrap = true;
      }
    } else {
      cfg[t.getAttribute('data-nfbd-x')] = !cfg[t.getAttribute('data-nfbd-x')];
    }
    recalc();               /* single source of truth; __paint wrapper redraws this panel */
  });
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape' && openK) close_(); });
  window.addEventListener('resize', nfbdSync);

  /* OPENING. On a purchase, adding a unit opens the dossier — "once the user
     has clicked + 1 2 3 or whatever number". Bound on #mcards rather than on
     the cards so it runs AFTER each card's own [data-q] handler has already
     updated the count; this listener only reacts to the result. */
  var host = document.getElementById('mcards');
  if(host) host.addEventListener('click', function(e){
    /* CAPTURE PHASE, AND IT HAS TO BE — the second half of the disappearing-card
       bug. This listener used to sit on the bubble phase, which runs AFTER the
       card's own [data-q] handler. That handler calls recalc(), and __paint
       rewrites [data-addzero]'s innerHTML — so if the reader happened to press
       the PRICE half of the Add pill, e.target was destroyed before this ran,
       e.target.closest() returned null on the orphan, and pressing Add did
       nothing at all. Pressing the word "Add" worked, because .mx-cta is not
       inside the rewritten span. A control that works or not depending on which
       half of it you hit is the same fault this file has already logged twice:
       "__paint rewrites the rows on every repaint".

       So the TARGET is resolved here, while the DOM is still intact, and the
       ACTION is deferred to the next frame, by which time the card's handler
       has updated the count this decision depends on. */
    var t = e.target.closest ? e.target.closest('[data-q],[data-mode]') : null;
    if(!t) return;
    var card = t.closest('.q-eq-card'); if(!card) return;
    var k = card.getAttribute('data-m'); if(!k || !Q.m[k]) return;
    var isMode = t.hasAttribute('data-mode');
    requestAnimationFrame(function(){
      if(!Q.m[k]) return;
      /* leaving purchase must CLOSE the panel — it is a purchase-only surface,
         and the card's rental tail comes back underneath it. Caught in the
         stress run: switching back to Rental left the dark sheet sitting under
         a row of rental cards, describing a configuration no longer on offer. */
      if(Q.m[k].mode !== 'purchase' || Q.m[k].q < 1){ if(openK === k) close_(); return; }
      /* switching INTO purchase opens nothing on its own — the reader has not
         asked for a machine yet, and a panel that appears unbidden is the
         clutter this whole pass has been removing */
      if(isMode) return;
      open_(k);
    });
  }, true);

  /* keep the panel in step with recalc() without editing recalc() itself */
  MACHINES.forEach(function(m){
    var card = document.querySelector('.q-eq-card[data-m="' + m.k + '"]');
    if(!card || !card.__paint || card.__nfbdWrapped) return;
    card.__nfbdWrapped = true;
    var base = card.__paint;
    card.__paint = function(){
      base.apply(this, arguments);
      /* heals a card left invisible by the earlier build of this module, which
         wrote opacity:0 inline and could fail to clear it. Nothing writes it
         any more, so this only ever undoes damage. */
      if(this.style.opacity !== '') this.style.opacity = '';
      window.__nfBuyDossPaint(m.k);
    };
  });

  window.__nfCloseBuyDoss = close_;
})();

'''

src = io.open(F, encoding="utf-8").read()
if "nfBuyDoss" in src and "MODULE C2" in src:
    print("ALREADY PATCHED — js skipped"); sys.exit(0)

assert src.count(HTML_OLD) == 1, "mcards anchor not unique: %d" % src.count(HTML_OLD)
src = src.replace(HTML_OLD, HTML_NEW)

ANCHOR = "\nfunction compute(){"
assert src.count(ANCHOR) == 1, "compute anchor not unique: %d" % src.count(ANCHOR)
src = src.replace(ANCHOR, "\n" + JS + ANCHOR)

io.open(F, "w", encoding="utf-8").write(src)
print("html + js inserted")
