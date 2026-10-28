"""Reviewed, one-off template edit. Not part of the build chain. 28 Oct 2026.
Structured data links the brand, the Singapore company and the founder to their other
official profiles: the Singapore Google Business Profile (Maps CID, from Alex's share
link), its Knowledge Graph entity, and Alex's LinkedIn."""
from pathlib import Path
root=Path(__file__).resolve().parents[3];T=root/'nf-build-tools/ship/SHIP-2026-08-30f'
MAPS='https://maps.google.com/?cid=3848062334334392515'
KG='https://www.google.com/search?kgmid=/g/11nvkx815c'
LI='https://www.linkedin.com/in/alexclark-nofilter/'
n=0
for f in sorted(T.rglob('*.html')):
    s=f.read_text();o=s
    s=s.replace('"founder":{"@type":"Person","name":"Alex Clark"}','"founder":{"@type":"Person","name":"Alex Clark","jobTitle":"Founder","sameAs":["'+LI+'"]}')
    s=s.replace('"sameAs":["https://www.linkedin.com/company/nofiltercoffee"]','"sameAs":["https://www.linkedin.com/company/nofiltercoffee","'+KG+'"]')
    s=s.replace('"@id":"https://nofilter.sg/#sg","name":"NoFilter Pte. Ltd"','"@id":"https://nofilter.sg/#sg","name":"NoFilter Pte. Ltd","hasMap":"'+MAPS+'","sameAs":["'+MAPS+'"]')
    if s!=o:f.write_text(s);n+=1
print('pages',n)
