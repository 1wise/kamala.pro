// Timestamp: 2026-11-16
// Version: 3.6.0
// Author & Credits: https://www.alawise.es/1-s
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {val_pnd,val_mst,est_pnd,exp_csv,crt_trz} from '../src/recovered-2.4.0/public/pendulum-core.mjs';
const dat_bas=JSON.parse(readFileSync(new URL('../deploy/recovered/kamala-pendulum-3.1.1/state.example.json',import.meta.url)));
const sys_ts=1700000005;
const dat_vnt={tilt_deg:32.5,dissociation:0.65,turbulence:true,factor:1.44,suppression_active:true,threshold_xy_mm:69};
const dat_mst={...dat_bas.sample,ts:sys_ts,dx:0,dy:0,dz:40,displacement:40,fit_pct:78,tracking_valid:true,alert:false,wind:dat_vnt};
const dat_env={...dat_bas,version:3,status:'live',collected_at:sys_ts,received_at:sys_ts,sample:dat_mst,history:[dat_mst],events:[]};
const dat_tel=val_pnd(dat_env);
assert.equal(est_pnd(dat_tel,sys_ts),'wind');
assert.equal(dat_tel.sample.displacement,40);
assert.equal(est_pnd(dat_tel,sys_ts+11),'stale');
const dat_cal={...dat_mst,wind:{...dat_vnt,dissociation:0.45,turbulence:false,suppression_active:false,factor:1,threshold_xy_mm:15}};
const dat_no=val_pnd({...dat_env,sample:dat_cal,history:[dat_cal]});
assert.equal(est_pnd(dat_no,sys_ts),'live','Z-only motion must not invent a bell alarm');
const dat_alr={...dat_cal,alert:true};
assert.equal(est_pnd(val_pnd({...dat_env,sample:dat_alr,history:[dat_alr]}),sys_ts),'swing');
assert.equal(val_mst({...dat_mst,alert:true}),null);
for(const dat_bad of [{...dat_vnt,dissociation:NaN},{...dat_vnt,dissociation:1.1},
  {...dat_vnt,factor:2.6},{...dat_vnt,threshold_xy_mm:15},{...dat_vnt,suppression_active:false}]) {
  assert.equal(val_mst({...dat_mst,wind:dat_bad}),null);
}
const dat_old=val_mst(dat_bas.sample);assert.equal(dat_old.wind,null);
const dat_csv=exp_csv([dat_old,dat_mst]).trim().split('\r\n').map(l=>l.split(','));
for(const dat_lin of dat_csv.slice(1))assert.equal(dat_lin.length,dat_csv[0].length);
const idx_dh=dat_csv[0].indexOf('wind_dissociation_0_1');
assert.equal(dat_csv[1][idx_dh],'');assert.equal(dat_csv[2][idx_dh],'0.65');
assert.equal(dat_csv[2][dat_csv[0].indexOf('source_wind_suppression')],'1');
assert.ok(crt_trz([{...dat_mst,tracking_valid:false}],'wind.dissociation',x=>x,y=>y).startsWith('M'));
console.log('Wind suppression, rounded boundary, stale state, legacy unknowns, Z-only motion and CSV passed.');

// Validate the JSON emitted by the real Python collector, rather than a JS-only shape.
const txt_py = `import importlib.util,json
s=importlib.util.spec_from_file_location('feed','deploy/pendulum-wind-3.6.0/pendulum_feed.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=m.prs_pnd('1700000000.123456|546,292,40.23|546,292,40.23|0,0,40|0,0,1|40|78|0|4|32.5|0.65|1|1.44')
a=m.PndState();a.act_pnd(p);print(json.dumps(a.snapshot()))`;
const dat_py=val_pnd(JSON.parse(execFileSync('python3',['-c',txt_py],{encoding:'utf8'})));
assert.equal(dat_py.sample.wind.dissociation,0.65);
assert.equal(dat_py.sample.wind.threshold_xy_mm,69);
console.log('Python multipart-to-browser JSON compatibility passed.');
