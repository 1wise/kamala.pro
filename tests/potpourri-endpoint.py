#!/usr/bin/env python3
# Timestamp: 2026-10-30
# Version: 2.0.0
# Author and Credits: https://www.alawise.es/1-s
"""Exercise the real PHP upload handler with a local, non-sending mail double."""
import base64
import http.client
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path

sys_rad=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as sys_tmp:
    pth_src=Path(sys_tmp)
    pth_dst=pth_src/'site/html/potpourri';pth_dst.mkdir(parents=True)
    pth_prv=pth_src/'site/private/send';pth_prv.mkdir(parents=True)
    pth_ses=pth_src/'sessions';pth_ses.mkdir()
    shutil.copy2(sys_rad/'deploy/potpourri/public/potpourri/send.php',pth_dst/'send.php')
    (pth_dst/'topics.json').write_text(json.dumps({'cards':{'title':'Cards'}}))
    (pth_prv/'autoload.php').write_text('<?php')
    (pth_prv/'send.php').write_text("""<?php
// Timestamp: 2026-10-30 | Version: 2.0.0 | Author and Credits: https://www.alawise.es/1-s
function env_cfg(){return ['contact_to'=>'fixture@example.invalid','autoload'=>__DIR__.'/autoload.php'];}
function env_cor($dat_env){
  $dat_adj=[];
  foreach($dat_env['attachments'] as $pth_fil) $dat_adj[]=['path'=>$pth_fil,'mime'=>(new finfo(FILEINFO_MIME_TYPE))->file($pth_fil),'bytes'=>filesize($pth_fil)];
  file_put_contents(__DIR__.'/accepted.json',json_encode(['channel'=>$dat_env['channel'],'to'=>$dat_env['to'],'files'=>$dat_adj]));
}
""")
    with socket.socket() as sys_fil:
        sys_fil.bind(('127.0.0.1',0));sys_prt=sys_fil.getsockname()[1]
    sys_prc=subprocess.Popen(['php','-d','session.save_path='+str(pth_ses),'-d','upload_max_filesize=5M','-d','post_max_size=16M','-S','127.0.0.1:'+str(sys_prt),'-t',str(pth_src/'site/html')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for sys_idx in range(100):
            try:
                sys_con=http.client.HTTPConnection('127.0.0.1',sys_prt,timeout=2);sys_con.request('GET','/potpourri/send.php');rsp_env=sys_con.getresponse();break
            except OSError:time.sleep(.05)
        else:raise AssertionError('Local PHP fixture could not start')
        assert rsp_env.status==200
        cfg_apl=json.loads(rsp_env.read());assert cfg_apl['ready'] is True
        tok_ctc=cfg_apl['csrf'];tok_ses=rsp_env.getheader('Set-Cookie').split(';')[0];sys_con.close()
        time.sleep(2.1)
        dat_img=subprocess.check_output(['php','-r','$obj_img=imagecreatetruecolor(2,2);ob_start();imagepng($obj_img);echo ob_get_clean();'])
        def env_prb(dat_frm,dat_img):
            txt_bnd='kamala-fixture-boundary'
            dat_env=b''
            for clv_esc,txt_val in dat_frm.items():
                dat_env+=('--'+txt_bnd+'\r\nContent-Disposition: form-data; name="'+clv_esc+'"\r\n\r\n'+txt_val+'\r\n').encode()
            dat_env+=('--'+txt_bnd+'\r\nContent-Disposition: form-data; name="photos[]"; filename="untrusted-name.php"\r\nContent-Type: image/png\r\n\r\n').encode()+dat_img+b'\r\n'+('--'+txt_bnd+'--\r\n').encode()
            sys_con=http.client.HTTPConnection('127.0.0.1',sys_prt,timeout=10)
            sys_con.request('POST','/potpourri/send.php',dat_env,{'Cookie':tok_ses,'Content-Type':'multipart/form-data; boundary='+txt_bnd})
            rsp_env=sys_con.getresponse();dat_dst=(rsp_env.status,json.loads(rsp_env.read()));sys_con.close();return dat_dst
        dat_frm={'csrf':tok_ctc,'name':'Fixture','email':'test@example.invalid','message':'Local test only','art':'cards','consent':'yes','website':''}
        assert env_prb({**dat_frm,'csrf':'invalid'},dat_img)[0]==403
        assert env_prb({**dat_frm,'art':'unknown'},dat_img)[0]==400
        assert env_prb(dat_frm,b'<?php echo "not an image";')[0]==400
        dat_res=env_prb(dat_frm,dat_img);assert dat_res[0]==200 and dat_res[1]['ok'],dat_res
        dat_env=json.loads((pth_prv/'accepted.json').read_text())
        assert dat_env['channel']=='potpourri' and dat_env['to']==['fixture@example.invalid']
        assert all(dat_itm['mime']=='image/jpeg' and not Path(dat_itm['path']).exists() for dat_itm in dat_env['files'])
        assert env_prb(dat_frm,dat_img)[0]==403
    finally:
        sys_prc.terminate();sys_prc.wait(timeout=5)
print('Potpourri PHP: CSRF, topic allowlist, spoofed MIME rejection, image re-encoding, mail envelope, temporary-file cleanup and consumed token passed; no email sent.')
