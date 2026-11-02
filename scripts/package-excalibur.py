#!/usr/bin/env python3
# Timestamp: 2026-11-02
# Version: 2.1.1
# Author and Credits: https://www.alawise.es/1-s
"""Package a cumulative Excalibur overlay without active host credentials."""
import hashlib
import json
import zipfile
from pathlib import Path
sys_rad=Path(__file__).resolve().parents[1]
dat_met=json.loads((sys_rad/'src/site.json').read_text())
pth_dst=sys_rad/'releases'/('kamala-pro-'+dat_met['release']+'-excalibur.zip')
pth_dst.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(pth_dst,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as sys_fil:
    for pth_fil in sorted((sys_rad/'dist').rglob('*')):
        if not pth_fil.is_file():continue
        pth_rel=pth_fil.relative_to(sys_rad/'dist')
        # Hosted download bundles are generated after this overlay to avoid recursion.
        if pth_rel.parts[0]=='downloads' or any(clv_esc.startswith('qa-') for clv_esc in pth_rel.parts) or str(pth_rel) in ('app.js','contact/index.html','contact/send.php','astroapp-config.json','assets/coin-portrait.png') or pth_rel.suffix=='.php':continue
        sys_fil.write(pth_fil,Path('html')/pth_rel)
    for pth_fil,pth_rel in [
        ('deploy/entropy/public/api/entropy.php','html/api/entropy.php'),
        ('deploy/potpourri/public/potpourri/send.php','html/potpourri/send.php'),
        ('deploy/send/private/send.php','private/send/send.php'),
        ('deploy/astroapp/configure_head.py','tools/configure_head.py'),
        ('deploy/site-update/install_v2.py','tools/install_v2.py'),
        ('deploy/site-update/update_contact_page.py','tools/update_contact_page.py'),
        ('deploy/astroapp/astroapp-config.example.json','examples/astroapp-config.example.json'),
    ]:
        sys_fil.write(sys_rad/pth_fil,pth_rel)
    for pth_fil in sorted((sys_rad/'deploy/site-update').glob('*.md')):sys_fil.write(pth_fil,pth_fil.name)
    for pth_fil in sorted((sys_rad/'deploy/site-update/fragments').glob('*')):sys_fil.write(pth_fil,Path('tools/fragments')/pth_fil.name)
    for pth_fil in sorted((sys_rad/'deploy/fedora44').glob('*.conf')):sys_fil.write(pth_fil,Path('fedora44')/pth_fil.name)
    for pth_fil in sorted((sys_rad/'deploy/contemplation').iterdir()):
        if pth_fil.is_file() and pth_fil.suffix != '.pyc':
            sys_fil.write(pth_fil,Path('contemplation')/pth_fil.name)
    dat_nom=set(sys_fil.namelist())
    assert 'html/astroapp-config.json' not in dat_nom
    assert 'html/contact/index.html' not in dat_nom and 'html/app.js' not in dat_nom
    assert all(not txt_val.startswith('html/bior/') for txt_val in dat_nom)
    assert 'private/send/config.php' not in dat_nom
txt_val=hashlib.sha256(pth_dst.read_bytes()).hexdigest()
pth_dst.with_suffix('.zip.sha256').write_text(txt_val+'  '+pth_dst.name+'\n')
print(str(pth_dst))
print('SHA256 '+txt_val)
