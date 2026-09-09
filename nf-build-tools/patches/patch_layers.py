import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 112 · THE SENTENCE THAT STOPPED BEING TRUE ═════════════════════════════
# Caught while auditing the site for AI searchability, not by looking for it.
#
# Block 105 (3 Sep) flipped the Gayo Lues "Ground evidence" tile from pending
# to live, on Alex's instruction: "Gayo Lues patrol · not yet in service — it
# is in service. so change to live like the other two layer tiles." The tile
# changed. The sentence above it, which counts the tiles, did not.
#
#   evidence tiles today:  live 3   pend 1
#   the copy still said:   "Two of the four layers are live today;
#                           the other two are dimmed until they are."
#
# This is the verification section — the part of the site whose entire claim
# is that the record is checkable. A number that contradicts the tiles
# directly beneath it is worse here than anywhere else on the site, and it is
# exactly the kind of line an assistant quotes back at somebody.
#
# Counted from the markup rather than assumed: any future change to a tile's
# data-state will make this assert fail, which is the point.
LIVE = src.count('<article class="ev" data-state="live"')
PEND = src.count('<article class="ev" data-state="pend"')
assert (LIVE, PEND) == (3, 1), \
    "layer states moved again: live=%d pend=%d — update the sentence" % (LIVE, PEND)

fix("Two of the four layers are live today; the other two are dimmed until they are.",
    "Three of the four layers are live today; the fourth is dimmed until it is.")

io.open(F, "w", encoding="utf-8").write(src)
print("the layer count matches the layers")
