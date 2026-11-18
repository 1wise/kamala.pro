#!/usr/bin/env python3
# Timestamp: 2026-11-07
# Version: 3.1.1
# Author & Credits: https://www.alawise.es/1-s
"""Update the existing Camera 4 collector and embedded instrument with backups."""

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import os
from pathlib import Path
import pwd
import re
import shutil
import subprocess
import sys
import tempfile

pth_src = Path(__file__).resolve().parent
txt_usr = "kamala-pendulum"
txt_ser = "kamala-pendulum.service"


class PndDivParser(HTMLParser):
    """Locate the instrument without rewriting surrounding site content."""

    def __init__(self, txt_htm):
        super().__init__(convert_charrefs=False)
        self.txt_htm = txt_htm
        self.dat_lin = [0]
        for txt_lin in txt_htm.splitlines(keepends=True):
            self.dat_lin.append(self.dat_lin[-1] + len(txt_lin))
        self.cnt_div = 0
        self.cnt_pnd = 0
        self.pos_ini = self.pos_fin = None
        self.feed(txt_htm)
        self.close()
        if self.cnt_pnd != 1 or self.pos_fin is None:
            raise ValueError("Each page must contain one complete data-pendulum div. Install Kamala 2.3.0 first.")

    def pos_act(self):
        idx_lin, idx_col = self.getpos()
        return self.dat_lin[idx_lin - 1] + idx_col

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return
        if "data-pendulum" in dict(attrs):
            self.cnt_pnd += 1
            if self.pos_ini is None:
                self.pos_ini = self.pos_act()
                self.cnt_div = 1
                return
        if self.pos_ini is not None and self.pos_fin is None:
            self.cnt_div += 1

    def handle_endtag(self, tag):
        if tag == "div" and self.pos_ini is not None and self.pos_fin is None:
            self.cnt_div -= 1
            if self.cnt_div == 0:
                self.pos_fin = self.txt_htm.index(">", self.pos_act()) + 1


def parchea_html(txt_htm, txt_pnd):
    obj_htm = PndDivParser(txt_htm)
    obj_pnd = PndDivParser(txt_pnd)
    txt_nvo = (txt_htm[:obj_htm.pos_ini] +
               txt_pnd[obj_pnd.pos_ini:obj_pnd.pos_fin] + txt_htm[obj_htm.pos_fin:])
    # Change only the instrument's cache keys; keep menus, metadata and other apps.
    pat_ast = r"((?:href|src)=[\"']/pendulum(?:\.css|\.mjs))(?:\?[^\"']*)?([\"'])"
    txt_nvo, cnt_ast = re.subn(pat_ast, r"\g<1>?v=3.1.1\g<2>", txt_nvo)
    if cnt_ast != 2:
        raise ValueError("The existing page must load pendulum.css and pendulum.mjs exactly once.")
    return txt_nvo


def val_pth(pth_fil):
    pth_fil = Path(pth_fil).absolute()
    if not re.fullmatch(r"/[A-Za-z0-9_./-]+", str(pth_fil)) or pth_fil.resolve() != pth_fil:
        raise ValueError("Use a normalized absolute path without symbolic links.")
    return pth_fil


def prepara(pth_rad):
    pth_rad = val_pth(pth_rad)
    if not pth_rad.is_dir() or not (pth_rad / "index.html").is_file():
        raise ValueError("--root must be the existing site HTML directory.")
    dat_plan = []
    for txt_nom in ("pendulum_feed.py", txt_ser, "kamala-pendulum.env", "web/pendulum.mjs",
                    "web/pendulum-core.mjs", "web/pendulum.css", "web/pendulum-main.html", "web/pendulum-live.html"):
        pth_fil = pth_src / txt_nom
        if not pth_fil.is_file() or pth_fil.is_symlink():
            raise ValueError("The update package is incomplete.")
    for txt_pag, txt_mod in (("techniques/pendulum/index.html", "pendulum-main.html"),
                             ("techniques/pendulum/live/index.html", "pendulum-live.html")):
        pth_pag = val_pth(pth_rad / txt_pag)
        txt_htm = parchea_html(pth_pag.read_text(), (pth_src / "web" / txt_mod).read_text())
        dat_plan.append((pth_pag, txt_htm, 0o644))
    for txt_nom in ("pendulum.mjs", "pendulum-core.mjs", "pendulum.css"):
        dat_plan.append((val_pth(pth_rad / txt_nom), (pth_src / "web" / txt_nom).read_text(), 0o644))
    dat_plan.append((val_pth("/usr/local/libexec/kamala/pendulum_feed.py"),
                     (pth_src / "pendulum_feed.py").read_text(), 0o644))
    pth_tel = val_pth(pth_rad / "telemetry-pendulum")
    txt_uni = (pth_src / txt_ser).read_text().replace(
        "/var/www/kamala.pro/html/telemetry-pendulum", str(pth_tel))
    dat_plan.append((val_pth(Path("/etc/systemd/system") / txt_ser), txt_uni, 0o644))
    pth_env = val_pth("/etc/sysconfig/kamala-pendulum")
    if not pth_env.exists():
        dat_plan.append((pth_env, (pth_src / "kamala-pendulum.env").read_text(), 0o640))
    for pth_fil, _, _ in dat_plan:
        if pth_fil.exists() and not pth_fil.is_file():
            raise ValueError("An installation target is not a regular file.")
    if pth_tel.exists():
        if not pth_tel.is_dir() or pth_tel.stat().st_mode & 0o022:
            raise ValueError("The dedicated feed directory has unsafe permissions.")
        try:
            cnt_uid = pwd.getpwnam(txt_usr).pw_uid
        except KeyError:
            cnt_uid = 0
        if pth_tel.stat().st_uid not in (0, cnt_uid):
            raise ValueError("The dedicated feed directory belongs to another account.")
        for pth_fil in pth_tel.iterdir():
            if pth_fil.is_symlink() or not pth_fil.is_file() or not (
                    pth_fil.name == "state.json" or pth_fil.name.startswith(".pendulum-")):
                raise ValueError("The feed directory contains unrelated files.")
    return pth_rad, dat_plan


def instala(pth_rad):
    if os.geteuid() != 0:
        raise PermissionError("Run --install as root.")
    pth_rad, dat_plan = prepara(pth_rad)
    try:
        dat_usr = pwd.getpwnam(txt_usr)
        if dat_usr.pw_uid == 0 or dat_usr.pw_shell not in ("/usr/sbin/nologin", "/sbin/nologin", "/bin/false"):
            raise ValueError("The existing account is not a dedicated service account.")
    except KeyError:
        subprocess.run(["useradd", "--system", "--user-group", "--no-create-home",
                        "--home-dir", "/", "--shell", "/usr/sbin/nologin", txt_usr], check=True)
        dat_usr = pwd.getpwnam(txt_usr)
    pth_tel = pth_rad / "telemetry-pendulum"
    pth_tel.mkdir(mode=0o755, exist_ok=True)
    os.chown(pth_tel, dat_usr.pw_uid, dat_usr.pw_gid)
    os.chmod(pth_tel, 0o755)
    pth_bak = Path("/var/backups/kamala-pendulum") / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    pth_bak.mkdir(mode=0o700, parents=True)
    for pth_fil, txt_val, cnt_mod in dat_plan:
        pth_fil.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        if pth_fil.exists():
            pth_ant = pth_bak / pth_fil.relative_to("/")
            pth_ant.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pth_fil, pth_ant)
        pth_tmp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=pth_fil.parent,
                                             prefix=".pendulum-install-", delete=False) as sys_fil:
                pth_tmp = Path(sys_fil.name)
                sys_fil.write(txt_val)
                sys_fil.flush()
                os.fchown(sys_fil.fileno(), 0, 0)
                os.fchmod(sys_fil.fileno(), cnt_mod)
            os.replace(pth_tmp, pth_fil)
        finally:
            if pth_tmp is not None and pth_tmp.exists():
                pth_tmp.unlink()
    if shutil.which("restorecon"):
        subprocess.run(["restorecon", "-R", str(pth_tel)], check=True)
        subprocess.run(["restorecon", *[str(pth_fil) for pth_fil, _, _ in dat_plan]], check=True)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    print("Collector and instrument updated. Existing source URL was retained.")
    print("Backup: " + str(pth_bak))
    print("Load the update: sudo systemctl restart " + txt_ser)


if __name__ == "__main__":
    sys_cfg = argparse.ArgumentParser(description=__doc__)
    sys_cfg.add_argument("--root", type=Path, default=Path("/var/www/kamala.pro/html"))
    sys_cfg.add_argument("--install", action="store_true")
    try:
        cfg_apl = sys_cfg.parse_args()
        if cfg_apl.install:
            instala(cfg_apl.root)
        else:
            _, dat_plan = prepara(cfg_apl.root)
            print("Dry run: no files or accounts changed.")
            for pth_fil, _, _ in dat_plan:
                print("Update: " + str(pth_fil))
            print("The existing environment file, source counter and camera daemon are retained.")
    except (OSError, ValueError, subprocess.SubprocessError) as sys_err:
        print("Installation stopped: " + str(sys_err), file=sys.stderr)
        sys.exit(1)
