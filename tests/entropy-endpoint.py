#!/usr/bin/env python3
# Timestamp: 2026-10-29
# Version: 1.7.0
# Author and Credits: https://www.alawise.es/1-s
"""Exercise endpoint validation and bounded image intake without contacting cameras."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
sys_rad = Path(__file__).resolve().parents[1]
sys_cfg = sys.argv[1] if len(sys.argv) == 2 else 'php'

# A PHP -n runtime without cURL permits deterministic transport fixtures.
txt_ext = r'''
foreach (['CURLOPT_CONNECTTIMEOUT_MS','CURLOPT_TIMEOUT_MS','CURLOPT_FOLLOWLOCATION','CURLOPT_SSL_VERIFYPEER','CURLOPT_SSL_VERIFYHOST','CURLOPT_USERAGENT','CURLOPT_WRITEFUNCTION','CURLINFO_CONTENT_TYPE','CURLINFO_HTTP_CODE'] as $sys_idx => $txt_val) define($txt_val, $sys_idx + 1);
function curl_init($url_app) { if ($url_app !== 'https://kam.2to1.me/stream/cam4') throw new Exception('Unexpected target'); return new stdClass(); }
function curl_setopt_array($sys_cnl, $cfg_apl) { $GLOBALS['cfg_apl'] = $cfg_apl; }
function curl_exec($sys_cnl) {
  $dat_par = "--boundary\r\nContent-Type: image/jpeg\r\n\r\n\xff\xd8\xff" . str_repeat('x', 200000);
  if (getenv('FIXTURE') === 'html') $dat_par = '<html>Error</html>';
  ($GLOBALS['cfg_apl'][CURLOPT_WRITEFUNCTION])($sys_cnl, $dat_par);
}
function curl_getinfo($sys_cnl, $clv_esc) { return $clv_esc === CURLINFO_HTTP_CODE ? 200 : 'multipart/x-mixed-replace; boundary=test'; }
function curl_close($sys_cnl) {}
'''
for clv_esc in ['fallback', 'image', 'html', 'invalid', 'post']:
    with tempfile.TemporaryDirectory() as pth_dst:
        txt_pag = '<?php\n' + (txt_ext if clv_esc in ['image', 'html'] else '')
        txt_pag += "\n$_SERVER['REQUEST_METHOD'] = " + ("'POST';" if clv_esc == 'post' else "'GET';")
        txt_pag += "\n$_GET['src'] = " + ("'https://attacker.invalid';" if clv_esc == 'invalid' else "'cam4';")
        txt_pag += '\nrequire ' + json.dumps(str(sys_rad / 'deploy/entropy/public/api/entropy.php')) + ';'
        pth_fil = Path(pth_dst) / 'fixture.php'
        pth_fil.write_text(txt_pag)
        sys_res = subprocess.run([sys_cfg, '-n', str(pth_fil)], capture_output=True, text=True, check=True, env={**os.environ, 'TMPDIR': pth_dst, 'FIXTURE': clv_esc})
        dat_env = json.loads(sys_res.stdout)
        if clv_esc in ['invalid', 'post']:
            assert 'error' in dat_env
        else:
            assert len(dat_env['hex']) == 128
            assert dat_env['mode'] == ('stream+system' if clv_esc == 'image' else 'system-only')
            assert dat_env['sample_bytes'] <= 131072
            assert (dat_env['sample_bytes'] > 1024) == (clv_esc == 'image')
            if clv_esc == 'fallback':
                sys_res = subprocess.run([sys_cfg, '-n', str(pth_fil)], capture_output=True, text=True, check=True, env={**os.environ, 'TMPDIR': pth_dst})
                assert 'cooling down' in json.loads(sys_res.stdout)['error']
print('Entropy endpoint: bounded image sampling, fallback, bad source, method and cooldown passed.')
