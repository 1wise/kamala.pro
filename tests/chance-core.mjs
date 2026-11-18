// Timestamp: 2026-10-29
// Version: 1.10.0
// Author and Credits: https://www.alawise.es/1-s
import assert from 'node:assert/strict';
import { crt_azr, rnd_ent } from '../dist/entropy-core.mjs';
const sys_cfg = globalThis.crypto;
const dat_azr = { seed: new Uint32Array(16), cursor: 0 };
const dat_env = [0xffffffff, 5, 0, 0xffffffff];
Object.defineProperty(globalThis, 'crypto', { configurable: true, value: {
  getRandomValues(dat_itm) { dat_itm.fill(dat_env.shift() ?? 0); return dat_itm; }
}});
assert.equal(rnd_ent(dat_azr, 6), 5, 'Reject the top four words for six outcomes');
assert.equal(dat_azr.cursor, 2);
assert.equal(rnd_ent(dat_azr, 1), 0);
assert.equal(rnd_ent(dat_azr, 0x100000000), 0xffffffff);
for (const cnt_tot of [0, -1, 1.1, 0x100000001]) assert.throws(() => rnd_ent(dat_azr, cnt_tot), RangeError);
Object.defineProperty(globalThis, 'crypto', { configurable: true, value: sys_cfg });
for (const cnt_tot of [2, 6, 24, 52, 256]) {
  for (let sys_idx = 0; sys_idx < 1000; sys_idx++) {
    const rnd_bit = rnd_ent(dat_azr, cnt_tot);
    assert.ok(rnd_bit >= 0 && rnd_bit < cnt_tot);
  }
}
const sys_res = globalThis.fetch;
globalThis.fetch = async () => { throw new Error('Offline'); };
assert.match((await crt_azr()).label, /sampler unavailable/);
assert.equal((await crt_azr('browser')).sample, null);
globalThis.fetch = async () => ({ok:true,json:async () => ({hex:'ab'.repeat(64),mode:'stream+system',source:'cam4',sample_bytes:2048})});
assert.match((await crt_azr('cam4')).label, /CAM4/);
globalThis.fetch = async () => ({ok:true,json:async () => ({hex:'00',mode:'stream+system',source:'cam4'})});
assert.match((await crt_azr()).label, /sampler unavailable/);
globalThis.fetch = sys_res;
console.log('Chance core: rejection boundaries, ranges, mixing and fallbacks passed.');
