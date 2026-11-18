#!/usr/bin/env python3
# Timestamp: 2026-10-30
# Version: 2.0.2
# Author and Credits: https://www.alawise.es/1-s
"""Repair an installed site's SDK scope without replacing its content or key."""

import argparse
import datetime
import importlib.util
import os
import shutil
from pathlib import Path


def act_inst(pth_src, pth_dst, pth_bak):
    pth_src = pth_src.resolve()
    pth_dst = pth_dst.resolve()
    if not pth_dst.is_dir() or pth_src == pth_dst:
        raise ValueError('Use the extracted repair directory and an existing site root.')
    for pth_fil in ('configure_head.py', 'astroapp-head.js', 'astroapp.js'):
        if not (pth_src / pth_fil).is_file():
            raise ValueError('The extracted repair directory is incomplete.')
    pth_bak = pth_bak / ('astroapp-2.0.2-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    pth_bak.mkdir(parents=True, mode=0o700)
    sys_cfg = importlib.util.spec_from_file_location('configure_head', pth_src / 'configure_head.py')
    dat_itm = importlib.util.module_from_spec(sys_cfg)
    sys_cfg.loader.exec_module(dat_itm)
    cnt_ast = dat_itm.cfg_ast(pth_dst, pth_bak / 'html')
    for pth_fil in ('astroapp-head.js', 'astroapp.js'):
        pth_dst_fil = pth_dst / pth_fil
        if pth_dst_fil.is_symlink():
            raise ValueError('A script target must be a regular file.')
        if pth_dst_fil.exists():
            (pth_bak / 'html').mkdir(parents=True, exist_ok=True)
            shutil.copy2(pth_dst_fil, pth_bak / 'html' / pth_fil)
        # Overwriting the existing inode retains its owner and SELinux label.
        shutil.copyfile(pth_src / pth_fil, pth_dst_fil)
        os.chmod(pth_dst_fil, 0o644)
    print('AstroApp workspace head tags: ' + str(cnt_ast))
    print('AstroApp was removed from other HTML pages.')
    print('Existing access code, content, apps and mail settings were retained.')
    print('Backup: ' + str(pth_bak))
    print('Reload the browser without cache once. No service restart is required.')


if __name__ == '__main__':
    sys_cfg = argparse.ArgumentParser()
    sys_cfg.add_argument('--root', type=Path, default=Path('/var/www/kamala.pro/html'))
    sys_cfg.add_argument('--backup-root', type=Path, default=Path('/var/backups/kamala'))
    cfg_apl = sys_cfg.parse_args()
    act_inst(Path(__file__).resolve().parent, cfg_apl.root, cfg_apl.backup_root)
