// Timestamp: 2026-10-30
// Version: 2.0.2
// Author and Credits: https://www.alawise.es/1-s
// The release installer writes the provider's literal head tag on Excalibur.
// This fallback supports a host configured after the HTML was installed.
window.kamalaAstroReady = (async () => {
  // Older pages may retain this loader until the HTML repair is applied.
  if (document.readyState === 'loading') await new Promise(act_fin => document.addEventListener('DOMContentLoaded', act_fin, {once:true}));
  if (!document.querySelector('[data-astroapp]')) return false;
  if (typeof window.AstroApp === 'function' && typeof window.astroRun === 'function') return true;
  if (document.querySelector('script[data-astroapp-sdk]')) return false;
  try {
    const rsp_env = await fetch('/astroapp-config.json', {cache:'no-store', credentials:'omit', redirect:'error', signal:AbortSignal.timeout(5000)});
    if (!rsp_env.ok) return false;
    const txt_val = await rsp_env.text();
    if (txt_val.length > 8192) return false;
    const cfg_ast = JSON.parse(txt_val);
    if (typeof cfg_ast.api_key !== 'string' || !cfg_ast.api_key || cfg_ast.api_key.length > 4096 || /[\s\x00-\x1f\x7f]/.test(cfg_ast.api_key) || /your[_ -]?api|replace[_ -]?me|access[_ -]?code/i.test(cfg_ast.api_key)) return false;
    const url_app = new URL('https://astroapp.com/astro/astroapi');
    url_app.searchParams.set('key', cfg_ast.api_key);
    // A previous rejected SDK response may still be in the browser cache.
    url_app.searchParams.set('v', '2.0.2');
    return await new Promise(act_fin => {
      const dmn_itm = document.createElement('script');
      dmn_itm.type = 'text/javascript';
      dmn_itm.dataset.astroappSdk = '';
      dmn_itm.referrerPolicy = 'origin';
      dmn_itm.src = url_app.href;
      const sys_ts = setTimeout(() => act_fin(false), 15000);
      dmn_itm.onload = () => { clearTimeout(sys_ts); act_fin(typeof window.AstroApp === 'function' && typeof window.astroRun === 'function'); };
      dmn_itm.onerror = () => { clearTimeout(sys_ts); act_fin(false); };
      document.head.appendChild(dmn_itm);
    });
  } catch { return false; }
})();
