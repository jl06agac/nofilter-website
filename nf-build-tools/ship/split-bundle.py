#!/usr/bin/env python3
"""Final route projection, after market/template transformations, before FAQ build.
HTMLParser spans preserve script raw text and nested section boundaries.
"""
from pathlib import Path
from html.parser import HTMLParser
import re,sys,html
from split import route_spans

PATHS={'home':'/','origins':'/origins','shop':'/shop','work':'/wholesale-coffee','quote':'/trade-pricing','faq':'/faqs'}
ORIGINS={'batang-toru':('toru','Batang Toru'),'arakan-mountains':('arakan','Arakan Mountains'),'batang-gadis':('gadis','Batang Gadis'),'gayo-lues':('gayo','Gayo Lues')}
class Elements(HTMLParser):
    def __init__(self,s):
        super().__init__(convert_charrefs=False);self.stack=[];self.spans=[];self.offsets=[0]
        for line in s.splitlines(True):self.offsets.append(self.offsets[-1]+len(line))
        self.feed(s)
    def at(self):
        l,c=self.getpos();return self.offsets[l-1]+c
    def handle_starttag(self,t,a):
        if t in ('section','div'):self.stack.append((t,dict(a),self.at()))
    def handle_endtag(self,t):
        if t not in ('section','div'):return
        if self.stack and self.stack[-1][0]==t:
            tag,a,start=self.stack.pop();self.spans.append((a,start,self.at()+len(t)+3))
def remove(s,spans):
    for a,b in sorted(spans,reverse=True):s=s[:a]+s[b:]
    return s

def project(s,rel):
    market='AE' if rel.startswith('ae/') else 'UK' if rel.startswith('uk/') else 'SG'
    tree=re.sub(r'^(ae|uk)/','',rel)
    route=next((r for r,p in PATHS.items() if tree==p.strip('/')+'/index.html'),None)
    if tree=='index.html':route='home'
    if tree.startswith('origins/'):route='origins'
    if not route:raise ValueError('Unknown route '+rel)
    rescued=[];cuts=[]
    for r,(a,b) in route_spans(s).items():
        if r!=route:
            rescued.extend(re.findall(r'<style\b[^>]*>.*?</style>',s[a:b],re.S));cuts.append((a,b))
    s=remove(s,cuts)
    if rescued:s=s.replace('</head>',''.join(rescued)+'</head>',1)
    s=re.sub(r'<section class="route(?: on)?" id="'+route+'"','<section class="route on" id="'+route+'"',s,count=1)
    # Keep only the market's master-authored service copy.
    cuts=[]
    for a,i,j in Elements(s).spans:
        if 'data-nf-market-copy' in a and a['data-nf-market-copy']!=market:cuts.append((i,j))
    s=remove(s,cuts)
    s=re.sub(r'<span data-nf-market-copy="(?!'+market+r'")[A-Z]+"(?: hidden)?>[^<]*</span>','',s)
    s=re.sub(r'(<[a-z]+ data-nf-market-copy="'+market+r'") hidden',r'\1',s)
    slug=tree.split('/')[1] if tree.startswith('origins/') and tree.count('/')==2 else None
    if slug:
        key,name=ORIGINS[slug]
        # Each record consists of its hero section, data strip and drawer.
        starts=[m.start() for m in re.finditer(r'<section class="fbh-origin\b',s)]
        last=next((j for a,i,j in Elements(s).spans if a.get('id')=='fbhd-gayo'),None)
        assert len(starts)==4 and last
        ends=starts[1:]+[last]
        cuts=[(a,b) for a,b in zip(starts,ends) if not re.match(r'<section[^>]*id="fbh-'+key+'"',s[a:])]
        s=remove(s,cuts)
        s=re.sub(r'(<h2 class="d2 d2-inline">).*?(</h2>)',lambda m:m[1]+html.escape(name)+' coffee'+m[2],s,count=1,flags=re.S)
        s=s.replace('Behind each is a real canopy edge','Behind this origin is a real canopy edge',1)
        s=s.replace('</div><!-- unused -->','</div>')
        # Initial HTML opens the full origin record, independent of JavaScript.
        s=re.sub(r'(<div class="fbh-drawer(?: is-open)?" id="fbhd-'+key+r'"[^>]*?)\s+hidden',r'\1',s)
        s=s.replace('<div class="fbh-drawer" id="fbhd-'+key+'"','<div class="fbh-drawer is-open" id="fbhd-'+key+'"')
    if route!='quote':
        s=remove(s,[(i,j) for a,i,j in Elements(s).spans if a.get('id')=='qLetterSrc'])
    # Real anchors avoid SPA interception and work without JavaScript.
    base='/uk' if market=='UK' else '/ae' if market=='AE' else ''
    def anchor(m):
        tag=m[0];h=re.search(r'\bhref="([^"]*)"',tag);dr=re.search(r'\bdata-r="([^"]*)"',tag)
        target=PATHS.get(dr[1]) if dr else None
        if h:
            value=h[1]
            if value.startswith('#') and value[1:] in PATHS:target=PATHS[value[1:]]
            elif value.startswith('/') and not value.startswith('//'):
                value=re.sub(r'^/(ae|uk)(?=/|$)','',value) or '/';target=value
        if target is not None:
            dest=base+target if target!='/' else (base+'/' if base else '/')
            tag=re.sub(r'\s+href="[^"]*"','',tag);tag=tag[:-1]+' href="'+dest+'">'
        return tag
    s=re.sub(r'<a\b[^>]*>',anchor,s)
    # Stable visible H1; preserve each heading's existing presentation classes.
    if route=='quote':
        s=s.replace('<span class="mani-slotc" id="qgSlotc"></span>','<span class="mani-slotc" id="qgSlotc">Office coffee</span>',1)
    if not re.search(r'<h1\b',s):
        a,b=route_spans(s)[route];seg=s[a:b]
        h=next((m for m in re.finditer(r'<h2\b([^>]*)>(.*?)</h2>',seg,re.S) if len(re.sub('<[^>]+>','',m[2]).strip())>3 and (route=='quote' or 'mani-slot' not in m[2])),None)
        if not h:raise ValueError('No suitable H1 '+rel)
        seg=seg[:h.start()]+'<h1'+h[1]+'>'+h[2]+'</h1>'+seg[h.end():];s=s[:a]+seg+s[b:]
    if route=='shop':
        fallback='<noscript><div class="wrap"><p>Retail bags are coming soon. For office supply, request trade access.</p><ul>'+''.join('<li><a href="'+base+'/origins/'+o+'">'+n+' coffee</a></li>' for o,(_,n) in ORIGINS.items())+'</ul></div></noscript>'
        a,b=route_spans(s)['shop'];s=s[:b-10]+fallback+s[b-10:]
    if route=='origins' and not slug:
        # Explicit index links remain discoverable without the drawer runtime.
        links='<nav class="wrap" aria-label="Coffee origin records">'+''.join('<a href="'+base+'/origins/'+o+'">'+n+'</a> ' for o,(_,n) in ORIGINS.items())+'</nav>'
        a,b=route_spans(s)['origins'];s=s[:b-10]+links+s[b-10:]
    if slug:
        a,b=route_spans(s)['origins'];s=s[:b-10]+'<p class="wrap"><a href="'+base+'/origins">Explore all origins</a></p>'+s[b-10:]
    s=s.replace('<html ', '<html data-nf-page="'+route+'" ',1)
    # Every tree declares a market, including SG, so timezone cannot change it.
    if not re.search(r'<meta\b[^>]*name="nf-market"',s):s=s.replace('</head>','<meta name="nf-market" content="'+market+'"></head>',1)
    s=s.replace('</head>','<script src="/assets/nf-pages.js"></script><noscript><style>.route.on .fade,.route.on .rl>span,.route.on .fbh-reveal,.route.on .rv,.route.on .ev,.route.on .wp-bundle{opacity:1!important;transform:none!important;visibility:visible!important}.route.on{display:block!important}</style></noscript></head>',1)
    assert len(route_spans(s))==1,(rel,route_spans(s))
    assert len(re.findall(r'<h1\b',s))==1,rel
    return s

if __name__=='__main__':
    root=Path(sys.argv[1]);count=0
    for p in sorted(root.rglob('*.html')):
        if p.name=='404.html' or 'assets' in p.parts or 'faqs' in p.parts:continue
        p.write_text(project(p.read_text(),p.relative_to(root).as_posix()));count+=1
    print('Projected',count,'route-specific pages')
