#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-11-07
# Version: 3.1.1
# Author and Credits: https://www.alawise.es/1-s

import os
import sys
import math
import time
import threading
import collections
import numpy as np
import cv2
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# --- System Layer Variables (Latin / Greek / Andorran abbreviated) ---
sys_via = sys.argv[1] if len(sys.argv) > 1 else "/dev/video0"
dmn_prt = 8080                   # Local TCP daemon port on minimaqui
chr_lim = 0                      # Delay window in seconds (0 for live)
chr_deb = 2.5                    # Cooldown seconds between logged swing triggers
mem_coda = collections.deque(maxlen=100)   # Ring buffer FIFO in RAM: (chr_ts, img_crp, pnd_pld)
sys_lck = threading.Lock()       # Thread synchronization mutex

# --- Photogrammetric Physical Constants (3.5 cm Equatorial Bell Standard) ---
cas_dia_mm = 35.0                # Exact physical width at widest equatorial rim (35.0 mm)
cam_dst_mm = 550.0               # Reference lens distance (550.0 mm)
cas_rad_px = 32                  # Reference radius in pixels at 550 mm (64.0 px width)
foc_k_rad = cas_rad_px * cam_dst_mm  # Focal-radius constant: 17600.0 px*mm

# --- Application Layer Variables (Spanish abbreviated) ---
reg_arc = "/opt/1wise/pecks/pendulum.log"
cab_lim = b"boundary_1wise_x"    # Custom MIME multipart boundary tag

# Pendulum Search ROI (X:450..750, Y:180..420)
zon_x1, zon_y1 = 450, 180
zon_x2, zon_y2 = 750, 420
umb_mrg_mm = 15.0                # 3D Trigger threshold in millimeters (1.5 cm)
cnt_evn = 0                      # Total pendulum events recorded
ult_evn = 0.0                    # Timestamp of last event
ult_pnd = b"0|0,0,0|0,0,0|0,0,0|0,0,0|0|0|0|0"


def gen_krn_geo(rad_px: int = 32) -> tuple:
    """
    Build pure geometric shape kernel for the 3.5cm sphere and its equatorial rim.
    """
    tam_k = (rad_px * 2) + 16
    ctr_k = tam_k // 2

    krn_cir = np.zeros((tam_k, tam_k), dtype=np.float32)
    cv2.circle(krn_cir, (ctr_k, ctr_k), rad_px, 1.0, 3, cv2.LINE_AA)
    cv2.line(krn_cir, (ctr_k - rad_px + 4, ctr_k + 2), (ctr_k + rad_px - 4, ctr_k + 2), 0.7, 2)

    msk_int = np.zeros((tam_k, tam_k), dtype=np.float32)
    cv2.circle(msk_int, (ctr_k, ctr_k), rad_px - 6, 1.0, -1)
    msk_int[ctr_k - 3 : ctr_k + 6, :] = 0.0
    krn_cir -= msk_int * 0.28
    krn_cir /= np.sum(np.abs(krn_cir))

    return krn_cir, ctr_k


def med_rad_subpx(brd_nrm: np.ndarray, cx_rel: int, cy_rel: int, r_ant: float) -> float:
    """
    Measure sub-pixel radius of the 3.5cm bell rim via Polar Unwrapping (cv2.warpPolar)
    and 3-point parabolic interpolation (numerical interpolation; physical accuracy requires calibration).
    """
    max_r = 46
    pol_map = cv2.warpPolar(
        brd_nrm, (max_r, 180), (float(cx_rel), float(cy_rel)),
        float(max_r), cv2.WARP_POLAR_LINEAR
    )

    # Profile edges avoiding top suspension strap (angles 25..155 deg)
    prf_rad = np.mean(pol_map[25:155, :], axis=0)

    r_min, r_max = 26, 39
    idx_pk = int(np.argmax(prf_rad[r_min:r_max])) + r_min

    # Parabolic sub-pixel peak interpolation
    if 1 <= idx_pk < (max_r - 1):
        y1, y2, y3 = float(prf_rad[idx_pk - 1]), float(prf_rad[idx_pk]), float(prf_rad[idx_pk + 1])
        denom = (y1 - 2.0 * y2 + y3)
        off_sub = 0.5 * (y1 - y3) / denom if abs(denom) > 1e-5 else 0.0
        r_med = float(idx_pk) + float(np.clip(off_sub, -0.5, 0.5))
    else:
        r_med = float(idx_pk)

    # Exponential smoothing to reject single-frame motion blur
    return (r_ant * 0.75) + (r_med * 0.25)


def loc_cas_geo(
    frm_bgr: np.ndarray, krn_cir: np.ndarray, ancl_x: float, ancl_y: float, r_ant: float
) -> tuple:
    """
    Locate 2D center (cx, cy) and sub-pixel equatorial radius (r_sub) of the 3.5cm bell.
    """
    roi_gry = cv2.cvtColor(frm_bgr[zon_y1:zon_y2, zon_x1:zon_x2], cv2.COLOR_BGR2GRAY)
    roi_sue = cv2.GaussianBlur(roi_gry, (5, 5), 1.2)

    gx = cv2.Scharr(roi_sue, cv2.CV_32F, 1, 0)
    gy = cv2.Scharr(roi_sue, cv2.CV_32F, 0, 1)
    mag_brd = cv2.magnitude(gx, gy)

    med_loc = cv2.GaussianBlur(mag_brd, (31, 31), 0) + 12.0
    brd_nrm = mag_brd / med_loc

    map_cir = cv2.filter2D(brd_nrm, cv2.CV_32F, krn_cir)

    v_strp = cv2.GaussianBlur(np.abs(gx) / med_loc, (7, 35), 0)
    map_chn = np.zeros_like(map_cir)
    off_chn = cas_rad_px + 22
    map_chn[off_chn:, :] = v_strp[:-off_chn, :] * 0.35

    h_m, w_m = map_cir.shape
    grd_y, grd_x = np.ogrid[:h_m, :w_m]
    rel_ax = ancl_x - zon_x1
    rel_ay = ancl_y - zon_y1
    pen_dst = np.hypot(grd_x - rel_ax, grd_y - rel_ay) * 0.0025

    scr_tot = map_cir + map_chn - pen_dst

    mrg_b = cas_rad_px + 4
    scr_tot[:mrg_b, :] = -1.0
    scr_tot[-mrg_b:, :] = -1.0
    scr_tot[:, :mrg_b] = -1.0
    scr_tot[:, -mrg_b:] = -1.0

    _, max_scr, _, max_loc = cv2.minMaxLoc(scr_tot)
    cx_rel, cy_rel = max_loc[0], max_loc[1]
    cx = zon_x1 + cx_rel
    cy = zon_y1 + cy_rel

    fit_val = float(np.clip(max_scr * 1.4, 0.0, 0.99))
    r_sub = med_rad_subpx(brd_nrm, cx_rel, cy_rel, r_ant) if fit_val > 0.15 else r_ant

    return cx, cy, r_sub, fit_val


def cap_v4l2_wrk():
    """
    Real-time OpenCV V4L2 worker with full 3D Photogrammetry (dX, dY, dZ in mm)
    calibrated to the invariant 35.0 mm widest diameter of the brass bell.
    """
    global cnt_evn, ult_evn, ult_pnd
    os.makedirs(os.path.dirname(reg_arc), exist_ok=True)

    dev_idx = int(sys_via.replace("/dev/video", "")) if "/dev/video" in sys_via else sys_via
    krn_cir, _ = gen_krn_geo(cas_rad_px)

    # 3D Resting Equilibrium Anchor: (ancl_x, ancl_y, ancl_r)
    ancl_x, ancl_y, ancl_r = 608.0, 300.0, float(cas_rad_px)
    pos_x, pos_y, rad_act = 608, 300, float(cas_rad_px)
    ant_x, ant_y, ant_z = 608, 300, cam_dst_mm
    ant_ts = time.time()
    ini_lck = False

    while True:
        try:
            cap_dev = cv2.VideoCapture(dev_idx, cv2.CAP_V4L2)
            cap_dev.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            cap_dev.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap_dev.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap_dev.set(cv2.CAP_PROP_FPS, 25)
            cap_dev.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not cap_dev.isOpened():
                sys.stderr.write(f"[!] Cannot open {sys_via}. Retrying in 2s...\n")
                time.sleep(2)
                continue

            print(f"[+] 3D Geometric Tracker v3.1.1 locked! Standard: D={cas_dia_mm}mm")

            while True:
                ret_ok, frm_bgr = cap_dev.read()
                if not ret_ok or frm_bgr is None:
                    break

                chr_ts = time.time()
                dlt_t = max(0.001, chr_ts - ant_ts)

                # 1. Detect 2D center (det_x, det_y) + sub-pixel apparent radius (det_r)
                det_x, det_y, det_r, fit_geo = loc_cas_geo(frm_bgr, krn_cir, ancl_x, ancl_y, rad_act)

                if fit_geo > 0.15:
                    pos_x, pos_y, rad_act = det_x, det_y, det_r
                    if not ini_lck:
                        ancl_x, ancl_y, ancl_r = float(pos_x), float(pos_y), float(rad_act)
                        ant_x, ant_y = pos_x, pos_y
                        ant_z = foc_k_rad / ancl_r
                        ini_lck = True

                # 2. Self-calibrating lateral scale (mm/px) & Z-depth (mm) from 35.0mm constant
                esc_act = cas_dia_mm / (2.0 * ancl_r)
                z_act_mm = foc_k_rad / max(20.0, rad_act)
                z_anc_mm = foc_k_rad / max(20.0, ancl_r)

                dx_mm = (pos_x - ancl_x) * esc_act
                dy_mm = (pos_y - ancl_y) * esc_act
                dz_mm = z_act_mm - z_anc_mm          # -dZ = closer to lens, +dZ = further away

                vx_mms = ((pos_x - ant_x) * esc_act) / dlt_t
                vy_mms = ((pos_y - ant_y) * esc_act) / dlt_t
                vz_mms = (z_act_mm - ant_z) / dlt_t

                # Total 2D & 3D displacement amplitude in millimeters
                des_2d_mm = math.hypot(dx_mm, dy_mm)
                des_3d_mm = math.sqrt(dx_mm**2 + dy_mm**2 + dz_mm**2)

                ant_x, ant_y, ant_z = pos_x, pos_y, z_act_mm
                ant_ts = chr_ts

                # 3. 3D Equilibrium slow-drift & threshold state machine
                if des_3d_mm < umb_mrg_mm:
                    ancl_x = (ancl_x * 0.985) + (pos_x * 0.015)
                    ancl_y = (ancl_y * 0.985) + (pos_y * 0.015)
                    ancl_r = (ancl_r * 0.992) + (rad_act * 0.008)
                    est_alr = 0
                    col_hud = (0, 255, 0)
                    est_txt = (
                        f"IDLE | dX:{dx_mm:+.1f} dY:{dy_mm:+.1f} dZ:{dz_mm:+.1f}mm | "
                        f"3D:{des_3d_mm:.1f}mm | Z:{z_act_mm:.0f}mm | Ev:{cnt_evn}"
                    )
                else:
                    est_alr = 1
                    col_hud = (0, 0, 255)
                    ancl_x = (ancl_x * 0.996) + (pos_x * 0.004)
                    ancl_y = (ancl_y * 0.996) + (pos_y * 0.004)
                    ancl_r = (ancl_r * 0.998) + (rad_act * 0.002)

                    if (chr_ts - ult_evn) >= chr_deb:
                        ult_evn = chr_ts
                        cnt_evn += 1
                        ts_iso = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(chr_ts))
                        msj_log = (
                            f"[{ts_iso}] EVENT #{cnt_evn} | 3D={des_3d_mm:.1f}mm "
                            f"(dX={dx_mm:+.1f}, dY={dy_mm:+.1f}, dZ={dz_mm:+.1f}mm) "
                            f"V=({vx_mms:+.1f},{vy_mms:+.1f},{vz_mms:+.1f})mm/s\n"
                        )
                        sys.stdout.write(msj_log)
                        sys.stdout.flush()
                        with open(reg_arc, "a", encoding="utf-8") as f_log:
                            f_log.write(msj_log)

                    est_txt = (
                        f"SWING #{cnt_evn}! | dX:{dx_mm:+.1f} dY:{dy_mm:+.1f} dZ:{dz_mm:+.1f}mm | "
                        f"3D:{des_3d_mm:.1f}mm"
                    )

                # 4. Pack 3D telemetry into X-1wise-Pendulum boundary header
                # Format: ts|x_px,y_px,r_px|ax_px,ay_px,ar_px|dx,dy,dz|vx,vy,vz|shift_3d|fit_pct|alert|events
                fit_pct = int(fit_geo * 100)
                pnd_pld = (
                    f"{chr_ts:.6f}|{pos_x},{pos_y},{rad_act:.2f}|"
                    f"{ancl_x:.2f},{ancl_y:.2f},{ancl_r:.2f}|"
                    f"{dx_mm:.2f},{dy_mm:.2f},{dz_mm:.2f}|"
                    f"{vx_mms:.1f},{vy_mms:.1f},{vz_mms:.1f}|"
                    f"{des_3d_mm:.2f}|{fit_pct}|{est_alr}|{cnt_evn}"
                ).encode("ascii")

                # 5. Draw calibrated 3D geometric HUD on frame
                ax, ay = int(ancl_x), int(ancl_y)
                umb_px = int(umb_mrg_mm / esc_act)
                cv2.circle(frm_bgr, (ax, ay), umb_px, (255, 255, 0), 1, cv2.LINE_AA)
                cv2.circle(frm_bgr, (pos_x, pos_y), int(round(rad_act)), col_hud, 2, cv2.LINE_AA)
                cv2.drawMarker(frm_bgr, (pos_x, pos_y), col_hud, cv2.MARKER_CROSS, 10, 1)
                cv2.line(frm_bgr, (ax, ay), (pos_x, pos_y), col_hud, 1, cv2.LINE_AA)

                cv2.rectangle(frm_bgr, (14, 10), (880, 46), (0, 0, 0), -1)
                cv2.putText(
                    frm_bgr, est_txt, (22, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.54, col_hud, 2, cv2.LINE_AA
                )

                # 6. Encode JPEG and push 3-tuple into ring buffer
                ok_jpg, buf_jpg = cv2.imencode(".jpg", frm_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
                if ok_jpg:
                    img_crp = buf_jpg.tobytes()
                    with sys_lck:
                        ult_pnd = pnd_pld
                        mem_coda.append((chr_ts, img_crp, pnd_pld))

            cap_dev.release()
            time.sleep(2)
        except Exception as val_err:
            sys.stderr.write(f"[!] Tracker error: {val_err}. Retrying in 2s...\n")
            time.sleep(2)


class MjpegStreamSrv(BaseHTTPRequestHandler):
    """
    Low-latency HTTP multipart broadcaster injecting calibrated 3D millimeter
    X-1wise-Pendulum telemetry into every frame boundary.
    """
    def do_GET(self):
        qry_prs = parse_qs(urlparse(self.path).query)
        out_fmt = qry_prs.get("out_fmt", ["stream"])[0]

        if out_fmt == "status":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            with sys_lck:
                q_len = len(mem_coda)
                pnd_str = ult_pnd.decode("ascii")
            self.wfile.write(
                f"Source: {sys_via} | Standard: D={cas_dia_mm}mm | Frames: {q_len} | 3D-Pendulum: {pnd_str}\n".encode()
            )
            return

        if out_fmt == "view":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            htm_rsp = (
                b"<!DOCTYPE html><html><head><meta charset='utf-8'>"
                b"<title>1wise Minimaqui Live</title>"
                b"<style>body{margin:0;background:#000;overflow:hidden;display:flex;"
                b"justify-content:center;align-items:center;height:100vh;cursor:none;}"
                b"img{width:100vw;height:100vh;object-fit:contain;}</style></head>"
                b"<body><img src='/?out_fmt=stream'></body></html>"
            )
            self.wfile.write(htm_rsp)
            return

        self.send_response(200)
        self.send_header("Content-Type", f"multipart/x-mixed-replace; boundary={cab_lim.decode()}")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Connection", "close")
        self.end_headers()

        ult_ts = 0.0

        try:
            while True:
                chr_act = time.time()
                obj_ts = chr_act - chr_lim
                itm_sel = None

                with sys_lck:
                    while mem_coda and mem_coda[0][0] < (obj_ts - 2.0):
                        mem_coda.popleft()

                    for itm_cur in reversed(mem_coda):
                        if itm_cur[0] <= obj_ts:
                            if itm_cur[0] > ult_ts:
                                itm_sel = itm_cur
                            break

                if itm_sel:
                    ult_ts, img_crp, pnd_pld = itm_sel
                    cab_pkt = (
                        b"--" + cab_lim + b"\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: " + str(len(img_crp)).encode() + b"\r\n"
                        b"X-1wise-Pendulum: " + pnd_pld + b"\r\n\r\n"
                    )
                    self.wfile.write(cab_pkt + img_crp + b"\r\n")
                    self.wfile.flush()
                else:
                    time.sleep(0.005)

        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    ThreadingHTTPServer.allow_reuse_address = True
    t_cap = threading.Thread(target=cap_v4l2_wrk, daemon=True)
    t_cap.start()
    print(f"[*] 1wise 3D Geometric Pendulum Tracker v3.1.1 on 0.0.0.0:{dmn_prt} | D_const={cas_dia_mm}mm")
    srv_inst = ThreadingHTTPServer(("0.0.0.0", dmn_prt), MjpegStreamSrv)
    try:
        srv_inst.serve_forever()
    except KeyboardInterrupt:
        srv_inst.server_close()
