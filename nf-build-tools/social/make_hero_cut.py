#!/usr/bin/env python3
"""
make_hero_cut.py — the HOLD THE LINE argument as a standalone social clip.

Recreates the cover's "mega-farm battle" from the site's own source clips and its
own CSS, with no browser and no screen recording:

  spine   _CDN-UPLOAD-SAFE/hero.mp4            1920x1080, 24fps, 30s (agroforest)
  intrus. _CDN-UPLOAD-SAFE/clears-forest.mp4   1280x720, 20.75s (industrial monocrop)

  PRE_HUE is not decoration. The site's grade only reads cold because hue-rotate(165deg)
  maps a GOLDEN/OLIVE palette to blue-grey. clears-forest.mp4 is vivid green, and the
  same matrix returns silver frost on it. Rotating it into the palette the filter expects
  first is what makes the site's own CSS land where the site lands. Checked frame by
  frame against a graded mega-farm-test.mp4 reference, 9 Sep 2026.

  It is used rather than the golden aerials because it is top-down: every horizontal
  slice shows regimented rows and machinery. The horizon clips put sky in the top band,
  which reads as a blank grey bar rather than as a plantation.

Two things are lifted verbatim from NoFilter-Website-Master.html so the clip and the
site cannot drift apart:

  .cover-mega   filter: grayscale(.7) contrast(1.15) brightness(.88)
                        sepia(.35) hue-rotate(165deg) saturate(1.1)
  @keyframes coverMegaTear   the five clip-path/translate states

CSS filters are a chain of affine ops in sRGB. They are composed here into ONE 3x3
matrix plus an offset and handed to ffmpeg's colorchannelmixer, rather than guessed
at with eq/hue, so the monocrop is the same cold blue-grey the site paints.

Usage:  python3 make_hero_cut.py [out.mp4]
"""
import math, subprocess, sys, os

CDN = os.path.expanduser("/sessions/rcw-01djhabq5dlqkc198szyl1mg/mnt/NoFilter/_CDN-UPLOAD-SAFE")
SPINE, INTRUDER = f"{CDN}/hero.mp4", f"{CDN}/clears-forest.mp4"
W, H, FPS, DUR = 1920, 1080, 24, 30.0
PRE_HUE = -55        # see the note above; green -> the golden palette the grade expects

# ── the CSS filter chain, composed ────────────────────────────────────────────
def mul(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

LR, LG, LB = 0.2126, 0.7152, 0.0722

def grayscale(a):
    k = 1 - a
    return [[LR+k*(1-LR), LG*(1-k),   LB*(1-k)],
            [LR*(1-k),    LG+k*(1-LG), LB*(1-k)],
            [LR*(1-k),    LG*(1-k),   LB+k*(1-LB)]]

def sepia(a):
    S = [[0.393,0.769,0.189],[0.349,0.686,0.168],[0.272,0.534,0.131]]
    return [[(1-a)*(i==j) + a*S[i][j] for j in range(3)] for i in range(3)]

def hue_rotate(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[0.213+c*0.787-s*0.213, 0.715-c*0.715-s*0.715, 0.072-c*0.072+s*0.928],
            [0.213-c*0.213+s*0.143, 0.715+c*0.285+s*0.140, 0.072-c*0.072-s*0.283],
            [0.213-c*0.213-s*0.787, 0.715-c*0.715+s*0.715, 0.072+c*0.928+s*0.072]]

def saturate(s):
    return [[0.213+0.787*s, 0.715-0.715*s, 0.072-0.072*s],
            [0.213-0.213*s, 0.715+0.285*s, 0.072-0.072*s],
            [0.213-0.213*s, 0.715-0.715*s, 0.072+0.928*s]]

# grayscale(.7) -> contrast(1.15) -> brightness(.88) -> sepia(.35) -> hue-rotate(165) -> saturate(1.1)
# contrast: x*1.15 + 0.5*(1-1.15);  brightness: x*0.88  =>  x*1.012 - 0.066
M_post = mul(saturate(1.1), mul(hue_rotate(165), sepia(0.35)))
A = [[1.012*v for v in row] for row in mul(M_post, grayscale(0.7))]
b = [-0.066*sum(M_post[i]) for i in range(3)]          # offset, per channel
OFFSET = sum(b)/3                                       # ffmpeg eq takes one value

CCM = ("colorchannelmixer="
       f"rr={A[0][0]:.5f}:rg={A[0][1]:.5f}:rb={A[0][2]:.5f}:"
       f"gr={A[1][0]:.5f}:gg={A[1][1]:.5f}:gb={A[1][2]:.5f}:"
       f"br={A[2][0]:.5f}:bg={A[2][1]:.5f}:bb={A[2][2]:.5f}")

# ── coverMegaTear: (top inset %, bottom inset %, x translate %) ───────────────
TEAR = [(0, 88, -1.0), (42, 44, 1.4), (70, 16, -1.4), (18, 66, 1.0)]
STEP = 0.1          # one state per 100ms, as the .5s/steps(3) loop reads on screen

# Five states, cycled: the four CSS bands, then both outer bands at once. The double
# is not in the stylesheet; it is here because a band that sits across the frame in
# two places makes the comparison legible in a single glance, which is the whole job.
STATES = [(0,), (1,), (2,), (3,), (0, 2)]

# ── where the monocrop intrudes ──────────────────────────────────────────────
# Six events, each: banded tear IN, a full-frame hold long enough to actually read,
# banded tear OUT. Two earlier passes each failed one half of the brief -- straight
# cuts to full frame showed the monocrop but ate the forest; bands alone kept the
# forest but never let you see what it was being compared to, and 30s of slow drone
# footage between sparse bands reads as a still. This does both, and spaces the events
# so nothing holds still for more than about two seconds.
EVENTS = [(3.5, 5.7), (8.0, 10.2), (12.5, 14.7), (17.0, 19.2), (21.0, 23.2), (25.5, 27.7)]
TEAR_LEN = 0.5      # banded ramp at each end of an event

def windows():
    """(x, y, w, h, start, end) per band; full frame carries x=None."""
    out, n = [], 0
    for s, e in EVENTS:
        t = s                                            # tear in
        while t < s + TEAR_LEN - 1e-6:
            for bi in STATES[n % len(STATES)]:
                top, bot, dx = TEAR[bi]
                y = round(H*top/100); h = round(H*(100-top-bot)/100)
                out.append((round(W*dx/100), y, W, h, t, t+STEP))
            n += 1; t += STEP
        out.append((None, None, None, None, t, e - TEAR_LEN))   # the hold
        t = e - TEAR_LEN                                 # tear out
        while t < e - 1e-6:
            for bi in STATES[n % len(STATES)]:
                top, bot, dx = TEAR[bi]
                y = round(H*top/100); h = round(H*(100-top-bot)/100)
                out.append((round(W*dx/100), y, W, h, t, min(t+STEP, e)))
            n += 1; t += STEP
    return out

def build():
    parts = [f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
             f"crop={W}:{H},setsar=1,format=rgb24,hue=h={PRE_HUE},"
             f"{CCM},eq=brightness={OFFSET:.5f},format=yuv420p[mono]"]
    wins = windows()
    parts.append("[mono]split=%d%s" % (len(wins), "".join(f"[m{i}]" for i in range(len(wins)))))
    parts.append(f"[0:v]setsar=1,fps={FPS}[base0]")
    for i, (x, y, w, h, s, e) in enumerate(wins):
        if x is None:
            parts.append(f"[base{i}][m{i}]overlay=enable='between(t,{s:.3f},{e:.3f})'[base{i+1}]")
        else:
            parts.append(f"[m{i}]crop={w}:{h}:0:{y}[c{i}]")
            parts.append(f"[base{i}][c{i}]overlay=x={x}:y={y}:"
                         f"enable='between(t,{s:.3f},{e:.3f})'[base{i+1}]")
    parts.append(f"[base{len(wins)}]format=yuv420p[v]")
    return ";".join(parts)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        "/sessions/rcw-01djhabq5dlqkc198szyl1mg/mnt/Desktop/NoFilter-HTL-forest-v-monoculture.mp4")
    cmd = ["ffmpeg", "-v", "warning", "-i", SPINE, "-stream_loop", "-1", "-i", INTRUDER,
           "-filter_complex", build(), "-map", "[v]", "-an", "-t", str(DUR),
           "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-profile:v", "high",
           "-movflags", "+faststart", "-y", out]
    print("matrix :", CCM)
    print("offset :", f"{OFFSET:.5f}")
    print("bands  :", len(windows()))
    sys.exit(subprocess.call(cmd))
