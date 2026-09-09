import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── A · zero-padded step numbers ──────────────────────────────────────────
subs.append((
"""          '<span class="nfbd-stepno">Step ' + n + '</span>' +""",
"""          '<span class="nfbd-stepno">Step 0' + n + '</span>' +"""))

# ── B · step titles per the hand-off ──────────────────────────────────────
subs.append((
"""          '<div>' + step(1, 'Select care &amp; servicing plan', 'Required',""",
"""          '<div>' + step(1, 'Select servicing &amp; care plan', 'Required',"""))

# ── C+D · the free tier: Standard care ────────────────────────────────────
subs.append((
"""      var NAMES = { 0:'Standard factory warranty', 2:'2-year total care', 3:'3-year complete care' };""",
"""      /* 1 Sep · Alex's hand-off spec. "Standard care" over "Standard factory
         warranty" — shorter, and the tier now carries a calibration session so
         it is genuinely care, not only the maker's paper. */
      var NAMES = { 0:'Standard care', 2:'2-year total care', 3:'3-year complete care' };"""))

subs.append((
"""        '<span class="pm">' + (none
          ? 'Nothing to pay'
          : CUR() + '&middot; about ' + money0(t / (n * 12)) + ' a month') + '</span>' +""",
"""        /* 1 Sep (micro-edits) — "The bold label carries the state on its
           own." The sub-line goes, the LINE BOX stays: a ghost span holds the
           row so the divider and bullets stay level with the paid columns. */
        (none
          ? '<span class="pm is-ghost" aria-hidden="true">&nbsp;</span>'
          : '<span class="pm">' + CUR() + '&middot; about ' + money0(t / (n * 12)) + ' a month</span>') +"""))

subs.append((
"""    var COVROWS = {
      0:['1-year manufacturer warranty &mdash; parts and labour',
         'On-site repair of factory defects',
         'Routine servicing and cleaning sold separately'],
      2:[(comp ? 'Breakdowns and parts covered for 2 full years'
                : 'Serviced and maintained for 2 full years'),
         visits,
         calib],
      3:[(comp ? 'Breakdowns and parts covered for 3 full years'
                : 'Serviced and maintained for 3 full years'),
         visits,
         calib,
         'Free: co-branded wrap + live impact counter']
    };""",
"""    /* 1 Sep · the hand-off deck's copy, with the one thing it glossed kept:
       visit counts and the parts promise stay branched by model, because the
       C2 sits on Boncafé Bi-Annual and "full breakdown & parts cover" is a
       promise we have only bought for the Comprehensive machines. The spec
       was written for the C6, where the branch resolves to its wording
       exactly. The free tier now STATES a calibration session — universal
       calibration was already Alex's rule, so this prints an existing promise
       rather than making a new one. */
    var COVROWS = {
      0:['1-year coverage on parts &amp; labour',
         '1 on-site coffee calibration session',
         'Routine servicing sold separately'],
      2:[(comp ? 'Full breakdown &amp; parts cover for 2 full years'
                : 'Serviced and maintained for 2 full years'),
         visits,
         calib],
      3:[(comp ? 'Full breakdown &amp; parts cover for 3 full years'
                : 'Serviced and maintained for 3 full years'),
         visits,
         calib,
         'Free: co-branded wrap + live impact screen']
    };"""))

subs.append((
"""    var calib = '2 on-site coffee calibration sessions';""",
"""    var calib = '2 on-site coffee calibration sessions a year';"""))

# numerals, not words — the calibration bullets say "2" and "1"; a "Four"
# beside them is two voices in one list. (Done here, at the end of the chain,
# because patch_polish anchors on the worded version.)
subs.append((
"""    var visits = comp ? 'Four scheduled maintenance visits a year'
                      : 'Two scheduled maintenance visits a year';""",
"""    var visits = comp ? '4 scheduled maintenance visits a year'
                      : '2 scheduled maintenance visits a year';"""))

# ── F+G · extras: thumbnails gone, spec copy in ───────────────────────────
subs.append((
"""        (img ? '<span class="nfbd-th"><img src="' + ASSET + img + '" alt="" loading="lazy" onerror="this.style.display=\\'none\\'"></span>'
             : '<span class="nfbd-th is-todo" aria-hidden="true"></span>') +""",
"""        /* 1 Sep · THUMBNAILS REMOVED, per the hand-off: "eliminates awkward
           multi-line text wrapping and keeps titles on a single row." Also
           retires the [PHOTO] placeholder the fridge has carried since the CDN
           never got its picture, and hands the description the 56px the thumb
           and its gap were holding. */"""))

subs.append((
"""            ex('cooler','Countertop milk fridge',
               'Sits beside the machine',
               'Standard &middot; ' + CUR() + money(x.cooler), false,
               x.cooler, '') +""",
"""            ex('cooler','Countertop Milk Fridge',
               'Direct-fit 6L cooler sitting alongside the unit',
               CUR() + money(x.cooler), false,
               x.cooler, '') +"""))

subs.append((
"""            ex('wrap','Co-branded machine wrap',
               'Our artwork, your logo',
               CUR() + money(x.wrap), wrapFree,
               0, 'machine-livery-uwcsea.png') +""",
"""            ex('wrap','Co-Branded Wrap',
               'Signature NoFilter artwork with your logo',
               CUR() + money(x.wrap), wrapFree,
               0, '') +"""))

subs.append((
"""            ex('counter','Live impact counter',
               'Cups and funds, on screen',
               CUR() + money(x.counter), wrapFree,""",
"""            ex('counter','Live Impact Screen',
               'Displays real-time conservation data on screen',
               CUR() + money(x.counter), wrapFree,"""))

# ── H · the pill says INCLUDED ────────────────────────────────────────────
subs.append((
"""            (free ? '<span class="nfbd-inc">Included with plan</span>' : price) +""",
"""            (free ? '<span class="nfbd-inc">Included</span>' : price) +"""))

# step-2 helper line follows the new names
subs.append((
"""                          'Countertop milk fridge, co-branded machine wrap, live impact screen.') +""",
"""                          'Countertop milk fridge, co-branded wrap, live impact screen.') +"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = r'''
/* ── 41 · EXTRAS WITHOUT THUMBNAILS ───────────────────────────────────────
   The tile is text + switch + price now. The description gets the full column
   (two reserved lines, so the spec's longer sentences fit without any tile
   changing height), and the title holds one line at every width the grid
   reaches — measured with the longest name at 1.3x letter-spacing. */
#nfConsoleWrap .nfbd-ex{padding:11px 13px;}
#nfConsoleWrap .nfbd-ex .d{-webkit-line-clamp:2;min-height:2.6em;padding-right:16px;}
#nfConsoleWrap .nfbd-cov .pm.is-ghost{visibility:hidden;}
#nfConsoleWrap .nfbd-ex .hd .t{min-height:0;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis;}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("hand-off spec applied")
