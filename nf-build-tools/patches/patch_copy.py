import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()
subs = []

# ── 1 · the three columns say what an office manager needs, in her words ───
subs.append((
"""    var COVROWS = {
      0:['Parts and labour carried by the maker, year one',
         'Servicing can be added separately'],
      2:['Year-one servicing included',
         (comp ? 'Every part and breakdown insured' : 'Serviced and maintained') + ' from month 13',
         (comp ? 'Four scheduled visits a year' : 'Two scheduled visits a year')],
      3:['Year-one servicing included',
         (comp ? 'Every part and breakdown insured' : 'Serviced and maintained') + ' from month 13',
         (comp ? 'Four scheduled visits a year' : 'Two scheduled visits a year'),
         'Wrap + impact counter free']
    };""",
"""    /* ── 1 Sep 2026 · THE COLUMNS ANSWER THE THREE QUESTIONS ─────────────────
       Alex: "An office manager reading this needs to know three things
       instantly: What is included for free? How long am I protected if it
       breaks? How often does a technician come to the office?"

       The old copy answered none of them without arithmetic. It said "from
       month 13", which asks the reader to convert a contract boundary into a
       date; and it said "Nothing" over the free column, which is the worst
       word on the page — year one carries a full manufacturer warranty, so
       "Nothing" both frightens the buyer and understates what she has.

       Each column now leads with duration, follows with visit frequency, and
       ends with what is thrown in. Two things did NOT survive contact with the
       facts, and they matter more than the wording:

       · VISIT COUNT STAYS BRANCHED. Four visits a year is the Boncafé
         Comprehensive schedule (C5/C6/C8). A C2 sits on Bi-Annual, which is
         two. Printing "4 visits" across all four models would be a promise we
         have not bought for the C2.

       · "PRIORITY TECHNICIAN DISPATCH" IS NOT WRITTEN HERE. It was asked for
         and there is nothing behind it: the signed agreement has no response-
         time SLA. What it does have is §4.2, two pooled operator sessions per
         Comprehensive machine per year, which we already pay for and have never
         put on the card. That is real, so that is what the third bullet says.
         If a dispatch promise is wanted it has to be bought from Boncafé and
         priced first — see RATE-CARD. */
    var visits = comp ? 'Four scheduled maintenance visits a year'
                      : 'Two scheduled maintenance visits a year';
    /* "covered for N full years" counts from day one, which is what the plan
       now sells — but year one is carried by the MAKER, not by us. The free
       column states that plainly so the two columns read against each other,
       and RATE-CARD carries the flag about who pays if a year-one claim is
       refused. */
    var COVROWS = {
      0:['1-year manufacturer warranty &mdash; parts and labour',
         'On-site repair of factory defects',
         'Routine servicing and cleaning sold separately'],
      2:[(comp ? 'Breakdowns and parts covered for 2 full years'
                : 'Serviced and maintained for 2 full years'),
         visits,
         (comp ? 'Two operator training sessions a year' : 'Year-one servicing included')],
      3:[(comp ? 'Breakdowns and parts covered for 3 full years'
                : 'Serviced and maintained for 3 full years'),
         visits,
         (comp ? 'Two operator training sessions a year' : 'Year-one servicing included'),
         'Free: livery wrap + live impact counter']
    };"""))

# ── 2 · the names, the price words, and a monthly the reader can hold ──────
subs.append((
"""      /* the sub-line is PER YEAR OF COVER, not per month. Per month was the right
         unit while year one was inside the plan and the ladder could get cheaper
         monthly as it lengthened; priced on real cover it cannot — two years of
         cover is genuinely more money than one. Per covered year restores an
         honest discount that runs the right way: 2,000 then 1,800. */
      var covYears = n - 1;                    /* cover to 24 mo = 1 year, to 36 = 2 */
      return '<button type="button" class="nfbd-cov' + (lit ? ' is-on' : '') + (none ? ' is-none' : '') +
        '" data-nfbd-yrs="' + n + '" aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (n === 3 ? '<span class="rec">Recommended</span>' : '') +
        '<span class="tick" aria-hidden="true"></span>' +
        '<span class="yr">' + (none ? 'No coverage' : (n * 12) + ' months coverage') + '</span>' +
        '<p class="pr">' + (none ? 'Nothing' : money(t)) + '</p>' +
        '<span class="pm">' + (none
          ? 'Year one under manufacturer warranty'
          : CUR() + '&middot; ' + money0(t / n) + ' a year') + '</span>' +""",
"""      /* PER MONTH, and hedged with "about". A lump of 5,150 is the number they
         sign for and it stays the headline; 143 a month is the number they can
         hold against a coffee budget. The per-YEAR unit this replaces had a
         reading fault I flagged and it is worth recording: because year one is
         cheap and now sits inside both plans, the longer plan divides to a
         BIGGER per-period figure (C6: 1,475 a year at 24 months, 1,717 at 36),
         so a reader scanning two numbers saw a penalty for committing longer.
         Per month it is 123 against 143 — the same direction, smaller
         absolute gap, and in a unit nobody mistakes for a discount claim. The
         real saving on the third year is the 2,000 of hardware, which is why
         that column's last bullet names it. */
      var NAMES = { 0:'Standard factory warranty', 2:'2-year total care', 3:'3-year complete care' };
      return '<button type="button" class="nfbd-cov' + (lit ? ' is-on' : '') + (none ? ' is-none' : '') +
        '" data-nfbd-yrs="' + n + '" aria-pressed="' + (lit ? 'true' : 'false') + '">' +
        (n === 3 ? '<span class="rec">Recommended</span>' : '') +
        '<span class="tick" aria-hidden="true"></span>' +
        '<span class="yr">' + NAMES[n] + '</span>' +
        '<p class="pr">' + (none ? 'Included' : money(t)) + '</p>' +
        '<span class="pm">' + (none
          ? 'Nothing to pay'
          : CUR() + '&middot; about ' + money0(t / (n * 12)) + ' a month') + '</span>' +"""))

# ── 3 · the section heading names the decision, not the axis ───────────────
subs.append((
"""<p class="nfbd-sect">Choose how long it is covered</p>""",
"""<p class="nfbd-sect">Select care &amp; servicing plan</p>"""))

# ── 4 · the add-on keeps its space when it is not offered ──────────────────
subs.append((
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
            '</button>') + '</div>' +""",
"""            /* 1 Sep — NOT OFFERED once a plan is taken, because a plan already
               contains it: leaving a paid toggle on screen for something already
               bought is how a buyer ends up paying twice and blaming the quote.

               1 Sep (2) — but it is HIDDEN, not removed. Alex: "all of these
               should sit exactly the same and not move, across no coverage,
               24-36 months ... perhaps the standard sizing of the 24 & 36
               coverage imagery and sizing should retain nocoverage's
               dimensions."
               Right, and it is the same fault as the price pill an hour ago:
               taking an element out of layout makes everything below it jump,
               and here "everything below it" includes the machine photograph,
               which is the largest object on the panel. Reserving the row keeps
               the panel one fixed height across all three states, so the photo,
               the extras and the total never move. visibility:hidden rather
               than a min-height for the same reason as the pill — the row
               measures itself, so it survives a font change. */
            '<button type="button" class="nfbd-svc1' + (cfg.svc1 ? ' is-on' : '') +
              (on ? ' is-off" tabindex="-1" aria-hidden="true' : '') +
              '" data-nfbd-x="svc1" aria-pressed="' + (cfg.svc1 ? 'true' : 'false') + '">' +
              '<span class="nfbd-sw" aria-hidden="true"><i></i></span>' +
              '<span class="t">Add Year 1 maintenance package</span>' +
              '<span class="d">Two preventative servicing visits during your factory-warranty year</span>' +
              '<span class="p">' + CUR() + money(x.svc1) + '</span>' +
            '</button>' + '</div>' +"""))

for old, new in subs:
    assert src.count(old) == 1, "anchor not unique (%d): %s" % (src.count(old), old[:70])
    src = src.replace(old, new)

CSS = "\n".join([
"/* the add-on row when a plan already contains it: present for layout, gone",
"   for every other purpose — unpainted, unclickable, out of the tab order and",
"   out of the accessibility tree (aria-hidden + tabindex on the element). */",
"#nfConsoleWrap .nfbd-svc1.is-off{visibility:hidden;pointer-events:none;}",
])
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("plan copy + reserved add-on row")
