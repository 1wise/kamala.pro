// Timestamp: 2026-11-02
// Version: 2.1.1
// Author & Credits: https://www.alawise.es/1-s
// Exercise delayed files and stale jobs without calculating charts or using keys.
import assert from 'node:assert/strict';
import {url_img,obs_img} from '../src/astroapp-image.mjs';
assert.equal(url_img('http://astroapp.com/astro/adata/outdb/chart.png?seed=abc','https://www.kamala.pro/'),'https://astroapp.com/astro/adata/outdb/chart.png?seed=abc');
assert.equal(url_img('https://cdn.example/chart.png?signature=abc%2B','https://www.kamala.pro/',2,100),'https://cdn.example/chart.png?signature=abc%2B');
const url_try=new URL(url_img('https://astroapp.com/astro/adata/outdb/chart.png?seed=abc','https://www.kamala.pro/',1,100));
assert.equal(url_try.searchParams.get('seed'),'abc');assert.equal(url_try.searchParams.get('_kamala_image_retry'),'100-1');
for(const txt_val of ['javascript:alert(1)','https://user:secret@astroapp.com/chart.png','http://untrusted.example/chart.png'])assert.throws(()=>url_img(txt_val,'https://www.kamala.pro/'));

function crt_prb(est_err=false) {
  let chr_ts=0,idx_job=0;
  const dat_tms=new Map(),dat_est=[],dat_req=[];
  const sys_win={
    MutationObserver:class {observe(){} disconnect(){}},
    setTimeout(act_fin,cnt_del){const idx_req=++idx_job;dat_tms.set(idx_req,{time:chr_ts+cnt_del,run:act_fin});return idx_req;},
    clearTimeout(idx_req){dat_tms.delete(idx_req);}
  };
  class ImgPrb extends EventTarget {
    constructor() {super();this.attrs=new Map([['src','https://astroapp.com/astro/adata/outdb/chart.png?seed=abc']]);this.complete=est_err;this.naturalWidth=0;}
    getAttribute(clv_esc){return this.attrs.get(clv_esc)||null;}
    setAttribute(clv_esc,txt_val){this.attrs.set(clv_esc,txt_val);if(clv_esc==='src'){dat_req.push(txt_val);this.complete=false;this.naturalWidth=0;}}
    removeAttribute(clv_esc){this.attrs.delete(clv_esc);}
    set src(txt_val){this.setAttribute('src',txt_val);}
    get src(){return this.getAttribute('src');}
  }
  const dmn_img=new ImgPrb();
  const dmn_out={ownerDocument:{defaultView:sys_win,baseURI:'https://www.kamala.pro/astrology/'},images:[dmn_img],
    contains(dmn_vis){return this.images.includes(dmn_vis);},querySelectorAll(){return this.images;}};
  const ctl_img=obs_img(dmn_out,txt_est=>dat_est.push(txt_est));
  function avanza(cnt_del) {
    const chr_fin=chr_ts+cnt_del;
    while(true) {
      const dat_env=[...dat_tms.entries()].filter(([,dat_itm])=>dat_itm.time<=chr_fin).sort((a,b)=>a[1].time-b[1].time)[0];
      if(!dat_env)break;
      chr_ts=dat_env[1].time;dat_tms.delete(dat_env[0]);dat_env[1].run();
    }
    chr_ts=chr_fin;
  }
  return {ctl_img,dmn_img,dmn_out,dat_est,dat_req,dat_tms,avanza,newImage:()=>new ImgPrb()};
}
{
  const prb=crt_prb(true);assert.equal(prb.ctl_img.refresh(),1);assert.equal(prb.dat_est.at(-1),'loading');
  prb.avanza(800);assert.equal(prb.dat_req.length,1);assert.match(prb.dat_req[0],/_kamala_image_retry=/);
  prb.dmn_img.complete=true;prb.dmn_img.naturalWidth=830;prb.dmn_img.dispatchEvent(new Event('load'));
  assert.equal(prb.dat_est.at(-1),'loaded');prb.avanza(30000);assert.equal(prb.dat_req.length,1);
}
{
  const prb=crt_prb();prb.ctl_img.refresh();
  prb.dmn_img.dispatchEvent(new Event('error'));prb.dmn_img.dispatchEvent(new Event('error'));prb.avanza(800);
  assert.equal(prb.dat_req.length,1,'Duplicate errors must not schedule duplicate requests');
  prb.dmn_img.dispatchEvent(new Event('error'));prb.avanza(2000);
  assert.equal(prb.dat_req.length,2);prb.dmn_img.dispatchEvent(new Event('error'));
  assert.equal(prb.dat_est.at(-1),'failed');assert.equal(prb.dat_tms.size,0);
  assert.equal(prb.ctl_img.retry(),1);assert.equal(prb.dat_est.at(-1),'loading');
  prb.dmn_img.complete=true;prb.dmn_img.naturalWidth=830;prb.dmn_img.dispatchEvent(new Event('load'));
  assert.equal(prb.dat_est.at(-1),'loaded');
}
{
  const prb=crt_prb();prb.dmn_img.complete=true;prb.dmn_img.naturalWidth=830;
  prb.dmn_out.images.push(prb.newImage());prb.ctl_img.refresh();
  assert.ok(!prb.dat_est.includes('loaded'),'All chart images must finish before reporting success');
  assert.equal(prb.dat_est.at(-1),'loading');prb.ctl_img.stop();
}
{
  const prb=crt_prb();prb.ctl_img.refresh();prb.dmn_img.dispatchEvent(new Event('error'));
  const cnt_ant=prb.dat_est.length;prb.ctl_img.stop();prb.avanza(40000);
  prb.dmn_img.naturalWidth=830;prb.dmn_img.dispatchEvent(new Event('load'));
  assert.equal(prb.dat_req.length,0);assert.equal(prb.dat_est.length,cnt_ant);
}
console.log('Delayed PNG retries, bounded failures, manual reload, cache policy and stale-job cleanup passed.');
