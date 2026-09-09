# Patches that are NOT in the build chain

Recovered 9 Sep 2026 from `nf-build-tools-2026-09-03.tgz`, where they were the only
copies. They are **not** listed in `build.sh`, so the current master is not built from
them and running them is not part of any build.

Blocks 70, 71, 72, 73, 74 and 91. Each carries Alex's own words in its header comment,
which is why they were worth rescuing rather than leaving inside an archive:

| file | block | opening note |
|---|---|---|
| `patch_zones.py`   | 70 | "Separate each screen into four distinct vertical zones …" |
| `patch_banner.py`  | 71 | the CTA in Title Case |
| `patch_collide.py` | 72 | "YOUR LIKELY CUPS PER YEAR is overlapping the Price" |
| `patch_stack.py`   | 73 | the stage becomes a flex column; block 72 made 72 worse |
| `patch_align.py`   | 74 | "still really bad, and now lost its standardisation" |
| `patch_herovid.py` | 91 | "i loaded nofilter.sg this morning and it was really quite …" |

**Open question, not yet answered:** whether each block's effect was folded into a later
patch or quietly dropped from the site. Until someone checks, do not assume either.
