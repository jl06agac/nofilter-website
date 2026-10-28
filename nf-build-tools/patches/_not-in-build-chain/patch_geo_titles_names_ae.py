"""Reviewed, one-off source edit. Not part of the build chain. 28 Oct 2026.
1. Titles (title, og:title, twitter:title): no em dashes; brand suffix "NoFilter Coffee".
2. Structured data and og:site_name: the brand is "NoFilter Coffee", alternate "NoFilter".
3. netlify.toml: nofilter.ae/ae/* and nofilter.ae/uk/* get 301s to their one real address
   (placed after the per-path nofilter.ae rewrites, beside the nofilter.sg/ae rules).
4. split-bundle.py: UAE pages link to clean paths (/origins, not /ae/origins).
"""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[3]
T=root/'nf-build-tools/ship/SHIP-2026-08-30f'

def fix_title(t):
    t=t.replace('NoFilter — Conservation coffee · Singapore &amp; UAE','Conservation coffee in Singapore | NoFilter Coffee')
    m=re.match(r'NoFilter — (.*)$',t)
    if m: t=m.group(1)+' | NoFilter Coffee'
    t=t.replace(' — ',': ')
    t=re.sub(r'\| NoFilter( (UAE|UK|Singapore))?$',lambda m:'| NoFilter Coffee'+(m.group(1) or ''),t)
    return t

changed=0
for f in sorted(T.rglob('*.html')):
    s=f.read_text();o=s
    s=re.sub(r'(<title>)([^<]*)(</title>)',lambda m:m[1]+fix_title(m[2])+m[3],s)
    s=re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")([^"]*)(")',lambda m:m[1]+fix_title(m[2])+m[3],s)
    s=s.replace('<meta property="og:site_name" content="NoFilter">','<meta property="og:site_name" content="NoFilter Coffee">')
    s=s.replace('"@id":"https://nofilter.sg/#org","name":"NoFilter","alternateName":"NoFilter Coffee"','"@id":"https://nofilter.sg/#org","name":"NoFilter Coffee","alternateName":"NoFilter"')
    s=s.replace('"@id":"https://nofilter.sg/#website","url":"https://nofilter.sg/","name":"NoFilter"','"@id":"https://nofilter.sg/#website","url":"https://nofilter.sg/","name":"NoFilter Coffee","alternateName":"NoFilter"')
    if s!=o: f.write_text(s);changed+=1
print('template pages changed',changed)

# The build's market swaps match the template's own title text, so both sides move together.
b=root/'nf-build-tools/ship/build-ship.mjs';s=b.read_text()
n=s.count("| NoFilter'")
s=s.replace("| NoFilter'","| NoFilter Coffee'");b.write_text(s);print('build-ship suffixes',n)

q=root/'nf-build-tools/faq/faq_content.py';s=q.read_text()
for a in ['| NoFilter Singapore"','| NoFilter UAE"','| NoFilter UK"']:
    assert s.count(a)==1,a
    s=s.replace(a,a.replace('| NoFilter','| NoFilter Coffee'))
q.write_text(s)

t=T/'netlify.toml';s=t.read_text()
anchor='[[redirects]]\n  from = "https://nofilter.sg/ae/*"'
assert s.count(anchor)==1 and 'nofilter.ae/ae/*' not in s
block='# 28 Oct: the same rule from the UAE side. Built UAE pages now link to clean paths, and\n# any old /ae/ or /uk/ address on nofilter.ae goes to its one real address.\n'
for h in ['https://nofilter.ae','https://www.nofilter.ae','http://nofilter.ae','http://www.nofilter.ae']:
    block+=f'[[redirects]]\n  from = "{h}/ae/*"\n  to = "https://nofilter.ae/:splat"\n  status = 301\n  force = true\n'
    block+=f'[[redirects]]\n  from = "{h}/uk/*"\n  to = "https://nofilter.sg/uk/:splat"\n  status = 301\n  force = true\n'
s=s.replace(anchor,block+anchor);t.write_text(s)

p=root/'nf-build-tools/ship/split-bundle.py';s=p.read_text()
anchor="    slug=tree.split('/')[1] if tree.startswith('origins/')"
assert s.count(anchor)==1
s=s.replace(anchor,"    if market=='AE':s=re.sub(r'href=\"/ae(/[^\"]*)?\"',lambda m:'href=\"'+(m.group(1) or '/')+'\"',s)\n"+anchor)
p.write_text(s)
print('done')
