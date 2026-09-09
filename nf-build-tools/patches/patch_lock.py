import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

# ── 60 · THE LOCK-IN PASS ─────────────────────────────────────────────────
# Alex's review notes on step 4. Three changes, one of them qualified.

# ── 1 · the servicing line, in his words ──────────────────────────────────
# "Revert this to the agreed clean B2B copy: Scheduled maintenance every 4
# months · Parts and labor included."
#
# Taken, for the case where servicing IS on the quote. The declined case keeps
# its own line, because his own rule ("only there if they tally with the rules")
# and this copy collide head-on there: the VALUE on that row reads "NOT INCLUDED
# — plan declined", and printing a maintenance schedule beside it would put a
# contradiction on one line of a document a client signs. So the schedule
# appears wherever there is a schedule, and nowhere else.
#
# Spelling flagged rather than argued: the file is British throughout — 13
# "labour", 124 "colour", 6 "customise", zero US spellings — so "labor" here is
# the only Americanism in the document. His copy is used verbatim; the
# inconsistency is his to keep or drop.
old = """    setv('#qFleetSub', (buy && !rent && !svcBought)
        ? 'Sold separately · no servicing plan taken on this quote'
        : (buy && !rent)
          ? 'Per the servicing plan itemised above · parts and labour included'
          : 'Twice-yearly in years 1–2, every four months in year 3 · parts and labour included');"""
new = """    setv('#qFleetSub', (buy && !rent && !svcBought)
        ? 'Sold separately · no servicing plan taken on this quote'
        : 'Scheduled maintenance every 4 months · Parts and labor included');"""
assert src.count(old) == 1, "fleet sub anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

# ── 2 · one capitalisation for every tag in the column ────────────────────
# "the top right badge reads 1 × included (lowercase), whereas all other items
# read Included (Title Case)." Every branch is brought into line, not just the
# one he saw — the same function writes six other variants that would have
# drifted the moment a different combination was picked.
subs = [
("""    var cool = $('#qCoolerLine');
    if(cool) cool.textContent = !units ? '—'
      : buy && !rent ? (coolBought ? coolBought + ' × charged above' : 'not taken')
      : mixed ? (rent + ' × included · ' + coolBought + ' × charged above')
      : units + ' × included';""",
 """    var cool = $('#qCoolerLine');
    if(cool) cool.textContent = !units ? '—'
      : buy && !rent ? (coolBought ? coolBought + ' × Charged above' : 'Not taken')
      : mixed ? (rent + ' × Included · ' + coolBought + ' charged above')
      : units + ' × Included';"""),
("""    setv('#qTabletVal', !units ? '1 × included'
      : buy && !rent ? 'included with the cooler & servicing plan'
      : mixed ? rent + ' × included · purchased units per the block above'
      : units + ' × included');""",
 """    setv('#qTabletVal', !units ? '1 × Included'
      : buy && !rent ? 'Included with the cooler & servicing plan'
      : mixed ? rent + ' × Included · purchased units per the block above'
      : units + ' × Included');"""),
]
for old, new in subs:
    assert src.count(old) == 1, "tag anchor not unique (%d): %s" % (src.count(old), old[:60])
    src = src.replace(old, new)

# ── 3 · the conversion, rounded ───────────────────────────────────────────
# "rounding to 55 cups/kg keeps the math human and scannable." The arithmetic
# behind every figure still runs on 1000/18 = 55.555…; only the label rounds,
# so nothing on the page is computed from the rounded number.
old = """  set('qTopUpSub', '+' + topCup.toFixed(1) + '\\u00a2/cup top-up · '
      + CUPS_KG.toFixed(1) + ' cups/kg conversion');"""
new = """  /* label only — every figure on this page is still computed from 1000/18.
     FLOOR, not round: 1000/18 is 55.56, which rounds UP to 56 and would state a
     yield of one more cup than a kilo gives. 55 whole 18g doses is both the
     number Alex asked for and the true one. */
  set('qTopUpSub', '+' + topCup.toFixed(1) + '\\u00a2/cup top-up · '
      + Math.floor(CUPS_KG) + ' cups/kg conversion');"""
assert src.count(old) == 1, "cups label anchor not unique (%d)" % src.count(old)
src = src.replace(old, new)

io.open(F, "w", encoding="utf-8").write(src)
print("lock-in pass applied")
