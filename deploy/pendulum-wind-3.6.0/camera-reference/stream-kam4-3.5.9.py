#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-11-11
# Version: 3.5.9
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
mem_coda = collections.deque()   # Ring buffer FIFO in RAM: (chr_ts, img_crp, pnd_pld)
buf_arm = collections.deque(maxlen=30)  # Rolling kinematic window for harmonic dissociation
sys_lck = threading.Lock()       # Thread synchronization mutex

# --- Photogrammetric Physical Constants (44.0 mm Equatorial Bell Standard) ---
cas_dia_mm = 44.0                # Exact physical width of bell at equator (44.0 mm)
cam_dst_mm = 550.0               # Reference lens distance (550.0 mm)
cas_rad_px = 40                  # Reference radius in pixels at 550 mm (~80.5 px diameter)
foc_k_rad = 40.23 * cam_dst_mm   # Focal-radius constant for 44mm sphere: 22126.5 px*mm

# --- Application Layer Variables (Spanish abbreviated) ---
reg_arc = "/opt/1wise/pecks/pendulum.log"
cab_lim = b"boundary_1wise_x"    # Custom MIME multipart boundary tag

# Pendulum Search ROI (Centered around X:546, Y:290 where the 44mm bell hangs)
zon_x1, zon_y1 = 420, 160
zon_x2, zon_y2 = 720, 430
umb_mrg_mm = 15.0                # 3D Trigger threshold in millimeters (1.5 cm)

# Windchime Search ROI (Left flank: hanging pan cavity, tilted handle, and nickel-coated ladle)
zon_srt = (18, 185, 220, 470)    # (x1, y1, x2, y2) bounding box for acoustic anemometer
col_azl = (255, 140, 0)          # Crisp Azure-Blue BGR color for normal windchime HUD
col_roj = (0, 0, 255)            # Critical red alarm BGR color for turbulence threshold
ang_srt = 32.5                   # Pan handle tilt vector angle in degrees
dis_arm = 0.0                    # Harmonic dissociation turbulence index (0.00 to 1.00)
umb_trb = 0.45                   # Turbulence harmonic dissociation alarm threshold

cnt_evn = 0                      # Total pendulum events recorded
ult_evn = 0.0                    # Timestamp of last event
ult_trb = 0.0                    # Timestamp of last turbulence alarm log
ult_pnd = b"0|0,0,0|0,0,0|0,0,0|0,0,0|0|0|0|0|0.0|0.00|0|0.00"

# Persistent anchor caches for pan center and nickel ladle shaft
ant_sx, ant_sy = 78.5, 96.0
ant_lx = 78.5
ini_cuc = False


def gen_krn_vec(rad_px: int = 40) -> tuple:
    tam_k = (rad_px * 2) + 32
    ctr_k = tam_k // 2
    grd_y, grd_x = np.ogrid[:tam_k, :tam_k]
    dx = (grd_x - ctr_k).astype(np.float32)
    dy = (grd_y - ctr_k).astype(np.float32)
    dst_r = np.hypot(dx, dy) + 1e-5

    rng_w = np.exp(-0.5 * ((dst_r - float(rad_px)) / 2.2) ** 2).astype(np.float32)
    rng_w[dst_r < (rad_px - 6)] = 0.0
    rng_w[dst_r > (rad_px + 6)] = 0.0

    krn_nx = (dx / dst_r) * rng_w
    krn_ny = (dy / dst_r) * rng_w
    nrm_f = float(np.sum(rng_w)) + 1e-5
    krn_nx /= nrm_f
    krn_ny /= nrm_f

    krn_dsk = np.zeros((tam_k, tam_k), dtype=np.float32)
    msk_in = dst_r <= (rad_px - 4)
    msk_out = (dst_r >= (rad_px + 4)) & (dst_r <= (rad_px + 14))
    krn_dsk[msk_in] = 1.0 / float(np.sum(msk_in))
    krn_dsk[msk_out] = -1.0 / float(np.sum(msk_out))

    return krn_nx, krn_ny, krn_dsk


def med_rad_subpx(brd_nrm: np.ndarray, cx_rel: int, cy_rel: int, r_ant: float) -> float:
    max_r = 54
    pol_map = cv2.warpPolar(
        brd_nrm, (max_r, 180), (float(cx_rel), float(cy_rel)),
        float(max_r), cv2.WARP_POLAR_LINEAR
    )
    prf_rad = np.mean(pol_map[15:165, :], axis=0)
    r_min, r_max = 35, 46
    idx_pk = int(np.argmax(prf_rad[r_min:r_max])) + r_min

    if 1 <= idx_pk < (max_r - 1):
        y1, y2, y3 = float(prf_rad[idx_pk - 1]), float(prf_rad[idx_pk]), float(prf_rad[idx_pk + 1])
        denom = (y1 - 2.0 * y2 + y3)
        off_sub = 0.5 * (y1 - y3) / denom if abs(denom) > 1e-5 else 0.0
        r_med = float(idx_pk) + float(np.clip(off_sub, -0.5, 0.5))
    else:
        r_med = float(idx_pk)

    r_clmp = float(np.clip(r_med, 36.0, 45.0))
    return (r_ant * 0.82) + (r_clmp * 0.18)


def loc_cas_geo(
    frm_bgr: np.ndarray,
    krn_nx: np.ndarray,
    krn_ny: np.ndarray,
    krn_dsk: np.ndarray,
    ancl_x: float,
    ancl_y: float,
    r_ant: float
) -> tuple:
    roi_gry = cv2.cvtColor(frm_bgr[zon_y1:zon_y2, zon_x1:zon_x2], cv2.COLOR_BGR2GRAY)
    roi_sue = cv2.GaussianBlur(roi_gry, (5, 5), 1.2)
    gry_f = roi_sue.astype(np.float32)

    lum_med = float(np.median(gry_f))
    mod_dia = lum_med > 70.0

    gx = cv2.Scharr(roi_sue, cv2.CV_32F, 1, 0)
    gy = cv2.Scharr(roi_sue, cv2.CV_32F, 0, 1)
    mag_brd = cv2.magnitude(gx, gy)
    med_loc = cv2.GaussianBlur(mag_brd, (35, 35), 0) + 12.0

    gx_nrm = gx / med_loc
    gy_nrm = gy / med_loc
    brd_nrm = mag_brd / med_loc

    div_out = cv2.filter2D(gx_nrm, cv2.CV_32F, krn_nx) + cv2.filter2D(gy_nrm, cv2.CV_32F, krn_ny)
    cnt_dsk = cv2.filter2D(gry_f, cv2.CV_32F, krn_dsk) / 65.0

    if mod_dia:
        map_esf = np.clip(-cnt_dsk, 0.0, 2.5) * 1.4 + np.clip(div_out, 0.0, 2.0) * 1.1
        spc_dot = cv2.GaussianBlur(np.clip(gry_f - 170.0, 0.0, 85.0) / 85.0, (11, 11), 0)
        map_spc = np.zeros_like(map_esf)
        map_spc[14:, 10:] = spc_dot[:-14, :-10] * 0.55
        map_esf += map_spc
    else:
        map_dom = np.clip(cnt_dsk, 0.0, 2.5) * 1.4 + np.clip(-div_out, 0.0, 2.0) * 0.9
        map_esf = np.zeros_like(map_dom)
        map_esf[10:, :] = map_dom[:-10, :]

    v_strp = cv2.GaussianBlur(
        (np.abs(gx_nrm) * np.clip(120.0 - gry_f, 0.0, 120.0) / 80.0), (9, 39), 0
    )
    map_chn = np.zeros_like(map_esf)
    off_chn = cas_rad_px + 14
    map_chn[off_chn:, :] = v_strp[:-off_chn, :] * 0.85

    scr_tot = map_esf * (1.0 + map_chn) + (map_chn * 0.4)

    h_m, w_m = scr_tot.shape
    grd_y, grd_x = np.ogrid[:h_m, :w_m]
    rel_ax = ancl_x - zon_x1
    rel_ay = ancl_y - zon_y1
    scr_tot -= np.hypot(grd_x - rel_ax, grd_y - rel_ay) * 0.0022

    mrg_b = cas_rad_px + 6
    scr_tot[:mrg_b, :] = -1.0
    scr_tot[-mrg_b:, :] = -1.0
    scr_tot[:, :mrg_b] = -1.0
    scr_tot[:, -mrg_b:] = -1.0

    _, max_scr, _, max_loc = cv2.minMaxLoc(scr_tot)
    cx_rel, cy_rel = max_loc[0], max_loc[1]
    cx = zon_x1 + cx_rel
    cy = zon_y1 + cy_rel

    fit_val = float(np.clip(max_scr * 0.45, 0.0, 0.99))
    r_sub = med_rad_subpx(brd_nrm, cx_rel, cy_rel, r_ant) if fit_val > 0.14 else r_ant

    return cx, cy, r_sub, fit_val


def loc_srt_arm(frm_bgr: np.ndarray) -> tuple:
    """
    Optical Windchime Tracker v3.5.9:
    1. Pan cavity anchor (sx, sy) with strict proximity bounds.
    2. Nickel-coated ladle handle tracker with Gaussian temporal tether (ant_lx)
       and EMA smoothing to eliminate nighttime sensor-grain jumps.
    3. Pan tilt vector (ang_act) via radial bar-contrast along the pan handle.
    """
    global ant_sx, ant_sy, ant_lx, ini_cuc
    x1, y1, x2, y2 = zon_srt
    roi_gry = cv2.cvtColor(frm_bgr[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
    roi_sue = cv2.GaussianBlur(roi_gry, (5, 5), 1.1)

    roi_cav = roi_sue[:195, :155]
    umb_osc = float(np.percentile(roi_cav, 35))
    msk_pan = (roi_cav < max(42.0, min(95.0, umb_osc))).astype(np.uint8) * 255
    msk_pan[:, :18] = 0
    cnts_p, _ = cv2.findContours(msk_pan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    sx_rel, sy_rel = ant_sx, ant_sy
    elp_pan = None
    best_cnt = None
    min_dist = 999.0

    if cnts_p:
        for c in cnts_p:
            area = cv2.contourArea(c)
            if 350 < area < 4500:
                mom_p = cv2.moments(c)
                if mom_p["m00"] > 0:
                    cx_c = mom_p["m10"] / mom_p["m00"]
                    cy_c = mom_p["m01"] / mom_p["m00"]
                    if 45.0 <= cx_c <= 120.0 and 60.0 <= cy_c <= 135.0:
                        dist = math.hypot(cx_c - ant_sx, cy_c - ant_sy)
                        if dist < min_dist:
                            min_dist = dist
                            best_cnt = c
                            sx_rel, sy_rel = cx_c, cy_c

    if best_cnt is not None and len(best_cnt) >= 5:
        elp_pan = cv2.fitEllipse(best_cnt)

    ant_sx = (ant_sx * 0.85) + (sx_rel * 0.15)
    ant_sy = (ant_sy * 0.85) + (sy_rel * 0.15)
    sx_rel, sy_rel = ant_sx, ant_sy

    # 2. Nickel-coated Ladle Handle Tracker with Gaussian continuity tether
    ix1 = max(25, int(sx_rel - 36))
    ix2 = min(135, int(sx_rel + 36))
    iy1 = 10
    iy2 = 120

    zon_cuc = roi_sue[iy1:iy2, ix1:ix2].astype(np.float32)
    gx_cuc = np.abs(cv2.Scharr(zon_cuc, cv2.CV_32F, 1, 0))
    prf_cuc = np.mean(zon_cuc, axis=0) * 1.2 + (np.mean(gx_cuc, axis=0) * 0.45)

    if prf_cuc.size > 4:
        if ini_cuc:
            xs_idx = np.arange(prf_cuc.size, dtype=np.float32)
            rel_ant = float(np.clip(ant_lx - ix1, 0.0, float(prf_cuc.size - 1)))
            tether = np.exp(-0.5 * ((xs_idx - rel_ant) / 11.0) ** 2).astype(np.float32)
            prf_w = prf_cuc * (0.35 + 0.65 * tether)
        else:
            prf_w = prf_cuc

        idx_c = int(np.argmax(prf_w))
        if 1 <= idx_c < (prf_cuc.size - 1):
            y_a, y_b, y_c = float(prf_cuc[idx_c - 1]), float(prf_cuc[idx_c]), float(prf_cuc[idx_c + 1])
            den_c = (y_a - 2.0 * y_b + y_c)
            sub_c = 0.5 * (y_a - y_c) / den_c if abs(den_c) > 1e-5 else 0.0
            lx_raw = float(ix1 + idx_c) + float(np.clip(sub_c, -0.5, 0.5))
        else:
            lx_raw = float(ix1 + idx_c)

        if not ini_cuc:
            ant_lx = lx_raw
            ini_cuc = True
        else:
            ant_lx = (ant_lx * 0.75) + (lx_raw * 0.25)
        lx_rel = ant_lx
    else:
        lx_rel = ant_lx
    ly_top = float(iy1)
    ly_bot = float(iy2)

    # 3. Pan Tilt Vector (Radial Spoke Bar-Contrast Handle Detector)
    h_r, w_r = roi_sue.shape
    r_vec = np.arange(75.0, 172.0, 4.0, dtype=np.float32)
    ang_cand = np.linspace(12.0, 44.0, 65, dtype=np.float32)
    scr_bar = np.zeros_like(ang_cand)

    for idx_a, a_deg in enumerate(ang_cand):
        a_rad = math.radians(float(a_deg))
        ux, uy = math.sin(a_rad), math.cos(a_rad)
        px, py = -uy, ux

        cx_r = np.clip(np.round(sx_rel + ux * r_vec).astype(int), 0, w_r - 1)
        cy_r = np.clip(np.round(sy_rel + uy * r_vec).astype(int), 0, h_r - 1)
        lx1_r = np.clip(np.round(sx_rel + ux * r_vec + px * 11.0).astype(int), 0, w_r - 1)
        ly1_r = np.clip(np.round(sy_rel + uy * r_vec + py * 11.0).astype(int), 0, h_r - 1)
        lx2_r = np.clip(np.round(sx_rel + ux * r_vec - px * 11.0).astype(int), 0, w_r - 1)
        ly2_r = np.clip(np.round(sy_rel + uy * r_vec - py * 11.0).astype(int), 0, h_r - 1)

        val_in = float(np.mean(roi_sue[cy_r, cx_r]))
        val_out = 0.5 * float(np.mean(roi_sue[ly1_r, lx1_r]) + np.mean(roi_sue[ly2_r, lx2_r]))
        scr_bar[idx_a] = (val_in - val_out) - abs(float(a_deg) - 32.0) * 0.35


    idx_best = int(np.argmax(scr_bar))
    ang_act = float(ang_cand[idx_best])
    rad_best = math.radians(ang_act)
    mx_rel = sx_rel + math.sin(rad_best) * 162.0
    my_rel = sy_rel + math.cos(rad_best) * 162.0

    # 4. Harmonic Dissociation: Ladle nickel handle vs Pan tilt
    off_rel = lx_rel - sx_rel
    buf_arm.append((sx_rel, lx_rel, off_rel, ang_act))

    if len(buf_arm) >= 6:
        arr_b = np.array(buf_arm, dtype=np.float32)
        v_tlt = np.diff(arr_b[:, 3])
        v_cuc = np.diff(arr_b[:, 1])
        std_t = float(np.std(v_tlt))
        std_c = float(np.std(v_cuc))
        std_off = float(np.std(arr_b[:, 2]))

        act_mov = float(np.clip((std_t * 0.8 + std_c + std_off - 0.55) / 2.2, 0.0, 1.0))
        if std_t > 0.15 and std_c > 0.12:
            cor_v = float(np.sum((v_tlt - np.mean(v_tlt)) * (v_cuc - np.mean(v_cuc))))
            cor_v /= (len(v_tlt) * std_t * std_c + 1e-5)
            des_fas = 1.0 - min(1.0, abs(cor_v))
        else:
            des_fas = 0.0

        exc_int = float(np.clip(std_off / 5.5, 0.0, 1.0))
        dis_raw = act_mov * (0.55 * des_fas + 0.45 * exc_int)
    else:
        dis_raw = 0.0

    sx_abs, sy_abs = int(round(x1 + sx_rel)), int(round(y1 + sy_rel))
    lx_abs = int(round(x1 + lx_rel))
    ly_top_abs, ly_bot_abs = int(round(y1 + ly_top)), int(round(y1 + ly_bot))
    mx_abs, my_abs = int(round(x1 + mx_rel)), int(round(y1 + my_rel))

    return sx_abs, sy_abs, lx_abs, ly_top_abs, ly_bot_abs, mx_abs, my_abs, ang_act, dis_raw, elp_pan


def cap_v4l2_wrk():
    global cnt_evn, ult_evn, ult_trb, ult_pnd, ang_srt, dis_arm
    os.makedirs(os.path.dirname(reg_arc), exist_ok=True)

    dev_idx = int(sys_via.replace("/dev/video", "")) if "/dev/video" in sys_via else sys_via
    krn_nx, krn_ny, krn_dsk = gen_krn_vec(cas_rad_px)

    ancl_x, ancl_y, ancl_r = 546.0, 292.0, 40.23
    pos_x, pos_y, rad_act = 546, 292, 40.23
    ant_x, ant_y, ant_z = 546, 292, cam_dst_mm
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

            print(f"[+] Dual Tracker v3.5.9 locked! Bell: D={cas_dia_mm}mm | Windchime ROI={zon_srt}")

            while True:
                ret_ok, frm_bgr = cap_dev.read()
                if not ret_ok or frm_bgr is None:
                    break

                chr_ts = time.time()
                dlt_t = max(0.001, chr_ts - ant_ts)

                det_x, det_y, det_r, fit_geo = loc_cas_geo(
                    frm_bgr, krn_nx, krn_ny, krn_dsk, ancl_x, ancl_y, rad_act
                )

                if fit_geo > 0.14:
                    pos_x, pos_y, rad_act = det_x, det_y, det_r
                    if not ini_lck:
                        ancl_x, ancl_y, ancl_r = float(pos_x), float(pos_y), float(rad_act)
                        ant_x, ant_y = pos_x, pos_y
                        ant_z = foc_k_rad / ancl_r
                        ini_lck = True

                sx, sy, lx, ly_top, ly_bot, mx, my, ang_raw, dis_raw, elp_pan = loc_srt_arm(frm_bgr)
                ang_srt = (ang_srt * 0.80) + (ang_raw * 0.20)
                dis_arm = (dis_arm * 0.75) + (dis_raw * 0.25)

                trb_alr = 1 if dis_arm >= umb_trb else 0
                if trb_alr and (chr_ts - ult_trb) >= chr_deb:
                    ult_trb = chr_ts
                    ts_iso = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(chr_ts))
                    msj_trb = f"[{ts_iso}] TURBULENCE ALARM! DH={dis_arm:.2f} (Tilt={ang_srt:+.1f}deg) -> Bird trigger suppressed.\n"
                    sys.stdout.write(msj_trb)
                    sys.stdout.flush()
                    with open(reg_arc, "a", encoding="utf-8") as f_log:
                        f_log.write(msj_trb)

                esc_act = cas_dia_mm / (2.0 * ancl_r)
                z_act_mm = foc_k_rad / max(30.0, rad_act)
                z_anc_mm = foc_k_rad / max(30.0, ancl_r)

                dx_mm = (pos_x - ancl_x) * esc_act
                dy_mm = (pos_y - ancl_y) * esc_act
                dz_mm = z_act_mm - z_anc_mm

                vx_mms = ((pos_x - ant_x) * esc_act) / dlt_t
                vy_mms = ((pos_y - ant_y) * esc_act) / dlt_t
                vz_mms = (z_act_mm - ant_z) / dlt_t

                des_2d_mm = math.hypot(dx_mm, dy_mm)
                des_3d_mm = math.sqrt(dx_mm**2 + dy_mm**2 + dz_mm**2)

                ant_x, ant_y, ant_z = pos_x, pos_y, z_act_mm
                ant_ts = chr_ts

                fac_vnt = float(np.clip(dis_arm / umb_trb, 0.0, 2.5))
                eff_mrg_mm = umb_mrg_mm * (1.0 + 2.5 * fac_vnt) if trb_alr else umb_mrg_mm

                if des_2d_mm < eff_mrg_mm:
                    ancl_x = (ancl_x * 0.98) + (pos_x * 0.02)
                    ancl_y = (ancl_y * 0.98) + (pos_y * 0.02)
                    ancl_r = (ancl_r * 0.94) + (rad_act * 0.06)
                    est_alr = 0
                    col_hud = (0, 255, 0)
                    est_txt = (
                        f"IDLE | dX:{dx_mm:+.1f} dY:{dy_mm:+.1f} | 3D:{des_3d_mm:.1f}mm | "
                        f"W-Eff:{fac_vnt:.2f}x | Ev:{cnt_evn}"
                    )
                else:
                    if trb_alr:
                        est_alr = 0
                        col_hud = (0, 165, 255)
                        est_txt = f"WIND BUFFET (Suppressed) | dX:{dx_mm:+.1f} dY:{dy_mm:+.1f} | W-Eff:{fac_vnt:.2f}x"
                    else:
                        est_alr = 1
                        col_hud = (0, 0, 255)
                        ancl_x = (ancl_x * 0.995) + (pos_x * 0.005)
                        ancl_y = (ancl_y * 0.995) + (pos_y * 0.005)
                        ancl_r = (ancl_r * 0.995) + (rad_act * 0.005)

                        if (chr_ts - ult_evn) >= chr_deb:
                            ult_evn = chr_ts
                            cnt_evn += 1
                            ts_iso = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(chr_ts))
                            msj_log = (
                                f"[{ts_iso}] BIRD EVENT #{cnt_evn} | 3D={des_3d_mm:.1f}mm "
                                f"(dX={dx_mm:+.1f}, dY={dy_mm:+.1f}) W-Eff={fac_vnt:.2f}x\n"
                            )
                            sys.stdout.write(msj_log)
                            sys.stdout.flush()
                            with open(reg_arc, "a", encoding="utf-8") as f_log:
                                f_log.write(msj_log)

                        est_txt = (
                            f"BIRD EVENT #{cnt_evn}! | dX:{dx_mm:+.1f} dY:{dy_mm:+.1f} | 3D:{des_3d_mm:.1f}mm"
                        )

                fit_pct = int(fit_geo * 100)
                pnd_pld = (
                    f"{chr_ts:.6f}|{pos_x},{pos_y},{rad_act:.2f}|"
                    f"{ancl_x:.2f},{ancl_y:.2f},{ancl_r:.2f}|"
                    f"{dx_mm:.2f},{dy_mm:.2f},{dz_mm:.2f}|"
                    f"{vx_mms:.1f},{vy_mms:.1f},{vz_mms:.1f}|"
                    f"{des_3d_mm:.2f}|{fit_pct}|{est_alr}|{cnt_evn}|"
                    f"{ang_srt:.1f}|{dis_arm:.2f}|{trb_alr}|{fac_vnt:.2f}"
                ).encode("ascii")

                ax, ay = int(ancl_x), int(ancl_y)
                umb_px = int(eff_mrg_mm / esc_act)
                cv2.circle(frm_bgr, (ax, ay), umb_px, (255, 255, 0) if not trb_alr else (0, 165, 255), 1, cv2.LINE_AA)
                cv2.circle(frm_bgr, (pos_x, pos_y), int(round(rad_act)), col_hud, 2, cv2.LINE_AA)
                cv2.drawMarker(frm_bgr, (pos_x, pos_y), col_hud, cv2.MARKER_CROSS, 10, 1)
                cv2.line(frm_bgr, (ax, ay), (pos_x, pos_y), col_hud, 1, cv2.LINE_AA)

                col_wnd = col_roj if trb_alr else col_azl
                if elp_pan is not None:
                    (ex, ey), (ew, eh), e_ang = elp_pan
                    if ew > 10 and eh > 10:
                        cv2.ellipse(
                            frm_bgr,
                            ((float(ex) + float(zon_srt[0]), float(ey) + float(zon_srt[1])),
                             (float(ew), float(eh)), float(e_ang)),
                            col_wnd, 2, cv2.LINE_AA
                        )
                else:
                    cv2.circle(frm_bgr, (sx, sy), 38, col_wnd, 2, cv2.LINE_AA)

                t_rad = math.radians(ang_srt)
                bx1 = int(round(sx - math.cos(t_rad) * 32))
                by1 = int(round(sy + math.sin(t_rad) * 32))
                bx2 = int(round(sx + math.cos(t_rad) * 32))
                by2 = int(round(sy - math.sin(t_rad) * 32))
                cv2.line(frm_bgr, (bx1, by1), (bx2, by2), col_wnd, 2, cv2.LINE_AA)

                cv2.line(frm_bgr, (sx, sy), (mx, my), col_wnd, 2, cv2.LINE_AA)
                cv2.circle(frm_bgr, (mx, my), 4, col_wnd, -1, cv2.LINE_AA)

                cv2.line(frm_bgr, (lx, ly_top), (lx, ly_bot), (255, 255, 0), 3, cv2.LINE_AA)
                cv2.circle(frm_bgr, (lx, ly_top), 3, (255, 255, 0), -1, cv2.LINE_AA)
                cv2.circle(frm_bgr, (lx, ly_bot), 3, (255, 255, 0), -1, cv2.LINE_AA)

                wnd_txt = f"| WND Tilt:{ang_srt:+.1f}d DH:{dis_arm:.2f}" + (" [TURBULENCE SUPPRESSION!]" if trb_alr else "")
                cv2.rectangle(frm_bgr, (14, 10), (1260, 46), (0, 0, 0), -1)
                cv2.putText(
                    frm_bgr, est_txt, (22, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, col_hud, 2, cv2.LINE_AA
                )
                cv2.putText(
                    frm_bgr, wnd_txt, (790, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, col_wnd, 2, cv2.LINE_AA
                )

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
                f"Source: {sys_via} | Standard: D={cas_dia_mm}mm | Frames: {q_len} | Telemetry: {pnd_str}\n".encode()
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
        self.send_header("Content-Type", f"multipart/x-mixed-replace; boundary=--{cab_lim.decode()}")
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
    print(f"[*] 1wise Dual Pendulum & Windchime Tracker v3.5.9 on 0.0.0.0:{dmn_prt} | D_const={cas_dia_mm}mm")
    srv_inst = ThreadingHTTPServer(("0.0.0.0", dmn_prt), MjpegStreamSrv)
    try:
        srv_inst.serve_forever()
    except KeyboardInterrupt:
        srv_inst.server_close()
