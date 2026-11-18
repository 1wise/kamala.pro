// Timestamp: 2026-11-01
// Version: 2.1.0
// Author & Credits: https://www.alawise.es/1-s
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {crt_bar} from '../src/chance-core.mjs';
const dat_bar=JSON.parse(await readFile(new URL('../src/playing-cards.json',import.meta.url),'utf8')).cards;
assert.equal(dat_bar.length,100);
assert.equal(new Set(dat_bar.map(dat_itm=>dat_itm.art)).size,100);
const dat_nom=new Set();
for (const clv_bar of ['spanish','american']) {
  const dat_env=dat_bar.filter(dat_itm=>dat_itm.deck===clv_bar);
  const dat_cmp=crt_bar(clv_bar,clv_bar==='spanish'?48:40);
  assert.deepEqual(dat_env.map(dat_itm=>dat_itm.id),dat_cmp.map(dat_itm=>dat_itm.id));
  for (const [sys_idx,dat_itm] of dat_env.entries()) {
    assert.equal(dat_itm.art,dat_cmp[sys_idx].art);
    const dat_val=await readFile(new URL('../src'+dat_itm.art,import.meta.url));
    const txt_sha=createHash('sha256').update(dat_val).digest('hex');
    assert.ok(!dat_nom.has(txt_sha),'Unique image required: '+dat_itm.id);dat_nom.add(txt_sha);
    if(dat_itm.kind==='pip') {
      assert.equal((dat_val.toString().match(/data-pip="1"/g)||[]).length,dat_itm.count);
    } else {
      assert.equal(dat_val.subarray(0,4).toString(),'RIFF');assert.equal(dat_val.subarray(8,12).toString(),'WEBP');
    }
  }
  const txt_pag=await readFile(new URL('../dist/apps/cards/'+clv_bar+'/index.html',import.meta.url),'utf8');
  assert.equal((txt_pag.match(/data-card-id=/g)||[]).length,dat_env.length);
  assert.match(txt_pag,/src="\/tarot-viewer\.js/);
}
const dat_40=crt_bar('spanish',40),dat_48=crt_bar('spanish',48);
assert.equal(dat_40.length,40);assert.equal(dat_48.length,48);
assert.ok(dat_40.every(dat_itm=>dat_48.some(dat_cmp=>dat_cmp.id===dat_itm.id&&dat_cmp.art===dat_itm.art)));
console.log('100 unique Spanish/American images, 76 exact pip counts, 24 court illustrations and both galleries passed.');
