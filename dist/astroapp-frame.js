// Timestamp: 2026-10-30
// Version: 2.0.0
// Author and Credits: https://www.alawise.es/1-s
import {run_ast} from './astroapp-core.mjs?v=2.0.0';

const idx_job = Number(document.documentElement.dataset.astroappFrame);
const dmn_itm = document.getElementById('astroappDiv');
const txt_rsp = document.querySelector('.astro-frame-status');
let est_ast = 'waiting';
const obs_ast = () => {
  const dat_res = Boolean(dmn_itm.childElementCount || dmn_itm.textContent.trim());
  if (dat_res) txt_rsp.hidden = true;
  parent.postMessage({type: 'kamala:astroapp', job: idx_job, state: est_ast, output: dat_res, height: document.body.scrollHeight}, new URL(import.meta.url).origin);
};
new ResizeObserver(obs_ast).observe(document.body);
new MutationObserver(obs_ast).observe(dmn_itm, {childList: true, subtree: true, characterData: true});

// The documented sample invokes astroRun after the document's load event.
const act_ast = () => {
  try {
    run_ast(window, JSON.parse(document.getElementById('astroapp-data').textContent));
    est_ast = 'requested';
  } catch {
    est_ast = 'unavailable';
    txt_rsp.textContent = 'AstroApp could not start this chart.';
  }
  obs_ast();
};
if (document.readyState === 'complete') act_ast();
else window.addEventListener('load', act_ast, {once: true});
