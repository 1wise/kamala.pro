#!/usr/bin/env python3
# Timestamp: 2026-11-01
# Version: 2.1.0
# Author & Credits: https://www.alawise.es/1-s
"""Check metadata, shared navigation and article experiments across all routes."""

import base64
import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys_rad = Path(__file__).resolve().parents[1]
pth_dst = sys_rad / 'dist'
dat_met = json.loads((sys_rad / 'src/site.json').read_text())


class PrbPag(HTMLParser):
    def __init__(self, txt_pag):
        super().__init__()
        self.dat_met = {}
        self.dat_dst = []
        self.dat_env = []
        self.txt_nav = []
        self.cfg_apl = Counter()
        self.est_mnu = False
        self.feed(txt_pag)

    def handle_starttag(self, txt_val, dat_env):
        dat_itm = dict(dat_env)
        self.cfg_apl[txt_val] += 1
        if dat_itm.get('id'):
            self.dat_dst.append(dat_itm['id'])
        if txt_val == 'nav' and dat_itm.get('id') == 'main-nav-top':
            self.est_mnu = True
        if txt_val == 'meta':
            clv_esc = dat_itm.get('name', dat_itm.get('property'))
            if clv_esc:
                assert clv_esc not in self.dat_met, 'Duplicate meta: ' + clv_esc
                self.dat_met[clv_esc] = dat_itm.get('content')
        if txt_val == 'link' and dat_itm.get('rel') == 'canonical':
            assert 'canonical' not in self.dat_met
            self.dat_met['canonical'] = dat_itm['href']
        if self.est_mnu and txt_val == 'a':
            self.txt_nav.append(dat_itm['href'])
        for clv_esc in ('src', 'href'):
            if dat_itm.get(clv_esc):
                self.dat_env.append(dat_itm[clv_esc])

    def handle_endtag(self, txt_val):
        if txt_val == 'nav':
            self.est_mnu = False


# Release downloads have their own file-integrity validation in the packager.
dat_esc = {pth_fil: PrbPag(pth_fil.read_text()) for pth_fil in pth_dst.rglob('index.html') if pth_fil.parent != pth_dst / 'downloads'}
assert len(dat_esc) == 78 + len(json.loads((sys_rad / "src/glossary.json").read_text())["entries"]) + 9
for pth_fil, dat_itm in dat_esc.items():
    pth_pag = '/' + pth_fil.parent.relative_to(pth_dst).as_posix().strip('.')
    pth_pag = '/' if pth_pag == '/' else pth_pag + '/'
    url_can = dat_met['origin'] + pth_pag
    assert dat_itm.cfg_apl['h1'] == dat_itm.cfg_apl['main'] == dat_itm.cfg_apl['title'] == 1, pth_pag
    assert len(dat_itm.dat_dst) == len(set(dat_itm.dat_dst)), pth_pag
    assert dat_itm.txt_nav == dat_esc[pth_dst / 'index.html'].txt_nav, pth_pag
    assert dat_itm.dat_met['canonical'] == dat_itm.dat_met['og:url'] == dat_itm.dat_met['twitter:url'] == url_can
    assert dat_itm.dat_met['kamala:release'] == dat_met['release']
    assert dat_itm.dat_met['og:site_name'] == dat_met['title']
    assert dat_itm.dat_met['description'] == dat_itm.dat_met['og:description'] == dat_itm.dat_met['twitter:description']
    assert dat_itm.dat_met['twitter:card'] == 'summary_large_image'
    assert dat_itm.dat_met['og:title'] == dat_itm.dat_met['twitter:title']
    assert dat_itm.dat_met['og:title'].endswith(dat_met['title'])
    assert dat_itm.dat_met['og:image'] == dat_itm.dat_met['twitter:image'] == dat_met['origin'] + dat_met['share_image']
    assert dat_itm.dat_met['og:image:width'] == '1200' and dat_itm.dat_met['og:image:height'] == '630'
    for pth_lnk in dat_itm.dat_env:
        dat_fnt = urlsplit(pth_lnk)
        if dat_fnt.scheme or dat_fnt.netloc:
            continue
        pth_src = pth_dst / dat_fnt.path.lstrip('/') if dat_fnt.path.startswith('/') else pth_fil.parent / dat_fnt.path
        if pth_src.is_dir():
            pth_src /= 'index.html'
        assert pth_src.exists(), (pth_pag, pth_lnk)
        if dat_fnt.fragment and pth_src in dat_esc:
            assert unquote(dat_fnt.fragment) in dat_esc[pth_src].dat_dst, (pth_pag, pth_lnk)
    assert 'Status ↗' not in pth_fil.read_text()

for clv_esc in ('dice', 'coins', 'cards', 'runes', 'yijing', 'entropy-streams'):
    txt_pag = (pth_dst / 'techniques' / clv_esc / 'index.html').read_text()
    assert txt_pag.count('data-chance-app=') == 1
    assert 'id="experiment"' in txt_pag and ('src="/entropy.js?v=' + dat_met['release'] + '"') in txt_pag
    assert '<meta property="og:type" content="article">' in txt_pag

txt_hom = (pth_dst / 'index.html').read_text()
assert '<title>' + dat_met['title'] + '</title>' in txt_hom
assert 'class="home-control" src="https://go.1-s.es/"' in txt_hom
assert not re.search(r'<a[^>]+href="https://go\.1-s\.es/', txt_hom)
assert (pth_dst / dat_met['share_image'].lstrip('/')).is_file()
assert '/scales/hand/' in dat_esc[pth_dst / 'index.html'].txt_nav
assert (pth_dst / 'apps/yijing/index.html').is_file()
for clv_esc in ('cards', 'coins', 'dice', 'runes', 'yijing'):
    assert 'HAND SCALE / TECHNIQUE' in (pth_dst / 'techniques' / clv_esc / 'index.html').read_text()
for clv_esc in ('handreading', 'kinesthesia', 'clairvoyance', 'lucid-dreaming'):
    assert 'HUMAN SCALE / TECHNIQUE' in (pth_dst / 'techniques' / clv_esc / 'index.html').read_text()
print(str(len(dat_esc)) + ' pages: metadata, menus, assets, experiments and distinct Hand/Human scale placement passed.')

# The provider loader belongs only to the astrology workspace. No active code ships.
txt_ast = (pth_dst / 'astrology/index.html').read_text()
assert 'data-astroapp' in txt_ast and 'data-astroapp-calculate disabled' in txt_ast
assert txt_ast.index('src="/astroapp.js?v=' + dat_met['release']) < txt_ast.index('</head>')
assert 'NEXT INSTRUMENT / PLANNED' not in txt_ast
assert 'astroapp.js' not in (pth_dst / 'apps/entropy/index.html').read_text()
assert not (pth_dst / 'astroapp-config.json').exists()
for pth_fil in dat_esc:
    if pth_fil == pth_dst / 'astrology/index.html':
        assert 'astroapp-head.js' in pth_fil.read_text()
    else:
        assert 'astroapp-head.js' not in pth_fil.read_text(), pth_fil
        assert 'astroapp.com/astro/astroapi' not in pth_fil.read_text(), pth_fil
for pth_fil in ('astroapp.js', 'astroapp-frame.js', 'astroapp-core.mjs', 'astroapp.css'):
    assert (pth_dst / pth_fil).is_file()
print('AstroApp workspace, head controller, separate config and unchanged key-lab isolation passed.')

# Preserve the full exhibition when extending the SSH section.
txt_lab = (pth_dst / 'apps/entropy/index.html').read_text()
for clv_esc in ('ssh-keys', 'random-secrets', 'totp-setup', 'seed-art'):
    assert 'id="' + clv_esc + '"' in txt_lab
for clv_esc in ('hex', 'base64', 'base64url', 'base32', 'uuid'):
    assert 'value="' + clv_esc + '"' in txt_lab
assert 'href="/assets/keys-lab.html"' in txt_lab
txt_lab = (pth_dst / 'assets/keys-lab.html').read_text()
for pth_fil in ('keys-lab-2.0.0.html', 'keys-lab-2.0.4.html', 'keys-lab-' + dat_met['release'] + '.html'):
    assert (pth_dst / 'assets' / pth_fil).read_text() == txt_lab
for clv_esc in ('script', 'style'):
    dat_nom = re.findall('<' + clv_esc + '>(.*?)</' + clv_esc + '>', txt_lab, re.S)
    assert len(dat_nom) == 1
    txt_val = base64.b64encode(hashlib.sha256(dat_nom[0].encode()).digest()).decode()
    assert "'sha256-" + txt_val + "'" in txt_lab
print('Complete lab generators, portable download aliases and script/style CSP hashes passed.')
