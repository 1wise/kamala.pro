#!/usr/bin/env python3
# Timestamp: 2026-11-07
# Version: 3.1.1
# Author & Credits: https://www.alawise.es/1-s
"""Collect Camera 4 multipart telemetry into a bounded public JSON snapshot."""

import argparse
from collections import deque
from email.message import Message
import json
import math
import os
from pathlib import Path
import signal
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit
import urllib.request


def val_num(txt_val, val_min=-1e9, val_max=1e9):
    val_res = float(txt_val)
    if not math.isfinite(val_res) or not val_min <= val_res <= val_max:
        raise ValueError("invalid-measurement")
    return val_res


def prs_pnd(txt_val):
    """Distinguish 3D millimeter vectors from the legacy 2D pixel protocol."""
    dat_grp = txt_val.strip().split("|")
    if len(dat_grp) != 9:
        raise ValueError("invalid-field-count")
    dat_vec = []
    cnt_dim = None
    for txt_par in dat_grp[1:5]:
        dat_par = txt_par.split(",")
        if cnt_dim is None:
            cnt_dim = len(dat_par)
        if cnt_dim not in (2, 3) or len(dat_par) != cnt_dim:
            raise ValueError("invalid-vector")
        dat_vec.extend(val_num(txt_num) for txt_num in dat_par)
    dat_num = [val_num(dat_grp[0], 0, 1e12), *dat_vec]
    dat_num.extend(val_num(txt_num, 0, 2**53 - 1) for txt_num in dat_grp[5:])
    # The running broadcaster exposes this sentinel before its first CV frame.
    if all(val_res == 0 for val_res in dat_num):
        return None
    if dat_num[0] <= 0:
        raise ValueError("invalid-timestamp")
    if cnt_dim == 3:
        (pos_x, pos_y, rad_px, ancl_x, ancl_y, ancl_r,
         vec_dx, vec_dy, vec_dz, vel_x, vel_y, vel_z) = dat_vec
        if not (0 < rad_px <= 640 and 0 < ancl_r <= 640):
            raise ValueError("invalid-apparent-radius")
    else:
        pos_x, pos_y, ancl_x, ancl_y, vec_dx, vec_dy, vel_x, vel_y = dat_vec
        rad_px = ancl_r = vec_dz = vel_z = None
    if not (0 <= pos_x < 1280 and 0 <= pos_y < 720 and
            0 <= ancl_x < 1280 and 0 <= ancl_y < 720):
        raise ValueError("invalid-coordinate")
    des_tot, val_fit, est_alr, cnt_evn = dat_num[-4:]
    if des_tot > (1e9 if cnt_dim == 3 else math.hypot(1280, 720)) or not 0 <= val_fit <= (100 if cnt_dim == 3 else 255):
        raise ValueError("invalid-range")
    if val_fit != int(val_fit) or est_alr not in (0, 1) or cnt_evn != int(cnt_evn):
        raise ValueError("invalid-counter")
    return dict(ts=dat_num[0], mode="3d-mm" if cnt_dim == 3 else "2d-px",
                x=pos_x, y=pos_y, r=rad_px, ax=ancl_x, ay=ancl_y, ar=ancl_r,
                dx=vec_dx, dy=vec_dy, dz=vec_dz, vx=vel_x, vy=vel_y, vz=vel_z,
                displacement=des_tot, fit_pct=int(val_fit) if cnt_dim == 3 else None,
                luminance=int(val_fit) if cnt_dim == 2 else None,
                alert=bool(est_alr), events=int(cnt_evn),
                tracking_valid=val_fit > (15 if cnt_dim == 3 else 75))


def lee_lin(rsp_env, cnt_lim=8192):
    dat_lin = rsp_env.readline(cnt_lim + 1)
    if len(dat_lin) > cnt_lim:
        raise ValueError("oversized-part-header")
    if not dat_lin:
        raise EOFError("stream-ended")
    return dat_lin


def lee_mjp(rsp_env):
    """Honor JPEG lengths so byte patterns inside a frame cannot become headers."""
    dat_msg = Message()
    dat_msg["Content-Type"] = rsp_env.headers.get("Content-Type", "")
    if dat_msg.get_content_type().lower() != "multipart/x-mixed-replace":
        raise ValueError("not-a-multipart-stream")
    txt_bnd = dat_msg.get_param("boundary")
    if not txt_bnd or len(txt_bnd) > 72:
        raise ValueError("missing-boundary")
    dat_bnd = txt_bnd.encode("ascii")
    # Accept the current Pi's extra '--' parameter and standard MIME framing.
    dat_sep = {b"--" + dat_bnd}
    if dat_bnd.startswith(b"--"):
        dat_sep.add(dat_bnd)
    cnt_sin = 0
    while True:
        cnt_pre = 0
        while True:
            dat_lin = lee_lin(rsp_env)
            cnt_pre += len(dat_lin)
            if cnt_pre > 65536:
                raise ValueError("missing-part-boundary")
            dat_lin = dat_lin.strip()
            if dat_lin in dat_sep:
                break
            if any(dat_lin == dat_val + b"--" for dat_val in dat_sep):
                return
        dat_cab = {}
        cnt_cab = 0
        while True:
            dat_lin = lee_lin(rsp_env)
            cnt_cab += len(dat_lin)
            if cnt_cab > 16384:
                raise ValueError("oversized-part-header")
            if dat_lin in (b"\r\n", b"\n"):
                break
            if b":" not in dat_lin:
                raise ValueError("invalid-part-header")
            txt_nom, txt_val = dat_lin.decode("ascii").split(":", 1)
            txt_nom = txt_nom.strip().lower()
            if txt_nom in dat_cab:
                raise ValueError("duplicate-part-header")
            dat_cab[txt_nom] = txt_val.strip()
        if dat_cab.get("content-type", "").lower() != "image/jpeg":
            raise ValueError("not-a-jpeg-frame")
        txt_val = dat_cab.get("content-length", "")
        if not txt_val.isdecimal() or not 0 < int(txt_val) <= 4 * 1024 * 1024:
            raise ValueError("invalid-frame-length")
        cnt_res = int(txt_val)
        while cnt_res:
            dat_buf = rsp_env.read(min(cnt_res, 65536))
            if not dat_buf:
                raise EOFError("truncated-frame")
            cnt_res -= len(dat_buf)
        txt_val = dat_cab.get("x-1wise-pendulum")
        if txt_val is None:
            cnt_sin += 1
            if cnt_sin >= 25:
                raise ValueError("missing-pendulum-header")
            continue
        cnt_sin = 0
        yield prs_pnd(txt_val)


def esc_jsn(pth_fil, dat_tel):
    pth_fil = Path(pth_fil)
    pth_fil.parent.mkdir(parents=True, exist_ok=True)
    sys_tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                dir=pth_fil.parent, prefix=".pendulum-", delete=False) as sys_fil:
            sys_tmp = Path(sys_fil.name)
            json.dump(dat_tel, sys_fil, separators=(",", ":"), allow_nan=False)
            sys_fil.write("\n")
            sys_fil.flush()
            os.fchmod(sys_fil.fileno(), 0o644)
        os.replace(sys_tmp, pth_fil)
    finally:
        if sys_tmp is not None and sys_tmp.exists():
            sys_tmp.unlink()


class PndState:
    def __init__(self, int_mst=0.5, pth_reg=None, umb_mm=15.0):
        self.int_mst = int_mst
        self.pth_reg = Path(pth_reg) if pth_reg else None
        self.umb_mm = umb_mm
        self.dat_hst = deque(maxlen=240)
        self.dat_evn = deque(maxlen=20)
        self.dat_pnd = None
        self.sys_rec = None
        self.sys_ses = None
        self.sys_ant = -math.inf
        self.cnt_ses = 0
        self.cnt_frm = 0
        self.est_tel = "connecting"

    def reg_evn(self, dat_evn):
        if self.pth_reg is None:
            return
        self.pth_reg.parent.mkdir(parents=True, exist_ok=True)
        # Bound retention independently of external log rotation configuration.
        if self.pth_reg.exists() and self.pth_reg.stat().st_size > 8 * 1024 * 1024:
            os.replace(self.pth_reg, self.pth_reg.with_suffix(".previous.jsonl"))
        with self.pth_reg.open("a", encoding="utf-8") as sys_fil:
            os.chmod(self.pth_reg, 0o600)
            sys_fil.write(json.dumps(dat_evn, allow_nan=False) + "\n")

    def act_pnd(self, dat_pnd, sys_ts=None, sys_mnt=None):
        self.cnt_frm += 1
        if dat_pnd is None:
            self.est_tel = "waiting" if self.dat_pnd is None else "stale"
            return
        sys_ts = time.time() if sys_ts is None else sys_ts
        sys_mnt = time.monotonic() if sys_mnt is None else sys_mnt
        dat_ant = self.dat_pnd
        if dat_ant and (dat_pnd["mode"] != dat_ant["mode"] or
                        dat_pnd["ts"] < dat_ant["ts"] or
                        dat_pnd["events"] < dat_ant["events"]):
            self.dat_hst.clear()
            self.dat_evn.clear()
            self.sys_ant = -math.inf
            self.sys_ses = None
            dat_ant = None
        if dat_ant and dat_pnd["ts"] == dat_ant["ts"]:
            return
        if self.sys_ses is None:
            self.cnt_ses += 1
            self.sys_ses = sys_ts
        self.dat_pnd = dat_pnd
        self.sys_rec = sys_ts
        self.est_tel = "live"
        if dat_ant and dat_pnd["events"] > dat_ant["events"]:
            dat_evn = dict(ts=dat_pnd["ts"], received_at=sys_ts,
                count=dat_pnd["events"], delta=dat_pnd["events"] - dat_ant["events"],
                mode=dat_pnd["mode"], displacement=dat_pnd["displacement"],
                dx=dat_pnd["dx"], dy=dat_pnd["dy"], dz=dat_pnd["dz"],
                fit_pct=dat_pnd["fit_pct"], tracking_valid=dat_pnd["tracking_valid"])
            self.dat_evn.append(dat_evn)
            self.reg_evn(dat_evn)
        if sys_mnt - self.sys_ant >= self.int_mst:
            self.dat_hst.append(dat_pnd)
            self.sys_ant = sys_mnt

    def snapshot(self, est_tel=None, txt_err=None):
        est_3d = self.dat_pnd is not None and self.dat_pnd["mode"] == "3d-mm"
        return dict(version=2, camera="cam4", status=est_tel or self.est_tel,
            collected_at=time.time(), received_at=self.sys_rec,
            session_started_at=self.sys_ses, session=self.cnt_ses,
            frames_received=self.cnt_frm, sample=self.dat_pnd,
            history=list(self.dat_hst), events=list(self.dat_evn),
            error=txt_err,
            units=dict(position="px", displacement="mm" if est_3d else "px",
                       velocity="mm/s" if est_3d else "px/s"),
            limits=dict(width=1280, height=720, threshold=self.umb_mm if est_3d else 28,
                min_fit_pct=15, min_brightness=75, cooldown_s=2.5,
                sample_interval=self.int_mst))


def run_pnd(cfg_apl):
    sys_evt = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: sys_evt.set())
    signal.signal(signal.SIGINT, lambda *_: sys_evt.set())
    dat_url = urlsplit(cfg_apl.url)
    if dat_url.scheme not in ("http", "https") or not dat_url.hostname or dat_url.username:
        raise ValueError("Use an HTTP(S) stream URL without embedded credentials.")
    if not 0.2 <= cfg_apl.interval <= 5 or not 1 <= cfg_apl.timeout <= 30:
        raise ValueError("Interval must be 0.2–5 seconds; timeout must be 1–30 seconds.")
    if not math.isfinite(cfg_apl.threshold_mm) or not 0 < cfg_apl.threshold_mm <= 10000:
        raise ValueError("The millimeter threshold must be positive and at most 10000.")
    dat_tel = PndState(cfg_apl.interval, cfg_apl.events, cfg_apl.threshold_mm)
    sys_del = 1.0
    esc_jsn(cfg_apl.output, dat_tel.snapshot())
    while not sys_evt.is_set():
        try:
            pet_env = urllib.request.Request(cfg_apl.url,
                headers={"User-Agent": "Kamala-Pendulum/3.1.1",
                         "Accept": "multipart/x-mixed-replace", "Cache-Control": "no-cache"})
            with urllib.request.urlopen(pet_env, timeout=cfg_apl.timeout) as rsp_env:
                sys_pub = -math.inf
                for dat_pnd in lee_mjp(rsp_env):
                    if sys_evt.is_set():
                        break
                    dat_tel.act_pnd(dat_pnd)
                    sys_mnt = time.monotonic()
                    if sys_mnt - sys_pub >= cfg_apl.interval:
                        est_tel = None
                        if dat_tel.sys_rec is not None and time.time() - dat_tel.sys_rec > 10:
                            est_tel = "stale"
                        esc_jsn(cfg_apl.output, dat_tel.snapshot(est_tel))
                        sys_pub = sys_mnt
                    sys_del = 1.0
                    if cfg_apl.once:
                        esc_jsn(cfg_apl.output, dat_tel.snapshot())
                        return
            if not sys_evt.is_set():
                raise EOFError("stream-ended")
        except (OSError, ValueError, EOFError) as sys_err:
            # Public diagnostics describe the failure, never private source URLs.
            txt_err = str(sys_err) if isinstance(sys_err, (ValueError, EOFError)) else "source-unavailable"
            if len(txt_err) > 80 or "://" in txt_err:
                txt_err = "invalid-stream"
            esc_jsn(cfg_apl.output, dat_tel.snapshot("disconnected", txt_err))
            print("Pendulum collector: " + txt_err, file=sys.stderr, flush=True)
            if cfg_apl.once:
                raise
            sys_evt.wait(sys_del)
            sys_del = min(30.0, sys_del * 2)
    esc_jsn(cfg_apl.output, dat_tel.snapshot("stopped"))


if __name__ == "__main__":
    sys_cfg = argparse.ArgumentParser(description=__doc__)
    sys_cfg.add_argument("--url", default=os.environ.get("KAMALA_PENDULUM_URL",
                        "http://10.42.0.41:8080/?out_fmt=stream"))
    sys_cfg.add_argument("--output", type=Path,
                        default=Path("/var/www/kamala.pro/html/telemetry-pendulum/state.json"))
    sys_cfg.add_argument("--events", type=Path, help="Optional private bounded event journal.")
    sys_cfg.add_argument("--interval", type=float, default=0.5)
    sys_cfg.add_argument("--timeout", type=float, default=8)
    sys_cfg.add_argument("--threshold-mm", type=float, default=15,
                        help="Displayed 3D displacement threshold; does not change the source counter.")
    sys_cfg.add_argument("--once", action="store_true", help="Validate one complete multipart frame and exit.")
    try:
        run_pnd(sys_cfg.parse_args())
    except (OSError, ValueError, EOFError) as sys_err:
        print("Collector stopped: " + type(sys_err).__name__, file=sys.stderr)
        sys.exit(1)
