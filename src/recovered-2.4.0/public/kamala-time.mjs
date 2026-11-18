// Timestamp: 2026-11-09
// Version: 1.0.1
// Author & Credits: https://www.alawise.es/1-s
const dat_srv = Object.freeze({
  time: {
    url: 'https://time.1-s.es/',
    name: 'time.1-s.es',
    location: 'Bebe',
    title: 'time.1-s.es · Bebe clock, NTP diagnostics and PanIpSys'
  },
  time1: {
    url: 'https://time1.1-s.es/',
    name: 'time1.1-s.es',
    location: 'Excalibur',
    title: 'time1.1-s.es · Excalibur clock, NTP diagnostics and PanIpSys'
  }
});

for (const dmn_app of document.querySelectorAll('[data-time-app]')) {
  const dat_tab = [...dmn_app.querySelectorAll('[data-time-tab]')];
  const dmn_pag = dmn_app.querySelector('[data-time-frame]');
  const dmn_abr = dmn_app.querySelector('[data-time-open]');
  const dmn_est = dmn_app.querySelector('[data-time-current]');
  const dmn_pan = dmn_app.querySelector('[role="tabpanel"]');
  if (!dat_tab.length || !dmn_pag || !dmn_abr || !dmn_est || !dmn_pan) continue;

  const act_tab = (clv_srv, est_foc = false) => {
    const dat_act = Object.hasOwn(dat_srv, clv_srv) ? dat_srv[clv_srv] : null;
    const btn_act = dat_tab.find(btn_itm => btn_itm.dataset.timeTab === clv_srv);
    if (!dat_act || !btn_act) return;
    for (const btn_itm of dat_tab) {
      const est_act = btn_itm === btn_act;
      btn_itm.setAttribute('aria-selected', String(est_act));
      btn_itm.tabIndex = est_act ? 0 : -1;
    }
    dmn_pan.setAttribute('aria-labelledby', btn_act.id);
    dmn_pag.title = dat_act.title;
    // Reuse one frame so inactive clocks do not keep rendering or polling.
    if (dmn_pag.getAttribute('src') !== dat_act.url) dmn_pag.src = dat_act.url;
    dmn_abr.href = dat_act.url;
    dmn_abr.textContent = 'Open ' + dat_act.name + ' ↗';
    dmn_est.textContent = dat_act.name + ' · ' + dat_act.location;
    if (est_foc) btn_act.focus();
  };

  const act_elige = (btn_act, est_foc = false) => {
    act_tab(btn_act.dataset.timeTab, est_foc);
    history.replaceState(null, '', '#' + btn_act.dataset.timeTab);
  };

  for (const [idx_tab, btn_tab] of dat_tab.entries()) {
    btn_tab.addEventListener('click', () => act_elige(btn_tab));
    btn_tab.addEventListener('keydown', evt_ui => {
      let idx_nvo;
      if (evt_ui.key === 'ArrowRight') idx_nvo = (idx_tab + 1) % dat_tab.length;
      else if (evt_ui.key === 'ArrowLeft') idx_nvo = (idx_tab - 1 + dat_tab.length) % dat_tab.length;
      else if (evt_ui.key === 'Home') idx_nvo = 0;
      else if (evt_ui.key === 'End') idx_nvo = dat_tab.length - 1;
      else return;
      evt_ui.preventDefault();
      act_elige(dat_tab[idx_nvo], true);
    });
  }
  const act_url = () => act_tab(location.hash === '#time1' ? 'time1' : 'time');
  window.addEventListener('hashchange', act_url);
  act_url();
}
