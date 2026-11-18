#!/usr/bin/env python3
# Timestamp: 2026-11-18
# Version: 2.4.4
# Author & Credits: https://www.alawise.es/1-s
"""Restore the verified 2.4.0 feature pages after the baseline static build."""
import html
import json
import re
import shutil
from pathlib import Path
from page_meta import crt_met, dat_met

sys_rad = Path(__file__).resolve().parents[1]
pth_dst = sys_rad / 'dist'
pth_src = sys_rad / 'src/recovered-2.4.0'
txt_hom = (pth_dst / 'index.html').read_text()
txt_nav = re.search(r'<header class="site-menu">.*?</header>', txt_hom, re.S)[0]
txt_btm = re.search(r'<header class="site-menu menu-bottom">.*?</header>', txt_hom, re.S)[0]
txt_ftr = re.search(r'<footer>.*?</footer>', (pth_dst / 'approach/index.html').read_text(), re.S)[0]

for pth_fil in (pth_src / 'public').rglob('*'):
    if not pth_fil.is_file():
        continue
    pth_rel = pth_fil.relative_to(pth_src / 'public')
    (pth_dst / pth_rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pth_fil, pth_dst / pth_rel)

for pth_rel in json.loads((pth_src / 'pages.json').read_text()):
    txt_pag = (pth_src / 'pages' / pth_rel).read_text()
    url_pag = '/' + pth_rel.removesuffix('index.html')
    tit_pag = html.unescape(re.search(r'<title>(.*?)</title>', txt_pag, re.S)[1]).split(' · ')[0]
    dat_des = re.search(r'<meta name="description" content="([^"]*)">', txt_pag)
    txt_des = html.unescape(dat_des[1]) if dat_des else tit_pag
    txt_met = crt_met(url_pag, tit_pag, txt_des)
    if '<!-- KAMALA META START -->' in txt_pag:
        txt_pag = re.sub(r'<!-- KAMALA META START -->.*?<!-- KAMALA META END -->', lambda m: txt_met, txt_pag, flags=re.S)
    else:
        txt_pag = re.sub(r'<title>.*?</title>|<link rel="canonical"[^>]*>|<meta (?:name="(?:description|twitter:[^"]+|kamala:release)"|property="og:[^"]+")[^>]*>', '', txt_pag, flags=re.S)
        txt_pag = txt_pag.replace('</head>', txt_met + '</head>')
    def crt_nav(dat_mat):
        txt_val = txt_btm if 'menu-bottom' in dat_mat[0].split('>', 1)[0] else txt_nav
        txt_val = txt_val.replace(' aria-current="page"', '')
        return txt_val.replace('href="' + url_pag + '"', 'href="' + url_pag + '" aria-current="page"')
    txt_pag = re.sub(r'<header class="site-menu[^\"]*">.*?</header>', crt_nav, txt_pag, flags=re.S)
    txt_pag = re.sub(r'<footer>.*?</footer>', lambda m: txt_ftr, txt_pag, flags=re.S)
    txt_pag = re.sub(r'\?v=[0-9.]+', '?v=' + dat_met['release'], txt_pag)
    # The static mirror reads public host telemetry; no measurements are simulated.
    txt_pag = re.sub(r'data-endpoint="(/telemetry[^\"]*)"', r'data-endpoint="https://www.kamala.pro\1"', txt_pag)
    if 'data-endpoint=' in txt_pag and url_pag in ('/techniques/pendulum/live/', '/techniques/crystallization/'):
        txt_note = '<p class="section quiet-note">Live measurements are supplied by the original observatory. If this mirror cannot read the feed, <a href="https://www.kamala.pro' + url_pag + '" target="_blank" rel="noopener">open the original live workspace ↗</a>.</p>'
        txt_pag = txt_pag.replace('</main>', txt_note + '</main>')
    pth_pag = pth_dst / pth_rel
    pth_pag.parent.mkdir(parents=True, exist_ok=True)
    pth_pag.write_text(txt_pag)

# Rebuild the sitemap from the complete restored route set.
dat_url = sorted('/kamala' if p.parent == pth_dst / 'kamala' else '/' + str(p.relative_to(pth_dst)).removesuffix('index.html') for p in pth_dst.rglob('index.html') if p.parent not in (pth_dst / 'downloads', pth_dst / 'contact'))
txt_map = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + html.escape(dat_met['origin'] + u) + '</loc></url>' for u in dat_url) + '</urlset>'
(pth_dst / 'sitemaps.xml').write_text(txt_map)
print('Restored 15 feature pages, original modules, assets, Time navigation and the complete sitemap.')
