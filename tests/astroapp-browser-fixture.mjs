// Timestamp: 2026-10-30
// Version: 1.12.0
// Author and Credits: https://www.alawise.es/1-s
// This disposable preview fixture must never enter the deployment archive.
import {mkdir, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {fmt_ast, crt_ast} from '../src/astroapp-core.mjs';

const pth_dst = fileURLToPath(new URL('../dist/qa-astroapp/', import.meta.url));
const dat_ast = fmt_ast({date:'2000-02-29', time:'12:34:56', timezone:'+05:45', latitude:'42N30', longitude:'1E31'});
const txt_pag = crt_ast(dat_ast, {api_key:'fixture-only-never-transmitted'}, 1).replace(/src="https:\/\/astroapp\.com\/astro\/astroapi\?key=[^"]+"/, 'src="/qa-astroapp/sdk.js"');
if (txt_pag.includes('astroapp.com')) throw new Error('Fixture must not request a live provider.');
await mkdir(pth_dst, {recursive:true});
await writeFile(pth_dst + 'sdk.js', `// Timestamp: 2026-10-30 | Version: 1.12.0 | Author and Credits: https://www.alawise.es/1-s
window.AstroApp = function () { this.dat_ast = {}; };
for (const txt_val of ['setLongitude','setLatitude','setDate','setTime','setTimeZone','needImage']) window.AstroApp.prototype[txt_val] = function (dat_itm) { this.dat_ast[txt_val] = dat_itm ?? true; };
window.astroRun = dat_itm => {
  const dmn_itm = document.createElement('p');
  dmn_itm.textContent = 'SDK fixture output — no real chart. ' + JSON.stringify(dat_itm.dat_ast);
  document.getElementById('astroappDiv').append(dmn_itm);
};`);
await writeFile(pth_dst + 'index.html', `<!doctype html>
<!-- Timestamp: 2026-10-30 | Version: 1.12.0 | Author and Credits: https://www.alawise.es/1-s -->
<html lang="en"><head><meta charset="utf-8"><title>AstroApp SDK contract fixture</title></head><body><h1>AstroApp SDK contract fixture</h1><p>No real chart. No provider request. Synthetic coordinates and time.</p><p id="status" role="status">Waiting for the frame.</p><iframe id="frame" title="SDK fixture output" style="width:90%;height:480px"></iframe><script type="module">
const dmn_itm = document.getElementById('frame');
window.addEventListener('message', evt_ui => {
  if (evt_ui.source === dmn_itm.contentWindow && evt_ui.origin === location.origin && evt_ui.data?.type === 'kamala:astroapp' && evt_ui.data.state === 'requested' && evt_ui.data.output) document.getElementById('status').textContent = 'Fixture completed: documented methods, head loader, load event and parent status message.';
});
dmn_itm.srcdoc = ${JSON.stringify(txt_pag).replaceAll('<','\\u003c')};
</script></body></html>`);
console.log('Disposable fixture ready at /qa-astroapp/. Remove dist/qa-astroapp before packaging.');
