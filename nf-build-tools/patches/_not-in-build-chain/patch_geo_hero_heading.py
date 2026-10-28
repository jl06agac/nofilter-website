"""Reviewed, one-off master edit. Not part of the build chain.
28 Oct 2026: the plain service band above the At Work hero came out (Alex: it looked awful,
and it reversed commit 132). The market heading moves into the hero eyebrow instead:
same look as before, but it is now the page's h1 for each market."""
from pathlib import Path
import re
p=Path(__file__).resolve().parents[3]/'NoFilter-Website-Master.html'
s=p.read_text()
a=s.index('<style id="nf-service-css">'); b=s.index('</div></div>',s.index('id="nfServiceIntro"'))+len('</div></div>')
assert s.count('id="nfServiceIntro"')==1 and b>a
s=s[:a]+s[b:]
old='<p class="awx-eyebrow">The impact you can point to</p>'
assert s.count(old)==1
new=('<h1 class="awx-eyebrow">'
 '<span data-nf-market-copy="SG">Office coffee supply in Singapore</span>'
 '<span data-nf-market-copy="AE" hidden>Office coffee supply in Dubai and Abu Dhabi</span>'
 '<span data-nf-market-copy="UK" hidden>Office coffee supply for London and the UK</span></h1>')
s=s.replace(old,new)
css='.awx-eyebrow{font-family:var(--awx-font-mono);'
assert s.count(css)==1
s=s.replace(css,'h1.awx-eyebrow{font-weight:400;line-height:normal;}\n'+css)
p.write_text(s)
