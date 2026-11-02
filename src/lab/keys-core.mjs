// Timestamp: 2026-10-29
// Version: 1.10.0
// Author & Credits: https://www.alawise.es/1-s
import sys_kdf from 'bcrypt-pbkdf';
import sys_ncl from 'tweetnacl';
import sys_rsa from 'node-forge/lib/rsa.js';
import { rnd_oct } from '../entropy-core.mjs';
import { rnd_sys } from './crypto-shim.mjs';
export { rnd_sys };
const sys_enc = new TextEncoder();

export function cat_oct(...dat_env) {
  const dat_itm = new Uint8Array(dat_env.reduce((cnt_tot, dat_itm) => cnt_tot + dat_itm.length, 0));
  let sys_idx = 0;
  for (const dat_par of dat_env) { dat_itm.set(dat_par, sys_idx); sys_idx += dat_par.length; }
  return dat_itm;
}
export function enc_b64(dat_itm) {
  let txt_val = '';
  for (const rnd_bit of dat_itm) txt_val += String.fromCharCode(rnd_bit);
  return btoa(txt_val);
}
export function dec_b64(txt_val) {
  return Uint8Array.from(atob(txt_val.replace(/-/g, '+').replace(/_/g, '/')), txt_val => txt_val.charCodeAt(0));
}
export function enc_b32(dat_itm) {
  let txt_val = '', rnd_bit = 0, cnt_tot = 0;
  for (const sys_idx of dat_itm) {
    rnd_bit = (rnd_bit << 8) | sys_idx; cnt_tot += 8;
    while (cnt_tot >= 5) { cnt_tot -= 5; txt_val += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'[(rnd_bit >>> cnt_tot) & 31]; }
  }
  if (cnt_tot) txt_val += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'[(rnd_bit << (5 - cnt_tot)) & 31];
  return txt_val;
}
export function fmt_sec(dat_itm, fmt_clv) {
  if (fmt_clv === 'hex') return Array.from(dat_itm, rnd_bit => rnd_bit.toString(16).padStart(2, '0')).join('');
  if (fmt_clv === 'base64') return enc_b64(dat_itm);
  if (fmt_clv === 'base64url') return enc_b64(dat_itm).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  if (fmt_clv === 'base32') return enc_b32(dat_itm);
  if (fmt_clv === 'uuid') {
    if (dat_itm.length !== 16) throw new RangeError('UUID requires 16 bytes');
    dat_itm = dat_itm.slice(); dat_itm[6] = (dat_itm[6] & 15) | 64; dat_itm[8] = (dat_itm[8] & 63) | 128;
    const txt_val = fmt_sec(dat_itm, 'hex');
    return [txt_val.slice(0,8),txt_val.slice(8,12),txt_val.slice(12,16),txt_val.slice(16,20),txt_val.slice(20)].join('-');
  }
  throw new Error('Unknown format');
}
function enc_u32(cnt_tot) {
  const dat_itm = new Uint8Array(4); new DataView(dat_itm.buffer).setUint32(0, cnt_tot); return dat_itm;
}
function enc_str(dat_itm) {
  if (typeof dat_itm === 'string') dat_itm = sys_enc.encode(dat_itm);
  return cat_oct(enc_u32(dat_itm.length), dat_itm);
}
function enc_int(dat_itm) {
  while (dat_itm.length > 1 && dat_itm[0] === 0) dat_itm = dat_itm.slice(1);
  return enc_str(dat_itm[0] & 128 ? cat_oct(new Uint8Array([0]), dat_itm) : dat_itm);
}
function enc_pem(txt_val, dat_itm) {
  return '-----BEGIN ' + txt_val + '-----\n' + enc_b64(dat_itm).match(/.{1,64}/g).join('\n') + '\n-----END ' + txt_val + '-----\n';
}
export async function crt_clv(tip_clv = 'ed25519', txt_cmt = 'kamala', dat_azr, cfg_apl = {active:()=>true}) {
  if (!['ed25519', 'rsa3072', 'rsa4096'].includes(tip_clv)) throw new Error('Unsupported key type');
  txt_cmt = txt_cmt.replace(/[\x00-\x1f\x7f]/g, ' ').trim().slice(0,64);
  let dat_clv;
  if (tip_clv === 'ed25519') {
    const dat_sec = rnd_oct(dat_azr,32);
    const dat_itm = sys_ncl.sign.keyPair.fromSeed(dat_sec);
    try {
      const dat_env = {kty:'OKP',crv:'Ed25519',x:fmt_sec(dat_itm.publicKey,'base64url'),ext:true};
      dat_clv = {
        privateKey:await crypto.subtle.importKey('jwk',{...dat_env,d:fmt_sec(dat_sec,'base64url')},'Ed25519',true,['sign']),
        publicKey:await crypto.subtle.importKey('jwk',dat_env,'Ed25519',true,['verify'])
      };
    } finally { dat_sec.fill(0); dat_itm.secretKey.fill(0); }
  } else {
    // Native generateKey cannot accept the shared source. Supply every RSA
    // candidate byte explicitly, then retain only imported native CryptoKeys.
    const sys_prn = {getBytesSync:cnt_tot=>{
      const dat_itm = rnd_oct(dat_azr,cnt_tot);
      const txt_val = String.fromCharCode(...dat_itm); dat_itm.fill(0); return txt_val;
    }};
    const sys_cfg = sys_rsa.createKeyPairGenerationState(Number(tip_clv.slice(3)),65537,{prng:sys_prn});
    const sys_ts = Date.now();
    while (!sys_rsa.stepKeyPairGenerationState(sys_cfg,10)) {
      if (!cfg_apl.active()) throw new Error('Generation canceled');
      if (Date.now()-sys_ts > 120000) throw new Error('RSA generation timed out');
      await new Promise(dat_itm=>setTimeout(dat_itm,0));
    }
    const dat_env = {kty:'RSA',ext:true};
    for (const [txt_val,txt_cmt] of Object.entries({n:'n',e:'e',d:'d',p:'p',q:'q',dp:'dP',dq:'dQ',qi:'qInv'})) {
      let txt_pub = sys_cfg.keys.privateKey[txt_cmt].toString(16);
      if (txt_pub.length % 2) txt_pub = '0'+txt_pub;
      dat_env[txt_val] = fmt_sec(dec_hex(txt_pub),'base64url');
    }
    const sys_enc = {name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'};
    dat_clv = {
      privateKey:await crypto.subtle.importKey('jwk',dat_env,sys_enc,true,['sign']),
      publicKey:await crypto.subtle.importKey('jwk',{kty:'RSA',n:dat_env.n,e:dat_env.e,ext:true},sys_enc,true,['verify'])
    };
  }
  const dat_env = await crypto.subtle.exportKey('jwk', dat_clv.publicKey);
  const dat_itm = tip_clv === 'ed25519'
    ? cat_oct(enc_str('ssh-ed25519'), enc_str(dec_b64(dat_env.x)))
    : cat_oct(enc_str('ssh-rsa'), enc_int(dec_b64(dat_env.e)), enc_int(dec_b64(dat_env.n)));
  return { prv:dat_clv.privateKey, pub:dat_clv.publicKey, wire:dat_itm, tip:tip_clv, cmt:txt_cmt, azr:dat_azr,
    ssh:(tip_clv === 'ed25519' ? 'ssh-ed25519 ' : 'ssh-rsa ') + enc_b64(dat_itm) + (txt_cmt ? ' ' + txt_cmt : ''),
    fp:'SHA256:' + enc_b64(new Uint8Array(await crypto.subtle.digest('SHA-256', dat_itm))).replace(/=+$/, '') };
}
export async function exp_pub(dat_clv, fmt_clv) {
  if (fmt_clv === 'ssh') return dat_clv.ssh + '\n';
  if (fmt_clv === 'pem') return enc_pem('PUBLIC KEY', new Uint8Array(await crypto.subtle.exportKey('spki', dat_clv.pub)));
  if (fmt_clv === 'jwk') return JSON.stringify(await crypto.subtle.exportKey('jwk', dat_clv.pub), null, 2) + '\n';
  throw new Error('Unknown public format');
}
async function enc_ssh(dat_clv, txt_pss) {
  const dat_env = await crypto.subtle.exportKey('jwk', dat_clv.prv);
  const dat_mst = rnd_oct(dat_clv.azr,4);
  let dat_itm = cat_oct(dat_mst, dat_mst);
  if (dat_clv.tip === 'ed25519') {
    const dat_sec = dec_b64(dat_env.d);
    dat_itm = cat_oct(dat_itm, enc_str('ssh-ed25519'), enc_str(dec_b64(dat_env.x)), enc_str(cat_oct(dat_sec, dec_b64(dat_env.x))));
    dat_sec.fill(0);
  } else {
    dat_itm = cat_oct(dat_itm, enc_str('ssh-rsa'), ...['n','e','d','qi','p','q'].map(txt_val => enc_int(dec_b64(dat_env[txt_val]))));
  }
  dat_itm = cat_oct(dat_itm, enc_str(dat_clv.cmt));
  const cnt_tot = txt_pss ? 16 : 8;
  dat_itm = cat_oct(dat_itm, Uint8Array.from({length:(cnt_tot - dat_itm.length % cnt_tot) % cnt_tot}, (dat_itm, sys_idx) => sys_idx + 1));
  let dat_par = new Uint8Array();
  if (txt_pss) {
    const dat_sec = rnd_oct(dat_clv.azr,16), dat_azr = new Uint8Array(48), txt_val = sys_enc.encode(txt_pss);
    try {
      if (sys_kdf.pbkdf(txt_val, txt_val.length, dat_sec, dat_sec.length, dat_azr, 48, 64) !== 0) throw new Error('Key protection failed');
      const sys_cfg = await crypto.subtle.importKey('raw', dat_azr.slice(0,32), {name:'AES-CTR'}, false, ['encrypt']);
      dat_par = cat_oct(enc_str(dat_sec), enc_u32(64));
      const dat_dst = new Uint8Array(await crypto.subtle.encrypt({name:'AES-CTR', counter:dat_azr.slice(32), length:128}, sys_cfg, dat_itm));
      dat_itm.fill(0); dat_itm = dat_dst;
    } finally { dat_azr.fill(0); txt_val.fill(0); }
  }
  const txt_pub = enc_pem('OPENSSH PRIVATE KEY', cat_oct(sys_enc.encode('openssh-key-v1\x00'), enc_str(txt_pss ? 'aes256-ctr' : 'none'), enc_str(txt_pss ? 'bcrypt' : 'none'), enc_str(dat_par), enc_u32(1), enc_str(dat_clv.wire), enc_str(dat_itm)));
  dat_itm.fill(0);
  return txt_pub;
}
function dec_hex(txt_val) { return Uint8Array.from(txt_val.match(/../g), txt_val => parseInt(txt_val,16)); }
function enc_der(cnt_tot, ...dat_env) {
  const dat_itm = cat_oct(...dat_env);
  let dat_par = new Uint8Array([dat_itm.length]);
  if (dat_itm.length >= 128) {
    const txt_val = dat_itm.length.toString(16).padStart(Math.ceil(dat_itm.length.toString(16).length / 2) * 2,'0');
    dat_par = cat_oct(new Uint8Array([128 + txt_val.length / 2]), dec_hex(txt_val));
  }
  return cat_oct(new Uint8Array([cnt_tot]), dat_par, dat_itm);
}
function der_int(cnt_tot) {
  let txt_val = cnt_tot.toString(16); if (txt_val.length % 2) txt_val = '0' + txt_val;
  let dat_itm = dec_hex(txt_val); if (dat_itm[0] & 128) dat_itm = cat_oct(new Uint8Array([0]), dat_itm);
  return enc_der(2, dat_itm);
}
async function enc_p8(dat_clv, txt_pss) {
  const dat_itm = new Uint8Array(await crypto.subtle.exportKey('pkcs8', dat_clv.prv));
  try {
    if (!txt_pss) return enc_pem('PRIVATE KEY', dat_itm);
    const dat_sec = rnd_oct(dat_clv.azr,16), dat_par = rnd_oct(dat_clv.azr,16), txt_val = sys_enc.encode(txt_pss);
    const sys_kdf = await crypto.subtle.importKey('raw', txt_val, 'PBKDF2', false, ['deriveKey']);
    txt_val.fill(0);
    const sys_cfg = await crypto.subtle.deriveKey({name:'PBKDF2', salt:dat_sec, iterations:600000, hash:'SHA-256'}, sys_kdf, {name:'AES-CBC', length:256}, false, ['encrypt']);
    const dat_dst = new Uint8Array(await crypto.subtle.encrypt({name:'AES-CBC', iv:dat_par}, sys_cfg, dat_itm));
    // RFC 8018 PBES2 / PBKDF2-SHA256 / AES-256-CBC, wrapped as EncryptedPrivateKeyInfo.
    return enc_pem('ENCRYPTED PRIVATE KEY', enc_der(48,
      enc_der(48, dec_hex('06092a864886f70d01050d'), enc_der(48,
        enc_der(48, dec_hex('06092a864886f70d01050c'), enc_der(48, enc_der(4,dat_sec), der_int(600000), enc_der(48,dec_hex('06082a864886f70d0209'),enc_der(5)))),
        enc_der(48, dec_hex('060960864801650304012a'), enc_der(4,dat_par)))), enc_der(4,dat_dst)));
  } finally { dat_itm.fill(0); }
}
export async function exp_clv(dat_clv, fmt_clv = 'openssh', txt_pss = '') {
  if (txt_pss && txt_pss.length < 12) throw new Error('Use a passphrase of at least 12 characters.');
  if (fmt_clv === 'openssh') return enc_ssh(dat_clv, txt_pss);
  if (fmt_clv === 'pkcs8') return enc_p8(dat_clv, txt_pss);
  throw new Error('Unknown private format');
}
export async function crt_otp(dat_sec, sys_ts = Date.now() / 1000, cnt_tot = 6) {
  if (![6,8].includes(cnt_tot) || !Number.isFinite(sys_ts) || sys_ts < 0) throw new RangeError('Invalid TOTP parameters');
  const dat_itm = new Uint8Array(8); new DataView(dat_itm.buffer).setBigUint64(0, BigInt(Math.floor(sys_ts / 30)));
  const sys_cfg = await crypto.subtle.importKey('raw', dat_sec, {name:'HMAC', hash:'SHA-1'}, false, ['sign']);
  const dat_env = new Uint8Array(await crypto.subtle.sign('HMAC', sys_cfg, dat_itm));
  const sys_idx = dat_env[dat_env.length - 1] & 15;
  return ((new DataView(dat_env.buffer).getUint32(sys_idx) & 0x7fffffff) % (10 ** cnt_tot)).toString().padStart(cnt_tot,'0');
}
export function url_otp(dat_sec, txt_cmt, txt_val) {
  if (!txt_cmt.trim() || !txt_val.trim()) throw new Error('Enter an issuer and an account label.');
  return 'otpauth://totp/' + encodeURIComponent(txt_cmt.trim()) + ':' + encodeURIComponent(txt_val.trim()) + '?secret=' + enc_b32(dat_sec) + '&issuer=' + encodeURIComponent(txt_cmt.trim()) + '&algorithm=SHA1&digits=6&period=30';
}
