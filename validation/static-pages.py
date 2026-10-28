from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import re,json,subprocess,hashlib
root=Path('SHIP-2026-10-28a'); errors=[]; scripts={}; rows=[]
class Page(HTMLParser):
 def __init__(self,s):
  super().__init__();self.routes=[];self.h1=0;self.canonical=[];self.alternates={};self.title='';self.desc=[];self.market=[];self.assets=[];self.links=[];self.script=None;self.in_title=False;self.feed(s)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='section' and 'route' in a.get('class','').split():self.routes.append(a.get('id'))
  if t=='h1':self.h1+=1
  if t=='title':self.in_title=True
  if t=='meta' and a.get('name')=='description':self.desc.append(a.get('content'))
  if t=='meta' and a.get('name')=='nf-market':self.market.append(a.get('content'))
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  if t=='link' and a.get('rel')=='alternate':self.alternates[a.get('hreflang')]=a.get('href')
  if t=='a':self.links.append(a.get('href',''))
  if t in ('script','img','source'):self.assets.append(a.get('src',''))
  if t=='script':self.script={'type':a.get('type',''),'src':a.get('src'),'text':''}
 def handle_data(self,d):
  if self.in_title:self.title+=d
  if self.script is not None:self.script['text']+=d
 def handle_endtag(self,t):
  if t=='title':self.in_title=False
  if t=='script' and self.script:
   sc=self.script
   if not sc['src'] and sc['type'] not in ('application/ld+json','application/json') and sc['text'].strip():scripts[hashlib.sha256(sc['text'].encode()).hexdigest()]=sc['text']
   if sc['type']=='application/ld+json':json.loads(sc['text'])
   self.script=None
for p in sorted(root.rglob('*.html')):
 if p.name=='404.html':continue
 rel=p.relative_to(root).as_posix();s=p.read_text();page=Page(s);tree=re.sub(r'^(ae|uk)/','',rel);market='AE' if rel.startswith('ae/') else 'UK' if rel.startswith('uk/') else 'SG';path=tree.removesuffix('index.html').rstrip('/');canonical=('https://nofilter.ae' if market=='AE' else 'https://nofilter.sg')+('/uk' if market=='UK' else '')+('/'+path if path else '/')
 if path=='':canonical=canonical.rstrip('/')+'/' if market!='UK' else canonical.rstrip('/')
 for ok,label in [(len(page.routes)==1,'one route'),(page.h1==1,'one H1'),(page.market==[market],'market'),(len(page.desc)==1 and bool(page.desc[0]),'description'),(bool(page.title),'title'),(page.canonical==[canonical],'canonical'),(set(page.alternates)=={'en-sg','en-ae','en-gb','x-default'},'hreflang'),(not re.search(r'var RATES\s*=|r24:\s*[1-9]|calloutHr:',s),'private rates absent')]:
  if not ok:errors.append(f'{rel}: {label}'+(str(page.canonical) if label=='canonical' else ''))
 for src in page.assets+page.links:
  u=urlsplit(src)
  if u.scheme or u.netloc or not u.path.startswith('/'):continue
  target=root/u.path.lstrip('/')
  if not target.is_file() and not (target/'index.html').is_file():errors.append(f'{rel}: missing local target {u.path}')
 rows.append({'route':rel,'market':market,'bytes':len(s.encode()),'canonical':page.canonical,'title':page.title})
for digest,script in scripts.items():
 r=subprocess.run(['node','--check'],input=script,text=True,capture_output=True)
 if r.returncode:errors.append('Inline script syntax '+digest[:12]+': '+r.stderr.splitlines()[0])
result={'pages':len(rows),'uniqueInlineScriptsChecked':len(scripts),'errors':sorted(set(errors)),'routes':rows,'limitations':['No browser execution, visual, mobile or navigation testing: sandbox blocks local server.','Static initial HTML inspection is not a JavaScript-disabled browser test.']}
Path('validation/static-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='routes'},indent=2));raise SystemExit(bool(errors))
