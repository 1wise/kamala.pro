// Timestamp: 2026-10-29
// Version: 1.10.0
// Author & Credits: https://www.alawise.es/1-s
// Test keys are temporary fixtures, never installed as authentication credentials.
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { crt_clv, exp_pub, exp_clv, fmt_sec, enc_b32, crt_otp, url_otp, rnd_sys } from '../src/lab/keys-core.mjs';
import { crt_azr } from '../src/entropy-core.mjs';
const pth_dst = await mkdtemp(join(tmpdir(),'kamala-key-test-'));
try {
  for (const tip_clv of ['ed25519','rsa3072','rsa4096']) {
    const dat_azr = await crt_azr('browser');
    const dat_env = {cnt:0};
    dat_azr.seed = new Proxy(dat_azr.seed,{get:(dat_itm,txt_val)=>{
      if (typeof txt_val === 'string' && /^\d+$/.test(txt_val)) dat_env.cnt++;
      return Reflect.get(dat_itm,txt_val,dat_itm);
    }});
    const dat_clv = await crt_clv(tip_clv,'fixture\ninjection',dat_azr);
    assert.ok(dat_env.cnt > 0, tip_clv + ' must consume the shared entropy seed');
    assert.ok(!dat_clv.ssh.includes('\n'));
    const txt_pub = await exp_pub(dat_clv,'ssh');
    const pth_fil = join(pth_dst,'fixture.pub');
    await writeFile(pth_fil,txt_pub,{mode:0o600});
    assert.ok(execFileSync('ssh-keygen',['-lf',pth_fil,'-E','sha256'],{encoding:'utf8'}).includes(dat_clv.fp));
    assert.ok(!(await exp_pub(dat_clv,'jwk')).includes('"d"'));
    for (const fmt_clv of ['openssh','pkcs8']) {
      for (const txt_pss of ['', 'fixture-only passphrase 123']) {
        const txt_val = await exp_clv(dat_clv,fmt_clv,txt_pss);
        const pth_src = join(pth_dst,'fixture.key');
        await writeFile(pth_src,txt_val,{mode:0o600});
        if (fmt_clv === 'openssh') {
          const txt_pub = execFileSync('ssh-keygen',['-y','-P',txt_pss,'-f',pth_src],{encoding:'utf8'}).trim().split(/\s+/).slice(0,2).join(' ');
          assert.equal(txt_pub,dat_clv.ssh.split(/\s+/).slice(0,2).join(' '));
          if (!txt_pss) {
            const pth_adj = join(pth_dst,tip_clv+'.txt');
            const txt_msj = 'Kamala interoperability fixture\n';
            await writeFile(pth_adj,txt_msj,{mode:0o600});
            await writeFile(join(pth_dst,'allowed-signers'),'fixture '+dat_clv.ssh+'\n',{mode:0o600});
            execFileSync('ssh-keygen',['-Y','sign','-f',pth_src,'-n','kamala-test',pth_adj],{stdio:'pipe'});
            assert.match(execFileSync('ssh-keygen',['-Y','verify','-f',join(pth_dst,'allowed-signers'),'-I','fixture','-n','kamala-test','-s',pth_adj+'.sig'],{input:txt_msj,encoding:'utf8',stdio:'pipe'}),/Good/);
          }
          if (txt_pss) assert.throws(()=>execFileSync('ssh-keygen',['-y','-P','wrong-fixture-password','-f',pth_src],{stdio:'pipe'}));
        } else {
          const txt_pub = execFileSync('openssl',['pkey','-in',pth_src,'-passin','pass:'+txt_pss,'-pubout'],{encoding:'utf8'});
          assert.equal(txt_pub,await exp_pub(dat_clv,'pem'));
          if (txt_pss) assert.throws(()=>execFileSync('openssl',['pkey','-in',pth_src,'-passin','pass:wrong-fixture-password','-pubout'],{stdio:'pipe'}));
        }
      }
    }
    console.log(tip_clv + ': OpenSSH and OpenSSL import, encrypted/unencrypted, fingerprints and public formats passed.');
  }
  const dat_sec = new TextEncoder().encode('12345678901234567890');
  for (const [sys_ts,txt_val] of [[59,'94287082'],[1111111109,'07081804'],[1111111111,'14050471'],[1234567890,'89005924'],[2000000000,'69279037'],[20000000000,'65353130']]) assert.equal(await crt_otp(dat_sec,sys_ts,8),txt_val);
  assert.equal(enc_b32(new TextEncoder().encode('foobar')),'MZXW6YTBOI');
  assert.equal(fmt_sec(new Uint8Array([255,0,1]),'hex'),'ff0001');
  assert.equal(fmt_sec(new Uint8Array([255,0,1]),'base64'),'/wAB');
  assert.equal(fmt_sec(new Uint8Array([255,0,1]),'base64url'),'_wAB');
  assert.match(fmt_sec(rnd_sys(16),'uuid'),/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  assert.match(url_otp(dat_sec,'Issuer / test','name@test.invalid'),/^otpauth:\/\/totp\/Issuer%20%2F%20test:name%40test.invalid\?secret=/);
  assert.throws(()=>rnd_sys(0));
  await assert.rejects(()=>crt_clv('invalid'));
  console.log('Secret encodings, UUID version/variant and all RFC6238 SHA1 test vectors passed.');
} finally { await rm(pth_dst,{recursive:true,force:true}); }
