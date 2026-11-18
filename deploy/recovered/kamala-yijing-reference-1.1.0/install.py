#!/usr/bin/env python3
# Timestamp: 2026-11-07
# Version: 1.1.0
# Author & Credits: https://www.alawise.es/1-s
"""Show brief Zhouyi readings with their original Chinese after a completed cast."""

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

TXT_REF = ('<a class="text-link" data-iching-reference hidden '
           'href="https://ctext.org/book-of-changes" target="_blank" '
           'rel="noopener noreferrer">Read the Book of Changes — Chinese Text Project ↗</a>')
TXT_MOD = '<script type="module" src="/yijing-reference.mjs?v=1.1.0"></script>'
TXT_CSS = '<link rel="stylesheet" href="/yijing-readings.css?v=1.1.0">'
FIL_APP = ("yijing-reference.mjs", "yijing-readings.mjs", "yijing-readings.css")
PAG_APP = ("apps/coins/index.html", "apps/yijing/index.html",
           "techniques/coins/index.html", "techniques/yijing/index.html")


class RefParser(HTMLParser):
    """Match the cast's reference while preserving static article citations."""

    def __init__(self, txt_htm):
        super().__init__(convert_charrefs=False)
        self.txt_htm = txt_htm
        self.dat_lin = [0]
        for txt_lin in txt_htm.splitlines(keepends=True):
            self.dat_lin.append(self.dat_lin[-1] + len(txt_lin))
        self.cnt_sec = 0
        self.pos_ref = None
        self.dat_pos = []
        self.feed(txt_htm)
        self.close()

    def pos_act(self):
        idx_lin, idx_col = self.getpos()
        return self.dat_lin[idx_lin - 1] + idx_col

    def handle_starttag(self, tag, attrs):
        dat_atr = dict(attrs)
        if tag == "section":
            if self.cnt_sec:
                self.cnt_sec += 1
            elif "data-iching" in dat_atr:
                self.cnt_sec = 1
        if tag == "a" and self.cnt_sec and dat_atr.get("href", "").rstrip("/") == "https://ctext.org/book-of-changes":
            self.pos_ref = self.pos_act()

    def handle_endtag(self, tag):
        if tag == "a" and self.pos_ref is not None:
            self.dat_pos.append((self.pos_ref, self.txt_htm.index(">", self.pos_act()) + 1))
            self.pos_ref = None
        if tag == "section" and self.cnt_sec:
            self.cnt_sec -= 1


def parchea_html(txt_htm):
    obj_htm = RefParser(txt_htm)
    if len(obj_htm.dat_pos) != 1:
        raise ValueError("Expected one Book of Changes reference inside the I Ching cast.")
    pos_ini, pos_fin = obj_htm.dat_pos[0]
    txt_nvo = txt_htm[:pos_ini] + TXT_REF + txt_htm[pos_fin:]
    pat_mod = r'<script\b[^>]*\bsrc=[\"\']/yijing-reference\.mjs(?:\?[^\"\']*)?[\"\'][^>]*>\s*</script>'
    txt_nvo, cnt_mod = re.subn(pat_mod, TXT_MOD, txt_nvo)
    if cnt_mod > 1:
        raise ValueError("The page has duplicate reference modules.")
    if cnt_mod == 0:
        if txt_nvo.lower().count("</body>") != 1:
            raise ValueError("The page needs one closing body tag.")
        txt_nvo = re.sub(r"</body>", TXT_MOD + "</body>", txt_nvo, flags=re.IGNORECASE)
    pat_css = r'<link\b[^>]*\bhref=[\"\']/yijing-readings\.css(?:\?[^\"\']*)?[\"\'][^>]*>'
    txt_nvo, cnt_css = re.subn(pat_css, TXT_CSS, txt_nvo)
    if cnt_css > 1:
        raise ValueError("The page has duplicate reading stylesheets.")
    if cnt_css == 0:
        if txt_nvo.lower().count("</head>") != 1:
            raise ValueError("The page needs one closing head tag.")
        txt_nvo = re.sub(r"</head>", TXT_CSS + "</head>", txt_nvo, flags=re.IGNORECASE)
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
    for txt_pag in PAG_APP:
        pth_pag = val_pth(pth_rad / txt_pag)
        dat_plan.append((pth_pag, parchea_html(pth_pag.read_text(encoding="utf-8"))))
    for txt_nom in FIL_APP:
        pth_mod = pth_src / txt_nom
        if not pth_mod.is_file() or pth_mod.is_symlink():
            raise ValueError("A reading asset is missing: " + txt_nom)
        dat_plan.append((val_pth(pth_rad / txt_nom), pth_mod.read_text(encoding="utf-8")))
    for pth_fil, _ in dat_plan:
        if pth_fil.exists() and not pth_fil.is_file():
            raise ValueError("An installation target is not a regular file.")
    return dat_plan


def instala(pth_rad):
    if os.geteuid() != 0:
        raise PermissionError("Run --install as root.")
    dat_plan = prepara(pth_rad)
    pth_bak = Path("/var/backups/kamala-yijing-reference") / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    pth_bak.mkdir(mode=0o700, parents=True)
    for pth_fil, txt_val in dat_plan:
        if pth_fil.exists():
            pth_ant = pth_bak / pth_fil.relative_to("/")
            pth_ant.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pth_fil, pth_ant)
        pth_tmp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=pth_fil.parent,
                                             prefix=".yijing-reference-", delete=False) as sys_fil:
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
    print("Installed 1.1.0: brief readings and classical Chinese for all 64 hexagrams.")
    print("Site root: " + str(val_pth(pth_rad)))
    print("Backup: " + str(pth_bak))
    print("Reload the coin and I Ching pages.")


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
    except (OSError, ValueError, subprocess.SubprocessError) as sys_err:
        print("Installation stopped: " + str(sys_err), file=sys.stderr)
        sys.exit(1)

