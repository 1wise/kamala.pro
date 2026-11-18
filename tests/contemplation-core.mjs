// Timestamp: 2026-11-01
// Version: 2.1.0
// Author & Credits: https://www.alawise.es/1-s
// Freshness, reconnects and independent counters determine the visible signal.
import assert from 'node:assert/strict';
import {val_tel,act_tel,crt_demo} from '../src/contemplation-core.mjs';
const sys_ts=Date.parse('2026-11-01T12:00:10Z');
const dat_tel={...crt_demo(10,sys_ts),session_id:'test-session',status:'live',firewall:{available:true,total:100,delta:1}};
assert.equal(val_tel(dat_tel,sys_ts).interface,'enp6s0');
assert.equal(val_tel({...dat_tel,interval_s:0,rx_bps:0,tx_bps:0,rx_pps:0,tx_pps:0},sys_ts).interval_s,0);
for (const dat_env of [
  {...dat_tel,interface:'wg1'},{...dat_tel,rx_bps:NaN},{...dat_tel,tx_pps:-1},
  {...dat_tel,sampled_at:'2026-11-01T12:00:16Z'},
  {...dat_tel,sampled_at:'2026-11-01T11:59:54Z'},
  {...dat_tel,session_id:'bad session'},
  {...dat_tel,firewall:{available:true,total:1.5,delta:0}},
  {...dat_tel,status:'unavailable'}
]) assert.throws(()=>val_tel(dat_env,sys_ts));
assert.ok(!('private_log' in val_tel({...dat_tel,private_log:'must not render'},sys_ts)));
const dat_mem={};
assert.equal(act_tel(dat_tel,dat_mem).notices,0,'Initial load must not replay 100 notices');
assert.equal(act_tel(dat_tel,dat_mem).notices,0,'Repeated samples must not replay a delta');
const dat_nxt={...dat_tel,sampled_at:'2026-11-01T12:00:12Z',firewall:{available:true,total:104,delta:1}};
assert.equal(act_tel(dat_nxt,dat_mem).notices,4,'Use total differences across missing polls');
assert.equal(act_tel(dat_tel,dat_mem).notices,0,'Out-of-order responses cannot create a pulse');
assert.equal(act_tel({...dat_nxt,session_id:'restart',firewall:{available:true,total:2,delta:2}},dat_mem).notices,0,'New collector sessions establish a baseline');
assert.equal(act_tel({...dat_nxt,session_id:'restart',sampled_at:'2026-11-01T12:00:14Z',firewall:{available:false,total:4,delta:2}},dat_mem).notices,0,'Unavailable journals cannot produce a pulse');
for (const cnt_tot of [0,1,1e9,1e12]) {
  const dat_flu=act_tel({...dat_tel,rx_bps:cnt_tot,tx_bps:cnt_tot},{});assert.ok(dat_flu.rx>=0&&dat_flu.rx<=1&&dat_flu.tx>=0&&dat_flu.tx<=1);
}
console.log('Freshness, explicit demo, collector restart, missing polls and firewall pulse deduplication passed.');
