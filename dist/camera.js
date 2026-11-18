/* Timestamp: 2026-10-29 | Version: 1.6.0 | Author and Credits: https://www.alawise.es/1-s */
'use strict';

const dmn_itm = document.querySelector('.cam-player');
if (dmn_itm) {
  const dmn_vis = dmn_itm.querySelector('.cam-feed');
  const msj_rsp = dmn_itm.querySelector('.cam-message');
  const btn_cam = dmn_itm.querySelector('[data-camera-toggle]');
  let est_cam = true;
  let tms_cam;

  const act_cam = () => {
    clearInterval(tms_cam);
    est_cam = true;
    dmn_vis.hidden = false;
    btn_cam.textContent = 'Stop feed';
    msj_rsp.textContent = 'Connecting to camera…';
    // MJPEG does not consistently fire load after its first frame in every browser.
    tms_cam = setInterval(() => {
      if (est_cam && dmn_vis.naturalWidth > 0) {
        msj_rsp.textContent = 'Camera image available · source delay may apply';
        clearInterval(tms_cam);
      }
      if (est_cam && dmn_vis.complete && !dmn_vis.naturalWidth) {
        dmn_vis.dispatchEvent(new Event('error'));
      }
    }, 1000);
    dmn_vis.src = dmn_itm.dataset.source;
  };

  dmn_vis.addEventListener('error', () => {
    if (!est_cam) return;
    clearInterval(tms_cam);
    est_cam = false;
    dmn_vis.hidden = true;
    btn_cam.textContent = 'Reconnect';
    msj_rsp.textContent = 'Feed unavailable. Reconnect or open the source link.';
  });
  btn_cam.addEventListener('click', () => {
    if (!est_cam) { act_cam(); return; }
    est_cam = false;
    clearInterval(tms_cam);
    dmn_vis.removeAttribute('src');
    dmn_vis.hidden = true;
    btn_cam.textContent = 'Start feed';
    msj_rsp.textContent = 'Feed stopped';
  });
  dmn_itm.querySelector('[data-fullscreen]').addEventListener('click', async () => {
    if (dmn_itm.classList.contains('is-expanded')) {
      dmn_itm.classList.remove('is-expanded');
      dmn_itm.querySelector('[data-fullscreen]').textContent = 'Fullscreen';
      dmn_itm.querySelector('[data-fullscreen]').setAttribute('aria-pressed', 'false');
      return;
    }
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await dmn_itm.requestFullscreen();
    } catch {
      // Embedded browsers may deny native fullscreen. A full-window view still works.
      dmn_itm.classList.add('is-expanded');
      dmn_itm.querySelector('[data-fullscreen]').textContent = 'Exit full view';
      dmn_itm.querySelector('[data-fullscreen]').setAttribute('aria-pressed', 'true');
    }
  });
  document.addEventListener('keydown', (evt_ui) => {
    if (evt_ui.key === 'Escape' && dmn_itm.classList.contains('is-expanded')) {
      dmn_itm.classList.remove('is-expanded');
      dmn_itm.querySelector('[data-fullscreen]').textContent = 'Fullscreen';
      dmn_itm.querySelector('[data-fullscreen]').setAttribute('aria-pressed', 'false');
    }
  });
  document.addEventListener('fullscreenchange', () => {
    dmn_itm.querySelector('[data-fullscreen]').textContent = document.fullscreenElement ? 'Exit fullscreen' : 'Fullscreen';
    dmn_itm.querySelector('[data-fullscreen]').setAttribute('aria-pressed', String(Boolean(document.fullscreenElement)));
  });
  window.addEventListener('pagehide', () => {
    est_cam = false;
    clearInterval(tms_cam);
    dmn_vis.removeAttribute('src');
  });
  window.addEventListener('pageshow', (evt_ui) => {
    if (evt_ui.persisted) act_cam();
  });
  // The markup starts the initial connection; observe it without requesting it twice.
  tms_cam = setInterval(() => {
    if (est_cam && dmn_vis.naturalWidth > 0) {
      msj_rsp.textContent = 'Camera image available · source delay may apply';
      clearInterval(tms_cam);
    }
    // Catch failures that happened before the deferred script attached its listeners.
    if (est_cam && dmn_vis.complete && !dmn_vis.naturalWidth) {
      dmn_vis.dispatchEvent(new Event('error'));
    }
  }, 1000);
}
