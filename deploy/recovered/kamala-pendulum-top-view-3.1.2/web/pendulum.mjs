// Timestamp: 2026-11-07
// Version: 3.1.2
// Author & Credits: https://www.alawise.es/1-s
import {val_pnd, est_pnd, fil_mst, exp_csv, crt_trz, pry_sup} from './pendulum-core.mjs?v=3.1.2';

const dmn_pnd = document.querySelector('[data-pendulum]');
if (dmn_pnd) act_pnd(dmn_pnd);

function act_pnd(dmn_pnd) {
  const obt = txt_sel => dmn_pnd.querySelector(txt_sel);
  const img_cam = obt('[data-pnd-image]');
  const btn_cam = obt('[data-pnd-camera-toggle]');
  const dmn_sta = obt('[data-pnd-status]');
  const dmn_trz = obt('[data-pnd-trace]');
  const dmn_pos = obt('[data-pnd-position]');
  const btn_csv = obt('[data-pnd-export]');
  const url_cam = img_cam.getAttribute('src');
  const dat_txt = {
    waiting:['Waiting','No measured CV sample has arrived yet. The image can be viewed independently.'],
    live:['Tracking','Position and motion are updating.'],
    swing:['Movement','Measured displacement reaches the display threshold. Source events are recorded separately.'],
    'low-fit':['Low fit','Weak geometric fit. The source may be holding an earlier position; this sample is omitted from the traces.'],
    'low-light':['Low light','Low light: the tracker may hold its previous position.'],
    stale:['Last sample','Last received values. Fresh measurements are unavailable.'],
    disconnected:['Offline','The collector or upstream stream is unavailable.']
  };
  let dat_tel = null, clv_gra = 'displacement', cnt_seg = 60;
  let est_cam = true, est_fin = false, est_pet = false, sys_pet = null;
  let tms_pnd = 0, tms_cam = 0, sys_ult = null, chr_ult = 0;
  let sys_ref = null, chr_ref = 0;
  const fmt_num = (val_res, cnt_dec=1, est_sig=false) => typeof val_res !== 'number' ? '—' :
    (est_sig && val_res>0?'+':'')+val_res.toFixed(cnt_dec);
  const fmt_utc = sys_ts => new Date(sys_ts*1000).toISOString().replace('T',' ').replace('Z',' UTC');
  const txt_svg = (pos_x,pos_y,txt_val,txt_ext='') => '<text x="'+pos_x+'" y="'+pos_y+'" '+txt_ext+'>'+txt_val+'</text>';
  const est_3d = () => dat_tel?.sample?.mode === '3d-mm';
  const unt_mst = () => dat_tel?.sample && !est_3d() ? 'px' : 'mm';

  function crt_gra(dat_hst) {
    const dat_nom = clv_gra==='displacement'?['displacement']:clv_gra==='depth'?['dz']:
      clv_gra==='offset'?(est_3d()?['dx','dy','dz']:['dx','dy']):(est_3d()?['vx','vy','vz']:['vx','vy']);
    const dat_val = dat_hst.filter(dat_pnd=>dat_pnd.tracking_valid)
      .flatMap(dat_pnd=>dat_nom.map(clv_nom=>dat_pnd[clv_nom])).filter(Number.isFinite);
    const val_max = Math.max(clv_gra==='displacement'?(dat_tel?.threshold??15)*1.2:10,...dat_val.map(val_res=>Math.abs(val_res)))*1.12;
    const val_min = clv_gra==='displacement'?0:-val_max;
    const sys_fin = dat_tel?.sample?.ts ?? 0;
    const fac_x = sys_ts => 64+((sys_ts-(sys_fin-cnt_seg))/cnt_seg)*588;
    const fac_y = val_res => 226-((val_res-val_min)/(val_max-val_min))*200;
    let txt_val = '';
    for (let sys_idx=0;sys_idx<=4;sys_idx++) {
      const pos_y=26+sys_idx*50;
      txt_val+='<line class="pnd-grid" x1="64" x2="652" y1="'+pos_y+'" y2="'+pos_y+'"/>';
      txt_val+=txt_svg(52,pos_y+3,fmt_num(val_max-(val_max-val_min)*sys_idx/4,0),'text-anchor="end"');
    }
    for (let sys_idx=0;sys_idx<=4;sys_idx++) {
      const pos_x=64+sys_idx*147;
      txt_val+='<line class="pnd-grid" x1="'+pos_x+'" x2="'+pos_x+'" y1="26" y2="226"/>';
    }
    txt_val+=txt_svg(64,250,'−'+cnt_seg+'s')+txt_svg(358,250,'−'+cnt_seg/2+'s','text-anchor="middle"')+txt_svg(652,250,'latest','text-anchor="end"');
    txt_val+=txt_svg(16,14,unt_mst()+(clv_gra==='velocity'?'/s':''));
    if (clv_gra==='displacement') {
      const pos_y=fac_y(dat_tel?.threshold??15);
      txt_val+='<line class="pnd-plot-threshold" x1="64" x2="652" y1="'+pos_y+'" y2="'+pos_y+'"/>';
      txt_val+=txt_svg(646,pos_y-5,(dat_tel?.threshold??15)+' '+unt_mst(),'text-anchor="end"');
    }
    for (const [sys_idx,clv_nom] of dat_nom.entries()) {
      txt_val+='<path class="pnd-plot-line'+(clv_gra==='depth'||sys_idx===2?' third':sys_idx===1?' second':'')+'" d="'+crt_trz(dat_hst,clv_nom,fac_x,fac_y)+'"/>';
    }
    if (!dat_val.length) txt_val+=txt_svg(358,129,'Waiting for usable measurements','text-anchor="middle"');
    dmn_trz.innerHTML=txt_val;
    dmn_trz.setAttribute('aria-label',(clv_gra==='displacement'?'Displacement':clv_gra==='depth'?'Z depth change':clv_gra==='offset'?'Axis displacement':'Axis velocity')+' in '+unt_mst()+(clv_gra==='velocity'?' per second':'')+' over the last '+cnt_seg+' seconds.');
    const txt_leg=clv_gra==='displacement'?'Amplitude · dashed reference threshold':clv_gra==='depth'?'Red: Z · positive away from lens':
      'Indigo: X · Green: Y'+(est_3d()?' · Red: Z':'');
    obt('[data-pnd-legend]').textContent=txt_leg+' · '+unt_mst()+(clv_gra==='velocity'?'/s':'')+' · sampled display';
  }

  function crt_pos(dat_hst) {
    const dat_pnd=dat_tel?.sample;
    const dat_val=dat_hst.filter(dat_itm=>pry_sup(dat_itm)!==null);
    const val_umb=est_3d()?(dat_tel?.threshold??15):15;
    const val_max=Math.max(val_umb*1.5,...dat_val.flatMap(dat_itm=>[Math.abs(dat_itm.dx),Math.abs(dat_itm.dz)]),
      ...(pry_sup(dat_pnd)?[Math.abs(dat_pnd.dx),Math.abs(dat_pnd.dz)]:[]))*1.2;
    const fac_esc=105/val_max;
    let txt_val='';
    for (const pos_x of [65,117.5,170,222.5,275]) txt_val+='<line class="pnd-grid" x1="'+pos_x+'" x2="'+pos_x+'" y1="20" y2="230"/>';
    for (const pos_y of [20,72.5,125,177.5,230]) txt_val+='<line class="pnd-grid" x1="65" x2="275" y1="'+pos_y+'" y2="'+pos_y+'"/>';
    txt_val+='<line class="pnd-axis" x1="65" x2="275" y1="125" y2="125"/><line class="pnd-axis" x1="170" x2="170" y1="20" y2="230"/>';
    if (est_3d()) txt_val+='<circle class="pnd-plot-threshold" cx="170" cy="125" r="'+(val_umb*fac_esc)+'"/>';
    txt_val+='<circle cx="170" cy="125" r="3" fill="#82728f"/>';
    let txt_trz='',dat_ant=null;
    for (const dat_itm of dat_hst) {
      const pos_sup=pry_sup(dat_itm,fac_esc);
      if (!pos_sup) {dat_ant=null;continue;}
      txt_trz+=(!dat_ant||dat_itm.ts-dat_ant.ts>2?'M':'L')+pos_sup.x.toFixed(2)+','+pos_sup.y.toFixed(2)+' ';
      dat_ant=dat_itm;
    }
    txt_val+='<path class="pnd-plot-line" opacity=".6" d="'+txt_trz+'"/>';
    const pos_sup=pry_sup(dat_pnd,fac_esc);
    if (pos_sup) txt_val+='<circle cx="'+pos_sup.x+'" cy="'+pos_sup.y+'" r="5" fill="'+(dat_pnd.displacement>=val_umb?'#e6b08a':'#c3adff')+'"/>';
    if (!dat_val.length&&!pos_sup) txt_val+=txt_svg(170,264,'Waiting for usable 3D data','text-anchor="middle"');
    else txt_val+=txt_svg(170,264,'±'+Math.round(val_max)+' mm · top view XZ','text-anchor="middle"');
    txt_val+=txt_svg(284,128,'+X')+txt_svg(170,12,'+Z · away','text-anchor="middle"')+
      txt_svg(170,246,'−Z · camera','text-anchor="middle"');
    dmn_pos.innerHTML=txt_val;
    dmn_pos.setAttribute('aria-label',pos_sup?'Top view: X '+fmt_num(dat_pnd.dx)+' and Z '+fmt_num(dat_pnd.dz)+' millimeters from equilibrium. Positive Z is away from the camera.':'Top view XZ, waiting for usable 3D measurements.');
    obt('[data-pnd-map-note]').textContent=est_3d()?'Circle: '+val_umb+' mm radius in the XZ plane. Y is vertical; total amplitude uses XYZ.':'The top view requires X and Z measurements in millimeters.';
  }

  function crt_evn() {
    const dmn_evn=obt('[data-pnd-events]');
    const dat_evn=dat_tel?.events.slice(-6).reverse()??[];
    if (!dat_evn.length) {
      dmn_evn.innerHTML='<li class="pnd-empty">Events appear after an observed counter increase.</li>';
      return;
    }
    dmn_evn.replaceChildren(...dat_evn.map(dat_itm=>{
      const dmn_itm=document.createElement('li');
      const dmn_hor=document.createElement('time');
      dmn_hor.dateTime=new Date(dat_itm.ts*1000).toISOString();
      dmn_hor.textContent=dmn_hor.dateTime.slice(11,19);
      const dmn_nom=document.createElement('strong');
      dmn_nom.textContent='Event '+dat_itm.count+(dat_itm.delta>1?' · +'+dat_itm.delta:'');
      if (!dat_itm.tracking_valid) {const dmn_luz=document.createElement('small');dmn_luz.textContent=' · weak tracking';dmn_nom.append(dmn_luz);}
      const dmn_rad=document.createElement('span');dmn_rad.textContent=fmt_num(dat_itm.displacement)+' '+(dat_itm.mode==='3d-mm'?'mm':'px');
      dmn_itm.append(dmn_hor,dmn_nom,dmn_rad);return dmn_itm;
    }));
  }

  function act_vis() {
    const est_frs=sys_ult===null||performance.now()-chr_ult<10000;
    // Compare server receipt times with its HTTP clock, not the visitor's clock.
    const sys_ts=sys_ref===null?Date.now()/1000:sys_ref+(performance.now()-chr_ref)/1000;
    const clv_est=est_pnd(dat_tel,sys_ts,est_frs);
    dmn_pnd.dataset.state=clv_est;dmn_sta.dataset.state=clv_est;
    if(dmn_sta.textContent!==dat_txt[clv_est][0])dmn_sta.textContent=dat_txt[clv_est][0];
    obt('[data-pnd-message]').textContent=dat_txt[clv_est][1];
    const dat_pnd=dat_tel?.sample;
    for(const dmn_itm of dmn_pnd.querySelectorAll('[data-pnd-value]')) {
      const clv_nom=dmn_itm.dataset.pndValue;
      dmn_itm.textContent=dat_pnd?fmt_num(dat_pnd[clv_nom],['events','fit_pct','luminance'].includes(clv_nom)?0:1,['dx','dy','dz','vx','vy','vz'].includes(clv_nom)):'—';
    }
    for(const dmn_itm of dmn_pnd.querySelectorAll('[data-pnd-unit]'))dmn_itm.textContent=unt_mst()+(dmn_itm.dataset.pndUnit==='velocity'?'/s':'');
    obt('[data-pnd-quality-label]').textContent=dat_pnd&&!est_3d()?'HIGHLIGHT BRIGHTNESS':'GEOMETRIC FIT';
    obt('[data-pnd-quality]').textContent=dat_pnd?fmt_num(est_3d()?dat_pnd.fit_pct:dat_pnd.luminance,0):'—';
    obt('[data-pnd-quality-unit]').textContent=dat_pnd&&!est_3d()?'/ 255':'%';
    obt('[data-pnd-threshold]').textContent=(dat_tel?.threshold??15)+' '+unt_mst();
    obt('[data-pnd-amplitude-label]').textContent=dat_pnd&&!est_3d()?'Planar displacement':'3D displacement';
    obt('[data-pnd-source-alert]').textContent=dat_pnd?'Source alarm: '+(dat_pnd.alert?'active':'inactive'):'Source alarm: waiting';
    obt('[data-pnd-position-value]').textContent=pry_sup(dat_pnd)?fmt_num(dat_pnd.dx,1,true)+', '+fmt_num(dat_pnd.dz,1,true)+' mm':'—, — mm';
    obt('[data-pnd-anchor-value]').textContent=est_3d()?'0.0, 0.0 mm':'—, — mm';
    obt('[data-pnd-time]').textContent=dat_pnd?'Source '+fmt_utc(dat_pnd.ts)+' · '+(clv_est==='stale'?'last received sample':'Camera 4'):'No measured sample received';
    const dat_hst=fil_mst(dat_tel,cnt_seg);
    btn_csv.disabled=dat_hst.length===0;
    crt_gra(dat_hst);crt_pos(dat_hst);crt_evn();
  }

  async function pet_tel() {
    if(est_pet||est_fin||document.hidden)return;
    est_pet=true;sys_pet=new AbortController();
    const sys_ctl=sys_pet;
    const tms_lim=setTimeout(()=>sys_ctl.abort(),5000);
    try {
      const rsp_env=await fetch(dmn_pnd.dataset.endpoint,{cache:'no-store',credentials:'omit',signal:sys_ctl.signal});
      if(!rsp_env.ok)throw new Error('Telemetry unavailable.');
      if(Number(rsp_env.headers.get('Content-Length'))>256000)throw new Error('Oversized snapshot.');
      const txt_val=await rsp_env.text();
      if(txt_val.length>256000)throw new Error('Oversized snapshot.');
      const dat_nvo=val_pnd(JSON.parse(txt_val));
      const sys_dat=Date.parse(rsp_env.headers.get('Date'))/1000;
      if(Number.isFinite(sys_dat)){
        sys_ref=sys_dat+Math.max(0,Math.min(3600,Number(rsp_env.headers.get('Age'))||0));chr_ref=performance.now();
      }
      if(dat_nvo.sample&&(dat_nvo.sample.ts!==sys_ult||dat_nvo.session!==dat_tel?.session)){
        sys_ult=dat_nvo.sample.ts;chr_ult=performance.now();
      }
      dat_tel=dat_nvo;
    }catch(sys_err){
      if(dat_tel)dat_tel={...dat_tel,status:'disconnected'};
    }finally{
      clearTimeout(tms_lim);est_pet=false;
      if(sys_pet===sys_ctl)sys_pet=null;
      act_vis();clearTimeout(tms_pnd);
      if(!est_fin&&!document.hidden)tms_pnd=setTimeout(pet_tel,1000);
    }
  }

  function act_cam() {
    if(!est_cam){obt('[data-pnd-camera-status]').textContent='Image stopped';return;}
    if(img_cam.naturalWidth>0){
      obt('[data-pnd-camera-status]').textContent='Image connected';
      obt('[data-pnd-camera-note]').hidden=true;
    }
  }
  img_cam.addEventListener('load',act_cam);
  img_cam.addEventListener('error',()=>{
    if(!est_cam||document.hidden)return;
    obt('[data-pnd-camera-status]').textContent='Image unavailable';
    const dmn_note=obt('[data-pnd-camera-note]');dmn_note.hidden=false;
    dmn_note.textContent='Camera 4 is unavailable. Use Stop / Start image to reconnect, or open the source.';
  });
  btn_cam.addEventListener('click',()=>{
    est_cam=!est_cam;btn_cam.textContent=est_cam?'Stop image':'Start image';
    img_cam.hidden=!est_cam;
    if(est_cam){img_cam.src=url_cam;obt('[data-pnd-camera-status]').textContent='Connecting image';}
    else{img_cam.removeAttribute('src');act_cam();}
  });
  function sal_cam() {
    obt('.pnd-camera').classList.remove('is-expanded');document.body.classList.remove('pnd-expanded');
    obt('[data-pnd-fullscreen]').textContent='Fullscreen';obt('[data-pnd-fullscreen]').setAttribute('aria-pressed','false');
  }
  obt('[data-pnd-fullscreen]').addEventListener('click',async()=>{
    const dmn_cam=obt('.pnd-camera');
    if(dmn_cam.classList.contains('is-expanded')){
      sal_cam();if(document.fullscreenElement){try{await document.exitFullscreen();}catch{}}return;
    }
    // An in-page expansion also works when the host denies native fullscreen.
    dmn_cam.classList.add('is-expanded');document.body.classList.add('pnd-expanded');
    obt('[data-pnd-fullscreen]').textContent='Exit fullscreen';obt('[data-pnd-fullscreen]').setAttribute('aria-pressed','true');
    try{if(dmn_cam.requestFullscreen)await dmn_cam.requestFullscreen();}catch{}
  });
  document.addEventListener('keydown',sys_evn=>{if(sys_evn.key==='Escape')sal_cam();});
  document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement)sal_cam();});
  for(const btn_itm of dmn_pnd.querySelectorAll('[data-pnd-metric]'))btn_itm.addEventListener('click',()=>{
    clv_gra=btn_itm.dataset.pndMetric;
    for(const btn_otr of dmn_pnd.querySelectorAll('[data-pnd-metric]'))btn_otr.setAttribute('aria-pressed',String(btn_itm===btn_otr));
    act_vis();
  });
  obt('[data-pnd-window]').addEventListener('change',sys_evn=>{cnt_seg=Number(sys_evn.target.value);act_vis();});
  btn_csv.addEventListener('click',()=>{
    const dat_hst=fil_mst(dat_tel,cnt_seg);if(!dat_hst.length)return;
    const url_fil=URL.createObjectURL(new Blob([exp_csv(dat_hst)],{type:'text/csv;charset=utf-8'}));
    const dmn_lnk=document.createElement('a');dmn_lnk.href=url_fil;
    dmn_lnk.download='kamala-pendulum-'+new Date(dat_hst.at(-1).ts*1000).toISOString().replace(/[^0-9TZ]/g,'')+'.csv';
    document.body.append(dmn_lnk);dmn_lnk.click();dmn_lnk.remove();setTimeout(()=>URL.revokeObjectURL(url_fil),30000);
  });
  document.addEventListener('visibilitychange',()=>{
    clearTimeout(tms_pnd);
    if(document.hidden){sys_pet?.abort();img_cam.removeAttribute('src');}
    else{if(est_cam)img_cam.src=url_cam;pet_tel();}
  });
  window.addEventListener('pagehide',()=>{est_fin=true;sal_cam();clearTimeout(tms_pnd);clearInterval(tms_cam);sys_pet?.abort();img_cam.removeAttribute('src');});
  window.addEventListener('pageshow',sys_evn=>{if(sys_evn.persisted){est_fin=false;if(est_cam)img_cam.src=url_cam;tms_cam=setInterval(act_cam,1000);pet_tel();}});
  act_vis();pet_tel();tms_cam=setInterval(act_cam,1000);
}
