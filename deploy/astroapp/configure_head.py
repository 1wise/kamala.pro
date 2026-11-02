#!/usr/bin/env python3
# Timestamp: 2026-10-30
# Version: 2.0.2
# Author and Credits: https://www.alawise.es/1-s
"""Scope the literal SDK head tag to a chart workspace and repair older pages."""

import html
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlencode, urlsplit

def clr_ast(dat_itm):
    """Remove only the provider SDK or this project's dedicated SDK loader."""
    txt_val = re.search(r'''\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))''', dat_itm[1], re.I)
    if not txt_val:
        return dat_itm[0]
    url_app = urlsplit(html.unescape(next(txt_val for txt_val in txt_val.groups() if txt_val is not None)))
    if url_app.path.rstrip('/').split('/')[-1] == 'astroapp-head.js':
        return ''
    if url_app.hostname in ('astroapp.com', 'www.astroapp.com') and url_app.path.rstrip('/') == '/astro/astroapi':
        return ''
    return dat_itm[0]


def cfg_ast(pth_dst, pth_bak=None):
    pth_fil = pth_dst / 'astroapp-config.json'
    txt_ast = ''
    if pth_fil.is_file():
        if pth_fil.stat().st_size > 8192:
            raise ValueError('AstroApp configuration exceeds the expected size.')
        dat_ast = json.loads(pth_fil.read_text())
        txt_val = dat_ast.get('api_key')
        if not isinstance(txt_val, str) or not txt_val or len(txt_val) > 4096 or re.search(r'\s|[\x00-\x1f\x7f]', txt_val) or re.search(r'your[_ -]?api|replace[_ -]?me|access[_ -]?code', txt_val, re.I):
            raise ValueError('The configured JavaScript API access code is empty or malformed.')
        url_app = 'https://astroapp.com/astro/astroapi?' + urlencode({'key': txt_val, 'v': '2.0.2'})
        txt_ast = '<script type="text/javascript" data-astroapp-sdk src="' + html.escape(url_app, quote=True) + '" referrerpolicy="origin"></script>'
    cnt_tot = 0
    for pth_fil in pth_dst.rglob('*.html'):
        if pth_fil.is_symlink():
            continue
        txt_pag = pth_fil.read_text()
        est_ast = bool(re.search(r'<[^>]+\sdata-astroapp(?:\s|=|>)', txt_pag)) and 'id="astroappDiv"' in txt_pag
        txt_ext = re.sub(r'<!-- ASTROAPP SDK START -->.*?<!-- ASTROAPP SDK END -->', '', txt_pag, flags=re.S)
        txt_ext = re.sub(r'<script\b([^>]*)>.*?</script\s*>', clr_ast, txt_ext, flags=re.I | re.S)
        if est_ast:
            if len(re.findall(r'<head\b[^>]*>.*?</head>', txt_ext, re.I | re.S)) != 1:
                raise ValueError('Expected one workspace head: ' + str(pth_fil.relative_to(pth_dst)))
            txt_met = '<!-- ASTROAPP SDK START -->' + txt_ast + '<!-- ASTROAPP SDK END --><script src="/astroapp-head.js?v=2.0.2"></script>'
            txt_ext = re.sub(r'</head\s*>', lambda dat_itm: txt_met + '</head>', txt_ext, count=1, flags=re.I)
            cnt_tot += bool(txt_ast)
        if txt_ext == txt_pag:
            continue
        if pth_bak is not None:
            pth_arc = pth_bak / pth_fil.relative_to(pth_dst)
            pth_arc.parent.mkdir(parents=True, exist_ok=True)
            # The installer may already have saved the original file at this path.
            if not pth_arc.exists():
                shutil.copy2(pth_fil, pth_arc)
        with tempfile.NamedTemporaryFile(dir=pth_fil.parent, delete=False) as sys_fil:
            pth_src = Path(sys_fil.name)
            sys_fil.write(txt_ext.encode())
            sys_fil.flush()
            os.fsync(sys_fil.fileno())
        try:
            shutil.copystat(pth_fil, pth_src)
            os.utime(pth_src, None)
            if os.geteuid() == 0:
                os.chown(pth_src, pth_fil.stat().st_uid, pth_fil.stat().st_gid)
            os.replace(pth_src, pth_fil)
        finally:
            pth_src.unlink(missing_ok=True)
    return cnt_tot

if __name__ == '__main__':
    pth_dst=Path(sys.argv[1] if len(sys.argv)==2 else '/var/www/kamala.pro/html').resolve()
    print('AstroApp workspace head tags configured: '+str(cfg_ast(pth_dst))+'. Access code was not printed.')
