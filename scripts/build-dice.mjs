// Timestamp: 2026-11-02
// Version: 2.1.1
// Author & Credits: https://www.alawise.es/1-s
import {mkdir,writeFile} from 'node:fs/promises';
import {svg_dad} from '../src/dice-core.mjs';
const pth_dst=new URL('../src/assets/dice/',import.meta.url);
await mkdir(pth_dst,{recursive:true});
for(let cnt_val=1;cnt_val<=6;cnt_val++) {
  await writeFile(new URL('die-'+cnt_val+'.svg',pth_dst),'<!-- Timestamp: 2026-11-02 | Version: 2.1.1 | Author & Credits: https://www.alawise.es/1-s -->\n'+svg_dad(cnt_val)+'\n');
}
console.log('Built six original ivory dice faces with exact recessed indigo pips and no numerals.');
