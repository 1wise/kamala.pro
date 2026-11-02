// Timestamp: 2026-10-30
// Version: 2.0.2
// Author and Credits: https://www.alawise.es/1-s
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {runInNewContext} from 'node:vm';
const txt_pag=await readFile(new URL('../src/astroapp-head.js',import.meta.url),'utf8');
async function prb_ast(cfg_ast,est_env=true,est_ast=true) {
  const dat_hst=[];
  const sys_cfg={window:{},URL,AbortSignal,setTimeout,clearTimeout};
  sys_cfg.document={readyState:'complete',querySelector:txt_val=>txt_val==='[data-astroapp]'&&est_ast ? {} : null,createElement:()=>({dataset:{}}),head:{appendChild:dmn_itm=>{
    dat_hst.push(dmn_itm);
    if(est_env){sys_cfg.window.AstroApp=function(){};sys_cfg.window.astroRun=function(){};dmn_itm.onload();}
    else dmn_itm.onerror();
  }}};
  sys_cfg.fetch=async()=>{dat_hst.push('config');return {ok:true,text:async()=>JSON.stringify(cfg_ast)};};
  runInNewContext(txt_pag,sys_cfg);
  return {ready:await sys_cfg.window.kamalaAstroReady,dat_hst:dat_hst.filter(dat_itm=>dat_itm!=='config'),cnt_tot:dat_hst.length};
}
let dat_res=await prb_ast({api_key:'fixture/+&='});
assert.equal(dat_res.ready,true);
assert.equal(dat_res.dat_hst.length,1);
assert.equal(new URL(dat_res.dat_hst[0].src).searchParams.get('key'),'fixture/+&=');
assert.equal(dat_res.dat_hst[0].referrerPolicy,'origin');
assert.equal(dat_res.dat_hst[0].type,'text/javascript');
assert.equal(new URL(dat_res.dat_hst[0].src).searchParams.get('v'),'2.0.2');
assert.equal((await prb_ast({api_key:'fixture'},true,false)).cnt_tot,0,'Ordinary pages must not fetch config or the SDK');
assert.equal((await prb_ast({api_key:'your_API_Access_Code'})).dat_hst.length,0);
assert.equal((await prb_ast({api_key:'fixture'},false)).ready,false);
console.log('AstroApp head: workspace-only requests, encoded code, origin referrer, refreshed SDK URL, ready event and load failures passed; no provider request.');
