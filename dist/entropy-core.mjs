// Timestamp: 2026-10-31
// Version: 2.0.5
// Author and Credits: https://www.alawise.es/1-s
// One sampler contract serves article experiments and the standalone key tool.
export async function crt_azr(clv_cam = 'auto', url_app = '/api/entropy.php') {
  if (!['auto','cam1','cam2','cam3','cam4','browser'].includes(clv_cam)) throw new RangeError('Unknown source');
  if (!['/api/entropy.php','https://www.kamala.pro/api/entropy.php','https://kamala.pro/api/entropy.php'].includes(url_app)) throw new Error('Unknown sampler');
  const dat_azr = { seed:new Uint32Array(16), cursor:0, label:'Browser randomness only', sample:null };
  crypto.getRandomValues(dat_azr.seed);
  if (clv_cam === 'browser') return dat_azr;
  try {
    const rsp_env = await fetch(url_app + '?src=' + encodeURIComponent(clv_cam), {
      cache:'no-store', credentials:'omit', referrerPolicy:'no-referrer', redirect:'error',
      signal:AbortSignal.timeout(2800), headers:{Accept:'application/json'}
    });
    if (!rsp_env.ok) throw new Error('Sampler unavailable');
    const dat_env = await rsp_env.json();
    if (!/^[a-f0-9]{128}$/.test(dat_env.hex)) throw new Error('Invalid sample');
    if (!(dat_env.mode === 'system-only' && dat_env.source === null && dat_env.sample_bytes === 0) &&
        !(dat_env.mode === 'stream+system' && /^cam[1-4]$/.test(dat_env.source) &&
          (clv_cam === 'auto' || dat_env.source === clv_cam) && Number.isInteger(dat_env.sample_bytes) &&
          dat_env.sample_bytes >= 1024 && dat_env.sample_bytes <= 131072)) throw new Error('Invalid source metadata');
    for (let sys_idx = 0; sys_idx < 16; sys_idx++) dat_azr.seed[sys_idx] ^= parseInt(dat_env.hex.slice(sys_idx*8,sys_idx*8+8),16);
    dat_azr.sample = dat_env;
    dat_azr.label = dat_env.mode === 'stream+system'
      ? dat_env.source.toUpperCase() + ' + server + browser randomness · ' + dat_env.sample_bytes + ' image bytes'
      : 'Server + browser randomness · no camera sample available';
  } catch { dat_azr.label = 'Browser randomness only · stream sampler unavailable'; }
  return dat_azr;
}

export function rnd_ent(dat_azr, cnt_tot) {
  if (!Number.isInteger(cnt_tot) || cnt_tot < 1 || cnt_tot > 0x100000000) throw new RangeError('Invalid range');
  const sys_lim = Math.floor(0x100000000 / cnt_tot) * cnt_tot;
  let rnd_bit;
  do {
    rnd_bit = (crypto.getRandomValues(new Uint32Array(1))[0] ^ dat_azr.seed[dat_azr.cursor++ % 16]) >>> 0;
  } while (rnd_bit >= sys_lim);
  return rnd_bit % cnt_tot;
}

export function rnd_oct(dat_azr, cnt_tot) {
  if (!dat_azr || !(dat_azr.seed instanceof Uint32Array) || dat_azr.seed.length !== 16) throw new Error('A shared entropy session is required');
  if (!Number.isInteger(cnt_tot) || cnt_tot < 1 || cnt_tot > 8192) throw new RangeError('Invalid byte count');
  const dat_itm = crypto.getRandomValues(new Uint8Array(cnt_tot));
  // Public or repeated camera data never replaces fresh local OS randomness.
  for (let sys_idx = 0; sys_idx < cnt_tot; sys_idx++) {
    dat_itm[sys_idx] ^= dat_azr.seed[(dat_azr.cursor + Math.floor(sys_idx/4)) % 16] >>> (24 - (sys_idx % 4)*8);
  }
  dat_azr.cursor = (dat_azr.cursor + Math.ceil(cnt_tot/4)) % 16;
  return dat_itm;
}
