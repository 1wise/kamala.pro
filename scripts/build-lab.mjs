// Timestamp: 2026-11-02
// Version: 2.1.1
// Author & Credits: https://www.alawise.es/1-s
import { build } from 'esbuild';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
const sys_rad = fileURLToPath(new URL('../',import.meta.url));
const dat_env = await build({
  entryPoints:[join(sys_rad,'src/lab/lab.mjs')], bundle:true, minify:true, write:false,
  platform:'browser', format:'iife', target:['es2022'], legalComments:'eof',
  alias:{crypto:join(sys_rad,'src/lab/crypto-shim.mjs')},
  banner:{js:'// Timestamp: 2026-11-02 | Version: 2.1.1 | Author & Credits: https://www.alawise.es/1-s'},
  metafile:true
});
const txt_val = dat_env.outputFiles[0].text.replace(/<\/script/gi,'<\\/script');
await writeFile(join(sys_rad,'dist/lab.js'),txt_val);
const txt_art = await readFile(join(sys_rad,'src/lab/lab.css'),'utf8');
await writeFile(join(sys_rad,'dist/lab.css'),txt_art);
let txt_note = 'Kamala local tools — bundled third-party notices\n\n';
for (const pth_fil of ['qrcode/license','bcrypt-pbkdf/LICENSE','tweetnacl/LICENSE','bcrypt-pbkdf/node_modules/tweetnacl/LICENSE','node-forge/LICENSE','dijkstrajs/LICENSE.md']) {
  txt_note += '===== ' + pth_fil + ' =====\n' + await readFile(join(sys_rad,'node_modules',pth_fil),'utf8') + '\n\n';
}
await writeFile(join(sys_rad,'dist/assets/lab-licenses.txt'),txt_note);
const txt_ext = await readFile(join(sys_rad,'dist/style.css'),'utf8') + '\n' + await readFile(join(sys_rad,'src/v2.css'),'utf8') + '\n' + txt_art;
let txt_pag = await readFile(join(sys_rad,'dist/apps/entropy/index.html'),'utf8');
txt_pag = txt_pag.replace(/<link rel="stylesheet" href="\/style.css[^\"]*">/,()=>'<style>'+txt_ext+'</style>')
  .replace(/<link rel="stylesheet" href="\/lab.css[^\"]*">/,'').replace(/<link rel="stylesheet" href="\/v2.css[^\"]*">/,'')
  .replace(/href="\/([^\"]*)"/g,'href="https://www.kamala.pro/$1"')
  .replace('<body>','<body class="is-offline">');
const txt_met = "default-src 'none'; script-src 'sha256-" + createHash('sha256').update(txt_val).digest('base64') + "'; style-src 'sha256-" + createHash('sha256').update(txt_ext).digest('base64') + "'; img-src data: blob:; connect-src https://www.kamala.pro/api/entropy.php; worker-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'";
txt_pag = txt_pag.replace(/<meta http-equiv="Content-Security-Policy" content="[^\"]*">/,'<meta http-equiv="Content-Security-Policy" content="'+txt_met+'">')
  .replace(/<script src="\/lab.js[^\"]*" defer><\/script>/,()=>'<script>'+txt_val+'</script>');
const esc_htm = txt_val => txt_val.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
txt_pag = txt_pag.replace('</main>','<details class="section"><summary>Bundled library notices</summary><pre style="white-space:pre-wrap">'+esc_htm(txt_note)+'</pre></details></main>');
// Inline styles are hash-restricted too; the notice uses an existing CSS class.
txt_pag = txt_pag.replace('<pre style="white-space:pre-wrap">','<pre class="lab-notices">');
// Cached pages and earlier chat links can still open the complete current tool.
for (const pth_fil of ['keys-lab.html','keys-lab-2.0.0.html','keys-lab-2.0.4.html','keys-lab-2.1.1.html']) {
  await writeFile(join(sys_rad,'dist/assets',pth_fil),txt_pag);
}
console.log('Built the local browser bundle and a self-contained portable HTML.');
console.log('Bundled packages: ' + [...new Set(Object.keys(dat_env.metafile.inputs).filter(pth_fil=>pth_fil.includes('node_modules')).map(pth_fil=>pth_fil.split('node_modules/')[1].split('/')[0]))].join(', '));
