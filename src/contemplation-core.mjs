// Timestamp: 2026-11-01
// Version: 2.1.0
// Author & Credits: https://www.alawise.es/1-s
// Traffic and firewall counters are visual inputs, not certified random output.
const cnt_max = 1e12;
const val_num = txt_val => typeof txt_val === 'number' && Number.isFinite(txt_val) && txt_val >= 0 && txt_val <= cnt_max;

export function val_tel(dat_tel, sys_ts = Date.now()) {
  if (!dat_tel || dat_tel.schema !== 1 || dat_tel.interface !== 'enp6s0') throw new TypeError('Unsupported telemetry source');
  if (dat_tel.status && dat_tel.status !== 'live') throw new Error('The source interface is unavailable');
  const chr_ts = Date.parse(dat_tel.sampled_at);
  if (!Number.isFinite(chr_ts) || chr_ts > sys_ts + 5000 || sys_ts - chr_ts > 15000) throw new RangeError('The telemetry sample is stale');
  if (typeof dat_tel.session_id !== 'string' || !/^[a-zA-Z0-9._:-]{1,96}$/.test(dat_tel.session_id)) throw new TypeError('Missing collector session');
  if (!val_num(dat_tel.interval_s) || dat_tel.interval_s > 30) throw new TypeError('Invalid sample interval');
  for (const clv_esc of ['rx_bps','tx_bps','rx_pps','tx_pps']) {
    if (!val_num(dat_tel[clv_esc])) throw new TypeError('Invalid traffic counter');
  }
  if (typeof dat_tel.link_up !== 'boolean') throw new TypeError('Invalid link state');
  const dat_fir = dat_tel.firewall;
  if (!dat_fir || typeof dat_fir.available !== 'boolean' ||
      !Number.isSafeInteger(dat_fir.total) || dat_fir.total < 0 ||
      !Number.isSafeInteger(dat_fir.delta) || dat_fir.delta < 0) throw new TypeError('Invalid firewall counters');
  // Copy only the public contract. Extra fields can never become rendered text.
  return {schema:1,interface:'enp6s0',session_id:dat_tel.session_id,sampled_at:dat_tel.sampled_at,
    interval_s:dat_tel.interval_s,rx_bps:dat_tel.rx_bps,tx_bps:dat_tel.tx_bps,
    rx_pps:dat_tel.rx_pps,tx_pps:dat_tel.tx_pps,link_up:dat_tel.link_up,
    firewall:{available:dat_fir.available,total:dat_fir.total,delta:dat_fir.delta}};
}

export function act_tel(dat_tel, dat_mem) {
  // Establish a baseline on connection/restart; never replay old firewall notices.
  const est_nue = dat_mem.session !== dat_tel.session_id;
  const est_ord = !est_nue && Date.parse(dat_tel.sampled_at) > (dat_mem.timestamp || 0);
  const cnt_evt = est_ord && dat_tel.firewall.available ? Math.max(0, dat_tel.firewall.total - dat_mem.total) : 0;
  if (est_nue || est_ord) {
    dat_mem.session = dat_tel.session_id;
    dat_mem.timestamp = Date.parse(dat_tel.sampled_at);
    dat_mem.total = dat_tel.firewall.total;
  }
  const fac_rx = Math.min(1, Math.log2(1 + dat_tel.rx_bps / 1024) / 16);
  const fac_tx = Math.min(1, Math.log2(1 + dat_tel.tx_bps / 1024) / 16);
  const fac_pkt = Math.min(1, Math.log2(1 + dat_tel.rx_pps + dat_tel.tx_pps) / 16);
  return {rx:fac_rx,tx:fac_tx,packets:fac_pkt,notices:Math.min(12,cnt_evt),
    live:dat_tel.link_up,firewall:dat_tel.firewall.available};
}

export function crt_demo(chr_ts, sys_ts = Date.now()) {
  const cnt_rx = 180000 + 4e6 * Math.pow(.5 + .5 * Math.sin(chr_ts * .19), 4);
  const cnt_tx = 60000 + 1.6e6 * Math.pow(.5 + .5 * Math.cos(chr_ts * .27), 3);
  return {schema:1,interface:'enp6s0',session_id:'explicit-demo',sampled_at:new Date(sys_ts).toISOString(),
    interval_s:2,rx_bps:cnt_rx,tx_bps:cnt_tx,rx_pps:cnt_rx / 1000,tx_pps:cnt_tx / 1100,link_up:true,
    firewall:{available:true,total:Math.floor(chr_ts / 9),delta:0}};
}
