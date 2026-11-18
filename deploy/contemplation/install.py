#!/usr/bin/env python3
# Timestamp: 2026-11-01
# Version: 2.1.0
# Author & Credits: https://www.alawise.es/1-s
"""Review or install the optional Excalibur contemplation collector."""

import argparse
import datetime
import grp
import os
from pathlib import Path
import pwd
import re
import shutil
import stat
import subprocess
import sys


pth_src = Path(__file__).resolve().parent
txt_usr = "kamala-flow"
txt_ser = "kamala-contemplation.service"


def val_pth(pth_dst):
    pth_dst = Path(pth_dst).absolute()
    if not re.fullmatch(r"/[A-Za-z0-9_./-]+", str(pth_dst)):
        raise ValueError("Use an absolute ASCII path without whitespace or shell syntax.")
    if any(txt_val in (".", "..") for txt_val in pth_dst.parts):
        raise ValueError("Use a normalized installation path.")
    if pth_dst.resolve() != pth_dst:
        raise ValueError("Installation paths must not contain symbolic links.")
    return pth_dst


def valida(pth_rad):
    pth_rad = val_pth(pth_rad)
    if not pth_rad.is_dir() or not (pth_rad / "index.html").is_file():
        raise ValueError("--root must be an existing site HTML directory.")
    for txt_nom in (
        "contemplation_feed.py", "kamala-contemplation.service",
        "kamala-contemplation.env"
    ):
        if not (pth_src / txt_nom).is_file() or (pth_src / txt_nom).is_symlink():
            raise ValueError("The collector package is incomplete.")
    pth_tel = val_pth(pth_rad / "telemetry")
    if pth_tel.exists():
        if not pth_tel.is_dir():
            raise ValueError("The telemetry path must be a dedicated directory.")
        if pth_tel.stat().st_mode & 0o022:
            raise ValueError("The telemetry directory must not be group/world writable.")
        for pth_fil in pth_tel.iterdir():
            if pth_fil.name != "contemplation.json" or pth_fil.is_symlink() or not pth_fil.is_file():
                raise ValueError("The existing telemetry directory contains other files.")
        if pth_tel.stat().st_uid != 0:
            try:
                cnt_uid = pwd.getpwnam(txt_usr).pw_uid
            except KeyError:
                raise ValueError("The telemetry directory belongs to another account.") from None
            if pth_tel.stat().st_uid != cnt_uid:
                raise ValueError("The telemetry directory belongs to another account.")
    for pth_fil in (
        Path("/usr/local/libexec/kamala/contemplation_feed.py"),
        Path("/etc/systemd/system") / txt_ser,
        Path("/etc/sysconfig/kamala-contemplation"),
    ):
        val_pth(pth_fil)
        if pth_fil.exists() and not pth_fil.is_file():
            raise ValueError("An installation target is not a regular file.")
    return pth_rad


def crt_usr():
    grp.getgrnam("systemd-journal")
    try:
        dat_usr = pwd.getpwnam(txt_usr)
        if dat_usr.pw_uid == 0 or dat_usr.pw_shell not in ("/usr/sbin/nologin", "/sbin/nologin", "/bin/false"):
            raise ValueError("An existing kamala-flow account is not a service account.")
        return dat_usr
    except KeyError:
        # This dedicated user may read journals but receives no login or root role.
        subprocess.run([
            "/usr/sbin/useradd", "--system", "--user-group", "--no-create-home",
            "--home-dir", "/", "--shell", "/usr/sbin/nologin", txt_usr
        ], check=True)
        return pwd.getpwnam(txt_usr)


def instala(pth_rad):
    if os.geteuid() != 0:
        raise PermissionError("Run --install as root after reviewing the dry run.")
    pth_rad = valida(pth_rad)
    dat_usr = crt_usr()
    pth_tel = pth_rad / "telemetry"
    if pth_tel.exists() and pth_tel.stat().st_uid not in (0, dat_usr.pw_uid):
        raise ValueError("The telemetry directory belongs to another account.")
    pth_tel.mkdir(mode=0o755, exist_ok=True)
    os.chown(pth_tel, dat_usr.pw_uid, dat_usr.pw_gid)
    os.chmod(pth_tel, 0o755)
    pth_bak = val_pth(Path("/var/backups/kamala-contemplation") /
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S-%f"))
    pth_bak.mkdir(mode=0o700, parents=True)

    def cpy_fil(pth_fil, txt_val, cnt_mod):
        pth_fil = val_pth(pth_fil)
        pth_fil.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        if pth_fil.exists():
            shutil.copy2(pth_fil, pth_bak / pth_fil.name)
        pth_fil.write_text(txt_val)
        os.chown(pth_fil, 0, 0)
        os.chmod(pth_fil, cnt_mod)

    cpy_fil(
        Path("/usr/local/libexec/kamala/contemplation_feed.py"),
        (pth_src / "contemplation_feed.py").read_text(), 0o644
    )
    txt_uni = (pth_src / txt_ser).read_text().replace(
        "/var/www/kamala.pro/html/telemetry", str(pth_tel)
    )
    cpy_fil(Path("/etc/systemd/system") / txt_ser, txt_uni, 0o644)
    pth_env = Path("/etc/sysconfig/kamala-contemplation")
    if not pth_env.exists():
        cpy_fil(pth_env, (pth_src / "kamala-contemplation.env").read_text(), 0o640)
    # Existing environment settings and all web application configuration survive.
    if shutil.which("restorecon"):
        subprocess.run(["restorecon", "-R", str(pth_tel)], check=True)
        subprocess.run([
            "restorecon", "/usr/local/libexec/kamala/contemplation_feed.py",
            "/etc/systemd/system/" + txt_ser, str(pth_env)
        ], check=True)
    subprocess.run(["/usr/bin/systemctl", "daemon-reload"], check=True)
    print("Collector and unit installed. Existing environment settings were preserved.")
    print("Public feed directory: " + str(pth_tel))
    print("Backup: " + str(pth_bak))
    print("Start explicitly: sudo systemctl enable --now " + txt_ser)
    print("No service was started; no firewall or nginx settings were changed.")


def muestra(pth_rad):
    pth_rad = valida(pth_rad)
    print("Dry run: no files or accounts were changed.")
    print("Create/reuse the non-login kamala-flow service account.")
    print("Give the service systemd-journal membership only through its unit.")
    print("Install: /usr/local/libexec/kamala/contemplation_feed.py")
    print("Install: /etc/systemd/system/" + txt_ser)
    print("Create if absent: /etc/sysconfig/kamala-contemplation")
    print("Own only the dedicated feed directory: " + str(pth_rad / "telemetry"))
    print("Publish only aggregate JSON at /telemetry/contemplation.json.")
    print("Keep SELinux enforcing; restore normal installed-file labels.")
    print("Back up replaced collector/unit files in /var/backups/kamala-contemplation.")
    print("Reload systemd units. Starting the service is a separate explicit command.")
    print("No firewall rules, denied-logging settings, nginx settings or app credentials change.")


if __name__ == "__main__":
    sys_cfg = argparse.ArgumentParser(description=__doc__)
    sys_cfg.add_argument("--root", type=Path, default=Path("/var/www/kamala.pro/html"))
    sys_arg = sys_cfg.add_mutually_exclusive_group()
    sys_arg.add_argument("--install", action="store_true", help="Install reviewed files; do not start.")
    sys_arg.add_argument("--dry-run", action="store_true", help="Print changes without modifying anything.")
    cfg_apl = sys_cfg.parse_args()
    try:
        if cfg_apl.install:
            instala(cfg_apl.root)
        else:
            muestra(cfg_apl.root)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as sys_err:
        print("Installation stopped: " + str(sys_err), file=sys.stderr)
        sys.exit(1)
