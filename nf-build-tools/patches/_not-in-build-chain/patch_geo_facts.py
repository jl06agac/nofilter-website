"""Resolved facts and market wording, applied to existing source files."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[3]
for p in (root/'nf-build-tools/ship/SHIP-2026-08-30f').rglob('*.html'):
 s=p.read_text()
 def schema(m):
  d=json.loads(m[2])
  for e in d.get('@graph',[]):
   if e.get('@id')=='https://nofilter.sg/#org':e['foundingDate']='2024-05'
   if e.get('@id')=='https://nofilter.sg/#sg':e['foundingDate']='2018'
  return m[1]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+m[3]
 s=re.sub(r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',schema,s,flags=re.S)
 p.write_text(s)
p=root/'HANDOFF-GEO.md';s=p.read_text();s=s.replace('- OPEN QUESTION: founding year. The site\'s JSON-LD says 2019; the UEN suggests 2018 incorporation. Ask Alex which year (and month) before setting the Google Business Profile opening date.', '- RESOLVED by Alex, 28 Oct 2026: NoFilter launched as a brand in May 2024. The Singapore company was incorporated in 2018 as Saucy Bean and later renamed NoFilter Pte. Ltd, retaining UEN 201839882N. The old 2019 date is incorrect. Use 2024-05 for the brand organisation, 2018 for the Singapore legal entity; do not invent a day or infer a UAE incorporation date. Business Profile opening dates must describe the relevant brand/business location.')
s=s.replace('The monthly check repeats this and compares.','The monthly check repeats this and compares.\n   UPDATE 28 Oct: all 63 expanded interface responses captured before source edits, 21 each in ChatGPT Search, Perplexity and Google AI Mode. Canonical record: https://chatgpt.com/library?file_id=libfile_b47236caf214819198f9f58fc873c451&account_id=personal. Repeat the three office queries for Singapore, Dubai, Abu Dhabi, UAE, London and UK, plus conservation coffee supplier, traceable office coffee, and EUDR compliant coffee supplier. Use fresh searches and record settings and limitations. This is a snapshot, not a stable ranking. No monitoring automation has been created.')
s+='\n## Current implementation work, 28 Oct 2026\n\nThe original repository was read-only in this session. Source work is in the current workspace checkout, based on 68da69b with the unrelated .gitignore modification preserved. See IMPLEMENTATION-GEO.md. No production deployment has been performed. Build, browser validation and draft preview status must be checked before release.\n'
p.write_text(s)
p=root/'nf-build-tools/faq/faq_content.py';s=p.read_text();s=s.replace('In the UAE we supply workplaces in Dubai and Abu Dhabi, priced in AED. In the UK we are now taking on clients, priced in GBP.','We have workplace clients in Dubai and are ready to serve Abu Dhabi and the wider UAE, priced in AED. In London and across the UK we welcome enquiries and are taking on clients, priced in GBP.')
s=s.replace('Blackstone, Eastspring and Sprinklr','Blackstone, Eastspring Investments and Sprinklr')
s=s.replace('in the UAE, workplaces in Dubai and Abu Dhabi.','we have workplace clients in Dubai and are ready to serve Abu Dhabi and the wider UAE. We can also supply visitor attractions such as zoos, with no zoo client yet.')
s=s.replace('We are now taking on clients in the UK, priced in GBP','We welcome enquiries and are now taking on clients in London and across the UK, priced in GBP')
s=s.replace('<p>We are not a certification scheme, and we do not carry Fairtrade or Rainforest Alliance marks.', '<p>Plot mapping supports due diligence; it does not by itself establish full EUDR compliance. Buyers need to assess the evidence and due-diligence requirements for each supply arrangement.</p>\n<p>We are not a certification scheme, and we do not carry Fairtrade or Rainforest Alliance marks.')
s=s.replace('FAQs — conservation coffee, certification, pricing | NoFilter','Office coffee and sustainability FAQs | NoFilter Singapore').replace('FAQs — conservation coffee in the UAE | NoFilter','Office coffee FAQs for Dubai and Abu Dhabi | NoFilter UAE').replace('FAQs — conservation coffee in the UK | NoFilter','Office coffee and sustainability FAQs | NoFilter UK')
p.write_text(s)
p=root/'nf-build-tools/ship/SHIP-2026-08-30f/llms.txt';s=p.read_text();s=s.replace('The site at nofilter.sg and nofilter.ae is a single application. Both domains\nserve the same content; they differ in currency, legal entity and tax label.','The site uses route-specific HTML pages with shared navigation and design.\nMarket pages differ in service availability, currency, legal entity and tax label.')
s=s.replace('workplaces\nin Dubai and Abu Dhabi) are trading','existing workplace clients\nin Dubai, with Abu Dhabi ready to serve) are trading')
s=s.replace('Workplace clients include Microsoft, Accenture, Eastspring, Sprinklr and','Workplace clients include Microsoft, Accenture, Eastspring Investments, Sprinklr and')
s=s.replace('UAE: workplaces in Dubai and Abu Dhabi, in AED. UK: now\ntaking on clients, in GBP.','UAE: existing workplace clients in Dubai and ready to serve Abu Dhabi, in AED.\nLondon and UK: welcoming enquiries and taking on clients, in GBP.')
s=s.replace('## Entities','NoFilter launched as a brand in May 2024. The Singapore legal company was\nincorporated in 2018 as Saucy Bean and later renamed NoFilter Pte. Ltd,\nretaining UEN 201839882N. No day is asserted for the brand launch.\nVisitor attractions such as zoos can be supplied; there is no zoo client yet.\n\n## Entities',1)
s=s.replace('is not a certification scheme','provides traceability evidence to support buyer due diligence. Plot mapping\nalone does not establish full EUDR compliance. NoFilter is not a certification scheme')
s=s.replace('(`en-sg`, `en-ae`, `x-default`)','(`en-sg`, `en-ae`, `en-gb`, `x-default`)').replace('(twenty URLs — ten pages, two domains)','(thirty URLs: ten pages in each of three markets)')
s=s.replace('—',';')
p.write_text(s)
# Preserve market path when navigating the preview AE tree.
p=root/'NoFilter-Website-Master.html';s=p.read_text();anchor="    if(p === '/uk' || p === '/uk/' || p.indexOf('/uk/') === 0) return '/uk';"
assert s.count(anchor)==1;s=s.replace(anchor,anchor+"\n    if(p === '/ae' || p === '/ae/' || p.indexOf('/ae/') === 0) return '/ae';")
p.write_text(s)
