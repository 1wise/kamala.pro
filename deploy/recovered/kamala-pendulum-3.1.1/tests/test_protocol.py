#!/usr/bin/env python3
# Timestamp: 2026-11-07
# Version: 3.1.1
# Author & Credits: https://www.alawise.es/1-s
"""Exercise the actual wire contract, migration and bounded collector state."""

import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

pth_src = Path(__file__).resolve().parents[1]


def carga_mod(txt_nom, pth_fil):
    sys_mod = importlib.util.spec_from_file_location(txt_nom, pth_fil)
    obj_mod = importlib.util.module_from_spec(sys_mod)
    sys_mod.loader.exec_module(obj_mod)
    return obj_mod


obj_feed = carga_mod("pnd_feed", pth_src / "pendulum_feed.py")
obj_ins = carga_mod("pnd_install", pth_src / "install.py")
TXT_3D = "1794052800.125000|608,300,32.25|608.00,300.00,32.00|0.00,0.00,-4.26|0.0,0.0,-2.1|4.26|78|0|4"
TXT_2D = "1794052800.125000|608,300|600,290|8,10|2,3|12.81|210|0|4"


class PndProtocolTests(unittest.TestCase):
    def test_source_3d_fields_keep_units_and_radius(self):
        dat_pnd = obj_feed.prs_pnd(TXT_3D)
        self.assertEqual(dat_pnd["mode"], "3d-mm")
        self.assertEqual(dat_pnd["r"], 32.25)
        self.assertEqual(dat_pnd["dz"], -4.26)
        self.assertEqual(dat_pnd["vz"], -2.1)
        self.assertEqual(dat_pnd["displacement"], 4.26)
        self.assertEqual(dat_pnd["fit_pct"], 78)
        self.assertIsNone(dat_pnd["luminance"])
        self.assertTrue(dat_pnd["tracking_valid"])

    def test_legacy_pixels_do_not_acquire_physical_z(self):
        dat_pnd = obj_feed.prs_pnd(TXT_2D)
        self.assertEqual(dat_pnd["mode"], "2d-px")
        self.assertEqual(dat_pnd["luminance"], 210)
        for txt_clv in ("r", "ar", "dz", "vz", "fit_pct"):
            self.assertIsNone(dat_pnd[txt_clv])

    def test_both_startup_sentinels_are_waiting(self):
        self.assertIsNone(obj_feed.prs_pnd("0|0,0,0|0,0,0|0,0,0|0,0,0|0|0|0|0"))
        self.assertIsNone(obj_feed.prs_pnd("0|0,0|0,0|0,0|0,0|0|0|0|0"))

    def test_malformed_3d_data_is_rejected(self):
        for txt_bad in (
            TXT_3D.replace("608,300,32.25", "608,300"),
            TXT_3D.replace("32.25", "nan"), TXT_3D.replace("32.25", "0"),
            TXT_3D.replace("|78|", "|101|"), TXT_3D.replace("|78|", "|78.5|"),
            TXT_3D.replace("|0|4", "|2|4"), TXT_3D.replace("|0|4", "|0|4.5"),
            TXT_3D.replace("608,300,32.25", "1280,300,32.25"),
            TXT_3D.replace("|4.26|", "|-4.26|"),
        ):
            with self.subTest(wire=txt_bad), self.assertRaises(ValueError):
                obj_feed.prs_pnd(txt_bad)

    def test_low_fit_is_preserved_without_marking_it_as_brightness(self):
        dat_pnd = obj_feed.prs_pnd(TXT_3D.replace("|78|", "|10|"))
        self.assertFalse(dat_pnd["tracking_valid"])
        self.assertEqual(dat_pnd["fit_pct"], 10)
        self.assertIsNone(dat_pnd["luminance"])

    def test_sessions_do_not_mix_pixel_and_millimeter_histories(self):
        obj_est = obj_feed.PndState()
        obj_est.act_pnd(obj_feed.prs_pnd(TXT_2D), sys_ts=100, sys_mnt=0)
        obj_est.act_pnd(obj_feed.prs_pnd(TXT_3D), sys_ts=101, sys_mnt=1)
        dat_tel = obj_est.snapshot()
        self.assertEqual(dat_tel["session"], 2)
        self.assertEqual(len(dat_tel["history"]), 1)
        self.assertEqual(dat_tel["units"]["displacement"], "mm")

    def test_source_events_are_not_invented_from_z(self):
        obj_est = obj_feed.PndState()
        dat_pnd = obj_feed.prs_pnd(TXT_3D)
        obj_est.act_pnd(dat_pnd, sys_ts=100, sys_mnt=0)
        dat_nvo = dict(dat_pnd, ts=dat_pnd["ts"] + 1, dz=20, displacement=20)
        obj_est.act_pnd(dat_nvo, sys_ts=101, sys_mnt=1)
        self.assertEqual(obj_est.snapshot()["events"], [])
        dat_nvo = dict(dat_nvo, ts=dat_nvo["ts"] + 1, events=5, alert=True)
        obj_est.act_pnd(dat_nvo, sys_ts=102, sys_mnt=2)
        dat_evn = obj_est.snapshot()["events"][0]
        self.assertEqual(dat_evn["delta"], 1)
        self.assertEqual(dat_evn["dz"], 20)
        self.assertEqual(dat_evn["displacement"], 20)

    def test_history_is_bounded_and_source_restart_starts_a_new_session(self):
        obj_est = obj_feed.PndState()
        dat_pnd = obj_feed.prs_pnd(TXT_3D)
        for cnt_mst in range(500):
            obj_est.act_pnd(dict(dat_pnd, ts=dat_pnd["ts"] + cnt_mst),
                            sys_ts=100 + cnt_mst, sys_mnt=cnt_mst)
        self.assertEqual(len(obj_est.snapshot()["history"]), 240)
        obj_est.act_pnd(dict(dat_pnd, events=0), sys_ts=700, sys_mnt=600)
        self.assertEqual(len(obj_est.snapshot()["history"]), 1)
        self.assertEqual(obj_est.snapshot()["session"], 2)

    def test_html_patch_preserves_the_rest_of_the_page(self):
        txt_htm = ('<!doctype html><head><link href="/pendulum.css?v=2.3.0">'
                   '<script src="/pendulum.mjs?v=2.3.0"></script></head>'
                   '<main><p>Keep the existing article.</p><div data-pendulum>'
                   '<div>old instrument</div></div><p>Keep the footer.</p></main>')
        txt_nvo = obj_ins.parchea_html(txt_htm, '<div data-pendulum><div>new instrument</div></div>')
        self.assertIn('<p>Keep the existing article.</p>', txt_nvo)
        self.assertIn('<p>Keep the footer.</p>', txt_nvo)
        self.assertNotIn('old instrument', txt_nvo)
        self.assertEqual(txt_nvo.count('?v=3.1.1'), 2)

    def test_full_multipart_round_trip_with_both_boundary_spellings(self):
        # A fake header inside the JPEG must never be treated as part telemetry.
        dat_jpg = b'\xff\xd8\r\n--boundary_1wise_x\r\nX-1wise-Pendulum: injected\r\n\xff\xd9'
        for txt_bnd in ('boundary_1wise_x', '--boundary_1wise_x'):
            class MjpHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=' + txt_bnd)
                    self.end_headers()
                    dat_hdr = ('--boundary_1wise_x\r\nContent-Type: image/jpeg\r\nContent-Length: ' +
                               str(len(dat_jpg)) + '\r\nX-1wise-Pendulum: ' + TXT_3D + '\r\n\r\n').encode()
                    self.wfile.write(dat_hdr + dat_jpg + b'\r\n--boundary_1wise_x--\r\n')

                def log_message(self, *args):
                    pass

            with self.subTest(boundary=txt_bnd), tempfile.TemporaryDirectory() as txt_tmp:
                obj_srv = ThreadingHTTPServer(('127.0.0.1', 0), MjpHandler)
                sys_hil = threading.Thread(target=obj_srv.serve_forever, daemon=True)
                sys_hil.start()
                try:
                    pth_out = Path(txt_tmp) / 'state.json'
                    subprocess.run([sys.executable, str(pth_src / 'pendulum_feed.py'), '--once',
                                    '--url', 'http://127.0.0.1:' + str(obj_srv.server_port),
                                    '--output', str(pth_out)], check=True, timeout=5)
                    dat_tel = json.loads(pth_out.read_text())
                    self.assertEqual(dat_tel['version'], 2)
                    self.assertEqual(dat_tel['sample']['dz'], -4.26)
                    self.assertEqual(dat_tel['units']['velocity'], 'mm/s')
                    self.assertEqual(dat_tel['status'], 'live')
                finally:
                    obj_srv.shutdown()
                    obj_srv.server_close()


if __name__ == '__main__':
    unittest.main()
