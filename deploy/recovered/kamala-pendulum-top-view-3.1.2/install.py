#!/usr/bin/env python3
# Timestamp: 2026-11-07
# Version: 3.1.2
# Author & Credits: https://www.alawise.es/1-s
"""Install the overhead XZ instrument while preserving the existing collector."""

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

pth_src = Path(__file__).resolve().parent


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
    txt_nvo, cnt_ast = re.subn(pat_ast, r"\g<1>?v=3.1.2\g<2>", txt_nvo)
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
    for txt_nom in ("pendulum.mjs", "pendulum-core.mjs", "pendulum.css", "pendulum-main.html", "pendulum-live.html"):
        pth_fil = pth_src / "web" / txt_nom
        if not pth_fil.is_file() or pth_fil.is_symlink():
            raise ValueError("The web update package is incomplete.")
    dat_plan = []
    for txt_pag, txt_mod in (("techniques/pendulum/index.html", "pendulum-main.html"),
                             ("techniques/pendulum/live/index.html", "pendulum-live.html")):
        pth_pag = val_pth(pth_rad / txt_pag)
        txt_htm = parchea_html(pth_pag.read_text(), (pth_src / "web" / txt_mod).read_text())
        dat_plan.append((pth_pag, txt_htm))
    for txt_nom in ("pendulum.mjs", "pendulum-core.mjs", "pendulum.css"):
        dat_plan.append((val_pth(pth_rad / txt_nom), (pth_src / "web" / txt_nom).read_text()))
    for pth_fil, _ in dat_plan:
        if pth_fil.exists() and not pth_fil.is_file():
            raise ValueError("An installation target is not a regular file.")
    return dat_plan


def instala(pth_rad):
    if os.geteuid() != 0:
        raise PermissionError("Run --install as root.")
    dat_plan = prepara(pth_rad)
    pth_bak = Path("/var/backups/kamala-pendulum-web") / datetime.now(timezone.utc).strftime("3.1.2-%Y%m%d-%H%M%S-%f")
    pth_bak.mkdir(mode=0o700, parents=True)
    for pth_fil, txt_val in dat_plan:
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
                os.fchmod(sys_fil.fileno(), 0o644)
            os.replace(pth_tmp, pth_fil)
        finally:
            if pth_tmp is not None and pth_tmp.exists():
                pth_tmp.unlink()
    if shutil.which("restorecon"):
        subprocess.run(["restorecon", *[str(pth_fil) for pth_fil, _ in dat_plan]], check=True)
    print("Top view XZ installed in both pendulum pages.")
    print("Backup: " + str(pth_bak))
    print("Reload the page to load the new instrument.")


if __name__ == "__main__":
    sys_cfg = argparse.ArgumentParser(description=__doc__)
    sys_cfg.add_argument("--root", type=Path, default=Path("/var/www/kamala.pro/html"))
    sys_cfg.add_argument("--install", action="store_true")
    try:
        cfg_apl = sys_cfg.parse_args()
        if cfg_apl.install:
            instala(cfg_apl.root)
        else:
            dat_plan = prepara(cfg_apl.root)
            print("Dry run: no files changed.")
            for pth_fil, _ in dat_plan:
                print("Update: " + str(pth_fil))
            print("Only the web instrument is updated.")
    except (OSError, ValueError, subprocess.SubprocessError) as sys_err:
        print("Installation stopped: " + str(sys_err), file=sys.stderr)
        sys.exit(1)

