/* Timestamp: 2026-10-28 | Version: 1.3.1 | Author and Credits: https://www.alawise.es/1-s */
'use strict';

// Each menu owns its disclosure so the duplicate navigation has independent controls.
for (const btn_mnu of document.querySelectorAll('.menu-toggle')) {
  const dmn_nav = document.getElementById(btn_mnu.getAttribute('aria-controls'));
  btn_mnu.addEventListener('click', () => {
    const est_mnu = btn_mnu.getAttribute('aria-expanded') !== 'true';
    btn_mnu.setAttribute('aria-expanded', String(est_mnu));
    dmn_nav.classList.toggle('is-open', est_mnu);
  });
}
document.addEventListener('keydown', (evt_ui) => {
  if (evt_ui.key !== 'Escape') return;
  for (const dmn_det of document.querySelectorAll('details[open]')) dmn_det.open = false;
  for (const btn_mnu of document.querySelectorAll('.menu-toggle')) {
    if (btn_mnu.getAttribute('aria-expanded') === 'true') {
      btn_mnu.setAttribute('aria-expanded', 'false');
      document.getElementById(btn_mnu.getAttribute('aria-controls')).classList.remove('is-open');
      btn_mnu.focus();
    }
  }
});

for (const btn_flt of document.querySelectorAll('[data-filter]')) {
  btn_flt.addEventListener('click', () => {
    for (const btn_itm of document.querySelectorAll('[data-filter]')) {
      btn_itm.classList.toggle('active', btn_itm === btn_flt);
      btn_itm.setAttribute('aria-pressed', String(btn_itm === btn_flt));
    }
    for (const dmn_itm of document.querySelectorAll('.card[data-cat]')) {
      dmn_itm.hidden = btn_flt.dataset.filter !== 'all' && dmn_itm.dataset.cat !== btn_flt.dataset.filter;
    }
  });
}

let cnt_car = 0;
let cnt_crz = 0;
const act_cnt = () => {
  const cnt_tot = cnt_car + cnt_crz;
  document.querySelector('#results').textContent = `${cnt_tot} ${cnt_tot === 1 ? 'toss' : 'tosses'} · ${cnt_car} heads · ${cnt_crz} tails`;
};
document.querySelector('#toss')?.addEventListener('click', () => {
  // A single random bit avoids modulo bias without implying physical measurement.
  const rnd_bit = crypto.getRandomValues(new Uint8Array(1))[0] & 1;
  if (rnd_bit) cnt_car++; else cnt_crz++;
  document.querySelector('#coin').textContent = rnd_bit ? 'H' : 'T';
  document.querySelector('#coin').setAttribute('aria-label', rnd_bit ? 'Heads' : 'Tails');
  act_cnt();
});
document.querySelector('#reset')?.addEventListener('click', () => {
  cnt_car = 0;
  cnt_crz = 0;
  document.querySelector('#coin').textContent = '?';
  document.querySelector('#coin').setAttribute('aria-label', 'No toss yet');
  act_cnt();
});

const frm_ctc = document.querySelector('#contact-form');
if (frm_ctc) {
  const btn_env = frm_ctc.querySelector('[type="submit"]');
  const msj_rsp = document.querySelector('#form-status');
  // Prime the session while the visitor fills out the form.
  let tok_ctc = fetch('/contact/send.php', { credentials: 'same-origin', cache: 'no-store' })
    .then((rsp_env) => { if (!rsp_env.ok) throw new Error('Unavailable'); return rsp_env.json(); })
    .then((dat_ctc) => dat_ctc.csrf).catch(() => null);
  frm_ctc.addEventListener('submit', async (evt_frm) => {
    evt_frm.preventDefault();
    btn_env.disabled = true;
    msj_rsp.textContent = 'Sending…';
    try {
      tok_ctc = await tok_ctc;
      if (!tok_ctc) {
        const rsp_env = await fetch('/contact/send.php', { credentials: 'same-origin', cache: 'no-store' });
        if (!rsp_env.ok) throw new Error('Unavailable');
        tok_ctc = (await rsp_env.json()).csrf;
      }
      if (typeof tok_ctc !== 'string' || !tok_ctc) throw new Error('Unavailable');
      const dat_ctc = new FormData(frm_ctc);
      dat_ctc.set('csrf', tok_ctc);
      const rsp_env = await fetch('/contact/send.php', { method: 'POST', credentials: 'same-origin', body: dat_ctc });
      const dat_env = await rsp_env.json();
      msj_rsp.textContent = dat_env.message || 'Email could not be submitted. Please try again later.';
      if (rsp_env.ok && dat_env.ok) { frm_ctc.reset(); tok_ctc = null; }
      if (rsp_env.status === 403) tok_ctc = null;
    } catch {
      msj_rsp.textContent = 'Email could not be submitted. Please try again later.';
      tok_ctc = null;
    } finally {
      btn_env.disabled = false;
    }
  });
}
for (const btn_app of document.querySelectorAll('[data-app-src]')) {
  btn_app.addEventListener('click', () => {
    if (btn_app.getAttribute('aria-pressed') === 'true') return;
    for (const btn_itm of document.querySelectorAll('[data-app-src]')) {
      btn_itm.classList.toggle('active', btn_itm === btn_app);
      btn_itm.setAttribute('aria-pressed', String(btn_itm === btn_app));
    }
    // Keep both legacy tools on their original origin so their forms and assets work.
    document.querySelector('#original-app').src = btn_app.dataset.appSrc;
    document.querySelector('#original-app').title = `Biorhythms: ${btn_app.textContent}`;
    document.querySelector('#open-app').href = btn_app.dataset.appSrc;
  });
}
