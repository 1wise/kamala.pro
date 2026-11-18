#!/usr/bin/env python3
# Timestamp: 2026-11-18
# Version: 2.5.2
# Author and Credits: https://www.alawise.es/1-s
"""Package a cumulative Excalibur overlay without active host credentials."""
import hashlib
import io
import json
import tarfile
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
        # Solid compression shares the repeated locale chrome across all pages.
        if pth_rel.parts[0] in ('es','calo','i18n'):continue
        # Historical share cards remain on the host; the overlay ships current cards.
        if pth_rel.parts[:2] == ('assets','social') and '/'+str(pth_rel) not in {dat_met['share_image'], *dat_met.get('share_images',{}).values()}:continue
        if pth_rel.name.startswith('keys-lab-') and pth_rel.name != 'keys-lab-' + dat_met['release'] + '.html':continue
        # Hosted download bundles are generated after this overlay to avoid recursion.
        if pth_rel.parts[0]=='downloads' or any(clv_esc.startswith('qa-') for clv_esc in pth_rel.parts) or str(pth_rel) in ('app.js','contact/index.html','contact/send.php','astroapp-config.json','assets/coin-portrait.png') or pth_rel.suffix=='.php':continue
        sys_fil.write(pth_fil,Path('html')/pth_rel)
    sys_buf=io.BytesIO()
    with tarfile.open(fileobj=sys_buf,mode='w:gz',compresslevel=9) as sys_tar:
        dat_loc=[]
        for clv_loc in ('es','calo','i18n'):
            for pth_fil in sorted((sys_rad/'dist'/clv_loc).rglob('*')):
                if not pth_fil.is_file():continue
                pth_rel=pth_fil.relative_to(sys_rad/'dist')
                if 'downloads' in pth_rel.parts:continue
                dat_loc.append((pth_rel,pth_fil))
        # Adjacent equivalents share text within gzip's compression window.
        for pth_rel,pth_fil in sorted(dat_loc,key=lambda x:(x[0].parts[1:],x[0].parts[0])):
            sys_tar.add(pth_fil,arcname=str(pth_rel),recursive=False)
    sys_fil.writestr('locales/site-locales.tar.gz',sys_buf.getvalue())
    # Host downloads on the Site, avoiding recursive archives and stale hashes.
    url_dwn='https://kamala-observatory.workspace-441958.chatgpt.site'
    for clv_loc in ('','es/','calo/'):
        url_pag=url_dwn+'/'+clv_loc+'downloads/'
        txt_pag='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url='+url_pag+'"><title>Kamala downloads</title></head><body><a href="'+url_pag+'">Open project downloads</a></body></html>'
        sys_fil.writestr('html/'+clv_loc+'downloads/index.html',txt_pag)
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
    for pth_fil in sorted((sys_rad/'deploy/recovered').rglob('*')):
        if pth_fil.is_file():sys_fil.write(pth_fil,Path('recovered')/pth_fil.relative_to(sys_rad/'deploy/recovered'))
    for pth_fil in sorted((sys_rad/'deploy/pendulum-wind-3.6.0').rglob('*')):
        if pth_fil.is_file() and pth_fil.suffix != '.pyc':sys_fil.write(pth_fil,Path('pendulum-wind-3.6.0')/pth_fil.relative_to(sys_rad/'deploy/pendulum-wind-3.6.0'))
    dat_nom=set(sys_fil.namelist())
    assert 'html/astroapp-config.json' not in dat_nom
    assert 'html/contact/index.html' not in dat_nom and 'html/app.js' not in dat_nom
    assert all(not txt_val.startswith('html/bior/') for txt_val in dat_nom)
    assert 'private/send/config.php' not in dat_nom
txt_val=hashlib.sha256(pth_dst.read_bytes()).hexdigest()
pth_dst.with_suffix('.zip.sha256').write_text(txt_val+'  '+pth_dst.name+'\n')
print(str(pth_dst))
print('SHA256 '+txt_val)
