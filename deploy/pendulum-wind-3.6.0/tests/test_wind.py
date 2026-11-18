#!/usr/bin/env python3
# Timestamp: 2026-11-16
# Version: 3.6.0
# Author & Credits: https://www.alawise.es/1-s
"""Exercise the actual 13-group source contract, legacy data and alarm gating."""
import importlib.util
import unittest
import io
from pathlib import Path

pth_mod = Path(__file__).resolve().parents[1] / 'pendulum_feed.py'
obj_esp = importlib.util.spec_from_file_location('pendulum_feed', pth_mod)
obj_mod = importlib.util.module_from_spec(obj_esp)
obj_esp.loader.exec_module(obj_mod)
txt_bas = '1700000000.123456|546,292,40.23|546,292,40.23|0,0,40|0,0,1|40|78|0|4'

class PrbViento(unittest.TestCase):
    def test_wind_fields_survive_the_wire(self):
        dat_mst = obj_mod.prs_pnd(txt_bas + '|32.5|0.65|1|1.44')
        self.assertEqual(dat_mst['wind']['tilt_deg'], 32.5)
        self.assertEqual(dat_mst['wind']['dissociation'], 0.65)
        self.assertTrue(dat_mst['wind']['suppression_active'])
        self.assertAlmostEqual(dat_mst['wind']['threshold_xy_mm'], 69.0)
        self.assertFalse(dat_mst['alert'])
        self.assertEqual(dat_mst['displacement'], 40)

    def test_rounding_does_not_override_source_decisions(self):
        for flg_trb in (0, 1):
            dat_mst = obj_mod.prs_pnd(txt_bas + f'|32.5|0.45|{flg_trb}|1.00')
            self.assertEqual(dat_mst['wind']['turbulence'], bool(flg_trb))

    def test_multipart_header_ignores_jpeg_body_lookalikes(self):
        dat_jpg = b"JPEG\r\nX-1wise-Pendulum: not-a-header\r\n"
        dat_hdr = (b"--boundary_1wise_x\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(dat_jpg)).encode() + b"\r\nX-1wise-Pendulum: " + (txt_bas + '|32.5|0.65|1|1.44').encode() + b"\r\n\r\n")
        obj_rsp = io.BytesIO(dat_hdr + dat_jpg + b"\r\n--boundary_1wise_x--\r\n")
        obj_rsp.headers = {'Content-Type': 'multipart/x-mixed-replace; boundary=--boundary_1wise_x'}
        dat_mst = list(obj_mod.lee_mjp(obj_rsp))
        self.assertEqual(len(dat_mst), 1)
        self.assertEqual(dat_mst[0]['wind']['dissociation'], 0.65)

    def test_legacy_wind_is_unknown(self):
        self.assertIsNone(obj_mod.prs_pnd(txt_bas)['wind'])

    def test_startup_remains_waiting(self):
        self.assertIsNone(obj_mod.prs_pnd('0|0,0,0|0,0,0|0,0,0|0,0,0|0|0|0|0|0.0|0.00|0|0.00'))

    def test_malformed_wind_is_rejected(self):
        for txt_bad in ['nan|0.5|1|1', '181|0.5|1|1', '32|1.1|1|1',
                        '32|0.5|2|1', '32|0.5|1|2.51', '32|0.5|1|-1',
                        '32|0.5|1', '32|0.5|1|1|0']:
            with self.subTest(payload=txt_bad), self.assertRaises(ValueError):
                obj_mod.prs_pnd(txt_bas + '|' + txt_bad)
        with self.assertRaises(ValueError):
            obj_mod.prs_pnd(txt_bas.replace('|78|0|4', '|78|1|4') + '|32|0.65|1|1.44')

    def test_event_history_preserves_wind_context(self):
        obj_est = obj_mod.PndState()
        obj_est.act_pnd(obj_mod.prs_pnd(txt_bas + '|32|0.65|1|1.44'), sys_ts=100, sys_mnt=0)
        txt_nvo = txt_bas.replace('1700000000.123456', '1700000001.123456').replace('|78|0|4','|78|1|5')
        obj_est.act_pnd(obj_mod.prs_pnd(txt_nvo + '|33|0.20|0|0.44'), sys_ts=101, sys_mnt=1)
        dat_tel = obj_est.snapshot()
        self.assertEqual(dat_tel['version'], 3)
        self.assertEqual(len(dat_tel['history']), 2)
        self.assertEqual(dat_tel['events'][0]['wind']['factor'], 0.44)
        self.assertFalse(dat_tel['events'][0]['wind']['turbulence'])

if __name__ == '__main__':
    unittest.main()
