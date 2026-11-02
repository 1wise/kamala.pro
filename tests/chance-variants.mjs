// Timestamp: 2026-10-29
// Version: 1.11.0
// Author & Credits: https://www.alawise.es/1-s
import assert from 'node:assert/strict';
import { crt_bar, crt_tir, cfg_tir, pos_crz, dat_run, crt_lin, crt_hex } from '../src/chance-core.mjs';
import { crt_azr } from '../src/entropy-core.mjs';

for(const [clv_bar,cnt_tot] of [['spanish',40],['spanish',48],['american',52],['marseille',78]]) {
  const dat_bar=crt_bar(clv_bar,cnt_tot);assert.equal(dat_bar.length,cnt_tot);
  assert.equal(new Set(dat_bar.map(dat_itm=>dat_itm.id)).size,cnt_tot);
  const dat_env=crt_tir(dat_bar,cnt_tot,await crt_azr('browser'));
  assert.equal(new Set(dat_env.map(dat_itm=>dat_itm.id)).size,cnt_tot);assert.equal(dat_bar.length,0);
  assert.throws(()=>crt_tir(dat_bar,1,{}));
}
assert.ok(!crt_bar('spanish',40).some(dat_itm=>['8','9'].includes(dat_itm.rank)));
assert.equal(crt_bar('spanish',48).filter(dat_itm=>['8','9'].includes(dat_itm.rank)).length,8);
assert.equal(crt_bar('marseille').filter(dat_itm=>dat_itm.suit==='Major arcana').length,22);
assert.equal(crt_bar('marseille').find(dat_itm=>dat_itm.label==='La Justice').rank,'VIII');
assert.equal(crt_bar('marseille').find(dat_itm=>dat_itm.label==='La Force').rank,'XI');
assert.deepEqual(cfg_tir('matrix',4,13,52),{rows:4,cols:13,count:52});
assert.deepEqual(cfg_tir('cross',1,1,40),{rows:3,cols:3,count:5});
assert.deepEqual(pos_crz.map(dat_itm=>[dat_itm.row,dat_itm.col]),[[2,2],[1,2],[3,2],[2,1],[2,3]]);
for(const dat_env of [['matrix',0,2,40],['matrix',1.5,2,40],['matrix',2,40,78],['cross',3,3,4],['bad',1,1,52]])assert.throws(()=>cfg_tir(...dat_env));
for(const cnt_tot of [16,24]) {
  const dat_bar=[...dat_run[cnt_tot]];
  assert.equal(dat_bar.length,cnt_tot);assert.equal(new Set(dat_bar.map(dat_itm=>dat_itm.glyph)).size,cnt_tot);
  assert.ok(dat_bar.every(dat_itm=>dat_itm.fi&&dat_itm.name&&dat_itm.latin));
  assert.equal(new Set(crt_tir(dat_bar,cnt_tot,await crt_azr('browser')).map(dat_itm=>dat_itm.id)).size,cnt_tot);
}
assert.deepEqual(dat_run['16'].map(dat_itm=>dat_itm.latin),['f','u','þ','ą','r','k','h','n','i','a','s','t','b','m','l','ʀ']);
// Exhaust all eight equally likely three-coin outcomes: 1, 3, 3, 1.
const sys_cfg=globalThis.crypto, dat_lim={6:0,7:0,8:0,9:0};
try {
  for(let sys_idx=0;sys_idx<8;sys_idx++) {
    const dat_env=[sys_idx&1,(sys_idx>>1)&1,(sys_idx>>2)&1];
    Object.defineProperty(globalThis,'crypto',{configurable:true,value:{getRandomValues:dat_itm=>{dat_itm[0]=dat_env.shift();return dat_itm;}}});
    const dat_lin=crt_lin({seed:new Uint32Array(16),cursor:0});dat_lim[dat_lin.value]++;
    assert.equal(dat_lin.value,dat_lin.coins.reduce((cnt_tot,rnd_bit)=>cnt_tot+2+rnd_bit,0));
  }
} finally {Object.defineProperty(globalThis,'crypto',{configurable:true,value:sys_cfg});}
assert.deepEqual(dat_lim,{6:1,7:3,8:3,9:1});
for(const [dat_lin,cnt_tot] of [
  [[7,7,7,7,7,7],1],[[8,8,8,8,8,8],2],[[7,7,7,8,8,8],11],[[8,8,8,7,7,7],12],
  [[7,8,8,8,8,8],24],[[7,8,7,8,7,8],63],[[8,7,8,7,8,7],64],[[7,7,8,8,7,7],61]
])assert.equal(crt_hex(dat_lin).number,cnt_tot);
assert.deepEqual(crt_hex([6,7,8,9,8,7]).changing,[1,4]);
assert.deepEqual(crt_hex([6,7,8,9,8,7]).related,[1,1,0,0,0,1]);
const dat_hex=Array.from({length:64},(_,sys_idx)=>crt_hex(Array.from({length:6},(_,idx_act)=>(sys_idx>>idx_act)&1 ? 7 : 8)).number);
assert.equal(new Set(dat_hex).size,64);assert.deepEqual([...dat_hex].sort((cnt_car,cnt_crz)=>cnt_car-cnt_crz),Array.from({length:64},(_,sys_idx)=>sys_idx+1));
assert.throws(()=>crt_hex([7,8]));assert.throws(()=>crt_hex([7,8,9,6,7,10]));
console.log('Decks 40/48/52/78, no replacement, exact cross positions, matrix bounds, both rune alphabets, three-coin probabilities and 64 hexagrams passed.');
