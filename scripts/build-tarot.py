#!/usr/bin/env python3
# Timestamp: 2026-11-01
# Version: 2.1.0
# Author & Credits: https://www.alawise.es/1-s
"""Build exact Marseille pip cards with curved swords and woven batons."""

import importlib.util
import json
from pathlib import Path

sys_rad = Path(__file__).resolve().parents[1]
sys_cfg = importlib.util.spec_from_file_location('kamala_pips', sys_rad / 'scripts/build-playing-cards.py')
sys_mod = importlib.util.module_from_spec(sys_cfg)
sys_cfg.loader.exec_module(sys_mod)
dat_tar = json.loads((sys_rad / 'src/tarot.json').read_text())['cards']
assert len(dat_tar) == len({dat_itm['id'] for dat_itm in dat_tar}) == 78
cnt_tot = 0
for dat_itm in dat_tar:
    if dat_itm['kind'] != 'pip':
        continue
    pth_fil = sys_rad / 'src' / dat_itm['art'].lstrip('/')
    pth_fil.parent.mkdir(parents=True, exist_ok=True)
    pth_fil.write_text(sys_mod.crt_tar(dat_itm))
    cnt_tot += 1
print('Built ' + str(cnt_tot) + ' engraved Marseille pip cards with exact suit counts.')
