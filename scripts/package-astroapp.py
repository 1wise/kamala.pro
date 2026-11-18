#!/usr/bin/env python3
# Timestamp: 2026-10-30
# Version: 2.0.3
# Author and Credits: https://www.alawise.es/1-s
"""Package chart and navigation fixes without copying private mail modules."""

import hashlib
import json
import zipfile
from pathlib import Path

sys_rad = Path(__file__).resolve().parents[1]
dat_met = json.loads((sys_rad / 'src/site.json').read_text())
pth_dst = sys_rad / 'releases' / ('kamala-pro-' + dat_met['release'] + '-astrology-update.zip')
pth_dst.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(pth_dst, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as sys_fil:
    for pth_fil in sorted((sys_rad / 'dist').rglob('index.html')):
        if any(txt_val.startswith('qa-') for txt_val in pth_fil.parts) or pth_fil.relative_to(sys_rad / 'dist').as_posix() == 'contact/index.html':
            continue
        sys_fil.write(pth_fil, Path('html') / pth_fil.relative_to(sys_rad / 'dist'))
    for pth_rel in ('astroapp-core.mjs', 'astroapp.js', 'astroapp-frame.js', 'astroapp-head.js', 'astroapp.css', 'v2.css', 'lab.js', 'lab.css', 'assets/keys-lab-' + dat_met['release'] + '.html'):
        sys_fil.write(sys_rad / 'dist' / pth_rel, Path('html') / pth_rel)
    for pth_src, pth_rel in (
        ('deploy/site-update/install_v2.py', 'tools/install_v2.py'),
        ('deploy/site-update/update_contact_page.py', 'tools/update_contact_page.py'),
        ('deploy/astroapp/configure_head.py', 'tools/configure_head.py'),
        ('deploy/astroapp/CHARTS.md', 'INSTALAR-ASTROLOGIA.md'),
    ):
        sys_fil.write(sys_rad / pth_src, pth_rel)
    for pth_fil in sorted((sys_rad / 'deploy/site-update/fragments').glob('*')):
        sys_fil.write(pth_fil, Path('tools/fragments') / pth_fil.name)
    assert not any(txt_val.startswith('private/') or txt_val.endswith('/astroapp-config.json') for txt_val in sys_fil.namelist())
txt_val = hashlib.sha256(pth_dst.read_bytes()).hexdigest()
pth_dst.with_suffix('.zip.sha256').write_text(txt_val + '  ' + pth_dst.name + '\n')
print(str(pth_dst))
print('SHA256 ' + txt_val)
