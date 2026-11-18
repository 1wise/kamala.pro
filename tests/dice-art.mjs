// Timestamp: 2026-11-02
// Version: 2.1.1
// Author & Credits: https://www.alawise.es/1-s
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dat_dad,svg_dad} from '../src/dice-core.mjs';
for(let cnt_val=1;cnt_val<=6;cnt_val++) {
  const txt_val=svg_dad(cnt_val);
  assert.equal((txt_val.match(/data-pip="1"/g)||[]).length,cnt_val);
  assert.equal(dat_dad[cnt_val].pips.length,cnt_val);
  assert.equal(new Set(dat_dad[cnt_val].pips.map(dat_itm=>dat_itm.join(','))).size,cnt_val);
  assert.ok(!txt_val.includes('<text'),'The face must not contain printed numerals');
  assert.ok(txt_val.includes('aria-label="'+dat_dad[cnt_val].label+'"'));
  assert.ok((await readFile(new URL('../src/assets/dice/die-'+cnt_val+'.svg',import.meta.url),'utf8')).includes(txt_val));
}
for(const cnt_val of [0,7,NaN,1.5,'1'])assert.throws(()=>svg_dad(cnt_val));
for(const [cnt_a,cnt_b] of [[1,6],[2,5],[3,4]])assert.equal(cnt_a+cnt_b,7);
console.log('All six numeral-free dice faces, distinct pip positions and accessible labels passed.');
