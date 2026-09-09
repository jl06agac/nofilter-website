import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 94 · THE COUNTER'S STILL HOLDS UNTIL THE PAGE HAS ACTUALLY STOPPED ═════
# Alex, 3 Sep: "the slower i scroll the more the judder effect is exacerbated."
# That sentence is the diagnosis. pass128 hides the live counter iframe and
# shows a still while the page is moving — display:none, deliberately,
# because the iframe composites even when invisible — and the flag came off
# two frames after the last movement. A scripted scroll moves every frame, so
# the flag held and the pass measured smooth; a slow trackpad scroll through
# the eased scroller moves the page a pixel or two every few frames, with
# gaps longer than two frames between them. Every gap flipped the flag: the
# iframe came back (layout, a compositor attach, the board repainting), the
# next nudge hid it again, and so on — a judder that gets worse the slower
# you go, on the one route that has the board. Fast scrolling never let the
# flag drop, which is why it felt fine.
# The still now holds until the page has been genuinely still for 400ms:
# one flip when you start, one when you stop, nothing in between. The board
# is back well before the eye goes looking for it.
fix("""      stillT = setTimeout(function(){ host.classList.remove('is-moving'); }, 40);""",
    """      stillT = setTimeout(function(){ host.classList.remove('is-moving'); }, 400);   /* block 94: was 40 */""")

io.open(F, "w", encoding="utf-8").write(src)
print("counter still holds 400ms")
