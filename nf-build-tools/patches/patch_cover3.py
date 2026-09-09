import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 5 · the plan covers from DAY ONE, so it carries year-one servicing ────
subs.append((
"""function svcPlanCost(m, yrs){
  var y = Math.max(2, Math.min(3, yrs | 0));
  return coverRate(m) * (y - 1);
}""",
"""/* ── 1 Sep 2026 · A PLAN COVERS FROM DAY ONE ──────────────────────────────
   Alex: "me selecting the cover to 24 months only adds the 2200 and not 2 years
   insurance servicing etc" — and, in the same breath, "the moment the 24 month
   coverage is selected the 'add year one servicing' option should disappear".

   Both say the same thing: "24 months coverage" has to mean MONTHS 1 TO 24. It
   meant months 13 to 24, because the risk-based build priced only the years
   NoFilter actually insures — which is correct arithmetic and the wrong product.
   A buyer reading "24 months coverage" beside 2,200 is being told they have two
   covered years; they have one, and the other is a separate toggle four rows
   down that they have to find and add themselves.

   So the plan is now the whole period: year-one servicing PLUS the insured
   years. The money is the straight sum of the two things it contains — nothing
   invented, and it still adds up in public:

       C6, 24 months = 750 (year-one servicing) + 2,200 (year 2 insured) = 2,950
       C6, 36 months = 750 + 2,200 + 2,200                               = 5,150

   Year one is still not INSURED by us — the manufacturer carries parts and
   labour, and the No-coverage column says so. What the plan adds in year one is
   the two maintenance visits, which is the only thing missing. */
function svcPlanCost(m, yrs){
  var y = Math.max(2, Math.min(3, yrs | 0));
  var x = buyExtras();
  return (x.svc1 || 0) + coverRate(m) * (y - 1);
}"""))

# and buyTotal must not charge year-one servicing twice
subs.append((
"""       + (cfg.svc1    ? x.svc1               : 0)   /* year-one servicing, optional */
       + (cfg.svc     ? svcPlanCost(m, yrs)  : 0)   /* cover, from month 13 */""",
"""       /* a plan already contains year-one servicing (see svcPlanCost), so the
          standalone charge only applies when no plan is taken. Adding both was
          the first thing this refactor got wrong. */
       + (cfg.svc ? svcPlanCost(m, yrs) : (cfg.svc1 ? x.svc1 : 0))"""))

subs.append((
"""      var svc  = s.svc     ? svcPlanCost(m, yrs) : 0;
      var svc1 = s.svc1    ? x.svc1              : 0;""",
"""      var svc  = s.svc     ? svcPlanCost(m, yrs) : 0;
      var svc1 = (!s.svc && s.svc1) ? x.svc1      : 0;"""))

# ── 2 · the names Alex asked for ──────────────────────────────────────────
# ── 3 · the warranty line moves INTO the no-coverage column ───────────────
subs.append((
"""    var COVROWS = {
      0:['Nothing to pay after the machine','Warranty carries parts and labour in year one'],
      2:[(comp ? 'Every part and breakdown insured' : 'Serviced and maintained') + ', from month 13',
         (comp ? 'Four scheduled visits a year' : 'Two scheduled visits a year')],
      3:[(comp ? 'Every part and breakdown insured' : 'Serviced and maintained') + ', from month 13',
         (comp ? 'Four scheduled visits a year' : 'Two scheduled visits a year'),
         'Wrap + impact counter free']
    };""",
"""    /* 1 Sep — the warranty sentence lives IN the no-coverage column now, not on
       a line floating above the group. Alex: "No Coverage should include the
       Year one is under manufacturer warranty rather than have that wording
       outside". It was a caption for the whole group, which made it read as a
       condition of all three rather than as the thing the free column IS. */
    var COVROWS = {
      0:['Parts and labour carried by the maker, year one',
         'Servicing can be added separately'],
      2:['Year-one servicing included',
         (comp ? 'Every part and breakdown insured' : 'Serviced and maintained') + ' from month 13',
         (comp ? 'Four scheduled visits a year' : 'Two scheduled visits a year')],
      3:['Year-one servicing included',
         (comp ? 'Every part and breakdown insured' : 'Serviced and maintained') + ' from month 13',
         (comp ? 'Four scheduled visits a year' : 'Two scheduled visits a year'),
         'Wrap + impact counter free']
    };"""))

subs.append((
"""        '<span class="yr">' + (none ? 'No cover' : 'Cover to ' + (n * 12) + ' months') + '</span>' +
        '<p class="pr">' + (none ? 'Nothing' : money(t)) + '</p>' +
        '<span class="pm">' + (none ? 'Warranty only' : CUR() + '&middot; ' + money0(t / covYears) + ' a year') + '</span>' +""",
"""        '<span class="yr">' + (none ? 'No coverage' : (n * 12) + ' months coverage') + '</span>' +
        '<p class="pr">' + (none ? 'Nothing' : money(t)) + '</p>' +
        '<span class="pm">' + (none
          ? 'Year one under manufacturer warranty'
          : CUR() + '&middot; ' + money0(t / n) + ' a year') + '</span>' +"""))

# ── 4 · the year-one toggle disappears once a plan is taken ───────────────
subs.append((
"""            '<button type="button" class="nfbd-svc1' + (cfg.svc1 ? ' is-on' : '') +
              '" data-nfbd-x="svc1" aria-pressed="' + (cfg.svc1 ? 'true' : 'false') + '">' +
              '<span class="nfbd-sw" aria-hidden="true"><i></i></span>' +
              '<span class="t">Add year-one servicing</span>' +
              '<span class="d">Two visits, in the year the warranty covers the parts</span>' +
              '<span class="p">' + CUR() + money(x.svc1) + '</span>' +
            '</button></div>' +""",
"""            /* 1 Sep — GONE the moment a plan is taken, because a plan contains
               it. Alex asked for exactly this, and it is also the only way the
               panel stays honest: leaving a paid toggle on screen for something
               already bought is how a buyer ends up paying twice and blaming
               the quote. */
            (on ? '' :
            '<button type="button" class="nfbd-svc1' + (cfg.svc1 ? ' is-on' : '') +
              '" data-nfbd-x="svc1" aria-pressed="' + (cfg.svc1 ? 'true' : 'false') + '">' +
              '<span class="nfbd-sw" aria-hidden="true"><i></i></span>' +
              '<span class="t">Add year-one servicing</span>' +
              '<span class="d">Two visits, in the year the warranty covers the parts</span>' +
              '<span class="p">' + CUR() + money(x.svc1) + '</span>' +
            '</button>') + '</div>' +"""))

# and the caption above the group goes with it
subs.append((
"""            '<span class="nfbd-always">Year one is under manufacturer warranty &mdash; cover takes over from month 13</span>' +""",
"""            /* the warranty caption moved into the No-coverage column — see COVROWS */"""))

# ── 1 · the rent-vs-buy comparison goes entirely ──────────────────────────
subs.append((
"""            '<p class="nfbd-vs">' + (gaps""",
"""            /* ── 1 Sep · THE RENT-VS-BUY LINE IS REMOVED ────────────────────
               Alex: "i think we remove this comparison wording all together."
               Right, and it had stopped earning its place. Once the NPV work
               showed buying is not actually cheaper than renting at either
               horizon, a line claiming a saving was either wrong or, when it
               flipped to the not-like-for-like warning, an apology printed under
               the price at the exact moment the reader is deciding. Neither is
               worth the space. The buy-versus-rent case belongs in a
               conversation, not stapled to a total.
               The block is kept, disabled, because the arithmetic behind it
               (gaps, d, rent) is still correct and re-enabling it is one line if
               a future version wants it back. */
            '' + (false ? (gaps"""))

subs.append((
"""                  : 'That is <b>' + CUR() + money(-d) + ' more</b> than renting the same ' +
                    (q > 1 ? q + ' machines' : 'machine') + ' for ' + BUY_TERM + ' months.')) +
            '</p>' +""",
"""                  : 'That is <b>' + CUR() + money(-d) + ' more</b> than renting the same ' +
                    (q > 1 ? q + ' machines' : 'machine') + ' for ' + BUY_TERM + ' months.')) : '') +"""))

# ── the card's own hidden include-list, kept truthful ─────────────────────
subs.append((
"""        { k:'svc',     nm:'Annual servicing plan',
          sub:(isBuy
                ? (yrs === 1 ? '1 year &middot; 2 visits, under warranty'
                             : yrs + ' years &middot; 3 visits/yr + parts')
                : yrs + (yrs === 1 ? ' year' : ' years') + ' &middot; parts &amp; labour'),
          buy:isBuy ? svcPlanCost(m, yrs) : x.svcYr * yrs },""",
"""        /* 1 Sep — this list is hidden on a purchase (block 23), but it was still
           describing a product that no longer exists: a one-year rung that was
           withdrawn, "3 visits/yr" where the panel says four, and "N years" where
           the panel now sells months of coverage. Dead code that contradicts the
           live panel is one unhide away from being a pricing dispute. */
        { k:'svc',     nm:(isBuy ? 'Coverage plan' : 'Annual servicing plan'),
          sub:(isBuy
                ? (yrs * 12) + ' months &middot; from day one'
                : yrs + (yrs === 1 ? ' year' : ' years') + ' &middot; parts &amp; labour'),
          buy:isBuy ? svcPlanCost(m, yrs) : x.svcYr * yrs },"""))

subs.append((
"""          sub:(isBuy && cfgm.svc && (cfgm.svcYrs || 1) >= 2)
                ? 'free on a 2-year plan' : 'your branding on it',""",
"""          /* the reward moved to the top rung (see wrapCost); this rider stayed
             behind at >= 2 and announced a discount the total was not giving. */
          sub:(isBuy && cfgm.svc && (cfgm.svcYrs || 2) >= 3)
                ? 'free on 36 months coverage' : 'your branding on it',"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("day-one cover + relabels + comparison removed")
