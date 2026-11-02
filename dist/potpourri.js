// Timestamp: 2026-10-30
// Version: 2.0.0
// Author and Credits: https://www.alawise.es/1-s
const dmn_itm = document.querySelector('[data-potpourri]');
if (dmn_itm) {
  const frm_ctc = dmn_itm.querySelector('form');
  const btn_env = frm_ctc.querySelector('button[type=submit]');
  const txt_rsp = frm_ctc.querySelector('[data-pot-status]');
  const dat_adj = [];
  let est_env = false;
  let dat_tec = {};
  const act_tec = () => {
    const dat_itm = dat_tec[frm_ctc.elements.namedItem('art').value];
    const dmn_vis = dmn_itm.querySelector('[data-photo-tips]');
    dmn_vis.replaceChildren();
    for (const txt_val of dat_itm?.photo || ['Include a full view and one clear detail.', 'Describe the preparation and the order of any sequence.']) {
      const dmn_det = document.createElement('li');dmn_det.textContent = txt_val;dmn_vis.append(dmn_det);
    }
  };
  const clr_fot = () => {
    for (const url_app of dat_adj) URL.revokeObjectURL(url_app);
    dat_adj.length = 0;
    frm_ctc.querySelector('[data-pot-previews]').replaceChildren();
  };
  frm_ctc.elements.namedItem('art').addEventListener('change',act_tec);
  frm_ctc.querySelector('[data-pot-files]').addEventListener('change',evt_ui => {
    clr_fot();
    const dat_itm = [...evt_ui.target.files];
    if (dat_itm.length > 3 || dat_itm.some(dat_env => dat_env.size > 5*1024*1024 || !['image/jpeg','image/png','image/webp'].includes(dat_env.type)) || dat_itm.reduce((cnt_tot,dat_env)=>cnt_tot+dat_env.size,0)>12*1024*1024) {
      evt_ui.target.value='';txt_rsp.textContent='Choose up to 3 JPEG, PNG or WebP photos: 5 MB each and 12 MB total.';return;
    }
    for (const dat_env of dat_itm) {
      const url_app = URL.createObjectURL(dat_env);dat_adj.push(url_app);
      const dmn_vis = document.createElement('img');dmn_vis.src=url_app;dmn_vis.alt=dat_env.name;frm_ctc.querySelector('[data-pot-previews]').append(dmn_vis);
    }
    txt_rsp.textContent=dat_itm.length+' photo(s) selected locally. Nothing has been uploaded.';
  });
  (async () => {
    try {
      const rsp_env = await fetch('/potpourri/topics.json',{cache:'no-cache'});
      dat_tec = await rsp_env.json();
      const api_qry = new URLSearchParams(location.search);
      if (Object.hasOwn(dat_tec,api_qry.get('art'))) frm_ctc.elements.namedItem('art').value=api_qry.get('art');
      act_tec();
      const rsp_ctc = await fetch('/potpourri/send.php',{cache:'no-store',credentials:'same-origin',headers:{Accept:'application/json'}});
      if (!rsp_ctc.ok || !rsp_ctc.headers.get('content-type')?.includes('application/json')) throw new Error();
      const dat_ctc = await rsp_ctc.json();
      if (!/^[a-f0-9]{64}$/.test(dat_ctc.csrf || '') || dat_ctc.ready !== true) throw new Error();
      frm_ctc.elements.namedItem('csrf').value=dat_ctc.csrf;
      btn_env.disabled=false;
      txt_rsp.textContent='Ready. Photos are sent only when Send is pressed.';
    } catch {
      txt_rsp.textContent='Photo submissions are temporarily unavailable here. ';
      const dmn_vis=document.createElement('a');
      dmn_vis.href=['kamala.pro','www.kamala.pro'].includes(location.hostname)?'/contact/':'https://kamala.pro/potpourri/';
      dmn_vis.textContent=['kamala.pro','www.kamala.pro'].includes(location.hostname)?'Contact Kamala ↗':'Open Potpourri at kamala.pro ↗';
      txt_rsp.append(dmn_vis);
    }
  })();
  frm_ctc.addEventListener('submit',async evt_ui => {
    evt_ui.preventDefault();
    if (est_env || btn_env.disabled || !frm_ctc.reportValidity()) return;
    est_env=true;btn_env.disabled=true;txt_rsp.textContent='Sending photos privately…';
    try {
      const rsp_env = await fetch('/potpourri/send.php',{method:'POST',body:new FormData(frm_ctc),credentials:'same-origin',headers:{Accept:'application/json'},signal:AbortSignal.timeout(45000)});
      const dat_env = await rsp_env.json();
      if (!rsp_env.ok || dat_env.ok !== true) throw new Error(dat_env.message || 'The submission could not be completed.');
      frm_ctc.reset();clr_fot();act_tec();txt_rsp.textContent=dat_env.message;
      // A completed submission consumes its token; reload before sending another.
    } catch(err_env) {txt_rsp.textContent=err_env.name==='TimeoutError'?'The response timed out. Check for a reply before sending again.':err_env.message;btn_env.disabled=false;}
    finally {est_env=false;}
  });
  window.addEventListener('pagehide',clr_fot);
}
