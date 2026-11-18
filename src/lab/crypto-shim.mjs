// Timestamp: 2026-10-29
// Version: 1.9.0
// Author & Credits: https://www.alawise.es/1-s
// The bcrypt dependency only needs SHA-512; its optional RNG stays OS-backed too.
export function rnd_sys(cnt_tot) {
  if (!Number.isInteger(cnt_tot) || cnt_tot < 1 || cnt_tot > 8192) throw new RangeError('Invalid byte count');
  return crypto.getRandomValues(new Uint8Array(cnt_tot));
}
export { rnd_sys as randomBytes };
