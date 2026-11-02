// Timestamp: 2026-10-29
// Version: 1.10.0
// Author & Credits: https://www.alawise.es/1-s
import assert from 'node:assert/strict';
import { crt_azr } from '../src/entropy-core.mjs';
import sys_qr from 'qrcode';
import { PNG } from 'pngjs';
import { default as dec_qr } from 'jsqr';
import { crt_clv, exp_pub, rnd_sys, fmt_sec, url_otp } from '../src/lab/keys-core.mjs';
for (const tip_clv of ['ed25519','rsa4096']) {
  const dat_clv = await crt_clv(tip_clv,'fixture',await crt_azr('browser'));
  for (const fmt_clv of ['ssh','pem','jwk']) {
    const txt_pub = (await exp_pub(dat_clv,fmt_clv)).trimEnd();
    const dat_itm = PNG.sync.read(await sys_qr.toBuffer(txt_pub,{type:'png',errorCorrectionLevel:'M',margin:4,scale:5}));
    assert.equal(dec_qr(new Uint8ClampedArray(dat_itm.data),dat_itm.width,dat_itm.height)?.data,txt_pub);
    assert.match(await sys_qr.toString(txt_pub,{type:'svg',errorCorrectionLevel:'M',margin:4}),/^<svg/);
  }
}
for (const txt_val of [fmt_sec(rnd_sys(128),'hex'),fmt_sec(rnd_sys(32),'base64url'),url_otp(rnd_sys(20),'kamala.pro','fixture')]) {
  const dat_itm = PNG.sync.read(await sys_qr.toBuffer(txt_val,{type:'png',errorCorrectionLevel:'M',margin:4,scale:5}));
  assert.equal(dec_qr(new Uint8ClampedArray(dat_itm.data),dat_itm.width,dat_itm.height)?.data,txt_val);
}
console.log('Independent QR decoding: public OpenSSH/PEM/JWK, large RSA, secrets and TOTP payloads passed.');
