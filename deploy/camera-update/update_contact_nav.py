#!/usr/bin/env python3
# Timestamp: 2026-10-29
# Version: 1.7.0
# Author and Credits: https://www.alawise.es/1-s
"""Update only contact navigation, preserving the installed form and mail integration."""

import datetime
import sys
from pathlib import Path

if len(sys.argv) > 2:
    raise SystemExit('Usage: update_contact_nav.py [contact-index-path]')
pth_fil = Path(sys.argv[1]) if len(sys.argv) == 2 else Path('/var/www/kamala.pro/html/contact/index.html')
txt_pag = pth_fil.read_text()
txt_val = '<a class="status-nav" href="https://go.1-s.es/" target="_blank" rel="noopener">Status ↗</a>'
txt_ext = txt_pag.replace(txt_val, '<a href="/stream/">Cameras</a>')
if 'href="https://go.1-s.es/' in txt_ext:
    raise SystemExit('A custom old navigation link remains. Update that link manually; the form was left unchanged.')
if 'href="/apps/"' not in txt_ext:
    txt_ext = txt_ext.replace('<a href="/stream/">Cameras</a>', '<a href="/stream/">Cameras</a><a href="/apps/">Chance apps</a>')
if txt_ext == txt_pag:
    print('Contact navigation is already current or customized. Contact page left unchanged.')
    raise SystemExit(0)

# Keep the rollback copy outside the public document root.
pth_dst = Path('/var/backups/kamala')
pth_dst.mkdir(mode=0o700, parents=True, exist_ok=True)
pth_src = pth_dst / ('contact-index.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.html')
with pth_src.open('x') as sys_fil:
    sys_fil.write(txt_pag)
pth_src.chmod(0o600)
pth_fil.write_text(txt_ext)
print('Contact navigation updated. Form and mail settings preserved.')
print('Backup: ' + str(pth_src))
