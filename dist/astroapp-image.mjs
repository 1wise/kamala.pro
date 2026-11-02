// Timestamp: 2026-11-02
// Version: 2.1.1
// Author & Credits: https://www.alawise.es/1-s
// The SDK callback precedes PNG loading. Observe the image as a separate job.
export function url_img(txt_val, url_base, cnt_try=0, sys_ts=Date.now()) {
  const url_app=new URL(txt_val,url_base);
  if(url_app.username||url_app.password) throw new TypeError('Image credentials are not supported');
  const est_ast=['astroapp.com','www.astroapp.com'].includes(url_app.hostname);
  if(est_ast&&url_app.protocol==='http:') {url_app.protocol='https:';if(url_app.port==='80')url_app.port='';}
  const est_loc=url_app.origin===new URL(url_base).origin;
  const est_dat=url_app.protocol==='data:'&&/^data:image\/(?:png|jpeg|gif|webp|svg\+xml)[;,]/i.test(url_app.href);
  if(url_app.protocol!=='https:'&&!(est_loc&&url_app.protocol==='http:')&&!est_dat&&url_app.protocol!=='blob:') throw new TypeError('Unsupported chart image source');
  // Only the provider's observed static PNG directory accepts this cache buster.
  // All other query strings, including signed image URLs, remain unchanged.
  if(cnt_try>0&&est_ast&&url_app.pathname.startsWith('/astro/adata/outdb/')&&/\.png$/i.test(url_app.pathname)) url_app.searchParams.set('_kamala_image_retry',sys_ts+'-'+cnt_try);
  return url_app.href;
}

export function obs_img(dmn_out,act_est,cfg_apl={}) {
  const sys_win=dmn_out.ownerDocument.defaultView;
  const dat_img=new Map();
  const dat_del=cfg_apl.delays||[800,2000];
  const cnt_lim=cfg_apl.timeout||8000;
  let est_fin=false,est_rev=false;
  function act_rsp() {
    if(est_fin||est_rev||!dat_img.size)return;
    const dat_env=[...dat_img.values()];
    const txt_est=dat_env.every(dat_itm=>dat_itm.status==='loaded')?'loaded':dat_env.some(dat_itm=>dat_itm.status==='loading'||dat_itm.status==='retrying')?'loading':'failed';
    const dat_itm=dat_env[0];
    act_est(txt_est,{count:dat_env.length,url:dat_itm.expected||dat_itm.url});
  }
  function clr_tms(dat_itm) {sys_win.clearTimeout(dat_itm.timer);}
  function act_carga(dat_itm) {
    if(est_fin||!dmn_out.contains(dat_itm.img))return;
    if(!dat_itm.img.naturalWidth)return;
    clr_tms(dat_itm);dat_itm.status='loaded';act_rsp();
  }
  function act_err(dat_itm) {
    if(est_fin||!dmn_out.contains(dat_itm.img)||dat_itm.status==='loaded'||dat_itm.status==='retrying'||dat_itm.status==='failed')return;
    clr_tms(dat_itm);
    if(dat_itm.tries<dat_del.length) {
      dat_itm.status='retrying';act_rsp();
      dat_itm.timer=sys_win.setTimeout(()=>recarga(dat_itm),dat_del[dat_itm.tries]);
    } else {dat_itm.status='failed';act_rsp();}
  }
  function recarga(dat_itm) {
    if(est_fin||!dmn_out.contains(dat_itm.img))return;
    clr_tms(dat_itm);dat_itm.tries++;dat_itm.status='loading';
    dat_itm.expected=url_img(dat_itm.url,dmn_out.ownerDocument.baseURI,dat_itm.tries);
    dat_itm.img.removeAttribute('srcset');
    dat_itm.img.removeAttribute('src');
    dat_itm.img.setAttribute('src',dat_itm.expected);
    dat_itm.timer=sys_win.setTimeout(()=>act_err(dat_itm),cnt_lim);act_rsp();
  }
  function enlaza(dmn_img) {
    const txt_src=dmn_img.getAttribute('src');
    if(!txt_src)return;
    const dat_ant=dat_img.get(dmn_img);
    if(dat_ant&&(txt_src===dat_ant.expected||txt_src===dat_ant.url))return;
    if(dat_ant)desliga(dat_ant);
    let url_app;
    try {url_app=url_img(txt_src,dmn_out.ownerDocument.baseURI);}
    catch {act_est('failed',{count:1,url:null});return;}
    const dat_itm={img:dmn_img,url:url_app,expected:txt_src,tries:0,timer:null,status:'loading'};
    dat_itm.load=()=>act_carga(dat_itm);dat_itm.error=()=>act_err(dat_itm);
    dat_img.set(dmn_img,dat_itm);
    dmn_img.addEventListener('load',dat_itm.load);
    dmn_img.addEventListener('error',dat_itm.error);
    dmn_img.loading='eager';dmn_img.decoding='async';dmn_img.fetchPriority='high';
    if(!dmn_img.getAttribute('alt'))dmn_img.alt='Calculated AstroApp chart';
    if(url_app!==new URL(txt_src,dmn_out.ownerDocument.baseURI).href) {
      dat_itm.expected=url_app;dmn_img.src=url_app;
    }
    dat_itm.timer=sys_win.setTimeout(()=>act_err(dat_itm),cnt_lim);
    if(dmn_img.complete) {
      if(dmn_img.naturalWidth)act_carga(dat_itm);
      else act_err(dat_itm);
    }
  }
  function desliga(dat_itm) {
    clr_tms(dat_itm);dat_itm.img.removeEventListener('load',dat_itm.load);
    dat_itm.img.removeEventListener('error',dat_itm.error);dat_img.delete(dat_itm.img);
  }
  function revisa() {
    if(est_fin)return 0;
    est_rev=true;
    for(const dat_itm of dat_img.values())if(!dmn_out.contains(dat_itm.img))desliga(dat_itm);
    for(const dmn_img of dmn_out.querySelectorAll('img'))enlaza(dmn_img);
    est_rev=false;
    act_rsp();return dat_img.size;
  }
  const ob_mut=new sys_win.MutationObserver(revisa);
  ob_mut.observe(dmn_out,{childList:true,subtree:true,attributes:true,attributeFilter:['src']});
  return {
    refresh:revisa,
    retry() {
      revisa();
      for(const dat_itm of dat_img.values()){dat_itm.tries=0;dat_itm.status='loading';recarga(dat_itm);}
      return dat_img.size;
    },
    stop() {est_fin=true;ob_mut.disconnect();for(const dat_itm of [...dat_img.values()])desliga(dat_itm);}
  };
}
