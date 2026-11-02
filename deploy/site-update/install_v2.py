#!/usr/bin/env python3
# Timestamp: 2026-11-02
# Version: 2.1.1
# Author and Credits: https://www.alawise.es/1-s
"""Install a reviewable overlay, preserving apps, active configuration and mail."""

import argparse
import datetime
import importlib.util
import os
import shutil
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
        pth_dst_fil=pth_dst/pth_rel
        if not pth_dst_fil.parent.resolve().is_relative_to(pth_dst): raise ValueError('A target escapes the site root.')
        cpy_fil(pth_fil,pth_dst_fil,Path('html')/pth_rel);cnt_tot+=1
    if txt_ctc is not None:
        pth_arc=pth_bak/'html/contact/index.html';pth_arc.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(pth_ctc,pth_arc)
        pth_ctc.write_text(txt_ctc)
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
