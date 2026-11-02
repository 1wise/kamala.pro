#!/usr/bin/env python3
# Timestamp: 2026-10-30
# Version: 2.0.2
# Author & Credits: https://www.alawise.es/1-s
"""Ensure an installed mail form survives the shared identity migration."""

import re
import json
import runpy
import subprocess
import sys
from pathlib import Path

sys_rad = Path(__file__).resolve().parents[1]
dat_met = json.loads((sys_rad / 'src/site.json').read_text())
cfg_apl = runpy.run_path(str(sys_rad / 'deploy/site-update/update_contact_page.py'))
txt_ctc = '<main id="main"><form method="post" action="/contact/send.php"><input name="token" value="fixture"><textarea name="message">A &amp; B</textarea></form><script>/* Custom form logic */</script></main>'
txt_pag = '''<!doctype html><html><head><meta charset="utf-8"><title>Old title</title><meta name='description' content='Old'><meta property='og:title' content='Old'><meta name='twitter:card' content='summary'><link href='https://old.invalid/' rel='canonical'><meta name="csrf-token" content="fixture"><link rel="stylesheet" href="/style.css"></head><body><header class="site-menu"><a href="https://go.1-s.es/">Status</a></header>''' + txt_ctc + '<footer>Old footer</footer><script src="/app.js" defer></script></body></html>'
for txt_val in (txt_pag, txt_pag.replace('><', '>\r\n<'), subprocess.check_output(['git', 'show', '5f18dd7:deploy/send/public/contact/index.html'], cwd=sys_rad, text=True)):
    txt_ext = cfg_apl['act_ctc'](txt_val)
    assert re.search(r'<main\b[^>]*>.*?</main>', txt_ext, re.S).group() == re.search(r'<main\b[^>]*>.*?</main>', txt_val, re.S).group()
    assert txt_ext == cfg_apl['act_ctc'](txt_ext), 'Migration must be idempotent'
    assert txt_ext.count('rel="canonical"') == txt_ext.count('property="og:title"') == 1
    assert 'content="' + dat_met['release'] + '"' in txt_ext
    assert 'src="/app.js?v=' + dat_met['release'] + '"' in txt_ext
    assert 'astroapp-head.js' not in txt_ext
    assert 'href="/apps/"' in txt_ext
    assert 'Status' not in txt_ext
    if 'csrf-token' in txt_val:
        assert '<meta name="csrf-token" content="fixture">' in txt_ext
        assert '<script>/* Custom form logic */</script>' in txt_ext
try:
    cfg_apl['act_ctc'](txt_pag.replace('<footer>Old footer</footer>', ''))
except ValueError:
    pass
else:
    raise AssertionError('A custom unrecognized shell must not be overwritten')
if len(sys.argv) == 2:
    txt_pag = Path(sys.argv[1]).read_bytes().decode('utf-8')
    txt_ext = cfg_apl['act_ctc'](txt_pag)
    assert re.search(r'<main\b[^>]*>.*?</main>', txt_ext, re.S).group() == re.search(r'<main\b[^>]*>.*?</main>', txt_pag, re.S).group()
    assert txt_ext == cfg_apl['act_ctc'](txt_ext)
print('Contact migration: legacy and current forms, CRLF, custom head data, inline scripts and idempotence passed.')
