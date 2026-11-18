// Timestamp: 2026-10-31
// Version: 2.0.5
// Author & Credits: https://www.alawise.es/1-s
import sys_qr from 'qrcode';
import { crt_clv, exp_clv, exp_pub, fmt_sec, enc_b32, crt_otp, url_otp } from './keys-core.mjs';
import { crt_azr, rnd_oct } from '../entropy-core.mjs';

// This workspace deliberately does not load the site's general application script.
for (const btn_mnu of document.querySelectorAll('.menu-toggle')) {
  btn_mnu.addEventListener('click', () => {
    const est_mnu = btn_mnu.getAttribute('aria-expanded') !== 'true';
    btn_mnu.setAttribute('aria-expanded', String(est_mnu));
    document.getElementById(btn_mnu.getAttribute('aria-controls')).classList.toggle('is-open', est_mnu);
  });
}
document.addEventListener('keydown', evt_ui => {
  if (evt_ui.key !== 'Escape') return;
  for (const dmn_det of document.querySelectorAll('details[open]')) dmn_det.open = false;
  for (const btn_mnu of document.querySelectorAll('.menu-toggle')) {
    btn_mnu.setAttribute('aria-expanded','false');
    document.getElementById(btn_mnu.getAttribute('aria-controls')).classList.remove('is-open');
  }
});
const frm_lab = document.querySelector('[data-keys-lab]');
const dat_lab = { clv:null, sec:null, otp:null, qr:{}, fmt:'hex' };
let idx_job = 0, int_est = null;
const act_lab = (txt_val, est_env) => {
  if (txt_val !== null) frm_lab.querySelector('[data-lab-status]').textContent = txt_val;
  if (typeof est_env === 'boolean') {
    for (const btn_itm of frm_lab.querySelectorAll('[data-generate-key],[data-generate-secret],[data-generate-otp],[data-generate-seed-art],[data-download-private],[data-lab-source],[data-camera-required],[data-secret-format],[data-secret-bytes]')) btn_itm.disabled = est_env;
    frm_lab.setAttribute('aria-busy',String(est_env));
    if (!est_env) {
      frm_lab.querySelector('[data-camera-required]').disabled = frm_lab.querySelector('[data-lab-source]').value === 'browser';
      frm_lab.querySelector('[data-secret-bytes]').disabled = frm_lab.querySelector('[data-secret-format]').value === 'uuid';
    }
  }
};
async function obt_azr(sys_idx = idx_job) {
  frm_lab.querySelector('[data-source-status]').textContent = 'Requesting a fresh shared-source sample…';
  const clv_cam = frm_lab.querySelector('[data-lab-source]').value;
  const est_dom = ['kamala.pro','www.kamala.pro'].includes(location.hostname);
  const url_azr = location.protocol === 'https:' && est_dom ? '/api/entropy.php' : 'https://www.kamala.pro/api/entropy.php';
  const dat_azr = await crt_azr(clv_cam,url_azr);
  if (sys_idx !== idx_job) { dat_azr.seed.fill(0); throw new Error('Generation canceled'); }
  frm_lab.querySelector('[data-source-status]').textContent = dat_azr.label;
  if (clv_cam !== 'browser' && frm_lab.querySelector('[data-camera-required]').checked && dat_azr.sample?.mode !== 'stream+system') {
    dat_azr.seed.fill(0);
    throw new Error('A camera sample is required. Retry after a moment, or explicitly select Browser only for offline use.');
  }
  return dat_azr;
}

function dsc_fil(txt_val, pth_fil, txt_note = 'text/plain;charset=utf-8') {
  const dat_dst = new Blob([txt_val],{type:txt_note});
  const url_app = URL.createObjectURL(dat_dst);
  const dmn_itm = document.createElement('a');
  dmn_itm.href = url_app; dmn_itm.download = fmt_fil(pth_fil);
  document.body.append(dmn_itm); dmn_itm.click(); dmn_itm.remove();
  // Keep the object URL alive until the browser has accepted the download.
  setTimeout(()=>URL.revokeObjectURL(url_app),1000);
}
function fmt_fil(pth_fil) {
  const txt_pre = frm_lab.querySelector('[data-file-label]').value.trim().replace(/[^A-Za-z0-9_-]/g,'').slice(0,32);
  return txt_pre ? txt_pre + '-' + pth_fil : pth_fil;
}
async function crt_qr(tip_clv, txt_qr) {
  const sys_idx = idx_job;
  const dmn_itm = frm_lab.querySelector('[data-qr="'+tip_clv+'"]');
  await sys_qr.toCanvas(dmn_itm,txt_qr,{errorCorrectionLevel:'M',margin:4,scale:5,color:{dark:'#000000',light:'#ffffff'}});
  if (sys_idx === idx_job) dat_lab.qr[tip_clv] = txt_qr;
}
function fmt_art(dat_sem) {
  const txt_sim = ' .:-=+*#';
  const arr_lns = [];
  const cnt_wid = 32;
  const cnt_hgt = 16;
  for (let cnt_fil = 0; cnt_fil < cnt_hgt; cnt_fil++) {
    let txt_lin = '';
    for (let cnt_col = 0; cnt_col < cnt_wid; cnt_col++) {
      txt_lin += txt_sim[dat_sem[cnt_fil * cnt_wid + cnt_col] & 7];
    }
    arr_lns.push(txt_lin);
  }
  const txt_brd = '+' + '-'.repeat(cnt_wid) + '+';
  return ['KAMALA / RANDOM SEED ART','Independent sample; the raw seed is not shown.',txt_brd,...arr_lns.map(txt_lin => '|' + txt_lin + '|'),txt_brd].join('\n') + '\n';
}

function clr_lab() {
  idx_job++;
  if (dat_lab.clv) dat_lab.clv.azr.seed.fill(0);
  dat_lab.clv = null;
  if (dat_lab.sec) dat_lab.sec.fill(0);
  if (dat_lab.otp) dat_lab.otp.sec.fill(0);
  dat_lab.sec = null; dat_lab.otp = null; dat_lab.qr = {};
  clearInterval(int_est); int_est = null;
  for (const dmn_itm of frm_lab.querySelectorAll('[data-fingerprint],[data-key-label],[data-otp-time],[data-ssh-help]')) dmn_itm.textContent = '';
  frm_lab.querySelector('[data-seed-art]').textContent = '';
  frm_lab.querySelector('[data-otp-code]').textContent = '------';
  frm_lab.querySelector('[data-otp-account]').value = '';
  for (const dmn_itm of frm_lab.querySelectorAll('textarea,[data-passphrase]')) dmn_itm.value = '';
  for (const dmn_itm of frm_lab.querySelectorAll('canvas')) { dmn_itm.width = 1; dmn_itm.height = 1; }
  for (const dmn_itm of frm_lab.querySelectorAll('[data-key-result],[data-secret-result],[data-secret-qr-box],[data-otp-result],[data-seed-art-result]')) dmn_itm.hidden = true;
  for (const btn_itm of frm_lab.querySelectorAll('button')) btn_itm.disabled = false;
  for (const dmn_itm of frm_lab.querySelectorAll('[data-key-source],[data-secret-source],[data-otp-source],[data-seed-art-source]')) dmn_itm.textContent = '';
  frm_lab.querySelector('[data-source-status]').textContent = 'Ready. A fresh sample is requested for each generation.';
  act_lab('Session cleared. Downloads and clipboard contents are controlled separately by the browser.',false);
}

if (!window.isSecureContext || !crypto.subtle) {
  frm_lab.querySelector('[data-unsupported]').hidden = false;
  for (const btn_itm of frm_lab.querySelectorAll('button')) btn_itm.disabled = true;
  act_lab('Open this workspace over HTTPS or use the downloaded offline HTML in a supported browser.');
} else {
  const api_qry = new URLSearchParams(location.search);
  if (location.search.length > 1) {
    const api_ver = api_qry.get('api_ver') || '1';
    const api_act = api_qry.get('api_act') || 'configure';
    const vw_mod = api_qry.get('vw_mod');
    let txt_get = '';
    if (api_ver !== '1' || api_act !== 'configure' || (vw_mod && vw_mod !== 'entropy')) {
      txt_get = 'URL settings were ignored. Use API v1, api_act=configure and vw_mod=entropy.';
    } else {
      const src_cam = api_qry.get('src_cam');
      const key_typ = api_qry.get('key_typ');
      const out_fmt = api_qry.get('out_fmt');
      const cnt_itm = api_qry.get('cnt_itm');
      const fil_id = api_qry.get('fil_id') || '';
      if (['auto','cam1','cam2','cam3','cam4','browser'].includes(src_cam)) frm_lab.querySelector('[data-lab-source]').value = src_cam;
      if (['ed25519','rsa3072','rsa4096'].includes(key_typ)) frm_lab.querySelector('[data-key-type]').value = key_typ;
      for (const clv_sel of ['[data-public-format]','[data-private-format]','[data-secret-format]']) {
        const dmn_sel = frm_lab.querySelector(clv_sel);
        if ([...dmn_sel.options].some(dmn_opt => dmn_opt.value === out_fmt)) dmn_sel.value = out_fmt;
      }
      if (['16','32','64','128'].includes(cnt_itm)) frm_lab.querySelector('[data-secret-bytes]').value = cnt_itm;
      if (/^[A-Za-z0-9_-]{1,32}$/.test(fil_id)) frm_lab.querySelector('[data-file-label]').value = fil_id;
      frm_lab.querySelector('[data-camera-required]').disabled = frm_lab.querySelector('[data-lab-source]').value === 'browser';
      txt_get = 'URL settings are prefilled. Review them and press a Generate button when ready; nothing has been generated.';
    }
    if (txt_get) act_lab(txt_get);
  }
  frm_lab.querySelector('[data-lab-source]').addEventListener('change',()=>{
    frm_lab.querySelector('[data-camera-required]').disabled = frm_lab.querySelector('[data-lab-source]').value === 'browser';
    frm_lab.querySelector('[data-source-status]').textContent = 'Source selection applies to the next generation. Existing outputs keep their original source label.';
  });
  frm_lab.querySelector('[data-generate-key]').addEventListener('click', async evt_ui => {
    const sys_idx = ++idx_job;
    const tip_clv = frm_lab.querySelector('[data-key-type]').value;
    const txt_cmt = frm_lab.querySelector('[data-key-comment]').value;
    evt_ui.currentTarget.disabled = true;
    if (dat_lab.clv) dat_lab.clv.azr.seed.fill(0);
    dat_lab.clv = null; delete dat_lab.qr.key;
    frm_lab.querySelector('[data-key-result]').hidden = true;
    act_lab('Sampling and generating a local key pair… RSA can take up to two minutes.',true);
    let dat_azr;
    try {
      dat_azr = await obt_azr();
      if (sys_idx !== idx_job) { dat_azr.seed.fill(0); return; }
      const dat_clv = await crt_clv(tip_clv,txt_cmt,dat_azr,{active:()=>sys_idx === idx_job});
      if (sys_idx !== idx_job) { dat_azr.seed.fill(0); return; }
      dat_lab.clv = dat_clv;
      frm_lab.querySelector('[data-key-label]').textContent = 'CURRENT KEY / ' + dat_clv.tip.toUpperCase();
      frm_lab.querySelector('[data-fingerprint]').textContent = dat_clv.fp;
      frm_lab.querySelector('[data-key-source]').textContent = dat_azr.label;
      frm_lab.querySelector('[data-key-result]').hidden = false;
      await exp_pub_ui();
      act_lab('Key pair ready. Download the private file and its matching public key.');
    } catch (err_env) {
      if (dat_azr && !dat_lab.clv) dat_azr.seed.fill(0);
      if (sys_idx === idx_job) act_lab(err_env.message.includes('camera sample') ? err_env.message : 'Key generation failed or timed out. Try Ed25519 in a current browser. No key was exported.');
    } finally { if (sys_idx === idx_job) act_lab(null,false); }
  });
  async function exp_pub_ui() {
    const dat_clv = dat_lab.clv;
    if (!dat_clv) return;
    const txt_pub = await exp_pub(dat_clv,frm_lab.querySelector('[data-public-format]').value);
    if (dat_clv !== dat_lab.clv) return;
    frm_lab.querySelector('[data-public-output]').value = txt_pub;
    await crt_qr('key',txt_pub.trimEnd());
    const pth_fil = (dat_clv.tip === 'ed25519' ? 'id_ed25519_' : 'id_rsa_') + dat_clv.fp.slice(7,15).replace(/[^a-zA-Z0-9_-]/g,'_');
    frm_lab.querySelector('[data-ssh-help]').textContent = 'mkdir -p ~/.ssh\nchmod 700 ~/.ssh\nchmod 600 ~/Downloads/' + pth_fil + '\ninstall -m 600 ~/Downloads/' + pth_fil + ' ~/.ssh/' + pth_fil + '\ninstall -m 644 ~/Downloads/' + pth_fil + '.pub ~/.ssh/' + pth_fil + '.pub\nssh-keygen -lf ~/.ssh/' + pth_fil + '.pub\nssh-copy-id -i ~/.ssh/' + pth_fil + '.pub USER@HOST\nssh -i ~/.ssh/' + pth_fil + ' USER@HOST';
  }
  frm_lab.querySelector('[data-public-format]').addEventListener('change',()=>exp_pub_ui().catch(()=>act_lab('Public export or QR failed. Try generating the key again.')));
  frm_lab.querySelector('[data-download-public]').addEventListener('click',async()=>{
    const dat_clv = dat_lab.clv; if (!dat_clv) return;
    const fmt_clv = frm_lab.querySelector('[data-public-format]').value;
    const txt_pub = await exp_pub(dat_clv,fmt_clv);
    if (dat_clv !== dat_lab.clv) return;
    const pth_fil = (dat_clv.tip === 'ed25519' ? 'id_ed25519_' : 'id_rsa_') + dat_clv.fp.slice(7,15).replace(/[^a-zA-Z0-9_-]/g,'_');
    dsc_fil(txt_pub,pth_fil+(fmt_clv === 'ssh' ? '.pub' : fmt_clv === 'pem' ? '.public.pem' : '.public.json'));
  });
  frm_lab.querySelector('[data-protect]').addEventListener('change',evt_ui=>{
    frm_lab.querySelector('[data-passphrase-label]').hidden = !evt_ui.target.checked;
    frm_lab.querySelector('[data-passphrase]').value = '';
    frm_lab.querySelector('[data-private-note]').textContent = evt_ui.target.checked ? 'Keep the passphrase separately from the private key.' : 'This export will be unencrypted. Restrict access to the downloaded private file.';
  });
  frm_lab.querySelector('[data-download-private]').addEventListener('click',async evt_ui=>{
    const dat_clv = dat_lab.clv; if (!dat_clv) return;
    const sys_idx = idx_job;
    const txt_pss = frm_lab.querySelector('[data-protect]').checked ? frm_lab.querySelector('[data-passphrase]').value : '';
    if (frm_lab.querySelector('[data-protect]').checked && txt_pss.length < 12) { act_lab('Enter a passphrase of at least 12 characters, or explicitly choose an unencrypted export.'); frm_lab.querySelector('[data-passphrase]').focus(); return; }
    const fmt_clv = frm_lab.querySelector('[data-private-format]').value;
    evt_ui.currentTarget.disabled = true; act_lab('Protecting and preparing the private download…',true);
    // Let the progress message paint before bcrypt's bounded local computation.
    await new Promise(dat_itm=>requestAnimationFrame(()=>setTimeout(dat_itm,0)));
    try {
      const txt_val = await exp_clv(dat_clv,fmt_clv,txt_pss);
      if (sys_idx !== idx_job || dat_clv !== dat_lab.clv) return;
      const pth_fil = (dat_clv.tip === 'ed25519' ? 'id_ed25519_' : 'id_rsa_') + dat_clv.fp.slice(7,15).replace(/[^a-zA-Z0-9_-]/g,'_');
      dsc_fil(txt_val,pth_fil+(fmt_clv === 'pkcs8' ? '.pem' : ''));
      frm_lab.querySelector('[data-passphrase]').value = '';
      act_lab('Private download prepared' + (txt_pss ? ' with passphrase protection.' : ' without encryption.') + ' Keep the matching public key with the same fingerprint.');
    } catch { act_lab('Private export failed. The current key pair is still available; try again.'); }
    finally { if (sys_idx === idx_job) { frm_lab.querySelector('[data-download-private]').disabled = false; act_lab(null,false); } }
  });
  function fmt_sec_ui() {
    const fmt_clv = frm_lab.querySelector('[data-secret-format]').value;
    const est_env = fmt_clv === 'uuid';
    frm_lab.querySelector('[data-secret-bytes]').disabled = est_env;
    if (dat_lab.sec && ((dat_lab.fmt === 'uuid') !== est_env)) {
      dat_lab.sec.fill(0); dat_lab.sec = null; delete dat_lab.qr.secret;
      frm_lab.querySelector('[data-secret-result]').hidden = true;
      frm_lab.querySelector('[data-secret-qr-box]').hidden = true;
      act_lab('Switching to or from UUID needs a new generation.');
    }
    dat_lab.fmt = fmt_clv;
    if (!dat_lab.sec) return;
    frm_lab.querySelector('[data-secret-output]').value = fmt_sec(dat_lab.sec,fmt_clv);
    delete dat_lab.qr.secret; frm_lab.querySelector('[data-secret-qr-box]').hidden = true;
  }
  frm_lab.querySelector('[data-generate-secret]').addEventListener('click',async()=>{
    const sys_idx = ++idx_job;
    if (dat_lab.sec) dat_lab.sec.fill(0);
    dat_lab.sec = null; delete dat_lab.qr.secret;
    frm_lab.querySelector('[data-secret-result]').hidden = true;
    frm_lab.querySelector('[data-secret-qr-box]').hidden = true;
    act_lab('Sampling and generating a new secret…',true);
    try {
      const dat_azr = await obt_azr();
      if (sys_idx !== idx_job) { dat_azr.seed.fill(0); return; }
      const fmt_clv = frm_lab.querySelector('[data-secret-format]').value;
      dat_lab.sec = rnd_oct(dat_azr,fmt_clv === 'uuid' ? 16 : Number(frm_lab.querySelector('[data-secret-bytes]').value));
      dat_azr.seed.fill(0);
      dat_lab.fmt = fmt_clv; fmt_sec_ui();
      frm_lab.querySelector('[data-secret-source]').textContent = dat_azr.label;
      frm_lab.querySelector('[data-secret-result]').hidden = false;
      act_lab('New random value ready. Formatting does not add randomness.');
    } catch (err_env) { if (sys_idx === idx_job) act_lab(err_env.message.includes('camera sample') ? err_env.message : 'Secret generation failed. No new value was created.'); }
    finally { if (sys_idx === idx_job) act_lab(null,false); }
  });
  frm_lab.querySelector('[data-secret-format]').addEventListener('change',fmt_sec_ui);
  fmt_sec_ui();
  frm_lab.querySelector('[data-show-secret-qr]').addEventListener('click',async()=>{
    const dat_sec = dat_lab.sec;
    const txt_val = frm_lab.querySelector('[data-secret-output]').value;
    if (!dat_sec) return;
    await crt_qr('secret',txt_val);
    if (dat_sec !== dat_lab.sec || txt_val !== frm_lab.querySelector('[data-secret-output]').value) return;
    frm_lab.querySelector('[data-secret-qr-box]').hidden = false;
    act_lab('The displayed QR contains this secret. Scanning it transfers the secret to that device.');
  });
  frm_lab.querySelector('[data-download-secret]').addEventListener('click',()=>{if(dat_lab.sec) dsc_fil(frm_lab.querySelector('[data-secret-output]').value+'\n','kamala-secret.'+dat_lab.fmt+'.txt');});
  async function act_otp() {
    const dat_clv = dat_lab.otp; if (!dat_clv) return;
    const txt_val = await crt_otp(dat_clv.sec);
    if (dat_lab.otp !== dat_clv) return;
    frm_lab.querySelector('[data-otp-code]').textContent = txt_val;
    frm_lab.querySelector('[data-otp-time]').textContent = (30 - Math.floor(Date.now()/1000)%30) + ' seconds remaining';
  }
  frm_lab.querySelector('[data-generate-otp]').addEventListener('click',async()=>{
    const txt_cmt = frm_lab.querySelector('[data-otp-issuer]').value;
    const txt_val = frm_lab.querySelector('[data-otp-account]').value;
    if (!txt_cmt.trim() || !txt_val.trim()) { act_lab('Enter an issuer and an account label first.'); return; }
    const sys_idx = ++idx_job;
    if (dat_lab.otp) dat_lab.otp.sec.fill(0);
    dat_lab.otp = null; delete dat_lab.qr.otp;
    clearInterval(int_est); int_est = null;
    frm_lab.querySelector('[data-otp-result]').hidden = true;
    act_lab('Sampling and creating an authenticator setup…',true);
    try {
    const dat_azr = await obt_azr();
    if (sys_idx !== idx_job) { dat_azr.seed.fill(0); return; }
    const dat_sec = rnd_oct(dat_azr,20); dat_azr.seed.fill(0);
    dat_lab.otp = {sec:dat_sec,uri:url_otp(dat_sec,txt_cmt,txt_val)};
    const dat_clv = dat_lab.otp;
    frm_lab.querySelector('[data-otp-secret]').value = enc_b32(dat_sec);
    frm_lab.querySelector('[data-otp-source]').textContent = dat_azr.label;
    await crt_qr('otp',dat_clv.uri);
    if (dat_lab.otp !== dat_clv) return;
    frm_lab.querySelector('[data-otp-result]').hidden = false;
    clearInterval(int_est); int_est = setInterval(()=>act_otp().catch(()=>{}),1000);
    await act_otp(); if (dat_lab.otp !== dat_clv) return; act_lab('New authenticator setup created locally. Configure the target service with the same setup secret.');
    } catch (err_env) { if (sys_idx === idx_job) act_lab(err_env.message.includes('camera sample') ? err_env.message : 'Authenticator setup failed. Try again.'); }
    finally { if (sys_idx === idx_job) act_lab(null,false); }
  });
  frm_lab.querySelector('[data-download-otp]').addEventListener('click',()=>{if(dat_lab.otp) dsc_fil('Base32 secret: '+enc_b32(dat_lab.otp.sec)+'\n'+dat_lab.otp.uri+'\n','kamala-totp-setup.txt');});
  frm_lab.querySelector('[data-generate-seed-art]').addEventListener('click',async evt_ui=>{
    const sys_idx = ++idx_job;
    evt_ui.currentTarget.disabled = true;
    frm_lab.querySelector('[data-seed-art-result]').hidden = true;
    frm_lab.querySelector('[data-seed-art]').textContent = '';
    act_lab('Sampling a fresh source for independent seed artwork…',true);
    let dat_azr, dat_sem;
    try {
      dat_azr = await obt_azr(sys_idx);
      if (sys_idx !== idx_job) { dat_azr.seed.fill(0); return; }
      dat_sem = rnd_oct(dat_azr,512);
      const txt_art = fmt_art(dat_sem);
      const txt_src = dat_azr.label;
      dat_sem.fill(0); dat_sem = null;
      dat_azr.seed.fill(0); dat_azr = null;
      if (sys_idx !== idx_job) return;
      frm_lab.querySelector('[data-seed-art]').textContent = txt_art;
      frm_lab.querySelector('[data-seed-art-source]').textContent = txt_src;
      frm_lab.querySelector('[data-seed-art-result]').hidden = false;
      act_lab('Independent random seed artwork ready. It does not contain an SSH key seed.');
    } catch (err_env) {
      if (dat_sem) dat_sem.fill(0);
      if (dat_azr) dat_azr.seed.fill(0);
      if (sys_idx === idx_job) act_lab(err_env.message.includes('camera sample') ? err_env.message : 'Seed artwork could not be generated. No output was created.');
    } finally { if (sys_idx === idx_job) act_lab(null,false); }
  });

  frm_lab.querySelector('[data-download-seed-art]').addEventListener('click',()=>{
    const txt_art = frm_lab.querySelector('[data-seed-art]').textContent;
    if (txt_art) dsc_fil(txt_art,'kamala-seed-art.txt');
  });
  for (const btn_itm of frm_lab.querySelectorAll('[data-copy-public],[data-copy-secret],[data-copy-otp],[data-copy-seed-art]')) btn_itm.addEventListener('click',async()=>{
    const dmn_itm = frm_lab.querySelector(btn_itm.hasAttribute('data-copy-public') ? '[data-public-output]' : btn_itm.hasAttribute('data-copy-secret') ? '[data-secret-output]' : btn_itm.hasAttribute('data-copy-otp') ? '[data-otp-secret]' : '[data-seed-art]');
    const txt_val = dmn_itm.value || dmn_itm.textContent;
    if (!txt_val) return;
    try { await navigator.clipboard.writeText(txt_val); act_lab('Copied to the clipboard. Clear does not remove clipboard contents.'); }
    catch {
      if (dmn_itm instanceof HTMLTextAreaElement) { dmn_itm.focus(); dmn_itm.select(); }
      act_lab('Clipboard access is unavailable. Select and copy the visible output manually.');
    }
  });

  for (const btn_itm of frm_lab.querySelectorAll('[data-save-qr]')) btn_itm.addEventListener('click',async()=>{
    const tip_clv = btn_itm.dataset.saveQr, txt_qr = dat_lab.qr[tip_clv]; if (!txt_qr) return;
    const sys_idx = idx_job;
    if (btn_itm.dataset.qrFormat === 'svg') {
      const txt_val = await sys_qr.toString(txt_qr,{type:'svg',errorCorrectionLevel:'M',margin:4});
      if (sys_idx === idx_job && dat_lab.qr[tip_clv] === txt_qr) dsc_fil(txt_val,'kamala-'+tip_clv+'-qr.svg','image/svg+xml');
    } else {
      const dat_itm = await new Promise(dat_itm=>frm_lab.querySelector('[data-qr="'+tip_clv+'"]').toBlob(dat_itm,'image/png'));
      if (dat_itm && sys_idx === idx_job && dat_lab.qr[tip_clv] === txt_qr) dsc_fil(dat_itm,'kamala-'+tip_clv+'-qr.png','image/png');
    }
  });
  for (const btn_itm of frm_lab.querySelectorAll('[data-clear]')) btn_itm.addEventListener('click',clr_lab);
  window.addEventListener('pagehide',clr_lab);
}
