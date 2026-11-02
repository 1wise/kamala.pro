// Timestamp: 2026-10-31
// Version: 2.0.5
// Author and Credits: https://www.alawise.es/1-s
// Deterministic fixtures prove that a sample reaches the Ed25519 key material.
import assert from 'node:assert/strict';
import { crt_azr, rnd_oct } from '../src/entropy-core.mjs';
import { crt_clv } from '../src/lab/keys-core.mjs';
const sys_cfg = globalThis.crypto, sys_res = globalThis.fetch;
let cnt_tot = 0;
try {
  Object.defineProperty(globalThis,'crypto',{configurable:true,value:{
    subtle:sys_cfg.subtle,
    getRandomValues(dat_itm) { dat_itm.fill(0); return dat_itm; }
  }});
  globalThis.fetch = async (url_app,cfg_apl)=>{
    cnt_tot++;
    assert.equal(url_app,'https://www.kamala.pro/api/entropy.php?src=cam4');
    assert.equal(cfg_apl.credentials,'omit'); assert.equal(cfg_apl.referrerPolicy,'no-referrer');
    assert.equal(cfg_apl.redirect,'error'); assert.equal(cfg_apl.body,undefined);
    return {ok:true,json:async()=>({hex:'01'.repeat(64),mode:'stream+system',source:'cam4',sample_bytes:2048})};
  };
  const dat_azr = await crt_azr('cam4','https://www.kamala.pro/api/entropy.php');
  assert.match(dat_azr.label,/CAM4/);
  assert.deepEqual([...rnd_oct(dat_azr,4)],[1,1,1,1]);
  const dat_clv = await crt_clv('ed25519','fixture',dat_azr);
  globalThis.fetch = async()=>({ok:true,json:async()=>({hex:'02'.repeat(64),mode:'stream+system',source:'cam4',sample_bytes:2048})});
  const dat_itm = await crt_clv('ed25519','fixture',await crt_azr('cam4'));
  assert.notEqual(dat_clv.fp,dat_itm.fp,'Changing the camera response changes the derived Ed25519 key with fixed browser test bytes');
  assert.deepEqual([...rnd_oct(await crt_azr('browser'),4)],[0,0,0,0]);
  assert.equal(cnt_tot,1,'Browser-only makes no sampler request');
  for (const dat_env of [
    {hex:'ff'.repeat(64),mode:'stream+system',source:'cam3',sample_bytes:2048},
    {hex:'ff'.repeat(64),mode:'stream+system',source:'cam4',sample_bytes:999999},
    {hex:'zz'.repeat(64),mode:'stream+system',source:'cam4',sample_bytes:2048},
    {hex:'ff'.repeat(64),mode:'fake',source:'cam4',sample_bytes:2048}
  ]) {
    globalThis.fetch=async()=>({ok:true,json:async()=>dat_env});
    assert.equal((await crt_azr('cam4')).sample,null);
  }
  globalThis.fetch=async()=>({ok:true,json:async()=>({hex:'ab'.repeat(64),mode:'system-only',source:null,sample_bytes:0})});
  assert.match((await crt_azr()).label,/no camera/);
  globalThis.fetch=async()=>{throw new Error('offline');};
  assert.match((await crt_azr()).label,/sampler unavailable/);
  await assert.rejects(()=>crt_azr('bad'));
  await assert.rejects(()=>crt_azr('cam4','https://untrusted.invalid'));
  for (const cnt_tot of [0,-1,8193,1.5]) assert.throws(()=>rnd_oct(dat_azr,cnt_tot));
  assert.throws(()=>rnd_oct(null,32));
  await assert.rejects(()=>crt_clv('ed25519','fixture'));
  console.log('Shared entropy: camera-to-key influence, public GET-only contract, source validation, browser/offline fallback and byte bounds passed.');
} finally {
  Object.defineProperty(globalThis,'crypto',{configurable:true,value:sys_cfg});
  globalThis.fetch=sys_res;
}
