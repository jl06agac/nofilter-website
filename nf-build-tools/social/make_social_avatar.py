#!/usr/bin/env python3
"""
make_social_avatar.py - square profile avatar for LinkedIn / any social page slot.

Why this exists
---------------
The asset previously in the LinkedIn Page logo slot was the full wordmark
(nofilter_white_on_F27126.png, 2236x446). A social logo slot is square, so a
5:1 wordmark gets centre-cropped: all that survives is the "O" of NOFILTER and
the torn cross of the "T". That is the "+ not formulated for it" problem.

The fix is to set the standalone mark - the torn cross, which is the "T" of the
wordmark lifted out - on a full-bleed brand field, centred, with enough margin
that it survives both the square and the rounded/circular crops LinkedIn applies
in different surfaces.

Decisions, and their evidence
-----------------------------
* Mark geometry is taken verbatim from _CDN-UPLOAD-SAFE/nofilter-favicon-v3.svg
  (the two paths, 1000-unit space). Nothing is redrawn: the tear, the notch and
  the offset right arm are the designer's, unaltered.
* Field colour is #F27126, the orange locked in Brand Bible v4.1 (March 2026).
  Note the live site does not use it: NoFilter-Website-Master.html uses #EE4D17
  in 39 places and #F27126 in none. #EE4D17 is the red-vermilion drift already
  flagged as off-brand, so the Brand Bible is treated as the authority here and
  the site is the outlier. If the site is ever the authority instead, change
  FIELD, not this note.
* Mark is white, matching the wordmark lockup it is lifted from.
* Mark height is 62% of the canvas. The mark bbox is 657 x 754 in its own space,
  so at 62% height its corner-to-corner diagonal sits inside the circle
  LinkedIn masks to in feed contexts, while still reading large in the square
  page-header crop.
* 800 x 800 output. LinkedIn's floor is 300 x 300; 800 covers retina without
  going near the 4 MB ceiling.

Run
---
    python3 make_social_avatar.py <path-to-nofilter-favicon-v3.svg> <out.png>
"""

import sys
import re
import cairosvg

SIZE = 800          # px, square
FIELD = "#F27126"   # locked brand orange, Brand Bible v4.1
MARK = "#ffffff"
MARK_HEIGHT_FRAC = 0.62

# bbox of the two mark paths in the source SVG's 1000-unit coordinate space,
# measured from the path data (x 182.00-839.31, y 140.88-895.10).
BBOX = (182.00, 140.88, 839.31, 895.10)


def extract_paths(svg_text):
    """Pull the two mark path d= strings out of the favicon SVG, in order."""
    ds = re.findall(r'<path[^>]*\sd="([^"]+)"', svg_text)
    if len(ds) != 2:
        raise SystemExit(
            f"expected 2 paths in the source mark, found {len(ds)} - "
            "the source SVG has changed, check it before trusting this output"
        )
    return ds


def build(svg_text):
    x0, y0, x1, y1 = BBOX
    w, h = x1 - x0, y1 - y0

    target_h = SIZE * MARK_HEIGHT_FRAC
    scale = target_h / h
    target_w = w * scale

    # translate so the mark bbox lands centred on the canvas
    tx = (SIZE - target_w) / 2 - x0 * scale
    ty = (SIZE - target_h) / 2 - y0 * scale

    paths = "".join(f'<path d="{d}" fill="{MARK}"/>' for d in extract_paths(svg_text))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" '
        f'viewBox="0 0 {SIZE} {SIZE}">'
        f'<rect width="{SIZE}" height="{SIZE}" fill="{FIELD}"/>'
        f'<g transform="translate({tx:.4f} {ty:.4f}) scale({scale:.6f})">{paths}</g>'
        f"</svg>"
    )


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    src, out = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as fh:
        svg = build(fh.read())
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out,
                     output_width=SIZE, output_height=SIZE)
    print(f"wrote {out} ({SIZE}x{SIZE}, field {FIELD}, mark {MARK})")


if __name__ == "__main__":
    main()
