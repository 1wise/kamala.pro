#!/usr/bin/env python3
# Timestamp: 2026-10-30
# Version: 2.0.3
# Author and Credits: https://www.alawise.es/1-s
"""Check the Excalibur overlay without touching an installed server."""
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path
sys_rad=Path(__file__).resolve().parents[1]
sys_cfg=importlib.util.spec_from_file_location('install_v2',sys_rad/'deploy/site-update/install_v2.py')
dat_itm=importlib.util.module_from_spec(sys_cfg);sys_cfg.loader.exec_module(dat_itm)
with tempfile.TemporaryDirectory() as sys_tmp:
    pth_tmp=Path(sys_tmp);pth_src=pth_tmp/'release';pth_dst=pth_tmp/'site/html'
    pth_dst.mkdir(parents=True);(pth_src/'html').mkdir(parents=True);(pth_src/'tools').mkdir()
    for pth_fil in ['index.html','astrology/index.html','apps/entropy/index.html','potpourri/index.html']:
        (pth_src/'html'/pth_fil).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(sys_rad/'dist'/pth_fil,pth_src/'html'/pth_fil)
    for pth_fil in ['update_contact_page.py','configure_head.py']:
        shutil.copy2(sys_rad/('deploy/astroapp' if pth_fil.startswith('configure') else 'deploy/site-update')/pth_fil,pth_src/'tools'/pth_fil)
    shutil.copytree(sys_rad/'deploy/site-update/fragments',pth_src/'tools/fragments')
    (pth_src/'private/send').mkdir(parents=True);shutil.copy2(sys_rad/'deploy/send/private/send.php',pth_src/'private/send/send.php')
    (pth_dst/'bior').mkdir();(pth_dst/'bior/keep.php').write_text('original app')
    (pth_dst/'contact').mkdir();shutil.copy2(sys_rad/'deploy/send/public/contact/index.html',pth_dst/'contact/index.html')
    txt_pag=(pth_dst/'contact/index.html').read_text()
    (pth_dst/'astroapp-config.json').write_text(json.dumps({'api_key':'fixture123+abc/xyz'}))
    (pth_dst.parent/'private/send').mkdir(parents=True);(pth_dst.parent/'private/send/config.php').write_text('original private configuration')
    dat_itm.act_inst(pth_src,pth_dst,pth_tmp/'backups')
    assert (pth_dst/'bior/keep.php').read_text()=='original app'
    assert (pth_dst.parent/'private/send/config.php').read_text()=='original private configuration'
    assert json.loads((pth_dst/'astroapp-config.json').read_text())['api_key']=='fixture123+abc/xyz'
    for pth_fil in ['astrology/index.html']:
        txt_ext=(pth_dst/pth_fil).read_text();assert 'data-astroapp-sdk' in txt_ext.split('</head>')[0]
        assert 'key=fixture123%2Babc%2Fxyz' in txt_ext
    for pth_fil in ['index.html','contact/index.html','apps/entropy/index.html','potpourri/index.html']:
        assert 'astroapp-head' not in (pth_dst/pth_fil).read_text()
        assert 'data-astroapp-sdk' not in (pth_dst/pth_fil).read_text()
    assert len(list((pth_tmp/'backups').iterdir()))==1
    txt_val=(pth_dst.parent/'private/send/send.php').read_text()
    (pth_src/'private/send/send.php').unlink()
    try:
        dat_itm.act_inst(pth_src,pth_dst,pth_tmp/'backups')
    except ValueError as err_env:
        assert '--public-only' in str(err_env)
    else:
        raise AssertionError('A public-only package must require its installation flag before writing.')
    assert len(list((pth_tmp/'backups').iterdir()))==1
    dat_itm.act_inst(pth_src,pth_dst,pth_tmp/'backups',est_prv=False)
    assert (pth_dst.parent/'private/send/send.php').read_text()==txt_val
    assert (pth_dst.parent/'private/send/config.php').read_text()=='original private configuration'
print('Excalibur installer: apps, contact and private config retained; literal SDK tag only in the chart workspace; backups created.')
