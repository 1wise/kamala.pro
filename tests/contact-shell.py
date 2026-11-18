#!/usr/bin/env python3
# Timestamp: 2026-11-18
# Version: 2.4.4
# Author & Credits: https://www.alawise.es/1-s
"""Ensure an installed mail form survives the shared identity migration."""

import re
import json
import io
import runpy
import shutil
import sys
import tempfile
import tarfile
from pathlib import Path

sys_rad = Path(__file__).resolve().parents[1]
dat_met = json.loads((sys_rad / 'src/site.json').read_text())
cfg_apl = runpy.run_path(str(sys_rad / 'deploy/site-update/update_contact_page.py'))
txt_ctc = '<main id="main"><form method="post" action="/contact/send.php"><input name="token" value="fixture"><textarea name="message">A &amp; B</textarea></form><script>/* Custom form logic */</script></main>'
txt_pag = '''<!doctype html><html><head><meta charset="utf-8"><title>Old title</title><meta name='description' content='Old'><meta property='og:title' content='Old'><meta name='twitter:card' content='summary'><link href='https://old.invalid/' rel='canonical'><meta name="csrf-token" content="fixture"><link rel="stylesheet" href="/style.css"></head><body><header class="site-menu"><a href="https://go.1-s.es/">Status</a></header>''' + txt_ctc + '<footer>Old footer</footer><script src="/app.js" defer></script></body></html>'
for txt_val in (txt_pag, txt_pag.replace('><', '>\r\n<'), (sys_rad / 'deploy/send/public/contact/index.html').read_text()):
    txt_ext = cfg_apl['act_ctc'](txt_val)
    assert re.search(r'<main\b[^>]*>.*?</main>', txt_ext, re.S).group() == re.search(r'<main\b[^>]*>.*?</main>', txt_val, re.S).group()
    assert txt_ext == cfg_apl['act_ctc'](txt_ext), 'Migration must be idempotent'
    assert txt_ext.count('rel="canonical"') == txt_ext.count('property="og:title"') == 1
    assert 'content="' + dat_met['release'] + '"' in txt_ext
    assert 'src="/app.js?v=' + dat_met['release'] + '"' in txt_ext
    assert 'astroapp-head.js' not in txt_ext
    assert 'href="/apps/"' in txt_ext
    assert 'Status' not in txt_ext
    assert 'href="https://www.kamala.pro/kamala"' in txt_ext
    assert 'href="/kamala" aria-current="page"' in txt_ext
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

# Exercise both the first migration and a later update with a customized form.
cfg_ins = runpy.run_path(str(sys_rad / 'deploy/site-update/install_v2.py'))
with tempfile.TemporaryDirectory() as txt_tmp:
    sys_tmp = Path(txt_tmp)
    pth_pkg, pth_web, pth_bak = (sys_tmp / n for n in ('package', 'site/html', 'backups'))
    (pth_pkg / 'html/kamala').mkdir(parents=True)
    (pth_pkg / 'tools').mkdir()
    (pth_web / 'contact').mkdir(parents=True)
    (pth_pkg / 'html/index.html').write_text('<!doctype html><html><head></head><body>Home</body></html>')
    (pth_pkg / 'html/kamala/index.html').write_text('Static mirror fallback')
    for txt_nom in ('install_v2.py', 'update_contact_page.py'):
        shutil.copy2(sys_rad / 'deploy/site-update' / txt_nom, pth_pkg / 'tools' / txt_nom)
    shutil.copytree(sys_rad / 'deploy/site-update/fragments', pth_pkg / 'tools/fragments')
    shutil.copy2(sys_rad / 'deploy/astroapp/configure_head.py', pth_pkg / 'tools/configure_head.py')
    (pth_pkg / 'locales').mkdir()
    with tarfile.open(pth_pkg / 'locales/site-locales.tar.gz', 'w:gz') as sys_tar:
        dat_pag='<h1>Inicio en castellano</h1>'.encode()
        dat_inf=tarfile.TarInfo('es/index.html');dat_inf.size=len(dat_pag)
        sys_tar.addfile(dat_inf,io.BytesIO(dat_pag))
    (pth_web / 'contact/index.html').write_text(txt_pag)
    (pth_web / 'contact/send.php').write_text('Existing endpoint')
    (pth_web / 'app.js').write_text('Existing form logic')
    for idx_pas in range(2):
        cfg_ins['act_inst'](pth_pkg, pth_web, pth_bak, est_prv=False)
        txt_nvo = (pth_web / 'kamala/index.html').read_text()
        assert re.search(r'<main\b[^>]*>.*?</main>', txt_nvo, re.S)[0] == txt_ctc
        assert 'href="https://www.kamala.pro/kamala"' in txt_nvo
        assert (pth_web / 'contact/index.html').read_text() == txt_nvo
        assert (pth_web / 'contact/send.php').read_text() == 'Existing endpoint'
        assert (pth_web / 'app.js').read_text() == 'Existing form logic'
        assert (pth_web / 'es/index.html').read_text() == '<h1>Inicio en castellano</h1>'
        if idx_pas == 0:
            txt_ctc = txt_ctc.replace('A &amp; B', 'A customized observation')
            (pth_web / 'kamala/index.html').write_text(txt_nvo.replace('A &amp; B', 'A customized observation'))
    assert any(pth_bak.rglob('contact/index.html'))
print('Installer: indexed contact route, customized form, endpoint, client logic and backups preserved on both updates.')
