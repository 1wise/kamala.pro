// Timestamp: 2026-11-07 | Version: 2.3.0 | Author & Credits: https://www.alawise.es/1-s
import { calc_ejes, dat_fas, exp_csv, val_mst, val_tel } from './crystallization-core.mjs?v=2.3.0';

const dmn_app = document.querySelector('[data-crystallization]');
if (dmn_app) ini_mic(dmn_app);

function ini_mic(dmn_app) {
  const sel_mic = clv_dat => dmn_app.querySelector(`[data-mic-${clv_dat}]`);
  const dmn_frm = sel_mic('form');
  const dmn_img = sel_mic('image');
  const dmn_nota = sel_mic('camera-note');
  const dmn_txt = dmn_nota.querySelector('span');
  const dmn_btn = sel_mic('toggle');
  const clv_loc = 'kamala-crystallization-observations-v1';
  let est_cam = false;
  let sys_clk;
  let est_pet = false;
  let clv_vis = 'local';
  let dat_daemon = [];
  let dat_loc = [];
  try {
    const dat_lec = JSON.parse(localStorage.getItem(clv_loc) ?? '[]');
    if (Array.isArray(dat_lec)) dat_loc = dat_lec.slice(0, 200).map(val_mst).filter(Boolean);
  } catch {
    // A blocked or corrupt local store still permits a record for this tab.
  }
  const dat_ejm = [
    { phase: 3, axes_deg: [19, 20, 23, 24, 32, 103], observed_at: '2026-01-01T10:45:00Z' },
    { phase: 2, axes_deg: [18, 22, 32], observed_at: '2026-01-01T10:25:00Z' },
    { phase: 1, axes_deg: [18], observed_at: '2026-01-01T10:10:00Z' },
    { phase: 0, axes_deg: [], observed_at: '2026-01-01T10:00:00Z' },
  ].map(dat_mst => ({ ...dat_mst, sample_id: 'EXAMPLE', material: 'glycine', north_deg: 5, mirrored: false, notes: '' }));
  const dat_sel = () => clv_vis === 'local' ? dat_loc : clv_vis === 'daemon' ? dat_daemon : dat_ejm;

  function dib_rosa(dat_eje, est_nrt) {
    const dmn_ros = sel_mic('rose');
    const cnt_max = Math.max(1, ...dat_eje.bins);
    const txt_eje = dat_eje.bins.map((cnt_eje, idx_bin) => {
      if (cnt_eje === 0) return '';
      const val_rad = (idx_bin * 15 + 7.5) * Math.PI / 180;
      const val_lon = 12 + 60 * cnt_eje / cnt_max;
      const val_x = Math.sin(val_rad) * val_lon;
      const val_y = Math.cos(val_rad) * val_lon;
      return `<line class="mic-angle" x1="${120-val_x}" y1="${101+val_y}" x2="${120+val_x}" y2="${101-val_y}"/>`;
    }).join('');
    // Plot markup contains only constants and arithmetic on validated angle counts.
    dmn_ros.innerHTML = `<g class="mic-grid"><circle cx="120" cy="101" r="75"/><circle cx="120" cy="101" r="50"/><circle cx="120" cy="101" r="25"/><path d="M45 101h150M120 26v150"/></g>${txt_eje}<g class="mic-label" text-anchor="middle"><text x="120" y="18">${est_nrt ? 'N · 0°' : 'TOP · 0°'}</text><text x="217" y="105">${est_nrt ? 'E' : '90°'}</text><text x="120" y="193">${est_nrt ? 'S' : 'BOTTOM'}</text><text x="24" y="105">${est_nrt ? 'W' : '90°'}</text></g>`;
    dmn_ros.setAttribute('aria-label', `Axial distribution of ${dat_eje.angles.length} visible axes, ${est_nrt ? 'north reference' : 'image reference'}`);
  }

  function act_vst() {
    const dat_obs = dat_sel();
    const dat_mst = dat_obs[0];
    const dat_eje = calc_ejes(dat_mst ?? { north_deg: null, axes_deg: [], mirrored: false });
    const est_nrt = Boolean(dat_mst && dat_mst.north_deg !== null);
    sel_mic('phase').textContent = dat_mst?.phase ?? '—';
    sel_mic('phase-text').textContent = dat_mst ? dat_fas[dat_mst.phase] : 'Waiting for an observation';
    sel_mic('reference').textContent = est_nrt ? 'North marker' : 'Image axis · north uncalibrated';
    sel_mic('count').textContent = dat_mst ? dat_eje.angles.length : '—';
    sel_mic('mean').textContent = dat_eje.mean === null ? '—' : `${(Math.round(dat_eje.mean * 10) / 10) % 180}°`;
    sel_mic('concentration').textContent = dat_eje.concentration?.toFixed(2) ?? '—';
    sel_mic('caption').textContent = clv_vis === 'example'
      ? 'Synthetic example. These angles are excluded from the observation log and CSV.'
      : dat_mst
        ? `${dat_mst.sample_id} · ${dat_mst.observed_at} · Visible axes in one image. R summarizes alignment, including cases with several directions.`
        : 'Calibrate north and check east in the image before treating a frame angle as a compass angle.';
    dib_rosa(dat_eje, est_nrt);
    const dmn_lst = sel_mic('history');
    dmn_lst.replaceChildren();
    for (const dat_val of dat_obs.slice(0, 6)) {
      const dmn_fil = document.createElement('li');
      const dmn_cod = document.createElement('b');
      dmn_cod.textContent = dat_val.sample_id + (dat_val.condition_code ? ` / ${dat_val.condition_code}` : '');
      dmn_fil.append(dmn_cod, ` · ${dat_fas[dat_val.phase]} · ${dat_val.axes_deg.length} axes · ${dat_val.observed_at.slice(0, 16).replace('T', ' ')} UTC`);
      if (dat_val.notes) {
        const dmn_det = document.createElement('div');
        dmn_det.textContent = dat_val.notes;
        dmn_fil.append(dmn_det);
      }
      dmn_lst.append(dmn_fil);
    }
    if (!dat_obs.length) {
      const dmn_fil = document.createElement('li');
      dmn_fil.textContent = clv_vis === 'local' ? 'No local observations yet.' : 'Waiting for a daemon observation.';
      dmn_lst.append(dmn_fil);
    }
    sel_mic('export').disabled = !dat_obs.length || clv_vis === 'example';
    sel_mic('history-note').textContent = clv_vis === 'local' ? 'Current browser only'
      : clv_vis === 'daemon' ? 'Published observations' : 'Synthetic example';
  }

  function sel_vst(clv_new) {
    clv_vis = clv_new;
    for (const dmn_tab of dmn_app.querySelectorAll('[data-mic-view]')) {
      dmn_tab.setAttribute('aria-pressed', String(dmn_tab.dataset.micView === clv_vis));
    }
    act_vst();
  }

  dmn_app.querySelectorAll('[data-mic-view]').forEach(dmn_tab => {
    dmn_tab.addEventListener('click', () => sel_vst(dmn_tab.dataset.micView));
  });

  dmn_frm.addEventListener('submit', sys_evt => {
    sys_evt.preventDefault();
    const dat_frm = Object.fromEntries(new FormData(dmn_frm));
    const dat_ang = dat_frm.axes.trim() ? dat_frm.axes.split(',').map(txt_ang => txt_ang.trim()) : [];
    if (dat_ang.some(txt_ang => !/^\d+(?:\.\d+)?$/.test(txt_ang))) {
      sel_mic('feedback').textContent = 'Enter comma-separated image angles using a decimal point.';
      return;
    }
    const dat_mst = val_mst({
      sample_id: dat_frm.sample_id.trim(), material: dat_frm.material, phase: Number(dat_frm.phase),
      observed_at: new Date().toISOString(), north_deg: dat_frm.north_deg === '' ? null : Number(dat_frm.north_deg),
      axes_deg: dat_ang.map(Number), mirrored: dat_frm.mirrored === 'on', notes: dat_frm.notes.trim(),
      condition_code: dat_frm.condition_code.trim(),
    });
    if (!dat_mst) {
      sel_mic('feedback').textContent = 'Check the sample code and angles. A liquid observation has no crystal axes.';
      return;
    }
    dat_loc = [dat_mst, ...dat_loc].slice(0, 200);
    try {
      localStorage.setItem(clv_loc, JSON.stringify(dat_loc));
      sel_mic('feedback').textContent = 'Saved in this browser.';
    } catch {
      sel_mic('feedback').textContent = 'Saved for this tab. Download the CSV before closing.';
    }
    dmn_frm.elements.axes.value = '';
    dmn_frm.elements.notes.value = '';
    sel_vst('local');
  });

  sel_mic('export').addEventListener('click', () => {
    const dat_obs = dat_sel();
    if (!dat_obs.length || clv_vis === 'example') return;
    const pth_url = URL.createObjectURL(new Blob([exp_csv(dat_obs, clv_vis)], { type: 'text/csv;charset=utf-8' }));
    const dmn_lnk = document.createElement('a');
    dmn_lnk.href = pth_url;
    dmn_lnk.download = `kamala-crystallization-${clv_vis}.csv`;
    dmn_lnk.click();
    setTimeout(() => URL.revokeObjectURL(pth_url), 1000);
  });

  function act_cam() {
    const est_img = est_cam && !document.hidden;
    dmn_btn.textContent = est_cam ? 'Stop image' : 'Start image';
    if (est_img && !dmn_img.hasAttribute('src')) {
      sel_mic('camera-status').textContent = 'Connecting';
      dmn_txt.textContent = 'Connecting to Mic 1…';
      dmn_img.src = dmn_app.dataset.source;
    } else if (!est_img) {
      dmn_img.removeAttribute('src');
      dmn_img.hidden = true;
      dmn_nota.hidden = false;
      sel_mic('camera-status').textContent = 'Image paused';
      dmn_txt.textContent = 'Start the live microscope image.';
    }
  }

  dmn_btn.addEventListener('click', () => {
    est_cam = !est_cam;
    act_cam();
  });
  dmn_img.addEventListener('load', () => {
    if (!est_cam || document.hidden || !dmn_img.naturalWidth) return;
    dmn_img.hidden = false;
    dmn_nota.hidden = true;
    sel_mic('camera-status').textContent = 'Image connected';
  });
  dmn_img.addEventListener('error', () => {
    if (!est_cam || !dmn_img.hasAttribute('src')) return;
    est_cam = false;
    act_cam();
    sel_mic('camera-status').textContent = 'Image unavailable';
    dmn_txt.textContent = 'The feed is unavailable. Start again to retry.';
  });

  async function lee_tel() {
    if (est_pet || document.hidden) return;
    est_pet = true;
    try {
      const rsp_tel = await fetch(dmn_app.dataset.endpoint, { cache: 'no-store', signal: AbortSignal.timeout(5000) });
      if (rsp_tel.status === 404) {
        sel_mic('status').textContent = 'Waiting for daemon';
        return;
      }
      if (!rsp_tel.ok || !rsp_tel.headers.get('Content-Type')?.includes('application/json') || !rsp_tel.body) {
        throw new Error('Unexpected response');
      }
      const sys_lee = rsp_tel.body.getReader();
      const sys_dec = new TextDecoder();
      let cnt_byt = 0;
      let txt_jso = '';
      while (true) {
        const { done, value } = await sys_lee.read();
        if (done) break;
        cnt_byt += value.byteLength;
        if (cnt_byt > 131072) {
          await sys_lee.cancel();
          throw new Error('Telemetry size limit');
        }
        txt_jso += sys_dec.decode(value, { stream: true });
      }
      const dat_tel = val_tel(JSON.parse(txt_jso + sys_dec.decode()));
      if (!dat_tel) throw new Error('Invalid telemetry');
      dat_daemon = dat_tel.observations;
      const sys_ts = Date.parse(rsp_tel.headers.get('Date') ?? '') || Date.now();
      const cnt_age = Math.max(0, Number(rsp_tel.headers.get('Age')) || 0);
      const est_act = sys_ts + cnt_age * 1000 - Date.parse(dat_tel.updated_at) < 180000;
      sel_mic('status').textContent = est_act ? 'Daemon connected' : 'Daemon record is stale';
      if (clv_vis === 'daemon') act_vst();
    } catch {
      sel_mic('status').textContent = dat_daemon.length ? 'Daemon unavailable · last record' : 'Waiting for daemon';
    } finally {
      est_pet = false;
      if (!document.hidden) sys_clk = setTimeout(lee_tel, 15000);
    }
  }

  document.addEventListener('visibilitychange', () => {
    clearTimeout(sys_clk);
    act_cam();
    if (!document.hidden) lee_tel();
  });
  window.addEventListener('pagehide', () => {
    clearTimeout(sys_clk);
    dmn_img.removeAttribute('src');
  });
  window.addEventListener('pageshow', () => {
    clearTimeout(sys_clk);
    act_cam();
    lee_tel();
  });
  act_vst();
  lee_tel();
}
