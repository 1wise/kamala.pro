#!/usr/bin/env python3
# Timestamp: 2026-11-01
# Version: 2.1.0
# Author & Credits: https://www.alawise.es/1-s
"""Publish aggregate interface traffic and firewall activity, never raw logs."""

import argparse
import datetime
import grp
import json
import math
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import time
import uuid


dat_lim = 16384
dat_nom = ("rx_bytes", "tx_bytes", "rx_packets", "tx_packets")
rgx_ifc = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,14}\Z")
rgx_fld = re.compile(r"(?:^|\s)(?:IN|OUT)=([^\s]*)")
rgx_fwl = re.compile(
    r"(?:^|[\s_\[\]-])(?:DROP|REJECT|DENIED|DENY|BLOCK)"
    r"(?:$|[\s_\]\]:-])|\[PORT-CLOSED(?:-[A-Z]+)?\]", re.IGNORECASE
)


def fmt_tmp(sys_ts=None):
    """Use a public timestamp without exposing any journal addressing fields."""
    if sys_ts is None:
        sys_ts = time.time()
    return datetime.datetime.fromtimestamp(
        sys_ts, datetime.timezone.utc
    ).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def val_ifc(txt_ifc):
    if not isinstance(txt_ifc, str) or not rgx_ifc.fullmatch(txt_ifc):
        raise ValueError("Use a single Linux interface name, at most 15 characters.")
    return txt_ifc


def lee_red(txt_ifc, pth_sys=Path("/sys/class/net")):
    """Read the kernel counters directly; a missing interface stays unavailable."""
    val_ifc(txt_ifc)
    pth_fil = Path(pth_sys) / txt_ifc
    dat_env = {}
    try:
        for txt_nom in dat_nom:
            with (pth_fil / "statistics" / txt_nom).open() as sys_fil:
                txt_val = sys_fil.read(128).strip()
            if not re.fullmatch(r"\d{1,20}", txt_val):
                return None
            dat_env[txt_nom] = int(txt_val)
            if dat_env[txt_nom] > 2**64 - 1:
                return None
        with (pth_fil / "operstate").open() as sys_fil:
            txt_val = sys_fil.read(32).strip()
        dat_env["link_up"] = txt_val == "up"
        if txt_val == "unknown":
            try:
                with (pth_fil / "carrier").open() as sys_fil:
                    dat_env["link_up"] = sys_fil.read(8).strip() == "1"
            except OSError:
                pass
        return dat_env
    except (OSError, UnicodeError):
        return None


def es_avs(dat_itm, txt_ifc):
    """Only accept interface-tagged kernel firewall records, not arbitrary text."""
    if not isinstance(dat_itm, dict) or dat_itm.get("_TRANSPORT") != "kernel":
        return False
    txt_val = dat_itm.get("MESSAGE")
    if not isinstance(txt_val, str) or len(txt_val.encode("utf-8")) > dat_lim:
        return False
    return bool(rgx_fwl.search(txt_val)) and txt_ifc in rgx_fld.findall(txt_val)


class DatFwl:
    def __init__(self, txt_ifc):
        self.txt_ifc = val_ifc(txt_ifc)
        self.est_dis = False
        self.cnt_tot = 0
        self.cnt_del = 0
        self.txt_ult = None
        self.txt_cur = None

    def agrega(self, dat_itm, sys_ts=None):
        if not isinstance(dat_itm, dict):
            return False
        txt_cur = dat_itm.get("__CURSOR")
        if isinstance(txt_cur, str) and len(txt_cur) < 2048:
            # The last cursor remains private and prevents a repeated tail record.
            if txt_cur == self.txt_cur:
                return False
            self.txt_cur = txt_cur
        if not es_avs(dat_itm, self.txt_ifc):
            return False
        self.cnt_tot += 1
        self.cnt_del += 1
        self.txt_ult = fmt_tmp(sys_ts)
        return True

    def muestra(self):
        dat_env = {
            "available": self.est_dis,
            "delta": self.cnt_del,
            "total": self.cnt_tot,
            "last_at": self.txt_ult,
        }
        self.cnt_del = 0
        return dat_env


class DatRed:
    def __init__(self, txt_ifc, txt_ses=None):
        self.txt_ifc = val_ifc(txt_ifc)
        self.txt_ses = txt_ses or uuid.uuid4().hex
        self.dat_ant = None
        self.sys_ant = None

    def muestra(self, dat_tel, dat_fwl, sys_ts, sys_mnt):
        dat_env = {
            "schema": 1,
            "session_id": self.txt_ses,
            "interface": self.txt_ifc,
            "sampled_at": fmt_tmp(sys_ts),
            "interval_s": 0.0,
            "rx_bps": 0.0,
            "tx_bps": 0.0,
            "rx_pps": 0.0,
            "tx_pps": 0.0,
            "link_up": bool(dat_tel and dat_tel["link_up"]),
            "firewall": dat_fwl,
            "status": "live" if dat_tel is not None else "unavailable",
        }
        if dat_tel is not None and self.dat_ant is not None:
            sys_del = sys_mnt - self.sys_ant
            if sys_del > 0 and math.isfinite(sys_del):
                dat_env["interval_s"] = round(sys_del, 3)
                for txt_src, txt_dst in zip(
                    dat_nom, ("rx_bps", "tx_bps", "rx_pps", "tx_pps")
                ):
                    # An interface reset starts a new baseline instead of a spike.
                    cnt_del = max(0, dat_tel[txt_src] - self.dat_ant[txt_src])
                    dat_env[txt_dst] = round(cnt_del / sys_del, 3)
        self.dat_ant = dict(dat_tel) if dat_tel is not None else None
        self.sys_ant = sys_mnt if dat_tel is not None else None
        return dat_env


def guarda(pth_dst, dat_tel):
    """Replace one public aggregate file without following a writable symlink."""
    pth_dst = Path(pth_dst).absolute()
    if pth_dst.parent.resolve(strict=True) != pth_dst.parent:
        raise ValueError("The telemetry directory must not contain symbolic links.")
    sys_dir = os.open(pth_dst.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    txt_tmp = ".contemplation-" + uuid.uuid4().hex + ".tmp"
    try:
        try:
            sys_inf = os.stat(pth_dst.name, dir_fd=sys_dir, follow_symlinks=False)
            if not stat.S_ISREG(sys_inf.st_mode):
                raise ValueError("The telemetry target must be a regular file.")
        except FileNotFoundError:
            pass
        dat_env = (json.dumps(
            dat_tel, ensure_ascii=True, allow_nan=False, separators=(",", ":")
        ) + "\n").encode("ascii")
        sys_fil = os.open(
            txt_tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o644, dir_fd=sys_dir
        )
        with os.fdopen(sys_fil, "wb") as sys_out:
            os.fchmod(sys_out.fileno(), 0o644)
            sys_out.write(dat_env)
            sys_out.flush()
            os.fsync(sys_out.fileno())
        os.replace(txt_tmp, pth_dst.name, src_dir_fd=sys_dir, dst_dir_fd=sys_dir)
    finally:
        try:
            os.unlink(txt_tmp, dir_fd=sys_dir)
        except FileNotFoundError:
            pass
        os.close(sys_dir)


class SysLns:
    """Bound memory even if an input line is malformed or never terminates."""
    def __init__(self):
        self.dat_buf = b""
        self.est_exc = False

    def separa(self, dat_env):
        dat_res = []
        cnt_tot = dat_env.count(b"\n")
        for sys_idx, dat_itm in enumerate(dat_env.split(b"\n")):
            est_fin = sys_idx < cnt_tot
            if self.est_exc:
                if est_fin:
                    self.est_exc = False
                continue
            if len(self.dat_buf) + len(dat_itm) > dat_lim:
                self.dat_buf = b""
                self.est_exc = not est_fin
                continue
            self.dat_buf += dat_itm
            if est_fin:
                dat_res.append(self.dat_buf)
                self.dat_buf = b""
        return dat_res


class SysJrn:
    def __init__(self, dat_fwl, sys_sel):
        self.dat_fwl = dat_fwl
        self.sys_sel = sys_sel
        self.sys_prc = None
        self.dat_lns = SysLns()
        self.sys_try = 0.0

    def inicia(self, sys_mnt):
        if self.sys_prc is not None or sys_mnt < self.sys_try:
            return
        self.sys_try = sys_mnt + 10.0
        try:
            # The system group is explicit: no broad root execution is needed.
            cnt_gid = grp.getgrnam("systemd-journal").gr_gid
            if os.geteuid() != 0 and cnt_gid not in os.getgroups():
                return
            dat_env = subprocess.run(
                ["/usr/bin/journalctl", "--system", "--dmesg", "--lines=0",
                 "--quiet", "--no-pager"],
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                timeout=3, check=False,
            )
            if dat_env.returncode != 0 or dat_env.stderr:
                return
            dat_arg = [
                "/usr/bin/journalctl", "--system", "--dmesg", "--follow",
                "--output=json", "--no-pager", "--quiet",
            ]
            if self.dat_fwl.txt_cur:
                dat_arg += ["--after-cursor=" + self.dat_fwl.txt_cur, "--lines=all"]
            else:
                # A newly started service must not replay historical notices.
                dat_arg += ["--since=now", "--lines=0"]
            self.sys_prc = subprocess.Popen(
                dat_arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                bufsize=0, start_new_session=True,
            )
            for sys_fil, txt_typ in (
                (self.sys_prc.stdout, "journal"), (self.sys_prc.stderr, "error")
            ):
                os.set_blocking(sys_fil.fileno(), False)
                self.sys_sel.register(sys_fil, selectors.EVENT_READ, txt_typ)
            self.dat_lns = SysLns()
            self.dat_fwl.est_dis = True
        except (OSError, KeyError, subprocess.SubprocessError):
            self.cierra()

    def lee(self, sys_fil, txt_typ):
        try:
            dat_env = os.read(sys_fil.fileno(), 65536)
        except (OSError, BlockingIOError):
            return
        if not dat_env:
            try:
                self.sys_sel.unregister(sys_fil)
            except (KeyError, ValueError):
                pass
            return
        if txt_typ == "error":
            # Journal errors stay private, and availability is never invented.
            self.dat_fwl.est_dis = False
            return
        for dat_itm in self.dat_lns.separa(dat_env):
            try:
                dat_tel = json.loads(dat_itm)
                self.dat_fwl.agrega(dat_tel)
            except (ValueError, UnicodeError):
                continue

    def revisa(self):
        if self.sys_prc is not None and self.sys_prc.poll() is not None:
            if self.sys_prc.returncode != 0:
                # Rotation can invalidate a cursor; recover at the current tail.
                self.dat_fwl.txt_cur = None
            self.cierra()

    def cierra(self):
        self.dat_fwl.est_dis = False
        if self.sys_prc is None:
            return
        for sys_fil in (self.sys_prc.stdout, self.sys_prc.stderr):
            try:
                self.sys_sel.unregister(sys_fil)
            except (KeyError, ValueError):
                pass
            sys_fil.close()
        if self.sys_prc.poll() is None:
            self.sys_prc.terminate()
            try:
                self.sys_prc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.sys_prc.kill()
                self.sys_prc.wait(timeout=1)
        self.sys_prc = None


def ejecuta(cfg_apl):
    sys_sel = selectors.DefaultSelector()
    dat_fwl = DatFwl(cfg_apl.interface)
    dat_red = DatRed(cfg_apl.interface)
    sys_jrn = SysJrn(dat_fwl, sys_sel)
    est_fin = False

    def termina(_sys_sig, _sys_frm):
        nonlocal est_fin
        est_fin = True

    signal.signal(signal.SIGTERM, termina)
    signal.signal(signal.SIGINT, termina)
    sys_sig = time.monotonic()
    try:
        while not est_fin:
            sys_mnt = time.monotonic()
            if not cfg_apl.no_firewall:
                sys_jrn.revisa()
                sys_jrn.inicia(sys_mnt)
            sys_mnt = time.monotonic()
            if sys_mnt >= sys_sig:
                dat_tel = lee_red(cfg_apl.interface)
                guarda(cfg_apl.output, dat_red.muestra(
                    dat_tel, dat_fwl.muestra(), time.time(), sys_mnt
                ))
                if cfg_apl.once:
                    break
                sys_sig = time.monotonic() + cfg_apl.interval
            for sys_clv, _sys_evt in sys_sel.select(
                timeout=max(0.0, min(0.5, sys_sig - time.monotonic()))
            ):
                sys_jrn.lee(sys_clv.fileobj, sys_clv.data)
    finally:
        sys_jrn.cierra()
        sys_sel.close()


def argumentos():
    sys_cfg = argparse.ArgumentParser(description=__doc__)
    sys_cfg.add_argument(
        "--interface", type=val_ifc,
        default=os.environ.get("KAMALA_FLOW_INTERFACE", "enp6s0")
    )
    sys_cfg.add_argument(
        "--output", type=Path,
        default=Path(os.environ.get(
            "KAMALA_FLOW_OUTPUT",
            "/var/www/kamala.pro/html/telemetry/contemplation.json"
        ))
    )
    sys_cfg.add_argument(
        "--interval", type=float,
        default=os.environ.get("KAMALA_FLOW_INTERVAL", "1")
    )
    sys_cfg.add_argument("--once", action="store_true", help="Write one real sample.")
    sys_cfg.add_argument(
        "--no-firewall", action="store_true",
        help="Read interface counters only; firewall.available remains false."
    )
    cfg_apl = sys_cfg.parse_args()
    if not math.isfinite(cfg_apl.interval) or not 0.5 <= cfg_apl.interval <= 10:
        sys_cfg.error("--interval must be between 0.5 and 10 seconds.")
    return cfg_apl


if __name__ == "__main__":
    try:
        ejecuta(argumentos())
    except (OSError, ValueError) as sys_err:
        print("Telemetry collector stopped: " + type(sys_err).__name__, file=sys.stderr)
        sys.exit(1)
