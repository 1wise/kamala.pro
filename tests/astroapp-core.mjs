// Timestamp: 2026-10-30
// Version: 2.0.3
// Author and Credits: https://www.alawise.es/1-s
import assert from 'node:assert/strict';
import {fmt_ast, url_ast, crt_ast, run_ast, dat_opt, dat_car} from '../src/astroapp-core.mjs';

const dat_frm = {date: '2000-02-29', time: '13:05', timezone: '+01:00', latitude: '42n30', longitude: '001e31'};
const dat_ast = fmt_ast(dat_frm);
assert.deepEqual(dat_ast, {date: '2000/02/29', time: '13:05:00', timezone: '+01:00', latitude: '42N30', longitude: '1E31', chart:'western', house:'placidus', zodiac:'tropical', coordinates:'geo', style:'proportional', language:'en', varga:null, height:0, xml:false});
for (const [clv_esc, dat_env] of [
  ['date', ['1900-02-29', '2026-04-31', '0000-01-01', '2026-13-01', '2026-01-00']],
  ['time', ['24:00', '12:60', '12:00:60', '12']],
  ['timezone', ['+14:01', '-14:59', '+15:00', '+01:60', 'UTC', '1:00']],
  ['latitude', ['90N01', '91N00', '42E30', '42N60', '<script>']],
  ['longitude', ['180W01', '181E00', '1N30', '1E60', '1.5']]
]) for (const txt_val of dat_env) assert.throws(() => fmt_ast({...dat_frm, [clv_esc]: txt_val}), undefined, clv_esc + ':' + txt_val);
for (const dat_env of [{latitude: '90S00', longitude: '180W00', timezone: '-14:00'}, {date: '0001-01-01', timezone: '+05:45'}, {date: '2400-02-29', time: '23:59:59'}]) assert.doesNotThrow(() => fmt_ast({...dat_frm, ...dat_env}));

// Fixtures exercise encoding and the API contract without contacting AstroApp.
const cfg_ast = {api_key: 'fixture/+&="<>', endpoint: 'https://invalid.example/script.js'};
const url_app = new URL(url_ast(cfg_ast));
assert.equal(url_app.origin + url_app.pathname, 'https://astroapp.com/astro/astroapi');
assert.equal(url_app.searchParams.get('key'), cfg_ast.api_key);
for (const txt_val of ['', 'your_API_Access_Code', ' x ', '\n', 'x'.repeat(4097)]) assert.throws(() => url_ast({api_key: txt_val}));
assert.throws(() => url_ast({}));
const txt_pag = crt_ast({...dat_ast, unexpected: '</script><script>bad()</script>'}, cfg_ast, 7);
assert(txt_pag.indexOf('src="https://astroapp.com/astro/astroapi?key=') < txt_pag.indexOf('</head>'));
assert(txt_pag.includes('id="astroappDiv"'));
assert(!txt_pag.includes('http://astroapp.com'));
assert(!txt_pag.includes('</script><script>bad()'));
assert(!txt_pag.includes('invalid.example'));
assert.throws(() => crt_ast(dat_ast, cfg_ast, 'x" onload="bad()'));

const dat_hst = [];
const sys_cfg = {AstroApp: function () {this.aID=1;}, astroRun: dat_itm => dat_hst.push(['astroRun', dat_itm])};
for (const txt_val of ['setLongitude', 'setLatitude', 'setDate', 'setTime', 'setTimeZone', 'setHouseSys', 'setAyanamsa', 'setCoordSys', 'setStyle', 'setLanguage', 'setHeight', 'setVarga', 'needObjects', 'needAspects', 'needImage']) sys_cfg.AstroApp.prototype[txt_val] = function (...dat_env) { dat_hst.push([txt_val, ...dat_env]); };
for (const dat_itm of Object.values(dat_opt)) for (const txt_val of Object.values(dat_itm)) sys_cfg.AstroApp[txt_val] = txt_val;
const dat_res = run_ast(sys_cfg, dat_ast);
assert.deepEqual(dat_hst.slice(0, 5), [['setLongitude', '1E31'], ['setLatitude', '42N30'], ['setDate', '2000/02/29'], ['setTime', '13:05:00'], ['setTimeZone', '+01:00']]);
assert.equal(dat_hst.at(-1)[1], dat_res);
assert(dat_hst.some(dat_itm=>dat_itm[0]==='setStyle' && dat_itm[1]==='STYLE_PROPORTIONAL'));
assert(!dat_hst.some(dat_itm=>dat_itm[0]==='setVarga'),'A Western natal chart must retain the standard calculation.');
assert.equal(dat_res.aID,1);
assert.equal(fmt_ast({...dat_frm,varga:'60'}).varga,null,'A stale hidden division must not change a natal request.');
for (const clv_esc of Object.keys(dat_opt)) for (const txt_val of Object.keys(dat_opt[clv_esc])) assert.doesNotThrow(()=>run_ast(sys_cfg,fmt_ast({...dat_frm,chart:['south','north','lahiri','raman'].includes(txt_val)?'jyotish':'western',[clv_esc]:txt_val})));
dat_hst.length=0;
const dat_env=fmt_ast({...dat_frm,chart:'jyotish'});
assert.equal(dat_env.zodiac,'lahiri');assert.equal(dat_env.house,'whole');assert.equal(dat_env.style,'south');assert.equal(dat_env.varga,null);
assert.equal(run_ast(sys_cfg,dat_env).aID,1);
assert(!dat_hst.some(dat_itm=>dat_itm[0]==='setVarga'),'Rasi / D1 is not a divisional request.');
for(const cfg_apl of [{chart:'maya'},{chart:'western',style:'south'},{chart:'jyotish',zodiac:'tropical'},{chart:'jyotish',coordinates:'helio'},{chart:'varga',varga:1},{chart:'varga',varga:13}])assert.throws(()=>fmt_ast({...dat_frm,...cfg_apl}));
sys_cfg.AstroApp.prototype.setVarga=function(cnt_tot){this.aID='varga';this.param=cnt_tot;dat_hst.push(['setVarga',cnt_tot]);};
// Reproduce the currently served SDK: it stores param but drops it from getData.
sys_cfg.AstroApp.prototype.getData=function(){return {aID:this.aID};};
dat_hst.length=0;
assert.throws(()=>run_ast(sys_cfg,fmt_ast({...dat_frm,chart:'varga',varga:9})),/omits the divisional chart number/);
assert(!dat_hst.some(dat_itm=>dat_itm[0]==='astroRun'),'An incomplete division must never reach the provider.');
// A compatible encoder must carry the requested number without changing it.
sys_cfg.AstroApp.prototype.getData=function(){return {aID:this.aID,param:this.param};};
for(const cnt_tot of [2,3,4,5,6,7,8,9,10,11,12,16,20,24,27,30,40,45,60]){
  const dat_itm=run_ast(sys_cfg,fmt_ast({...dat_frm,chart:'varga',varga:cnt_tot}));
  assert.deepEqual(dat_itm.getData(),{aID:'varga',param:cnt_tot});
}
assert.deepEqual(Object.keys(dat_car),['western','jyotish','varga']);
assert.throws(() => run_ast({}, dat_ast));
delete sys_cfg.AstroApp.prototype.needImage;
dat_hst.length = 0;
assert.throws(() => run_ast(sys_cfg, dat_ast));
assert.equal(dat_hst.length, 0);
console.log('AstroApp: slash dates, natal/Rasi/divisional dispatch, cultural conventions, complete division requests, rejected broken SDK and coordinate/loader checks passed; no live API call.');
