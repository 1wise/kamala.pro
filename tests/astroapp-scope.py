#!/usr/bin/env python3
# Timestamp: 2026-10-30
# Version: 2.0.2
# Author and Credits: https://www.alawise.es/1-s
"""Reproduce global SDK tags from 2.0.1 and check the installed-site repair."""

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

sys_rad = Path(__file__).resolve().parents[1]
sys_cfg = importlib.util.spec_from_file_location('repair', sys_rad / 'deploy/astroapp/repair_astroapp_loading.py')
dat_itm = importlib.util.module_from_spec(sys_cfg)
sys_cfg.loader.exec_module(dat_itm)
with tempfile.TemporaryDirectory() as sys_tmp:
    pth_tmp = Path(sys_tmp)
    pth_src = pth_tmp / 'repair'
    pth_dst = pth_tmp / 'site/html'
    pth_src.mkdir()
    pth_dst.mkdir(parents=True)
    shutil.copy2(sys_rad / 'deploy/astroapp/configure_head.py', pth_src / 'configure_head.py')
    shutil.copy2(sys_rad / 'src/astroapp-head.js', pth_src / 'astroapp-head.js')
    shutil.copy2(sys_rad / 'src/astroapp.mjs', pth_src / 'astroapp.js')
    txt_ast = '<!-- ASTROAPP SDK START --><script data-astroapp-sdk src="https://astroapp.com/astro/astroapi?key=fixture"></script><!-- ASTROAPP SDK END --><script src="/astroapp-head.js?v=2.0.1"></script>'
    txt_pag = '<html><head><title>Keep title</title>' + txt_ast + '<script src="/app.js" defer></script></head><body><main>Keep content</main><script>const message="keep";</script></body></html>'
    for pth_fil in ('index.html', 'contact/index.html', 'glossary/index.html', 'stream/cam1/index.html', 'apps/entropy/index.html', 'potpourri/index.html', 'astrology/index.html'):
        (pth_dst / pth_fil).parent.mkdir(parents=True, exist_ok=True)
        (pth_dst / pth_fil).write_text(txt_pag if pth_fil != 'astrology/index.html' else txt_pag.replace('Keep content', '<section data-astroapp><div id="astroappDiv"></div></section>'))
    (pth_dst / 'manual.html').write_text(txt_pag.replace(txt_ast, "<script src='http://astroapp.com/astro/astroapi?key=fixture'></script><script src=/astroapp-head.js></script>"))
    (pth_dst / 'astroapp-config.json').write_text(json.dumps({'api_key': 'fixture123+abc/xyz'}))
    (pth_dst / 'astroapp-head.js').write_text('old loader')
    (pth_dst / 'astroapp.js').write_text('old controller')
    (pth_dst / 'bior').mkdir()
    (pth_dst / 'bior/keep.php').write_text('original app')
    (pth_dst.parent / 'private/send').mkdir(parents=True)
    (pth_dst.parent / 'private/send/config.php').write_text('original mail configuration')
    dat_itm.act_inst(pth_src, pth_dst, pth_tmp / 'backups')
    for pth_fil in pth_dst.rglob('*.html'):
        txt_ext = pth_fil.read_text()
        if pth_fil.relative_to(pth_dst).as_posix() == 'astrology/index.html':
            assert txt_ext.count('data-astroapp-sdk') == 1
            assert txt_ext.count('src="/astroapp-head.js') == 1
            assert 'key=fixture123%2Babc%2Fxyz&amp;v=2.0.2' in txt_ext.split('</head>')[0]
            assert 'referrerpolicy="origin"' in txt_ext
        else:
            assert 'astroapp.com/astro/astroapi' not in txt_ext, pth_fil
            assert 'astroapp-head.js' not in txt_ext, pth_fil
        assert '<title>Keep title</title>' in txt_ext
        assert '<script src="/app.js" defer></script>' in txt_ext
        assert '<script>const message="keep";</script>' in txt_ext
    assert json.loads((pth_dst / 'astroapp-config.json').read_text())['api_key'] == 'fixture123+abc/xyz'
    assert (pth_dst / 'bior/keep.php').read_text() == 'original app'
    assert (pth_dst.parent / 'private/send/config.php').read_text() == 'original mail configuration'
    pth_bak = next((pth_tmp / 'backups').iterdir())
    assert (pth_bak / 'html/index.html').read_text() == txt_pag
    assert (pth_bak / 'html/astroapp-head.js').read_text() == 'old loader'
    dat_env = {pth_fil: pth_fil.read_bytes() for pth_fil in pth_dst.rglob('*.html')}
    dat_itm.act_inst(pth_src, pth_dst, pth_tmp / 'backups')
    assert all(pth_fil.read_bytes() == txt_val for pth_fil, txt_val in dat_env.items())
print('AstroApp repair: legacy/global/manual tags removed, chart head retained, origin policy, key/content/mail preserved, backups and idempotence passed.')
