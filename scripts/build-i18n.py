#!/usr/bin/env python3
# Timestamp: 2026-11-18 | Version: 2.5.2
# Author & Credits: https://www.alawise.es/1-s
"""Build locale routes without changing app IDs, data contracts or media URLs."""
import ast
import html
import json
import math
import re
import sys
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

sys_rad = Path(__file__).resolve().parents[1]
pth_dst = sys_rad / 'dist'
pth_loc = sys_rad / 'src/i18n'
dat_met = json.loads((sys_rad / 'src/site.json').read_text())
TAG_OMIT = {'script', 'style', 'code', 'pre', 'kbd', 'samp'}
TAG_VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
ATR_TXT = {'title','alt','aria-label','placeholder'}
META_TXT = {'description','og:title','og:description','og:image:alt','twitter:title','twitter:description','twitter:image:alt'}
META_URL = {'og:url','twitter:url'}

def norm_txt(txt):
    return re.sub(r'\s+', ' ', html.unescape(txt)).strip()

def is_txt(txt):
    return bool(re.search(r'[A-Za-z]{2}', txt)) and not re.fullmatch(r'[\d\W_]+',txt) and len(txt)<4000

def base_files():
    return sorted(p for p in pth_dst.rglob('index.html') if p.relative_to(pth_dst).parts[0] not in ('es','calo','downloads') and not any(x.startswith('qa-') for x in p.parts))

def route_pag(pth):
    txt='/' + str(pth.relative_to(pth_dst)).removesuffix('index.html')
    return '/kamala' if txt=='/kamala/' else txt

class PrbTxt(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stk=[];self.lng=[];self.phr=set()
    def handle_starttag(self,tag,attrs):
        dat=dict(attrs)
        if tag not in TAG_VOID:
            self.stk.append(tag)
            self.lng.append(dat.get('lang', self.lng[-1] if self.lng else 'en'))
        for key,val in attrs:
            if key in ATR_TXT and val and is_txt(val):self.phr.add(norm_txt(val))
        if tag=='meta' and dat.get('name',dat.get('property')) in META_TXT and is_txt(dat.get('content','')):
            self.phr.add(norm_txt(dat['content']))
    def handle_endtag(self,tag):
        if tag in self.stk:
            num=len(self.stk)-1-self.stk[::-1].index(tag)
            self.stk=self.stk[:num];self.lng=self.lng[:num]
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in TAG_VOID:self.handle_endtag(tag)
    def handle_data(self,txt):
        if not any(t in TAG_OMIT for t in self.stk) and (not self.lng or self.lng[-1].startswith('en')) and is_txt(txt):self.phr.add(norm_txt(txt))

def extract():
    phr=set()
    for p in base_files()+[pth_dst/'downloads/index.html']:
        if not p.exists():continue
        obj=PrbTxt();obj.feed(p.read_text());phr.update(obj.phr)
    # Literal UI messages cover state changes after a page has loaded.
    vals=json.loads(subprocess.check_output(['node', str(sys_rad/'scripts/extract-ui-strings.mjs')],text=True))
    for val in vals:
        val=norm_txt(val)
        if is_txt(val) and len(val)<1800 and not re.search(r'[<>={}\\]|https?://|^/|\b(?:import|function|const|throw|return)\b|\b(?:dat|frm|dmn|sys|txt|est|clv|pth|num|cnt)_|querySelector|^\W*[),+&.]|^install |^mkdir |^noopener',val) and (re.search(r'\s',val) or re.fullmatch('[A-Z][A-Za-z-]+',val)):
            phr.add(val)
    # Card and technique names can be inserted dynamically by the applications.
    def visit(v):
        if isinstance(v,dict):
            for k,x in v.items():
                if isinstance(x,str) and k in ('name','title','summary','meaning','notes','description','label') and is_txt(x):phr.add(norm_txt(x))
                elif isinstance(x,(dict,list)):visit(x)
        elif isinstance(v,list):
            for x in v:visit(x)
    for p in (sys_rad/'src').glob('*.json'):visit(json.loads(p.read_text()))
    (pth_loc/'source-strings.json').write_text(json.dumps(sorted(phr),ensure_ascii=False,indent=2)+'\n')
    print('Collected',len(phr),'translation units;',sum(len(x.split()) for x in phr),'words.')


def locale_url(url,loc,routes):
    dat=urlsplit(html.unescape(url))
    if dat.scheme or dat.netloc:return url
    if dat.path not in routes:return url
    path=('/'+loc if loc!='en' else '') + dat.path
    if path in ('/es/','/calo/'):pass
    return urlunsplit(('', '', path, dat.query, dat.fragment))

class LocHTML(PrbTxt):
    def __init__(self,catalog,loc,routes):
        super().__init__();self.cat=catalog;self.loc=loc;self.routes=routes;self.out=[]
    def trans(self,txt):
        norm=norm_txt(txt)
        if norm not in self.cat:
            if norm.startswith('Download ZIP ·'):return txt.replace('Download ZIP','Descargar ZIP',1)
            return txt
        return re.sub(r'\S(?:.*\S)?',lambda _:self.cat[norm],txt,flags=re.S)
    def handle_starttag(self,tag,attrs):
        raw=self.get_starttag_text();dat=dict(attrs)
        for key,val in attrs:
            new=val
            if val and (key in ATR_TXT or tag=='meta' and key=='content' and dat.get('name',dat.get('property')) in META_TXT):
                new=self.trans(val)
            if key=='href':new=locale_url(val,self.loc,self.routes)
            if tag=='html' and key=='lang':new='es' if self.loc=='es' else 'git-ES'
            if new!=val:
                pat=r'(?<![\w:-])'+re.escape(key)+r'''\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)'''
                raw=re.sub(pat,key+'="'+html.escape(new,quote=True)+'"',raw,count=1,flags=re.I)
        self.out.append(raw)
        if tag not in TAG_VOID:
            self.stk.append(tag)
            self.lng.append(dat.get('lang', self.lng[-1] if self.lng else 'en'))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in TAG_VOID:self.handle_endtag(tag,emit=False)
    def handle_endtag(self,tag,emit=True):
        if emit:self.out.append('</'+tag+'>')
        super().handle_endtag(tag)
    def handle_data(self,txt):
        if any(t in TAG_OMIT for t in self.stk):
            # Script and style raw text must retain exact bytes and syntax.
            self.out.append(txt if any(t in ('script','style') for t in self.stk) else html.escape(txt,quote=False))
        elif self.lng and not self.lng[-1].startswith('en'):
            self.out.append(html.escape(txt,quote=False))
        else:self.out.append(html.escape(self.trans(txt),quote=False))
    def handle_comment(self,txt):self.out.append('<!--'+txt+'-->')
    def handle_decl(self,txt):self.out.append('<!'+txt+'>')
    def handle_pi(self,txt):self.out.append('<?'+txt+'>')


def language_menu(route,loc):
    items=[]
    spokes=''.join('<line x1="30" y1="20" x2="'+str(30+10*math.sin(i*math.pi/8))+'" y2="'+str(20-10*math.cos(i*math.pi/8))+'"/>' for i in range(16))
    roma='<svg class="language-flag" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40" aria-hidden="true" focusable="false"><path fill="#1673d1" d="M0 0h60v20H0z"/><path fill="#16833e" d="M0 20h60v20H0z"/><g fill="none" stroke="#ef3038" stroke-width="1.8"><circle cx="30" cy="20" r="10"/>'+spokes+'</g></svg>'
    for code,label,flag in (('en','English','🇬🇧'),('es','Español','🇪🇸'),('calo','Caló ibérico',roma)):
        href=('/'+code if code!='en' else '')+route
        current=' aria-current="true"' if code==loc else ''
        items.append('<a href="'+href+'" data-locale="'+code+'" lang="'+('git-ES' if code=='calo' else code)+'" hreflang="'+('git-ES' if code=='calo' else code)+'" aria-label="'+label+'" title="'+label+'"'+current+'>'+flag+'</a>')
    return '<span class="language-menu" role="group" aria-label="Language / Idioma" data-no-translate>'+''.join(items)+'</span>'


def localized_title(original,loc,cat):
    brand=dat_met.get('titles',{}).get(loc,dat_met['title'])
    if original==dat_met['title']:return brand
    prefix=original.removesuffix(' · '+dat_met['title'])
    if prefix in cat:return cat[prefix]+' · '+brand
    # Reuse the retained translations when a shared brand suffix changes.
    old=cat.get(prefix+' · kamala.pro — Artes Mánticos')
    return (old.rsplit(' · ',1)[0] if old else prefix)+' · '+brand


def set_meta(txt,route,loc,original_title=None,catalog=None):
    if loc!='en':
        title=localized_title(original_title,loc,catalog)
        txt=re.sub(r'<title>.*?</title>',lambda m:'<title>'+html.escape(title)+'</title>',txt,flags=re.S)
        txt=re.sub(r'(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*',lambda m:m[1]+html.escape(title,quote=True),txt)
        brand=dat_met.get('titles',{}).get(loc,dat_met['title'])
        txt=re.sub(r'(<meta property="og:site_name" content=")[^"]*',lambda m:m[1]+html.escape(brand,quote=True),txt)
        image=dat_met.get('share_images',{}).get(loc,dat_met['share_image'])
        txt=txt.replace(dat_met['origin']+dat_met['share_image'],dat_met['origin']+image)
        mime='image/jpeg' if image.endswith(('.jpg','.jpeg')) else 'image/png'
        txt=re.sub(r'(<meta property="og:image:type" content=")[^"]*',lambda m:m[1]+mime,txt)
    can_route='/kamala' if route=='/contact/' else route
    path=('/'+loc if loc!='en' else '')+can_route
    canonical=dat_met['origin']+path
    txt=re.sub(r'<link rel="canonical"[^>]*>', '<link rel="canonical" href="'+canonical+'">',txt)
    txt=re.sub(r'(<meta (?:property|name)="(?:og:url|twitter:url)" content=")[^"]*',lambda m:m[1]+canonical,txt)
    txt=re.sub(r'<link rel="alternate"[^>]*hreflang=[^>]*>','',txt)
    links=[]
    # Search hreflang requires ISO 639-1; Calo uses its BCP 47 HTML tag instead.
    # Its approved pages remain crawlable through real links and the sitemap.
    if loc!='calo':
        for code in ('en','es'):
            url=dat_met['origin']+('/'+code if code!='en' else '')+can_route
            links.append('<link rel="alternate" hreflang="'+code+'" href="'+url+'">')
        links.append('<link rel="alternate" hreflang="x-default" href="'+dat_met['origin']+can_route+'">')
    if loc!='en':
        txt=txt.replace('content="en_US"','content="es_ES"')
        links.append('<script src="/i18n/runtime.js?v='+dat_met['release']+'" defer></script>')
        txt=txt.replace('<body','<body data-site-locale="'+loc+'"',1)
        txt=txt.replace('connect-src https://www.kamala.pro/api/entropy.php', 'connect-src &apos;self&apos; https://www.kamala.pro/api/entropy.php')
    txt=txt.replace('</head>','\n'+''.join(links)+'\n</head>')
    txt=re.sub(r'<span class="language-menu".*?</span>','',txt,flags=re.S)
    # Each desktop/mobile menu contains real links to the equivalent page.
    txt=re.sub(r'(<nav[^>]*id="main-nav-(?:top|bottom)".*?)(</nav>)',lambda m:m[1]+language_menu(route,loc)+m[2],txt,flags=re.S)
    if '<nav' not in txt or 'class="language-menu"' not in txt:
        txt=txt.replace('<main','<div class="section">'+language_menu(route,loc)+'</div><main',1)
    if loc=='calo':
        txt=re.sub(r'(<main\b)([^>]*>)',r'\1 lang="es"\2',txt,count=1)
        txt=txt.replace('</footer>','<a href="/calo/lengua/" lang="git-ES">Diquelar el léxico ↗</a></footer>')
    if route=='/contact/':
        dest=('/'+loc if loc!='en' else '')+'/kamala'
        txt=re.sub(r'content="0;url=[^"]*"','content="0;url='+dest+'"',txt)
    return txt


def build(downloads_only=False):
    es=json.loads((pth_loc/'es.json').read_text())
    overrides=json.loads((pth_loc/'es.overrides.json').read_text()) if (pth_loc/'es.overrides.json').exists() else {}
    es.update(overrides)
    for key,val in list(es.items()):
        # Published titles retain the project's exact brand spelling.
        suffix=' · '+dat_met['title']
        if key.endswith(suffix):
            prefix=key[:-len(suffix)]
            es[key]=es.get(prefix,val.rsplit(' · ',1)[0])+suffix
        if key.endswith('↗') and not es[key].endswith('↗'):
            es[key]=es[key].rstrip(' ,.;')+' ↗'
    calo=dict(es);calo.update(json.loads((pth_loc/'calo.overrides.json').read_text()))
    files=[pth_dst/'downloads/index.html'] if downloads_only else base_files()
    routes={route_pag(p) for p in base_files()}|{'/downloads/'}
    routes|={r.rstrip('/')+'/' for r in routes if r!='/' and not r.endswith('/')}
    (pth_dst/'i18n').mkdir(exist_ok=True)
    for p in files:
        route=route_pag(p)
        base=p.read_text()
        base=re.sub(r'<link rel="alternate"[^>]*hreflang=[^>]*>','',base)
        base=re.sub(r'<span class="language-menu".*?</span>','',base,flags=re.S)
        p.write_text(set_meta(base,route,'en'))
        original_title=html.unescape(re.search(r'<title>(.*?)</title>',base,re.S)[1])
        for loc,cat in (('es',es),('calo',calo)):
            parser=LocHTML(cat,loc,routes);parser.feed(base)
            txt=set_meta(''.join(parser.out),route,loc,original_title,cat)
            dst=pth_dst/loc/p.relative_to(pth_dst)
            dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(txt)
    if not downloads_only:
        # The public lexicon retains documented variants and source attribution.
        txt_rev=(pth_dst/'calo/kamala/index.html').read_text()
        lex=json.loads((pth_loc/'calo-lexicon.json').read_text())
        txt_lex=(pth_loc/'calo-language.html').read_text()
        categories=sorted({x['category'] for x in lex['entries']})
        txt_lex=txt_lex.replace('<!-- CALO CATEGORIES -->',''.join('<option value="'+html.escape(x,quote=True)+'">'+html.escape(x)+'</option>' for x in categories))
        txt_lex=txt_lex.replace('<!-- CALO COUNT -->',str(len(lex['entries']))+' voces documentadas')
        rows=[]
        for entry in sorted(lex['entries'],key=lambda x:x['term']):
            source=lex['sources'][entry['source']]
            variants='<small>'+html.escape('; '.join(entry['variants']))+'</small>' if entry['variants'] else ''
            note='<small>'+html.escape(entry['note'])+'</small>' if entry['note'] else ''
            ref=source['label']+(' · voz '+str(entry['entry']) if entry['source']=='ugr' else '')
            rows.append('<tr data-calo-entry data-category="'+html.escape(entry['category'],quote=True)+'"><th scope="row"><span lang="git-ES">'+html.escape(entry['term'])+'</span>'+variants+'</th><td>'+html.escape(entry['es'])+note+'</td><td>'+html.escape(entry['category'])+'</td><td><a href="'+source['url']+'" target="_blank" rel="noopener">'+html.escape(ref)+' ↗</a></td></tr>')
        txt_lex=txt_lex.replace('<!-- CALO ENTRIES -->',''.join(rows))
        txt_rev=re.sub(r'<main\b[^>]*>.*?</main>',lambda m:'<main id="main" lang="es">'+txt_lex+'</main>',txt_rev,flags=re.S)
        txt_rev=re.sub(r'<title>.*?</title>','<title>Caló ibérico: criterios y vocabulario · Kamala</title>',txt_rev,flags=re.S)
        txt_rev=txt_rev.replace(dat_met['origin']+'/calo/kamala',dat_met['origin']+'/calo/lengua/')
        txt_rev=re.sub(r'(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*',lambda m:m[1]+'Caló ibérico: criterios y vocabulario · Kamala',txt_rev)
        txt_rev=re.sub(r'(<meta (?:property|name)="(?:description|og:description|twitter:description)" content=")[^"]*',lambda m:m[1]+'Léxico público del caló ibérico: 84 voces documentadas, variantes, equivalencias y fuentes.',txt_rev)
        # This Calo-only reference has no contact-page equivalent in other languages.
        txt_menu=language_menu('/glossary/','calo').replace('href="/calo/glossary/"','href="/calo/lengua/"')
        txt_rev=re.sub(r'<span class="language-menu".*?</span>',lambda m:txt_menu,txt_rev,flags=re.S)
        txt_rev=txt_rev.replace('</body>','<script src="/i18n/calo-lexicon.js?v='+dat_met['release']+'" defer></script></body>')
        dst=pth_dst/'calo/lengua/index.html';dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(txt_rev)
    for loc,cat in (('es',es),('calo',json.loads((pth_loc/'calo.overrides.json').read_text()))):
        (pth_dst/'i18n'/f'{loc}.json').write_text(json.dumps(cat,ensure_ascii=False,separators=(',',':')))
    (pth_dst/'i18n/runtime.js').write_text((pth_loc/'runtime.js').read_text())
    (pth_dst/'i18n/calo-lexicon.js').write_text((pth_loc/'calo-lexicon.js').read_text())
    # Locale UI is shared; never modify the existing application selectors.
    css=(pth_loc/'languages.css').read_text()
    style=(pth_dst/'v2.css').read_text()
    if '/* KAMALA LOCALES */' not in style:(pth_dst/'v2.css').write_text(style+'\n'+css)
    if not downloads_only:
        # The original host keeps its mail form while receiving the new menu.
        txt_ctc=(pth_dst/'kamala/index.html').read_text()
        pth_frag=sys_rad/'deploy/site-update/fragments'
        (pth_frag/'contact-header.html').write_text(re.search(r'<header class="site-menu">.*?</header>',txt_ctc,re.S)[0])
        (pth_frag/'contact-footer.html').write_text(re.search(r'<footer>.*?</footer>',txt_ctc,re.S)[0])
        paths=sorted({route_pag(p) for p in base_files() if route_pag(p)!='/contact/'})
        urls=[dat_met['origin']+prefix+r for prefix in ('','/es','/calo') for r in paths]
        urls.append(dat_met['origin']+'/calo/lengua/')
        (pth_dst/'sitemaps.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+html.escape(u)+'</loc></url>' for u in urls)+'</urlset>')
    print('Localized',len(files),'routes: English, Spanish and approved Calo edition.')

if __name__=='__main__':
    if '--extract' in sys.argv:extract()
    else:build('--downloads-only' in sys.argv)
