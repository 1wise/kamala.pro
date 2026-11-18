// Timestamp: 2026-11-07
// Version: 3.1.1
// Author & Credits: https://www.alawise.es/1-s
// Test the published contract across collection, UI validation and CSV export.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {val_pnd,val_mst,est_pnd,exp_csv,crt_trz} from '../web/pendulum-core.mjs';

const dat_tel=val_pnd(JSON.parse(readFileSync(new URL('../state.example.json',import.meta.url),'utf8')));
assert.equal(dat_tel.sample.mode,'3d-mm');
assert.equal(dat_tel.sample.dz,-4.26);
assert.equal(dat_tel.sample.r,32.25);
assert.equal(dat_tel.sample.luminance,null);
assert.equal(est_pnd(dat_tel,dat_tel.collected_at),'live');
const dat_z={...dat_tel,sample:{...dat_tel.sample,dz:20,displacement:20,alert:false}};
assert.equal(est_pnd(dat_z,dat_tel.collected_at),'swing');
assert.equal(dat_z.events.length,0);
const dat_low={...dat_tel,sample:{...dat_tel.sample,fit_pct:10,tracking_valid:false}};
assert.equal(est_pnd(dat_low,dat_tel.collected_at),'low-fit');
assert.equal(est_pnd(dat_tel,dat_tel.collected_at+11),'stale');
assert.equal(crt_trz([dat_low.sample],'dz',x=>x,y=>y),'');
assert.equal(val_mst({...dat_tel.sample,fit_pct:200}),null);
assert.equal(val_mst({...dat_tel.sample,dz:NaN}),null);
assert.equal(val_mst({...dat_tel.sample,luminance:78}),null);
const dat_csv=exp_csv(dat_tel.history).trim().split('\r\n').map(txt_lin=>txt_lin.split(','));
assert.equal(dat_csv[0].length,dat_csv[1].length);
assert.equal(dat_csv[1][dat_csv[0].indexOf('offset_z_mm')],'-4.26');
assert.equal(dat_csv[1][dat_csv[0].indexOf('apparent_radius_px')],'32.25');
assert.equal(dat_csv[1][dat_csv[0].indexOf('brightness_0_255')],'');
const dat_ant={ts:dat_tel.sample.ts,x:608,y:300,ax:600,ay:290,dx:8,dy:10,vx:2,vy:3,
  radius:12.81,luminance:210,alert:false,events:4,highlight:true};
const dat_v1={version:1,camera:'cam4',status:'live',collected_at:dat_tel.collected_at,
  received_at:dat_tel.received_at,sample:dat_ant,history:[dat_ant],events:[]};
const dat_px=val_pnd(dat_v1);
assert.equal(dat_px.sample.mode,'2d-px');
assert.equal(dat_px.sample.dz,null);
assert.equal(dat_px.threshold,28);
assert.ok(exp_csv(dat_px.history).startsWith('source_unix_s,'));
assert.ok(exp_csv(dat_px.history).includes('offset_x_px'));
assert.throws(()=>exp_csv([dat_tel.sample,dat_px.sample]),/Cannot combine/);
assert.throws(()=>val_pnd({...JSON.parse(readFileSync(new URL('../state.example.json',import.meta.url),'utf8')),
  units:{position:'px',displacement:'px',velocity:'px/s'}}),/units/);
console.log('Frontend contract, Z-only movement, migration, staleness and CSV checks passed.');
