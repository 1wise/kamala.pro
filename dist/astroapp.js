// Timestamp: 2026-11-02
// Version: 2.1.1
// Author and Credits: https://www.alawise.es/1-s
import {fmt_ast, fmt_geo, run_ast, dat_car} from './astroapp-core.mjs?v=2.0.3';
import {obs_img} from './astroapp-image.mjs?v=2.1.1';

for (const dmn_itm of document.querySelectorAll('[data-astroapp]')) {
  const frm_ast = dmn_itm.querySelector('form');
  const btn_env = dmn_itm.querySelector('[data-astroapp-calculate]');
  const btn_geo = dmn_itm.querySelector('[data-astroapp-location]');
  const txt_rsp = dmn_itm.querySelector('[data-astroapp-status]');
  const dat_dst = dmn_itm.querySelector('[data-astroapp-result]');
  const txt_met = dmn_itm.querySelector('[data-astroapp-reference]');
  const btn_img = dmn_itm.querySelector('[data-astroapp-retry-image]');
  const lnk_img = dmn_itm.querySelector('[data-astroapp-open-image]');
  const est_ast = {job:0, busy:false, timer:null,images:null};
  const dat_opt = Object.fromEntries(Object.keys(dat_car.western.defaults).map(clv_esc => [clv_esc,[...frm_ast.elements.namedItem(clv_esc).options].map(dat_itm => dat_itm.cloneNode(true))]));
  const act_ast = txt_val => {txt_rsp.textContent = txt_val;};
  const clr_ast = () => {
    est_ast.job++;
    est_ast.images?.stop();est_ast.images=null;
    btn_img.hidden=true;lnk_img.hidden=true;lnk_img.removeAttribute('href');
    clearTimeout(est_ast.timer);
    est_ast.busy = false;
    btn_env.disabled = false;
    frm_ast.elements.namedItem('chart').disabled = false;
    document.getElementById('astroappDiv').replaceChildren();
    dmn_itm.querySelector('[data-astroapp-xml]').textContent = '';
    dat_dst.hidden = true;
    txt_met.textContent = '';
  };
  const fin_ast = (idx_job,txt_val='Chart image loaded. Review the calculation settings and any provider messages.') => {
    if (idx_job !== est_ast.job || !est_ast.busy) return;
    clearTimeout(est_ast.timer);
    est_ast.busy = false;
    btn_env.disabled = false;
    frm_ast.elements.namedItem('chart').disabled = false;
    act_ast(txt_val);
  };
  const act_car = () => {
    const cfg_ast = dat_car[frm_ast.elements.namedItem('chart').value];
    for (const [clv_esc,txt_val] of Object.entries(cfg_ast.defaults)) {
      const dmn_det = frm_ast.elements.namedItem(clv_esc);
      dmn_det.replaceChildren(...dat_opt[clv_esc].filter(dat_itm => !cfg_ast[clv_esc] || cfg_ast[clv_esc].includes(dat_itm.value)).map(dat_itm => dat_itm.cloneNode(true)));
      dmn_det.value = txt_val;
    }
    dmn_itm.querySelector('[data-astroapp-varga]').hidden = !cfg_ast.divisional;
    frm_ast.elements.namedItem('varga').disabled = !cfg_ast.divisional;
    frm_ast.elements.namedItem('consent').checked = false;
    dmn_itm.querySelector('[data-astroapp-method-note]').textContent = cfg_ast.note;
  };
  frm_ast.elements.namedItem('chart').addEventListener('change', () => {
    if (est_ast.busy) return;
    clr_ast();act_car();act_ast('Chart method updated. Review its calculation conventions before submitting.');
  });
  for (const dmn_det of document.querySelectorAll('[data-chart-choice]')) dmn_det.addEventListener('click', evt_ui => {
    if (est_ast.busy) {evt_ui.preventDefault();act_ast('Wait for the current chart request before changing its method.');return;}
    if (!Object.hasOwn(dat_car,dmn_det.dataset.chartChoice)) return;
    frm_ast.elements.namedItem('chart').value = dmn_det.dataset.chartChoice;
    clr_ast();act_car();act_ast('Chart method selected. Enter time and place before calculating.');
  });
  function obs_ast(idx_job) {
    est_ast.images=obs_img(document.getElementById('astroappDiv'),(txt_est,dat_env)=>{
      if(idx_job!==est_ast.job)return;
      if(dat_env.url&&new URL(dat_env.url,location.href).protocol==='https:') {lnk_img.href=dat_env.url;lnk_img.hidden=false;}
      if(txt_est==='loaded') {btn_img.hidden=true;fin_ast(idx_job);act_ast('Chart image loaded. Review the calculation settings and any provider messages.');}
      else if(txt_est==='loading') {btn_img.hidden=true;act_ast('Calculation received. Loading the chart image…');}
      else {
        btn_img.hidden=false;
        fin_ast(idx_job,'The calculation returned, but its image did not load. Retry the image below or open it in a new tab.');
        act_ast('The calculation returned, but its image did not load. Retry the image below or open it in a new tab.');
      }
    });
  }
  btn_img.addEventListener('click',()=>{btn_img.hidden=true;est_ast.images?.retry();});
  dmn_itm.querySelector('[data-astroapp-now]').addEventListener('click', () => {
    const txt_val = new Date().toISOString();
    frm_ast.elements.namedItem('date').value = txt_val.slice(0,10);
    frm_ast.elements.namedItem('time').value = txt_val.slice(11,19);
    frm_ast.elements.namedItem('timezone').value = '+00:00';
    frm_ast.elements.namedItem('consent').checked = false;
  });
  btn_geo.addEventListener('click', () => {
    if (!navigator.geolocation) {act_ast('Location access is unavailable. Enter coordinates manually.');return;}
    btn_geo.disabled = true;
    act_ast('Requesting the current location from this browser…');
    navigator.geolocation.getCurrentPosition(dat_ast => {
      try {
        frm_ast.elements.namedItem('latitude').value = fmt_geo(dat_ast.coords.latitude,'latitude');
        frm_ast.elements.namedItem('longitude').value = fmt_geo(dat_ast.coords.longitude,'longitude');
        frm_ast.elements.namedItem('consent').checked = false;
        act_ast('Current coordinates filled. For a birth chart, check that they match the birthplace.');
      } catch(err_env) {act_ast(err_env.message);}
      finally {btn_geo.disabled = false;}
    }, () => {btn_geo.disabled = false;act_ast('The current location could not be obtained. Enter coordinates manually.');}, {enableHighAccuracy:false,maximumAge:60000,timeout:10000});
  });
  dmn_itm.querySelector('[data-astroapp-clear]').addEventListener('click', () => {
    if (est_ast.busy) {act_ast('Wait for the current request before clearing.');return;}
    frm_ast.reset();clr_ast();act_car();act_ast('Chart and form cleared.');
  });
  frm_ast.addEventListener('submit', async evt_ui => {
    evt_ui.preventDefault();
    if (est_ast.busy || !frm_ast.reportValidity()) return;
    let dat_ast;
    try {dat_ast = fmt_ast(Object.fromEntries(new FormData(frm_ast)));}
    catch(err_env) {act_ast(err_env.message);return;}
    clr_ast();est_ast.busy = true;btn_env.disabled = true;frm_ast.elements.namedItem('chart').disabled = true;
    const idx_job = est_ast.job;
    obs_ast(idx_job);
    act_ast('Loading the AstroApp connection…');
    if (!(await window.kamalaAstroReady)) {
      fin_ast(idx_job);act_ast('AstroApp did not initialize. Check the JavaScript access code and authorized site URL in AstroApp, then reload this page.');return;
    }
    if (idx_job !== est_ast.job) return;
    dat_dst.hidden = false;
    txt_met.textContent = dat_car[dat_ast.chart].label + ' · ' + dat_ast.date.replaceAll('/','-') + ' · ' + dat_ast.time + ' · UTC' + dat_ast.timezone + ' · ' + dat_ast.latitude + ' / ' + dat_ast.longitude + ' · ' + dat_ast.style + ' · ' + dat_ast.zodiac + ' · ' + dat_ast.house + ' · ' + dat_ast.coordinates + (dat_ast.varga ? ' · D' + dat_ast.varga : '');
    try {
      act_ast('Calculating the selected chart with AstroApp…');
      // The provider has no documented cancellation API. Keep a timed-out job
      // blocked until its response arrives or this document is reloaded.
      est_ast.timer = setTimeout(() => {if (idx_job === est_ast.job) act_ast('AstroApp has not returned a result. Wait for its response or reload this page before retrying.');},30000);
      run_ast(window,dat_ast,dat_env => {
        if (idx_job !== est_ast.job) return;
        const txt_val = ['objectsXML','aspectsXML'].filter(clv_esc => dat_env?.[clv_esc]).map(clv_esc => clv_esc + '\n' + (typeof dat_env[clv_esc] === 'string' ? dat_env[clv_esc] : new XMLSerializer().serializeToString(dat_env[clv_esc]))).join('\n\n');
        dmn_itm.querySelector('[data-astroapp-xml]').textContent = txt_val.slice(0,500000);
        clearTimeout(est_ast.timer);
        if(!est_ast.images.refresh()) fin_ast(idx_job,'AstroApp returned a response without a chart image. Review its message below.');
      });
    } catch(err_env) {fin_ast(idx_job);act_ast(err_env.message);}
  });
  window.addEventListener('pagehide', () => {frm_ast.reset();clr_ast();act_car();});
  act_car();
  btn_env.disabled = false;
}
