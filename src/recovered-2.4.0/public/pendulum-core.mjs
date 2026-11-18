// Timestamp: 2026-11-16
// Version: 3.6.0
// Author & Credits: https://www.alawise.es/1-s
// Keep image radii in pixels and physical movement in the source's declared units.
// Wind flags are source decisions; quantized DH does not reproduce their boundary.
function val_vnt(dat_vnt, est_alr) {
  if (dat_vnt == null) return null;
  if (typeof dat_vnt !== 'object' ||
      ['tilt_deg','dissociation','factor','threshold_xy_mm'].some(k=>!Number.isFinite(dat_vnt[k])) ||
      dat_vnt.tilt_deg < -180 || dat_vnt.tilt_deg > 180 ||
      dat_vnt.dissociation < 0 || dat_vnt.dissociation > 1 ||
      dat_vnt.factor < 0 || dat_vnt.factor > 2.5 ||
      typeof dat_vnt.turbulence !== 'boolean' ||
      dat_vnt.suppression_active !== dat_vnt.turbulence ||
      (dat_vnt.turbulence && est_alr)) throw new TypeError('Invalid wind measurement.');
  const umb_xy = dat_vnt.turbulence ? 15 * (1 + 2.5 * dat_vnt.factor) : 15;
  if (Math.abs(dat_vnt.threshold_xy_mm - umb_xy) > 0.001) throw new TypeError('Invalid wind threshold.');
  return Object.freeze({tilt_deg:dat_vnt.tilt_deg,dissociation:dat_vnt.dissociation,
    turbulence:dat_vnt.turbulence,factor:dat_vnt.factor,
    suppression_active:dat_vnt.suppression_active,threshold_xy_mm:umb_xy});
}

export function val_mst(dat_pnd) {
  if (!dat_pnd || typeof dat_pnd !== 'object') return null;
  if (!dat_pnd.mode && 'radius' in dat_pnd) {
    dat_pnd = {...dat_pnd, mode:'2d-px', displacement:dat_pnd.radius,
      r:null, ar:null, dz:null, vz:null, fit_pct:null,
      tracking_valid:dat_pnd.luminance > 75};
  }
  const est_3d = dat_pnd.mode === '3d-mm';
  if (!est_3d && dat_pnd.mode !== '2d-px') return null;
  const dat_nom = ['ts','x','y','ax','ay','dx','dy','vx','vy','displacement','events'];
  if (dat_nom.some(clv_nom => typeof dat_pnd[clv_nom] !== 'number' || !Number.isFinite(dat_pnd[clv_nom]))) return null;
  if (dat_pnd.ts <= 0 || dat_pnd.ts > 1e12 ||
      dat_pnd.x < 0 || dat_pnd.x >= 1280 || dat_pnd.y < 0 || dat_pnd.y >= 720 ||
      dat_pnd.ax < 0 || dat_pnd.ax >= 1280 || dat_pnd.ay < 0 || dat_pnd.ay >= 720 ||
      dat_pnd.displacement < 0 || dat_pnd.displacement > (est_3d?1e9:Math.hypot(1280,720)) ||
      !Number.isSafeInteger(dat_pnd.events) || dat_pnd.events < 0 ||
      typeof dat_pnd.alert !== 'boolean' ||
      ['dx','dy','vx','vy'].some(clv_nom => Math.abs(dat_pnd[clv_nom]) > 1e9)) return null;
  if (est_3d) {
    if (['r','ar','dz','vz'].some(clv_nom => typeof dat_pnd[clv_nom] !== 'number' ||
        !Number.isFinite(dat_pnd[clv_nom]) || Math.abs(dat_pnd[clv_nom]) > 1e9) ||
        dat_pnd.r <= 0 || dat_pnd.r > 640 || dat_pnd.ar <= 0 || dat_pnd.ar > 640 ||
        !Number.isInteger(dat_pnd.fit_pct) || dat_pnd.fit_pct < 0 || dat_pnd.fit_pct > 100 ||
        dat_pnd.luminance !== null) return null;
  } else if (!Number.isInteger(dat_pnd.luminance) || dat_pnd.luminance < 0 ||
      dat_pnd.luminance > 255 || ['r','ar','dz','vz','fit_pct'].some(clv_nom => dat_pnd[clv_nom] !== null)) return null;
  const est_val = est_3d ? dat_pnd.fit_pct > 15 : dat_pnd.luminance > 75;
  if (dat_pnd.tracking_valid !== est_val) return null;
  let dat_vnt;
  try { dat_vnt=val_vnt(dat_pnd.wind,dat_pnd.alert); } catch { return null; }
  if (dat_vnt && !est_3d) return null;
  return Object.freeze({...Object.fromEntries([
    ...[...dat_nom,'mode','r','ar','dz','vz','fit_pct','luminance','alert','tracking_valid']
      .map(clv_nom => [clv_nom,dat_pnd[clv_nom]])
  ]),wind:dat_vnt});
}

export function val_pnd(dat_tel) {
  if (!dat_tel || ![1,2,3].includes(dat_tel.version) || dat_tel.camera !== 'cam4' ||
      !['connecting','waiting','live','stale','disconnected','stopped'].includes(dat_tel.status) ||
      !Number.isFinite(dat_tel.collected_at) || dat_tel.collected_at <= 0 ||
      !Array.isArray(dat_tel.history) || dat_tel.history.length > 240 ||
      !Array.isArray(dat_tel.events) || dat_tel.events.length > 20) throw new TypeError('Invalid pendulum snapshot.');
  const dat_pnd = dat_tel.sample === null ? null : val_mst(dat_tel.sample);
  if (dat_tel.sample !== null && !dat_pnd) throw new TypeError('Invalid pendulum measurement.');
  if (dat_tel.version >= 2 && dat_tel.sample !== null && !dat_tel.sample.mode) throw new TypeError('Missing measurement mode.');
  const dat_hst = dat_tel.history.map(val_mst);
  if (dat_hst.some(dat_itm => !dat_itm || dat_itm.mode !== dat_pnd?.mode) ||
      dat_hst.some((dat_itm,sys_idx) => sys_idx && dat_itm.ts <= dat_hst[sys_idx-1].ts) ||
      (dat_hst.length && dat_hst.at(-1).ts > dat_pnd.ts)) throw new TypeError('Invalid sample history.');
  const dat_evn = dat_tel.events.map(dat_itm => {
    const est_ant = dat_tel.version === 1;
    const val_des = est_ant ? dat_itm?.radius : dat_itm?.displacement;
    const est_val = est_ant ? dat_itm?.highlight : dat_itm?.tracking_valid;
    const txt_mod = est_ant ? '2d-px' : dat_itm?.mode;
    if (!dat_itm || !Number.isFinite(dat_itm.ts) || dat_itm.ts <= 0 ||
        !Number.isSafeInteger(dat_itm.count) || dat_itm.count < 0 ||
        !Number.isSafeInteger(dat_itm.delta) || dat_itm.delta < 1 ||
        !Number.isFinite(val_des) || val_des < 0 || val_des > 1e9 ||
        txt_mod !== dat_pnd?.mode || typeof est_val !== 'boolean') throw new TypeError('Invalid source event.');
    return {ts:dat_itm.ts,count:dat_itm.count,delta:dat_itm.delta,
      displacement:val_des,tracking_valid:est_val,mode:txt_mod,wind:val_vnt(dat_itm.wind,false)};
  });
  if (dat_tel.received_at !== null && (!Number.isFinite(dat_tel.received_at) ||
      dat_tel.received_at <= 0)) throw new TypeError('Invalid receipt time.');
  const est_3d = dat_pnd?.mode === '3d-mm';
  const val_umb = dat_tel.version === 1 ? 28 : dat_tel.limits?.threshold;
  if (!Number.isFinite(val_umb) || val_umb <= 0 || val_umb > 10000) throw new TypeError('Invalid display threshold.');
  if (dat_tel.version >= 2 && (dat_tel.units?.position !== 'px' ||
      dat_tel.units?.displacement !== (est_3d?'mm':'px') ||
      dat_tel.units?.velocity !== (est_3d?'mm/s':'px/s'))) throw new TypeError('Invalid measurement units.');
  return {status:dat_tel.status,collected_at:dat_tel.collected_at,received_at:dat_tel.received_at,
    session:Number.isSafeInteger(dat_tel.session)?dat_tel.session:0,
    sample:dat_pnd,history:dat_hst,events:dat_evn,threshold:val_umb};
}

export function est_pnd(dat_tel, sys_ts=Date.now()/1000, est_frs=true) {
  if (!dat_tel) return 'waiting';
  if (!dat_tel.sample) return ['disconnected','stopped'].includes(dat_tel.status)?'disconnected':'waiting';
  if (!est_frs || dat_tel.status !== 'live' || dat_tel.received_at === null ||
      sys_ts-dat_tel.received_at > 10 || sys_ts-dat_tel.collected_at > 10) return 'stale';
  if (!dat_tel.sample.tracking_valid) return dat_tel.sample.mode === '3d-mm'?'low-fit':'low-light';
  if (dat_tel.sample.wind) {
    if (dat_tel.sample.wind.turbulence) return 'wind';
    return dat_tel.sample.alert ? 'swing' : 'live';
  }
  // The source counter remains separate: the original 3.1.0 source triggers on XY.
  return dat_tel.sample.displacement >= dat_tel.threshold ? 'swing':'live';
}

export function fil_mst(dat_tel,cnt_seg=60) {
  if (!dat_tel?.sample) return [];
  const sys_min=dat_tel.sample.ts-Math.min(120,Math.max(1,cnt_seg));
  return dat_tel.history.filter(dat_itm => dat_itm.ts >= sys_min);
}

export function pry_sup(dat_pnd,fac_esc=1,pos_cx=170,pos_cz=125) {
  // Use physical XZ offsets only; positive Z points away from the camera, upward.
  if (!dat_pnd || dat_pnd.mode !== '3d-mm' || !dat_pnd.tracking_valid ||
      !Number.isFinite(dat_pnd.dx) || !Number.isFinite(dat_pnd.dz)) return null;
  if (!Number.isFinite(fac_esc) || fac_esc <= 0 ||
      !Number.isFinite(pos_cx) || !Number.isFinite(pos_cz)) throw new TypeError('Invalid top-view scale.');
  return {x:pos_cx+dat_pnd.dx*fac_esc,y:pos_cz-dat_pnd.dz*fac_esc};
}

export function exp_csv(dat_hst) {
  const dat_val=dat_hst.map(val_mst).filter(Boolean);
  if (!dat_val.length) return '';
  const txt_mod=dat_val[0].mode;
  if (dat_val.some(dat_itm => dat_itm.mode !== txt_mod)) throw new TypeError('Cannot combine pixel and millimeter sessions.');
  const est_3d=txt_mod === '3d-mm';
  const txt_uni=est_3d?'mm':'px';
  const dat_nom=['ts','x','y','r','ax','ay','ar','dx','dy','dz','vx','vy','vz',
    'displacement','fit_pct','luminance','alert','events','tracking_valid','mode',
    'wind.tilt_deg','wind.dissociation','wind.turbulence','wind.factor','wind.threshold_xy_mm','wind.suppression_active'];
  const dat_cab=['source_unix_s','position_x_px','position_y_px','apparent_radius_px',
    'reference_x_px','reference_y_px','reference_radius_px',
    'offset_x_'+txt_uni,'offset_y_'+txt_uni,'offset_z_'+txt_uni,
    'velocity_x_'+txt_uni+'_s','velocity_y_'+txt_uni+'_s','velocity_z_'+txt_uni+'_s',
    'displacement_'+txt_uni,'geometric_fit_pct','brightness_0_255',
    'source_threshold_active','tracker_event_count','tracking_valid','measurement_mode',
    'wind_pan_tilt_deg','wind_dissociation_0_1','source_turbulence_alarm','wind_factor_0_2_5','estimated_xy_threshold_mm','source_wind_suppression'];
  const dat_lin=dat_val.map(dat_pnd => dat_nom.map(clv_nom => {
    const val_res=clv_nom.startsWith('wind.')?dat_pnd.wind?.[clv_nom.slice(5)]??null:dat_pnd[clv_nom];
    return val_res === null?'':typeof val_res === 'boolean'?Number(val_res):val_res;
  }).join(','));
  return [dat_cab.join(','),...dat_lin].join('\r\n')+'\r\n';
}

export function crt_trz(dat_hst,clv_nom,fac_x,fac_y) {
  let txt_val='',dat_ant=null;
  for (const dat_pnd of dat_hst) {
    const est_vnt=clv_nom.startsWith('wind.');
    const val_res=est_vnt?dat_pnd.wind?.[clv_nom.slice(5)]:dat_pnd[clv_nom];
    if ((!est_vnt && !dat_pnd.tracking_valid) || !Number.isFinite(val_res)) {dat_ant=null;continue;}
    const est_nvo=!dat_ant || dat_pnd.ts-dat_ant.ts > 2;
    txt_val+=(est_nvo?'M':'L')+fac_x(dat_pnd.ts).toFixed(2)+','+fac_y(val_res).toFixed(2)+' ';
    dat_ant=dat_pnd;
  }
  return txt_val.trim();
}
