#!/usr/bin/env python3
# Timestamp: 2026-11-18 | Version: 2.5.2
# Author & Credits: https://www.alawise.es/1-s
"""Verify translated routes without changing sensor and application contracts."""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

sys_rad=Path(__file__).resolve().parents[1]
pth_dst=sys_rad/'dist'
dat_met=json.loads((sys_rad/'src/site.json').read_text())

class Pag(HTMLParser):
    def __init__(self,txt):
        super().__init__();self.ids=[];self.assets=[];self.values=[];self.links=[];self.lang=None;self.canonical=None;self.alt={}
        self.feed(txt)
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='html':self.lang=d.get('lang')
        if 'id' in d:self.ids.append(d['id'])
        if 'src' in d and not d['src'].startswith('/i18n/'):self.assets.append(d['src'])
        if tag in ('input','option'):self.values.append((tag,d.get('name'),d.get('value'),d.get('type')))
        if 'href' in d:self.links.append(d['href'])
        if tag=='link' and d.get('rel')=='canonical':self.canonical=d['href']
        if tag=='link' and d.get('rel')=='alternate':self.alt[d['hreflang']]=d['href']
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)

cnt=0
for base in pth_dst.rglob('index.html'):
    rel=base.relative_to(pth_dst)
    if rel.parts[0] in ('es','calo','downloads') or any(s.startswith('qa-') for s in rel.parts):continue
    txt_en=base.read_text()
    en=Pag(txt_en)
    assert 'Mantic Arts' in re.search(r'<title>(.*?)</title>',txt_en,re.S)[1],base
    for txt_menu in re.findall(r'<span class="language-menu".*?</span>',txt_en,re.S):
        assert txt_menu.count('data-locale=')==3 and txt_menu.count('aria-current="true"')==1,base
        assert '🇬🇧' in txt_menu and '🇪🇸' in txt_menu and 'class="language-flag"' in txt_menu,base
        # Visible labels contain flags only; names remain in accessible attributes.
        assert not re.sub(r'<[^>]+>','',txt_menu).isascii(),base
        assert not re.search(r'[A-Za-z]',re.sub(r'<[^>]+>','',txt_menu)),base
    route='/'+str(rel).removesuffix('index.html')
    if route in ('/kamala/','/contact/'):route='/kamala'
    for loc in ('es','calo'):
        path=pth_dst/loc/rel;txt=path.read_text();p=Pag(txt)
        assert p.ids==en.ids,(loc,route,'app IDs changed')
        assert p.assets==en.assets,(loc,route,'source URL changed')
        assert p.values==en.values,(loc,route,'input values changed')
        assert len(p.ids)==len(set(p.ids)),path
        assert p.lang==('es' if loc=='es' else 'git-ES')
        assert p.canonical==dat_met['origin']+'/'+loc+route,(path,p.canonical)
        if loc=='es':
            assert p.alt['en']==dat_met['origin']+route
            assert p.alt['es']==dat_met['origin']+'/es'+route
            assert p.alt['x-default']==dat_met['origin']+route
        else:
            assert p.alt=={},(path,'unsupported search language annotation')
        assert 'aria-label="English"' in txt and 'aria-label="Español"' in txt and 'data-locale="calo"' in txt
        if loc=='calo':
            assert 'edición en revisión' not in txt and 'class="locale-note"' not in txt,path
            assert re.findall(r'<meta name="robots"[^>]*>',txt)==re.findall(r'<meta name="robots"[^>]*>',txt_en),path
            assert 'aria-label="Caló ibérico"' in txt,path
        for link in p.links:
            u=urlsplit(link)
            if u.scheme or u.netloc or not u.path.startswith('/'):continue
            target=pth_dst/u.path.lstrip('/')
            if target.is_dir():target/='index.html'
            assert target.exists(),(path,link)
        # Inline application code must survive localization byte for byte.
        scripts=lambda t:re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',t,re.S)
        assert scripts(txt)==scripts(base.read_text()),path
    cnt+=1
assert cnt==138,cnt
map_txt=(pth_dst/'sitemaps.xml').read_text()
assert '/es/techniques/pendulum/' in map_txt and '/calo/techniques/pendulum/' in map_txt
assert '<loc>https://www.kamala.pro/calo/lengua/</loc>' in map_txt
assert '<loc>https://www.kamala.pro/calo/kamala</loc>' in map_txt
assert 'noindex' not in (pth_dst/'calo/index.html').read_text()
assert '<loc>https://www.kamala.pro/kamala</loc>' in map_txt
assert '<loc>https://www.kamala.pro/es/kamala</loc>' in map_txt
es=(pth_dst/'es/api/index.html').read_text()
assert 'drogodependencias' not in es and 'minentropía' in es
assert 'no cuenta con una certificación de fuente de entropía' in es
assert 'FastCGI como acceso educativo al análisis estadístico' in es
assert '<title>Mantic Arts · Kamala</title>' in (pth_dst/'index.html').read_text()
assert '<title>Artes Mánticos · Kamala</title>' in (pth_dst/'es/index.html').read_text()
lex=json.loads((sys_rad/'src/i18n/calo-lexicon.json').read_text())
assert len(lex['entries'])==84 and len({x['category'] for x in lex['entries']})==8
txt_lex=(pth_dst/'calo/lengua/index.html').read_text()
assert txt_lex.count('data-calo-entry')==84 and 'data-calo-query' in txt_lex
assert 'borrador' not in txt_lex and 'noindex' not in txt_lex
assert Pag(txt_lex).canonical==dat_met['origin']+'/calo/lengua/'
assert 'The public site offers vocabulary, tools and technical observations' in (pth_dst/'approach/index.html').read_text()
assert 'reserved mantic teachings' in (pth_dst/'traditions/roma/index.html').read_text()
assert 'does not ask for the words, transcription or reconstruction' in (pth_dst/'traditions/shamanic/karelian-finnic/index.html').read_text()
print('138 equivalent routes per language: locale metadata, links, app IDs, source URLs, input values, inline code and scientific qualifications passed.')
