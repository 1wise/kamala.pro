#!/usr/bin/env python3
# Timestamp: 2026-11-02
# Version: 2.1.1
# Author & Credits: https://www.alawise.es/1-s
"""Publish downloadable release files without nesting generated archives."""

import hashlib
import html
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


sys_rad = Path(__file__).resolve().parents[1]
dat_met = json.loads((sys_rad / 'src/site.json').read_text())
pth_dst = sys_rad / 'dist/downloads'
pth_dst.mkdir(parents=True, exist_ok=True)
pth_arc = 'kamala-pro-' + dat_met['release']
pth_src = sys_rad / 'releases' / (pth_arc + '-excalibur.zip')
shutil.copy2(pth_src, pth_dst / pth_src.name)

# Include the current source and built pages, with no release history or Git data.
if (sys_rad / '.git').exists():
    dat_nom = subprocess.check_output(
        ['git', 'ls-files', '-co', '--exclude-standard', '-z'], cwd=sys_rad
    ).decode().split('\0')
else:
    # A downloaded source ZIP can be repackaged before its first Git commit.
    dat_nom = [str(pth_fil.relative_to(sys_rad)) for pth_fil in sys_rad.rglob('*')
               if pth_fil.relative_to(sys_rad).parts[0] in
               ('src', 'dist', 'scripts', 'tests', 'deploy', 'legacy', '.openai')
               or pth_fil.name in ('.gitignore', 'ASSETS.md', 'GIT.md', 'README.md',
                                   'package.json', 'package-lock.json')]
with zipfile.ZipFile(pth_dst / (pth_arc + '-proyecto-git.zip'), 'w',
                     zipfile.ZIP_DEFLATED, compresslevel=9) as sys_fil:
    for txt_val in sorted(set(dat_nom)):
        if not txt_val:
            continue
        pth_rel = Path(txt_val)
        if pth_rel.parts[0] == 'releases' or pth_rel.parts[:2] == ('dist', 'downloads'):
            continue
        # The historical unrendered portrait remains in Git; current bronze faces ship.
        if str(pth_rel) == 'src/assets/coin-portrait.png':
            continue
        # Source assets are included once; the build restores their deployed copies.
        if pth_rel.parts[:2] == ('dist', 'assets') and (sys_rad / 'src' / Path(*pth_rel.parts[1:])).is_file():
            continue
        if any(clv_esc.startswith('qa-') for clv_esc in pth_rel.parts):
            continue
        if any(clv_esc in ('node_modules', 'vendor', '__pycache__', 'consultas') for clv_esc in pth_rel.parts):
            continue
        if pth_rel.name in ('config.php', 'astroapp-config.json', '.env'):
            continue
        if pth_rel.suffix in ('.key', '.pem', '.p12', '.pfx', '.log', '.pyc'):
            continue
        pth_fil = sys_rad / pth_rel
        if pth_fil.is_file() and not pth_fil.is_symlink():
            sys_fil.write(pth_fil, Path('kamala-pro') / pth_rel)

pth_tar = pth_dst / (pth_arc + '-barajas-completas.zip')
with zipfile.ZipFile(pth_tar, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as sys_fil:
    for txt_nom in ('tarot.json', 'playing-cards.json'):
        for dat_itm in json.loads((sys_rad / 'src' / txt_nom).read_text())['cards']:
            pth_fil = sys_rad / 'src' / dat_itm['art'].lstrip('/')
            sys_fil.write(pth_fil, Path('tarot' if txt_nom == 'tarot.json' else 'playing-cards') / pth_fil.name)
        sys_fil.write(sys_rad / 'src' / txt_nom, txt_nom)
    sys_fil.write(sys_rad / 'src/playing-cards-art.json', 'playing-cards-art.json')
    sys_fil.write(sys_rad / 'ASSETS.md', 'ASSETS.md')

dat_fil = []
for pth_fil in (pth_dst / pth_src.name, pth_dst / (pth_arc + '-proyecto-git.zip'), pth_tar):
    with zipfile.ZipFile(pth_fil) as sys_fil:
        if sys_fil.testzip() is not None:
            raise ValueError('Archive integrity check failed: ' + pth_fil.name)
    txt_val = hashlib.sha256(pth_fil.read_bytes()).hexdigest()
    pth_fil.with_suffix('.zip.sha256').write_text(txt_val + '  ' + pth_fil.name + '\n')
    dat_fil.append({'name': pth_fil.name, 'size': pth_fil.stat().st_size, 'sha': txt_val})

txt_pag = '''<!doctype html>
<!-- Timestamp: 2026-11-02 | Version: 2.1.1 | Author & Credits: https://www.alawise.es/1-s -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Project downloads · kamala.pro</title>
<link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/v2.css">
<style>.release-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:24px}
.release-grid article{border:1px solid #433951;padding:28px}.release-grid h2{font-size:30px}
.release-grid code{display:block;font-size:11px;overflow-wrap:anywhere;margin-top:20px}
.release-grid a{display:inline-block;margin:12px 14px 0 0}h1{font-size:clamp(40px,6vw,70px)}</style></head>
<body><main class="section"><a class="back-link" href="/apps/entropy/">KAMALA / ENTROPY LAB</a>
<div class="eyebrow">RELEASE ''' + html.escape(dat_met['release']) + '''</div><h1>Project downloads.</h1>
<p>Choose the server update, source project, all three illustrated decks or the portable laboratory.</p><div class="release-grid">'''
for dat_itm, txt_tit, txt_note in zip(dat_fil,
        ('Excalibur update', 'Source project for Git', 'All three decks · 178 images'),
        ('Unzip outside the public root and follow INSTALAR.md. The installer keeps the existing application configuration.',
         'Source, current artwork, baseline pages and packaging tools. Run npm ci and npm run build before deployment; generated asset copies, the unused historical portrait and binary release history are omitted.',
         'Complete Spanish, American and Marseille decks: 62 individual court/major illustrations, 116 exact pip cards, image maps and the art prompts.')):
    txt_pag += '<article><h2>' + txt_tit + '</h2><p>' + txt_note + '</p>'
    txt_pag += '<a class="button" href="' + dat_itm['name'] + '" download>Download ZIP · ' + format(dat_itm['size'] / 1048576, '.1f') + ' MiB</a>'
    txt_pag += '<a href="' + dat_itm['name'] + '.sha256" download>SHA-256</a><code>' + dat_itm['sha'] + '</code></article>'
txt_pag += '''<article><h2>Portable entropy lab</h2><p>All four generators in one HTML file: SSH pairs, secrets and encodings, TOTP, and ASCII seed art.</p>
<a class="button" href="/assets/keys-lab.html" download>Download HTML</a>
<p class="quiet-note">The file contains the application. Generated session values are kept in the local tab.</p></article>
</div><p class="quiet-note">The ZIP checksums are available beside each download.</p></main></body></html>'''
(pth_dst / 'index.html').write_text(txt_pag)
print('Built hosted downloads: ' + ', '.join(dat_itm['name'] for dat_itm in dat_fil))
