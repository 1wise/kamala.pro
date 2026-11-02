#!/usr/bin/env python3
# Timestamp: 2026-11-02
# Version: 2.1.1
# Author & Credits: https://www.alawise.es/1-s
"""Apply the shared site shell while preserving the installed contact form."""

import datetime
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path


def act_ctc(txt_pag):
    sys_rad = Path(__file__).resolve().parent / 'fragments'
    txt_met = (sys_rad / 'contact-meta.html').read_text()
    txt_nav = (sys_rad / 'contact-header.html').read_text()
    txt_ftr = (sys_rad / 'contact-footer.html').read_text()
    if len(re.findall(r'<head\b[^>]*>.*?</head>', txt_pag, re.I | re.S)) != 1:
        raise ValueError('Expected one HTML head; contact was left unchanged.')
    txt_ext = re.search(r'<head\b[^>]*>.*?</head>', txt_pag, re.I | re.S).group()
    txt_ext = re.sub(r'\s*<!-- KAMALA META START -->.*?<!-- KAMALA META END -->\s*', '', txt_ext, flags=re.S)
    txt_ext = re.sub(r'<title\b[^>]*>.*?</title>', '', txt_ext, flags=re.I | re.S)
    txt_ext = re.sub(r'''<meta\b(?=[^>]*\b(?:name|property)\s*=\s*["'](?:description|og:[^"']+|twitter:[^"']+|kamala:release)["'])[^>]*>''', '', txt_ext, flags=re.I)
    txt_ext = re.sub(r'''<link\b(?=[^>]*\brel\s*=\s*["']canonical["'])[^>]*>''', '', txt_ext, flags=re.I)
    txt_ext = re.sub(r'<link\b[^>]*href="/v2\.css[^\"]*"[^>]*>', '', txt_ext)
    txt_ext = re.sub(r'<!-- ASTROAPP SDK START -->.*?<!-- ASTROAPP SDK END -->', '', txt_ext, flags=re.S)
    txt_ext = re.sub(r'<script\b[^>]*src="/astroapp-head\.js[^\"]*"[^>]*></script>', '', txt_ext)
    txt_ext = re.sub(r'\s*</head>', '\n' + txt_met + '\n</head>', txt_ext, flags=re.I)
    if '/v2.css' not in txt_ext:
        txt_ext=txt_ext.replace('</head>','<link rel="stylesheet" href="/v2.css?v=2.1.1"></head>')
    txt_pag = re.sub(r'<head\b[^>]*>.*?</head>', lambda dat_itm: txt_ext, txt_pag, count=1, flags=re.I | re.S)
    # Update only the site header; custom form markup and inline scripts stay intact.
    txt_pag, cnt_tot = re.subn(r'''<header\b(?=[^>]*\bclass\s*=\s*["'][^"']*\bsite-menu\b[^"']*["'])[^>]*>.*?</header>''', lambda dat_itm: txt_nav, txt_pag, flags=re.I | re.S)
    if cnt_tot != 1:
        raise ValueError('Expected one site header; contact was left unchanged.')
    txt_pag, cnt_tot = re.subn(r'<footer\b[^>]*>.*?</footer>', lambda dat_itm: txt_ftr, txt_pag, flags=re.I | re.S)
    if cnt_tot != 1:
        raise ValueError('Expected one site footer; contact was left unchanged.')
    for pth_lnk in ('style.css', 'app.js'):
        txt_pag = re.sub(r'''(["'])/''' + re.escape(pth_lnk) + r'''(?:\?[^"']*)?\1''', lambda dat_itm: dat_itm[1] + '/' + pth_lnk + '?v=2.1.1' + dat_itm[1], txt_pag)
    txt_pag = re.sub(r'<!-- Timestamp: [^>]+Author (?:and|&) Credits: https://www.alawise.es/1-s -->', '<!-- Timestamp: 2026-11-02 | Version: 2.1.1 | Author & Credits: https://www.alawise.es/1-s -->', txt_pag, count=1)
    return txt_pag


if __name__ == '__main__':
    if len(sys.argv) > 2:
        raise SystemExit('Usage: update_contact_page.py [contact-index-path]')
    pth_fil = Path(sys.argv[1]) if len(sys.argv) == 2 else Path('/var/www/kamala.pro/html/contact/index.html')
    if pth_fil.is_symlink() or not pth_fil.is_file() or pth_fil.suffix != '.html':
        raise SystemExit('Expected an existing regular contact HTML file.')
    txt_pag = pth_fil.read_bytes().decode('utf-8')
    try:
        txt_ext = act_ctc(txt_pag)
        txt_ctc = re.search(r'<main\b[^>]*>.*?</main>', txt_pag, re.I | re.S)
        if not txt_ctc or re.search(r'<main\b[^>]*>.*?</main>', txt_ext, re.I | re.S).group() != txt_ctc.group():
            raise ValueError('Contact content differs; no change was written.')
    except ValueError as err_env:
        raise SystemExit(str(err_env))
    if txt_ext == txt_pag:
        print('Contact identity, metadata and navigation are already current.')
        raise SystemExit(0)
    pth_dst = Path('/var/backups/kamala')
    pth_dst.mkdir(mode=0o700, parents=True, exist_ok=True)
    pth_src = pth_dst / ('contact-index.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.html')
    with pth_src.open('xb') as sys_fil:
        sys_fil.write(txt_pag.encode('utf-8'))
    pth_src.chmod(0o600)
    # Prepare the complete replacement next to its target, then rename atomically.
    with tempfile.NamedTemporaryFile(dir=pth_fil.parent, prefix='.kamala-contact-', delete=False) as sys_fil:
        sys_tmp = Path(sys_fil.name)
        sys_fil.write(txt_ext.encode('utf-8'))
        sys_fil.flush()
        os.fsync(sys_fil.fileno())
    try:
        shutil.copystat(pth_fil, sys_tmp)
        if os.geteuid() == 0:
            os.chown(sys_tmp, pth_fil.stat().st_uid, pth_fil.stat().st_gid)
        os.replace(sys_tmp, pth_fil)
    finally:
        sys_tmp.unlink(missing_ok=True)
    print('Contact shell updated. Form, message endpoint and mail settings preserved.')
    print('Backup: ' + str(pth_src))
