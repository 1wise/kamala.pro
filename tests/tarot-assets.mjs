// Timestamp: 2026-11-01
// Version: 2.1.0
// Author & Credits: https://www.alawise.es/1-s
// Image identity and exact pip counts are part of the deck's public contract.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { crt_bar } from '../src/chance-core.mjs';
const dat_tar=JSON.parse(await readFile(new URL('../src/tarot.json',import.meta.url),'utf8')).cards;
const dat_bar=crt_bar('marseille');
assert.equal(dat_tar.length,78);
assert.deepEqual(dat_bar.map(dat_itm=>dat_itm.id),dat_tar.map(dat_itm=>dat_itm.id));
assert.equal(new Set(dat_tar.map(dat_itm=>dat_itm.art)).size,78);
const dat_nom=new Set();
for(const [sys_idx,dat_itm] of dat_tar.entries()) {
  assert.equal(dat_bar[sys_idx].art,dat_itm.art);
  assert.match(dat_itm.art,/^\/assets\/tarot\/[a-z0-9-]+\.(webp|svg)$/);
  const dat_val=await readFile(new URL('../src'+dat_itm.art,import.meta.url));
  const txt_val=createHash('sha256').update(dat_val).digest('hex');
  assert.ok(!dat_nom.has(txt_val),'Every card must have its own image: '+dat_itm.id);dat_nom.add(txt_val);
  if(dat_itm.kind==='pip') {
    const txt_art=dat_val.toString();
    assert.equal((txt_art.match(/data-pip="1"/g)||[]).length,dat_itm.count);
    assert.ok(txt_art.includes('data-pip-count="'+dat_itm.count+'"'));
  } else {
    assert.equal(dat_val.subarray(0,4).toString(),'RIFF');
    assert.equal(dat_val.subarray(8,12).toString(),'WEBP');
    assert.ok(dat_itm.prompt);
  }
}
assert.equal(dat_tar.filter(dat_itm=>dat_itm.kind==='illustration').length,38);
assert.equal(dat_tar.filter(dat_itm=>dat_itm.kind==='pip').length,40);
for(const clv_bar of ['spanish','american']) assert.ok(crt_bar(clv_bar).every(dat_itm=>dat_itm.art));
const txt_pag=await readFile(new URL('../dist/apps/cards/tarot/index.html',import.meta.url),'utf8');
assert.equal((txt_pag.match(/data-card-id=/g)||[]).length,78);
assert.match(txt_pag,/src="\/tarot-viewer\.js/);
console.log('78 unique mapped images, 38 illustrations, 40 exact pip counts, gallery and viewer passed.');
