#!/usr/bin/env python3
"""
make_hero_cut.py — the HOLD THE LINE argument as a standalone social clip.

Recreates the cover's "mega-farm battle" from the site's own source clips and its
own CSS, with no browser and no screen recording:

  spine   _CDN-UPLOAD-SAFE/hero.mp4            1920x1080, 24fps, 30s (agroforest)
  intrus. _CDN-UPLOAD-SAFE/mono-coffee-long.mp4 960x506, 53.6s (industrial monocrop)

  The intruder MUST be one of the golden/olive aerials. The site's grade is only cold
  because hue-rotate(165deg) maps that palette to blue-grey; feed it a vivid green
  plantation (clears-forest.mp4) and the same matrix returns silver frost. Checked
  frame by frame, 9 Sep 2026.

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
SPINE, INTRUDER = f"{CDN}/hero.mp4", f"{CDN}/mono-coffee-long.mp4"
W, H, FPS, DUR = 1920, 1080, 24, 30.0

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
STEP = 0.1          # one band per 100ms, as the .5s/steps(3) loop reads on screen

# ── where the monocrop interrupts, and for how long ──────────────────────────
# placed on the spine's own beats: over the canopy, the bridge, the drying,
# the forest drone, then the longest hold before the village closes it out.
INSERTS = [(5.0, 6.2), (10.4, 11.2), (15.0, 16.6), (20.2, 21.2), (25.0, 27.0)]
TEAR_OUT = 0.3

def windows():
    """(x, y, w, h, start, end) for every band, and (None,...) for full frame."""
    out = []
    for s, e in INSERTS:
        t = s
        for i, (top, bot, dx) in enumerate(TEAR):        # tear in
            y = round(H*top/100); h = round(H*(100-top-bot)/100)
            out.append((round(W*dx/100), y, W, h, t, t+STEP)); t += STEP
        full_end = e - TEAR_OUT
        if full_end > t:
            out.append((None, None, None, None, t, full_end))
        t = full_end
        for top, bot, dx in reversed(TEAR[:3]):          # tear out
            y = round(H*top/100); h = round(H*(100-top-bot)/100)
            out.append((round(W*dx/100), y, W, h, t, min(t+STEP, e))); t += STEP
    return out

def build():
    parts = [f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
             f"crop={W}:{H},setsar=1,format=rgb24,"
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
