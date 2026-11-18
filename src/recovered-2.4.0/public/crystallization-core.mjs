// Timestamp: 2026-11-07 | Version: 2.3.0 | Author & Credits: https://www.alawise.es/1-s
export const dat_fas = ['Liquid', 'First crystals', 'Growth', 'Final observed'];

const pat_cod = /^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$/;
const pat_utc = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/;
const es_ang = val_ang => Number.isFinite(val_ang) && val_ang >= 0 && val_ang < 360;
const mod_eje = val_ang => ((val_ang % 180) + 180) % 180;

export function val_mst(dat_mst) {
  if (!dat_mst || typeof dat_mst !== 'object') return null;
  const { sample_id, material, phase, observed_at, north_deg, axes_deg } = dat_mst;
  const { condition_code = '', mirrored = false, notes = '' } = dat_mst;
  if (typeof sample_id !== 'string' || !pat_cod.test(sample_id)
      || typeof material !== 'string' || !pat_cod.test(material)
      || typeof condition_code !== 'string' || condition_code.length > 16
      || (condition_code !== '' && !pat_cod.test(condition_code))
      || !Number.isInteger(phase) || phase < 0 || phase > 3
      || typeof observed_at !== 'string' || !pat_utc.test(observed_at) || !Number.isFinite(Date.parse(observed_at))
      || (north_deg !== null && !es_ang(north_deg)) || typeof mirrored !== 'boolean'
      || !Array.isArray(axes_deg) || axes_deg.length > 32 || !axes_deg.every(es_ang)
      || (phase === 0 && axes_deg.length > 0)
      || typeof notes !== 'string' || notes.length > 240) return null;
  return { sample_id, material, phase, observed_at, north_deg, axes_deg, condition_code, mirrored, notes };
}

export function val_tel(dat_tel) {
  if (!dat_tel || dat_tel.version !== 1
      || typeof dat_tel.updated_at !== 'string' || !pat_utc.test(dat_tel.updated_at)
      || !Number.isFinite(Date.parse(dat_tel.updated_at))
      || !Array.isArray(dat_tel.observations) || dat_tel.observations.length > 200) return null;
  const dat_obs = dat_tel.observations.map(val_mst);
  if (dat_obs.some(dat_mst => dat_mst === null)) return null;
  dat_obs.sort((dat_izq, dat_der) => Date.parse(dat_der.observed_at) - Date.parse(dat_izq.observed_at));
  return { updated_at: dat_tel.updated_at, observations: dat_obs };
}

export function calc_ejes(dat_mst) {
  const { north_deg, axes_deg, mirrored } = dat_mst;
  const dat_ang = axes_deg.map(val_ang => north_deg === null
    ? mod_eje(val_ang)
    : mod_eje((val_ang - north_deg) * (mirrored ? -1 : 1)));
  const dat_bin = Array(12).fill(0);
  let sum_cos = 0;
  let sum_sen = 0;
  for (const val_ang of dat_ang) {
    dat_bin[Math.floor(val_ang / 15)] += 1;
    // Double the angle because the two ends of a crystal axis are equivalent.
    const val_rad = val_ang * Math.PI / 90;
    sum_cos += Math.cos(val_rad);
    sum_sen += Math.sin(val_rad);
  }
  const val_con = dat_ang.length > 1 ? Math.min(1, Math.hypot(sum_cos, sum_sen) / dat_ang.length) : null;
  const val_med = val_con !== null && val_con >= 0.1
    ? mod_eje(Math.atan2(sum_sen, sum_cos) * 90 / Math.PI) : null;
  return { angles: dat_ang, bins: dat_bin, concentration: val_con, mean: val_med };
}

export function exp_csv(dat_obs, clv_fnt) {
  const txt_csv = val_cel => {
    let txt_cel = String(val_cel ?? '');
    if (/^\s*[=+\-@\t\r]/.test(txt_cel)) txt_cel = "'" + txt_cel;
    return '"' + txt_cel.replaceAll('"', '""') + '"';
  };
  const dat_col = ['source', 'sample_id', 'condition_code', 'material', 'observed_at_utc', 'phase',
    'north_in_image_deg', 'mirrored', 'axis_reference', 'axes_in_image_deg', 'reported_axes_deg',
    'mean_axis_deg', 'concentration_r', 'notes'];
  const dat_fil = dat_obs.map(dat_mst => {
    const dat_eje = calc_ejes(dat_mst);
    return [clv_fnt, dat_mst.sample_id, dat_mst.condition_code, dat_mst.material, dat_mst.observed_at,
      dat_mst.phase, dat_mst.north_deg, dat_mst.mirrored,
      dat_mst.north_deg === null ? 'image' : 'north', dat_mst.axes_deg.join(';'),
      dat_eje.angles.map(val_ang => val_ang.toFixed(2)).join(';'),
      dat_eje.mean?.toFixed(2), dat_eje.concentration?.toFixed(3), dat_mst.notes].map(txt_csv).join(',');
  });
  return [dat_col.join(','), ...dat_fil].join('\r\n') + '\r\n';
}
