// Timestamp: 2026-10-30
// Version: 2.0.3
// Author and Credits: https://www.alawise.es/1-s
// Names match the complete JavaScript reference supplied by the site owner.
export const dat_opt = {
  house: {placidus:'HOUSE_PLACIDUS', koch:'HOUSE_KOCH', whole:'HOUSE_WHOLE_SIGN', porphyrius:'PORPHYRIUS', regiomontanus:'REGIOMONTANUS'},
  zodiac: {tropical:'NO_AYANAMSA', lahiri:'AYANAMSA_LAHIRI', faganbradley:'AYANAMSA_FAGANBRADLEY', raman:'AYANAMSA_RAMAN'},
  coordinates: {geo:'COORD_GEO', helio:'COORD_HELIO'},
  style: {proportional:'STYLE_PROPORTIONAL', south:'STYLE_INDIAN_SOUTH', north:'STYLE_INDIAN_NORTH', rainbow:'STYLE_CIRC_RAINBOW', european:'STYLE_EURO1'},
  language: {en:'LANG_ENGLISH', de:'LANG_GERMAN', ja:'LANG_JAPANESE'}
};

export const dat_car = {
  western: {label:'Western · natal chart', note:'A natal horoscope. Tropical or Fagan/Bradley sidereal zodiac, with its own house system and diagram.', defaults:{house:'placidus',zodiac:'tropical',coordinates:'geo',style:'proportional',language:'en'}, style:['proportional','rainbow','european'], zodiac:['tropical','faganbradley'], coordinates:['geo','helio'], divisional:false},
  jyotish: {label:'Jyotisha · Rāśi / D1', note:'The principal sign chart in Jyotisha. Lahiri or Raman ayanamsa, with a North or South Indian diagram.', defaults:{house:'whole',zodiac:'lahiri',coordinates:'geo',style:'south',language:'en'}, style:['south','north'], zodiac:['lahiri','raman'], coordinates:['geo'], divisional:false},
  varga: {label:'Jyotisha · divisional chart', note:'A divisional calculation, such as D9 Navamsa. It requires the selected division to be included in the provider request.', defaults:{house:'whole',zodiac:'lahiri',coordinates:'geo',style:'south',language:'en'}, style:['south','north'], zodiac:['lahiri','raman'], coordinates:['geo'], divisional:true}
};

export function fmt_ast(dat_frm) {
  const dat_ast = Object.fromEntries(['date', 'time', 'timezone', 'longitude', 'latitude'].map(clv_esc => [clv_esc, String(dat_frm[clv_esc] ?? '').trim().toUpperCase()]));
  dat_ast.chart = String(dat_frm.chart || 'western');
  if (!Object.hasOwn(dat_car,dat_ast.chart)) throw new Error('Choose a listed chart method.');
  const cfg_ast = dat_car[dat_ast.chart];
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dat_ast.date)) throw new Error('Enter a complete date.');
  const dat_env = dat_ast.date.split('-').map(Number);
  const dat_lim = [31, dat_env[0] % 4 === 0 && (dat_env[0] % 100 !== 0 || dat_env[0] % 400 === 0) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (dat_env[0] < 1 || dat_env[1] < 1 || dat_env[1] > 12 || dat_env[2] < 1 || dat_env[2] > dat_lim[dat_env[1] - 1]) throw new Error('Enter a valid calendar date.');
  if (!/^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$/.test(dat_ast.time)) throw new Error('Enter a valid clock time.');
  if (!/^[+-](?:0\d|1[0-4]):[0-5]\d$/.test(dat_ast.timezone) || /^[-+]14:(?!00)/.test(dat_ast.timezone)) throw new Error('Use a UTC offset such as +01:00 or -05:00, within ±14:00.');
  for (const [clv_esc, cnt_tot, txt_val] of [['longitude', 180, 'EW'], ['latitude', 90, 'NS']]) {
    const dat_res = new RegExp('^(\\d{1,3})([' + txt_val + '])([0-5]\\d)$').exec(dat_ast[clv_esc]);
    if (!dat_res || Number(dat_res[1]) > cnt_tot || (Number(dat_res[1]) === cnt_tot && Number(dat_res[3]) !== 0)) throw new Error('Use degree-minute coordinates such as 1E31 and 42N30, within their geographic bounds.');
    dat_ast[clv_esc] = Number(dat_res[1]) + dat_res[2] + dat_res[3];
  }
  // The current servlet rejects the colon form accepted by the older guide.
  dat_ast.date = dat_ast.date.replaceAll('-', '/');
  if (dat_ast.time.length === 5) dat_ast.time += ':00';
  for (const [clv_esc, txt_val] of Object.entries(cfg_ast.defaults)) {
    dat_ast[clv_esc] = String(dat_frm[clv_esc] || txt_val);
    if (!Object.hasOwn(dat_opt[clv_esc], dat_ast[clv_esc])) throw new Error('Choose a documented ' + clv_esc + ' option.');
    if (cfg_ast[clv_esc] && !cfg_ast[clv_esc].includes(dat_ast[clv_esc])) throw new Error('Choose a ' + clv_esc + ' convention for the selected chart method.');
  }
  dat_ast.varga = cfg_ast.divisional ? Number(dat_frm.varga || 9) : null;
  if (cfg_ast.divisional && ![2,3,4,5,6,7,8,9,10,11,12,16,20,24,27,30,40,45,60].includes(dat_ast.varga)) throw new Error('Choose a listed divisional chart. Rāśi / D1 has its own chart method.');
  dat_ast.height = Number(dat_frm.height || 0);
  if (!Number.isFinite(dat_ast.height) || dat_ast.height < -500 || dat_ast.height > 10000) throw new Error('Elevation must be between -500 and 10000 meters.');
  dat_ast.xml = dat_frm.xml === true || dat_frm.xml === 'on';
  return dat_ast;
}

export function fmt_geo(val_geo, clv_eje) {
  const lim_deg = clv_eje === 'latitude' ? 90 : clv_eje === 'longitude' ? 180 : -1;
  if (!Number.isFinite(val_geo) || lim_deg < 0 || Math.abs(val_geo) > lim_deg) throw new Error('The browser returned coordinates outside the valid range.');
  const ang_sig = Math.abs(val_geo);
  let cnt_deg = Math.floor(ang_sig);
  let min_geo = Math.round((ang_sig - cnt_deg) * 60);
  if (min_geo === 60) { cnt_deg++; min_geo = 0; }
  if (cnt_deg > lim_deg || (cnt_deg === lim_deg && min_geo !== 0)) throw new Error('The browser returned coordinates outside the valid range.');
  const txt_val = clv_eje === 'latitude' ? (val_geo < 0 ? 'S' : 'N') : (val_geo < 0 ? 'W' : 'E');
  return `${cnt_deg}${txt_val}${String(min_geo).padStart(2, '0')}`;
}

export function url_ast(cfg_ast) {
  const txt_val = cfg_ast?.api_key;
  if (typeof txt_val !== 'string' || !txt_val.trim() || txt_val.length > 4096 || /[\s\x00-\x1f\x7f]/.test(txt_val) || /your[_ -]?api|replace[_ -]?me|access[_ -]?code/i.test(txt_val)) throw new Error('AstroApp is not configured.');
  const url_app = new URL('https://astroapp.com/astro/astroapi');
  url_app.searchParams.set('key', txt_val);
  return url_app.href;
}

function esc_htm(txt_val) {
  return String(txt_val).replace(/[&<>"']/g, txt_val => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[txt_val]));
}

export function crt_ast(dat_ast, cfg_ast, idx_job) {
  if (!Number.isSafeInteger(idx_job) || idx_job < 1) throw new Error('Invalid chart request.');
  // A separate document preserves the provider's parser-time head loader and
  // on-load contract. Replacing it prevents older charts from changing a new one.
  return `<!doctype html>
<!-- Timestamp: 2026-10-30 | Version: 2.0.0 | Author and Credits: https://www.alawise.es/1-s -->
<html lang="en" data-astroapp-frame="${idx_job}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="origin"><title>AstroApp chart</title><link rel="stylesheet" href="/astroapp.css?v=2.0.0"><script type="text/javascript" src="${esc_htm(url_ast(cfg_ast))}" referrerpolicy="origin"></script><script type="module" src="/astroapp-frame.js?v=2.0.0"></script></head><body class="astro-document"><script type="application/json" id="astroapp-data">${JSON.stringify(dat_ast).replaceAll('<', '\\u003c')}</script><div id="astroappDiv"></div><p class="astro-frame-status" role="status">Waiting for AstroApp…</p></body></html>`;
}

export function run_ast(sys_cfg, dat_frm, act_fin) {
  if (typeof sys_cfg.AstroApp !== 'function' || typeof sys_cfg.astroRun !== 'function') throw new Error('The AstroApp loader is unavailable.');
  const dat_ast = new sys_cfg.AstroApp();
  for (const txt_val of ['setLongitude', 'setLatitude', 'setDate', 'setTime', 'setTimeZone', 'setHouseSys', 'setAyanamsa', 'setCoordSys', 'setStyle', 'setLanguage', 'setHeight', 'needImage']) {
    if (typeof dat_ast[txt_val] !== 'function') throw new Error('The AstroApp interface is unavailable.');
  }
  dat_ast.setLongitude(dat_frm.longitude);
  dat_ast.setLatitude(dat_frm.latitude);
  dat_ast.setDate(dat_frm.date);
  dat_ast.setTime(dat_frm.time);
  dat_ast.setTimeZone(dat_frm.timezone);
  for (const [clv_esc, txt_val] of Object.entries({house:'setHouseSys', zodiac:'setAyanamsa', coordinates:'setCoordSys', style:'setStyle', language:'setLanguage'})) {
    const dat_val = sys_cfg.AstroApp[dat_opt[clv_esc][dat_frm[clv_esc]]];
    if (dat_val === undefined) throw new Error('The loaded AstroApp SDK does not provide the selected ' + clv_esc + '.');
    dat_ast[txt_val](dat_val);
  }
  dat_ast.setHeight(dat_frm.height);
  if (dat_car[dat_frm.chart]?.divisional) {
    if (typeof dat_ast.setVarga !== 'function' || typeof dat_ast.getData !== 'function') throw new Error('Divisional charts are unavailable in the loaded AstroApp SDK.');
    dat_ast.setVarga(dat_frm.varga);
    // The observed SDK stores this number but omits it from getData().
    // Stop that incomplete request instead of calculating an unrelated chart.
    const dat_env = dat_ast.getData();
    if (Number(dat_env.param) !== dat_frm.varga) throw new Error('The loaded AstroApp SDK omits the divisional chart number from its request. This divisional chart cannot be submitted with this SDK version.');
  }
  if (dat_frm.xml) {
    if (typeof dat_ast.needObjects !== 'function' || typeof dat_ast.needAspects !== 'function') throw new Error('XML output is unavailable in this SDK.');
    dat_ast.needObjects();
    dat_ast.needAspects();
  }
  dat_ast.needImage();
  sys_cfg.astroRun(dat_ast, act_fin);
  return dat_ast;
}
