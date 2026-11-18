#!/usr/bin/env python3
# Timestamp: 2026-11-18
# Version: 2.5.0
# Author and Credits: https://www.alawise.es/1-s
"""Install a reviewable overlay, preserving apps, active configuration and mail."""

import argparse
import datetime
import importlib.util
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

def crt_mod(pth_fil):
    sys_cfg=importlib.util.spec_from_file_location(pth_fil.stem,pth_fil)
    dat_itm=importlib.util.module_from_spec(sys_cfg)
    sys_cfg.loader.exec_module(dat_itm)
    return dat_itm

def act_inst(pth_src,pth_dst,pth_bak,est_prv=True):
    pth_src=pth_src.resolve()
    pth_dst=pth_dst.resolve()
    if not (pth_src/'html/index.html').is_file() or not pth_dst.is_dir() or pth_src==pth_dst:
        raise ValueError('Use an extracted release and an existing site HTML directory.')
    if est_prv and not (pth_src/'private/send/send.php').is_file():
        raise ValueError('This package updates public files only. Run with --public-only; no files were changed.')
    for pth_env in (pth_dst/'contact/index.html', pth_dst/'kamala/index.html'):
        if pth_env.is_symlink() or not pth_env.parent.resolve().is_relative_to(pth_dst):
            raise ValueError('Contact paths must remain regular files inside the site root.')
    # Prefer an already migrated form; never replace it with the static mirror.
    pth_ctc=pth_dst/'kamala/index.html'
    if not pth_ctc.is_file() or '<form' not in pth_ctc.read_text():
        pth_ctc=pth_dst/'contact/index.html'
    txt_ctc=None
    if pth_ctc.is_file():
        if pth_ctc.is_symlink(): raise ValueError('The contact page must be a regular file.')
        txt_ctc=crt_mod(pth_src/'tools/update_contact_page.py').act_ctc(pth_ctc.read_text())
    pth_bak=pth_bak/('v2-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    pth_bak.mkdir(mode=0o700,parents=True)
    def cpy_fil(pth_fil,pth_dst,pth_rel):
        if pth_fil.is_symlink() or pth_dst.is_symlink(): raise ValueError('Symbolic links are not install targets: '+str(pth_rel))
        if pth_dst.exists():
            pth_arc=pth_bak/pth_rel;pth_arc.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(pth_dst,pth_arc)
        pth_dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(pth_fil,pth_dst)
    cnt_tot=0
    for pth_fil in sorted((pth_src/'html').rglob('*')):
        if not pth_fil.is_file(): continue
        pth_rel=pth_fil.relative_to(pth_src/'html')
        if pth_rel.parts[0] in ('bior',) or str(pth_rel) in ('astroapp-config.json','app.js','contact/index.html','contact/send.php'): continue
        if str(pth_rel) == 'kamala/index.html' and txt_ctc is not None: continue
        pth_dst_fil=pth_dst/pth_rel
        if not pth_dst_fil.parent.resolve().is_relative_to(pth_dst): raise ValueError('A target escapes the site root.')
        cpy_fil(pth_fil,pth_dst_fil,Path('html')/pth_rel);cnt_tot+=1
    pth_loc=pth_src/'locales/site-locales.tar.gz'
    if pth_loc.is_file():
        with tarfile.open(pth_loc,'r:gz') as sys_tar:
            dat_loc=sys_tar.getmembers()
            if sum(x.size for x in dat_loc)>64*1024*1024:
                raise ValueError('Locale bundle exceeds the expected size.')
            for dat_fil in dat_loc:
                pth_rel=Path(dat_fil.name)
                if not dat_fil.isfile() or pth_rel.is_absolute() or '..' in pth_rel.parts or pth_rel.parts[0] not in ('es','calo','i18n'):
                    raise ValueError('Unexpected file in the locale bundle.')
            with tempfile.TemporaryDirectory(prefix='kamala-locales-') as txt_tmp:
                sys_tar.extractall(txt_tmp,filter='data')
                for pth_fil in sorted(Path(txt_tmp).rglob('*')):
                    if not pth_fil.is_file():continue
                    pth_rel=pth_fil.relative_to(txt_tmp);pth_dst_fil=pth_dst/pth_rel
                    if not pth_dst_fil.parent.resolve().is_relative_to(pth_dst):
                        raise ValueError('A locale target escapes the site root.')
                    cpy_fil(pth_fil,pth_dst_fil,Path('html')/pth_rel);cnt_tot+=1
    if txt_ctc is not None:
        for pth_env in (pth_dst/'contact/index.html', pth_dst/'kamala/index.html'):
            if pth_env.is_symlink(): raise ValueError('The contact page must be a regular file.')
            if pth_env.exists():
                pth_arc=pth_bak/'html'/pth_env.relative_to(pth_dst)
                pth_arc.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(pth_env,pth_arc)
            pth_env.parent.mkdir(parents=True,exist_ok=True)
            pth_env.write_text(txt_ctc)
    pth_prv=pth_dst.parent/'private/send'
    if est_prv:
        pth_prv.mkdir(parents=True,exist_ok=True)
        cpy_fil(pth_src/'private/send/send.php',pth_prv/'send.php',Path('private/send/send.php'))
    cnt_ast=crt_mod(pth_src/'tools/configure_head.py').cfg_ast(pth_dst,pth_bak/'html')
    print('Installed public files: '+str(cnt_tot))
    print('Backup: '+str(pth_bak))
    print('AstroApp head tags: '+str(cnt_ast))
    print('Existing mail configuration present: '+str((pth_prv/'config.php').is_file()))
    print('No messages were sent. Review PHP upload limits before accepting photos.')

if __name__=='__main__':
    sys_cfg=argparse.ArgumentParser()
    sys_cfg.add_argument('--root',type=Path,default=Path('/var/www/kamala.pro/html'))
    sys_cfg.add_argument('--backup-root',type=Path,default=Path('/var/backups/kamala'))
    sys_cfg.add_argument('--public-only',action='store_true',help='Update public pages and assets without changing private mail modules.')
    cfg_apl=sys_cfg.parse_args()
    act_inst(Path(__file__).resolve().parents[1],cfg_apl.root,cfg_apl.backup_root,est_prv=not cfg_apl.public_only)
