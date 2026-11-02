// Timestamp: 2026-11-01
// Version: 2.1.0
// Author & Credits: https://www.alawise.es/1-s
import {val_tel, act_tel, crt_demo} from './contemplation-core.mjs?v=2.1.0';

// Local brush motion is decorative. Only validated feed counters drive the signal.
const dmn_itm = document.querySelector('[data-contemplation]');
if (dmn_itm) {
  const sys_cnv = dmn_itm.querySelector('canvas');
  const sys_ctx = sys_cnv.getContext('2d', {alpha:false});
  const dmn_st = dmn_itm.querySelector('[data-flow-status]');
  const dmn_cap = dmn_itm.querySelector('[data-flow-caption]');
  const btn_pau = dmn_itm.querySelector('[data-flow-pause]');
  const btn_foc = dmn_itm.querySelector('[data-flow-focus]');
  const btn_ful = dmn_itm.querySelector('[data-flow-fullscreen]');
  const dat_qry = new URLSearchParams(location.search);
  const cfg_apl = {mode:dat_qry.get('src_mode') === 'demo' ? 'demo' : 'live',
    glow:Math.min(1.4,Math.max(.4,Number(dat_qry.get('int_lvl')) || .85))};
  const dat_mem = {};
  const dat_flu = {rx:0,tx:0,packets:0,notices:0,live:false,firewall:false};
  const dat_dst = {...dat_flu};
  const dat_pul = [];
  const sys_neb = document.createElement('canvas');
  sys_neb.width=192; sys_neb.height=192;
  const ctx_neb = sys_neb.getContext('2d');
  const dat_pix = ctx_neb.createImageData(192,192);
  const chr_ini = performance.now();
  const prf_mov = matchMedia('(prefers-reduced-motion: reduce)');
  let est_pau=prf_mov.matches, est_foc=false, est_fin=false, est_vis=!document.hidden;
  let chr_ant=0, chr_draw=0, chr_neb=-1000, chr_sig=0, chr_ani=0, cnt_fir=0;
  let tms_ren=null, req_ctl=null, sys_raf=null, dat_tel=null, idx_job=0;
  let sys_w=1000,sys_h=700,fac_dpr=1;

  function act_est(clv_esc, txt_val) {
    dmn_itm.dataset.signal=clv_esc;
    if (dmn_st.textContent!==txt_val) dmn_st.textContent=txt_val;
  }
  function fmt_flu(cnt_tot) {
    if (cnt_tot<1024) return Math.round(cnt_tot)+' B/s';
    if (cnt_tot<1048576) return (cnt_tot/1024).toFixed(1)+' KiB/s';
    if (cnt_tot<1073741824) return (cnt_tot/1048576).toFixed(2)+' MiB/s';
    return (cnt_tot/1073741824).toFixed(2)+' GiB/s';
  }
  function act_dat(dat_env, est_dem=false) {
    dat_tel=dat_env;
    Object.assign(dat_dst,act_tel(dat_env,dat_mem));
    chr_sig=performance.now();
    if (dat_dst.notices && !est_pau && !prf_mov.matches) {
      // Many log lines become one gentle pulse, avoiding a strobe during a burst.
      dat_pul.push({time:chr_ani,strength:Math.min(1,.35+Math.log2(1+dat_dst.notices)/5)});
      if (dat_pul.length>3) dat_pul.shift();
    }
    cnt_fir=dat_env.firewall.total;
    dmn_itm.querySelector('[data-flow-rx]').textContent=fmt_flu(dat_env.rx_bps);
    dmn_itm.querySelector('[data-flow-tx]').textContent=fmt_flu(dat_env.tx_bps);
    dmn_itm.querySelector('[data-flow-firewall]').textContent=dat_env.firewall.available ? cnt_fir+' logged' : 'Journal unavailable';
    act_est(est_dem?'demo':'live',est_dem?'Demo · simulated signals':dat_env.link_up?'Live · receiving telemetry':'Live feed · link down');
    dmn_cap.textContent=est_dem
      ? 'Demo mode. Traffic and firewall notices are simulated; no Excalibur measurements are being shown.'
      : 'Live aggregate signal from enp6s0. '+(dat_env.firewall.available?'Amber reflections mark newly logged firewall notices.':'The firewall journal is unavailable; traffic remains visible.');
    if (est_pau) {Object.assign(dat_flu,dat_dst);crt_vis(chr_ani);}
  }
  function act_err(est_old=false) {
    dat_dst.rx=0;dat_dst.tx=0;dat_dst.packets=0;dat_dst.live=false;
    act_est(est_old?'stale':'offline',est_old?'Stale feed · waiting for a fresh sample':'Live feed unavailable');
    dmn_itm.querySelector('[data-flow-rx]').textContent='—';
    dmn_itm.querySelector('[data-flow-tx]').textContent='—';
    dmn_itm.querySelector('[data-flow-firewall]').textContent='Waiting';
    dmn_cap.textContent='No fresh Excalibur sample is available. The collector must publish /telemetry/contemplation.json on this host. Demo is available as a separate simulated view.';
    if (est_pau) crt_vis(chr_ani);
  }
  async function pet_tel() {
    if (!est_vis || est_fin) return;
    const idx_req=idx_job;
    if (cfg_apl.mode==='demo') {
      act_dat(crt_demo((performance.now()-chr_ini)/1000),true);
      tms_ren=setTimeout(pet_tel,2000); return;
    }
    req_ctl=new AbortController();
    const tms_lim=setTimeout(()=>req_ctl?.abort(),3500);
    try {
      const rsp_env=await fetch('/telemetry/contemplation.json',{cache:'no-store',credentials:'same-origin',signal:req_ctl.signal,headers:{Accept:'application/json'}});
      if (!rsp_env.ok) throw new Error('Feed unavailable');
      const txt_val=await rsp_env.text();
      if (txt_val.length>16384) throw new Error('Feed too large');
      const dat_env=val_tel(JSON.parse(txt_val));
      if (idx_req===idx_job && cfg_apl.mode==='live' && est_vis) act_dat(dat_env);
    } catch (err_env) {
      if (idx_req===idx_job && cfg_apl.mode==='live' && est_vis) act_err(err_env instanceof RangeError || !!dat_tel);
    } finally {
      clearTimeout(tms_lim);
      if (idx_req===idx_job && est_vis && !est_fin) tms_ren=setTimeout(pet_tel,2000);
    }
  }
  function act_mod(clv_esc) {
    idx_job++; clearTimeout(tms_ren); req_ctl?.abort();
    cfg_apl.mode=clv_esc; dat_mem.session=null;dat_tel=null;dat_pul.length=0;
    for (const clv_itm of ['rx','tx','packets']) {dat_dst[clv_itm]=0;dat_flu[clv_itm]=0;}
    dat_dst.live=false;dat_flu.live=false;
    dmn_itm.querySelector('[data-flow-live]').setAttribute('aria-pressed',String(clv_esc==='live'));
    dmn_itm.querySelector('[data-flow-demo]').setAttribute('aria-pressed',String(clv_esc==='demo'));
    act_est('waiting',clv_esc==='live'?'Connecting to the live feed…':'Demo · simulated signals');
    pet_tel();
  }
  function act_tam() {
    const dat_rec=sys_cnv.getBoundingClientRect();
    sys_w=Math.max(1,dat_rec.width);sys_h=Math.max(1,dat_rec.height);
    // Limit the pixel budget for an uninterrupted quiet room on mobile hardware.
    fac_dpr=Math.min(devicePixelRatio || 1,1.5,Math.sqrt(2200000/(sys_w*sys_h)));
    sys_cnv.width=Math.round(sys_w*fac_dpr);sys_cnv.height=Math.round(sys_h*fac_dpr);
    sys_ctx.setTransform(fac_dpr,0,0,fac_dpr,0,0);
    crt_vis(chr_ani);
  }
  function crt_rad(cnt_x,cnt_y,cnt_r,dat_col,cnt_ex=0,cnt_ey=0) {
    const sys_grd=sys_ctx.createRadialGradient(cnt_x,cnt_y,0,cnt_x+cnt_ex,cnt_y+cnt_ey,cnt_r);
    for (const [fac_itm,txt_val] of dat_col) sys_grd.addColorStop(fac_itm,txt_val);
    return sys_grd;
  }
  function crt_elip(cnt_x,cnt_y,cnt_rx,cnt_ry,txt_col) {
    sys_ctx.beginPath();sys_ctx.ellipse(cnt_x,cnt_y,cnt_rx,cnt_ry,0,0,Math.PI*2);
    sys_ctx.fillStyle=txt_col;sys_ctx.fill();
  }
  function crt_fnd(chr_ts) {
    sys_ctx.fillStyle='#030309';sys_ctx.fillRect(0,0,sys_w,sys_h);
    const cnt_x=sys_w*.5,cnt_y=sys_h*.53;
    sys_ctx.fillStyle=crt_rad(cnt_x,cnt_y,sys_h*.68,[[0,'#181025'],[.5,'#0b0815'],[1,'#030309']]);
    sys_ctx.fillRect(0,0,sys_w,sys_h);
    // An almost invisible horizon gives the objects a material resting place.
    sys_ctx.fillStyle=sys_ctx.createLinearGradient(0,sys_h*.78,0,sys_h);
    sys_ctx.fillStyle='#07060c';sys_ctx.fillRect(0,sys_h*.79,sys_w,sys_h*.21);
    sys_ctx.strokeStyle='#8d77990c';sys_ctx.lineWidth=1;
    sys_ctx.beginPath();sys_ctx.moveTo(0,sys_h*.79);sys_ctx.lineTo(sys_w,sys_h*.79);sys_ctx.stroke();
  }
  function crt_cera(cnt_x,cnt_y,cnt_r,cnt_alt,fac_luz) {
    const sys_grd=sys_ctx.createLinearGradient(cnt_x-cnt_r,0,cnt_x+cnt_r,0);
    sys_grd.addColorStop(0,'#352a25');sys_grd.addColorStop(.18,'#85725a');
    sys_grd.addColorStop(.43,'#d2bf98');sys_grd.addColorStop(.68,'#a48d6b');sys_grd.addColorStop(1,'#31252a');
    sys_ctx.fillStyle=sys_grd;
    sys_ctx.beginPath();sys_ctx.moveTo(cnt_x-cnt_r,cnt_y);
    sys_ctx.bezierCurveTo(cnt_x-cnt_r*.98,cnt_y+cnt_alt*.3,cnt_x-cnt_r*1.04,cnt_y+cnt_alt*.8,cnt_x-cnt_r*.97,cnt_y+cnt_alt);
    sys_ctx.quadraticCurveTo(cnt_x,cnt_y+cnt_alt+cnt_r*.32,cnt_x+cnt_r*.99,cnt_y+cnt_alt);
    sys_ctx.lineTo(cnt_x+cnt_r,cnt_y);sys_ctx.closePath();sys_ctx.fill();
    // Irregular wax rivulets are drawn as material rather than animated telemetry.
    for (let sys_idx=0;sys_idx<7;sys_idx++) {
      const cnt_dx=cnt_x+Math.sin(sys_idx*8.31)*cnt_r*.82;
      const cnt_len=cnt_alt*(.12+.36*(.5+.5*Math.sin(sys_idx*4.17)));
      sys_ctx.strokeStyle=sys_idx%2?'#e1cca025':'#271e2428';
      sys_ctx.lineWidth=2+sys_idx%3;
      sys_ctx.beginPath();sys_ctx.moveTo(cnt_dx,cnt_y+2);
      sys_ctx.bezierCurveTo(cnt_dx+3,cnt_y+cnt_len*.3,cnt_dx-3,cnt_y+cnt_len*.8,cnt_dx+1,cnt_y+cnt_len);
      sys_ctx.stroke();
    }
    crt_elip(cnt_x,cnt_y,cnt_r,cnt_r*.25,'#b8a07b');
    crt_elip(cnt_x,cnt_y+1,cnt_r*.72,cnt_r*.17,'#69513a');
    const sys_luz=sys_ctx.createRadialGradient(cnt_x,cnt_y,0,cnt_x,cnt_y,cnt_r);
    sys_luz.addColorStop(0,'rgba(255,210,128,'+(.1+.45*fac_luz)+')');sys_luz.addColorStop(1,'#eac99c00');
    crt_elip(cnt_x,cnt_y,cnt_r,cnt_r*.25,sys_luz);
    sys_ctx.strokeStyle='#251e26';sys_ctx.lineWidth=2.5;sys_ctx.beginPath();
    sys_ctx.moveTo(cnt_x,cnt_y);sys_ctx.quadraticCurveTo(cnt_x-2,cnt_y-7,cnt_x+1,cnt_y-12);sys_ctx.stroke();
  }
  function crt_llama(cnt_x,cnt_y,cnt_r,cnt_alt,chr_ts,fac_luz,fac_evt) {
    if (fac_luz<.015) return;
    const cnt_vnt=Math.sin(chr_ts*1.7+dat_flu.tx*4)*cnt_r*(.1+.4*dat_flu.tx);
    const cnt_tip=cnt_x+cnt_vnt+Math.sin(chr_ts*2.9)*cnt_r*.14;
    const cnt_h=cnt_alt*(.9+.08*Math.sin(chr_ts*1.45)+.2*fac_evt);
    sys_ctx.save();sys_ctx.globalCompositeOperation='screen';
    sys_ctx.fillStyle=crt_rad(cnt_x,cnt_y-cnt_h*.32,cnt_h*1.05,[[0,'rgba(245,157,57,'+(.12*fac_luz)+')'],[.45,'rgba(180,84,35,'+(.035*fac_luz)+')'],[1,'#d5863000']]);
    sys_ctx.fillRect(cnt_x-cnt_h*1.4,cnt_y-cnt_h*1.6,cnt_h*2.8,cnt_h*2.8);
    for (let sys_idx=0;sys_idx<5;sys_idx++) {
      const fac_itm=1-sys_idx*.14;
      const sys_grd=sys_ctx.createLinearGradient(0,cnt_y-cnt_h,0,cnt_y);
      sys_grd.addColorStop(0,sys_idx<2?'#c86c3200':'#ffda9d00');
      sys_grd.addColorStop(.15,sys_idx<2?'#e2893b80':'#f7cb7dc0');
      sys_grd.addColorStop(.6,sys_idx<2?'#ffb745a0':'#fff1b9e0');
      sys_grd.addColorStop(.88,sys_idx<2?'#bf5e3c80':'#fffbeadd');
      sys_grd.addColorStop(1,'#51428620');
      sys_ctx.fillStyle=sys_grd;sys_ctx.globalAlpha=fac_luz*(.7+sys_idx*.05);
      sys_ctx.beginPath();sys_ctx.moveTo(cnt_x,cnt_y+2);
      sys_ctx.bezierCurveTo(cnt_x-cnt_r*1.35*fac_itm,cnt_y-cnt_h*.03,cnt_x-cnt_r*.8*fac_itm+cnt_vnt,cnt_y-cnt_h*.43,cnt_tip,cnt_y-cnt_h*fac_itm);
      sys_ctx.bezierCurveTo(cnt_x+cnt_r*.34*fac_itm+cnt_vnt,cnt_y-cnt_h*.5,cnt_x+cnt_r*1.15*fac_itm,cnt_y-cnt_h*.12,cnt_x,cnt_y+2);
      sys_ctx.fill();
    }
    sys_ctx.globalAlpha=fac_luz;
    crt_elip(cnt_x,cnt_y-2,cnt_r*.31,cnt_r*.24,'#5d66cc65');
    crt_elip(cnt_x,cnt_y-10,2,3,'#ffdc98');
    sys_ctx.restore();
  }
  function crt_cir(chr_ts,fac_evt) {
    const cnt_x=sys_w*.5,cnt_base=sys_h*.765;
    const cnt_r=Math.min(sys_h*.062,sys_w*.1),cnt_alt=sys_h*.215,cnt_y=cnt_base-cnt_alt;
    const fac_luz=dat_flu.live ? Math.min(1,(.48+.36*dat_flu.rx+.12*dat_flu.tx)*cfg_apl.glow) : dat_flu.rx*.3;
    sys_ctx.save();sys_ctx.globalCompositeOperation='screen';
    sys_ctx.fillStyle=crt_rad(cnt_x,cnt_y-sys_h*.07,sys_h*.4,[[0,'rgba(179,100,40,'+(.12*fac_luz)+')'],[.55,'rgba(70,40,45,'+(.035*fac_luz)+')'],[1,'#08040a00']]);
    sys_ctx.fillRect(0,0,sys_w,sys_h);sys_ctx.restore();
    crt_elip(cnt_x,cnt_base+sys_h*.025,cnt_r*2.6,cnt_r*.43,'#000009');
    // Turned brass catches the same changing light as the wax.
    const sys_grd=sys_ctx.createLinearGradient(0,cnt_base-8,0,cnt_base+15);
    sys_grd.addColorStop(0,'#a17b42');sys_grd.addColorStop(.2,'#d0b677');
    sys_grd.addColorStop(.44,'#332434');sys_grd.addColorStop(.68,'#7d5e35');sys_grd.addColorStop(1,'#1a1320');
    crt_elip(cnt_x,cnt_base+8,cnt_r*2.35,cnt_r*.41,sys_grd);
    sys_ctx.strokeStyle='#c09b5940';sys_ctx.lineWidth=1;sys_ctx.beginPath();
    sys_ctx.ellipse(cnt_x,cnt_base+4,cnt_r*2.25,cnt_r*.29,0,0,Math.PI*2);sys_ctx.stroke();
    crt_cera(cnt_x,cnt_y,cnt_r,cnt_alt,fac_luz);
    crt_llama(cnt_x,cnt_y-9,cnt_r*.48,sys_h*(.18+.06*dat_flu.rx),chr_ts,fac_luz,fac_evt);
    if (fac_evt>.01) {
      sys_ctx.save();sys_ctx.globalCompositeOperation='screen';
      crt_elip(cnt_x,cnt_base+6,cnt_r*2.2,cnt_r*.2,'rgba(240,166,71,'+fac_evt*.09+')');sys_ctx.restore();
    }
  }
  function crt_nube(chr_ts,fac_evt) {
    const cnt_t=chr_ts*.19*(.3+dat_flu.tx),fac_sig=.32+.68*dat_flu.rx;
    for (let cnt_y=0;cnt_y<192;cnt_y++) {
      const cnt_v=Math.sin(cnt_y*.068-cnt_t*1.4),cnt_m=Math.cos(cnt_y*.029+cnt_t);
      for (let cnt_x=0;cnt_x<192;cnt_x++) {
        const sys_idx=(cnt_y*192+cnt_x)*4;
        const cnt_a=Math.sin(cnt_x*.055+cnt_v*2+cnt_t)+Math.cos(cnt_x*.029-cnt_y*.042+cnt_t*.7)+Math.sin(cnt_x*.093+cnt_m*2-cnt_t*.6);
        const fac_n=Math.pow(Math.max(0,(cnt_a+2.3)/5.3),2);
        const cnt_rad=Math.hypot(cnt_x-96,cnt_y-96)/96;
        const fac_r=Math.max(0,1-cnt_rad*cnt_rad);
        dat_pix.data[sys_idx]=Math.round(49+fac_n*72+fac_evt*100*fac_n);
        dat_pix.data[sys_idx+1]=Math.round(39+fac_n*58+fac_evt*45*fac_n);
        dat_pix.data[sys_idx+2]=Math.round(91+fac_n*108-fac_evt*24);
        dat_pix.data[sys_idx+3]=Math.round(Math.min(180,fac_n*195*fac_r*fac_sig));
      }
    }
    ctx_neb.putImageData(dat_pix,0,0);
  }
  function crt_bola(chr_ts,fac_evt) {
    const cnt_r=Math.min(sys_h*.25,sys_w*.37),cnt_x=sys_w*.5,cnt_y=sys_h*.45;
    const fac_luz=cfg_apl.glow*(.55+.4*dat_flu.rx);
    sys_ctx.save();sys_ctx.globalCompositeOperation='screen';
    sys_ctx.fillStyle=crt_rad(cnt_x,cnt_y,cnt_r*1.65,[[0,'#46376d28'],[.6,'#42305d14'],[1,'#130a2600']]);
    sys_ctx.fillRect(0,0,sys_w,sys_h);sys_ctx.restore();
    crt_elip(cnt_x,cnt_y+cnt_r*1.27,cnt_r*.84,cnt_r*.12,'#000008');
    const sys_stn=sys_ctx.createLinearGradient(0,cnt_y+cnt_r*.95,0,cnt_y+cnt_r*1.28);
    sys_stn.addColorStop(0,'#9a7f52');sys_stn.addColorStop(.2,'#3c2c32');
    sys_stn.addColorStop(.6,'#6f5337');sys_stn.addColorStop(1,'#100d18');
    sys_ctx.fillStyle=sys_stn;sys_ctx.beginPath();
    sys_ctx.moveTo(cnt_x-cnt_r*.4,cnt_y+cnt_r*.87);sys_ctx.quadraticCurveTo(cnt_x-cnt_r*.17,cnt_y+cnt_r*1.08,cnt_x-cnt_r*.55,cnt_y+cnt_r*1.21);
    sys_ctx.quadraticCurveTo(cnt_x,cnt_y+cnt_r*1.35,cnt_x+cnt_r*.55,cnt_y+cnt_r*1.21);
    sys_ctx.quadraticCurveTo(cnt_x+cnt_r*.17,cnt_y+cnt_r*1.08,cnt_x+cnt_r*.4,cnt_y+cnt_r*.87);sys_ctx.closePath();sys_ctx.fill();
    crt_elip(cnt_x,cnt_y+cnt_r*.97,cnt_r*.44,cnt_r*.12,sys_stn);
    sys_ctx.save();sys_ctx.beginPath();sys_ctx.arc(cnt_x,cnt_y,cnt_r,0,Math.PI*2);sys_ctx.clip();
    sys_ctx.fillStyle=crt_rad(cnt_x-cnt_r*.35,cnt_y-cnt_r*.4,cnt_r*1.65,[[0,'#373044'],[.3,'#18132b'],[.7,'#0a0816'],[1,'#41354f']]);
    sys_ctx.fillRect(cnt_x-cnt_r,cnt_y-cnt_r,cnt_r*2,cnt_r*2);
    if (chr_ts-chr_neb>.08 || est_pau) {crt_nube(chr_ts,fac_evt);chr_neb=chr_ts;}
    sys_ctx.save();sys_ctx.globalCompositeOperation='screen';sys_ctx.globalAlpha=fac_luz;
    sys_ctx.translate(cnt_x,cnt_y);sys_ctx.rotate(Math.sin(chr_ts*.045)*.25);
    sys_ctx.drawImage(sys_neb,-cnt_r,-cnt_r,cnt_r*2,cnt_r*2);
    sys_ctx.globalAlpha=.35*fac_luz;sys_ctx.rotate(.8);
    sys_ctx.drawImage(sys_neb,-cnt_r*1.1,-cnt_r*.9,cnt_r*2.2,cnt_r*1.8);sys_ctx.restore();
    // Amber rings are linked to new journal counters, never invented in live mode.
    for (const dat_evt of dat_pul) {
      const cnt_age=chr_ts-dat_evt.time;
      if (cnt_age<0 || cnt_age>5) continue;
      sys_ctx.strokeStyle='rgba(231,177,102,'+(.2*dat_evt.strength*(1-cnt_age/5))+')';
      sys_ctx.lineWidth=1.2;sys_ctx.beginPath();
      sys_ctx.ellipse(cnt_x,cnt_y+cnt_r*.2,cnt_r*(.12+cnt_age*.22),cnt_r*(.04+cnt_age*.07),-.2,0,Math.PI*2);sys_ctx.stroke();
    }
    sys_ctx.save();sys_ctx.globalCompositeOperation='screen';
    for (let sys_idx=0;sys_idx<22;sys_idx++) {
      const cnt_a=sys_idx*2.399+chr_ts*.005*(.2+dat_flu.packets);
      const cnt_d=cnt_r*Math.sqrt((sys_idx+.5)/24)*.87;
      const cnt_px=cnt_x+Math.cos(cnt_a)*cnt_d,cnt_py=cnt_y+Math.sin(cnt_a)*cnt_d*.83;
      const fac_itm=.04+.15*(.5+.5*Math.sin(sys_idx+chr_ts*.35))*dat_flu.packets;
      crt_elip(cnt_px,cnt_py,sys_idx%4===0?1.1:.55,sys_idx%4===0?1.1:.55,'rgba(219,204,245,'+fac_itm+')');
    }
    // Surface refraction stays quiet while the interior carries the flow.
    sys_ctx.fillStyle=crt_rad(cnt_x,cnt_y,cnt_r,[[0,'#3d295300'],[.72,'#49395900'],[.9,'#c2a8dd22'],[.97,'#bdb9df4b'],[1,'#8b809b14']]);
    sys_ctx.fillRect(cnt_x-cnt_r,cnt_y-cnt_r,cnt_r*2,cnt_r*2);
    const sys_lun=sys_ctx.createLinearGradient(cnt_x-cnt_r,cnt_y-cnt_r,cnt_x+cnt_r,cnt_y+cnt_r);
    sys_lun.addColorStop(0,'#ddd9edaa');sys_lun.addColorStop(.28,'#c9c7dc18');sys_lun.addColorStop(.62,'#c0b8e000');sys_lun.addColorStop(1,'#d9cfdd45');
    sys_ctx.strokeStyle=sys_lun;sys_ctx.lineWidth=cnt_r*.022;sys_ctx.beginPath();sys_ctx.arc(cnt_x,cnt_y,cnt_r*.965,Math.PI*.86,Math.PI*1.77);sys_ctx.stroke();
    sys_ctx.translate(cnt_x-cnt_r*.37,cnt_y-cnt_r*.46);sys_ctx.rotate(-.7);
    const sys_ref=sys_ctx.createRadialGradient(0,0,0,0,0,cnt_r*.22);
    sys_ref.addColorStop(0,'#fffef2a0');sys_ref.addColorStop(.25,'#f1e9e65f');sys_ref.addColorStop(1,'#d3c8e000');
    crt_elip(0,0,cnt_r*.22,cnt_r*.09,sys_ref);
    sys_ctx.restore();sys_ctx.restore();
    sys_ctx.strokeStyle='#a397bb65';sys_ctx.lineWidth=.8;sys_ctx.beginPath();sys_ctx.arc(cnt_x,cnt_y,cnt_r,0,Math.PI*2);sys_ctx.stroke();
  }
  function crt_vis(chr_ts) {
    if (!sys_ctx) return;
    crt_fnd(chr_ts);
    let fac_evt=0;
    for (const dat_evt of dat_pul) fac_evt+=dat_evt.strength*Math.exp(-Math.max(0,chr_ts-dat_evt.time)*1.35);
    fac_evt=Math.min(.8,fac_evt);
    if (dmn_itm.dataset.contemplation==='candle') crt_cir(chr_ts,fac_evt);
    else crt_bola(chr_ts,fac_evt);
  }
  function act_ani(chr_ts) {
    if (est_fin || !est_vis) return;
    sys_raf=requestAnimationFrame(act_ani);
    if (est_pau) {chr_ant=chr_ts;return;}
    if (chr_ts-chr_draw<33) return;
    const cnt_dt=Math.min(.1,Math.max(0,(chr_ts-(chr_ant || chr_ts))/1000));
    chr_ant=chr_ts;chr_draw=chr_ts;chr_ani+=cnt_dt;
    for (const clv_esc of ['rx','tx','packets']) dat_flu[clv_esc]+=(dat_dst[clv_esc]-dat_flu[clv_esc])*(1-Math.exp(-cnt_dt*1.8));
    dat_flu.live=dat_dst.live;
    if (cfg_apl.mode==='live' && chr_sig && performance.now()-chr_sig>15000 && dmn_itm.dataset.signal==='live') act_err(true);
    while (dat_pul.length && chr_ani-dat_pul[0].time>6) dat_pul.shift();
    crt_vis(chr_ani);
  }
  function act_pau() {
    btn_pau.textContent=est_pau?'Resume motion':'Pause motion';
    btn_pau.setAttribute('aria-pressed',String(est_pau));
  }
  function act_foc(est_env) {
    est_foc=est_env;dmn_itm.classList.toggle('is-focused',est_foc);
    document.body.style.overflow=est_foc?'hidden':'';
    if (est_foc) dmn_itm.querySelector('[data-exit-focus]').focus();else btn_foc.focus();
    act_tam();
  }
  if (!sys_ctx) {
    act_est('offline','Canvas is unavailable in this browser');
    dmn_cap.textContent='A browser with Canvas 2D support is required for this room.';
  } else {
    dmn_itm.querySelector('[data-flow-glow]').value=String(Math.round(cfg_apl.glow*100));
    dmn_itm.querySelector('[data-flow-glow]').addEventListener('input',evt_ui=>{cfg_apl.glow=Number(evt_ui.target.value)/100;crt_vis(chr_ani);});
    dmn_itm.querySelector('[data-flow-live]').addEventListener('click',()=>act_mod('live'));
    dmn_itm.querySelector('[data-flow-demo]').addEventListener('click',()=>act_mod('demo'));
    btn_pau.addEventListener('click',()=>{est_pau=!est_pau;act_pau();chr_ant=0;crt_vis(chr_ani);});
    btn_foc.addEventListener('click',()=>act_foc(true));
    dmn_itm.querySelector('[data-exit-focus]').addEventListener('click',()=>act_foc(false));
    btn_ful.addEventListener('click',async()=>{
      try {if(document.fullscreenElement) await document.exitFullscreen();else await dmn_itm.requestFullscreen();}
      catch {dmn_cap.textContent='Fullscreen is unavailable. Focus view remains available.';}
    });
    if (!dmn_itm.requestFullscreen) {btn_ful.disabled=true;btn_ful.title='Fullscreen is unavailable in this browser';}
    document.addEventListener('fullscreenchange',()=>{btn_ful.textContent=document.fullscreenElement?'Exit fullscreen':'Fullscreen';act_tam();});
    document.addEventListener('keydown',evt_ui=>{
      if(evt_ui.key==='Escape'&&est_foc)act_foc(false);
      if(evt_ui.key==='Tab'&&est_foc){evt_ui.preventDefault();dmn_itm.querySelector('[data-exit-focus]').focus();}
    });
    const ob_tam=new ResizeObserver(act_tam);ob_tam.observe(sys_cnv);
    prf_mov.addEventListener('change',evt_ui=>{if(evt_ui.matches){est_pau=true;dat_pul.length=0;act_pau();crt_vis(chr_ani);}});
    document.addEventListener('visibilitychange',()=>{
      est_vis=!document.hidden;clearTimeout(tms_ren);req_ctl?.abort();cancelAnimationFrame(sys_raf);
      idx_job++;dat_mem.session=null;
      if(est_vis){chr_ant=0;pet_tel();sys_raf=requestAnimationFrame(act_ani);}
    });
    window.addEventListener('pagehide',()=>{est_fin=true;clearTimeout(tms_ren);req_ctl?.abort();cancelAnimationFrame(sys_raf);ob_tam.disconnect();});
    act_pau();act_tam();act_mod(cfg_apl.mode);sys_raf=requestAnimationFrame(act_ani);
  }
}
